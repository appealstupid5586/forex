"""Sweep engine for detecting and cleaning orphaned orders.

This module provides order sweep logic: detecting orphaned orders and 
issuing close orders.
"""
from __future__ import annotations

from app.core.models import Order, RobotState
from backend.app.skills.shared.sweep import detect_orphans, sweep_orders


class SweepEngine:
    """Engine for sweeping and managing orphaned orders."""

    def detect_orphans(self, state: RobotState, broker_orders: list[Order]) -> list[Order]:
        """Detect orders that exist in broker but not in local state."""
        return detect_orphans(state=state, broker_orders=broker_orders)

    def sweep(self, orphans: list[Order]) -> list[Order]:
        """Generate sweep (close) orders for orphaned orders."""
        return sweep_orders(orphans)
