from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import get_settings

router = APIRouter(prefix="/api/ctrader", tags=["ctrader"])
settings = get_settings()

CTRADER_SESSION: dict[str, Any] = {
    "broker": "ctrader",
    "connected": False,
    "environment": "demo",
    "account_id": None,
    "access_token": None,
    "app_id": None,
    "app_secret": None,
    "last_error": None,
}


class ConnectRequest(BaseModel):
    access_token: str | None = None
    app_id: str | None = None
    app_secret: str | None = None
    account_id: str | None = None
    environment: str = Field(default="demo")


class OrderRequest(BaseModel):
    symbol: str
    side: str = "buy"
    volume: float = Field(default=0.01, ge=0.00001)
    order_type: str = "market"
    price: float | None = None
    comment: str | None = None


def _session_payload() -> dict[str, Any]:
    return {
        "broker": "ctrader",
        "connected": bool(CTRADER_SESSION.get("connected")),
        "environment": CTRADER_SESSION.get("environment", "demo"),
        "account_id": CTRADER_SESSION.get("account_id"),
        "mode": "live" if settings.allow_live_execution else "demo",
        "last_error": CTRADER_SESSION.get("last_error"),
    }


@router.get("/status")
def status() -> dict[str, Any]:
    return _session_payload()


@router.post("/connect")
def connect(payload: ConnectRequest) -> dict[str, Any]:
    if not payload.access_token and not (payload.app_id and payload.app_secret):
        raise HTTPException(status_code=400, detail="Provide an access_token or app credentials")

    CTRADER_SESSION.update(
        {
            "connected": True,
            "environment": payload.environment or "demo",
            "account_id": payload.account_id,
            "access_token": payload.access_token,
            "app_id": payload.app_id,
            "app_secret": payload.app_secret,
            "last_error": None,
        }
    )
    return {
        "broker": "ctrader",
        "connected": True,
        "success": True,
        "environment": CTRADER_SESSION["environment"],
        "account_id": CTRADER_SESSION["account_id"],
        "message": "cTrader session ready for OAuth token exchange",
    }


@router.post("/disconnect")
def disconnect() -> dict[str, Any]:
    CTRADER_SESSION.update(
        {
            "connected": False,
            "account_id": None,
            "access_token": None,
            "app_id": None,
            "app_secret": None,
            "last_error": None,
        }
    )
    return {"broker": "ctrader", "connected": False, "success": True}


@router.get("/account")
def account() -> dict[str, Any]:
    if not CTRADER_SESSION.get("connected"):
        return {"broker": "ctrader", "connected": False, "account_id": None, "message": "Not connected"}

    return {
        "broker": "ctrader",
        "connected": True,
        "account_id": CTRADER_SESSION.get("account_id") or "demo-account",
        "environment": CTRADER_SESSION.get("environment", "demo"),
        "balance": 100000.0,
        "equity": 100000.0,
        "margin": 0.0,
        "currency": "USD",
        "mode": "live" if settings.allow_live_execution else "demo",
    }


@router.get("/positions")
def positions() -> dict[str, Any]:
    return {"broker": "ctrader", "connected": bool(CTRADER_SESSION.get("connected")), "positions": []}


@router.get("/orders")
def orders() -> dict[str, Any]:
    return {"broker": "ctrader", "connected": bool(CTRADER_SESSION.get("connected")), "orders": []}


@router.post("/order")
def place_order(payload: OrderRequest) -> dict[str, Any]:
    if not CTRADER_SESSION.get("connected"):
        raise HTTPException(status_code=400, detail="Connect to cTrader before placing orders")

    return {
        "broker": "ctrader",
        "success": True,
        "order_id": f"ctrader-{abs(hash(payload.symbol)) % 100000:05d}",
        "symbol": payload.symbol,
        "side": payload.side.upper(),
        "volume": payload.volume,
        "order_type": payload.order_type,
        "message": "cTrader order submission stub is ready for production API wiring",
    }


@router.delete("/order/{order_id}")
def cancel_order(order_id: str) -> dict[str, Any]:
    if not CTRADER_SESSION.get("connected"):
        raise HTTPException(status_code=400, detail="Connect to cTrader before cancelling orders")

    return {"broker": "ctrader", "success": True, "order_id": order_id, "message": "cTrader cancellation stub"}


@router.get("/quote")
def quote(symbol: str | None = None) -> dict[str, Any]:
    symbol = symbol or "EURUSD"
    return {
        "broker": "ctrader",
        "symbol": symbol,
        "bid": 1.1000,
        "ask": 1.1004,
        "spread": 0.0004,
        "timestamp": "stub",
    }
