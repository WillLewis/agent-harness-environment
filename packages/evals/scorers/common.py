from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class ScoreResult:
    name: str
    score: float
    passed: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def events(trace: dict[str, Any]) -> list[dict[str, Any]]:
    return list(trace.get("events", []))
