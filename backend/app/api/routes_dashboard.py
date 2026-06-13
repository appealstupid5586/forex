from __future__ import annotations

from pathlib import Path
from fastapi import APIRouter

from app.core.config import get_settings
from app.core.runtime import genes_memory, get_or_create_robot_state, state_store

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])
settings = get_settings()


@router.get("/hedge-os")
def dashboard():
    state = get_or_create_robot_state()
    orders = state_store.all_orders()
    logs = []
    log_path = Path(settings.logs_path)
    if log_path.exists():
        logs = log_path.read_text(encoding="utf-8").splitlines()[-20:]
    return {
        "robot": state,
        "orders_count": len(orders),
        "open_orders": [o for o in orders if o.status == "OPEN"],
        "winner_genes": genes_memory.winners(),
        "latest_logs": logs,
    }
