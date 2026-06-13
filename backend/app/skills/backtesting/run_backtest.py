"""Backtesting engine entry point."""

from typing import List, Dict

from .schemas import BacktestResult
from backend.app.skills.shared.skill_metadata import SkillIO, SkillMetadata


def run_backtest(prices: List[float], signals: List[str]) -> BacktestResult:
    capital = 10000.0
    position = 0.0
    trade_log = []

    for index, signal in enumerate(signals):
        price = prices[index]
        if signal == "buy" and position == 0:
            position = capital / price
            trade_log.append({"type": "buy", "price": price})
        elif signal == "sell" and position > 0:
            capital = position * price
            trade_log.append({"type": "sell", "price": price})
            position = 0.0

    return BacktestResult(final_balance=capital, trades=trade_log)

METADATA = SkillMetadata(
    name='skills.backtesting.run_backtest',
    description='Execute a simple backtest using price history and trading signals.',
    version='1.0.0',
    category='backtesting',
    inputs=[
        SkillIO(name='prices', description='Historical price series for backtesting.', data_type='List[float]', required=True, example=[100.0, 101.0, 102.0]),
        SkillIO(name='signals', description='Trading signals mapped to each price.', data_type='List[str]', required=True, example=['buy', 'hold', 'sell']),
    ],
    outputs=[
        SkillIO(name='final_balance', description='Final account balance after backtest.', data_type='float', required=True),
        SkillIO(name='trades', description='Executed trade log.', data_type='List[dict]', required=True),
    ],
    dependencies=['skills.backtesting.schemas.BacktestResult'],
    examples=[{
        'input': {'prices': [100.0, 105.0, 110.0], 'signals': ['buy', 'hold', 'sell']},
        'output': {'final_balance': 11000.0, 'trades': [{'type': 'buy', 'price': 100.0}]},
    }],
    tags=['backtesting', 'simulation', 'signals'],
)
