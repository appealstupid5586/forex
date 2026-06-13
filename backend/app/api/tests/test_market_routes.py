from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def build_ohlcv(close_prices):
    return [
        {
            "open": float(price * 0.9995),
            "high": float(price * 1.001),
            "low": float(price * 0.999),
            "close": float(price),
            "volume": 1000.0,
        }
        for price in close_prices
    ]


def test_detect_market_regime():
    ohlcv = build_ohlcv([1.0 + i * 0.001 for i in range(60)])
    response = client.post("/api/v1/market/regime", json={"ohlcv": ohlcv})
    assert response.status_code == 200
    payload = response.json()
    assert "regime_analysis" in payload
    assert payload["regime_analysis"]["structure"]["structure"] in {"HH_HL", "LL_LH", "SIDEWAY"}


def test_detect_market_structure():
    ohlcv = build_ohlcv([1.0 + i * 0.001 for i in range(60)])
    response = client.post("/api/v1/market/structure", json={"ohlcv": ohlcv})
    assert response.status_code == 200
    payload = response.json()
    assert payload["structure_analysis"]["structure"] == "HH_HL"


def test_detect_market_momentum():
    ohlcv = build_ohlcv([1.0 + i * 0.001 for i in range(60)])
    response = client.post("/api/v1/market/momentum", json={"ohlcv": ohlcv})
    assert response.status_code == 200
    payload = response.json()
    assert payload["momentum_analysis"]["momentum"] in {"bullish", "neutral", "bearish"}


def test_detect_market_volatility():
    ohlcv = build_ohlcv([1.0 + i * 0.001 for i in range(60)])
    response = client.post("/api/v1/market/volatility", json={"ohlcv": ohlcv})
    assert response.status_code == 200
    payload = response.json()
    assert payload["volatility_analysis"]["atr_state"] in {"high", "normal", "low"}


def test_validate_market_ohlcv():
    ohlcv = build_ohlcv([1.0 + i * 0.001 for i in range(10)])
    response = client.post("/api/v1/market/validate", json={"ohlcv": ohlcv})
    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is True
    assert payload["total_candles"] == 10


def test_validate_market_ohlcv_rejects_short_series():
    short_ohlcv = build_ohlcv([1.0, 1.001, 1.002])
    response = client.post("/api/v1/market/validate", json={"ohlcv": short_ohlcv})
    assert response.status_code == 422
