# Knowledge Layer

This directory is the curated layer that sits between raw source documents and model training.

Raw documents tell the system what exists in your world. The files in `knowledge/` tell the system what you actually believe, prefer, reject, and want repeated consistently.

That distinction matters:

- `data/raw/` and `data/processed/` are evidence stores
- `knowledge/` is your high-signal operating manual
- `data/training/` is where that knowledge gets turned into SFT and refusal examples

## What belongs here

- your preferred response style
- your domain-specific opinions and heuristics
- default architecture choices
- tool preferences and anti-patterns
- finance, tax, and governance cautions you want repeated
- explicit boundary rulings for difficult mixed-domain questions

## Suggested workflow

1. edit [persona.md](persona.md)
2. fill in the relevant files listed in [domains/README.md](domains/README.md)
3. create training examples using [docs/10_dataset_design_examples.md](../docs/10_dataset_design_examples.md)
4. record a versioned snapshot under [snapshots/README.md](snapshots/README.md)
5. build or refresh your LoRA dataset

## Directory layout

| Path | Purpose |
| --- | --- |
| `persona.md` | How the assistant should sound and reason |
| `domains/` | One canonical file per professional domain cluster |
| `templates/` | Reusable authoring templates |
| `snapshots/` | Versioning notes that tie knowledge state to dataset and adapter runs |

## Best practice

Do not try to fine-tune directly from all raw documents. Use raw documents mainly for RAG and evidence retrieval. Use curated knowledge files to encode:

- your stable opinions
- your preferred decision logic
- the exact type of concise or detailed answers you want

That combination usually produces a much better personal assistant than training on noisy source material alone.
