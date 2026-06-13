from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings
from app.strategy.grid_math import calculate_grid

router = APIRouter(prefix="/api/v1/grid", tags=["grid"])
settings = get_settings()


class GridRequest(BaseModel):
    symbol: str = settings.default_symbol
    base_price: float
    current_price: float
    step_size: float = settings.default_step_size
    x_level: int = settings.default_x_level
    tick_size: float = settings.tick_size


@router.post("/calculate")
def calculate(req: GridRequest):
    return calculate_grid(**req.model_dump())
