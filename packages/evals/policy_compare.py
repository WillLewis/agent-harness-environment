#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/evals/policy_comparison.json")
    rows = json.loads(path.read_text())
    print("Policy comparison")
    print("-" * 92)
    print(f"{'policy':<24} {'success':>8} {'recovery':>9} {'loop':>6} {'hallucinated':>13} {'unsafe':>8} {'human':>8}")
    for row in rows:
        print(
            f"{row['policy']:<24} {row['success']:>7}% {row['recovery']:>8}% {row['loop']:>5}% "
            f"{row['hallucinatedFiles']:>12}% {row['unsafeAttempts']:>7}% {row['humanInterventions']:>8}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
