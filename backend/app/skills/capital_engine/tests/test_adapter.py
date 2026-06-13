def test_capital_adapter_imports():
    from backend.app.skills.capital_engine import capital_analysis

    assert callable(capital_analysis)
