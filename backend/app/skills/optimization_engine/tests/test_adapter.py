def test_optimization_adapter_imports():
    from backend.app.skills.optimization_engine import optimize_parameters

    assert callable(optimize_parameters)
