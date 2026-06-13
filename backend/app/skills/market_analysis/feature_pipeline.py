from __future__ import annotations

import pandas as pd


def compute_features(df: pd.DataFrame) -> dict:
    """Compute basic indicators from OHLCV dataframe.

    Required columns: open, high, low, close.
    """
    if df.empty or len(df) < 30:
        return {"ready": False, "reason": "need at least 30 candles"}
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(14).mean().iloc[-1]
    ma20 = df["close"].rolling(20).mean().iloc[-1]
    volatility_regime = "HIGH" if atr > df["close"].iloc[-1] * 0.0015 else "NORMAL"
    trend_regime = "UP" if df["close"].iloc[-1] > ma20 else "DOWN"
    return {
        "ready": True,
        "atr": float(atr),
        "ma20": float(ma20),
        "volatility_regime": volatility_regime,
        "trend_regime": trend_regime,
    }
