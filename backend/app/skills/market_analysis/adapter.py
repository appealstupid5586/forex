from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from backend.app.skills.market_analysis.feature_pipeline import compute_features


def analyze_market_state(market_state: Dict[str, Any]) -> Dict[str, Any]:
    """Adapter function to provide the standard skill interface.

    Expects `market_state` to contain key `ohlcv` which is an array-like or
    pandas-compatible structure. Returns a JSON-compatible dictionary with
    `decision`, `confidence`, `evidence`, `metadata`.
    """

    ohlcv = market_state.get("ohlcv")
    if ohlcv is None:
        return {
            "decision": "no_data",
            "confidence": 0.0,
            "evidence": ["missing ohlcv in market_state"],
            "metadata": {},
        }

    df = pd.DataFrame(ohlcv)
    features = compute_features(df)

    if not features.get("ready"):
        return {
            "decision": "insufficient_history",
            "confidence": 0.1,
            "evidence": [features.get("reason")],
            "metadata": features,
        }

    # Basic rule-based decision for now — evidence contains computed indicators
    evidence = [
        {"atr": features.get("atr")},
        {"ma20": features.get("ma20")},
        {"volatility_regime": features.get("volatility_regime")},
        {"trend_regime": features.get("trend_regime")},
    ]

    decision = "neutral"
    confidence = 0.5
    if features.get("trend_regime") == "UP":
        decision = "bias_long"
        confidence = 0.6
    elif features.get("trend_regime") == "DOWN":
        decision = "bias_short"
        confidence = 0.6

    return {
        "decision": decision,
        "confidence": confidence,
        "evidence": evidence,
        "metadata": features,
    }
