#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "packages" / "evals"
if str(EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(EVAL_DIR))

from fixture_validation import validate_trace  # noqa: E402


def main() -> int:
    errors: list[str] = []
    for path in sorted((ROOT / "data" / "traces").glob("*.json")):
        errors.extend(validate_trace(path))
    if errors:
        print("Fixture validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Fixture validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
