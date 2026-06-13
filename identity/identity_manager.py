from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict
from typing import Any


@dataclass
class IdentityManager:
    mission: str = "Transform Experience into Evolution"
    vision: str = "AI Capability OS -> Enterprise OS -> Evolution"
    principles: tuple[str, ...] = (
        "Small Files",
        "Single Responsibility",
        "Skills First",
        "Memory First",
        "Governance First",
        "Hooks First",
    )

    def verify_structure(self, base_path: str | Path) -> Dict[str, bool]:
        base = Path(base_path)
        checks: Dict[str, bool] = {}
        checks["backend_exists"] = (base / "backend").exists()
        checks["skills_exists"] = (base / "skills").exists()
        checks["memory_exists"] = (base / "memory").exists()
        checks["governance_exists"] = (base / "governance").exists()
        checks["hooks_exists"] = (base / "hooks").exists()
        checks["tests_exists"] = (base / "tests").exists()
        return checks

    def load_config(self, path: str | Path | None = None) -> Dict[str, Any]:
        config_path = Path(path) if path else Path(__file__).resolve().parent / "config.yaml"
        if not config_path.exists():
            return {"error": "config not found"}
        data: Dict[str, Any] = {}
        with config_path.open("r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" not in line:
                    continue
                key, value = [p.strip() for p in line.split(":", 1)]
                data[key] = self._cast_value(value)
        return data

    @staticmethod
    def _cast_value(value: str) -> Any:
        lowered = value.lower()
        if lowered in {"true", "false"}:
            return lowered == "true"
        if value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError:
            return value

    def scan_for_violations(self, base_path: str | Path) -> Dict[str, list[str]]:
        """Scan the codebase for simple policy violations.

        Returns a dict with lists of file paths for each violation type.
        """
        base = Path(base_path)
        violations: Dict[str, list[str]] = {
            "yaml_in_skills": [],
            "file_open_in_skills": [],
            "agents_with_large_classes": [],
            "files_reading_yaml_anywhere": [],
            "imports_from_skills_in_agents": [],
        }

        # 1) Scan skills for yaml imports or opening yaml files
        skills_dir = base / "skills"
        if skills_dir.exists():
            for path in skills_dir.rglob("*.py"):
                try:
                    text = path.read_text(encoding="utf-8")
                except Exception:
                    continue
                lowered = text.lower()
                if "import yaml" in lowered or "pyyaml" in lowered or "from yaml" in lowered:
                    violations["yaml_in_skills"].append(str(path))
                if "open(" in text and (".yaml" in text or "'rules.yaml'" in text or '"rules.yaml"' in text or "'.yaml'" in text or '".yaml"' in text):
                    # crude check for opening yaml files
                    violations["file_open_in_skills"].append(str(path))

        # 2) Scan whole repo for files reading .yaml anywhere
        for path in base.rglob("*.py"):
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            if ".yaml" in text and ("open(" in text or "path(" in text.lower() or "read_text(" in text):
                violations["files_reading_yaml_anywhere"].append(str(path))

        # 3) Scan backend agents for large Agent classes (possible business logic)
        backend_dir = base / "backend"
        if backend_dir.exists():
            for path in (backend_dir / "app").rglob("*.py"):
                try:
                    text = path.read_text(encoding="utf-8")
                except Exception:
                    continue
                # find class declarations ending with Agent
                import re
                for m in re.finditer(r"class\s+(\w+Agent)\b", text):
                    start = m.start()
                    # estimate class length by lines until next class or EOF
                    lines_after = text[start:].splitlines()
                    length = 0
                    for ln in lines_after[1:]:
                        if ln.startswith("class "):
                            break
                        length += 1
                    if length > 80:
                        violations["agents_with_large_classes"].append(str(path))

                # detect imports from skills.* inside backend agent files
                if "from skills." in text or "import skills." in text:
                    violations["imports_from_skills_in_agents"].append(str(path))

        return violations
