from __future__ import annotations

from typing import Any

from app.memory import MemoryManager


class RegimeSimulator:
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager

    def simulate(self, strategy_data: dict[str, Any]) -> list[dict[str, Any]]:
        regimes = [
            {"regime": "trending", "expected_behavior": "trend continuation"},
            {"regime": "ranging", "expected_behavior": "range oscillation"},
            {"regime": "volatile", "expected_behavior": "sudden swings"},
            {"regime": "news", "expected_behavior": "spike and mean reversion"},
            {"regime": "low_liquidity", "expected_behavior": "wide spreads and fade"},
        ]
        return [{"strategy_data": strategy_data, **regime} for regime in regimes]
