# HEDGE MATH AUTONOMOUS TRADING OS — MVP Architecture

## Flow

Market Data → Data Validation → Technical Intelligence → Grid Math → Hedge Engine → FSM Brain → Risk Guard → Execution Adapter → Sweep → Backtest → Winner Genes → Dashboard.

## Agent Map

- Technical Lead Agent: điều phối, review, khóa live promotion.
- Infrastructure Agent: env, state, DB/Redis future, magic number.
- Market Data Agent: tick/OHLCV, spread, missing candle, independent source.
- Grid Math Agent: Step/X-Level coordinate.
- Hedge Strategy Agent: base hedge + surplus direction.
- FSM Brain Agent: trạng thái vận hành.
- Risk Guard Agent: chặn lệnh nguy hiểm.
- Execution Adapter Agent: mock/paper/live broker adapter.
- Sweep Agent: orphan order cleanup.
- Backtest Optimization Agent: tìm genes thắng.
- Winner Genes Memory Agent: lưu/promotion genes.
- Dashboard Control Agent: quan sát trạng thái.

## MVP restriction

Bản này là MOCK/PAPER-first. Live adapter thật phải được thêm sau khi có broker SDK, sandbox, log đầy đủ và kiểm thử độc lập.
