from __future__ import annotations

from typing import Any

from app.memory import MemoryManager


class FutureGenerator:
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager

    def generate(self, evidence: dict[str, Any]) -> list[dict[str, Any]]:
        futures: list[dict[str, Any]] = []
        if not evidence:
            return futures

        futures.append({
            "name": "continue_trend",
            "description": "Market continues the current trend",
            "confidence": 0.6,
            "evidence": evidence,
        })
        futures.append({
            "name": "range_expansion",
            "description": "Market enters a widening range",
            "confidence": 0.55,
            "evidence": evidence,
        })
        futures.append({
            "name": "reversal",
            "description": "Market reverses the current move",
            "confidence": 0.5,
            "evidence": evidence,
        })

        return futures
