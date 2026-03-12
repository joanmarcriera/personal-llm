# Smoke Tests

Use the smoke tests when you want a quick confidence check that the API surface still starts and responds.

## Run them

```bash
uv run pytest tests/smoke
```

## Scope

- API boot and request handling
- basic serving-path regressions
- high-level sanity checks after documentation, config, or orchestration changes

Smoke tests are not a substitute for the evaluation suite. Use [../../docs/07_evaluation.md](../../docs/07_evaluation.md) and [../../docs/15_first_training_run.md](../../docs/15_first_training_run.md) when you need model-quality or guardrail validation.
