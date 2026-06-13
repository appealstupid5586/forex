"""Structure Detection - HH-HL (Higher High-Higher Low) and LL-LH (Lower Low-Lower High)

Responsibility: Identify price structure patterns that indicate trend direction.
This is the MOST IMPORTANT detection criterion.
"""

from typing import List, Tuple, Optional
from datetime import datetime, timedelta
from .types import CandleData, StructureOutput, StructureType


class StructureDetector:
    """Detects HH-HL and LL-LH structures"""
    
    def __init__(self, lookback_bars: int = 20):
        """
        Args:
            lookback_bars: Number of bars to analyze for structure
        """
        self.lookback_bars = lookback_bars
    
    def detect(self, candles: List[CandleData]) -> StructureOutput:
        """Detect price structure from candlesticks
        
        Args:
            candles: List of candlestick data (oldest first)
            
        Returns:
            StructureOutput with detected structure and trend
        """
        if len(candles) < 4:
            return StructureOutput(
                structure=StructureType.UNCLEAR,
                trend="neutral",
                confidence=0.0
            )
        
        # Use recent bars for structure detection
        recent = candles[-self.lookback_bars:]
        
        # Find pivots
        hh, hl, ll, lh = self._find_pivots(recent)
        
        if hh is None or hl is None or ll is None or lh is None:
            return StructureOutput(
                structure=StructureType.UNCLEAR,
                trend="neutral",
                confidence=0.0
            )
        
        # Determine structure
        hh_hl_pattern = hh > ll and hl > lh
        ll_lh_pattern = ll < hh and lh < hl
        
        confidence = self._calculate_confidence(hh, hl, ll, lh)
        
        if hh_hl_pattern:
            return StructureOutput(
                structure=StructureType.HH_HL,
                trend="bullish",
                hh_value=hh,
                hl_value=hl,
                ll_value=ll,
                lh_value=lh,
                confidence=confidence
            )
        elif ll_lh_pattern:
            return StructureOutput(
                structure=StructureType.LL_LH,
                trend="bearish",
                hh_value=hh,
                hl_value=hl,
                ll_value=ll,
                lh_value=lh,
                confidence=confidence
            )
        else:
            return StructureOutput(
                structure=StructureType.UNCLEAR,
                trend="neutral",
                hh_value=hh,
                hl_value=hl,
                ll_value=ll,
                lh_value=lh,
                confidence=confidence
            )
    
    def _find_pivots(self, candles: List[CandleData]) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
        """Find highest high, highest low, lowest low, lowest high
        
        Returns:
            (HH, HL, LL, LH) tuples
        """
        if not candles:
            return None, None, None, None
        
        highs = [c.high for c in candles]
        lows = [c.low for c in candles]
        
        hh = max(highs)  # Highest High
        ll = min(lows)   # Lowest Low
        
        # Highest Low (highest of the low points)
        hl = max(lows)
        
        # Lowest High (lowest of the high points)
        lh = min(highs)
        
        return hh, hl, ll, lh
    
    def _calculate_confidence(self, hh: float, hl: float, ll: float, lh: float) -> float:
        """Calculate confidence score for structure detection
        
        Range: 0-1
        Higher when gaps between pivots are clearer
        """
        if hh == ll or hl == lh:
            return 0.0
        
        # Measure gap quality
        upside_gap = (hh - hl) / hl if hl != 0 else 0
        downside_gap = (ll - lh) / lh if lh != 0 else 0
        
        # Normalize to 0-1
        confidence = min(1.0, (abs(upside_gap) + abs(downside_gap)) / 2 * 10)
        
        return confidence
    
    def get_last_hh_hl(self, candles: List[CandleData]) -> Tuple[Optional[int], Optional[int]]:
        """Get indices of last HH and HL
        
        Returns:
            (hh_index, hl_index) or (None, None)
        """
        if len(candles) < 2:
            return None, None
        
        recent = candles[-self.lookback_bars:]
        highs = [c.high for c in recent]
        lows = [c.low for c in recent]
        
        hh_idx = highs.index(max(highs))
        hl_idx = lows.index(max(lows))
        
        return hh_idx, hl_idx
    
    def get_last_ll_lh(self, candles: List[CandleData]) -> Tuple[Optional[int], Optional[int]]:
        """Get indices of last LL and LH
        
        Returns:
            (ll_index, lh_index) or (None, None)
        """
        if len(candles) < 2:
            return None, None
        
        recent = candles[-self.lookback_bars:]
        highs = [c.high for c in recent]
        lows = [c.low for c in recent]
        
        ll_idx = lows.index(min(lows))
        lh_idx = highs.index(min(highs))
        
        return ll_idx, lh_idx
