from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.main import app
from app.core.runtime import evolution_agent
from hooks.schemas import HookContext, SignalHookResult


def test_before_and_after_close_hook_endpoints():
    client = TestClient(app)

    def before_close_hook(ctx: HookContext) -> SignalHookResult:
        return SignalHookResult(proceed=False, reasons=["blocked_close"], metadata={"hook": "before_close"})

    def after_close_hook(ctx: HookContext) -> SignalHookResult:
        return SignalHookResult(proceed=True, reasons=["closed"], metadata={"hook": "after_close"})

    evolution_agent.register_before_close_hook(before_close_hook)
    evolution_agent.register_after_close_hook(after_close_hook)

    available_resp = client.get("/api/v1/hooks/available")
    assert available_resp.status_code == 200
    data = available_resp.json()
    assert any("before_close" in name for name in data["before_close"]) or len(data["before_close"]) >= 1
    assert any("after_close" in name for name in data["after_close"]) or len(data["after_close"]) >= 1

    run_before_resp = client.post("/api/v1/hooks/run-before-close", json={"event": "close_check", "payload": {}})
    assert run_before_resp.status_code == 200
    before_results = run_before_resp.json()["results"]
    assert any(result["proceed"] is False for result in before_results)
    assert any("blocked_close" in result["reasons"] for result in before_results)

    run_after_resp = client.post("/api/v1/hooks/run-after-close", json={"event": "close_done", "payload": {}})
    assert run_after_resp.status_code == 200
    after_results = run_after_resp.json()["results"]
    assert any(result["proceed"] is True for result in after_results)
    assert any("closed" in result["reasons"] for result in after_results)
