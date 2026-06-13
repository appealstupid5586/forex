from backend.app.governance.governance_manager import GovernanceManager


def test_governance_manager_loads_rules():
    manager = GovernanceManager("backend/app/governance")
    rules = manager._load_yaml("risk_rules.yaml")

    assert rules["max_risk_per_trade"] == 1
    assert rules["max_open_positions"] == 5


# Legacy root governance tests removed due to governance migration
