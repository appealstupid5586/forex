from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .report_generator import discover_weaknesses, generate_report
from .statistics import calculate_statistics


REGIMES = {"Trending", "Ranging", "Volatile", "News", "Low Liquidity"}


class BacktestEngine:
    def __init__(self, memory_root: str | Path | None = None):
        self.memory_root = Path(memory_root) if memory_root else Path(__file__).resolve().parents[2] / "memory"

    def run(self, strategy: dict[str, Any], market_data: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
        config = config or {}
        starting_balance = float(config.get("starting_balance", 10000.0))
        trades = self._trades(strategy, market_data)
        statistics = calculate_statistics(trades, starting_balance=starting_balance)
        regime_analysis = self._analyze_regimes(trades)
        curves = self._build_curves(trades, starting_balance)

        result = {
            "win_rate": statistics["win_rate"],
            "profit_factor": statistics["profit_factor"],
            "max_drawdown": statistics["max_drawdown"],
            "best_regime": regime_analysis.get("best_regime"),
            "worst_regime": regime_analysis.get("worst_regime"),
            "statistics": statistics,
            "regime_analysis": regime_analysis,
            **curves,
        }
        result["weaknesses"] = discover_weaknesses(statistics, regime_analysis)
        result["evidence"] = self._build_evidence(strategy, result)
        result["report"] = generate_report(result)

        if config.get("save_memory", False):
            self.save_evidence(result)

        return result

    def save_evidence(self, result: dict[str, Any]) -> Path:
        destination = self.memory_root / "strategies"
        destination.mkdir(parents=True, exist_ok=True)
        strategy_name = result.get("evidence", [{}])[0].get("strategy", "strategy")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = destination / f"backtest_{strategy_name}_{timestamp}.json"
        payload = {
            "kind": "backtest_evidence",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "summary": result.get("report", {}).get("summary", {}),
            "weaknesses": result.get("weaknesses", []),
            "evidence": result.get("evidence", []),
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def _trades(self, strategy: dict[str, Any], market_data: dict[str, Any]) -> list[dict[str, Any]]:
        if "trades" in market_data:
            return list(market_data.get("trades") or [])

        prices = list(market_data.get("prices") or [])
        signals = list(strategy.get("signals") or market_data.get("signals") or [])
        size = float(strategy.get("position_size", 1.0))
        trades: list[dict[str, Any]] = []
        open_trade: dict[str, Any] | None = None

        for index, price in enumerate(prices):
            signal = signals[index] if index < len(signals) else "hold"
            if signal == "buy" and open_trade is None:
                open_trade = {"direction": "buy", "entry": price, "size": size, "entry_index": index}
            elif signal == "sell" and open_trade is not None:
                open_trade.update({"exit": price, "exit_index": index, "regime": self._regime_at(market_data, index)})
                trades.append(open_trade)
                open_trade = None

        return trades

    def _analyze_regimes(self, trades: list[dict[str, Any]]) -> dict[str, Any]:
        by_regime: dict[str, dict[str, Any]] = {}
        for trade in trades:
            regime = str(trade.get("regime") or "Unknown")
            profit = float(trade.get("profit", 0.0)) if "profit" in trade else self._trade_profit(trade)
            summary = by_regime.setdefault(regime, {"trades": 0, "wins": 0, "profit": 0.0})
            summary["trades"] += 1
            summary["wins"] += 1 if profit > 0 else 0
            summary["profit"] += profit

        for summary in by_regime.values():
            summary["win_rate"] = round(summary["wins"] / summary["trades"], 4) if summary["trades"] else 0.0
            summary["profit"] = round(summary["profit"], 4)

        ranked = sorted(by_regime.items(), key=lambda item: item[1]["profit"], reverse=True)
        return {
            "by_regime": by_regime,
            "best_regime": ranked[0][0] if ranked else None,
            "worst_regime": ranked[-1][0] if ranked else None,
            "known_regimes": sorted(REGIMES),
        }

    def _build_curves(self, trades: list[dict[str, Any]], starting_balance: float) -> dict[str, list[float]]:
        balance = starting_balance
        peak = starting_balance
        equity_curve = [round(balance, 4)]
        drawdown_curve = [0.0]

        for trade in trades:
            balance += self._trade_profit(trade)
            peak = max(peak, balance)
            equity_curve.append(round(balance, 4))
            drawdown_curve.append(round(((peak - balance) / max(peak, 1.0)) * 100.0, 4))

        return {"equity_curve": equity_curve, "drawdown_curve": drawdown_curve}

    def _build_evidence(self, strategy: dict[str, Any], result: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "strategy": strategy.get("name", "unknown"),
                "win_rate": result.get("win_rate"),
                "profit_factor": result.get("profit_factor"),
                "max_drawdown": result.get("max_drawdown"),
                "best_regime": result.get("best_regime"),
                "worst_regime": result.get("worst_regime"),
                "weaknesses": result.get("weaknesses", []),
            }
        ]

    def _regime_at(self, market_data: dict[str, Any], index: int) -> str:
        regimes = list(market_data.get("regimes") or [])
        if index < len(regimes):
            return str(regimes[index])
        return "Unknown"

    def _trade_profit(self, trade: dict[str, Any]) -> float:
        if "profit" in trade:
            return float(trade.get("profit") or 0.0)
        entry = float(trade.get("entry", trade.get("entry_price", 0.0)) or 0.0)
        exit_price = float(trade.get("exit", trade.get("exit_price", entry)) or entry)
        size = float(trade.get("size", trade.get("lot", 1.0)) or 1.0)
        direction = str(trade.get("direction", "buy")).lower()
        multiplier = -1.0 if direction in {"sell", "short"} else 1.0
        return (exit_price - entry) * size * multiplier


def run_backtest(strategy: dict[str, Any], market_data: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
    return BacktestEngine().run(strategy=strategy, market_data=market_data, config=config)
