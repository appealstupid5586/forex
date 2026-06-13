"""Mock market data generation logic moved out of the backend agent."""

from __future__ import annotations

import random
from datetime import datetime, timezone

from app.core.models import MarketTick


def generate_tick(symbol: str, start_price: float, spread: float) -> MarketTick:
    price = start_price + random.uniform(-0.00035, 0.00035)
    bid = price - spread / 2
    ask = price + spread / 2
    return MarketTick(symbol=symbol, bid=round(bid, 5), ask=round(ask, 5), timestamp=datetime.now(timezone.utc))


def validate_independent_source(tick: MarketTick) -> bool:
    simulated_mid = tick.mid + random.uniform(-0.00003, 0.00003)
    return abs(simulated_mid - tick.mid) <= 0.00005
