"""Type definitions for market analysis"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime


class RegimeType(str, Enum):
    """Market regime classifications"""
    SIDEWAY = "SIDEWAY"
    UPTREND = "UPTREND"
    DOWNTREND = "DOWNTREND"
    STRONG_BULL = "STRONG_BULL"
    STRONG_BEAR = "STRONG_BEAR"
    TRANSITION = "TRANSITION"


class StructureType(str, Enum):
    """Price structure patterns"""
    HH_HL = "HH_HL"  # Higher High - Higher Low (bullish)
    LL_LH = "LL_LH"  # Lower Low - Lower High (bearish)
    UNCLEAR = "UNCLEAR"  # No clear structure


class TrendStrength(str, Enum):
    """Trend strength classification"""
    WEAK = "WEAK"
    NORMAL = "NORMAL"
    STRONG = "STRONG"


class VolatilityState(str, Enum):
    """Volatility states"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXPANSION = "EXPANSION"
    CONTRACTION = "CONTRACTION"


class MomentumState(str, Enum):
    """Momentum states"""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


@dataclass
class CandleData:
    """OHLC candlestick data"""
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: datetime


@dataclass
class StructureOutput:
    """Structure detection output"""
    structure: StructureType
    trend: str  # "bullish" or "bearish"
    hh_value: Optional[float] = None
    hl_value: Optional[float] = None
    ll_value: Optional[float] = None
    lh_value: Optional[float] = None
    confidence: float = 0.0


@dataclass
class VolatilityOutput:
    """Volatility detection output"""
    atr_value: float
    atr_state: VolatilityState
    atr_trend: str  # "increasing", "decreasing", "stable"
    expansion_level: str  # "high", "medium", "low"
    contraction_level: str  # "high", "medium", "low"
    confidence: float = 0.0


@dataclass
class MomentumOutput:
    """Momentum detection output"""
    momentum: MomentumState
    macd_value: float
    macd_signal: float
    macd_histogram: float
    ema20_slope: float
    ema_alignment: str  # "perfect", "good", "weak", "none"
    confidence: float = 0.0


@dataclass
class TrendStrengthOutput:
    """Trend strength output"""
    strength: TrendStrength
    score: float  # 0-1
    factors: Dict[str, float]  # breakdown of contributing factors


@dataclass
class MarketAnalysisOutput:
    """Complete market analysis output"""
    regime: RegimeType
    structure: StructureOutput
    momentum: MomentumOutput
    volatility: VolatilityOutput
    trend_strength: TrendStrengthOutput
    timestamp: datetime
    
    # Risk and execution guidance
    risk_multiplier: float  # 0.5 for SIDEWAY, 1.0 for normal, 1.5+ for strong
    allow_trade: bool  # False for TRANSITION
    allow_pyramiding: bool  # True for STRONG regimes
    
    # Additional metadata
    confidence: float  # 0-1 overall confidence
    journal_data: Dict[str, Any]  # For memory integration
