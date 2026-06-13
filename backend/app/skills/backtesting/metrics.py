"""Backtesting metrics calculation skill."""

from typing import List
from backend.app.skills.shared.skill_metadata import SkillIO, SkillMetadata


def calculate_return(start_balance: float, end_balance: float) -> float:
    return (end_balance - start_balance) / max(start_balance, 1.0)


def calculate_sharpe(returns: List[float], risk_free_rate: float = 0.0) -> float:
    if not returns:
        return 0.0
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    std_dev = variance ** 0.5
    return 0.0 if std_dev == 0 else (mean_return - risk_free_rate) / std_dev

METADATA = SkillMetadata(
    name='skills.backtesting.metrics',
    description='Calculate backtesting performance metrics such as return and Sharpe ratio.',
    version='1.0.0',
    category='backtesting',
    inputs=[
        SkillIO(name='start_balance', description='Starting account balance.', data_type='float', required=True, example=10000.0),
        SkillIO(name='end_balance', description='Ending account balance.', data_type='float', required=True, example=11000.0),
        SkillIO(name='returns', description='Sequence of period returns.', data_type='List[float]', required=False, example=[0.01, 0.02, -0.005]),
        SkillIO(name='risk_free_rate', description='Risk-free return rate for Sharpe ratio calculation.', data_type='float', required=False, example=0.0),
    ],
    outputs=[
        SkillIO(name='return', description='Total return over the period.', data_type='float', required=True),
        SkillIO(name='sharpe_ratio', description='Sharpe ratio calculated from returns.', data_type='float', required=True),
    ],
    dependencies=[],
    examples=[{
        'input': {'start_balance': 10000.0, 'end_balance': 11000.0, 'returns': [0.01, 0.02]},
        'output': {'return': 0.1, 'sharpe_ratio': 1.3},
    }],
    tags=['backtesting', 'metrics', 'performance'],
)
