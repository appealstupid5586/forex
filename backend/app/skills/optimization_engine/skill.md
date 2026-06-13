# Skill: Optimization Engine

Purpose: Orchestrate parameter optimization and gene search across configurable
ranges for symbol, timeframe, step size, X level, and risk.

Standard Input: Search ranges for symbol, timeframe, step_range, x_range, risk_range.
Standard Output: Optimized parameter sets and fitness metrics.

Responsibilities:
- Coordinate parameter grid generation.
- Execute backtest on each parameter combination.
- Rank results by performance metrics.
- Return optimal gene candidates.

Constraints: For MVP only; replace with production backtest engine before live trading.
