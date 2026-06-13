# Skill: Risk Engine

Purpose: Evaluate robot risk state and decide whether trading actions should be
allowed, paused, or reduced. Provides a programmatic API and an adapter that
returns JSON-friendly decisions for orchestration.

Standard Input: `RobotState`, optional `MarketTick`, `Settings`.
Standard Output: `RiskDecision` or JSON with `allowed`, `action`, `reasons`.

Constraints: The skill must not perform order execution; it only evaluates
risk and suggests actions.
