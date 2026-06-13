"""Support and resistance detection skill implementations."""

from typing import List, Tuple
from backend.app.skills.shared.skill_metadata import SkillIO, SkillMetadata


def find_support_resistance(prices: List[float], window: int = 5) -> Tuple[List[float], List[float]]:
    """Identify simple support and resistance levels from recent price data."""
    if len(prices) < window * 2 + 1:
        return [], []

    supports = []
    resistances = []
    for i in range(window, len(prices) - window):
        current = prices[i]
        before = prices[i - window: i]
        after = prices[i + 1: i + 1 + window]

        if current <= min(before + after):
            supports.append(current)
        if current >= max(before + after):
            resistances.append(current)

    return supports, resistances

METADATA = SkillMetadata(
    name='skills.market_analysis.support_resistance',
    description='Identify support and resistance levels from price history.',
    version='1.0.0',
    category='market_analysis',
    inputs=[
        SkillIO(name='prices', description='Price series for support/resistance detection.', data_type='List[float]', required=True, example=[1.0, 1.01, 1.02, 1.03, 1.02, 1.01]),
        SkillIO(name='window', description='Window size for level detection.', data_type='int', required=False, example=5),
    ],
    outputs=[
        SkillIO(name='supports', description='Detected support levels.', data_type='List[float]', required=True),
        SkillIO(name='resistances', description='Detected resistance levels.', data_type='List[float]', required=True),
    ],
    dependencies=[],
    examples=[{'input': {'prices': [1.0, 1.1, 1.05, 1.2, 1.15, 1.25]}, 'output': {'supports': [], 'resistances': [1.2]}}],
    tags=['market_analysis', 'support_resistance'],
)
