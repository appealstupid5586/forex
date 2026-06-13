from pathlib import Path

from backend.app.evolution.manager import EvolutionManager


def test_evolution_manager_discover_patterns_empty_memory(tmp_path):
    memory_path = tmp_path / "memory"
    manager = EvolutionManager(memory_path=str(memory_path))

    assert manager.discover_patterns() == []


def test_evolution_manager_detect_weaknesses_and_recommendations(tmp_path):
    memory_path = tmp_path / "memory"
    manager = EvolutionManager(memory_path=str(memory_path))
    evidence = {
        "performance": {"drawdown": 12, "win_rate": 0.48},
        "symbol": "EURUSD",
        "session": {"name": "asian_session"},
    }

    weaknesses = manager.detect_weaknesses(evidence)
    recommendations = manager.generate_recommendations(weaknesses)

    assert any(w.get("type") == "regime_weakness" for w in weaknesses)
    assert any(w.get("type") == "strategy_weakness" for w in weaknesses)
    assert any(w.get("type") == "session_weakness" for w in weaknesses)
    assert any(r.get("action") == "reduce_risk" for r in recommendations)
    assert any(r.get("action") == "strategy_review" for r in recommendations)
    assert any(r.get("action") == "session_adjustment" for r in recommendations)


def test_evolution_manager_save_evolution_history(tmp_path):
    memory_path = tmp_path / "memory"
    manager = EvolutionManager(memory_path=str(memory_path))
    record = {"timestamp": "2026-06-12T00:00:00Z", "summary": "evolution run"}

    history_path = manager.save_evolution_history(record)
    assert Path(history_path).exists()
    assert "evolution_2026-06-12T00:00:00Z" in history_path
