# Review Rules for Agent Harness Environment

For changes under `packages/harness` or `packages/evals`:

- Flag any new policy that lacks a deterministic or heuristic scorer.
- Flag any terminal execution path that bypasses command safety checks.
- Flag eval changes that only use LLM-assisted judges without code-based metrics.
- Require tests for loop detection, hallucinated file detection, unsafe tool detection, and retry limits.
- Require trace instrumentation for every new tool path.
- Flag any hosted-demo change that depends on live API calls.
- Flag any product copy that overclaims RL-lite as model training.

For changes under `apps/web`:

- Verify baseline and guarded recovery states update trace, metrics, diff, terminal output, and verdict together.
- Verify raw JSON is hidden behind disclosure by default.
- Verify status labels are text-readable and not color-only.
