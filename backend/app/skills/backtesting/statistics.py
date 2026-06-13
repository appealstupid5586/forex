from __future__ import annotations

from math import sqrt
from typing import Any


def _profit(trade: dict[str, Any]) -> float:
    if "profit" in trade:
        return float(trade.get("profit") or 0.0)

    entry = float(trade.get("entry", trade.get("entry_price", 0.0)) or 0.0)
    exit_price = float(trade.get("exit", trade.get("exit_price", entry)) or entry)
    size = float(trade.get("size", trade.get("lot", 1.0)) or 1.0)
    direction = str(trade.get("direction", "buy")).lower()
    multiplier = -1.0 if direction in {"sell", "short"} else 1.0
    return (exit_price - entry) * size * multiplier


def _returns(profits: list[float], starting_balance: float) -> list[float]:
    balance = starting_balance
    values: list[float] = []
    for profit in profits:
        base = max(abs(balance), 1.0)
        values.append(profit / base)
        balance += profit
    return values


def calculate_drawdowns(profits: list[float], starting_balance: float = 10000.0) -> dict[str, float | int]:
    balance = starting_balance
    peak = starting_balance
    current_loss_streak = 0
    max_consecutive_losses = 0
    drawdowns: list[float] = []
    recovery_bars: list[int] = []
    bars_since_peak = 0

    for profit in profits:
        balance += profit
        if profit < 0:
            current_loss_streak += 1
            max_consecutive_losses = max(max_consecutive_losses, current_loss_streak)
        else:
            current_loss_streak = 0

        if balance >= peak:
            if bars_since_peak:
                recovery_bars.append(bars_since_peak)
            peak = balance
            bars_since_peak = 0
            drawdowns.append(0.0)
            continue

        bars_since_peak += 1
        drawdown = ((peak - balance) / max(peak, 1.0)) * 100.0
        drawdowns.append(drawdown)

    non_zero = [value for value in drawdowns if value > 0]
    return {
        "max_drawdown": round(max(drawdowns, default=0.0), 4),
        "average_drawdown": round(sum(non_zero) / len(non_zero), 4) if non_zero else 0.0,
        "consecutive_losses": max_consecutive_losses,
        "recovery_time": max(recovery_bars, default=bars_since_peak),
    }


def calculate_statistics(trades: list[dict[str, Any]], starting_balance: float = 10000.0) -> dict[str, float | int]:
    profits = [_profit(trade) for trade in trades]
    wins = [profit for profit in profits if profit > 0]
    losses = [profit for profit in profits if profit < 0]
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    trade_count = len(profits)
    win_rate = len(wins) / trade_count if trade_count else 0.0
    expectancy = sum(profits) / trade_count if trade_count else 0.0
    average_win = gross_profit / len(wins) if wins else 0.0
    average_loss = gross_loss / len(losses) if losses else 0.0
    average_rr = average_win / average_loss if average_loss else 0.0
    period_returns = _returns(profits, starting_balance)
    mean_return = sum(period_returns) / len(period_returns) if period_returns else 0.0
    variance = sum((value - mean_return) ** 2 for value in period_returns) / len(period_returns) if period_returns else 0.0
    sharpe_ratio = mean_return / sqrt(variance) if variance > 0 else 0.0
    drawdown = calculate_drawdowns(profits, starting_balance)
    net_profit = sum(profits)
    recovery_factor = net_profit / drawdown["max_drawdown"] if drawdown["max_drawdown"] else 0.0

    return {
        "trade_count": trade_count,
        "win_rate": round(win_rate, 4),
        "profit_factor": round(gross_profit / gross_loss, 4) if gross_loss else round(gross_profit, 4),
        "expectancy": round(expectancy, 4),
        "average_rr": round(average_rr, 4),
        "sharpe_ratio": round(sharpe_ratio, 4),
        "recovery_factor": round(recovery_factor, 4),
        "net_profit": round(net_profit, 4),
        **drawdown,
    }
