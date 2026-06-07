#!/usr/bin/env python3
"""Optional observability for the local runner/eval pipeline (Phase 13b).

Emits one structured record per task/policy run to Braintrust and/or Weights &
Biases, then exports a small, safe metadata/link JSON
(`data/evals/observability_links.json`) that the static hosted webapp can read.

Boundaries (hard):
- Default mode is ``off``. Nothing here is required for tests, builds, the
  hosted demo, trace replay, or CI.
- Vendor SDKs are optional imports. A missing SDK fails softly with a warning
  unless observability is explicitly required.
- No live vendor calls, API keys, or SDK imports belong in ``apps/web``. This
  module only ever produces sanitized JSON evidence for the webapp to display.
- Exported artifacts never contain absolute local paths, secrets, env values,
  or machine-specific data.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

EVAL_DIR = Path(__file__).resolve().parent
if str(EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(EVAL_DIR))

from run_eval import run_eval  # noqa: E402
from run_suite import discover_traces  # noqa: E402

OBSERVABILITY_VERSION = "1"
DEFAULT_PROJECT = "agent-harness-environment"
LINKS_RELATIVE_PATH = "data/evals/observability_links.json"

MODE_OFF = "off"
MODE_BRAINTRUST = "braintrust"
MODE_WANDB = "wandb"
MODE_BOTH = "both"
VALID_MODES = (MODE_OFF, MODE_BRAINTRUST, MODE_WANDB, MODE_BOTH)

VALID_WANDB_MODES = ("online", "offline", "disabled")

# Env var names that may hold secrets; their values are redacted from any
# string before it is written to an exported artifact.
SECRET_ENV_KEYS = (
    "BRAINTRUST_API_KEY",
    "WANDB_API_KEY",
    "OPENAI_API_KEY",
)

# Absolute home/system paths that must never leak into committed artifacts.
_ABS_PATH_RE = re.compile(r"(?:/Users|/home|/private|/root|/var/folders)/[^\s\"']+")

# Policy labels for fixtures whose policy id is not in data/policies.json.
_EXTRA_POLICY_LABELS = {
    "baseline_with_steering": "Baseline with steering",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ObservabilityConfig:
    """Env-gated observability configuration (defaults fully off)."""

    mode: str
    braintrust_project: str
    braintrust_api_key_present: bool
    braintrust_package_installed: bool
    wandb_project: str
    wandb_entity: str
    wandb_mode: str
    wandb_api_key_present: bool
    wandb_package_installed: bool

    @property
    def braintrust_requested(self) -> bool:
        return self.mode in (MODE_BRAINTRUST, MODE_BOTH)

    @property
    def wandb_requested(self) -> bool:
        return self.mode in (MODE_WANDB, MODE_BOTH)

    @property
    def braintrust_ready(self) -> bool:
        return self.braintrust_requested and self.braintrust_package_installed and self.braintrust_api_key_present

    @property
    def wandb_ready(self) -> bool:
        # WANDB_MODE=offline/disabled does not require an API key.
        key_ok = self.wandb_api_key_present or self.wandb_mode in ("offline", "disabled")
        return self.wandb_requested and self.wandb_package_installed and key_ok

    def to_public_dict(self) -> dict[str, Any]:
        """Config view safe to print/export (never includes key values)."""
        return {
            "mode": self.mode,
            "braintrust": {
                "requested": self.braintrust_requested,
                "project": self.braintrust_project,
                "api_key_present": self.braintrust_api_key_present,
                "package_installed": self.braintrust_package_installed,
                "ready": self.braintrust_ready,
            },
            "wandb": {
                "requested": self.wandb_requested,
                "project": self.wandb_project,
                "entity": self.wandb_entity,
                "wandb_mode": self.wandb_mode,
                "api_key_present": self.wandb_api_key_present,
                "package_installed": self.wandb_package_installed,
                "ready": self.wandb_ready,
            },
        }


def parse_mode(value: str | None) -> str:
    raw = (value or "").strip().lower()
    if raw in VALID_MODES:
        return raw
    if raw in ("", "0", "false", "none", "no", "disabled"):
        return MODE_OFF
    # Unknown value: stay safe and off rather than guessing a vendor.
    return MODE_OFF


def parse_wandb_mode(value: str | None) -> str:
    raw = (value or "").strip().lower()
    return raw if raw in VALID_WANDB_MODES else "online"


def _package_installed(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def load_config(env: dict[str, str] | None = None) -> ObservabilityConfig:
    env = env if env is not None else dict(os.environ)
    return ObservabilityConfig(
        mode=parse_mode(env.get("AHE_OBSERVABILITY")),
        braintrust_project=(env.get("BRAINTRUST_PROJECT") or DEFAULT_PROJECT).strip() or DEFAULT_PROJECT,
        braintrust_api_key_present=bool((env.get("BRAINTRUST_API_KEY") or "").strip()),
        braintrust_package_installed=_package_installed("braintrust"),
        wandb_project=(env.get("WANDB_PROJECT") or DEFAULT_PROJECT).strip() or DEFAULT_PROJECT,
        wandb_entity=(env.get("WANDB_ENTITY") or "").strip(),
        wandb_mode=parse_wandb_mode(env.get("WANDB_MODE")),
        wandb_api_key_present=bool((env.get("WANDB_API_KEY") or "").strip()),
        wandb_package_installed=_package_installed("wandb"),
    )


# --------------------------------------------------------------------------- #
# Sanitization
# --------------------------------------------------------------------------- #


def scrub_text(
    text: Any,
    *,
    project_root: Path | None = None,
    env: dict[str, str] | None = None,
) -> Any:
    """Strip project-root paths, absolute home/system paths, and secret values."""
    if not isinstance(text, str):
        return text
    result = text
    if project_root is not None:
        root = str(project_root.resolve())
        result = result.replace(root + os.sep, "").replace(root, ".")

    env = env if env is not None else dict(os.environ)
    for key in SECRET_ENV_KEYS:
        value = (env.get(key) or "").strip()
        if value and len(value) >= 4 and value in result:
            result = result.replace(value, "***redacted***")

    result = _ABS_PATH_RE.sub("<path>", result)
    return result


def sanitize(value: Any, *, project_root: Path | None = None, env: dict[str, str] | None = None) -> Any:
    """Recursively scrub strings inside dicts/lists for safe export."""
    if isinstance(value, dict):
        return {k: sanitize(v, project_root=project_root, env=env) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize(v, project_root=project_root, env=env) for v in value]
    if isinstance(value, str):
        return scrub_text(value, project_root=project_root, env=env)
    return value


# --------------------------------------------------------------------------- #
# Record building (one record per task/policy run)
# --------------------------------------------------------------------------- #


def _score_value(eval_result: dict[str, Any], name: str, default: float = 0.0) -> float:
    for score in eval_result.get("scores", []):
        if score.get("name") == name:
            return float(score.get("score", default))
    return default


def _failure_labels(trace: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    for event in trace.get("events", []):
        label = event.get("failure_label")
        if label and label not in labels:
            labels.append(label)
    return labels


def _policy_label(policy_id: str, policy_meta: dict[str, dict[str, Any]]) -> str:
    meta = policy_meta.get(policy_id)
    if meta and meta.get("name"):
        return str(meta["name"])
    if policy_id in _EXTRA_POLICY_LABELS:
        return _EXTRA_POLICY_LABELS[policy_id]
    return policy_id.replace("_", " ")


def build_run_record(
    task: dict[str, Any],
    trace: dict[str, Any],
    eval_result: dict[str, Any],
    *,
    policy_meta: dict[str, dict[str, Any]] | None = None,
    router_decision: dict[str, Any] | None = None,
    trace_rel_path: str | None = None,
    project_root: Path | None = None,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a single sanitized observability record for a task/policy run."""
    policy_meta = policy_meta or {}
    events = trace.get("events", [])
    policy_id = str(trace.get("policy") or "unknown")
    task_id = str(trace.get("task_id") or task.get("id") or "unknown")

    scorers = {score["name"]: bool(score.get("passed")) for score in eval_result.get("scores", [])}
    passed = sorted(name for name, ok in scorers.items() if ok)
    failed = sorted(name for name, ok in scorers.items() if not ok)

    interventions = sum(
        1 for e in events if e.get("actor") == "human" or e.get("action_type") == "ASK_USER"
    )
    tool_calls = sum(1 for e in events if e.get("action_type") not in ("PLAN", "FINAL"))
    final_event = next((e for e in reversed(events) if e.get("action_type") == "FINAL"), None)
    judge_summary = (final_event or {}).get("output_summary") if final_event else None

    record: dict[str, Any] = {
        "run_identity": f"{task_id}::{policy_id}",
        "task_id": task_id,
        "task_title": trace.get("task_title") or task.get("title"),
        "task_type": task.get("type"),
        "repo": trace.get("repo_snapshot") or task.get("repo"),
        "policy_id": policy_id,
        "policy_label": _policy_label(policy_id, policy_meta),
        "tags": task.get("tags", []),
        "failure_modes": task.get("failureModes", []),
        "expected_files": task.get("expectedFiles", trace.get("expected_files", [])),
        "known_files": trace.get("known_files", []),
        "trace_path": trace_rel_path,
        "run_id": trace.get("run_id"),
        "verdict": trace.get("verdict"),
        "metrics": {
            "task_success": _score_value(eval_result, "tests_passed"),
            "loop_rate": round(_score_value(eval_result, "loop_score"), 4),
            "interventions": interventions,
            "tool_calls": tool_calls,
            "event_count": len(events),
        },
        "aggregate_run_quality": eval_result.get("aggregate_run_quality"),
        "scorers": scorers,
        "scorer_labels": {"passed": passed, "failed": failed},
        "failure_labels": _failure_labels(trace),
        "judge_summary": judge_summary,
        "started_at": events[0].get("timestamp") if events else None,
        "ended_at": events[-1].get("timestamp") if events else None,
        "evidence_summary": {
            "event_count": len(events),
            "tool_calls": tool_calls,
            "final_summary": judge_summary,
        },
    }

    if router_decision is not None:
        record["router"] = {
            "selected_policy": router_decision.get("selectedPolicy"),
            "why": router_decision.get("why"),
            "is_router_selection": router_decision.get("selectedPolicy") == policy_id,
        }

    return sanitize(record, project_root=project_root, env=env)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_records(project_root: Path, *, env: dict[str, str] | None = None) -> list[dict[str, Any]]:
    """Build sanitized records for every curated trace fixture (deterministic)."""
    traces_dir = project_root / "data" / "traces"
    tasks = {row["id"]: row for row in _load_json(project_root / "data" / "tasks.json")}
    policy_meta = {row["id"]: row for row in _load_json(project_root / "data" / "policies.json")}

    router_path = project_root / "data" / "router_decisions.json"
    router = _load_json(router_path) if router_path.exists() else {}

    records: list[dict[str, Any]] = []
    for path in discover_traces(traces_dir):
        trace = _load_json(path)
        eval_result = run_eval(path)
        task_id = trace.get("task_id")
        records.append(
            build_run_record(
                tasks.get(task_id, {}),
                trace,
                eval_result,
                policy_meta=policy_meta,
                router_decision=router.get(task_id),
                trace_rel_path=str(path.relative_to(project_root)),
                project_root=project_root,
                env=env,
            )
        )
    return records


# --------------------------------------------------------------------------- #
# Adapters
# --------------------------------------------------------------------------- #


def empty_link(mode: str) -> dict[str, Any]:
    return {
        "braintrust_url": None,
        "braintrust_experiment_id": None,
        "wandb_url": None,
        "wandb_run_id": None,
        "last_observed_at": None,
        "observability_mode": mode,
    }


class ObservabilityAdapter(Protocol):
    name: str

    def log_run(self, record: dict[str, Any]) -> dict[str, Any]:
        """Log one run; return safe link metadata (may be empty)."""


class NoOpAdapter:
    """Default adapter. Logs nothing and returns no links."""

    name = "noop"

    def log_run(self, record: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        return {}


class BraintrustObservabilityAdapter:
    """Logs one Braintrust span/record per run behind an optional SDK import."""

    name = "braintrust"

    def __init__(
        self,
        config: ObservabilityConfig,
        *,
        braintrust_module: Any | None = None,
    ) -> None:
        self.config = config
        self._module = braintrust_module

    def _import(self) -> Any:
        if self._module is not None:
            return self._module
        import braintrust  # noqa: PLC0415

        return braintrust

    def log_run(self, record: dict[str, Any]) -> dict[str, Any]:
        try:
            bt = self._import()
            experiment = bt.init(
                project=self.config.braintrust_project,
                experiment=f"ahe_observability_{record.get('task_id')}",
            )
            experiment.log(
                input={"task_id": record.get("task_id"), "policy": record.get("policy_id")},
                output={"verdict": record.get("verdict")},
                scores={name: (1.0 if passed else 0.0) for name, passed in record.get("scorers", {}).items()},
                metadata={
                    "run_identity": record.get("run_identity"),
                    "task_type": record.get("task_type"),
                    "failure_labels": record.get("failure_labels", []),
                    "source": "ahe_observability",
                },
            )
            experiment_id = getattr(experiment, "id", None)
            url = None
            summarize = getattr(experiment, "summarize", None)
            if callable(summarize):
                summary = summarize()
                url = getattr(summary, "experiment_url", None)
            if hasattr(experiment, "flush"):
                experiment.flush()
            return {
                "braintrust_experiment_id": experiment_id,
                "braintrust_url": url,
            }
        except Exception as exc:  # noqa: BLE001 — soft-fail; never break the pipeline
            return {"braintrust_error": str(exc)}


class WandbObservabilityAdapter:
    """Logs one W&B run per task/policy behind an optional SDK import."""

    name = "wandb"

    def __init__(
        self,
        config: ObservabilityConfig,
        *,
        wandb_module: Any | None = None,
        group: str | None = None,
    ) -> None:
        self.config = config
        self._module = wandb_module
        self.group = group or "ahe_eval_suite"

    def _import(self) -> Any:
        if self._module is not None:
            return self._module
        import wandb  # noqa: PLC0415

        return wandb

    def log_run(self, record: dict[str, Any]) -> dict[str, Any]:
        try:
            wandb = self._import()
            init_kwargs: dict[str, Any] = {
                "project": self.config.wandb_project,
                "group": self.group,
                "name": record.get("run_identity"),
                "mode": self.config.wandb_mode,
                "reinit": True,
                "config": {
                    "task_id": record.get("task_id"),
                    "task_type": record.get("task_type"),
                    "policy_id": record.get("policy_id"),
                    "verdict": record.get("verdict"),
                },
            }
            if self.config.wandb_entity:
                init_kwargs["entity"] = self.config.wandb_entity
            run = wandb.init(**init_kwargs)
            metrics = dict(record.get("metrics", {}))
            metrics["aggregate_run_quality"] = record.get("aggregate_run_quality")
            run.log(metrics)
            run_url = getattr(run, "url", None)
            run_id = getattr(run, "id", None)
            finish = getattr(run, "finish", None)
            if callable(finish):
                finish()
            return {"wandb_url": run_url, "wandb_run_id": run_id}
        except Exception as exc:  # noqa: BLE001 — soft-fail; never break the pipeline
            return {"wandb_error": str(exc)}


def get_adapters(
    config: ObservabilityConfig,
    *,
    require: bool = False,
    braintrust_module: Any | None = None,
    wandb_module: Any | None = None,
) -> tuple[list[ObservabilityAdapter], list[str]]:
    """Resolve adapters for the configured mode.

    Returns (adapters, warnings). Missing SDKs warn (soft) unless ``require`` is
    set, in which case a missing SDK raises ``RuntimeError``.
    """
    adapters: list[ObservabilityAdapter] = []
    warnings: list[str] = []

    if config.braintrust_requested:
        if config.braintrust_ready or braintrust_module is not None:
            adapters.append(
                BraintrustObservabilityAdapter(config, braintrust_module=braintrust_module)
            )
        else:
            reason = _missing_reason(
                "braintrust",
                package_installed=config.braintrust_package_installed,
                api_key_present=config.braintrust_api_key_present,
            )
            if require:
                raise RuntimeError(f"Observability required but Braintrust unavailable: {reason}")
            warnings.append(f"braintrust observability skipped: {reason}")

    if config.wandb_requested:
        if config.wandb_ready or wandb_module is not None:
            adapters.append(WandbObservabilityAdapter(config, wandb_module=wandb_module))
        else:
            reason = _missing_reason(
                "wandb",
                package_installed=config.wandb_package_installed,
                api_key_present=config.wandb_api_key_present or config.wandb_mode in ("offline", "disabled"),
            )
            if require:
                raise RuntimeError(f"Observability required but W&B unavailable: {reason}")
            warnings.append(f"wandb observability skipped: {reason}")

    if not adapters:
        adapters.append(NoOpAdapter())
    return adapters, warnings


def _missing_reason(vendor: str, *, package_installed: bool, api_key_present: bool) -> str:
    missing: list[str] = []
    if not package_installed:
        missing.append(f"{vendor} package")
    if not api_key_present:
        missing.append("API key / mode")
    return ", ".join(missing) or "not configured"


# --------------------------------------------------------------------------- #
# Link export
# --------------------------------------------------------------------------- #


def build_links_artifact(
    project_root: Path,
    *,
    config: ObservabilityConfig | None = None,
    env: dict[str, str] | None = None,
    require: bool = False,
    braintrust_module: Any | None = None,
    wandb_module: Any | None = None,
) -> dict[str, Any]:
    """Build the exportable, null-safe observability link artifact."""
    config = config or load_config(env)
    artifact: dict[str, Any] = {
        "observability_version": OBSERVABILITY_VERSION,
        "observability_mode": config.mode,
        "generated_at": None,
        "warnings": [],
        "runs": {},
    }

    if config.mode == MODE_OFF:
        return artifact

    adapters, warnings = get_adapters(
        config,
        require=require,
        braintrust_module=braintrust_module,
        wandb_module=wandb_module,
    )
    artifact["warnings"] = warnings

    records = build_records(project_root, env=env)
    has_links = False
    for record in records:
        key = record["run_identity"]
        link = empty_link(config.mode)
        for adapter in adapters:
            result = adapter.log_run(record)
            for field in ("braintrust_url", "braintrust_experiment_id", "wandb_url", "wandb_run_id"):
                value = result.get(field)
                if value:
                    link[field] = value
                    has_links = True
        if any(link.get(f) for f in ("braintrust_url", "braintrust_experiment_id", "wandb_url", "wandb_run_id")):
            link["last_observed_at"] = _now_iso()
        artifact["runs"][key] = link

    artifact["generated_at"] = _now_iso() if has_links else None
    return sanitize(artifact, project_root=project_root, env=env)


def write_links_artifact(project_root: Path, artifact: dict[str, Any]) -> Path:
    path = project_root / LINKS_RELATIVE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def run_observability(
    project_root: Path,
    *,
    env: dict[str, str] | None = None,
    write: bool = True,
    require: bool = False,
    braintrust_module: Any | None = None,
    wandb_module: Any | None = None,
) -> dict[str, Any]:
    config = load_config(env)
    artifact = build_links_artifact(
        project_root,
        config=config,
        env=env,
        require=require,
        braintrust_module=braintrust_module,
        wandb_module=wandb_module,
    )
    written_path: str | None = None
    if write:
        written_path = str(write_links_artifact(project_root, artifact).relative_to(project_root))
    return {
        "ok": True,
        "mode": config.mode,
        "config": config.to_public_dict(),
        "warnings": artifact.get("warnings", []),
        "run_count": len(artifact.get("runs", {})),
        "links_path": written_path,
        "artifact": artifact,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Optional observability export for the local runner/eval pipeline. "
            "Default mode is off; configure with AHE_OBSERVABILITY and vendor env vars."
        )
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Repository root (default: auto-detected)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build records and link artifact without writing the JSON file.",
    )
    parser.add_argument(
        "--require",
        action="store_true",
        help="Fail (nonzero) if a requested vendor SDK/credential is unavailable.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    args = parser.parse_args()

    root = args.project_root.resolve()
    try:
        result = run_observability(root, write=not args.dry_run, require=args.require)
    except RuntimeError as exc:
        print(json.dumps({"ok": False, "code": "observability_required", "message": str(exc)}))
        return 1

    indent = 2 if args.pretty else None
    print(json.dumps(result, indent=indent, separators=None if args.pretty else (",", ":")))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
