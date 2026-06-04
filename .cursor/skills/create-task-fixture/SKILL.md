---
name: create-task-fixture
description: Use when creating a new coding task fixture for hosted replay or local evals.
---

# Create Task Fixture

1. Add a task row to `data/tasks.json` and `packages/evals/datasets/coding_tasks.jsonl`.
2. Add or update toy repo files under `toy_repos/<repo_name>`.
3. Create at least two traces:
   - baseline failure or weak result
   - improved policy result
4. Add expected files, success command, tags, and failure modes.
5. Ensure every trace event conforms to `AgentTraceEvent`.
6. Add eval comparison data if the task appears in the hosted UI.

Hosted task fixtures should be curated and readable. Do not add dozens of tasks to the default cockpit.
