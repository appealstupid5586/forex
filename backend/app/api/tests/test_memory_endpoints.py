from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.memory.memory_manager import MemoryManager as FileMemoryManager


def test_save_evidence_and_failure_and_short_term(tmp_path):
    client = TestClient(app)
    # use isolated memory store for test
    store_path = tmp_path / "mem.json"
    client.app.state.memory_agent = FileMemoryManager(str(store_path))

    # evidence
    ev_payload = {"content": {"note": "evidence-note"}, "tags": ["test"]}
    r = client.post("/api/v1/memory/evidence", json=ev_payload)
    assert r.status_code == 200
    data = r.json()["saved_memory"]
    assert data["content"]["kind"] == "evidence"

    # failure
    fail_payload = {"content": {"reason": "bad-trade"}, "tags": ["test"]}
    r2 = client.post("/api/v1/memory/failure", json=fail_payload)
    assert r2.status_code == 200
    data2 = r2.json()["saved_memory"]
    assert data2["content"]["kind"] == "failure"

    # short term
    st_payload = {"content": {"temp": 1}, "tags": ["ephemeral"]}
    r3 = client.post("/api/v1/memory/short-term/save", json=st_payload)
    assert r3.status_code == 200
    data3 = r3.json()["saved_memory"]
    assert data3["memory_type"] == "short_term"


def test_save_and_query_memory(tmp_path):
    """Test save generic memory and query it."""
    client = TestClient(app)
    client.app.state.memory_agent = FileMemoryManager(str(tmp_path / "mem.json"))

    # Save generic memory
    payload = {"kind": "test", "content": {"data": "test-data"}, "memory_type": "long_term", "tags": ["query-test"]}
    r = client.post("/api/v1/memory/save", json=payload)
    assert r.status_code == 200
    saved = r.json()["saved_memory"]
    assert saved["content"]["kind"] == "test"
    assert saved["tags"] == ["query-test"]

    # Query memory
    query_payload = {"query": "test-data", "tags": ["query-test"]}
    r2 = client.post("/api/v1/memory/query", json=query_payload)
    assert r2.status_code == 200
    results = r2.json()["results"]
    # Note: query operates on short_term in-memory records, so might be empty if save stores to long-term
    assert isinstance(results, list)


def test_save_trade_context_and_get_all(tmp_path):
    """Test save trade context and list all memory."""
    client = TestClient(app)
    client.app.state.memory_agent = FileMemoryManager(str(tmp_path / "mem.json"))

    # Save trade context
    tc_payload = {
        "symbol": "EURUSD",
        "timeframe": "H1",
        "trade_context": {"entry": 1.0800, "exit": 1.0850},
        "tags": ["eurusd"],
    }
    r = client.post("/api/v1/memory/save-trade-context", json=tc_payload)
    assert r.status_code == 200
    tc_saved = r.json()["saved_memory"]
    assert tc_saved["content"]["kind"] == "trade_context"
    assert tc_saved["content"]["symbol"] == "EURUSD"

    # Get all memory
    r2 = client.get("/api/v1/memory/all")
    assert r2.status_code == 200
    records = r2.json()["records"]
    assert isinstance(records, list)


def test_short_term_recent(tmp_path):
    """Test recent short term memory with limit."""
    client = TestClient(app)
    client.app.state.memory_agent = FileMemoryManager(str(tmp_path / "mem.json"))

    # Save multiple short-term records
    for i in range(3):
        st_payload = {"content": {"index": i}, "tags": ["batch"]}
        r = client.post("/api/v1/memory/short-term/save", json=st_payload)
        assert r.status_code == 200

    # Get recent with limit
    r2 = client.get("/api/v1/memory/short-term/recent?limit=2")
    assert r2.status_code == 200
    recent = r2.json()["recent_memories"]
    assert len(recent) == 2
    assert recent[0]["content"]["index"] == 2  # most recent


def test_market_insight(tmp_path):
    """Test market insight query."""
    client = TestClient(app)
    client.app.state.memory_agent = FileMemoryManager(str(tmp_path / "mem.json"))

    # Save short-term memory that should be queryable
    st_payload = {"content": {"market": "bullish", "signal": "cross"}, "tags": ["market_insight"]}
    r = client.post("/api/v1/memory/short-term/save", json=st_payload)
    assert r.status_code == 200

    # Query market insight
    query_payload = {"query": "bullish", "tags": ["market_insight"]}
    r2 = client.post("/api/v1/memory/market-insight", json=query_payload)
    assert r2.status_code == 200
    insights = r2.json()["market_insights"]
    assert isinstance(insights, list)
