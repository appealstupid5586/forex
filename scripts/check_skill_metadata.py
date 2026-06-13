from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"
EXCLUDED_DIRS = {"shared"}
EXCLUDED_FILES = {"__init__.py", "schemas.py"}


def iter_skill_modules(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.py")):
        if path.name in EXCLUDED_FILES:
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        yield path


def has_metadata(path: Path) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return False

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "METADATA":
                    return True
    return False


def should_require_metadata(path: Path) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return False

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return True
    return False


def main() -> int:
    if not SKILLS_ROOT.exists():
        print("Skills directory not found.")
        return 1

    missing = []
    for path in iter_skill_modules(SKILLS_ROOT):
        if should_require_metadata(path) and not has_metadata(path):
            missing.append(str(path.relative_to(REPO_ROOT)))

    print(f"Checked {sum(1 for _ in iter_skill_modules(SKILLS_ROOT))} skill modules.")
    print(f"Missing METADATA: {len(missing)}")
    if missing:
        for path in missing:
            print(f"  - {path}")
        return 1

    print("All skill modules that require metadata expose METADATA.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
