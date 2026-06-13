from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.skills.portfolio_analysis import analyze_portfolio

router = APIRouter(prefix="/api/v1/portfolio", tags=["portfolio"])


class PortfolioRequest(BaseModel):
    portfolio: dict[str, Any] = Field(default_factory=dict)


@router.post("/analyze")
def analyze(req: PortfolioRequest):
    result = analyze_portfolio(req.portfolio)
    return {"result": result}
