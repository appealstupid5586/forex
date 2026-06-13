from __future__ import annotations

from fastapi import APIRouter

from app.core.models import RiskDecision
from app.core.runtime import get_or_create_robot_state, market_agent, no_trade_guard, risk_guard

router = APIRouter(prefix="/api/v1/guard", tags=["guard"])


@router.get("/check")
def check_guard():
    state = get_or_create_robot_state()
    tick = market_agent.fetch_tick(state.symbol)
    return risk_guard.evaluate(state, tick)


@router.get("/no-trade", response_model=RiskDecision)
def check_no_trade():
    """Return NO TRADE ENGINE permission status for the current robot state."""
    state = get_or_create_robot_state()
    tick = market_agent.fetch_tick(state.symbol)
    market_state = {"tick": tick, "confidence": 0.8, "regime": "REGIME_UPTREND"}
    return no_trade_guard.evaluate(state, market_state)
