from __future__ import annotations

from dataclasses import is_dataclass
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, List
import sys
import json


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"
BACKEND_ROOT = REPO_ROOT / "backend"
OUTPUT_ROOT = REPO_ROOT / "enterprise_graph"
OUTPUT_PATH = OUTPUT_ROOT / "skill_metadata_registry.json"

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(BACKEND_ROOT))


EXCLUDED_DIRS = {"shared"}
EXCLUDED_FILES = {"__init__.py", "schemas.py"}


def iter_skill_modules(root: Path) -> List[str]:
    modules: List[str] = []
    for path in sorted(root.rglob("*.py")):
        if path.name in EXCLUDED_FILES:
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        rel_path = path.relative_to(REPO_ROOT)
        if rel_path.parts[0] != "skills":
            continue
        module_name = ".".join(rel_path.with_suffix("").parts)
        modules.append(module_name)
    return modules


def load_metadata(module_name: str) -> Dict[str, Any] | None:
    try:
        module = import_module(module_name)
    except Exception as exc:
        print(f"WARNING: failed to import {module_name}: {exc}")
        return None

    metadata = getattr(module, "METADATA", None)
    if metadata is None:
        return None

    if hasattr(metadata, "to_dict"):
        return metadata.to_dict()
    if is_dataclass(metadata):
        return {"name": getattr(metadata, "name", module_name), **metadata.__dict__}
    return None


def main() -> int:
    if not SKILLS_ROOT.exists():
        print("skills directory not found")
        return 1

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    registry: Dict[str, Dict[str, Any]] = {}
    modules = iter_skill_modules(SKILLS_ROOT)
    for module_name in modules:
        metadata = load_metadata(module_name)
        if metadata is not None:
            registry[module_name] = metadata

    OUTPUT_PATH.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")

    missing = [m for m in modules if m not in registry]
    print(f"Skill metadata registry generated: {OUTPUT_PATH}")
    print(f"  Modules scanned: {len(modules)}")
    print(f"  Metadata entries: {len(registry)}")
    print(f"  Missing metadata: {len(missing)}")
    if missing:
        print("  First missing modules:")
        for module_name in missing[:20]:
            print(f"    - {module_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
