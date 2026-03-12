# Evaluation Reports

Store baseline and post-training evaluation notes here.

Recommended files:

- `baseline-original-model.md`
- `baseline-standard-runtime.md`
- `post-lora-run-001.md`

Use [docs/15_first_training_run.md](../../docs/15_first_training_run.md) for the recommended baseline and comparison workflow.

Helpful utilities:

- [scripts/archive_evaluation_report.py](../../scripts/archive_evaluation_report.py)
- [scripts/compare_evaluation_reports.py](../../scripts/compare_evaluation_reports.py)
- [scripts/benchmark_guardrail_profiles.py](../../scripts/benchmark_guardrail_profiles.py)

Example reports:

- [guardrail_matrix_qwen2.5-3b-instruct.md](guardrail_matrix_qwen2.5-3b-instruct.md)
- [example_improvement_matrix_3b_original_vs_matrix_3b_standard.md](example_improvement_matrix_3b_original_vs_matrix_3b_standard.md)
- [example_degradation_matrix_3b_standard_vs_matrix_3b_strict.md](example_degradation_matrix_3b_standard_vs_matrix_3b_strict.md)

Local generated machine-readable outputs such as `latest.json`, archived report JSON files, and `.jsonl` report snapshots are intended for local use and are ignored by `.gitignore`.
