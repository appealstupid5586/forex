from __future__ import annotations

from fastapi import APIRouter

from app.core.models import FsmState, RobotStatus
from app.core.runtime import get_or_create_robot_state, save_robot_state

router = APIRouter(prefix="/api/v1/robot", tags=["robot"])


@router.post("/start")
def start_robot():
    state = get_or_create_robot_state()
    state.status = RobotStatus.RUNNING
    state.fsm_state = FsmState.RESTORE_STATE
    return save_robot_state(state)


@router.post("/stop")
def stop_robot():
    state = get_or_create_robot_state()
    state.status = RobotStatus.STOPPED
    state.fsm_state = FsmState.IDLE
    return save_robot_state(state)


@router.post("/freeze")
def freeze_robot():
    state = get_or_create_robot_state()
    state.status = RobotStatus.FROZEN
    state.fsm_state = FsmState.FREEZE
    return save_robot_state(state)


@router.get("/state")
def robot_state():
    return get_or_create_robot_state()
