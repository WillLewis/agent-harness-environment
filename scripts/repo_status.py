#!/usr/bin/env python3
"""Read-only repo hygiene report for local/generated artifacts.

Does not delete files or run git clean. Use before commits to confirm
generated outputs stay out of version control.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Paths that should be gitignored and must not appear in `git ls-files`.
GENERATED_SPECS: tuple[dict[str, str], ...] = (
    {
        "id": "runs",
        "path": "runs",
        "classification": "runner_generated_local_trace",
        "description": "Local runner traces and sandboxes (pnpm runner:batch)",
    },
    {
        "id": "trace_candidates",
        "path": "data/trace_candidates",
        "classification": "promoted_runner_trace",
        "description": "Promoted runner traces (promote_run_trace / runner:batch:promote)",
    },
    {
        "id": "generated_candidates",
        "path": "data/datasets/generated_candidates.jsonl",
        "classification": "mcp_promote_dataset",
        "description": "Append-only promote metadata from MCP or promote script",
    },
    {
        "id": "next_build",
        "path": "apps/web/.next",
        "classification": "next_build_output",
        "description": "Next.js build cache (pnpm build / pnpm dev)",
    },
)

TRACKED_GLOBS: tuple[str, ...] = (
    "runs/*",
    "data/trace_candidates/*",
    "data/datasets/generated_candidates.jsonl",
    "apps/web/.next/*",
    "**/*.tsbuildinfo",
    "**/__pycache__/**",
    "**/*.pyc",
)


def _run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


def _dir_file_count(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return 1
    return sum(1 for p in path.rglob("*") if p.is_file())


def _gitignore_covers(relative: str) -> bool:
    candidates = [relative]
    if not relative.endswith("/"):
        candidates.append(f"{relative}/")
        candidates.append(f"{relative}/.gitkeep")

    for candidate in candidates:
        result = subprocess.run(
            ["git", "check-ignore", "-q", candidate],
            cwd=PROJECT_ROOT,
            capture_output=True,
            check=False,
        )
        if result.returncode == 0:
            return True
    return False


def _tracked_generated_files() -> list[str]:
    tracked: list[str] = []
    for pattern in TRACKED_GLOBS:
        out = _run_git("ls-files", pattern)
        if out:
            tracked.extend(line for line in out.splitlines() if line.strip())
    return sorted(set(tracked))


def _working_tree_short() -> list[str]:
    out = _run_git("status", "--short")
    return [line for line in out.splitlines() if line.strip()] if out else []


def build_report() -> dict[str, Any]:
    artifacts: list[dict[str, Any]] = []
    for spec in GENERATED_SPECS:
        rel = spec["path"]
        full = PROJECT_ROOT / rel
        artifacts.append(
            {
                "id": spec["id"],
                "path": rel,
                "classification": spec["classification"],
                "description": spec["description"],
                "exists": full.exists(),
                "file_count": _dir_file_count(full),
                "gitignored": _gitignore_covers(rel),
            }
        )

    tracked = _tracked_generated_files()
    status_lines = _working_tree_short()
    warnings: list[dict[str, str]] = []

    for item in artifacts:
        if item["exists"] and not item["gitignored"]:
            warnings.append(
                {
                    "code": "generated_path_not_gitignored",
                    "severity": "error",
                    "message": f"{item['path']} exists but is not covered by .gitignore",
                }
            )

    if tracked:
        warnings.append(
            {
                "code": "tracked_generated_artifacts",
                "severity": "error",
                "message": "Generated artifacts are tracked in git; remove from index with git rm --cached",
            }
        )

    if status_lines:
        warnings.append(
            {
                "code": "dirty_working_tree",
                "severity": "info",
                "message": "Working tree has uncommitted changes (may be intentional source edits)",
            }
        )

    return {
        "repo_status_version": "1",
        "project_root": str(PROJECT_ROOT),
        "artifacts": artifacts,
        "tracked_generated_files": tracked,
        "working_tree_short": status_lines,
        "warnings": warnings,
        "ok": not any(w["severity"] == "error" for w in warnings),
    }


def format_table(report: dict[str, Any]) -> str:
    lines = [
        "Repo hygiene status",
        "=" * 72,
        f"ok={report['ok']}",
        "",
        "Generated artifacts (local-only; should be gitignored)",
        "-" * 72,
        f"{'path':<40} {'exists':>6} {'files':>6} {'ignored':>8}",
    ]
    for item in report["artifacts"]:
        lines.append(
            f"{item['path']:<40} {str(item['exists']):>6} {item['file_count']:>6} {str(item['gitignored']):>8}"
        )

    if report["tracked_generated_files"]:
        lines.extend(["", "TRACKED GENERATED FILES (should be empty)", "-" * 72])
        for path in report["tracked_generated_files"]:
            lines.append(f"  {path}")

    if report["working_tree_short"]:
        lines.extend(["", "git status --short", "-" * 72])
        lines.extend(f"  {line}" for line in report["working_tree_short"])

    if report["warnings"]:
        lines.extend(["", "Warnings", "-" * 72])
        for warning in report["warnings"]:
            lines.append(f"  [{warning['severity']}] {warning['code']}: {warning['message']}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only report of local/generated artifact hygiene.")
    parser.add_argument(
        "--format",
        choices=("json", "table"),
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    parser.add_argument(
        "--fail-on-tracked",
        action="store_true",
        help="Exit 1 if generated files are tracked in git",
    )
    args = parser.parse_args()

    report = build_report()

    if args.format == "json":
        indent = 2 if args.pretty else None
        print(json.dumps(report, indent=indent, separators=None if args.pretty else (",", ":")))
    else:
        print(format_table(report))

    if args.fail_on_tracked and report["tracked_generated_files"]:
        return 1
    if not report["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
