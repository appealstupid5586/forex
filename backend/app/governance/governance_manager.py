from __future__ import annotations

import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class GovernanceDecision:
    allowed: bool
    reason: str
    rule: str | None = None


class GovernanceManager:
    def __init__(self, rules_path: str | Path):
        self.rules_path = Path(rules_path)
        self.permissions = self._load_yaml("permissions.yaml")
        self.risk_rules = self._load_yaml("risk_rules.yaml")
        self.capital_rules = self._load_yaml("capital_rules.yaml")
        self.session_rules = self._load_yaml("session_rules.yaml")
        self.strategy_rules = self._load_yaml("strategy_rules.yaml")

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        path = self.rules_path / filename
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def is_skill_allowed(self, skill_name: str) -> GovernanceDecision:
        allowed = bool(self.permissions.get(skill_name, False))
        return GovernanceDecision(
            allowed=allowed,
            reason="Skill permission granted" if allowed else "Skill permission denied",
            rule="permissions"
        )

    def is_strategy_allowed(self, strategy_name: str) -> GovernanceDecision:
        allowed = bool(self.strategy_rules.get(strategy_name, False))
        return GovernanceDecision(
            allowed=allowed,
            reason="Strategy allowed" if allowed else "Strategy blocked",
            rule="strategy_rules"
        )

    def validate_risk(self, risk_data: Dict[str, Any]) -> GovernanceDecision:
        max_risk = float(self.risk_rules.get("max_risk_per_trade", 0))
        current_risk = float(risk_data.get("risk", 0))
        if current_risk > max_risk:
            return GovernanceDecision(
                allowed=False,
                reason=f"Risk {current_risk}% exceeds max allowed {max_risk}%",
                rule="risk_rules"
            )
        return GovernanceDecision(
            allowed=True,
            reason="Risk within allowed range",
            rule="risk_rules"
        )

    def validate_capital(self, capital_data: Dict[str, Any]) -> GovernanceDecision:
        drawdown = float(capital_data.get("drawdown", 0))
        max_drawdown = float(self.capital_rules.get("max_account_drawdown", 0))
        margin_usage = float(capital_data.get("margin_usage", 0))
        max_margin = float(self.capital_rules.get("max_margin_usage", 0))
        free_margin = float(capital_data.get("free_margin", 100))
        min_free = float(self.capital_rules.get("minimum_free_margin", 0))

        if drawdown > max_drawdown:
            return GovernanceDecision(
                allowed=False,
                reason=f"Drawdown {drawdown}% exceeds max allowed {max_drawdown}%",
                rule="capital_rules"
            )

        if margin_usage > max_margin:
            return GovernanceDecision(
                allowed=False,
                reason=f"Margin usage {margin_usage}% exceeds max allowed {max_margin}%",
                rule="capital_rules"
            )

        if free_margin < min_free:
            return GovernanceDecision(
                allowed=False,
                reason=f"Free margin {free_margin}% below minimum {min_free}%",
                rule="capital_rules"
            )

        return GovernanceDecision(
            allowed=True,
            reason="Capital protections pass",
            rule="capital_rules"
        )

    def validate_session(self, session_data: Dict[str, Any]) -> GovernanceDecision:
        if not any(self.session_rules.get(session, False) for session in ["asian_session", "london_session", "new_york_session"]):
            return GovernanceDecision(
                allowed=False,
                reason="No trading sessions are enabled",
                rule="session_rules"
            )
        return GovernanceDecision(
            allowed=True,
            reason="Session permissions allow trading",
            rule="session_rules"
        )

    def approve_trade(self, signal: Dict[str, Any]) -> GovernanceDecision:
        skill_check = self.is_skill_allowed(signal.get("skill", ""))
        if not skill_check.allowed:
            return skill_check

        strategy_check = self.is_strategy_allowed(signal.get("strategy", ""))
        if not strategy_check.allowed:
            return strategy_check

        risk_check = self.validate_risk(signal.get("risk", {}))
        if not risk_check.allowed:
            return risk_check

        capital_check = self.validate_capital(signal.get("capital", {}))
        if not capital_check.allowed:
            return capital_check

        session_check = self.validate_session(signal.get("session", {}))
        if not session_check.allowed:
            return session_check

        return GovernanceDecision(
            allowed=True,
            reason="Governance approved trade",
            rule="governance"
        )
