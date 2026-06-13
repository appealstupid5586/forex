from __future__ import annotations

from fastapi import APIRouter

from app.core.runtime import get_or_create_robot_state, market_agent, no_trade_guard, risk_guard

router = APIRouter(prefix="/api/v1/guard", tags=["guard"])


@router.get("/check")
def check_guard():
    state = get_or_create_robot_state()
    tick = market_agent.fetch_tick(state.symbol)
    return risk_guard.evaluate(state, tick)


@router.get("/no-trade")
def check_no_trade():
    state = get_or_create_robot_state()
    tick = market_agent.fetch_tick(state.symbol)
    result = no_trade_guard.evaluate(state, {"tick": tick})
    return {"allowed": result.allowed, "action": result.action, "reasons": result.reasons}
