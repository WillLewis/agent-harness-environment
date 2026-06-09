#!/usr/bin/env python3
"""Deterministic hosted-demo deployment readiness checks (local only).

Does not deploy, call external services, or require secrets.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = PROJECT_ROOT / "apps" / "web"
DATA_ROOT = PROJECT_ROOT / "data"

REQUIRED_DATA_PATHS = (
    "tasks.json",
    "policies.json",
    "failure_clusters.json",
    "evals/policy_comparison.json",
    "traces/baseline_date_parser.json",
    "traces/guarded_recovery_date_parser.json",
)


def _check_monorepo_layout() -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for rel in (
        "package.json",
        "pnpm-workspace.yaml",
        "apps/web/package.json",
        "apps/web/next.config.mjs",
        "packages/harness/package.json",
    ):
        if not (PROJECT_ROOT / rel).exists():
            issues.append({"code": "missing_path", "message": f"Required path missing: {rel}"})
    return issues


def _check_fixture_paths() -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for rel in REQUIRED_DATA_PATHS:
        if not (DATA_ROOT / rel).exists():
            issues.append({"code": "missing_fixture", "message": f"Hosted build imports data/{rel}"})
    lib_dir = WEB_ROOT / "lib"
    if lib_dir.exists():
        import_paths: set[str] = set()
        for lib_file in lib_dir.rglob("*"):
            if lib_file.suffix not in {".ts", ".tsx"}:
                continue
            import_paths.update(
                re.findall(
                    r"from ['\"](\.\./\.\./\.\./data/[^'\"]+)['\"]",
                    lib_file.read_text(encoding="utf-8"),
                )
            )
        for import_path in sorted(import_paths):
            if import_path.startswith("../../../data/"):
                resolved = PROJECT_ROOT / "data" / import_path.removeprefix("../../../data/")
            else:
                resolved = (WEB_ROOT / "lib" / import_path).resolve()
            if not resolved.exists():
                issues.append(
                    {
                        "code": "broken_fixture_import",
                        "message": f"apps/web import does not resolve: {import_path}",
                    }
                )
    return issues


def _check_no_api_routes() -> list[dict[str, str]]:
    api_dir = WEB_ROOT / "app" / "api"
    if api_dir.exists() and any(api_dir.rglob("*")):
        return [{"code": "api_routes_present", "message": "app/api routes are not expected for static demo"}]
    return []


# Build-time deploy toggles for the Cloudflare static export. These are NOT runtime
# secrets: they only switch `next build` into static-export mode and set the asset
# base path, both have safe defaults (unset => normal build; base path => "/harness"),
# and they are documented in docs/DEPLOYMENT.md. The hosted bundle ships no runtime
# env dependency, so these are allowed; anything else under process.env is still flagged.
ALLOWED_BUILD_ENV = {"AHE_DEPLOY_TARGET", "AHE_PUBLIC_BASE_PATH"}


def _check_env_usage() -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for path in WEB_ROOT.rglob("*"):
        if path.suffix not in {".ts", ".tsx", ".js", ".jsx", ".mjs"}:
            continue
        if {"node_modules", ".next", "out"} & set(path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "process.env" not in text:
            continue
        referenced = set(re.findall(r"process\.env\.([A-Za-z_][A-Za-z0-9_]*)", text))
        bare_env = re.search(r"process\.env(?!\.[A-Za-z_])", text) is not None
        disallowed = referenced - ALLOWED_BUILD_ENV
        if bare_env or disallowed:
            detail = ", ".join(sorted(disallowed)) if disallowed else "process.env"
            issues.append(
                {
                    "code": "env_var_usage",
                    "message": f"undocumented process.env ({detail}) in {path.relative_to(PROJECT_ROOT)} — document in docs/DEPLOYMENT.md",
                }
            )
    return issues


def _check_root_build_script() -> list[dict[str, str]]:
    pkg = json.loads((PROJECT_ROOT / "package.json").read_text(encoding="utf-8"))
    build = pkg.get("scripts", {}).get("build", "")
    if "filter @ahe/web" not in build and "apps/web" not in build:
        return [{"code": "build_script", "message": "Root package.json build should target @ahe/web"}]
    return []


def build_report() -> dict[str, Any]:
    checks = {
        "monorepo_layout": _check_monorepo_layout(),
        "fixture_paths": _check_fixture_paths(),
        "no_api_routes": _check_no_api_routes(),
        "no_env_vars": _check_env_usage(),
        "root_build_script": _check_root_build_script(),
    }
    issues = [issue for group in checks.values() for issue in group]
    return {
        "deployment_check_version": "1",
        "project_root": str(PROJECT_ROOT),
        "recommended_host": "vercel",
        "build_command": "pnpm build",
        "preview_command": "pnpm preview",
        "environment_variables_required": [],
        "checks": checks,
        "issue_count": len(issues),
        "ok": len(issues) == 0,
    }


def format_table(report: dict[str, Any]) -> str:
    lines = [
        "Deployment readiness",
        "=" * 72,
        f"ok={report['ok']}  recommended_host={report['recommended_host']}",
        f"build: {report['build_command']}  preview: {report['preview_command']}",
        f"env vars required: {report['environment_variables_required'] or '(none)'}",
        "",
    ]
    for name, issues in report["checks"].items():
        status = "ok" if not issues else "FAIL"
        lines.append(f"  [{status}] {name}")
        for issue in issues:
            lines.append(f"         {issue['code']}: {issue['message']}")
    if report["ok"]:
        lines.append("")
        lines.append("See docs/DEPLOYMENT.md for Vercel/Netlify settings and post-deploy smoke.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Local deployment readiness checks for apps/web.")
    parser.add_argument("--format", choices=("json", "table"), default="table")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report()

    if args.format == "json":
        indent = 2 if args.pretty else None
        print(json.dumps(report, indent=indent, separators=None if args.pretty else (",", ":")))
    else:
        print(format_table(report))

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
