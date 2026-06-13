def test_risk_adapter_imports():
    from backend.app.skills.risk_engine import risk_analysis

    assert callable(risk_analysis)
