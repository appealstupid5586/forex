# HedgeMath OS MVP

MVP robot hedging operating system theo kiến trúc Agent + FSM + Risk Guard + Grid Math + Winner Genes.

## Skills Package

A new `skills/` package has been added to support modular strategy building and analysis.

Package structure:
- `skills/market_analysis` — market trend, support/resistance, liquidity analysis.
- `skills/signal_engine` — signal generation for EMA crossovers, breakouts, and structure breaks.
- `skills/risk_management` — position sizing, stop loss, take profit, and risk/reward tools.
- `skills/execution` — order payload builders for open, close, and modify operations.
- `skills/journal` — trade journaling, statistics, and export helpers.
- `skills/backtesting` — lightweight backtesting routines and performance metrics.
- `skills/memory` — short-term and long-term memory operating system primitives.
- `skills/shared` — shared models, constants, enums, exceptions, and utilities.

## Memory API

The backend exposes a memory API for saving and querying memory records.
- `POST /api/v1/memory/save` — save a generic memory entry.
- `POST /api/v1/memory/save-trade-context` — save a structured trade context record.
- `POST /api/v1/memory/short-term/save` — save short-term memory entries.
- `GET /api/v1/memory/short-term/recent` — retrieve recent short-term memories.
- `POST /api/v1/memory/query` — query memory by text and tags.
- `POST /api/v1/memory/market-insight` — query long-term market insight records.
- `GET /api/v1/memory/all` — list all saved memory records.

Example usage:

- `skills/market_analysis/trend.py`
- `skills/signal_engine/ema_cross.py`

## Chạy nhanh

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
```

## Skill Metadata và Enterprise Graph

- Skill modules can expose `METADATA` using `skills.shared.SkillMetadata`.
- See `docs/skill_metadata.md` for the Layer 4 skill metadata standard and agent/skill guidance.
- Generate the enterprise graph with:

```bash
python scripts/generate_enterprise_graph.py
```

This produces:
- `enterprise_graph/enterprise_graph.json`
- `enterprise_graph/enterprise_graph.mermaid`
- `enterprise_graph/enterprise_graph.dot`

### Giao diện mới
Giao diện hiện tại đã được thay bằng app `QuantDinger-Vue` trong thư mục `frontend`.

```bash
cd frontend
pnpm install
pnpm dev
```

Mặc định app frontend sẽ kết nối tới backend tại `http://127.0.0.1:8000`.

## cTrader live support

Repo hiện có một stub integration cho cTrader ở backend và frontend để chuẩn bị cho live trading production:
- Backend: `POST /api/ctrader/connect`, `GET /api/ctrader/status`, `GET /api/ctrader/account`, `GET /api/ctrader/positions`, `GET /api/ctrader/orders`, `POST /api/ctrader/order`, `DELETE /api/ctrader/order/{order_id}`, `GET /api/ctrader/quote`.
- Frontend: broker tab `cTrader` trong giao diện Broker Accounts và mục chọn broker `cTrader` cho Forex trading assistant.
- Env: `BROKER_MODE=ctrader` và `ALLOW_LIVE_EXECUTION=true` có thể dùng để bật luồng live-ready.

Hiện tại implementation là stub/ready-for-production và cần thay thế bằng calls thật tới cTrader Open API khi có credentials và app registration.

