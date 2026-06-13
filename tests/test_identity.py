import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from identity.identity_manager import IdentityManager


def test_identity_structure_exists():
    manager = IdentityManager()
    checks = manager.verify_structure(ROOT)
    assert checks["backend_exists"] is True
    assert checks["skills_exists"] is True
    assert checks["memory_exists"] is True
    assert checks["governance_exists"] is True
    assert checks["hooks_exists"] is True
    assert checks["tests_exists"] is True
