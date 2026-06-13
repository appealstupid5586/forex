from backend.app.skills.setup_detection import detect_setup

if __name__ == "__main__":
    market_state = {
        "ohlcv": [
            {"open": 1.0, "high": 1.01, "low": 0.99, "close": 1.001},
            {"open": 1.001, "high": 1.02, "low": 1.0, "close": 1.002},
            {"open": 1.002, "high": 1.03, "low": 1.01, "close": 1.003},
        ]
    }
    print(detect_setup(market_state))
