# Cursor Prompt Pack

## Build hosted cockpit

```text
Read docs/UX_PLAN.md and apps/web/lib/demoData.ts. Build the cockpit so policy selection updates trace rows, metrics, verdict, file tree, terminal output, diff, and judge notes together. Use static fixtures only. Prioritize the baseline → guarded_recovery comparison.
```

## Add scorer tests

```text
Read packages/evals/run_eval.py and packages/evals/scorers. Add pytest coverage for loop_score, hallucinated_file, unsafe_tool_use, patch_minimality, and recovery_score. Use small inline trace dictionaries and keep tests deterministic.
```

## Add a new task fixture

```text
Use .cursor/skills/create-task-fixture/SKILL.md. Add an adversarial .env task with a blocked-action trace, an improved guarded_recovery trace, eval comparison rows, and a failure cluster for unsafe_tool_attempt.
```

## Implement runner MVP

```text
Implement the smallest real runner step in services/runner. It should copy toy_repos/date_utils into a temp sandbox, run an allow-listed test command, emit AgentTraceEvent records, and write runs/<run_id>.json. Do not introduce a live LLM yet.
```

## Improve MCP

```text
Read tools/mcp_server.py and .cursor/mcp.json. Make each MCP tool return compact results under 4KB by default, with optional verbose arguments for full trace JSON.
```
