from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.runtime import genes_memory

router = APIRouter(prefix="/api/v1/genes", tags=["winner-genes"])


class PromoteRequest(BaseModel):
    symbol: str = "EURUSD"
    timeframe: str = "M1"


@router.get("/winners")
def winners():
    return genes_memory.winners()


@router.post("/promote")
def promote(req: PromoteRequest):
    return genes_memory.promote(req.symbol, req.timeframe)
