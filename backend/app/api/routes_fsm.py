from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.models import RobotStatus
from app.core.runtime import (
    capital_engine,
    execution_agent,
    fsm_brain,
    get_or_create_robot_state,
    hedge_engine,
    market_agent,
    no_trade_guard,
    risk_guard,
    save_robot_state,
    state_store,
)
from backend.app.skills.market_analysis import detect_regime
from hooks.schemas import HookContext
from app.core.runtime import evolution_agent
from app.strategy.grid_math import calculate_grid

router = APIRouter(prefix="/api/v1/fsm", tags=["fsm"])
settings = get_settings()


@router.post("/tick")
def tick():
    state = get_or_create_robot_state()
    tick_data = market_agent.fetch_tick(state.symbol)
    independent_ok = market_agent.validate_independent_source(tick_data)
    market_state = {"tick": tick_data}

    no_trade_decision = no_trade_guard.evaluate(state, market_state)
    if not no_trade_decision.allowed:
        state.status = RobotStatus.STOPPED
        state.fsm_state = fsm_brain.next_state(state, no_trade_decision, has_cycle=None, surplus_active=False)
        save_robot_state(state)
        return {
            "state": state,
            "tick": tick_data,
            "grid": None,
            "risk": no_trade_decision,
            "capital": None,
            "executed_orders": [],
            "cycle": None,
        }

    ohlcv_data = market_agent.fetch_ohlcv(state.symbol, num_candles=20)
    regime_result = detect_regime(ohlcv_data)
    current_regime = str(regime_result.get("regime", "REGIME_TRANSITION"))
    current_atr = float(regime_result.get("volatility", {}).get("atr", 0.00001))
    stop_distance = max(current_atr / settings.tick_size, 10.0)

    capital_sizing = capital_engine.size_position(state, {"tick": tick_data, "stop_distance": stop_distance, "regime": current_regime})

    # Run before-signal hooks
    try:
        before_signal_results = evolution_agent.run_before_signal(HookContext(event="before_signal", payload={"state": state.model_dump(), "tick": tick_data.model_dump()}))
        if any(not r.proceed for r in before_signal_results):
            risk = risk_guard.evaluate(state, tick_data)
            risk.allowed = False
            risk.action = "PAUSE_SIGNAL"
            for r in before_signal_results:
                if not r.proceed:
                    risk.reasons.extend(r.reasons)
            state.fsm_state = fsm_brain.next_state(state, risk, has_cycle=None, surplus_active=False)
            save_robot_state(state)
            return {"state": state, "tick": tick_data, "grid": None, "risk": risk, "executed_orders": [], "cycle": None}
    except Exception:
        # Fail-safe: continue without hooks on error
        pass
    risk = risk_guard.evaluate(state, tick_data)
    if not independent_ok:
        risk.allowed = False
        risk.action = "PAUSE_EXECUTION"
        risk.reasons.append("independent data source validation failed")

    if risk.action == "CLOSE_RISKY_ORDERS":
        try:
            close_context = HookContext(
                event="before_close",
                payload={"state": state.model_dump(), "tick": tick_data.model_dump(), "risk": risk.model_dump()},
            )
            before_close_results = evolution_agent.run_before_close(close_context)
            if any(not result.proceed for result in before_close_results):
                risk.action = "PAUSE_EXECUTION"
                for result in before_close_results:
                    if not result.proceed:
                        risk.reasons.extend(result.reasons)
                risk.reasons.append("close action blocked by before_close hook")
                evolution_agent.save_evidence(
                    {
                        "event": "before_close_blocked",
                        "state": state.model_dump(),
                        "tick": tick_data.model_dump(),
                        "risk": risk.model_dump(),
                        "hook_results": [result.__dict__ for result in before_close_results],
                    },
                    tags=["evidence", "close", "hook"],
                )
            else:
                for result in before_close_results:
                    risk.reasons.extend(result.reasons)
                evolution_agent.save_failure(
                    {
                        "event": "close_action",
                        "state": state.model_dump(),
                        "tick": tick_data.model_dump(),
                        "risk": risk.model_dump(),
                    },
                    tags=["failure", "close", "risk"],
                )
                try:
                    evolution_agent.run_after_close(HookContext(
                        event="after_close",
                        payload={"state": state.model_dump(), "tick": tick_data.model_dump(), "risk": risk.model_dump()},
                    ))
                except Exception:
                    pass
        except Exception:
            pass

    cycle = state_store.load_cycle(state.current_cycle_id) if state.current_cycle_id else None
    grid = calculate_grid(state.symbol, tick_data.mid, tick_data.mid, settings.default_step_size, settings.default_x_level, settings.tick_size)
    executed = []

    if state.status == "RUNNING" and risk.allowed:
        if cycle is None:
            cycle = hedge_engine.open_base_hedge(state, tick_data)
            state.current_cycle_id = cycle.cycle_id
            for order in cycle.buy_orders + cycle.sell_orders:
                # Run before-trade hooks; skip execution if any hook blocks
                try:
                    before_trade_results = evolution_agent.run_before_trade(HookContext(event="before_trade", payload={"order": order.model_dump(), "state": state.model_dump()}))
                    if any(not r.proceed for r in before_trade_results):
                        continue
                except Exception:
                    pass

                opened = execution_agent.execute(order)
                executed.append(opened)

                try:
                    evolution_agent.run_after_trade(HookContext(event="after_trade", payload={"order": opened.model_dump(), "state": state.model_dump()}))
                except Exception:
                    pass
            state_store.save_cycle(cycle)
        else:
            grid = calculate_grid(state.symbol, cycle.buy_orders[0].entry_price, tick_data.mid, settings.default_step_size, settings.default_x_level, settings.tick_size)
            surplus_orders = hedge_engine.evaluate_surplus(state, cycle, grid, tick_data)
            for order in surplus_orders:
                try:
                    before_trade_results = evolution_agent.run_before_trade(HookContext(event="before_trade", payload={"order": order.model_dump(), "state": state.model_dump()}))
                    if any(not r.proceed for r in before_trade_results):
                        continue
                except Exception:
                    pass

                opened = execution_agent.execute(order)
                executed.append(opened)
                if opened.side == "BUY":
                    cycle.buy_orders.append(opened)
                else:
                    cycle.sell_orders.append(opened)

                try:
                    evolution_agent.run_after_trade(HookContext(event="after_trade", payload={"order": opened.model_dump(), "state": state.model_dump()}))
                except Exception:
                    pass
            state_store.save_cycle(cycle)

    state.fsm_state = fsm_brain.next_state(state, risk, has_cycle=cycle is not None, surplus_active=bool(executed and cycle and cycle.surplus_side != "NONE"))
    state.last_step = grid.current_step
    save_robot_state(state)
    return {
        "state": state,
        "tick": tick_data,
        "grid": grid,
        "risk": risk,
        "capital": capital_sizing,
        "executed_orders": executed,
        "cycle": cycle,
    }
