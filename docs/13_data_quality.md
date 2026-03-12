# 13 Data Quality

This guide covers the quality-control rules that matter before data becomes training material.

## Core principle

Do not treat all ingested content as equally trustworthy or equally suitable for LoRA.

The safest model quality pattern is:

- broad raw corpus for RAG
- narrow curated corpus for fine-tuning

## Source trust ranking

Use a simple ranking model:

1. curated knowledge files you wrote intentionally
2. reviewed internal runbooks, ADRs, policies, and finance models
3. recent operational documents with clear ownership
4. external docs and bookmarks
5. noisy OCR output and low-confidence extraction

Higher-ranked sources should dominate training examples when conflicts exist.

## Duplicate handling

The pipeline already supports exact and near-duplicate detection. Your job is to decide which copy is canonical.

Best practice:

- keep the highest-quality source as canonical
- retain provenance to alternates in metadata
- do not fine-tune on the same knowledge repeated many times

## Contradictions

Contradictions are normal in personal corpora. Handle them deliberately:

- if one source is newer and authoritative, mark the older one as superseded
- if the answer genuinely depends on date, include the date explicitly in the training example
- if the issue is unresolved, prefer RAG with citations over encoding a strong LoRA answer

## Staleness and freshness

Ask these questions before promoting content into training:

- is this still your current view
- is the regulation or policy still current
- is the system architecture described still the real one
- are the assumptions in this spreadsheet still valid

If not, keep it for historical reference or archive it from training candidates.

## Noisy PDFs and OCR

Treat OCR-heavy files with caution.

Promote to training only if:

- extraction quality is readable
- tables or formulas survived well enough
- the document still contains stable knowledge

Otherwise, keep it retrieval-only or exclude it entirely.

## Spreadsheets and models

Do not fine-tune on raw spreadsheets blindly.

Instead:

- extract the stable logic
- write curated examples that explain the model or control logic
- keep the spreadsheet itself as retrieval evidence

## Sensitive information

Before fine-tuning or remote export:

- remove secrets
- redact credentials, personal data, and confidential identifiers where practical
- separate highly sensitive content from general domain knowledge

## Quality checklist before dataset generation

- is the content current
- is it authoritative
- is it duplicative
- is it stable enough to encode into the model
- is it better handled through RAG instead
- does it align with the persona and guardrail profile

## Recommended operating rule

When unsure:

- keep the material in RAG
- do not put it into LoRA training until it has been curated

That rule reduces the risk of encoding outdated or low-quality behavior into the adapter.

## Source strategy matrix

Use this as a first-pass default:

| Source type | Default use | Why |
| --- | --- | --- |
| `knowledge/persona.md` | LoRA + runtime prompt design | This is your intended voice and behavior |
| Curated domain files in `knowledge/domains/` | LoRA + optional RAG | Stable heuristics and default positions |
| Internal runbooks and ADRs | Both | Good retrieval sources and good basis for distilled examples |
| Policies and controls docs | Both | Strong source for governance and security behavior |
| Code repositories | Mostly RAG, selective LoRA | Good for retrieval, but LoRA should only encode stable patterns or preferences |
| Spreadsheets and financial models | RAG, plus distilled LoRA examples | Raw sheets are noisy; the logic is what matters |
| Email archives | Mostly RAG | Useful context, but often too noisy or transient for LoRA |
| Linkwarden bookmarks | Mostly RAG | Good discovery and citation layer, weak direct training material |
| OCR-heavy PDFs | RAG only unless curated | Extraction quality is often too unstable for fine-tuning |
| Temporary tickets or logs | Usually neither, or short-term RAG only | High churn and low long-term value |

If a source contains stable judgment and reusable reasoning, it is a LoRA candidate. If it mainly contains changing facts or one-off reference material, keep it in RAG.
