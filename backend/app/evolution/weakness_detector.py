from __future__ import annotations

from typing import Any

from app.memory import MemoryManager


class WeaknessDetector:
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager

    def detect(self, evidence: dict[str, Any]) -> list[dict[str, Any]]:
        weaknesses: list[dict[str, Any]] = []
        if not evidence:
            return weaknesses

        performance = evidence.get("performance", {})
        if performance.get("drawdown", 0) > 10:
            weaknesses.append({
                "type": "regime_weakness",
                "cause": "drawdown_exceeds_threshold",
                "details": performance,
                "confidence": 0.85,
            })

        if performance.get("win_rate", 1.0) < 0.5:
            weaknesses.append({
                "type": "strategy_weakness",
                "cause": "low_win_rate",
                "details": performance,
                "confidence": 0.8,
            })

        if evidence.get("session") and evidence["session"].get("name") == "asian_session" and performance.get("win_rate", 1.0) < 0.5:
            weaknesses.append({
                "type": "session_weakness",
                "cause": "asian_session_underperformance",
                "details": evidence,
                "confidence": 0.75,
            })

        if evidence.get("symbol") and performance.get("win_rate", 1.0) < 0.5:
            weaknesses.append({
                "type": "symbol_weakness",
                "cause": "symbol_underperformance",
                "details": evidence,
                "confidence": 0.7,
            })

        return weaknesses
