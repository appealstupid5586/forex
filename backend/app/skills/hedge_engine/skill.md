# Skill: Hedge Engine

Purpose: Provide hedge-related capabilities: open/maintain hedge cycles, evaluate
surplus, and propose hedge orders to manage portfolio exposure and correlation.

Standard Input: The skill accepts either a `RobotState`/`HedgeCycle` context and
current `MarketTick`, or a `market_state` dict depending on the caller.

Standard Output: JSON-compatible object with keys: `decision`, `confidence`,
`evidence`, and `metadata`. When used programmatically the primary exported API
returns domain objects such as `HedgeCycle` and `Order` for execution agents.

Responsibilities:
- Open base hedge cycles given robot state and market tick.
- Evaluate surplus conditions and return hedge orders when thresholds are met.
- Maintain minimal bookkeeping for hedge ratio and surplus side.

Constraints:
- Must not perform direct order execution (execution handled by `execution-agent`).
- Must not compute position sizing beyond configured `base_lot`/`max_exposure_lots`.
- Keep logic pure so it can be unit-tested and evolved.

Notes:
- Implementations SHOULD expose both a programmatic API (classes/functions)
	and a lightweight adapter that returns the standard skill JSON when needed.

