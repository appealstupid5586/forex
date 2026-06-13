from pathlib import Path

from backend.app.skills.execution_engine import ExecutionAdapterAgent
from backend.app.skills.market_analysis import MockMarketDataAgent
from backend.app.skills.risk_engine import RiskGuardAgent


def test_skill_registry_replaces_legacy_capability_packages():
    assert MockMarketDataAgent is not None
    assert RiskGuardAgent is not None
    assert ExecutionAdapterAgent is not None

    assert not Path("backend/app/market").exists()
    assert not Path("backend/app/guard").exists()
    assert not Path("backend/app/execution").exists()
