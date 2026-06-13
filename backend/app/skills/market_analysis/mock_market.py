from __future__ import annotations

from app.core.models import MarketTick
from backend.app.skills.shared.mock_market import generate_tick, generate_ohlcv, validate_independent_source


class MockMarketDataAgent:
    """Skill-registry market data agent used by the runtime."""

    def __init__(self):
        self.name = "mock"

    def fetch_tick(self, symbol: str) -> MarketTick:
        return generate_tick(symbol=symbol, start_price=1.0, spread=0.0002)

    def fetch_ohlcv(self, symbol: str, num_candles: int = 20) -> list[dict]:
        """Fetch mock OHLCV candles for regime and volatility analysis."""
        return generate_ohlcv(symbol=symbol, start_price=1.0, num_candles=num_candles)

    def validate_independent_source(self, tick: MarketTick) -> bool:
        return validate_independent_source(tick)
