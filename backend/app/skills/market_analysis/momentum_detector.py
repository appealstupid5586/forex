from __future__ import annotations

from typing import Dict

import pandas as pd


def detect_momentum(ohlcv: pd.DataFrame) -> Dict[str, str]:
    """Assess momentum using MACD, EMA alignment, and EMA slope."""
    if ohlcv.empty or len(ohlcv) < 35:
        return {
            "momentum": "neutral",
            "macd_histogram": 0.0,
            "ema_alignment": "flat",
            "ema_slope": "flat",
        }

    df = ohlcv.dropna(subset=["close"]).copy()
    close = df["close"].astype(float)

    ema_fast = close.ewm(span=12, adjust=False).mean()
    ema_slow = close.ewm(span=26, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    macd_signal = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - macd_signal

    ema20 = close.ewm(span=20, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()

    ema_delta = ema20.iloc[-1] - ema50.iloc[-1]
    avg_price = float(close.mean()) if not close.empty else 1.0
    plenty = avg_price * 0.0008

    if ema_delta > plenty:
        ema_alignment = "bullish"
    elif ema_delta < -plenty:
        ema_alignment = "bearish"
    else:
        ema_alignment = "flat"

    ema_change = ema20.iloc[-1] - ema20.iloc[-3]
    if ema_change > plenty:
        slope = "up"
    elif ema_change < -plenty:
        slope = "down"
    else:
        slope = "flat"

    macd_histogram = float(histogram.iloc[-1])
    momentum = "neutral"
    if macd_histogram > 0 and ema_alignment == "bullish" and slope == "up":
        momentum = "bullish"
    elif macd_histogram < 0 and ema_alignment == "bearish" and slope == "down":
        momentum = "bearish"

    return {
        "momentum": momentum,
        "macd_histogram": macd_histogram,
        "ema_alignment": ema_alignment,
        "ema_slope": slope,
    }

    return {
        "momentum": momentum,
        "macd_histogram": macd_histogram,
        "ema_alignment": ema_alignment,
        "ema_slope": slope,
    }
