from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.brain.fsm import FsmBrainAgent
from app.core.config import get_settings
from app.core.models import FsmState, RobotState, RobotStatus, WinnerGene
from app.core.state_store import GeneStore, JsonStateStore
from app.strategy.hedge_engine import HedgeEngine
from app.governance import GovernanceManager
from app.evolution import EvolutionManager
from app.skills.optimization_engine.gene_search import BacktestOptimizer
from app.memory import MemoryManager
from app.skills.shared.memory import list_winner_genes, promote_gene, remember_gene
from app.identity.identity_manager import IdentityManager
from backend.app.skills.capital_engine.adapter import capital_analysis
from backend.app.skills.capital_engine.position_sizer import PositionSizer
from backend.app.skills.execution_engine.order_router import ExecutionAdapterAgent
from backend.app.skills.market_analysis.mock_market import MockMarketDataAgent
from backend.app.skills.no_trade_engine.no_trade_guard import NoTradeGuardAgent
from backend.app.skills.risk_engine.risk_guard import RiskGuardAgent
from enterprise_graph import EnterpriseGraphManager

settings = get_settings()


class WinnerGenesMemoryAgent:
    def __init__(self, store: GeneStore):
        self.store = store

    def remember(self, gene: WinnerGene) -> WinnerGene:
        return remember_gene(self.store, gene)

    def winners(self) -> list[WinnerGene]:
        return list_winner_genes(self.store)

    def promote(self, symbol: str, timeframe: str) -> WinnerGene | None:
        return promote_gene(self.store, symbol, timeframe)


state_store = JsonStateStore(settings.storage_path)
gene_store = GeneStore(settings.genes_path)
market_agent = MockMarketDataAgent()
no_trade_guard = NoTradeGuardAgent(settings)
risk_guard = RiskGuardAgent(settings)
capital_engine = PositionSizer(settings)
fsm_brain = FsmBrainAgent()
hedge_engine = HedgeEngine(settings.base_lot, settings.max_exposure_lots)
execution_agent = ExecutionAdapterAgent(settings)
optimizer = BacktestOptimizer()
genes_memory = WinnerGenesMemoryAgent(gene_store)
memory_agent = MemoryManager(settings.memory_path)
governance_agent = GovernanceManager(Path("./backend/app/governance"))
evolution_agent = EvolutionManager(
    memory_path=settings.memory_path,
    governance_rules_path=Path("./backend/app/governance"),
    metrics_path=Path("./backend/app/evolution/metrics/evolution_metrics.json"),
)
identity_agent = IdentityManager()
enterprise_graph_agent = EnterpriseGraphManager()


def get_or_create_robot_state() -> RobotState:
    restored = state_store.load_robot()
    if restored:
        return restored
    state = RobotState(
        robot_id=settings.robot_id,
        symbol=settings.default_symbol,
        broker=settings.broker_mode,
        magic_number=settings.magic_number,
        fsm_state=FsmState.BOOT,
    )
    state_store.save_robot(state)
    return state


def save_robot_state(state: RobotState) -> RobotState:
    state.last_heartbeat = datetime.now(timezone.utc)
    state_store.save_robot(state)
    return state
