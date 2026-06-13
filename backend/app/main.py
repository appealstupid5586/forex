from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_backtest import router as backtest_router
from app.api.routes_dashboard import router as dashboard_router
from app.api.routes_fsm import router as fsm_router
from app.api.routes_genes import router as genes_router
from app.api.routes_grid import router as grid_router
from app.api.routes_guard import router as guard_router
from app.api.routes_memory import router as memory_router
from app.api.routes_hooks import router as hooks_router
from app.api.routes_identity import router as identity_router
from app.api.routes_graph2 import router as graph_router
from app.api.routes_robot import router as robot_router
from app.api.routes_portfolio import router as portfolio_router
from app.api.routes_broker_ctrader import router as ctrader_router
from app.api.routes_market import router as market_router
from app.core.config import get_settings
from app.core.runtime import memory_agent

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(robot_router)
app.include_router(grid_router)
app.include_router(fsm_router)
app.include_router(guard_router)
app.include_router(backtest_router)
app.include_router(genes_router)
app.include_router(memory_router)
app.include_router(hooks_router)
app.include_router(identity_router)
app.include_router(portfolio_router)
app.include_router(dashboard_router)
app.include_router(graph_router)
app.include_router(market_router)
app.include_router(ctrader_router)

# expose memory agent on app state for DI and runtime access
app.state.memory_agent = memory_agent


@app.on_event("startup")
def _startup():
    # ensure memory directories exist
    try:
        memory_agent._ensure_dirs()
    except Exception:
        pass


@app.on_event("shutdown")
def _shutdown():
    # placeholder for future cleanup
    return None


@app.get("/health")
def health():
    return {"ok": True, "app": settings.app_name, "broker_mode": settings.broker_mode, "live_enabled": settings.allow_live_execution}
