from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

RUNNER_DIR = Path(__file__).resolve().parents[1]
if str(RUNNER_DIR) not in sys.path:
    sys.path.insert(0, str(RUNNER_DIR))

from run_batch import run_batch, scorer_signals  # noqa: E402
from task_runner import SUPPORTED_POLICIES, TASK_CONFIGS, list_batch_combinations  # noqa: E402


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def test_list_batch_combinations_covers_runner_registry():
    combos = list_batch_combinations()

    assert len(combos) == len(TASK_CONFIGS) * len(SUPPORTED_POLICIES)
    assert ("bugfix_date_parser_001", "baseline") in combos
    assert ("adversarial_env_001", "guarded_recovery") in combos
    assert ("multi_agent_contract_001", "baseline") in combos


def test_scorer_signals_shape():
    signals = scorer_signals(
        {
            "scores": [
                {"name": "tests_passed", "passed": True},
                {"name": "unsafe_tool_use", "passed": False},
            ]
        }
    )
    assert signals["passed"] == ["tests_passed"]
    assert signals["failed"] == ["unsafe_tool_use"]


def test_run_batch_summary_shape_and_verdict_mix(project_root: Path, tmp_path: Path):
    root = tmp_path
    _seed_batch_project(root, project_root)

    summary = run_batch(root, promote_candidates=False)

    assert summary["ok"] is True
    assert summary["batch_version"] == "1"
    assert summary["run_count"] == 6
    assert summary["accepted_count"] >= 1
    assert summary["rejected_count"] >= 1
    assert summary["accepted_count"] + summary["rejected_count"] == 6
    assert summary["error_count"] == 0

    required = {
        "run_id",
        "task_id",
        "policy",
        "verdict",
        "trace_path",
        "aggregate_run_quality",
        "scorer_signals",
    }
    for row in summary["runs"]:
        assert row["ok"] is True
        assert required.issubset(row)
        assert "passed" in row["scorer_signals"]
        assert "failed" in row["scorer_signals"]


def test_run_batch_promote_calls_shared_promotion_logic(project_root: Path, tmp_path: Path):
    root = tmp_path
    _seed_batch_project(root, project_root)
    promoted: list[str] = []

    def fake_promote(_root: Path, trace_path: str, _eval_impl, **kwargs: object) -> dict:
        promoted.append(trace_path)
        return {
            "ok": True,
            "candidate_trace_path": f"data/trace_candidates/{Path(trace_path).stem}.json",
            "already_exists": len(promoted) > 3,
            "metadata_written": len(promoted) <= 3,
            "candidate_refreshed": True,
        }

    summary = run_batch(root, promote_candidates=True, promote_impl=fake_promote)

    assert summary["promote_candidates"] is True
    assert len(promoted) == 6
    for row in summary["runs"]:
        assert row.get("candidate_trace_path")
        assert row["promotion"]["candidate_refreshed"] is True


def test_run_batch_does_not_mutate_toy_repos(project_root: Path, tmp_path: Path):
    root = tmp_path
    _seed_batch_project(root, project_root)

    before = {
        toy: _toy_tree_digest(project_root / "toy_repos" / toy)
        for toy in ("date_utils", "docs_site", "issue_tracker")
    }

    run_batch(root, promote_candidates=False)

    after = {
        toy: _toy_tree_digest(project_root / "toy_repos" / toy)
        for toy in ("date_utils", "docs_site", "issue_tracker")
    }
    assert before == after


def _toy_tree_digest(directory: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(directory.rglob("*")):
        if path.is_file():
            digest.update(str(path.relative_to(directory)).encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.hexdigest()


def _seed_batch_project(root: Path, project_root: Path) -> None:
    for toy_name in ("date_utils", "docs_site", "issue_tracker"):
        toy_src = project_root / "toy_repos" / toy_name
        toy_dest = root / "toy_repos" / toy_name
        toy_dest.parent.mkdir(parents=True, exist_ok=True)
        if toy_dest.exists():
            shutil.rmtree(toy_dest)
        shutil.copytree(toy_src, toy_dest)

    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "tasks.json").write_text(
        (project_root / "data" / "tasks.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    shutil.copy(
        project_root / "data" / "failure_clusters.json",
        data_dir / "failure_clusters.json",
    )
