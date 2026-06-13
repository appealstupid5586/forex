def test_adapter_imports():
    from backend.app.skills.market_analysis import analyze_market_state

    assert callable(analyze_market_state)
