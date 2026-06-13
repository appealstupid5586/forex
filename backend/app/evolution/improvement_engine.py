from __future__ import annotations

from typing import Any

from app.memory import MemoryManager


class ImprovementEngine:
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager

    def suggest(self, weaknesses: list[dict[str, Any]]) -> list[dict[str, Any]]:
        recommendations: list[dict[str, Any]] = []
        for weakness in weaknesses:
            if weakness["type"] == "regime_weakness":
                recommendations.append({
                    "recommendation": "Reduce exposure during adverse regimes",
                    "action": "reduce_risk",
                    "confidence": weakness.get("confidence", 0.7),
                    "tags": ["regime", "risk_management"],
                })
            elif weakness["type"] == "strategy_weakness":
                recommendations.append({
                    "recommendation": "Review strategy parameters and improve expectancy",
                    "action": "strategy_review",
                    "confidence": weakness.get("confidence", 0.7),
                    "tags": ["strategy", "review"],
                })
            elif weakness["type"] == "session_weakness":
                recommendations.append({
                    "recommendation": "Avoid or reduce trades during the identified weak session",
                    "action": "session_adjustment",
                    "confidence": weakness.get("confidence", 0.7),
                    "tags": ["session", "avoidance"],
                })
            elif weakness["type"] == "symbol_weakness":
                recommendations.append({
                    "recommendation": "Reduce symbol exposure and inspect correlation",
                    "action": "symbol_rebalance",
                    "confidence": weakness.get("confidence", 0.7),
                    "tags": ["symbol", "diversification"],
                })
        return recommendations
