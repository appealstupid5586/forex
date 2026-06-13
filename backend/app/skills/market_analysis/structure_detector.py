from __future__ import annotations

from typing import Dict

import pandas as pd


def detect_structure(ohlcv: pd.DataFrame, lookback: int = 30, tolerance: float = 0.002) -> Dict[str, str]:
    """Detect market structure from recent high/low price action."""
    if ohlcv.empty or len(ohlcv) < 6:
        return {"structure": "SIDEWAY", "trend": "neutral"}

    df = ohlcv.dropna(subset=["high", "low", "close"]).copy()
    if df.empty:
        return {"structure": "SIDEWAY", "trend": "neutral"}

    window = df.iloc[-lookback:]
    if len(window) < 6:
        window = df

    sample = window.iloc[[0, max(1, len(window) // 2), -1]]
    first_high = float(sample["high"].iloc[0])
    last_high = float(sample["high"].iloc[-1])
    first_low = float(sample["low"].iloc[0])
    last_low = float(sample["low"].iloc[-1])

    higher_highs = last_high > first_high * (1 + tolerance)
    higher_lows = last_low > first_low * (1 + tolerance)
    lower_highs = last_high < first_high * (1 - tolerance)
    lower_lows = last_low < first_low * (1 - tolerance)

    if higher_highs and higher_lows:
        return {"structure": "HH_HL", "trend": "bullish"}
    if lower_highs and lower_lows:
        return {"structure": "LL_LH", "trend": "bearish"}

    return {"structure": "SIDEWAY", "trend": "neutral"}
