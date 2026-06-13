"""Schemas for backtesting results."""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class BacktestResult:
    final_balance: float
    trades: List[Dict[str, object]]
