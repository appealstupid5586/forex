from backend.app.skills.hedge_engine import hedge_analysis


def test_hedge_adapter_import():
    assert callable(hedge_analysis)
