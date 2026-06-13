from __future__ import annotations

from typing import Any, Dict

from backend.app.skills.sweep_engine.sweep_engine_module import SweepEngine


def sweep_orders_adapter(state: Any, broker_orders: list[Any]) -> Dict[str, Any]:
    """Adapter for sweep engine: detect orphans and generate sweep orders.
    
    Returns JSON-serializable sweep decision.
    """
    engine = SweepEngine()
    orphans = engine.detect_orphans(state=state, broker_orders=broker_orders)
    sweep_result = engine.sweep(orphans)
    
    return {
        "decision": "sweep" if sweep_result else "no_sweep",
        "confidence": 0.9,
        "evidence": [f"detected {len(orphans)} orphans, generated {len(sweep_result)} sweep orders"],
        "metadata": {"orphan_count": len(orphans), "sweep_count": len(sweep_result)},
    }
