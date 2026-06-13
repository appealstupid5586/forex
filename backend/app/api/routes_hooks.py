from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.runtime import evolution_agent
from hooks.schemas import HookContext

router = APIRouter(prefix="/api/v1/hooks", tags=["hooks"])


class HookRequest(BaseModel):
    event: str = "manual"
    payload: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


@router.get("/available")
def available_hooks():
    return {
        "before_signal": [h.__name__ for h in evolution_agent.before_signal_hooks],
        "after_signal": [h.__name__ for h in evolution_agent.after_signal_hooks],
        "before_trade": [h.__name__ for h in evolution_agent.before_trade_hooks],
        "after_trade": [h.__name__ for h in evolution_agent.after_trade_hooks],
        "before_close": [h.__name__ for h in evolution_agent.before_close_hooks],
        "after_close": [h.__name__ for h in evolution_agent.after_close_hooks],
        "after_backtest": [h.__name__ for h in evolution_agent.after_backtest_hooks],
    }


@router.post("/reload")
def reload_hooks():
    try:
        evolution_agent._discover_hooks()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.post("/run-before-signal")
def run_before_signal(req: HookRequest):
    ctx = HookContext(event=req.event, payload=req.payload, metadata=req.metadata)
    results = evolution_agent.run_before_signal(ctx)
    return {"results": [r.__dict__ for r in results]}


@router.post("/run-after-signal")
def run_after_signal(req: HookRequest):
    ctx = HookContext(event=req.event, payload=req.payload, metadata=req.metadata)
    results = evolution_agent.run_after_signal(ctx)
    return {"results": [r.__dict__ for r in results]}


@router.post("/run-before-trade")
def run_before_trade(req: HookRequest):
    ctx = HookContext(event=req.event, payload=req.payload, metadata=req.metadata)
    results = evolution_agent.run_before_trade(ctx)
    return {"results": [r.__dict__ for r in results]}


@router.post("/run-after-trade")
def run_after_trade(req: HookRequest):
    ctx = HookContext(event=req.event, payload=req.payload, metadata=req.metadata)
    results = evolution_agent.run_after_trade(ctx)
    return {"results": [r.__dict__ for r in results]}


@router.post("/run-before-close")
def run_before_close(req: HookRequest):
    ctx = HookContext(event=req.event, payload=req.payload, metadata=req.metadata)
    results = evolution_agent.run_before_close(ctx)
    return {"results": [r.__dict__ for r in results]}


@router.post("/run-after-close")
def run_after_close(req: HookRequest):
    ctx = HookContext(event=req.event, payload=req.payload, metadata=req.metadata)
    results = evolution_agent.run_after_close(ctx)
    return {"results": [r.__dict__ for r in results]}


@router.post("/run-after-backtest")
def run_after_backtest(req: HookRequest):
    ctx = HookContext(event=req.event, payload=req.payload, metadata=req.metadata)
    results = evolution_agent.run_after_backtest(ctx)
    return {"results": [r.__dict__ for r in results]}
