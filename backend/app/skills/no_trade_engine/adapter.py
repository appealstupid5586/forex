from __future__ import annotations

from typing import Any, Dict

from backend.app.skills.no_trade_engine.no_trade_guard import evaluate_no_trade


def no_trade_analysis(market_state: Dict[str, Any], state: Any, settings: Any, api_latency_ms: int = 0) -> Dict[str, Any]:
    """Adapter that exposes NO TRADE ENGINE decision to the skill registry."""
    decision = evaluate_no_trade(settings=settings, state=state, market_state=market_state)
    return {"allowed": decision.allowed, "action": decision.action, "reasons": decision.reasons}
