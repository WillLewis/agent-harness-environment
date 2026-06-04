---
name: run-agent-eval
description: Use when you need to score a trace, compare policies, or verify eval regressions.
---

# Run Agent Eval

1. Validate fixtures with `pnpm validate:fixtures`.
2. Score the baseline trace with `pnpm eval:baseline`.
3. Score the improved trace with `pnpm eval`.
4. Compare policies with `pnpm compare`.
5. Inspect scorer reasons, not just aggregate scores.
6. If a scorer fails, fix scorer logic or fixture shape before changing UI.

Do not add live LLM judging to the critical path. LLM-assisted judging must be optional.
