from backend.app.skills.market_analysis import detect_regime


def run_example(ohlcv):
    result = detect_regime(ohlcv)
    print("Regime result:", result)
