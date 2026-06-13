from __future__ import annotations

from enum import Enum


class MemoryType(str, Enum):
    LONG_TERM = "long_term"
    SHORT_TERM = "short_term"


class MemoryQuery:
    def __init__(self, query: str = "", tags: list[str] | None = None, memory_type: MemoryType | None = None):
        self.query = query
        self.tags = tags or []
        self.memory_type = memory_type
