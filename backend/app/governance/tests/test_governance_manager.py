from backend.app.governance import GovernanceManager


def test_skill_permission_denied(tmp_path):
    rules_path = tmp_path
    (rules_path / "permissions.yaml").write_text("market_analysis: false\n")
    (rules_path / "risk_rules.yaml").write_text("max_risk_per_trade: 1\n")
    (rules_path / "capital_rules.yaml").write_text("max_account_drawdown: 15\nmax_margin_usage: 50\nminimum_free_margin: 40\n")
    (rules_path / "session_rules.yaml").write_text("asian_session: true\nlondon_session: true\nnew_york_session: true\n")
    (rules_path / "strategy_rules.yaml").write_text("breakout: true\n")

    manager = GovernanceManager(rules_path)
    decision = manager.approve_trade({
        "skill": "market_analysis",
        "strategy": "breakout",
        "risk": {"risk": 0.5},
        "capital": {"drawdown": 1, "margin_usage": 10, "free_margin": 80},
        "session": {"asian_session": true}
    })

    assert not decision.allowed
    assert decision.rule == "permissions"


def test_risk_validation_rejected(tmp_path):
    rules_path = tmp_path
    (rules_path / "permissions.yaml").write_text("market_analysis: true\n")
    (rules_path / "strategy_rules.yaml").write_text("breakout: true\n")
    (rules_path / "risk_rules.yaml").write_text("max_risk_per_trade: 1\n")
    (rules_path / "capital_rules.yaml").write_text("max_account_drawdown: 15\nmax_margin_usage: 50\nminimum_free_margin: 40\n")
    (rules_path / "session_rules.yaml").write_text("asian_session: true\nlondon_session: true\nnew_york_session: true\n")

    manager = GovernanceManager(rules_path)
    decision = manager.approve_trade({
        "skill": "market_analysis",
        "strategy": "breakout",
        "risk": {"risk": 5.0},
        "capital": {"drawdown": 1, "margin_usage": 10, "free_margin": 80},
        "session": {"asian_session": true}
    })

    assert not decision.allowed
    assert decision.rule == "risk_rules"


def test_capital_validation_shutdown(tmp_path):
    rules_path = tmp_path
    (rules_path / "permissions.yaml").write_text("execution_engine: true\n")
    (rules_path / "strategy_rules.yaml").write_text("breakout: true\n")
    (rules_path / "risk_rules.yaml").write_text("max_risk_per_trade: 1\n")
    (rules_path / "capital_rules.yaml").write_text("max_account_drawdown: 15\nmax_margin_usage: 50\nminimum_free_margin: 40\n")
    (rules_path / "session_rules.yaml").write_text("asian_session: true\nlondon_session: true\nnew_york_session: true\n")

    manager = GovernanceManager(rules_path)
    decision = manager.approve_trade({
        "skill": "execution_engine",
        "strategy": "breakout",
        "risk": {"risk": 0.5},
        "capital": {"drawdown": 20, "margin_usage": 60, "free_margin": 30},
        "session": {"asian_session": true}
    })

    assert not decision.allowed
    assert decision.rule == "capital_rules"


def test_session_blocked(tmp_path):
    rules_path = tmp_path
    (rules_path / "permissions.yaml").write_text("market_analysis: true\n")
    (rules_path / "strategy_rules.yaml").write_text("breakout: true\n")
    (rules_path / "risk_rules.yaml").write_text("max_risk_per_trade: 1\n")
    (rules_path / "capital_rules.yaml").write_text("max_account_drawdown: 15\nmax_margin_usage: 50\nminimum_free_margin: 40\n")
    (rules_path / "session_rules.yaml").write_text("asian_session: false\nlondon_session: false\nnew_york_session: false\n")

    manager = GovernanceManager(rules_path)
    decision = manager.approve_trade({
        "skill": "market_analysis",
        "strategy": "breakout",
        "risk": {"risk": 0.5},
        "capital": {"drawdown": 1, "margin_usage": 10, "free_margin": 80},
        "session": {"asian_session": false, "london_session": false, "new_york_session": false}
    })

    assert not decision.allowed
    assert decision.rule == "session_rules"
