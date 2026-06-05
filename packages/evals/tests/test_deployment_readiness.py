from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CHECK_SCRIPT = PROJECT_ROOT / "scripts" / "check_deployment_readiness.py"


def test_deployment_readiness_passes():
    result = subprocess.run(
        [sys.executable, str(CHECK_SCRIPT), "--format", "json"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    report = json.loads(result.stdout)
    assert report["ok"] is True
    assert report["environment_variables_required"] == []
    assert report["recommended_host"] == "vercel"


def test_deployment_doc_exists():
    doc = PROJECT_ROOT / "docs" / "DEPLOYMENT.md"
    assert doc.exists()
    text = doc.read_text(encoding="utf-8")
    assert "pnpm build" in text
    assert "Vercel" in text
