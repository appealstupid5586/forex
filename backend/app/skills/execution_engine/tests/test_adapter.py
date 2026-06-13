def test_execution_adapter_imports():
    from backend.app.skills.execution_engine import execute_order

    assert callable(execute_order)
