from __future__ import annotations

from typing import Any, Dict

from backend.app.skills.optimization_engine.gene_search import BacktestOptimizer


def optimize_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """Adapter for parameter optimization.
    
    Returns JSON-serializable optimization decision.
    """
    optimizer = BacktestOptimizer()
    # Placeholder: actual optimization would use params to call optimizer.run()
    return {
        "decision": "optimize",
        "confidence": 0.8,
        "evidence": ["optimizer ready for parameter sweep"],
        "metadata": {"engine_type": "optimization_engine"},
    }
