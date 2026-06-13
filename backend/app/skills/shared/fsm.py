"""Finite state machine transition logic moved out of the backend agent."""

from __future__ import annotations

from app.core.models import FsmState, RiskDecision, RobotState, RobotStatus


def determine_next_state(state: RobotState, risk: RiskDecision, has_cycle: bool, surplus_active: bool = False) -> tuple[FsmState, RobotStatus]:
    if not risk.allowed:
        if risk.action == "FREEZE":
            return FsmState.FREEZE, RobotStatus.FROZEN
        if risk.action in {"COOLDOWN", "PAUSE_EXECUTION", "PAUSE_NEW_ENTRY"}:
            return FsmState.IDLE, RobotStatus.COOLDOWN
    if state.status == RobotStatus.STOPPED:
        return FsmState.IDLE, RobotStatus.STOPPED
    if state.fsm_state in {FsmState.BOOT, FsmState.RESTORE_STATE}:
        return FsmState.SYNC_BROKER, state.status
    if not has_cycle:
        return FsmState.BUILD_GRID, state.status
    if surplus_active:
        return FsmState.SURPLUS_ACTIVE, state.status
    return FsmState.HEDGE_ACTIVE, state.status
