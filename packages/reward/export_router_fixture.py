#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER_DIR = ROOT / "services" / "runner"
if str(RUNNER_DIR) not in sys.path:
    sys.path.insert(0, str(RUNNER_DIR))

from router_state import export_decisions  # noqa: E402
from task_runner import TASK_CONFIGS, load_task  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Export learned router decisions for the hosted static demo.")
    parser.add_argument(
        "--output",
        default="data/router_decisions.json",
        help="Output fixture path relative to the project root.",
    )
    args = parser.parse_args([arg for arg in sys.argv[1:] if arg != "--"])

    tasks = [load_task(ROOT, task_id) for task_id in sorted(TASK_CONFIGS)]
    decisions = export_decisions(ROOT, tasks)
    output_path = ROOT / args.output
    output_path.write_text(json.dumps(decisions, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(output_path.relative_to(ROOT)), "task_count": len(tasks)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
