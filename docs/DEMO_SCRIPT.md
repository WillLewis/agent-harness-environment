# Demo Script

## Opening

The core question behind Agent Harness Environment is: when a coding agent fails, how do we know whether the problem was the model, the prompt, the tool policy, the retry logic, the context strategy, or the developer experience?

## Step 1 — Show the task

Select `Bugfix: timezone parser regression`.

Narration:

> This is a small coding task with a target test. The agent needs to understand the failing assertion, inspect the parser, patch the narrow bug, and avoid regressions.

## Step 2 — Replay the baseline failure

Policy: `baseline`

Visible trace:

```text
PLAN → READ_FILE → EDIT → TEST_FAIL → TEST_FAIL → TEST_FAIL → LOOP_DETECTED → REJECTED
```

## Step 3 — Toggle guarded recovery

Policy: `guarded_recovery`

Visible trace:

```text
PLAN → READ_TEST → READ_FILE → EDIT → TEST_FAIL → INSPECT_ERROR → PATCH → TEST_PASS → ACCEPTED
```

## Step 4 — Eval comparison

Show policy comparison and click the baseline loop metric.

## Step 5 — Failure cluster

Show `repeated_terminal_command` and promote to dataset.

## Step 6 — Router

Show the RL-lite router selecting `guarded_recovery` for bugfix tasks with failed-test recovery risk.

## Closing

Agent Harness Environment demonstrates the product loop: trace behavior, label failure, add eval coverage, change the harness, and measure whether the agent became more reliable.
