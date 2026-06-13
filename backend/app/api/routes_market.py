from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel, Field
from pydantic import model_validator

from backend.app.skills.market_analysis import (
    detect_momentum,
    detect_regime,
    detect_structure,
    detect_volatility,
)

router = APIRouter(prefix="/api/v1/market", tags=["market"])


class OHLCVCandle(BaseModel):
    timestamp: str | int | None = Field(None, description="Optional candle timestamp.")
    open: float = Field(..., ge=0.0, description="Open price for the candle.")
    high: float = Field(..., ge=0.0, description="High price for the candle.")
    low: float = Field(..., ge=0.0, description="Low price for the candle.")
    close: float = Field(..., ge=0.0, description="Close price for the candle.")
    volume: float | None = Field(None, ge=0.0, description="Optional traded volume.")

    @model_validator(mode="after")
    def check_price_relationships(cls, values: "OHLCVCandle") -> "OHLCVCandle":
        low = values.low
        high = values.high
        open_price = values.open
        close_price = values.close

        if high < max(open_price, close_price):
            raise ValueError("high must be greater than or equal to open and close")
        if low > min(open_price, close_price):
            raise ValueError("low must be less than or equal to open and close")
        if low > high:
            raise ValueError("low must be less than or equal to high")
        return values


class MarketOHLCVRequest(BaseModel):
    ohlcv: list[OHLCVCandle] = Field(..., description="List of validated OHLCV candle records.")


def _prepare_ohlcv(payload: MarketOHLCVRequest) -> pd.DataFrame:
    data = [item.dict(exclude_none=True) for item in payload.ohlcv]
    frame = pd.DataFrame(data)
    return frame


@router.post("/regime")
def detect_market_regime(payload: MarketOHLCVRequest):
    ohlcv = _prepare_ohlcv(payload)
    result = detect_regime(ohlcv)
    return {"regime_analysis": result}


@router.post("/structure")
def detect_market_structure(payload: MarketOHLCVRequest):
    ohlcv = _prepare_ohlcv(payload)
    result = detect_structure(ohlcv)
    return {"structure_analysis": result}


@router.post("/momentum")
def detect_market_momentum(payload: MarketOHLCVRequest):
    ohlcv = _prepare_ohlcv(payload)
    result = detect_momentum(ohlcv)
    return {"momentum_analysis": result}


@router.post("/volatility")
def detect_market_volatility(payload: MarketOHLCVRequest):
    ohlcv = _prepare_ohlcv(payload)
    result = detect_volatility(ohlcv)
    return {"volatility_analysis": result}
