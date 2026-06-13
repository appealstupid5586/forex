from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class HookContext:
    event: str
    payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SignalHookResult:
    proceed: bool = True
    reasons: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TradeHookResult:
    proceed: bool = True
    reasons: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CloseHookResult:
    proceed: bool = True
    reasons: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
