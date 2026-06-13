"""No Trade Engine guard implementation for the HedgeMath OS skill registry."""
from __future__ import annotations

from datetime import time, timezone
from typing import Any

from app.core.models import RiskDecision

METADATA = {
    "name": "no_trade_engine",
    "kind": "risk",
}


class NoTradeGuardAgent:
    """Judge for the NO TRADE ENGINE.

    This component decides whether the robot is permitted to trade at all.
    """

    def __init__(self, settings: Any):
        self.settings = settings

    def evaluate(self, state: Any, market_state: dict[str, Any]) -> RiskDecision:
        reasons: list[str] = []
        allowed = True
        action = "ALLOW"

        if self._is_end_of_day(market_state):
            allowed = False
            action = "STOP"
            reasons.append("NO_TRADE_END_OF_DAY")

        if self._is_outside_trading_window(market_state):
            allowed = False
            action = "PAUSE_NEW_ENTRY"
            reasons.append("NO_TRADE_SESSION_WINDOW")

        if self._is_low_confidence(market_state):
            allowed = False
            action = "PAUSE_NEW_ENTRY"
            reasons.append("NO_TRADE_LOW_CONFIDENCE")

        if self._is_transition_regime(market_state):
            allowed = False
            action = "PAUSE_NEW_ENTRY"
            reasons.append("NO_TRADE_TRANSITION")

        if self._is_sideway_regime(market_state):
            allowed = False
            action = "PAUSE_NEW_ENTRY"
            reasons.append("NO_TRADE_SIDEWAY")

        if self._is_news_event(market_state):
            allowed = False
            action = "PAUSE_NEW_ENTRY"
            reasons.append("NO_TRADE_NEWS")

        if self._is_spread_expansion(market_state):
            allowed = False
            action = "PAUSE_NEW_ENTRY"
            reasons.append("NO_TRADE_SPREAD")

        if self._is_market_chaos(market_state):
            allowed = False
            action = "PAUSE_NEW_ENTRY"
            reasons.append("NO_TRADE_CHAOS")

        if self._is_drawdown_exceeded(state):
            allowed = False
            action = "STOP"
            reasons.append("NO_TRADE_DRAWDOWN")

        if self._is_loss_streak(state):
            allowed = False
            action = "PAUSE_NEW_ENTRY"
            reasons.append("NO_TRADE_LOSS_STREAK")

        if self._is_over_exposure(state):
            allowed = False
            action = "PAUSE_NEW_ENTRY"
            reasons.append("NO_TRADE_OVER_EXPOSURE")

        if self._is_correlation_risk(state):
            allowed = False
            action = "PAUSE_NEW_ENTRY"
            reasons.append("NO_TRADE_CORRELATION")

        if self._is_session_weak(state):
            allowed = False
            action = "PAUSE_NEW_ENTRY"
            reasons.append("NO_TRADE_SESSION")

        return RiskDecision(allowed=allowed, action=action, reasons=reasons)

    def _is_end_of_day(self, market_state: dict[str, Any]) -> bool:
        tick = market_state.get("tick")
        if tick is None:
            return False
        local_ts = tick.timestamp.astimezone(timezone.utc)
        end_of_day = time(12, 0)  # 19:00 GMT+7 is 12:00 UTC
        return local_ts.time() >= end_of_day

    def _is_outside_trading_window(self, market_state: dict[str, Any]) -> bool:
        tick = market_state.get("tick")
        if tick is None:
            return False
        local_ts = tick.timestamp.astimezone(timezone.utc)
        asia_start = time(0, 0)  # 07:00 GMT+7 = 00:00 UTC
        asia_end = time(4, 0)  # 11:00 GMT+7 = 04:00 UTC
        europe_start = time(7, 0)  # 14:00 GMT+7 = 07:00 UTC
        europe_end = time(12, 0)  # 19:00 GMT+7 = 12:00 UTC
        if asia_start <= local_ts.time() < asia_end:
            return False
        if europe_start <= local_ts.time() < europe_end:
            return False
        return True

    def _is_low_confidence(self, market_state: dict[str, Any]) -> bool:
        confidence = float(market_state.get("confidence", 0.0))
        return confidence < 0.4

    def _is_transition_regime(self, market_state: dict[str, Any]) -> bool:
        regime = str(market_state.get("regime", ""))
        return regime == "REGIME_TRANSITION"

    def _is_sideway_regime(self, market_state: dict[str, Any]) -> bool:
        regime = str(market_state.get("regime", ""))
        return regime == "REGIME_SIDEWAY"

    def _is_news_event(self, market_state: dict[str, Any]) -> bool:
        return bool(market_state.get("news_event", False))

    def _is_spread_expansion(self, market_state: dict[str, Any]) -> bool:
        tick = market_state.get("tick")
        max_spread = getattr(self.settings, "max_spread_points", 25.0) * getattr(self.settings, "tick_size", 0.00001)
        return tick is not None and tick.spread > max_spread

    def _is_market_chaos(self, market_state: dict[str, Any]) -> bool:
        return bool(market_state.get("market_chaos", False))

    def _is_drawdown_exceeded(self, state: Any) -> bool:
        return float(getattr(state, "drawdown_pct", 0.0)) > 15.0

    def _is_loss_streak(self, state: Any) -> bool:
        return getattr(state, "consecutive_loss", 0) >= getattr(self.settings, "max_consecutive_loss", 5)

    def _is_over_exposure(self, state: Any) -> bool:
        return float(getattr(state, "margin_level_pct", 9999.0)) < 25.0

    def _is_correlation_risk(self, state: Any) -> bool:
        return float(getattr(state, "correlation_score", 0.0)) >= 0.8

    def _is_session_weak(self, state: Any) -> bool:
        return float(getattr(state, "session_performance", 1.0)) < 0.8


def evaluate_no_trade(settings: Any, state: Any, market_state: dict[str, Any]) -> RiskDecision:
    return NoTradeGuardAgent(settings).evaluate(state, market_state)
