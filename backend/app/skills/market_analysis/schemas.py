"""Schemas for market analysis skill results."""

from dataclasses import dataclass
from enum import Enum


class TrendDirection(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


@dataclass
class TrendResult:
    direction: TrendDirection
    confidence: float


@dataclass
class SupportResistanceLevel:
    supports: list[float]
    resistances: list[float]


@dataclass
class LiquidityProfile:
    average_volume: float
    latest_volume: float
    spike_detected: bool
