"""Market Analysis Skill - Regime Detection System

Based on Dow Theory + Price Action + Regime-First Architecture

Core Principle:
  Market → Regime → Trend Strength → Setup → Risk → Execution → Journal → Memory → Evolution
"""

from .regime_detector import RegimeDetector
from .structure_detector import StructureDetector
from .trend_strength import TrendStrengthAnalyzer
from .momentum_detector import MomentumDetector
from .volatility_detector import VolatilityDetector
from .types import RegimeType, MarketAnalysisOutput

__all__ = [
    "RegimeDetector",
    "StructureDetector",
    "TrendStrengthAnalyzer",
    "MomentumDetector",
    "VolatilityDetector",
    "RegimeType",
    "MarketAnalysisOutput",
]

__version__ = "1.0.0"
