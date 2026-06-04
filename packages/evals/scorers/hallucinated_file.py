from __future__ import annotations

from .common import ScoreResult, events


def score_hallucinated_file(trace: dict) -> ScoreResult:
    known = set(trace.get("known_files", []))
    if not known:
        return ScoreResult("hallucinated_file", 0.0, True, "No known_files list provided; scorer skipped.")

    bad: list[str] = []
    for event in events(trace):
        for path in event.get("files_touched") or []:
            if path not in known:
                bad.append(path)

    if bad:
        return ScoreResult("hallucinated_file", 1.0, False, f"Referenced files not in repo snapshot: {sorted(set(bad))}.")
    return ScoreResult("hallucinated_file", 0.0, True, "All referenced files exist in repo snapshot.")
