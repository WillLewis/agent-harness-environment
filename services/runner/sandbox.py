from __future__ import annotations

import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parents[2] / "packages" / "evals"
if str(EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(EVAL_DIR))

from scorers.command_rules import classify_command as classify_command_rules  # noqa: E402


@dataclass(frozen=True)
class CommandDecision:
    allowed: bool
    reason: str


@dataclass(frozen=True)
class CommandRunResult:
    allowed: bool
    reason: str
    exit_code: int | None
    stdout: str
    stderr: str


def classify_command(command: str) -> CommandDecision:
    allowed, reason = classify_command_rules(command)
    return CommandDecision(allowed=allowed, reason=reason)


def copy_toy_repo(project_root: Path, toy_repo_dir: str, sandbox_dir: Path) -> None:
    source = project_root / "toy_repos" / toy_repo_dir
    if sandbox_dir.exists():
        shutil.rmtree(sandbox_dir)
    shutil.copytree(source, sandbox_dir)


def read_repo_file(sandbox_root: Path, relative_path: str) -> str:
    return (sandbox_root / relative_path).read_text(encoding="utf-8")


def write_repo_file(sandbox_root: Path, relative_path: str, content: str) -> None:
    path = sandbox_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def summarize_file_preview(content: str, limit: int = 120) -> str:
    first_line = content.strip().splitlines()[0] if content.strip() else "(empty file)"
    if len(first_line) > limit:
        return first_line[: limit - 3] + "..."
    return first_line


def run_command(command: str, cwd: Path, timeout: int = 30) -> CommandRunResult:
    decision = classify_command(command)
    if not decision.allowed:
        return CommandRunResult(
            allowed=False,
            reason=decision.reason,
            exit_code=None,
            stdout="",
            stderr="",
        )

    completed = subprocess.run(
        shlex.split(command),
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=False,
    )
    return CommandRunResult(
        allowed=True,
        reason=decision.reason,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
