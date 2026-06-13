from __future__ import annotations

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator, model_validator

from backend.app.skills.market_analysis import (
    detect_momentum,
    detect_regime,
    detect_structure,
    detect_volatility,
)

router = APIRouter(prefix="/api/v1/market", tags=["market"])


class OHLCVCandle(BaseModel):
    timestamp: datetime | str | int | None = Field(
        None,
        description="Optional candle timestamp. Can be an ISO 8601 string, integer epoch, or datetime.",
    )
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
    ohlcv: list[OHLCVCandle] = Field(
        ..., min_length=6, description="List of validated OHLCV candle records. Minimum 6 candles for meaningful analysis.")

    @field_validator("ohlcv", mode="before")
    @classmethod
    def validate_minimum_candles(cls, values: Any) -> Any:
        if not isinstance(values, list):
            raise TypeError("ohlcv must be a list of candle objects")
        if len(values) < 6:
            raise ValueError("ohlcv list must contain at least 6 candle records")
        return values

    @model_validator(mode="after")
    @classmethod
    def validate_timestamps(cls, values: "MarketOHLCVRequest") -> "MarketOHLCVRequest":
        # Collect indices and original timestamp values
        indexed = [(i, item) for i, item in enumerate(values.ohlcv) if item.timestamp is not None]
        if not indexed:
            return values

        parsed_ns = []
        parsed_ts = []
        for idx, item in indexed:
            ts = item.timestamp
            try:
                # integers/floats: treat as epoch seconds (UTC)
                if isinstance(ts, (int, float)):
                    p = pd.to_datetime(int(ts), unit="s", utc=True)
                elif isinstance(ts, str):
                    # parse preserving tz info; require tz-aware strings
                    p = pd.to_datetime(ts, utc=False, errors="raise")
                    if p.tzinfo is None:
                        raise ValueError("string timestamps must include timezone information")
                    p = p.tz_convert("UTC")
                elif isinstance(ts, datetime):
                    if ts.tzinfo is None:
                        raise ValueError("datetime timestamps must be timezone-aware")
                    p = pd.Timestamp(ts).tz_convert("UTC")
                else:
                    # fallback: try pandas generic parse and require tz
                    p = pd.to_datetime(ts, utc=False, errors="raise")
                    if p.tzinfo is None:
                        raise ValueError("timestamps must be timezone-aware or epoch integers")
                    p = p.tz_convert("UTC")
            except Exception as exc:  # pragma: no cover - parsing errors are rare in tests
                raise ValueError(f"unable to parse ohlcv timestamp at index {idx}: {exc}")

            parsed_ts.append(p)
            parsed_ns.append(int(p.value))

        # uniqueness check based on nanosecond epoch
        if len(set(parsed_ns)) != len(parsed_ns):
            raise ValueError("ohlcv timestamps must be unique when provided")

        # monotonic increasing check
        for a, b in zip(parsed_ns, parsed_ns[1:]):
            if a >= b:
                raise ValueError("ohlcv timestamps must be monotonic increasing")

        # normalize timestamps back into the model as ISO UTC strings
        for (idx, item), p in zip(indexed, parsed_ts):
            # ISO format with Z indicator for UTC
            item.timestamp = p.tz_convert("UTC").isoformat()

        return values


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


@router.post("/validate")
def validate_market_ohlcv(payload: MarketOHLCVRequest):
    normalized = [item.timestamp for item in payload.ohlcv if item.timestamp is not None]
    return {"valid": True, "total_candles": len(payload.ohlcv), "normalized_timestamps": normalized}
