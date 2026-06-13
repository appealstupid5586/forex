import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import get_settings
from app.main import app
from app.api import routes_memory
from app.core.runtime import memory_agent
from backend.app.memory.memory_manager import MemoryManager
from backend.app.memory.schemas import MemoryQuery, MemoryType


def test_default_memory_path_points_to_backend_memory_root():
    settings = get_settings()
    assert settings.memory_path == "./backend/app/memory"


def test_query_memory_matches_content_and_tags(tmp_path):
    store_path = tmp_path / "memory_store.json"
    agent = MemoryManager(str(store_path))

    agent.remember({"message": "Market looks bullish"}, memory_type=MemoryType.LONG_TERM, tags=["insight"])
    agent.remember({"message": "Market looks bearish"}, memory_type=MemoryType.LONG_TERM, tags=["alert"])

    query = MemoryQuery(query="bullish", tags=["insight"], memory_type=MemoryType.LONG_TERM)
    results = agent.query(query.query, tags=query.tags, memory_type=query.memory_type)

    assert len(results) == 1
    assert results[0].content["message"] == "Market looks bullish"
    assert "insight" in results[0].tags


def test_memory_api_short_term_endpoints_and_long_term_query(tmp_path):
    routes_memory.memory_agent = MemoryManager(str(tmp_path / "memory_store.json"))
    client = TestClient(app)

    save_resp = client.post(
        "/api/v1/memory/short-term/save",
        json={"content": {"note": "trade idea"}, "tags": ["idea"]},
    )
    assert save_resp.status_code == 200
    saved = save_resp.json()["saved_memory"]
    assert saved["content"]["note"] == "trade idea"
    assert "idea" in saved["tags"]

    recent_resp = client.get("/api/v1/memory/short-term/recent")
    assert recent_resp.status_code == 200
    recent = recent_resp.json()["recent_memories"]
    assert len(recent) == 1
    assert recent[0]["content"]["note"] == "trade idea"

    save_long_resp = client.post(
        "/api/v1/memory/save",
        json={"kind": "generic", "content": {"note": "persisted"}, "memory_type": "long_term", "tags": ["persist"]},
    )
    assert save_long_resp.status_code == 200

    query_resp = client.post(
        "/api/v1/memory/query",
        json={"query": "persisted", "tags": ["persist"], "memory_type": "long_term"},
    )
    assert query_resp.status_code == 200
    query_results = query_resp.json()["results"]
    assert len(query_results) == 1
    assert query_results[0]["content"]["content"]["note"] == "persisted"
    assert query_results[0]["content"]["kind"] == "generic"
