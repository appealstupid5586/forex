"""Volatility Detection - ATR, Expansion, Contraction

Responsibility: Analyze market volatility to assess trend strength and reversal risk.
"""

from typing import List
from .types import CandleData, VolatilityOutput, VolatilityState


class VolatilityDetector:
    """Analyzes volatility using ATR and expansion/contraction patterns"""
    
    def __init__(self, atr_period: int = 14):
        """
        Args:
            atr_period: Period for ATR calculation (default 14)
        """
        self.atr_period = atr_period
    
    def detect(self, candles: List[CandleData]) -> VolatilityOutput:
        """Detect volatility state from candlesticks
        
        Args:
            candles: List of candlestick data (oldest first)
            
        Returns:
            VolatilityOutput with ATR analysis and expansion/contraction state
        """
        if len(candles) < self.atr_period:
            return VolatilityOutput(
                atr_value=0.0,
                atr_state=VolatilityState.MEDIUM,
                atr_trend="stable",
                expansion_level="medium",
                contraction_level="medium",
                confidence=0.0
            )
        
        # Calculate ATR
        atr = self._calculate_atr(candles)
        
        # Determine ATR state (relative to average)
        atr_state = self._classify_atr_state(candles, atr)
        
        # Determine ATR trend
        atr_trend = self._determine_atr_trend(candles)
        
        # Analyze expansion/contraction
        expansion_level, contraction_level = self._analyze_volatility_cycles(candles)
        
        # Calculate confidence
        confidence = self._calculate_confidence(candles, atr)
        
        return VolatilityOutput(
            atr_value=atr,
            atr_state=atr_state,
            atr_trend=atr_trend,
            expansion_level=expansion_level,
            contraction_level=contraction_level,
            confidence=confidence
        )
    
    def _calculate_atr(self, candles: List[CandleData]) -> float:
        """Calculate Average True Range"""
        if len(candles) < self.atr_period:
            return 0.0
        
        tr_values = []
        
        for i in range(len(candles)):
            current = candles[i]
            
            if i == 0:
                tr = current.high - current.low
            else:
                prev = candles[i - 1]
                tr1 = current.high - current.low
                tr2 = abs(current.high - prev.close)
                tr3 = abs(current.low - prev.close)
                tr = max(tr1, tr2, tr3)
            
            tr_values.append(tr)
        
        # Use the last atr_period values
        atr = sum(tr_values[-self.atr_period:]) / self.atr_period
        return atr
    
    def _classify_atr_state(self, candles: List[CandleData], current_atr: float) -> VolatilityState:
        """Classify ATR as LOW, MEDIUM, or HIGH"""
        if len(candles) < 50:
            return VolatilityState.MEDIUM
        
        # Calculate historical ATR average
        historical_atrs = []
        for i in range(len(candles) - 50, len(candles)):
            subset = candles[:i + 1]
            if len(subset) >= self.atr_period:
                atr = self._calculate_atr(subset)
                historical_atrs.append(atr)
        
        if not historical_atrs:
            return VolatilityState.MEDIUM
        
        avg_atr = sum(historical_atrs) / len(historical_atrs)
        
        if current_atr > avg_atr * 1.3:
            return VolatilityState.HIGH
        elif current_atr < avg_atr * 0.7:
            return VolatilityState.LOW
        else:
            return VolatilityState.MEDIUM
    
    def _determine_atr_trend(self, candles: List[CandleData]) -> str:
        """Determine if ATR is increasing, decreasing, or stable"""
        if len(candles) < 10:
            return "stable"
        
        recent_atr = self._calculate_atr(candles[-10:])
        older_atr = self._calculate_atr(candles[-20:-10]) if len(candles) >= 20 else recent_atr
        
        if recent_atr > older_atr * 1.05:
            return "increasing"
        elif recent_atr < older_atr * 0.95:
            return "decreasing"
        else:
            return "stable"
    
    def _analyze_volatility_cycles(self, candles: List[CandleData]) -> tuple:
        """Analyze expansion and contraction cycles"""
        if len(candles) < 5:
            return "medium", "medium"
        
        # Get recent range sizes
        ranges = [c.high - c.low for c in candles[-10:]]
        avg_range = sum(ranges) / len(ranges)
        current_range = ranges[-1]
        
        # Expansion when current range > average
        if current_range > avg_range * 1.2:
            expansion_level = "high"
        elif current_range > avg_range * 1.05:
            expansion_level = "medium"
        else:
            expansion_level = "low"
        
        # Contraction when current range < average
        if current_range < avg_range * 0.8:
            contraction_level = "high"
        elif current_range < avg_range * 0.95:
            contraction_level = "medium"
        else:
            contraction_level = "low"
        
        return expansion_level, contraction_level
    
    def _calculate_confidence(self, candles: List[CandleData], atr: float) -> float:
        """Calculate confidence score"""
        if len(candles) < self.atr_period:
            return 0.0
        
        # More bars = higher confidence
        bar_confidence = min(1.0, len(candles) / (self.atr_period * 3))
        
        # ATR > 0 = higher confidence
        atr_confidence = min(1.0, atr / (atr + 0.0001))
        
        return (bar_confidence + atr_confidence) / 2
