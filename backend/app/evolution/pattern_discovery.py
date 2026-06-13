from __future__ import annotations

from collections import Counter
from typing import Any

from app.memory import MemoryManager


class PatternDiscoveryEngine:
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager

    def discover(self) -> list[dict[str, Any]]:
        evidence_records = self._load_evidence()
        return self._find_patterns(evidence_records)

    def _load_evidence(self) -> list[dict[str, Any]]:
        records = []
        for path in self.memory_manager.list_entries("evidence"):
            records.append(self.memory_manager.load(path))
        return records

    def _find_patterns(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not records:
            return []

        symbol_counter = Counter()
        event_counter = Counter()
        stage_counter = Counter()
        category_counter = Counter()

        for record in records:
            content = record.get("content", {})
            symbol = content.get("symbol")
            event = content.get("event")
            stage = content.get("stage")
            category = content.get("category")
            if symbol:
                symbol_counter[symbol] += 1
            if event:
                event_counter[event] += 1
            if stage:
                stage_counter[stage] += 1
            if category:
                category_counter[category] += 1

        patterns = []
        for key, counter in (
            ("symbols", symbol_counter),
            ("events", event_counter),
            ("stages", stage_counter),
            ("categories", category_counter),
        ):
            most_common = counter.most_common(5)
            for value, count in most_common:
                patterns.append({"pattern_type": key, "pattern": value, "count": count})

        return patterns
