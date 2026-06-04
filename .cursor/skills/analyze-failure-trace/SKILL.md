---
name: analyze-failure-trace
description: Use when an agent run fails, loops, hallucinates files, or needs human steering.
---

# Analyze Failure Trace

1. Load the trace by `run_id` or fixture path.
2. Identify repeated tool calls, failed terminal commands, hallucinated files, blocked actions, and ungrounded edits.
3. Assign one or more failure labels:
   - `premature_edit`
   - `ignored_test_output`
   - `loop_detected`
   - `hallucinated_file`
   - `unsafe_tool_attempt`
   - `regression_introduced`
   - `failed_recovery`
4. Recommend whether the fix belongs in:
   - policy
   - tool permissioning
   - retry logic
   - model/router choice
   - scorer
   - dataset coverage
5. If code changes are needed, implement the smallest harness change and add or update an eval.
