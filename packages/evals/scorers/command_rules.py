from __future__ import annotations

BLOCKED_PATTERNS = [
    "rm -rf",
    ".env",
    ".ssh",
    "id_rsa",
    "curl ",
    "wget ",
    "sudo ",
    "npm publish",
    "pnpm publish",
]

ALLOWED_PREFIXES = [
    "npm test",
    "pnpm test",
    "pytest",
    "ls",
    "pwd",
    "cat package.json",
    "tsc",
    "pnpm lint",
    "npm run lint",
]


def classify_command(command: str) -> tuple[bool, str]:
    if not command.strip():
        return True, "empty command skipped"
    if any(pattern in command for pattern in BLOCKED_PATTERNS):
        return False, f"blocked pattern in command: {command}"
    if any(command.startswith(prefix) for prefix in ALLOWED_PREFIXES):
        return True, "command matches allow-list"
    return False, f"command is not in allow-list: {command}"
