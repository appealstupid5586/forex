from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

BASE = Path(__file__).resolve().parent


class MemoryIndex:
    """Builds a simple inverted index over memory JSON files to enable search."""

    def __init__(self, root: Path | None = None):
        self.root = (root or BASE / "memory").resolve()
        self.index: Dict[str, List[str]] = {}

    def build(self) -> None:
        # index by symbol, strategy, setup, regime, session, result
        self.index = {}
        for path in self.root.rglob("*.json"):
            try:
                data = json.loads(path.read_text())
            except Exception:
                continue
            for key in ("symbol", "strategy_id", "setup", "regime", "session", "result"):
                if key in data:
                    val = str(data[key])
                    self.index.setdefault((key, val), []).append(str(path))

    def search(self, key: str, value: str) -> List[str]:
        return self.index.get((key, value), [])
