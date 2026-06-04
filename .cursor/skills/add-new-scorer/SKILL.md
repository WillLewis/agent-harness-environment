---
name: add-new-scorer
description: Use when adding deterministic, heuristic, or optional LLM-assisted scoring logic.
---

# Add New Scorer

1. Add the scorer under `packages/evals/scorers/<name>.py`.
2. Return `name`, `score`, `passed`, and `reason`.
3. Add the scorer to `packages/evals/run_eval.py`.
4. Add or update fixture examples.
5. Add tests for at least one positive and one negative case.
6. Document the scorer in `docs/EVAL_DESIGN.md`.

Quality bar:

- deterministic when possible
- threshold documented when heuristic
- evidence included in reason
- no network/API dependency by default
