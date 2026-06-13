from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.memory import MemoryManager
from app.governance import GovernanceManager

from .pattern_discovery import PatternDiscoveryEngine
from .strategy_evaluator import StrategyEvaluator
from .weakness_detector import WeaknessDetector
from .improvement_engine import ImprovementEngine
from .future_generator import FutureGenerator
from .self_correction_engine import SelfCorrectionEngine
from .regime_simulator import RegimeSimulator
from .winner_dna import WinnerDna


@dataclass
class EvolutionMetrics:
    discovered_patterns: int = 0
    recommendations_generated: int = 0
    weaknesses_detected: int = 0
    confidence_score: float = 0.0


class EvolutionManager:
    def __init__(self, memory_path: str | None = None, governance_rules_path: str | None = None, metrics_path: str | None = None):
        self.memory_manager = MemoryManager(Path(memory_path) if memory_path else None)
        self.governance_manager = GovernanceManager(Path(governance_rules_path) if governance_rules_path else Path("./backend/app/governance"))
        self.pattern_engine = PatternDiscoveryEngine(self.memory_manager)
        self.strategy_evaluator = StrategyEvaluator(self.memory_manager)
        self.weakness_detector = WeaknessDetector(self.memory_manager)
        self.improvement_engine = ImprovementEngine(self.memory_manager)
        self.future_generator = FutureGenerator(self.memory_manager)
        self.self_correction_engine = SelfCorrectionEngine(self.memory_manager)
        self.regime_simulator = RegimeSimulator(self.memory_manager)
        self.winner_dna = WinnerDna(self.memory_manager)
        self.metrics_path = Path(metrics_path or "./backend/app/evolution/metrics/evolution_metrics.json")
        self.metrics = EvolutionMetrics()

    def discover_patterns(self) -> list[dict[str, Any]]:
        patterns = self.pattern_engine.discover()
        self.metrics.discovered_patterns = len(patterns)
        self._save_metrics()
        return patterns

    def evaluate_strategy(self, portfolio_data: dict[str, Any]) -> dict[str, Any]:
        result = self.strategy_evaluator.evaluate(portfolio_data)
        return result

    def detect_weaknesses(self, evidence: dict[str, Any]) -> list[dict[str, Any]]:
        weaknesses = self.weakness_detector.detect(evidence)
        self.metrics.weaknesses_detected = len(weaknesses)
        self._save_metrics()
        return weaknesses

    def generate_recommendations(self, weaknesses: list[dict[str, Any]]) -> list[dict[str, Any]]:
        recommendations = self.improvement_engine.suggest(weaknesses)
        self.metrics.recommendations_generated = len(recommendations)
        if recommendations:
            self.metrics.confidence_score = sum(item.get("confidence", 0.0) for item in recommendations) / len(recommendations)
        self._save_metrics()
        return recommendations

    def generate_futures(self, evidence: dict[str, Any]) -> list[dict[str, Any]]:
        futures = self.future_generator.generate(evidence)
        self.metrics.discovered_patterns = len(futures)
        self._save_metrics()
        return futures

    def self_correct(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        refined = self.self_correction_engine.refine(candidates)
        return refined

    def simulate_regimes(self, strategy_data: dict[str, Any]) -> list[dict[str, Any]]:
        return self.regime_simulator.simulate(strategy_data)

    def extract_winner_dna(self) -> dict[str, Any]:
        return self.winner_dna.extract()

    def save_evolution_history(self, record: dict[str, Any]) -> str:
        record_path = Path("./backend/app/evolution/history")
        record_path.mkdir(parents=True, exist_ok=True)
        filename = record_path / f"evolution_{record.get('timestamp', Path(record_path).stem)}.json"
        filename.write_text(json.dumps(record, default=str, ensure_ascii=False, indent=2))
        return str(filename)

    def _save_metrics(self) -> None:
        self.metrics_path.parent.mkdir(parents=True, exist_ok=True)
        self.metrics_path.write_text(json.dumps(self.metrics.__dict__, ensure_ascii=False, indent=2))

    def save_failure(self, content: dict[str, Any], tags: list[str] | None = None):
        return self.memory_manager.save_failure(content, tags)

    def save_evidence(self, content: dict[str, Any], tags: list[str] | None = None):
        return self.memory_manager.save_evidence(content, tags)
