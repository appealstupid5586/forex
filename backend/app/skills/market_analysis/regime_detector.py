from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from backend.app.skills.market_analysis.momentum_detector import detect_momentum
from backend.app.skills.market_analysis.structure_detector import detect_structure
from backend.app.skills.market_analysis.volatility_detector import detect_volatility
from backend.app.skills.market_analysis.trend_strength import determine_strength


def _normalize_ohlcv(ohlcv: Any) -> pd.DataFrame:
    if isinstance(ohlcv, pd.DataFrame):
        return ohlcv
    if isinstance(ohlcv, dict):
        return pd.DataFrame(ohlcv)
    if isinstance(ohlcv, list):
        try:
            return pd.DataFrame(ohlcv)
        except Exception:
            raise ValueError("Unable to convert ohlcv list to DataFrame")
    raise ValueError("Unsupported OHLCV format")


def detect_regime(ohlcv: Any) -> Dict[str, object]:
    """Detect the current market regime from structure, momentum, and volatility."""
    df = _normalize_ohlcv(ohlcv)
    structure = detect_structure(df)
    volatility = detect_volatility(df)
    momentum = detect_momentum(df)
    strength = determine_strength(structure, momentum, volatility)

    is_sideway = structure["structure"] == "SIDEWAY"
    is_low_atr = volatility["atr_state"] == "low"
    is_neutral_momentum = momentum["momentum"] == "neutral"
    is_flat_ema = momentum["ema_alignment"] == "flat" or momentum["ema_slope"] == "flat"

    if is_sideway and (is_low_atr or is_neutral_momentum or is_flat_ema):
        regime = "REGIME_SIDEWAY"
    elif structure["structure"] == "HH_HL" and momentum["momentum"] == "bullish":
        regime = "REGIME_UPTREND"
    elif structure["structure"] == "LL_LH" and momentum["momentum"] == "bearish":
        regime = "REGIME_DOWNTREND"
    elif structure["structure"] == "HH_HL" and volatility["atr_state"] == "high":
        regime = "REGIME_STRONG_BULL"
    elif structure["structure"] == "LL_LH" and volatility["atr_state"] == "high":
        regime = "REGIME_STRONG_BEAR"
    else:
        regime = "REGIME_TRANSITION"

    return {
        "structure": structure,
        "momentum": momentum,
        "volatility": volatility,
        "strength": strength,
        "regime": regime,
    }
