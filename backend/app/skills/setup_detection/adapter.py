from __future__ import annotations

from typing import Any, Dict


def detect_setup(market_state: Dict[str, Any]) -> Dict[str, Any]:
    """Simple setup detection adapter for the setup_detection skill."""
    # Minimal placeholder implementation. Replace with actual setup-detection logic.
    ohlcv = market_state.get("ohlcv")
    if not ohlcv:
        return {
            "decision": "no_data",
            "confidence": 0.0,
            "evidence": ["missing ohlcv in market_state"],
            "metadata": {},
        }

    recent = ohlcv[-3:]
    closes = [row.get("close") for row in recent if row.get("close") is not None]
    if len(closes) < 3:
        return {
            "decision": "insufficient_data",
            "confidence": 0.1,
            "evidence": ["need 3 close prices"],
            "metadata": {},
        }

    if closes[-1] > closes[-2] > closes[-3]:
        decision = "breakout"
        confidence = 0.6
    elif closes[-1] < closes[-2] < closes[-3]:
        decision = "reversal"
        confidence = 0.6
    else:
        decision = "continuation"
        confidence = 0.5

    return {
        "decision": decision,
        "confidence": confidence,
        "evidence": [{"recent_closes": closes}],
        "metadata": {"lookback": 3},
    }
