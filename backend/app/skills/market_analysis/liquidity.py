"""Liquidity analysis skill implementations."""

from typing import List
from backend.app.skills.shared.skill_metadata import SkillIO, SkillMetadata


def calculate_average_volume(volumes: List[float]) -> float:
    """Compute average traded volume over the supplied history."""
    return sum(volumes) / max(len(volumes), 1)


def is_liquidity_spike(volumes: List[float], threshold: float = 2.0) -> bool:
    """Detect whether the latest volume is a spike versus recent history."""
    if len(volumes) < 2:
        return False

    average = calculate_average_volume(volumes[:-1])
    return average > 0 and volumes[-1] >= average * threshold

METADATA = SkillMetadata(
    name='skills.market_analysis.liquidity',
    description='Analyze liquidity by computing average volume and detecting volume spikes.',
    version='1.0.0',
    category='market_analysis',
    inputs=[
        SkillIO(name='volumes', description='Volume series for recent market activity.', data_type='List[float]', required=True, example=[1000.0, 1500.0, 4000.0]),
        SkillIO(name='threshold', description='Liquidity spike threshold multiplier.', data_type='float', required=False, example=2.0),
    ],
    outputs=[
        SkillIO(name='average_volume', description='Average traded volume.', data_type='float', required=True),
        SkillIO(name='liquidity_spike', description='Whether the latest volume is a liquidity spike.', data_type='bool', required=True),
    ],
    dependencies=[],
    examples=[{'input': {'volumes': [1000.0, 1100.0, 5000.0]}, 'output': {'average_volume': 2033.33, 'liquidity_spike': True}}],
    tags=['market_analysis', 'liquidity'],
)
