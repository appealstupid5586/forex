# Skill: Sweep Engine

Purpose: Detect orphaned orders (broker-side orders not reflected in robot state)
and generate sweep (close) orders to clean them up.

Standard Input: `RobotState`, list of `Order` from broker.
Standard Output: Detected orphans and sweep orders, or JSON with sweep decision.

Responsibilities:
- Reconcile broker orders with robot state.
- Identify orphaned orders.
- Generate close orders for orphans.
- Log sweep events.

Constraints: Does not execute orders; only prepares sweep orders for execution.
