from __future__ import annotations

from typing import Any

from app.memory import MemoryManager


class SelfCorrectionEngine:
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager

    def refine(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for candidate in candidates:
            if candidate.get("confidence", 0) >= 0.55:
                filtered.append({
                    **candidate,
                    "status": "kept",
                })
            else:
                filtered.append({
                    **candidate,
                    "status": "rejected",
                })
        return filtered
