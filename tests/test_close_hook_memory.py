import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.main import app
import app.core.runtime as runtime
from app.core.state_store import JsonStateStore
from app.core.runtime import evolution_agent
from app.core.models import MarketTick, RobotState, RobotStatus
from backend.app.memory.memory_manager import MemoryManager
from hooks.schemas import HookContext, CloseHookResult


def test_close_hook_blocks_and_records_evidence(tmp_path):
    runtime_state_path = tmp_path / "runtime_state.json"
    memory_state_path = tmp_path / "memory_store.json"

    # Override runtime state and evolution memory to isolate the test.
    runtime.state_store = JsonStateStore(str(runtime_state_path))
    evolution_agent.memory_manager = MemoryManager(str(memory_state_path))
    evolution_agent.hook_manager.before_close_hooks.clear()
    evolution_agent.hook_manager.after_close_hooks.clear()
    runtime.market_agent.validate_independent_source = lambda tick: True
    runtime.market_agent.fetch_tick = lambda symbol: MarketTick(symbol=symbol, bid=1.08000, ask=1.08010)

    robot_state = RobotState(
        robot_id="test-robot",
        symbol="EURUSD",
        broker="mock",
        magic_number=1,
        status=RobotStatus.RUNNING,
        equity=9400.0,
        balance=10000.0,
        drawdown_pct=4.0,
        margin_level_pct=9999.0,
        consecutive_loss=0,
    )
    runtime.state_store.save_robot(robot_state)

    before_close_results = []

    def before_close_hook(context: HookContext) -> CloseHookResult:
        result = CloseHookResult(proceed=False, reasons=["blocked_close"], metadata={"hook": "before_close"})
        before_close_results.append(result)
        return result

    after_close_called = []

    def after_close_hook(context: HookContext) -> CloseHookResult:
        after_close_called.append(True)
        return CloseHookResult(proceed=True, reasons=["closed"], metadata={"hook": "after_close"})

    evolution_agent.register_before_close_hook(before_close_hook)
    evolution_agent.register_after_close_hook(after_close_hook)

    client = TestClient(app)
    response = client.post("/api/v1/fsm/tick")
    assert response.status_code == 200

    data = response.json()
    assert data["risk"]["action"] == "PAUSE_EXECUTION"
    assert any("blocked_close" in reason for reason in data["risk"]["reasons"])
    assert not after_close_called
    assert len(before_close_results) == 1
    assert before_close_results[0].metadata == {"hook": "before_close"}

    memory_records = MemoryManager(str(memory_state_path)).load_memory()
    evidence_records = [record for record in memory_records if record.content.get("kind") == "evidence"]
    assert len(evidence_records) == 1

    evidence = evidence_records[0].content["content"]
    assert evidence["event"] == "before_close_blocked"
    assert "hook_results" in evidence
    assert evidence_records[0].tags == ["evidence", "close", "hook"]
    assert any(result["metadata"] == {"hook": "before_close"} and result["reasons"] == ["blocked_close"] for result in evidence["hook_results"])


def test_before_close_allows_and_runs_after_close(tmp_path):
    runtime_state_path = tmp_path / "runtime_state.json"
    memory_state_path = tmp_path / "memory_store.json"

    runtime.state_store = JsonStateStore(str(runtime_state_path))
    evolution_agent.memory_manager = MemoryManager(str(memory_state_path))
    evolution_agent.hook_manager.before_close_hooks.clear()
    evolution_agent.hook_manager.after_close_hooks.clear()
    runtime.market_agent.validate_independent_source = lambda tick: True
    runtime.market_agent.fetch_tick = lambda symbol: MarketTick(symbol=symbol, bid=1.08000, ask=1.08010)

    robot_state = RobotState(
        robot_id="test-robot",
        symbol="EURUSD",
        broker="mock",
        magic_number=1,
        status=RobotStatus.RUNNING,
        equity=9400.0,
        balance=10000.0,
        drawdown_pct=4.0,
        margin_level_pct=9999.0,
        consecutive_loss=0,
    )
    runtime.state_store.save_robot(robot_state)

    before_close_context = []

    before_close_context = []
    before_close_results = []

    def before_close_hook(context: HookContext) -> CloseHookResult:
        before_close_context.append(context)
        result = CloseHookResult(proceed=True, reasons=["allow_close"], metadata={"hook": "before_close"})
        before_close_results.append(result)
        return result

    after_close_called = []
    after_close_context = []
    after_close_results = []

    def after_close_hook(context: HookContext) -> CloseHookResult:
        after_close_called.append(True)
        after_close_context.append(context)
        result = CloseHookResult(proceed=True, reasons=["closed"], metadata={"hook": "after_close"})
        after_close_results.append(result)
        return result

    evolution_agent.register_before_close_hook(before_close_hook)
    evolution_agent.register_after_close_hook(after_close_hook)

    client = TestClient(app)
    response = client.post("/api/v1/fsm/tick")
    assert response.status_code == 200

    data = response.json()
    assert data["risk"]["action"] == "CLOSE_RISKY_ORDERS"
    assert any("allow_close" in reason for reason in data["risk"]["reasons"])
    assert after_close_called
    assert len(before_close_context) == 1
    assert len(after_close_context) == 1
    assert len(before_close_results) == 1
    assert len(after_close_results) == 1

    before_context = before_close_context[0]
    assert before_context.event == "before_close"
    assert before_context.payload["state"]["robot_id"] == "test-robot"
    assert before_context.payload["tick"]["symbol"] == "EURUSD"
    assert before_context.payload["risk"]["action"] == "CLOSE_RISKY_ORDERS"
    assert before_close_results[0].metadata == {"hook": "before_close"}

    after_context = after_close_context[0]
    assert after_context.event == "after_close"
    assert after_context.payload["state"]["robot_id"] == "test-robot"
    assert after_context.payload["tick"]["symbol"] == "EURUSD"
    assert after_context.payload["risk"]["action"] == "CLOSE_RISKY_ORDERS"
    assert after_close_results[0].metadata == {"hook": "after_close"}

    memory_records = MemoryManager(str(memory_state_path)).load_memory()
    assert not any(record.content.get("kind") == "evidence" and record.content.get("content", {}).get("event") == "before_close_blocked" for record in memory_records)

    failure_records = [record for record in memory_records if record.content.get("kind") == "failure"]
    assert len(failure_records) == 1
    assert failure_records[0].tags == ["failure", "close", "risk"]
    failure_content = failure_records[0].content["content"]
    assert failure_content["event"] == "close_action"
    assert failure_content["risk"]["action"] == "CLOSE_RISKY_ORDERS"
