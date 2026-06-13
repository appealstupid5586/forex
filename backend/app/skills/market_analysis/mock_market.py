from __future__ import annotations

from app.core.models import MarketTick
from backend.app.skills.shared.mock_market import generate_tick, validate_independent_source


class MockMarketDataAgent:
    """Skill-registry market data agent used by the runtime."""

    def __init__(self):
        self.name = "mock"

    def fetch_tick(self, symbol: str) -> MarketTick:
        return generate_tick(symbol=symbol, start_price=1.0, spread=0.0002)

    def validate_independent_source(self, tick: MarketTick) -> bool:
        return validate_independent_source(tick)
