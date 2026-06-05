#!/usr/bin/env python3
"""URL-based smoke check for the hosted static demo (no browser required).

Fetches HTML and verifies server-rendered shell signals. Does not execute
client-side JavaScript, so interactive policy toggles are out of scope.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Any, Callable

SMOKE_VERSION = "1"
DEFAULT_URL = "http://localhost:3000"
DEFAULT_TIMEOUT = 15.0

LIMITATION_NOTE = (
    "Validates server-rendered HTML only (Next.js static/RSC shell). "
    "Does not execute client JS, capture screenshots, or verify policy-toggle behavior."
)


CheckFn = Callable[[str], tuple[bool, str]]


def _contains(html: str, needle: str, *, case_insensitive: bool = False) -> bool:
    if case_insensitive:
        return needle.lower() in html.lower()
    return needle in html


def _build_check_specs() -> list[tuple[str, str, CheckFn]]:
    def make_contains(
        needle: str,
        *,
        case_insensitive: bool = False,
        missing: str | None = None,
    ) -> CheckFn:
        def _run(html: str) -> tuple[bool, str]:
            ok = _contains(html, needle, case_insensitive=case_insensitive)
            return ok, "" if ok else (missing or f"Missing text: {needle!r}")

        return _run

    def make_all(*needles: str, case_insensitive: bool = True) -> CheckFn:
        def _run(html: str) -> tuple[bool, str]:
            missing = [n for n in needles if not _contains(html, n, case_insensitive=case_insensitive)]
            if missing:
                return False, f"Missing: {', '.join(missing)}"
            return True, ""

        return _run

    return [
        (
            "title_brand",
            "Page title includes Agent Harness Environment",
            lambda html: (
                _contains(html, "<title>Agent Harness Environment</title>")
                or _contains(html, "Agent Harness Environment", case_insensitive=True),
                "Missing <title> or Agent Harness Environment branding",
            ),
        ),
        (
            "hero_headline",
            "Hero headline present",
            make_contains("A flight recorder for coding agents."),
        ),
        (
            "static_demo_copy",
            "Static demo / no live runner copy in hero",
            make_all(
                "Static hosted demo",
                "No live LLM",
                case_insensitive=False,
            ),
        ),
        (
            "task_classes_hero",
            "Three task classes mentioned in hero copy",
            make_all("bugfix", "adversarial", "multi-agent"),
        ),
        (
            "anchor_cockpit",
            "Cockpit section anchor",
            lambda html: (
                'id="cockpit"' in html and '#cockpit' in html,
                'Missing id="cockpit" or href="#cockpit"',
            ),
        ),
        (
            "anchor_evals",
            "Eval report section anchor",
            lambda html: (
                'id="evals"' in html,
                'Missing id="evals"',
            ),
        ),
        (
            "anchor_architecture",
            "Implementation / architecture section anchor",
            lambda html: (
                'id="architecture"' in html and '#architecture' in html,
                'Missing id="architecture" or href="#architecture"',
            ),
        ),
        (
            "cockpit_section",
            "Interactive cockpit section heading",
            make_contains("Interactive cockpit"),
        ),
        (
            "eval_section",
            "Policy comparison eval table heading",
            make_contains("Policy comparison"),
        ),
        (
            "implementation_section",
            "Implementation evidence section",
            make_contains("Implementation evidence"),
        ),
        (
            "task_class_labels",
            "Cockpit task class labels (SSR shell)",
            make_all("BUGFIX", "ADVERSARIAL", "MULTI-AGENT", case_insensitive=False),
        ),
    ]


def fetch_page_html(url: str, *, timeout: float = DEFAULT_TIMEOUT) -> tuple[int, str]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ahe-smoke-hosted-demo/1"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        body = response.read().decode(charset, errors="replace")
        return response.status, body


def run_smoke_checks(html: str, *, url: str = "") -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for check_id, description, fn in _build_check_specs():
        passed, detail = fn(html)
        checks.append(
            {
                "id": check_id,
                "description": description,
                "passed": passed,
                "detail": detail,
            }
        )

    failed = [check for check in checks if not check["passed"]]
    return {
        "smoke_version": SMOKE_VERSION,
        "url": url,
        "ok": len(failed) == 0,
        "check_count": len(checks),
        "failed_count": len(failed),
        "checks": checks,
        "limitations": [LIMITATION_NOTE],
    }


def format_table(report: dict[str, Any]) -> str:
    lines = [
        "Hosted demo smoke",
        "=" * 72,
        f"url={report.get('url', '')}  ok={report['ok']}",
        "",
    ]
    for check in report["checks"]:
        status = "ok" if check["passed"] else "FAIL"
        lines.append(f"  [{status}] {check['id']}: {check['description']}")
        if not check["passed"] and check.get("detail"):
            lines.append(f"         {check['detail']}")

    lines.extend(["", "Limitations", "-" * 72])
    for note in report.get("limitations", []):
        lines.append(f"  {note}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Smoke-check hosted demo HTML at a URL (no browser)."
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help=f"Demo base URL (default: {DEFAULT_URL})",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"HTTP timeout seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--format",
        choices=("json", "table"),
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    url = args.url.rstrip("/") + "/"

    try:
        status, html = fetch_page_html(url, timeout=args.timeout)
    except urllib.error.HTTPError as exc:
        print(f"HTTP error: {exc.code} {exc.reason} for {url}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Request failed: {exc.reason} ({url})", file=sys.stderr)
        print("Hint: start the demo with `pnpm preview` or `pnpm dev` first.", file=sys.stderr)
        return 1

    if status != 200:
        print(f"Unexpected HTTP status {status} for {url}", file=sys.stderr)
        return 1

    report = run_smoke_checks(html, url=url)
    report["http_status"] = status

    if args.format == "json":
        indent = 2 if args.pretty else None
        print(json.dumps(report, indent=indent, separators=None if args.pretty else (",", ":")))
    else:
        print(format_table(report))

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
