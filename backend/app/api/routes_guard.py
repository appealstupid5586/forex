from __future__ import annotations

from fastapi import APIRouter

from app.core.runtime import get_or_create_robot_state, market_agent, risk_guard

router = APIRouter(prefix="/api/v1/guard", tags=["guard"])


@router.get("/check")
def check_guard():
    state = get_or_create_robot_state()
    tick = market_agent.fetch_tick(state.symbol)
    return risk_guard.evaluate(state, tick)
