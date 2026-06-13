from __future__ import annotations

import json
from pathlib import Path

from app.memory import MemoryManager


def test_save_and_load_tmp(tmp_path: Path):
    mgr = MemoryManager(root=tmp_path)
    data = {"trade_id": "t1", "symbol": "EURUSD", "result": 10}
    path = mgr.save_winner(data)
    assert Path(path).exists()
    loaded = mgr.load(path)
    assert loaded["trade_id"] == "t1"
    assert loaded["symbol"] == "EURUSD"


def test_list_entries(tmp_path: Path):
    mgr = MemoryManager(root=tmp_path)
    mgr.save_failure({"a": 1})
    entries = mgr.list_entries("failures")
    assert len(entries) >= 1
