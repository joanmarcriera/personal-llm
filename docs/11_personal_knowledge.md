# 11 Personal Knowledge

This guide explains how to build the part of the repository that is actually personal.

## Why this layer matters

If you only ingest raw files, the system will know what documents say. It will not reliably know:

- your preferred defaults
- which tradeoffs you care about most
- which tools you trust or reject
- how cautious or challenging the assistant should be
- what answer structure feels useful to you

That is why the repository includes `knowledge/` as a curated layer.

## Three knowledge tiers

### Tier 1: raw evidence

Location:

- `data/raw/`
- `data/processed/`

Use for:

- RAG
- citations
- source-of-truth lookup

### Tier 2: curated personal knowledge

Location:

- `knowledge/persona.md`
- [knowledge/domains/README.md](../knowledge/domains/README.md)

Use for:

- your stable opinions
- default recommendations
- tone and response structure
- anti-patterns and heuristics

### Tier 3: training-ready examples

Location:

- `data/training/`
- [data/training/examples/README.md](../data/training/examples/README.md)

Use for:

- converting the curated layer into SFT, refusal, and boundary-case examples

## Recommended authoring order

1. define the persona
2. write domain files for your strongest knowledge areas
3. mark boundary cases that should be allowed or refused
4. create a small but high-quality training set
5. snapshot the knowledge state before training

## What to write in domain files

Each domain file should capture:

- default recommendation
- core heuristics
- preferred tools or patterns
- anti-patterns
- exceptions to your usual rule
- realistic example Q&A

Use [knowledge/templates/domain_knowledge_template.md](../knowledge/templates/domain_knowledge_template.md) as the baseline.

## How much detail is enough

For the first useful adapter, aim for:

- one persona file
- three to five strong domain files
- twenty to fifty carefully written training pairs derived from them

That is usually more valuable than hundreds of noisy auto-generated examples.

## Versioning strategy

Best practice for a first-time user:

- keep one current working version in `knowledge/`
- create a small snapshot note before each serious LoRA run in [knowledge/snapshots/README.md](../knowledge/snapshots/README.md)
- include the persona, changed domain files, guardrail profile, dataset path, and evaluation report

This is simpler and safer than trying to build a complex versioning system immediately.

## What should stay out of LoRA data

Usually keep these in RAG only unless they are very stable:

- long vendor docs
- transient tickets
- stale PDFs
- duplicate notes
- one-off spreadsheets with shifting assumptions

Only fine-tune on material you want repeated consistently.

## Signals that a topic belongs in curated knowledge

- you have a strong default answer
- you want the same framing every time
- the advice is more about judgment than memorizing facts
- you want the response style to feel like your own

## Related guides

- [docs/10_dataset_design_examples.md](10_dataset_design_examples.md)
- [docs/12_guardrail_boundary_cases.md](12_guardrail_boundary_cases.md)
- [docs/13_data_quality.md](13_data_quality.md)
- [docs/14_workflow_map.md](14_workflow_map.md)
