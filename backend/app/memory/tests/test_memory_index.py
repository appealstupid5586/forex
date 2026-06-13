from __future__ import annotations

from pathlib import Path
import json

from app.memory import MemoryIndex


def test_build_and_search(tmp_path: Path):
    # create sample file
    mem_dir = tmp_path / "memory"
    (mem_dir / "winners").mkdir(parents=True)
    p = mem_dir / "winners" / "sample.json"
    p.write_text(json.dumps({"symbol": "EURUSD", "strategy_id": "s1", "result": "Winner"}))

    idx = MemoryIndex(root=tmp_path)
    idx.build()
    res = idx.search("symbol", "EURUSD")
    assert len(res) == 1
