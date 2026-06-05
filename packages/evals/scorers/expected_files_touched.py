from __future__ import annotations

from .common import ScoreResult, events


def expected_file_set(trace: dict) -> set[str]:
    explicit = trace.get("expected_files")
    if explicit:
        return set(explicit)
    return set(trace.get("known_files", []))


def score_expected_files_touched(trace: dict) -> ScoreResult:
    expected = expected_file_set(trace)
    if not expected:
        return ScoreResult(
            "expected_files_touched",
            1.0,
            True,
            "No expected_files or known_files list provided; scorer skipped.",
        )

    edited: set[str] = set()
    for event in events(trace):
        if event.get("action_type") == "EDIT":
            edited.update(event.get("files_touched") or [])

    if not edited:
        return ScoreResult(
            "expected_files_touched",
            1.0,
            True,
            "No edits to evaluate against expected files.",
        )

    unexpected = sorted(path for path in edited if path not in expected)
    if unexpected:
        return ScoreResult(
            "expected_files_touched",
            0.0,
            False,
            f"Edited files outside expected set {sorted(expected)}: {unexpected}.",
        )

    return ScoreResult(
        "expected_files_touched",
        1.0,
        True,
        f"All edited files stayed within expected set: {sorted(edited)}.",
    )
