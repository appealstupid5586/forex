from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.runtime import evolution_agent, genes_memory, optimizer
from app.skills.backtesting import run_backtest as execute_backtest
from hooks.schemas import HookContext

router = APIRouter(prefix="/api/v1/backtest", tags=["backtest"])


class BacktestRequest(BaseModel):
    symbol: str = "EURUSD"
    timeframe: str = "M1"
    step_range: list[float] = [0.0005, 0.001, 0.0015]
    x_range: list[int] = [1, 2, 3]
    risk_range: list[float] = [0.25, 0.5, 1.0]


class BacktestAnalyzeRequest(BaseModel):
    strategy: dict[str, Any] = Field(default_factory=dict)
    market_data: dict[str, Any] = Field(default_factory=dict)
    config: dict[str, Any] = Field(default_factory=dict)


@router.post("/run")
def run_backtest(req: BacktestRequest):
    gene = optimizer.run(req.symbol, req.timeframe, req.step_range, req.x_range, req.risk_range)
    genes_memory.remember(gene)
    return {"winner_gene_set": gene}


@router.post("/analyze")
def analyze_backtest(req: BacktestAnalyzeRequest):
    result = execute_backtest(req.strategy, req.market_data, req.config)
    hook_results = evolution_agent.run_after_backtest(
        HookContext(event="after_backtest", payload={"result": result}, metadata={"skill": "backtesting"})
    )
    return {"result": result, "hooks": [hook.__dict__ for hook in hook_results]}
