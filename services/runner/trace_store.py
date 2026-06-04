from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonTraceStore:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def write_trace(self, run_id: str, trace: dict[str, Any]) -> Path:
        path = self.root / f"{run_id}.json"
        path.write_text(json.dumps(trace, indent=2) + "\n")
        return path

    def read_trace(self, run_id: str) -> dict[str, Any]:
        return json.loads((self.root / f"{run_id}.json").read_text())
