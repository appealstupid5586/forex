from __future__ import annotations

import json
import sys
from pathlib import Path

from identity.identity_manager import IdentityManager


def main():
    repo_root = Path(__file__).resolve().parents[1]
    mgr = IdentityManager()
    violations = mgr.scan_for_violations(repo_root)
    # write violations to file for workflow consumption
    out = repo_root / "violations.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(violations, f, indent=2)
    print(json.dumps(violations, indent=2))
    # do not exit with error here; workflow will decide based on critical keys
    return 0


if __name__ == "__main__":
    main()
