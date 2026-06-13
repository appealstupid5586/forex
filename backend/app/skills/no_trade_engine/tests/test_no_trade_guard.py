from datetime import datetime, timezone

from app.core.models import RobotState
from backend.app.skills.no_trade_engine.no_trade_guard import NoTradeGuardAgent


def test_no_trade_negative_on_session_window():
    state = RobotState(
        robot_id="r1",
        symbol="EURUSD",
        broker="mock",
        magic_number=1,
        fsm_state="BOOT",
    )
    market_state = {
        "tick": type("T", (), {"timestamp": datetime(2026, 1, 1, 5, 0, tzinfo=timezone.utc), "spread": 0.00002})(),
        "confidence": 0.8,
        "regime": "REGIME_UPTREND",
    }

    decision = NoTradeGuardAgent(settings=type("S", (), {"max_spread_points": 25.0, "tick_size": 0.00001, "max_consecutive_loss": 5})()).evaluate(state, market_state)

    assert not decision.allowed
    assert "NO_TRADE_SESSION_WINDOW" in decision.reasons


def test_no_trade_block_on_low_confidence():
    state = RobotState(
        robot_id="r2",
        symbol="EURUSD",
        broker="mock",
        magic_number=2,
        fsm_state="BOOT",
    )
    market_state = {
        "tick": type("T", (), {"timestamp": datetime(2026, 1, 1, 1, 0, tzinfo=timezone.utc), "spread": 0.00002})(),
        "confidence": 0.2,
        "regime": "REGIME_UPTREND",
    }

    decision = NoTradeGuardAgent(settings=type("S", (), {"max_spread_points": 25.0, "tick_size": 0.00001, "max_consecutive_loss": 5})()).evaluate(state, market_state)

    assert not decision.allowed
    assert "NO_TRADE_LOW_CONFIDENCE" in decision.reasons


def test_no_trade_block_on_drawdown_exceeded():
    state = RobotState(
        robot_id="r3",
        symbol="EURUSD",
        broker="mock",
        magic_number=3,
        fsm_state="BOOT",
        drawdown_pct=16.0,
    )
    market_state = {
        "tick": type("T", (), {"timestamp": datetime(2026, 1, 1, 1, 0, tzinfo=timezone.utc), "spread": 0.00002})(),
        "confidence": 0.8,
        "regime": "REGIME_UPTREND",
    }

    decision = NoTradeGuardAgent(settings=type("S", (), {"max_spread_points": 25.0, "tick_size": 0.00001, "max_consecutive_loss": 5})()).evaluate(state, market_state)

    assert not decision.allowed
    assert decision.action == "STOP"
    assert "NO_TRADE_DRAWDOWN" in decision.reasons
