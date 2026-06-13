from __future__ import annotations

from typing import Any


def discover_weaknesses(statistics: dict[str, Any], regime_analysis: dict[str, Any]) -> list[str]:
    weaknesses: list[str] = []

    if statistics.get("trade_count", 0) < 20:
        weaknesses.append("low_sample_size")
    if statistics.get("max_drawdown", 0) > 10:
        weaknesses.append("high_drawdown")
    if statistics.get("expectancy", 0) <= 0:
        weaknesses.append("low_expectancy")
    if statistics.get("profit_factor", 0) < 1.2:
        weaknesses.append("poor_profit_factor")
    if statistics.get("average_rr", 0) < 1:
        weaknesses.append("poor_risk_reward")
    if statistics.get("consecutive_losses", 0) >= 4:
        weaknesses.append("loss_streak_risk")

    for regime, summary in regime_analysis.get("by_regime", {}).items():
        if summary.get("profit", 0) < 0:
            weaknesses.append(f"weak_regime:{regime}")

    return weaknesses


def generate_recommendations(weaknesses: list[str]) -> list[str]:
    recommendations = []
    for weakness in weaknesses:
        if weakness == "low_sample_size":
            recommendations.append("Increase sample size before publishing results.")
        elif weakness == "high_drawdown":
            recommendations.append("Reduce risk or add drawdown protection before live use.")
        elif weakness == "low_expectancy":
            recommendations.append("Review entry and exit rules because expected value is not positive.")
        elif weakness == "poor_profit_factor":
            recommendations.append("Filter low-quality setups and review transaction costs.")
        elif weakness == "poor_risk_reward":
            recommendations.append("Improve stop-loss and take-profit balance.")
        elif weakness == "loss_streak_risk":
            recommendations.append("Add cooling-off rules after consecutive losses.")
        elif weakness.startswith("weak_regime:"):
            regime = weakness.split(":", 1)[1]
            recommendations.append(f"Avoid or reduce risk during {regime} regime.")
    return recommendations


def generate_report(result: dict[str, Any]) -> dict[str, Any]:
    weaknesses = result.get("weaknesses") or discover_weaknesses(result.get("statistics", {}), result.get("regime_analysis", {}))
    return {
        "summary": {
            "win_rate": result.get("win_rate", 0.0),
            "profit_factor": result.get("profit_factor", 0.0),
            "max_drawdown": result.get("max_drawdown", 0.0),
            "best_regime": result.get("best_regime"),
            "worst_regime": result.get("worst_regime"),
        },
        "charts": {
            "equity_curve": result.get("equity_curve", []),
            "drawdown_curve": result.get("drawdown_curve", []),
        },
        "regime_analysis": result.get("regime_analysis", {}),
        "weaknesses": weaknesses,
        "recommendations": generate_recommendations(weaknesses),
        "evidence": result.get("evidence", []),
    }
