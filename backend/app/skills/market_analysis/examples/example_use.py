"""Minimal example showing how to call the `market-analysis` skill adapter.

Run manually with the project PYTHONPATH set so `app.market.feature_pipeline`
is importable (normal project execution should already have that configured).
"""
from backend.app.skills.market_analysis import analyze_market_state

if __name__ == "__main__":
    # Example synthetic OHLCV data: list of dicts with open/high/low/close
    ohlcv = [
        {"open": 1.0, "high": 1.01, "low": 0.99, "close": 1.005},
    ] * 40
    market_state = {"ohlcv": ohlcv}
    result = analyze_market_state(market_state)
    print(result)
