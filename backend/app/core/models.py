from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class RobotStatus(str, Enum):
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    FROZEN = "FROZEN"
    COOLDOWN = "COOLDOWN"


class FsmState(str, Enum):
    BOOT = "BOOT"
    RESTORE_STATE = "RESTORE_STATE"
    SYNC_BROKER = "SYNC_BROKER"
    IDLE = "IDLE"
    BUILD_GRID = "BUILD_GRID"
    HEDGE_ACTIVE = "HEDGE_ACTIVE"
    SURPLUS_ACTIVE = "SURPLUS_ACTIVE"
    TAKE_PROFIT = "TAKE_PROFIT"
    SWEEP = "SWEEP"
    FREEZE = "FREEZE"


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class MarketTick(BaseModel):
    symbol: str
    bid: float
    ask: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2

    @property
    def spread(self) -> float:
        return abs(self.ask - self.bid)


class RobotState(BaseModel):
    robot_id: str
    symbol: str
    broker: str
    magic_number: int
    status: RobotStatus = RobotStatus.STOPPED
    current_cycle_id: str | None = None
    fsm_state: FsmState = FsmState.BOOT
    equity: float = 10_000.0
    balance: float = 10_000.0
    drawdown_pct: float = 0.0
    margin_level_pct: float = 9999.0
    consecutive_loss: int = 0
    last_step: int = 0
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GridState(BaseModel):
    symbol: str
    base_price: float
    current_price: float
    step_size: float
    x_level: int
    tick_size: float
    current_step: int
    step_price: float
    upper_level: float
    lower_level: float
    step_distance: float


class Order(BaseModel):
    order_id: str = Field(default_factory=lambda: str(uuid4()))
    broker_order_id: str | None = None
    robot_id: str
    cycle_id: str
    symbol: str
    side: OrderSide
    lot: float
    entry_price: float
    magic_number: int
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: datetime | None = None
    pnl: float = 0.0


class HedgeCycle(BaseModel):
    cycle_id: str = Field(default_factory=lambda: str(uuid4()))
    symbol: str
    buy_orders: list[Order] = Field(default_factory=list)
    sell_orders: list[Order] = Field(default_factory=list)
    hedge_ratio: float = 1.0
    surplus_side: Literal["BUY", "SELL", "NONE"] = "NONE"
    realized_pnl: float = 0.0
    floating_pnl: float = 0.0
    status: str = "OPEN"


class RiskDecision(BaseModel):
    allowed: bool
    action: str = "ALLOW"
    reasons: list[str] = Field(default_factory=list)


class WinnerGene(BaseModel):
    symbol: str
    timeframe: str
    step_size: float
    x_level: int
    risk_pct: float
    atr_period: int
    profit_factor: float
    max_drawdown: float
    recovery_factor: float
    win_rate: float = 0.0
    expectancy: float = 0.0
    promoted: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
