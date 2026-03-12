# Knowledge Snapshots

Use this directory to record versioned knowledge states that feed training runs.

## Why snapshots matter

Your raw documents, curated knowledge, prompt profiles, and adapters will evolve over time. Without snapshots, you will not know why one run behaved better than another.

## Recommended naming

Use date plus a short label:

- `2026-03-11-v1-baseline`
- `2026-03-18-v2-guardrail-relaxed`
- `2026-04-02-v3-finance-refresh`

## What a snapshot note should include

- snapshot id
- date
- persona version or commit hash
- domain files changed
- guardrail profile
- training dataset paths and hashes
- source snapshot references from `data/raw/`
- model profile
- adapter output path
- evaluation report path
- short explanation of what changed

## Suggested file structure

Each snapshot can be a small Markdown note or YAML manifest. Example headings:

```text
snapshot_id: 2026-03-11-v1-baseline
model_profile: qwen2.5-7b-instruct
guardrail_profile: standard
knowledge_files:
  - knowledge/persona.md
  - knowledge/domains/01_infrastructure_platform.md
training_data:
  - data/training/generated/train.jsonl
evaluation_report: evaluation/reports/2026-03-11-v1-baseline.json
notes: First baseline after persona and infra domain curation.
```

## Best practice

- snapshot before every meaningful LoRA run
- snapshot before and after major guardrail changes
- snapshot after large knowledge refreshes
- keep the note small but complete enough to reproduce the run
