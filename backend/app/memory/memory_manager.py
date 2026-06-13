from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from backend.app.memory.schemas import MemoryType


BASE = Path(__file__).resolve().parent


@dataclass
class MemoryRecord:
    """Lightweight memory record for Phase C."""
    memory_id: str
    created_at: str
    memory_type: str  # "short_term" | "long_term" | "ephemeral"
    content: Dict[str, Any]
    tags: list[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "created_at": self.created_at,
            "memory_type": self.memory_type,
            "content": self.content,
            "tags": self.tags,
        }


class MemoryManager:
    """Simple filesystem-backed memory manager for Phase C."""

    def __init__(self, root: Path | str | None = None):
        root_path = Path(root) if root is not None else BASE
        self.root = root_path.resolve()
        self.short_term: list[MemoryRecord] = []
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        if self.root.exists() and not self.root.is_dir():
            self.root = self.root.parent / self.root.name.replace('.json', '')
        self.root.mkdir(parents=True, exist_ok=True)
        for sub in (
            "winners",
            "failures",
            "patterns",
            "strategies",
            "regimes",
            "sessions",
            "statistics",
            "evidence",
        ):
            p = self.root / sub
            p.mkdir(parents=True, exist_ok=True)

    def _write(self, subdir: str, data: Dict[str, Any]) -> str:
        fname = f"{uuid.uuid4().hex}.json"
        path = self.root / subdir / fname
        path.write_text(json.dumps(data, default=str, ensure_ascii=False))
        return str(path)

    def _load_persisted_records(self) -> list[MemoryRecord]:
        records: list[MemoryRecord] = []
        for subdir in (
            "winners",
            "failures",
            "patterns",
            "strategies",
            "regimes",
            "sessions",
            "statistics",
            "evidence",
        ):
            path = self.root / subdir
            if not path.exists():
                continue
            for file_path in sorted(path.glob("*.json")):
                try:
                    payload = json.loads(file_path.read_text())
                except json.JSONDecodeError:
                    continue
                records.append(
                    MemoryRecord(
                        memory_id=str(payload.get("memory_id", file_path.stem)),
                        created_at=str(payload.get("created_at", "")),
                        memory_type=str(payload.get("memory_type", "long_term")),
                        content=dict(payload.get("content", {})),
                        tags=list(payload.get("tags", [])),
                    )
                )
        return records

    def _record(self, content: Dict[str, Any], memory_type: str = "long_term", tags: list[str] | None = None) -> MemoryRecord:
        return MemoryRecord(
            memory_id=str(uuid.uuid4()),
            created_at=datetime.now(timezone.utc).isoformat(),
            memory_type=memory_type,
            content=content,
            tags=tags or [],
        )

    def save_winner(self, data: Dict[str, Any]) -> str:
        return self._write("winners", data)

    def save_failure(self, data: Dict[str, Any], tags: list[str] | None = None) -> MemoryRecord:
        record = self._record({"kind": "failure", "content": data}, "long_term", tags or ["failure"])
        self._write("failures", record.to_dict())
        return record

    def save_pattern(self, data: Dict[str, Any]) -> MemoryRecord:
        record = self._record({"kind": "pattern", "content": data}, "long_term", ["pattern"])
        self._write("patterns", record.to_dict())
        return record

    def save_strategy(self, data: Dict[str, Any]) -> MemoryRecord:
        record = self._record({"kind": "strategy", "content": data}, "long_term", ["strategy"])
        self._write("strategies", record.to_dict())
        return record

    def save_regime(self, data: Dict[str, Any]) -> MemoryRecord:
        record = self._record({"kind": "regime", "content": data}, "long_term", ["regime"])
        self._write("regimes", record.to_dict())
        return record

    def save_session(self, data: Dict[str, Any]) -> MemoryRecord:
        record = self._record({"kind": "session", "content": data}, "long_term", ["session"])
        self._write("sessions", record.to_dict())
        return record

    def save_statistics(self, data: Dict[str, Any]) -> MemoryRecord:
        record = self._record({"kind": "statistics", "content": data}, "long_term", ["statistics"])
        self._write("statistics", record.to_dict())
        return record

    def save_evidence(self, data: Dict[str, Any], tags: list[str] | None = None) -> MemoryRecord:
        record = self._record({"kind": "evidence", "content": data}, "long_term", tags or ["evidence"])
        self._write("evidence", record.to_dict())
        return record

    def remember(self, content: Dict[str, Any], memory_type: str = "long_term", tags: list[str] | None = None) -> MemoryRecord:
        """Generic remember method (compatible with routes)."""
        record = self._record(content, memory_type, tags)
        subdir = "sessions" if memory_type == "short_term" else "evidence"
        self._write(subdir, record.to_dict())
        return record

    def save_short_term(self, content: Dict[str, Any], tags: list[str] | None = None) -> MemoryRecord:
        record = self._record(content, "short_term", tags)
        self.short_term.append(record)
        return record

    def recent_short_term(self, limit: int = 10) -> list[MemoryRecord]:
        return list(reversed(self.short_term[-limit:]))

    def save_trade_context(self, symbol: str, timeframe: str, trade_context: Dict[str, Any], tags: list[str] | None = None) -> MemoryRecord:
        payload = {
            "kind": "trade_context",
            "symbol": symbol,
            "timeframe": timeframe,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "trade_context": trade_context,
        }
        record = self._record(payload, "long_term", (tags or ["trade_context", symbol, timeframe]))
        self._write("sessions", record.to_dict())
        return record

    def query(self, query_value: str, tags: list[str] | None = None, memory_type: str | MemoryType | None = None) -> list[MemoryRecord]:
        """Query persisted and short-term memory records."""
        records = list(self.short_term) + self._load_persisted_records()
        if memory_type is not None:
            expected_type = memory_type.value if isinstance(memory_type, MemoryType) else str(memory_type)
            records = [record for record in records if record.memory_type == expected_type]

        query_terms = [term.lower() for term in query_value.split() if term]
        search_tags = [tag.lower() for tag in (tags or [])]

        def matches(record: MemoryRecord) -> bool:
            searchable = f"{json.dumps(record.content, ensure_ascii=False).lower()} {' '.join(record.tags).lower()}"
            return all(term in searchable for term in query_terms) and all(tag in searchable for tag in search_tags)

        matched = [record for record in records if matches(record)]
        if matched:
            return [matched[-1]]
        return []

    def query_market_insight(self, query_value: str, tags: list[str] | None = None) -> list[MemoryRecord]:
        """Query market insights (alias for query with market_insight tag)."""
        return self.query(query_value, (tags or ["market_insight"]))

    def load_memory(self, memory_type: str | None = None) -> list[MemoryRecord]:
        """Load short-term and persisted records."""
        records = list(self.short_term) + self._load_persisted_records()
        if memory_type == "short_term":
            return list(self.short_term)
        return records

    def list_entries(self, subdir: str) -> list[str]:
        p = self.root / subdir
        if not p.exists():
            return []
        return [str(x) for x in p.glob("*.json")]

    def load(self, path: str) -> Dict[str, Any]:
        return json.loads(Path(path).read_text())
