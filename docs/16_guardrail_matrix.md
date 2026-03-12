# 16 Guardrail Matrix

Use this guide when you want to compare guardrail profiles several times without waiting for the full evaluation suite every time.

## Why this exists

The full suite in [evaluation/cases/core_eval_cases.jsonl](../evaluation/cases/core_eval_cases.jsonl) is the final sign-off set. It is too heavy for repeated local profile comparisons on MLX.

For repeated comparisons, use:

- [evaluation/cases/guardrail_profile_matrix.jsonl](../evaluation/cases/guardrail_profile_matrix.jsonl)
- [scripts/benchmark_guardrail_profiles.py](../scripts/benchmark_guardrail_profiles.py)

## Recommended first matrix

Run this first:

```bash
UV_CACHE_DIR=.uv-cache uv run python scripts/benchmark_guardrail_profiles.py \
  --model-profile qwen2.5-3b-instruct
```

This benchmarks:

- `original_model`
- `relaxed`
- `standard`
- `strict`

against a smaller case set focused on:

- hard refusals
- boundary cases
- persona behavior
- a small number of allowed-domain answers

## Recommended workflow

1. run the small matrix on `qwen2.5-3b-instruct`
2. choose the best candidate guardrail profile
3. rerun the full suite on that candidate using [evaluation/cases/core_eval_cases.jsonl](../evaluation/cases/core_eval_cases.jsonl)
4. if the candidate still looks good, repeat the same process on `qwen2.5-7b-instruct`
5. only then start the first serious LoRA run

Archive and compare the reports with:

- [scripts/archive_evaluation_report.py](../scripts/archive_evaluation_report.py)
- [scripts/compare_evaluation_reports.py](../scripts/compare_evaluation_reports.py)

## How to interpret results

- `original_model` tells you what the raw base model does
- `relaxed` shows how far you can reduce refusals without losing too much control
- `standard` is the recommended default
- `strict` is useful when mixed-domain prompts should be refused more aggressively

## Important note

The current evaluation scorer is intentionally lightweight. Treat the matrix as a fast comparison tool, not a final scientific benchmark.

For a beginner-friendly explanation of what the metrics mean, read [docs/17_reading_evaluation_results.md](17_reading_evaluation_results.md).
