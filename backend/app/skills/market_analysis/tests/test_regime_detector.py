from __future__ import annotations

import pandas as pd

from backend.app.skills.market_analysis import detect_regime


def build_ohlcv(close_prices):
    data = {
        "open": close_prices,
        "high": [p * 1.001 for p in close_prices],
        "low": [p * 0.999 for p in close_prices],
        "close": close_prices,
        "volume": [1000.0] * len(close_prices),
    }
    return pd.DataFrame(data)


def test_detect_regime_uptrend():
    prices = [1.0 + i * 0.001 for i in range(60)]
    ohlcv = build_ohlcv(prices)
    result = detect_regime(ohlcv)
    assert result["regime"] in {"REGIME_UPTREND", "REGIME_STRONG_BULL"}
    assert result["structure"]["structure"] == "HH_HL"


def test_detect_regime_downtrend():
    prices = [1.05 - i * 0.001 for i in range(60)]
    ohlcv = build_ohlcv(prices)
    result = detect_regime(ohlcv)
    assert result["regime"] in {"REGIME_DOWNTREND", "REGIME_STRONG_BEAR"}
    assert result["structure"]["structure"] == "LL_LH"


def test_detect_regime_sideway():
    prices = [1.0 + (0.0005 if i % 2 else -0.0005) for i in range(60)]
    ohlcv = build_ohlcv(prices)
    result = detect_regime(ohlcv)
    assert result["regime"] == "REGIME_SIDEWAY"
