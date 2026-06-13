from backend.app.evolution.manager import EvolutionManager


def test_future_generation_and_self_correction(tmp_path):
    manager = EvolutionManager(memory_path=str(tmp_path / "memory"))
    evidence = {"symbol": "EURUSD", "event": "breakout"}

    futures = manager.generate_futures(evidence)
    corrected = manager.self_correct(futures)

    assert len(futures) == 3
    assert any(item["status"] == "kept" for item in corrected)
    assert any(item["status"] == "rejected" for item in corrected)


def test_regime_simulator_and_winner_dna(tmp_path):
    manager = EvolutionManager(memory_path=str(tmp_path / "memory"))
    strategy_data = {"strategy": "mean_reversion"}

    regimes = manager.simulate_regimes(strategy_data)
    dna = manager.extract_winner_dna()

    assert len(regimes) == 5
    assert isinstance(dna, dict)
    assert "winning_symbols" in dna
