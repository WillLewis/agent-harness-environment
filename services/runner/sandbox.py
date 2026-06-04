from __future__ import annotations

from dataclasses import dataclass

BLOCKED_PATTERNS = ["rm -rf", ".env", ".ssh", "id_rsa", "curl ", "wget ", "sudo ", "npm publish", "pnpm publish"]
ALLOWED_PREFIXES = ["npm test", "pnpm test", "pytest", "ls", "pwd", "cat package.json", "tsc", "pnpm lint", "npm run lint"]


@dataclass(frozen=True)
class CommandDecision:
    allowed: bool
    reason: str


def classify_command(command: str) -> CommandDecision:
    if any(pattern in command for pattern in BLOCKED_PATTERNS):
        return CommandDecision(False, f"blocked pattern in command: {command}")
    if any(command.startswith(prefix) for prefix in ALLOWED_PREFIXES):
        return CommandDecision(True, "command matches allow-list")
    return CommandDecision(False, "command is not in allow-list")
