# Evaluation Case Suites

This folder contains the benchmark files used to measure baseline behavior, guardrail behavior, and post-training changes.

## Case files

- [core_eval_cases.jsonl](core_eval_cases.jsonl): the main benchmark suite for first-run baselines and post-LoRA comparison
- [guardrail_profile_matrix.jsonl](guardrail_profile_matrix.jsonl): a smaller repeated-comparison set for guardrail profile selection
- [sample_request.json](sample_request.json): a sample API request payload for manual end-to-end checks

## When to use each file

- use `core_eval_cases.jsonl` when you want a serious baseline or release-candidate comparison
- use `guardrail_profile_matrix.jsonl` when you want a faster local comparison between `original_model`, `relaxed`, `standard`, and `strict`
- use `sample_request.json` when you want to send a prompt through the live API and inspect the full response shape

## Related guides

- [../../docs/07_evaluation.md](../../docs/07_evaluation.md)
- [../../docs/15_first_training_run.md](../../docs/15_first_training_run.md)
- [../../docs/16_guardrail_matrix.md](../../docs/16_guardrail_matrix.md)
- [../../docs/17_reading_evaluation_results.md](../../docs/17_reading_evaluation_results.md)
