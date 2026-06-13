import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.main import app
from app.core.runtime import evolution_agent
from hooks.schemas import SignalHookResult, TradeHookResult


def test_hooks_api_register_and_run():
    client = TestClient(app)

    def before_signal_hook(ctx):
        return SignalHookResult(proceed=False, reasons=["blocked"], metadata={"hook": "bs"})

    def before_trade_hook(ctx):
        return TradeHookResult(proceed=False, reasons=["blocked_trade"], metadata={})

    # register hooks directly
    evolution_agent.register_before_signal_hook(before_signal_hook)
    evolution_agent.register_before_trade_hook(before_trade_hook)

    # available
    resp = client.get("/api/v1/hooks/available")
    assert resp.status_code == 200
    data = resp.json()
    assert any("before_signal_hook" in name for name in data["before_signal"]) or len(data["before_signal"]) >= 1

    # run before-signal
    run_resp = client.post("/api/v1/hooks/run-before-signal", json={"event": "t1", "payload": {}})
    assert run_resp.status_code == 200
    results = run_resp.json()["results"]
    assert results[0]["proceed"] is False
    assert "blocked" in results[0]["reasons"]

    # run before-trade
    run_trade = client.post("/api/v1/hooks/run-before-trade", json={"event": "t2", "payload": {}})
    assert run_trade.status_code == 200
    trade_results = run_trade.json()["results"]
    assert trade_results[0]["proceed"] is False
    assert "blocked_trade" in trade_results[0]["reasons"]

    # reload (should be safe)
    reload_resp = client.post("/api/v1/hooks/reload")
    assert reload_resp.status_code == 200
    assert "ok" in reload_resp.json()
