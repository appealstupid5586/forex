from __future__ import annotations

from statistics import mean
from typing import Any

from app.memory import MemoryManager


class StrategyEvaluator:
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager

    def evaluate(self, portfolio_data: dict[str, Any]) -> dict[str, Any]:
        if not portfolio_data:
            return {
                "expectancy": 0.0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "max_drawdown": 0.0,
                "recovery_factor": 0.0,
            }

        returns = portfolio_data.get("returns", [])
        wins = [r for r in returns if r > 0]
        losses = [abs(r) for r in returns if r < 0]
        gross_profit = sum(wins)
        gross_loss = sum(losses)
        total_trades = len(returns)
        winners = len(wins)
        losers = len(losses)

        expectancy = ((gross_profit / winners) if winners else 0.0) * (winners / total_trades) - ((gross_loss / losers) if losers else 0.0) * (losers / total_trades) if total_trades else 0.0
        win_rate = winners / total_trades if total_trades else 0.0
        profit_factor = (gross_profit / gross_loss) if gross_loss else 0.0
        max_drawdown = portfolio_data.get("max_drawdown", 0.0)
        recovery_factor = (portfolio_data.get("total_return", 0.0) / max_drawdown) if max_drawdown else 0.0

        return {
            "expectancy": expectancy,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "max_drawdown": max_drawdown,
            "recovery_factor": recovery_factor,
            "total_trades": total_trades,
            "timeframe": portfolio_data.get("timeframe"),
        }
