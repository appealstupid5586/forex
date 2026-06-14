"""Capital Engine position sizing and risk management."""
from __future__ import annotations

from typing import Any

from app.core.models import MarketTick

METADATA = {
    "name": "capital_engine",
    "kind": "capital",
}


class PositionSizer:
    """Compute risk size and position size for approved trades."""

    def __init__(self, settings: Any):
        self.settings = settings

    def size_position(self, state: Any, market_state: dict[str, Any]) -> dict[str, float]:
        regime = str(market_state.get("regime", "REGIME_TRANSITION"))
        risk_multiple = self._risk_multiple_for_regime(regime)
        risk_multiple *= self._drawdown_scale(state)
        risk_multiple *= self._loss_streak_scale(state)

        policy = self._trade_policy_for_regime(regime)
        target_risk = max(0.0, min(3.0, risk_multiple))
        position_size = self._estimate_position_size(state, market_state, target_risk)

        return {
            "regime": regime,
            "risk_multiple": round(risk_multiple, 4),
            "risk_size": round(target_risk, 4),
            "position_size": round(position_size, 6),
            "allow_pyramiding": policy["allow_pyramiding"],
            "allow_scale_in": policy["allow_scale_in"],
            "allow_wider_trailing_stop": policy["allow_wider_trailing_stop"],
        }

    def _risk_multiple_for_regime(self, regime: str) -> float:
        if regime == "REGIME_STRONG_BULL":
            return 3.0
        if regime == "REGIME_STRONG_BEAR":
            return 3.0
        if regime == "REGIME_UPTREND":
            return 1.0
        if regime == "REGIME_DOWNTREND":
            return 1.0
        return 0.5

    def _trade_policy_for_regime(self, regime: str) -> dict[str, bool]:
        if regime == "REGIME_STRONG_BULL":
            return {
                "allow_pyramiding": True,
                "allow_scale_in": True,
                "allow_wider_trailing_stop": True,
            }
        if regime == "REGIME_STRONG_BEAR":
            return {
                "allow_pyramiding": False,
                "allow_scale_in": True,
                "allow_wider_trailing_stop": False,
            }
        return {
            "allow_pyramiding": False,
            "allow_scale_in": False,
            "allow_wider_trailing_stop": False,
        }

    def _drawdown_scale(self, state: Any) -> float:
        drawdown = float(getattr(state, "drawdown_pct", 0.0))
        if drawdown < 5.0:
            return 1.0
        if drawdown < 10.0:
            return 0.5
        if drawdown < 15.0:
            return 0.25
        return 0.0

    def _loss_streak_scale(self, state: Any) -> float:
        losses = int(getattr(state, "consecutive_loss", 0))
        if losses >= getattr(self.settings, "max_consecutive_loss", 5):
            return 0.0
        if losses >= 3:
            return 0.5
        return 1.0

    def _estimate_position_size(self, state: Any, market_state: dict[str, Any], risk_size: float) -> float:
        balance = float(getattr(state, "balance", 0.0))
        tick = market_state.get("tick")
        if tick is None:
            return 0.0

        stop_distance = float(market_state.get("stop_distance", 0.0))
        if stop_distance <= 0.0:
            return 0.0

        trade_risk = stop_distance * getattr(self.settings, "tick_size", 0.00001)
        if trade_risk <= 0.0:
            return 0.0

        return min(balance * risk_size / trade_risk, getattr(self.settings, "max_exposure_lots", 0.10))
