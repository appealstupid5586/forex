"""Trend analysis skill implementations."""

from typing import List

from .schemas import TrendResult, TrendDirection
from backend.app.skills.shared.skill_metadata import SkillIO, SkillMetadata


def detect_trend(prices: List[float], sensitivity: float = 0.005) -> TrendResult:
    """Detect a trend from a sequence of prices."""
    if len(prices) < 2:
        return TrendResult(direction=TrendDirection.NEUTRAL, confidence=0.0)

    delta = prices[-1] - prices[0]
    magnitude = abs(delta) / max(abs(prices[0]), 1.0)

    if magnitude < sensitivity:
        direction = TrendDirection.NEUTRAL
        confidence = 1.0 - magnitude / sensitivity
    elif delta > 0:
        direction = TrendDirection.BULLISH
        confidence = min(1.0, magnitude / (sensitivity * 5))
    else:
        direction = TrendDirection.BEARISH
        confidence = min(1.0, magnitude / (sensitivity * 5))

    return TrendResult(direction=direction, confidence=confidence)


METADATA = SkillMetadata(
    name="skills.market_analysis.trend.detect_trend",
    description="Detect market trend direction and confidence from price history.",
    version="1.0.0",
    category="market_analysis",
    inputs=[
        SkillIO(
            name="prices",
            description="A list of historical price values.",
            data_type="List[float]",
            required=True,
            example=[1.0, 1.01, 1.02],
        ),
        SkillIO(
            name="sensitivity",
            description="Minimum percentage movement required to define a trend.",
            data_type="float",
            required=False,
            example=0.005,
        ),
    ],
    outputs=[
        SkillIO(
            name="trend_result",
            description="Trend direction and confidence score.",
            data_type="TrendResult",
            required=True,
        )
    ],
    dependencies=["skills.market_analysis.schemas.TrendResult", "skills.market_analysis.schemas.TrendDirection"],
    examples=[
        {
            "input": {"prices": [1.0, 1.01, 1.02], "sensitivity": 0.005},
            "output": {"direction": "BULLISH", "confidence": 0.8},
        }
    ],
    tags=["trend", "market_analysis", "signal_preparation"],
)
