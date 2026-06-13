def test_no_trade_adapter_imports():
    from backend.app.skills.no_trade_engine import no_trade_analysis

    assert callable(no_trade_analysis)
