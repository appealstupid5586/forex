"""Shared utility helpers for skills."""

from typing import Sequence, Optional


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    return numerator / denominator if denominator != 0 else default


def first_or_none(items: Sequence) -> Optional[object]:
    return items[0] if items else None
