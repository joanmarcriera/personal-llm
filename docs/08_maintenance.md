# 08 Maintenance

## Recurring tasks

- sync new documents
- rebuild processed manifests
- refresh vector indexes
- retrain adapters on an approved cadence
- run evaluation after any model, prompt, or taxonomy changes

## Suggested automation cadence

- Daily: sync and re-index newly approved documents
- Weekly: retrieval quality and refusal-compliance checks
- Monthly: LoRA refresh if enough new high-quality data exists

## Recommended controls

- back up `config/`, `prompts/`, `data/training/`, and approved adapters
- retain `data/raw/` snapshots long enough to reproduce any training or indexing run that matters
- encrypt raw data at rest
- rotate API keys
- review connector access scopes quarterly
