from __future__ import annotations

from typing import Any, Dict

from backend.app.skills.capital_engine.position_sizer import PositionSizer


def capital_analysis(market_state: Dict[str, Any], state: Any, settings: Any, api_latency_ms: int = 0) -> Dict[str, Any]:
    """Adapter that exposes capital engine position sizing to the skill registry."""
    sizer = PositionSizer(settings)
    result = sizer.size_position(state, market_state)
    return {"decision": "size_position", "confidence": 0.75, "evidence": ["capital sizing applied"], "metadata": result}
