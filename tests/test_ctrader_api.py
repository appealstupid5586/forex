import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.main import app


def test_ctrader_status_endpoint():
    client = TestClient(app)
    resp = client.get("/api/ctrader/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["broker"] == "ctrader"
    assert data["connected"] is False


def test_ctrader_connect_and_account_flow():
    client = TestClient(app)
    resp = client.post(
        "/api/ctrader/connect",
        json={
            "access_token": "demo-token",
            "account_id": "demo-account",
            "environment": "demo"
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["connected"] is True

    account_resp = client.get("/api/ctrader/account")
    assert account_resp.status_code == 200
    account_data = account_resp.json()
    assert account_data["account_id"] == "demo-account"
    assert account_data["environment"] == "demo"
