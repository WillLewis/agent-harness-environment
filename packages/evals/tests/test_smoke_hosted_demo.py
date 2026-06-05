from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SMOKE_SCRIPT = PROJECT_ROOT / "scripts" / "smoke_hosted_demo.py"
FIXTURE_OK = Path(__file__).resolve().parent / "fixtures" / "hosted_demo_smoke_ok.html"
FIXTURE_BAD = """<!DOCTYPE html><html><head><title>Wrong</title></head><body><p>empty</p></body></html>"""


@pytest.fixture
def smoke_module():
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    import smoke_hosted_demo  # noqa: E402

    return smoke_hosted_demo


def test_run_smoke_checks_passes_fixture_html(smoke_module):
    html = FIXTURE_OK.read_text(encoding="utf-8")
    report = smoke_module.run_smoke_checks(html, url="http://fixture.test/")
    assert report["ok"] is True
    assert report["failed_count"] == 0
    assert report["check_count"] >= 10


def test_run_smoke_checks_fails_missing_sections(smoke_module):
    report = smoke_module.run_smoke_checks(FIXTURE_BAD, url="http://fixture.test/")
    assert report["ok"] is False
    assert report["failed_count"] > 0
    failed_ids = {check["id"] for check in report["checks"] if not check["passed"]}
    assert "anchor_cockpit" in failed_ids
    assert "static_demo_copy" in failed_ids


def test_cli_returns_zero_on_valid_html(smoke_module):
    html = FIXTURE_OK.read_text(encoding="utf-8")
    with patch.object(smoke_module, "fetch_page_html", return_value=(200, html)):
        with patch.object(sys, "argv", ["smoke_hosted_demo.py", "--format", "json"]):
            assert smoke_module.main() == 0


def test_cli_returns_nonzero_on_invalid_html(smoke_module):
    with patch.object(smoke_module, "fetch_page_html", return_value=(200, FIXTURE_BAD)):
        with patch.object(sys, "argv", ["smoke_hosted_demo.py", "--format", "json"]):
            assert smoke_module.main() == 1


def test_smoke_script_exists():
    assert SMOKE_SCRIPT.exists()
