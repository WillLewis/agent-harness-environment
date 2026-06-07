from __future__ import annotations

from pathlib import Path

import pytest

import observability as obs
from observability import (
    BraintrustObservabilityAdapter,
    NoOpAdapter,
    WandbObservabilityAdapter,
    build_links_artifact,
    build_records,
    empty_link,
    get_adapters,
    load_config,
    parse_mode,
    parse_wandb_mode,
    scrub_text,
)


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


# --------------------------------------------------------------------------- #
# no-op adapter
# --------------------------------------------------------------------------- #


def test_noop_adapter_returns_no_links():
    adapter = NoOpAdapter()
    assert adapter.log_run({"task_id": "t", "policy_id": "p"}) == {}


def test_default_mode_uses_noop_only():
    config = load_config({})
    adapters, warnings = get_adapters(config)
    assert [a.name for a in adapters] == ["noop"]
    assert warnings == []


# --------------------------------------------------------------------------- #
# env parsing
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, "off"),
        ("", "off"),
        ("off", "off"),
        ("OFF", "off"),
        ("braintrust", "braintrust"),
        ("wandb", "wandb"),
        ("both", "both"),
        ("nonsense", "off"),
        ("weave", "off"),
    ],
)
def test_parse_mode(value, expected):
    assert parse_mode(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [(None, "online"), ("online", "online"), ("offline", "offline"), ("disabled", "disabled"), ("bogus", "online")],
)
def test_parse_wandb_mode(value, expected):
    assert parse_wandb_mode(value) == expected


def test_load_config_defaults_off():
    config = load_config({})
    assert config.mode == "off"
    assert config.braintrust_requested is False
    assert config.wandb_requested is False
    assert config.braintrust_project == "agent-harness-environment"


def test_load_config_both_requested():
    config = load_config(
        {
            "AHE_OBSERVABILITY": "both",
            "BRAINTRUST_PROJECT": "proj-bt",
            "WANDB_PROJECT": "proj-wb",
            "WANDB_ENTITY": "acme",
            "WANDB_MODE": "offline",
        }
    )
    assert config.mode == "both"
    assert config.braintrust_requested is True
    assert config.wandb_requested is True
    assert config.braintrust_project == "proj-bt"
    assert config.wandb_project == "proj-wb"
    assert config.wandb_entity == "acme"
    assert config.wandb_mode == "offline"


def test_public_config_never_contains_keys():
    config = load_config({"AHE_OBSERVABILITY": "both", "BRAINTRUST_API_KEY": "secret-key"})
    public = config.to_public_dict()
    assert "secret-key" not in repr(public)
    assert public["braintrust"]["api_key_present"] is True


# --------------------------------------------------------------------------- #
# missing SDK behavior
# --------------------------------------------------------------------------- #


def test_missing_sdk_soft_fails_with_warning():
    config = load_config({"AHE_OBSERVABILITY": "braintrust"})
    # No braintrust package / key in a clean env -> NoOp + warning, no raise.
    adapters, warnings = get_adapters(config)
    assert [a.name for a in adapters] == ["noop"]
    assert any("braintrust" in w for w in warnings)


def test_missing_sdk_raises_when_required():
    config = load_config({"AHE_OBSERVABILITY": "wandb"})
    with pytest.raises(RuntimeError):
        get_adapters(config, require=True)


def test_injected_modules_force_real_adapters():
    config = load_config({"AHE_OBSERVABILITY": "both"})
    adapters, warnings = get_adapters(
        config,
        braintrust_module=object(),
        wandb_module=object(),
    )
    names = {a.name for a in adapters}
    assert names == {"braintrust", "wandb"}
    assert warnings == []


def test_wandb_offline_mode_ready_without_key():
    config = load_config({"AHE_OBSERVABILITY": "wandb", "WANDB_MODE": "offline"})
    # Package still missing in CI, so this stays soft (no raise) but offline
    # does not require an API key.
    assert config.wandb_api_key_present is False
    assert config.wandb_mode == "offline"


# --------------------------------------------------------------------------- #
# exported link metadata shape
# --------------------------------------------------------------------------- #


def test_empty_link_shape():
    link = empty_link("off")
    assert set(link) == {
        "braintrust_url",
        "braintrust_experiment_id",
        "wandb_url",
        "wandb_run_id",
        "last_observed_at",
        "observability_mode",
    }
    assert link["observability_mode"] == "off"
    assert all(link[k] is None for k in link if k != "observability_mode")


def test_build_links_artifact_off_is_null_safe(project_root: Path):
    artifact = build_links_artifact(project_root, env={})
    assert artifact["observability_mode"] == "off"
    assert artifact["generated_at"] is None
    assert artifact["runs"] == {}
    assert artifact["warnings"] == []


def test_build_links_artifact_with_fake_vendors(project_root: Path):
    class FakeExp:
        id = "exp_1"

        def log(self, **_kwargs):
            return None

        def summarize(self):
            class Summary:
                experiment_url = "https://braintrust.dev/app/acme/exp_1"

            return Summary()

        def flush(self):
            return None

    class FakeBraintrust:
        @staticmethod
        def init(**_kwargs):
            return FakeExp()

    class FakeRun:
        id = "run_1"
        url = "https://wandb.ai/acme/proj/runs/run_1"

        def log(self, *_args, **_kwargs):
            return None

        def finish(self):
            return None

    class FakeWandb:
        @staticmethod
        def init(**_kwargs):
            return FakeRun()

    env = {"AHE_OBSERVABILITY": "both", "BRAINTRUST_API_KEY": "k", "WANDB_API_KEY": "k"}
    artifact = build_links_artifact(
        project_root,
        env=env,
        braintrust_module=FakeBraintrust,
        wandb_module=FakeWandb,
    )
    assert artifact["observability_mode"] == "both"
    assert artifact["generated_at"] is not None
    assert len(artifact["runs"]) >= 7
    sample = next(iter(artifact["runs"].values()))
    assert sample["braintrust_url"] == "https://braintrust.dev/app/acme/exp_1"
    assert sample["braintrust_experiment_id"] == "exp_1"
    assert sample["wandb_url"] == "https://wandb.ai/acme/proj/runs/run_1"
    assert sample["wandb_run_id"] == "run_1"
    assert sample["last_observed_at"] is not None


def test_build_records_shape_and_metrics(project_root: Path):
    records = build_records(project_root, env={})
    assert len(records) >= 7
    keys = {r["run_identity"] for r in records}
    assert all("::" in key for key in keys)
    record = records[0]
    for field in (
        "task_id",
        "policy_id",
        "policy_label",
        "verdict",
        "metrics",
        "scorers",
        "scorer_labels",
    ):
        assert field in record
    assert set(record["metrics"]) == {
        "task_success",
        "loop_rate",
        "interventions",
        "tool_calls",
        "event_count",
    }


# --------------------------------------------------------------------------- #
# secret / path scrubbing
# --------------------------------------------------------------------------- #


def test_scrub_text_redacts_secret_value():
    env = {"BRAINTRUST_API_KEY": "sk-supersecret-123"}
    scrubbed = scrub_text("token=sk-supersecret-123 done", env=env)
    assert "sk-supersecret-123" not in scrubbed
    assert "***redacted***" in scrubbed


def test_scrub_text_strips_project_root(project_root: Path):
    raw = f"{project_root}/data/traces/baseline_date_parser.json fixed"
    scrubbed = scrub_text(raw, project_root=project_root, env={})
    assert str(project_root) not in scrubbed
    assert scrubbed.startswith("data/traces/")


def test_scrub_text_strips_absolute_home_paths():
    scrubbed = scrub_text("see /Users/someone/secret/repo/file.py here", env={})
    assert "/Users/someone" not in scrubbed
    assert "<path>" in scrubbed


def test_records_never_leak_absolute_paths(project_root: Path):
    records = build_records(project_root, env={})
    blob = repr(records)
    assert str(project_root) not in blob
    assert "/Users/" not in blob
