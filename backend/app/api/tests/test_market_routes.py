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


def test_validate_market_ohlcv_monotonic_timestamps_accepts():
    base_ts = 1680000000
    ohlcv = []
    for i, price in enumerate([1.0 + i * 0.001 for i in range(10)]):
        ts = base_ts + i
        candle = build_ohlcv([price])[0]
        candle["timestamp"] = ts
        ohlcv.append(candle)

    response = client.post("/api/v1/market/validate", json={"ohlcv": ohlcv})
    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is True


def test_validate_market_ohlcv_monotonic_timestamps_rejects():
    # timestamps not monotonic
    ohlcv = []
    prices = [1.0, 1.001, 1.002, 1.003, 1.004]
    timestamps = [100, 101, 99, 102, 103]
    for price, ts in zip(prices, timestamps):
        candle = build_ohlcv([price])[0]
        candle["timestamp"] = ts
        ohlcv.append(candle)

    response = client.post("/api/v1/market/validate", json={"ohlcv": ohlcv})
    assert response.status_code == 422


def test_validate_market_ohlcv_rejects_naive_string_timestamp():
    # ISO strings without timezone should be rejected
    ohlcv = []
    for i, price in enumerate([1.0 + i * 0.001 for i in range(6)]):
        candle = build_ohlcv([price])[0]
        candle["timestamp"] = f"2023-01-01T00:00:0{i}"
        ohlcv.append(candle)

    response = client.post("/api/v1/market/validate", json={"ohlcv": ohlcv})
    assert response.status_code == 422


def test_validate_market_ohlcv_accepts_timezone_aware_strings():
    # ISO strings with timezone should be accepted and normalized to UTC
    ohlcv = []
    for i, price in enumerate([1.0 + i * 0.001 for i in range(6)]):
        candle = build_ohlcv([price])[0]
        candle["timestamp"] = f"2023-01-01T00:00:0{i}+07:00"
        ohlcv.append(candle)

    response = client.post("/api/v1/market/validate", json={"ohlcv": ohlcv})
    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is True
    assert "normalized_timestamps" in payload
    # normalized timestamps should end with Z (UTC)
    assert all(ts.endswith("+00:00") or ts.endswith("Z") for ts in payload["normalized_timestamps"])
