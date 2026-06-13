from app.core.config import Settings
from app.core.models import MarketTick, RobotState
from backend.app.skills.risk_engine.risk_guard import RiskGuardAgent


def test_risk_guard_blocks_drawdown():
    settings = Settings(max_drawdown_pct=10)
    guard = RiskGuardAgent(settings)
    state = RobotState(robot_id="r", symbol="EURUSD", broker="mock", magic_number=1, drawdown_pct=11)
    decision = guard.evaluate(state)
    assert decision.allowed is False
    assert decision.action == "FREEZE"


def test_risk_guard_blocks_spread():
    settings = Settings(max_spread_points=10, tick_size=0.00001)
    guard = RiskGuardAgent(settings)
    state = RobotState(robot_id="r", symbol="EURUSD", broker="mock", magic_number=1)
    decision = guard.evaluate(state, MarketTick(symbol="EURUSD", bid=1.0, ask=1.0003))
    assert decision.allowed is False
    assert decision.action == "PAUSE_NEW_ENTRY"
