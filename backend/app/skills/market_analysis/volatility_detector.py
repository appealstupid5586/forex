from __future__ import annotations

from typing import Dict

import pandas as pd


def detect_volatility(ohlcv: pd.DataFrame, atr_period: int = 14, lookback: int = 21) -> Dict[str, object]:
    """Calculate ATR-based volatility characteristics."""
    if ohlcv.empty or len(ohlcv) < atr_period + 2:
        return {
            "atr": 0.0,
            "atr_state": "normal",
            "expansion": False,
            "contraction": False,
        }

    df = ohlcv.dropna(subset=["high", "low", "close"]).copy()
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    close = df["close"].astype(float)

    tr = pd.concat(
        [high - low, (high - close.shift()).abs(), (low - close.shift()).abs()],
        axis=1,
    ).max(axis=1)
    atr = tr.rolling(atr_period).mean()
    if atr.empty or pd.isna(atr.iloc[-1]):
        return {
            "atr": 0.0,
            "atr_state": "normal",
            "expansion": False,
            "contraction": False,
        }

    current_atr = float(atr.iloc[-1])
    reference = atr.iloc[-lookback:-1].dropna()
    mean_atr = float(reference.mean()) if not reference.empty else current_atr

    atr_state = "normal"
    expansion = False
    contraction = False

    if current_atr > mean_atr * 1.15:
        atr_state = "high"
        expansion = True
    elif current_atr < mean_atr * 0.85:
        atr_state = "low"
        contraction = True

    return {
        "atr": current_atr,
        "atr_state": atr_state,
        "expansion": expansion,
        "contraction": contraction,
    }
