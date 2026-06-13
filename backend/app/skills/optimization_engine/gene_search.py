"""Gene search and optimization logic for the optimization_engine skill."""
from __future__ import annotations

from backend.app.skills.shared.optimizer import run_optimization


class BacktestOptimizer:
    """Deterministic optimization engine for parameter search.

    Replace with vectorbt/backtrader engine before using real capital.
    """

    def run(self, symbol: str, timeframe: str, step_range: list[float], x_range: list[int], risk_range: list[float]):
        """Run parameter optimization across ranges."""
        return run_optimization(symbol=symbol, timeframe=timeframe, step_range=step_range, x_range=x_range, risk_range=risk_range)
