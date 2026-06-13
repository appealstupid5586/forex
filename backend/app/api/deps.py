from __future__ import annotations

from fastapi import Request

from app.memory import MemoryManager


def get_memory_agent(request: Request) -> MemoryManager:
    """FastAPI dependency to retrieve the MemoryManager from app.state or the route module."""
    agent = getattr(request.app.state, "memory_agent", None)
    if agent is not None:
        return agent

    from backend.app.api import routes_memory

    return routes_memory.memory_agent
