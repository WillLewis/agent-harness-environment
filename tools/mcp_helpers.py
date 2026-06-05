from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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


def read_dataset_candidates(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def build_dataset_candidate(
    *,
    trace: dict[str, Any],
    trace_path: str,
    run_id: str,
    clusters: list[dict[str, Any]],
    eval_summary: dict[str, Any] | None,
) -> dict[str, Any]:
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


def promote_trace_to_dataset(
    project_root: Path,
    run_id: str,
    run_eval_impl,
) -> dict[str, Any]:
    found = find_trace(project_root, run_id)
    if found is None:
        return err(
            "trace_not_found",
            f"run_id not found: {run_id}",
            run_id=run_id,
            available_run_ids=list_known_run_ids(project_root),
        )

    trace, path = found
    trace_path = str(path.relative_to(project_root))
    output = project_root / "data" / "datasets" / "generated_candidates.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)

    existing_rows = read_dataset_candidates(output)
    for row in existing_rows:
        if row.get("source_run_id") == run_id:
            return ok(
                written=False,
                already_exists=True,
                written_to=str(output.relative_to(project_root)),
                candidate=row,
            )

    clusters = read_json(project_root, "data/failure_clusters.json")
    eval_summary = None
    try:
        eval_summary = compact_eval_summary(run_eval_impl(path))
    except Exception:
        eval_summary = None

    candidate = build_dataset_candidate(
        trace=trace,
        trace_path=trace_path,
        run_id=run_id,
        clusters=clusters,
        eval_summary=eval_summary,
    )

    with output.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(candidate) + "\n")

    return ok(
        written=True,
        already_exists=False,
        written_to=str(output.relative_to(project_root)),
        candidate=candidate,
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
