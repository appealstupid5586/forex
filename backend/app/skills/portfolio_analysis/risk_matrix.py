from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Dict, Any


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


RiskMatrix = RiskLevel


def _load_config() -> Dict[str, Any]:
    config_path = Path(__file__).resolve().parent / "config.json"
    try:
        return json.loads(config_path.read_text())
    except Exception:
        return {}


def exposure_risk_level(exposure_score: float) -> str:
    if exposure_score < 0.01:
        return RiskLevel.LOW.value
    if exposure_score < 0.02:
        return RiskLevel.MEDIUM.value
    if exposure_score < 0.03:
        return RiskLevel.HIGH.value
    return RiskLevel.CRITICAL.value


def correlation_risk_level(correlation_score: float, duplicated_exposure: float = 0.0) -> str:
    base_score = correlation_score
    if base_score < 0.25:
        level = RiskLevel.LOW
    elif base_score < 0.5:
        level = RiskLevel.MEDIUM
    elif base_score < 0.75:
        level = RiskLevel.HIGH
    else:
        level = RiskLevel.CRITICAL

    if duplicated_exposure >= 0.5 and level != RiskLevel.CRITICAL:
        if level == RiskLevel.LOW:
            level = RiskLevel.MEDIUM
        elif level == RiskLevel.MEDIUM:
            level = RiskLevel.HIGH
        elif level == RiskLevel.HIGH:
            level = RiskLevel.CRITICAL

    return level.value


def concentration_risk_level(concentration_score: float, sector_overlap: float, currency_overlap: float, same_direction_ratio: float = 0.0) -> str:
    risk_input = max(concentration_score, sector_overlap, currency_overlap, same_direction_ratio)
    if risk_input < 0.25:
        return RiskLevel.LOW.value
    if risk_input < 0.5:
        return RiskLevel.MEDIUM.value
    if risk_input < 0.75:
        return RiskLevel.HIGH.value
    return RiskLevel.CRITICAL.value


def margin_risk_level(margin_usage: float, free_margin: float = 1.0) -> str:
    config = _load_config()
    threshold = float(config.get("max_margin_usage", 50)) / 100.0
    if margin_usage < threshold * 0.5:
        return RiskLevel.LOW.value
    if margin_usage < threshold * 0.75:
        return RiskLevel.MEDIUM.value
    if margin_usage < threshold:
        return RiskLevel.HIGH.value
    return RiskLevel.CRITICAL.value


def assess_portfolio_risk(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Heuristic risk assessment across portfolio dimensions."""
    concentration = max(0.0, min(1.0, float(metrics.get("concentration_score", 0.0))))
    correlation = max(0.0, min(1.0, float(metrics.get("correlation_score", 0.0))))
    exposure = max(0.0, min(1.0, float(metrics.get("exposure_score", 0.0))))
    margin = max(0.0, min(1.0, float(metrics.get("margin_usage", 0.0))))
    drawdown = max(0.0, min(1.0, float(metrics.get("drawdown", 0.0))))

    dimensions = [concentration, correlation, exposure, margin]
    if drawdown > 0.0:
        dimensions.append(drawdown)

    score = sum(dimensions) / len(dimensions) if dimensions else 0.0
    if score < 0.25:
        level = RiskLevel.LOW
    elif score < 0.5:
        level = RiskLevel.MEDIUM
    elif score < 0.75:
        level = RiskLevel.HIGH
    else:
        level = RiskLevel.CRITICAL

    return {
        "risk_level": level.value,
        "risk_score": round(score, 4),
        "dimensions": {
            "exposure": exposure,
            "concentration": concentration,
            "correlation": correlation,
            "margin_usage": margin,
            "drawdown": drawdown,
        },
    }
