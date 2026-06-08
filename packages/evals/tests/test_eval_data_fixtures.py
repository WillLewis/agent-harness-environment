"""Structural + invariant guards for the exported reliability / capability fixtures.

These power the hosted Reliability panel and Capability chart (apps/web). They are
generated offline by pass_k.py / capability_sweep.py; this test pins the shape the
UI relies on and the one structural ordering that must always hold.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
TASK_IDS = {"bugfix_date_parser_001", "adversarial_env_001", "multi_agent_contract_001"}
POLICIES = {"baseline", "test_first", "context_first", "guarded_recovery"}
REAL_RELIABILITY = "data/evals/reliability_real.json"


def _load(rel_path: str) -> dict:
    return json.loads((ROOT / rel_path).read_text(encoding="utf-8"))


def _load_real_or_skip() -> dict:
    """The real-model fixture is a NONDETERMINISTIC offline export (never generated in
    CI). When it has been committed, pin its shape + the structural invariant; when it
    is absent (fresh checkout before a real export), skip — we never call the API here."""
    path = ROOT / REAL_RELIABILITY
    if not path.exists():
        pytest.skip(f"{REAL_RELIABILITY} not present (offline real export not committed)")
    return json.loads(path.read_text(encoding="utf-8"))


def test_reliability_fixture_covers_all_three_tasks():
    data = _load("data/evals/reliability.json")
    assert {task["task_id"] for task in data["tasks"]} == TASK_IDS
    for task in data["tasks"]:
        assert {row["policy"] for row in task["policies"]} == POLICIES
        for key in ("label", "visibleLabel", "heldOutLabel", "metric_note", "capability"):
            assert task.get(key) not in (None, ""), f"{task['task_id']} missing {key}"


def test_reliability_held_out_never_exceeds_visible():
    """A run cannot be accepted without passing the visible check, so for every
    (task, policy) cell held-out pass@1 <= visible pass@1. This is the measured
    'naive metric is optimistic' invariant — it must emerge, never be tuned."""
    data = _load("data/evals/reliability.json")
    for task in data["tasks"]:
        for row in task["policies"]:
            assert row["heldOut"]["pass1"] <= row["visible"]["pass1"] + 1e-9, (
                f"{task['task_id']}/{row['policy']}: heldOut {row['heldOut']['pass1']} "
                f"> visible {row['visible']['pass1']}"
            )
            # Per-seed vectors line up with the reported sample size.
            assert len(row["seedResults"]["visible"]) == data["n"]
            assert len(row["seedResults"]["heldOut"]) == data["n"]


def test_reliability_guarded_beats_baseline_on_held_out():
    """The hero ordering: the guarded harness is at least as reliable as baseline on
    the true (held-out) metric for every task."""
    data = _load("data/evals/reliability.json")
    for task in data["tasks"]:
        by_policy = {row["policy"]: row for row in task["policies"]}
        guarded = by_policy["guarded_recovery"]["heldOut"]["pass1"]
        baseline = by_policy["baseline"]["heldOut"]["pass1"]
        assert guarded >= baseline, f"{task['task_id']}: guarded {guarded} < baseline {baseline}"


def test_capability_fixture_covers_all_three_tasks():
    data = _load("data/evals/capability_curves.json")
    assert {task["task_id"] for task in data["tasks"]} == TASK_IDS
    n_caps = len(data["capabilities"])
    for task in data["tasks"]:
        assert len(task["curves"]) == n_caps
        assert task["series"], f"{task['task_id']} has no chart series"
        assert len(task["yDomain"]) == 2
        for row in task["curves"]:
            for series in task["series"]:
                assert series["key"] in row, f"{task['task_id']} curve missing {series['key']}"


# --- Real-model overlay fixture (offline export; skipped when absent) --------------


def test_real_reliability_fixture_shape_when_present():
    """Pin the real-model fixture's shape so the UI overlay can rely on it: it must be
    clearly labelled (engine=real, model, n) and cover the same tasks/policies as the
    seeded fixture, so the two can be shown side by side without silent merging."""
    data = _load_real_or_skip()
    assert data.get("engine") == "real", "real fixture must declare engine=real"
    assert data.get("model"), "real fixture must record the model id"
    assert isinstance(data.get("n"), int) and data["n"] >= 1
    assert {task["task_id"] for task in data["tasks"]} == TASK_IDS
    for task in data["tasks"]:
        assert {row["policy"] for row in task["policies"]} == POLICIES
        for row in task["policies"]:
            assert len(row["seedResults"]["visible"]) == data["n"]
            assert len(row["seedResults"]["heldOut"]) == data["n"]


def test_real_reliability_held_out_never_exceeds_visible():
    """The same structural invariant the seeded fixture must satisfy, now on the REAL
    model: a run cannot be accepted (held-out) without first passing the visible check,
    so held-out pass@1 <= visible pass@1 for every (task, policy). This must hold by
    construction for the real runner too — it is the 'naive metric is optimistic' claim
    measured from a real model, not a tuned magnitude."""
    data = _load_real_or_skip()
    for task in data["tasks"]:
        for row in task["policies"]:
            assert row["heldOut"]["pass1"] <= row["visible"]["pass1"] + 1e-9, (
                f"{task['task_id']}/{row['policy']}: heldOut {row['heldOut']['pass1']} "
                f"> visible {row['visible']['pass1']}"
            )
