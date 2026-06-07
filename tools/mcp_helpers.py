from __future__ import annotations

import copy
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

TERMINAL_OUTPUT_MAX_CHARS = 500
CANDIDATE_TIMESTAMP_BASE = datetime(2026, 6, 5, 12, 0, 0, tzinfo=timezone.utc)


def ok(**payload: Any) -> dict[str, Any]:
    return {"ok": True, **payload}


def err(code: str, message: str, **payload: Any) -> dict[str, Any]:
    return {"ok": False, "code": code, "message": message, **payload}


def read_json(project_root: Path, relative_path: str) -> Any:
    return json.loads((project_root / relative_path).read_text(encoding="utf-8"))


def trace_search_dirs(project_root: Path) -> list[Path]:
    return [project_root / "data" / "traces", project_root / "runs"]


def find_trace(project_root: Path, run_id: str) -> tuple[dict[str, Any], Path] | None:
    for directory in trace_search_dirs(project_root):
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.json")):
            trace = json.loads(path.read_text(encoding="utf-8"))
            if trace.get("run_id") == run_id:
                return trace, path
    return None


def list_known_run_ids(project_root: Path) -> list[str]:
    run_ids: list[str] = []
    for directory in trace_search_dirs(project_root):
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.json")):
            trace = json.loads(path.read_text(encoding="utf-8"))
            run_id = trace.get("run_id")
            if isinstance(run_id, str):
                run_ids.append(run_id)
    return sorted(set(run_ids))


def summarize_event(event: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "step_id": event.get("step_id"),
        "actor": event.get("actor"),
        "action_type": event.get("action_type"),
        "output_summary": event.get("output_summary"),
    }
    if event.get("failure_label"):
        summary["failure_label"] = event["failure_label"]
    if event.get("command"):
        summary["command"] = event["command"]
    if event.get("exit_code") is not None:
        summary["exit_code"] = event["exit_code"]
    if event.get("files_touched"):
        summary["files_touched"] = event["files_touched"]
    return summary


def summarize_trace(trace: dict[str, Any], trace_path: str) -> dict[str, Any]:
    events = trace.get("events", [])
    summaries = [summarize_event(event) for event in events]
    failure_labels = sorted(
        {
            label
            for event in events
            for label in [event.get("failure_label")]
            if isinstance(label, str) and label
        }
    )

    return {
        "run_id": trace.get("run_id"),
        "task_id": trace.get("task_id"),
        "task_title": trace.get("task_title"),
        "policy": trace.get("policy"),
        "verdict": trace.get("verdict"),
        "success_command": trace.get("success_command"),
        "known_files": trace.get("known_files", []),
        "trace_path": trace_path,
        "event_count": len(summaries),
        "failure_labels": failure_labels,
        "events": summaries,
    }


def list_eval_runs(project_root: Path) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    for directory in trace_search_dirs(project_root):
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.json")):
            trace = json.loads(path.read_text(encoding="utf-8"))
            runs.append(
                {
                    "run_id": trace.get("run_id"),
                    "task_id": trace.get("task_id"),
                    "policy": trace.get("policy"),
                    "verdict": trace.get("verdict"),
                    "path": str(path.relative_to(project_root)),
                }
            )
    return ok(runs=runs, count=len(runs))


def get_trace(project_root: Path, run_id: str, verbose: bool = False) -> dict[str, Any]:
    found = find_trace(project_root, run_id)
    if found is None:
        return err(
            "trace_not_found",
            f"run_id not found: {run_id}",
            run_id=run_id,
            available_run_ids=list_known_run_ids(project_root),
        )

    trace, path = found
    relative_path = str(path.relative_to(project_root))
    if verbose:
        return ok(trace=trace, trace_path=relative_path, verbose=True)

    return ok(summary=summarize_trace(trace, relative_path), verbose=False)


def compare_policies(project_root: Path, policy_a: str, policy_b: str) -> dict[str, Any]:
    rows = read_json(project_root, "data/evals/policy_comparison.json")
    by_policy = {row["policy"]: row for row in rows}
    available_policies = sorted(by_policy)

    missing = [policy for policy in (policy_a, policy_b) if policy not in by_policy]
    if missing:
        return err(
            "policy_not_found",
            f"Policy not found: {', '.join(missing)}",
            missing_policies=missing,
            available_policies=available_policies,
        )

    return ok(
        policy_a=policy_a,
        policy_b=policy_b,
        comparison={
            "policy_a": by_policy[policy_a],
            "policy_b": by_policy[policy_b],
        },
    )


def run_eval_trace(project_root: Path, trace_path: str, run_eval_impl) -> dict[str, Any]:
    absolute = project_root / trace_path
    if not absolute.exists():
        return err(
            "trace_path_not_found",
            f"Trace path not found: {trace_path}",
            trace_path=trace_path,
        )
    result = run_eval_impl(absolute)
    return ok(eval=result)


def list_failure_cluster_keys(clusters: list[dict[str, Any]]) -> list[str]:
    keys: list[str] = []
    for cluster in clusters:
        keys.append(cluster["id"])
        keys.append(cluster["label"])
    return sorted(set(keys))


def create_failure_cluster(project_root: Path, label: str) -> dict[str, Any]:
    clusters = read_json(project_root, "data/failure_clusters.json")
    normalized = label.lower()
    for cluster in clusters:
        if normalized in {cluster["id"].lower(), cluster["label"].lower()}:
            return ok(cluster=cluster)

    return err(
        "cluster_not_found",
        f"No failure cluster found for {label!r}",
        query=label,
        available_clusters=list_failure_cluster_keys(clusters),
    )


def primary_failure_label(trace: dict[str, Any]) -> str:
    labels = [event.get("failure_label") for event in trace.get("events", []) if event.get("failure_label")]
    if labels:
        return str(labels[-1])
    return "needs_review"


def recommended_policy_behavior(trace: dict[str, Any], clusters: list[dict[str, Any]]) -> str | None:
    failure_mode = primary_failure_label(trace)
    for cluster in clusters:
        candidate = cluster.get("datasetCandidate") or {}
        if candidate.get("failure_mode") == failure_mode:
            behavior = candidate.get("expected_policy_behavior")
            if isinstance(behavior, str):
                return behavior

    task_id = trace.get("task_id")
    for cluster in clusters:
        if task_id in cluster.get("affectedTasks", []):
            candidate = cluster.get("datasetCandidate") or {}
            behavior = candidate.get("expected_policy_behavior")
            if isinstance(behavior, str):
                return behavior
    return None


def compact_eval_summary(eval_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "verdict": eval_result.get("verdict"),
        "policy": eval_result.get("policy"),
        "aggregate_run_quality": eval_result.get("aggregate_run_quality"),
        "scores": [
            {
                "name": score.get("name"),
                "score": score.get("score"),
                "passed": score.get("passed"),
            }
            for score in eval_result.get("scores", [])
        ],
    }


def extract_failure_labels(trace: dict[str, Any]) -> list[str]:
    labels = {
        label
        for event in trace.get("events", [])
        for label in [event.get("failure_label")]
        if isinstance(label, str) and label
    }
    return sorted(labels)


def _truncate_terminal_output(text: str, limit: int = TERMINAL_OUTPUT_MAX_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 20].rstrip() + "\n...[truncated]"


def normalize_trace_for_candidate(trace: dict[str, Any], project_root: Path) -> dict[str, Any]:
    """Strip transient runner fields and compact raw payloads for fixture review."""
    normalized = copy.deepcopy(trace)
    normalized.pop("sandbox_path", None)

    root = str(project_root.resolve())
    events = normalized.get("events", [])
    for index, event in enumerate(events):
        event["timestamp"] = (CANDIDATE_TIMESTAMP_BASE + timedelta(seconds=6 * index)).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
        raw = event.get("raw")
        if not isinstance(raw, dict):
            continue
        for key, value in list(raw.items()):
            if not isinstance(value, str):
                continue
            # Scrub absolute project-root paths so curated fixtures never leak local
            # machine paths (e.g. inside captured terminal output or stack traces).
            value = value.replace(root + "/", "").replace(root, ".")
            raw[key] = value
        if "terminal_output" in raw and isinstance(raw["terminal_output"], str):
            raw["terminal_output"] = _truncate_terminal_output(raw["terminal_output"])

    return normalized


def write_dataset_candidates(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "".join(json.dumps(row) + "\n" for row in rows)
    path.write_text(content, encoding="utf-8")


def read_dataset_candidates(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def build_promotion_metadata(
    *,
    trace: dict[str, Any],
    source_path: str,
    candidate_trace_path: str,
    run_id: str,
    eval_result: dict[str, Any],
    clusters: list[dict[str, Any]],
) -> dict[str, Any]:
    failure_mode = primary_failure_label(trace)
    expected_behavior = recommended_policy_behavior(trace, clusters) or "derive from failure cluster review"
    return {
        "promoted_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_run_id": run_id,
        "source_path": source_path,
        "candidate_trace_path": candidate_trace_path,
        "task_id": trace.get("task_id"),
        "policy": trace.get("policy"),
        "verdict": trace.get("verdict"),
        "aggregate_run_quality": eval_result.get("aggregate_run_quality"),
        "failure_labels": extract_failure_labels(trace),
        "failure_mode": failure_mode,
        "expected_policy_behavior": expected_behavior,
        "success_command": trace.get("success_command"),
        "eval_summary": compact_eval_summary(eval_result),
    }


def build_dataset_candidate(
    *,
    trace: dict[str, Any],
    trace_path: str,
    run_id: str,
    clusters: list[dict[str, Any]],
    eval_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    """Legacy dataset-row shape; prefer build_promotion_metadata for new promotions."""
    failure_mode = primary_failure_label(trace)
    expected_behavior = recommended_policy_behavior(trace, clusters) or "derive from failure cluster review"
    candidate: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_run_id": run_id,
        "source_trace_path": trace_path,
        "task_id": f"{trace.get('task_id')}_promoted",
        "failure_mode": failure_mode,
        "expected_policy_behavior": expected_behavior,
        "success_command": trace.get("success_command"),
    }
    if eval_summary is not None:
        candidate["eval_summary"] = eval_summary
    return candidate


def promote_run_trace(
    project_root: Path,
    trace_path: str,
    run_eval_impl: Callable[[Path], dict[str, Any]],
    *,
    candidate_dir: str = "data/trace_candidates",
    datasets_path: str = "data/datasets/generated_candidates.jsonl",
    write_fixture: bool = False,
    fixture_name: str | None = None,
    validate_trace_impl: Callable[[dict[str, Any], str], list[str]] | None = None,
) -> dict[str, Any]:
    """
    Validate and score a runner trace, write a reviewable candidate JSON, and append metadata.

    Idempotent by source_run_id: re-promotion refreshes the candidate file but does not
    duplicate generated_candidates.jsonl rows. Curated fixtures are untouched unless
    write_fixture=True with an explicit fixture_name.
    """
    if write_fixture and not fixture_name:
        return err(
            "fixture_name_required",
            "--fixture-name is required when --write-fixture is set.",
        )

    absolute = (project_root / trace_path).resolve()
    if not absolute.exists():
        return err(
            "trace_path_not_found",
            f"Trace path not found: {trace_path}",
            trace_path=trace_path,
        )

    try:
        relative_source = str(absolute.relative_to(project_root.resolve()))
    except ValueError:
        relative_source = trace_path

    trace = json.loads(absolute.read_text(encoding="utf-8"))
    run_id = trace.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        return err("invalid_trace", "Trace is missing run_id.", trace_path=relative_source)

    if validate_trace_impl is not None:
        validation_errors = validate_trace_impl(trace, relative_source)
        if validation_errors:
            return err(
                "trace_validation_failed",
                "Trace failed fixture validation.",
                trace_path=relative_source,
                validation_errors=validation_errors,
            )

    eval_result = run_eval_impl(absolute)

    candidate_dir_path = project_root / candidate_dir
    candidate_dir_path.mkdir(parents=True, exist_ok=True)
    candidate_filename = f"{run_id}.json"
    candidate_absolute = candidate_dir_path / candidate_filename
    relative_candidate = str(candidate_absolute.relative_to(project_root))

    normalized = normalize_trace_for_candidate(trace, project_root)
    candidate_absolute.write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")

    datasets_file = project_root / datasets_path
    existing_rows = read_dataset_candidates(datasets_file)
    existing = next((row for row in existing_rows if row.get("source_run_id") == run_id), None)

    clusters = read_json(project_root, "data/failure_clusters.json")
    metadata = build_promotion_metadata(
        trace=trace,
        source_path=relative_source,
        candidate_trace_path=relative_candidate,
        run_id=run_id,
        eval_result=eval_result,
        clusters=clusters,
    )

    metadata_written = False
    if existing is None:
        write_dataset_candidates(datasets_file, [*existing_rows, metadata])
        metadata_written = True

    fixture_written = False
    relative_fixture: str | None = None
    if write_fixture and fixture_name:
        fixtures_dir = project_root / "data" / "traces"
        fixture_absolute = fixtures_dir / fixture_name
        if fixture_absolute.exists():
            return err(
                "fixture_exists",
                f"Refusing to overwrite existing curated fixture: {fixture_name}",
                fixture_path=str(fixture_absolute.relative_to(project_root)),
            )
        fixture_absolute.write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")
        fixture_written = True
        relative_fixture = str(fixture_absolute.relative_to(project_root))

    return ok(
        source_run_id=run_id,
        source_path=relative_source,
        candidate_trace_path=relative_candidate,
        metadata_path=str(datasets_file.relative_to(project_root)),
        metadata=existing or metadata,
        metadata_written=metadata_written,
        already_exists=existing is not None,
        candidate_refreshed=True,
        fixture_written=fixture_written,
        fixture_path=relative_fixture,
        eval=eval_result,
    )


def promote_trace_to_dataset(
    project_root: Path,
    run_id: str,
    run_eval_impl: Callable[[Path], dict[str, Any]],
) -> dict[str, Any]:
    found = find_trace(project_root, run_id)
    if found is None:
        return err(
            "trace_not_found",
            f"run_id not found: {run_id}",
            run_id=run_id,
            available_run_ids=list_known_run_ids(project_root),
        )

    _trace, path = found
    trace_path = str(path.relative_to(project_root))
    result = promote_run_trace(project_root, trace_path, run_eval_impl)
    if not result.get("ok"):
        return result

    return ok(
        written=result.get("metadata_written", False),
        already_exists=result.get("already_exists", False),
        written_to=result.get("metadata_path"),
        candidate_trace_path=result.get("candidate_trace_path"),
        candidate=result.get("metadata"),
    )


def get_policy_router_decision(project_root: Path, task_id: str) -> dict[str, Any]:
    decisions = read_json(project_root, "data/router_decisions.json")
    if task_id not in decisions:
        return err(
            "router_decision_not_found",
            f"No router decision found for task_id: {task_id}",
            task_id=task_id,
            available_task_ids=sorted(decisions),
        )
    return ok(task_id=task_id, decision=decisions[task_id])
