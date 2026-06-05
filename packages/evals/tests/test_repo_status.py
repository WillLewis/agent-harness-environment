from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPO_STATUS = PROJECT_ROOT / "scripts" / "repo_status.py"


def _run_repo_status_json() -> dict:
    result = subprocess.run(
        [sys.executable, str(REPO_STATUS), "--format", "json"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_repo_status_ok_and_no_tracked_generated():
    report = _run_repo_status_json()
    assert report["repo_status_version"] == "1"
    assert report["ok"] is True
    assert report["tracked_generated_files"] == []


def test_repo_status_artifacts_are_gitignored():
    report = _run_repo_status_json()
    for item in report["artifacts"]:
        assert item["gitignored"] is True, item["path"]
