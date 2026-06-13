# Skill Metadata Standard

This repository now supports a Layer 4 skill metadata standard for the TUNGNS Copilot OS v3 architecture.

## Skill Metadata Pattern

Each skill module may expose a `METADATA` object of type `skills.shared.SkillMetadata`.

A standard skill metadata object contains:

- `name`: unique skill name or module path
- `description`: what the skill does
- `version`: semantic version for the skill
- `category`: skill category such as `market_analysis`, `signal_engine`, or `risk_management`
- `inputs`: list of input definitions
- `outputs`: list of output definitions
- `dependencies`: other skills, models, or data nodes required
- `examples`: usage examples that show the input and expected output
- `tags`: optional tags for discovery and classification

## Why this matters

This metadata helps the system understand:

- what each skill does
- what inputs it expects
- what outputs it produces
- how skills depend on one another
- how to document and validate skill usage

## Standardizing examples and dependencies

To make metadata easier for downstream systems to consume, follow these conventions:

### Dependencies

Dependencies should use fully-qualified type or module names that refer to the contract, not implementation details:

- **Skill internal functions**: Reference the module only, not individual functions.
  - ✅ `skills.signal_engine.ema_cross` — points to the module/capability
  - ❌ `skills.signal_engine.ema_cross.calculate_ema` — too specific

- **Skill schemas and output types**: Use the full type path.
  - ✅ `skills.market_analysis.schemas.TrendResult` — concrete type dependency
  - ✅ `skills.backtesting.schemas.BacktestResult`

- **External app models**: Use the type name from its canonical import path.
  - ✅ `app.core.models.RiskDecision` — type from core models
  - ✅ `app.core.config.Settings` — settings type from config

### Examples

Examples should always be dictionaries with `input` and `output` keys:

- `output` values should be JSON-friendly whenever possible, not free-form human text.
- For structured output types, use a simple serialized representation or small typed placeholder.

Example:

```python
examples=[
  {
    "input": {"prices": [1.0, 1.01, 1.02], "period": 3},
    "output": "buy"
  }
]
```

This repository now normalizes metadata during serialization through `SkillMetadata.to_dict()`.

## Skill metadata coverage

To verify metadata coverage across the repository, run:

```bash
python scripts/check_skill_metadata.py
```

This script scans `skills/` and reports any modules that should expose `METADATA` but do not.

To generate the current skill metadata registry for discovery and graph integration, run:

```bash
python scripts/generate_skill_metadata_registry.py
```

## Agent vs Skill Responsibility

### Agent responsibilities

- receive requests or workflow context
- validate, route, and orchestrate data
- select the correct skill(s) to call
- persist or forward results

### Skill responsibilities

- perform domain-specific business logic
- return structured outputs
- remain small and testable
- expose metadata for discovery

### Example pattern

```python
from skills.market_analysis.trend import detect_trend

result = detect_trend(prices, sensitivity=0.005)
```

An agent should not contain the trend analysis implementation itself.
Instead it should call `detect_trend(...)` and use the returned structured result.

### Agent → Skill calling pattern

Agents should be orchestrators, not business logic containers.
That means:

- validate input context and permissions in the agent layer
- choose the correct skill based on intent or workflow
- call skill functions and consume structured outputs
- do not implement signal generation, risk math, or order logic inside the agent

A good pattern is:

```python
from skills.signal_engine.ema_cross import calculate_ema, detect_ema_cross

class SignalAgent:
    def __init__(self, market_data):
        self.market_data = market_data

    def run(self):
        prices = self.market_data.prices
        short_ema = calculate_ema(prices, period=9)
        long_ema = calculate_ema(prices, period=21)
        signal = detect_ema_cross(short_ema, long_ema)
        return {"signal": signal, "short_ema": short_ema, "long_ema": long_ema}
```

If you want to reduce direct `skills.*` imports in backend agent files, introduce a small adapter or registry layer that maps a request to the appropriate skill call.
That keeps the agent layer focused on routing and leaves domain logic inside `skills/`.

## Generating the Enterprise Graph

Use the script below to build a graph of skills and imports:

```bash
python scripts/generate_enterprise_graph.py
```

The script writes:

- `enterprise_graph/enterprise_graph.json`
- `enterprise_graph/enterprise_graph.mermaid`
- `enterprise_graph/enterprise_graph.dot`

For a full architecture overview of the enterprise graph and how the graph fits into the OS, see `docs/enterprise_graph_overview.md`.

These files represent the current capability map of the system.
