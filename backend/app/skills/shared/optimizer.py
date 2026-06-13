"""Optimization logic moved out of the backend agent."""

from __future__ import annotations

import random

from app.core.models import WinnerGene


def run_optimization(symbol: str, timeframe: str, step_range: list[float], x_range: list[int], risk_range: list[float]) -> WinnerGene:
    best: WinnerGene | None = None
    for step in step_range:
        for x in x_range:
            for risk in risk_range:
                profit_factor = round(random.uniform(0.8, 2.4) - risk * 0.05 + x * 0.02, 3)
                max_dd = round(random.uniform(2.0, 18.0) + risk * 0.3, 3)
                recovery = round(profit_factor / max(max_dd / 10, 0.1), 3)
                gene = WinnerGene(
                    symbol=symbol,
                    timeframe=timeframe,
                    step_size=step,
                    x_level=x,
                    risk_pct=risk,
                    atr_period=14,
                    profit_factor=profit_factor,
                    max_drawdown=max_dd,
                    recovery_factor=recovery,
                    win_rate=round(random.uniform(0.42, 0.68), 3),
                    expectancy=round(random.uniform(-0.2, 0.8), 3),
                )
                if best is None or (gene.profit_factor, gene.recovery_factor, -gene.max_drawdown) > (best.profit_factor, best.recovery_factor, -best.max_drawdown):
                    best = gene
    assert best is not None
    return best
