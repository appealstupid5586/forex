from __future__ import annotations

from typing import Any, Dict

from backend.app.skills.risk_engine.risk_guard import evaluate_risk


def risk_analysis(market_state: Dict[str, Any], state: Any, settings: Any, api_latency_ms: int = 0) -> Dict[str, Any]:
    """Adapter that converts runtime inputs to the programmatic `evaluate_risk` API.

    Returns a JSON-serializable RiskDecision-like dict.
    """
    decision = evaluate_risk(state=state, settings=settings, tick=market_state.get("tick"), api_latency_ms=api_latency_ms)
    return {"allowed": decision.allowed, "action": decision.action, "reasons": decision.reasons}
