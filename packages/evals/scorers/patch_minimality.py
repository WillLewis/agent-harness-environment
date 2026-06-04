from __future__ import annotations

from .common import ScoreResult, events


def score_patch_minimality(trace: dict) -> ScoreResult:
    touched = set()
    for event in events(trace):
        if event.get("action_type") == "EDIT":
            touched.update(event.get("files_touched") or [])
    if not touched:
        return ScoreResult("patch_minimality", 0.0, False, "No edited files found.")
    if len(touched) <= 2:
        return ScoreResult("patch_minimality", 1.0, True, f"Patch touched {len(touched)} file(s): {sorted(touched)}.")
    return ScoreResult("patch_minimality", 0.3, False, f"Patch touched many files: {sorted(touched)}.")
