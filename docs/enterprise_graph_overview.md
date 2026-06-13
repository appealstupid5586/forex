# Enterprise Graph Overview

The Enterprise Graph is the brain of the TUNGNS Copilot OS architecture.
It captures the relationships between:

- skills
- agents
- runtime modules
- data dependencies
- capability boundaries

## Purpose

The graph helps the system understand:

- what capabilities exist
- what modules depend on each other
- which skills are invoked by backend agents
- where the system may need stronger governance or better memory

## Generated artifacts

This repository produces the following graph artifacts:

- `enterprise_graph/enterprise_graph.json`
- `enterprise_graph/enterprise_graph.mermaid`
- `enterprise_graph/enterprise_graph.dot`
- `enterprise_graph/skill_metadata_registry.json`

## How to generate the graph

Run the generator script from the repo root:

```bash
PYTHONPATH=. python scripts/generate_enterprise_graph.py
```

This writes the graph files and prints node/edge counts.

To generate the skill metadata registry, run:

```bash
PYTHONPATH=. python scripts/generate_skill_metadata_registry.py
```

To verify metadata coverage across skills, run:

```bash
python scripts/check_skill_metadata.py
```

## Graph structure

The graph currently distinguishes node categories like:

- `skill` — modules inside `skills/`
- `agent` — backend startup or orchestrator modules
- `runtime` — app runtime, API routes, or infrastructure support modules
- `data` — named data dependencies such as YAML/JSON/CSV files

Edges describe relationships such as:

- `capability` — skill or agent capability dependencies
- `data` — explicit data dependencies
- `depends_on` — generic imports or module-level dependency links

## Using the graph API

The backend exposes a graph API under `/api/v1/graph`.

### Useful endpoints

- `GET /api/v1/graph/status`
- `POST /api/v1/graph/populate`
- `GET /api/v1/graph/dump`
- `GET /api/v1/graph/export/dot`
- `GET /api/v1/graph/export/mermaid`
- `GET /api/v1/graph/subgraph`

### Example export

```bash
curl http://127.0.0.1:8000/api/v1/graph/export/mermaid
```

## Recommended workflow

1. Run `python scripts/generate_skill_metadata_registry.py` to build the metadata registry.
2. Run `python scripts/check_skill_metadata.py` to verify skills expose metadata.
3. Run `PYTHONPATH=. python scripts/generate_enterprise_graph.py` to refresh the graph.
4. Review `enterprise_graph/enterprise_graph.json` or the Mermaid/DOT exports.

## Why this matters for Copilot OS v3

The Enterprise Graph is the authoritative capability map for the system.
It supports the v3 architecture by making the OS aware of:

- what skills exist
- which skills are strong or weak
- how agents orchestrate skill execution
- data and governance boundaries
- the structure of the system as it evolves
