from __future__ import annotations

from typing import Dict


def determine_strength(
    structure: Dict[str, str],
    momentum: Dict[str, str],
    volatility: Dict[str, object],
) -> Dict[str, str]:
    """Classify trend strength based on structure, momentum, and volatility."""
    structure_trend = structure.get("trend", "neutral")
    momentum_signal = momentum.get("momentum", "neutral")
    atr_state = str(volatility.get("atr_state", "normal"))

    if structure_trend in {"bullish", "bearish"}:
        if momentum_signal == structure_trend and atr_state == "high":
            strength = "strong"
        elif momentum_signal in {"bullish", "bearish"}:
            strength = "normal"
        else:
            strength = "weak"
    else:
        strength = "weak"

    return {"strength": strength}
