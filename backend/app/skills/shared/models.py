"""Shared domain models for the skill registry."""

from dataclasses import dataclass


@dataclass
class Asset:
    symbol: str
    name: str
    exchange: str


@dataclass
class Trade:
    symbol: str
    quantity: float
    entry_price: float
    exit_price: float
    profit_loss: float
