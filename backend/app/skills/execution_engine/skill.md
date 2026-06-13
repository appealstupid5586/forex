# Skill: Execution Engine

Purpose: Route orders through to broker execution: determine order status,
build broker order IDs, and log execution events.

Standard Input: `Order`, `Settings`
Standard Output: Updated `Order` with broker_order_id and status, or JSON 
with execution decision.

Responsibilities:
- Determine order status based on configuration and market conditions.
- Assign broker-specific order ID.
- Log execution events for audit trail.

Constraints: This skill orchestrates execution but does NOT perform direct
broker communication; that is delegated to broker adapters.
