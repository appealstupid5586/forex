import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from identity.identity_manager import IdentityManager


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_scan_detects_yaml_in_skills(tmp_path):
    # Setup fake repo structure
    skills_dir = tmp_path / "skills"
    bad_skill = skills_dir / "bad_skill.py"
    write_file(bad_skill, "import yaml\nopen('rules.yaml')\n")

    backend_agent = tmp_path / "backend" / "app" / "agents" / "bad_agent.py"
    # create a class Agent with >80 lines and an import from skills
    lines = ["from skills.some_skill import helper\n", "class BadAgent:\n"] + ["    def line(self):\n        pass\n" for _ in range(100)]
    write_file(backend_agent, "\n".join(lines))

    mgr = IdentityManager()
    violations = mgr.scan_for_violations(tmp_path)

    assert any(str(bad_skill) in p for p in violations["yaml_in_skills"])
    assert any(str(bad_skill) in p for p in violations["file_open_in_skills"])
    assert any(str(backend_agent) in p for p in violations["agents_with_large_classes"])
    assert any(str(backend_agent) in p for p in violations["imports_from_skills_in_agents"])
