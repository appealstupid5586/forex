from __future__ import annotations

from app.core.models import FsmState, RiskDecision, RobotState, RobotStatus
from backend.app.skills.shared.fsm import determine_next_state


class FsmBrainAgent:
    def next_state(self, state: RobotState, risk: RiskDecision, has_cycle: bool, surplus_active: bool = False) -> FsmState:
        next_state, next_status = determine_next_state(state=state, risk=risk, has_cycle=has_cycle, surplus_active=surplus_active)
        state.status = next_status
        return next_state
