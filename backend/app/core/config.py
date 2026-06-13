from __future__ import annotations

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central runtime configuration.

    LIVE trading is intentionally disabled by default. Promote from MOCK/PAPER
    to LIVE only after tests, walk-forward validation, and manual review.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "HedgeMath OS MVP"
    env: str = Field(default="dev", description="dev|paper|live")
    broker_mode: str = Field(default="mock", description="mock|paper|mt5|ctrader|binance|bitget")
    robot_id: str = "hedge-math-os-001"
    magic_number: int = 29052026
    default_symbol: str = "EURUSD"
    default_timeframe: str = "M1"

    storage_path: str = "./runtime_state.json"
    genes_path: str = "./winner_genes.json"
    memory_path: str = "./backend/app/memory"
    logs_path: str = "./execution_logs.jsonl"
    graph_path: str = "./data/enterprise_graph.json"

    max_drawdown_pct: float = 10.0
    equity_guard_pct: float = 5.0
    max_spread_points: float = 25.0
    max_api_latency_ms: int = 1200
    max_consecutive_loss: int = 5
    min_margin_level_pct: float = 300.0
    max_exposure_lots: float = 0.10

    base_lot: float = 0.01
    tick_size: float = 0.00001
    default_step_size: float = 0.0010
    default_x_level: int = 2

    allow_live_execution: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
