"""Risk guard skill implementation for the unified skill registry."""
from __future__ import annotations

from app.core.models import MarketTick, RiskDecision

METADATA = {
    "name": "risk_engine",
    "kind": "risk",
}


class RiskGuardAgent:
    """Simple risk guard that enforces drawdown and spread constraints."""

    def __init__(self, settings):
        self.settings = settings

    def evaluate(self, state, tick: MarketTick | None = None):
        reasons: list[str] = []
        allowed = True
        action = "ALLOW"

        if state.drawdown_pct > self.settings.max_drawdown_pct:
            allowed = False
            action = "FREEZE"
            reasons.append("drawdown exceeded")

        if tick is not None and tick.spread > self.settings.max_spread_points * self.settings.tick_size:
            allowed = False
            action = "PAUSE_NEW_ENTRY"
            reasons.append("spread exceeded")

        return RiskDecision(allowed=allowed, action=action, reasons=reasons)


def evaluate_risk(state, settings, tick: MarketTick | None = None, api_latency_ms: int = 0):
    """Compatibility wrapper for the risk engine adapter."""
    return RiskGuardAgent(settings).evaluate(state, tick)


__all__ = ["RiskGuardAgent", "evaluate_risk", "METADATA"]
