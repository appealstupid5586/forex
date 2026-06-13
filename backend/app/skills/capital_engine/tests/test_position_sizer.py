from datetime import datetime, timezone

from app.core.models import RobotState
from backend.app.skills.capital_engine.position_sizer import PositionSizer


def test_capital_position_sizer_uses_weak_trend():
    state = RobotState(
        robot_id="r1",
        symbol="EURUSD",
        broker="mock",
        magic_number=1,
        fsm_state="BOOT",
        balance=10000.0,
        drawdown_pct=2.0,
        consecutive_loss=0,
    )
    market_state = {
        "tick": type("T", (), {"timestamp": datetime(2026, 1, 1, 1, 0, tzinfo=timezone.utc), "spread": 0.00002})(),
        "regime": "REGIME_TRANSITION",
        "stop_distance": 50,
    }

    result = PositionSizer(settings=type("S", (), {"tick_size": 0.00001, "max_exposure_lots": 0.1, "max_consecutive_loss": 5})()).size_position(state, market_state)

    assert result["risk_size"] == 0.5
    assert result["regime"] == "REGIME_TRANSITION"
    assert result["position_size"] > 0
