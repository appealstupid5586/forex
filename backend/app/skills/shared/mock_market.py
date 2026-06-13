"""Mock market data generation logic moved out of the backend agent."""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from app.core.models import MarketTick


def generate_tick(symbol: str, start_price: float, spread: float) -> MarketTick:
    price = start_price + random.uniform(-0.00035, 0.00035)
    bid = price - spread / 2
    ask = price + spread / 2
    return MarketTick(symbol=symbol, bid=round(bid, 5), ask=round(ask, 5), timestamp=datetime.now(timezone.utc))


def generate_ohlcv(symbol: str, start_price: float, num_candles: int = 20) -> list[dict]:
    """Generate mock OHLCV candles for regime analysis."""
    candles = []
    current_price = start_price
    base_time = datetime.now(timezone.utc) - timedelta(minutes=num_candles)

    for i in range(num_candles):
        open_p = current_price
        close_p = current_price + random.uniform(-0.0005, 0.0005)
        high_p = max(open_p, close_p) + abs(random.uniform(0.0001, 0.0003))
        low_p = min(open_p, close_p) - abs(random.uniform(0.0001, 0.0003))
        timestamp = base_time + timedelta(minutes=i)

        candles.append(
            {
                "timestamp": timestamp.isoformat(),
                "open": round(open_p, 5),
                "high": round(high_p, 5),
                "low": round(low_p, 5),
                "close": round(close_p, 5),
                "volume": random.uniform(1000, 10000),
            }
        )
        current_price = close_p

    return candles


def validate_independent_source(tick: MarketTick) -> bool:
    simulated_mid = tick.mid + random.uniform(-0.00003, 0.00003)
    return abs(simulated_mid - tick.mid) <= 0.00005
