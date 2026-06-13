from __future__ import annotations

from fastapi import APIRouter

from app.core.runtime import identity_agent

router = APIRouter(prefix="/api/v1/identity", tags=["identity"])


@router.get("/info")
def identity_info():
    cfg = identity_agent.load_config()
    return {"identity": cfg}
