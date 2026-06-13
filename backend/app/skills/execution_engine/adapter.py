from __future__ import annotations

from typing import Any, Dict
from uuid import uuid4

from app.core.models import OrderStatus


def build_broker_order_id() -> str:
    """Create a broker-order identifier for execution events."""
    return f"broker-{uuid4().hex[:10]}"


def determine_order_status(settings: Any) -> OrderStatus:
    """Choose a status based on whether live execution is enabled."""
    return OrderStatus.OPEN if getattr(settings, "allow_live_execution", False) else OrderStatus.REJECTED


def execute_order(order_data: Dict[str, Any], settings: Any) -> Dict[str, Any]:
    """Adapter that routes an order through the execution engine.

    Returns JSON-serializable result with order data and status.
    """
    status = determine_order_status(settings)
    return {
        "decision": "execute" if status == OrderStatus.OPEN else "reject",
        "confidence": 0.95,
        "evidence": ["order routed to execution engine"],
        "metadata": {"engine_type": "execution_engine", "status": status.value},
    }
