from __future__ import annotations

from typing import Any

from app.memory import MemoryManager


class WinnerDna:
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager

    def extract(self) -> dict[str, Any]:
        winners = self._load_winners()
        symbol_counts = {}
        session_counts = {}
        regime_counts = {}

        for record in winners:
            content = record.get("content", {})
            symbol = content.get("symbol")
            session = content.get("session")
            regime = content.get("regime")
            if symbol:
                symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
            if session:
                session_counts[session] = session_counts.get(session, 0) + 1
            if regime:
                regime_counts[regime] = regime_counts.get(regime, 0) + 1

        return {
            "winning_symbols": sorted(symbol_counts, key=symbol_counts.get, reverse=True),
            "winning_sessions": sorted(session_counts, key=session_counts.get, reverse=True),
            "winning_regimes": sorted(regime_counts, key=regime_counts.get, reverse=True),
            "source_count": len(winners),
        }

    def _load_winners(self) -> list[dict[str, Any]]:
        winners = []
        for path in self.memory_manager.list_entries("winners"):
            winners.append(self.memory_manager.load(path))
        return winners
