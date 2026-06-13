"""Equity curve generation skill."""

from typing import List
from backend.app.skills.shared.skill_metadata import SkillIO, SkillMetadata


def build_equity_curve(prices: List[float], positions: List[float]) -> List[float]:
    return [price * position for price, position in zip(prices, positions)]

METADATA = SkillMetadata(
    name='skills.backtesting.equity_curve.build_equity_curve',
    description='Build an equity curve from historical prices and position sizes.',
    version='1.0.0',
    category='backtesting',
    inputs=[
        SkillIO(name='prices', description='Historical price series.', data_type='List[float]', required=True, example=[100.0, 101.0, 102.0]),
        SkillIO(name='positions', description='Position size for each price point.', data_type='List[float]', required=True, example=[1.0, 1.0, 1.0]),
    ],
    outputs=[
        SkillIO(name='equity_curve', description='Calculated equity curve values.', data_type='List[float]', required=True),
    ],
    dependencies=[],
    examples=[{'input': {'prices': [100.0, 101.0, 102.0], 'positions': [1.0, 1.0, 1.0]}, 'output': [100.0, 101.0, 102.0]}],
    tags=['backtesting', 'equity_curve', 'metrics'],
)
