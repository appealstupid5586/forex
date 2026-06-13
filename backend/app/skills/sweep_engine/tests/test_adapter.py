def test_sweep_adapter_imports():
    from backend.app.skills.sweep_engine import sweep_orders_adapter

    assert callable(sweep_orders_adapter)
