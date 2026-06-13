# Skill: Backtesting

Purpose: Replay market data against a strategy to discover drawdown, failure conditions, regime fit, and strategy weaknesses.

Standard Input: JSON with `strategy`, `market_data`, and `config`.

Standard Output: JSON with `win_rate`, `profit_factor`, `max_drawdown`, `best_regime`, `worst_regime`, `weaknesses`, and `evidence`.

Responsibilities:
- Replay historical trades or signals.
- Calculate statistics and drawdown.
- Analyze market regime performance.
- Discover weaknesses and failure conditions.
- Generate evidence-first reports.

Constraints:
- Do not place live trades.
- Do not generate signals.
- Do not save opinions as memory.
- Save only evidence suitable for Memory OS and Evolution.
