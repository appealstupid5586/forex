import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.main import app


def test_identity_api_info():
    client = TestClient(app)
    resp = client.get("/api/v1/identity/info")
    assert resp.status_code == 200
    data = resp.json()
    assert "identity" in data
    assert data["identity"].get("system_name") == "TUNGNS Copilot OS"
