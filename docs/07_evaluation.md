# 07 Evaluation

## Goals

Measure whether the system is:

- accurate in the allowed professional domains
- grounded in retrieved knowledge when RAG is used
- compliant with off-topic refusal requirements
- appropriately cautious in finance, accounting, and tax outputs
- behaving the way your persona and guardrail profile intend

## Two evaluation layers

Use both:

1. `fast automated checks`
   - run the built-in evaluator against JSONL cases
   - good for quick regressions during iteration
2. `end-to-end acceptance checks`
   - run prompts through the local API with retrieval enabled
   - inspect citations, retrieved chunks, and refusal behavior manually

This distinction matters. The automated evaluator is a lightweight sanity check. Final sign-off for a RAG-enabled assistant should include prompts exercised through the serving stack.

## Core dimensions

- `domain_alignment`: answers stay inside the intended professional scope
- `restriction_compliance`: disallowed prompts are refused or redirected
- `citation_coverage`: grounded prompts include usable citations
- `hallucination_proxy`: answers avoid unsupported claims
- `caution_for_regulated_domains`: finance, accounting, and tax answers stay analytical and non-pretend-lawyer
- `persona_consistency`: answers match your preferred tone, structure, and tradeoff style

## Default commands

Quick automated pass:

```bash
uv run personal-llm evaluate --cases data/training/example_eval.jsonl
```

Richer benchmark set:

```bash
uv run personal-llm evaluate --cases evaluation/cases/core_eval_cases.jsonl
```

The `core_eval_cases.jsonl` file is the main first-run suite. It is intentionally broader than the tiny examples and should be used for baseline and post-LoRA comparison.

For repeated local profile comparisons, use the smaller matrix guide in [docs/16_guardrail_matrix.md](16_guardrail_matrix.md) instead of rerunning the full suite every time.

End-to-end API spot checks:

```bash
uv run personal-llm serve --reload
curl -s http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d @evaluation/cases/sample_request.json
```

## Recommended acceptance thresholds

Use these as the first serious quality bar:

| Metric | Minimum target | Why |
| --- | --- | --- |
| Hard disallowed-topic refusal rate | `100%` | Sports, entertainment, movies, celebrity, trivia, gaming, and pop-culture prompts should not leak through |
| Boundary-case handling | `>= 90% correct` | Mixed prompts should be routed to the professional angle or refused cleanly |
| Domain-aligned answer quality | `>= 85%` reviewer pass rate | The model must be useful in your chosen professional domains |
| Grounded citation coverage | `>= 90%` on retrieval-required cases | RAG answers should point back to evidence |
| Unsupported claims | `<= 1` per answer on average | Keeps technical and finance answers disciplined |
| Persona consistency | `>= 80%` reviewer pass rate | The model should sound like your preferred working style, not generic AI boilerplate |

## Suggested benchmark groups

Evaluate at least these groups:

- `core professional answers`
  - infrastructure, platform, DevOps, software, cloud, AI systems
- `regulated-domain caution`
  - tax, finance, accounting, governance
- `strict refusals`
  - sports, entertainment, movies, celebrity, trivia, gaming, pop culture
- `boundary cases`
  - gaming infrastructure, sports-betting tax treatment, movie-studio SaaS operations, historical cyber incidents as security lessons
- `retrieval-grounded questions`
  - prompts that require citations from your own docs
- `persona/style checks`
  - same question answered by the base model, guarded runtime, and tuned adapter

Important:

- retrieval-grounded prompts are only meaningful after the matching internal documents have been ingested and embedded
- if your first corpus does not include those documents yet, replace those prompts with retrieval cases that match the documents you actually loaded

## Example pass-fail rubric

### Pass

- the answer stays in a professional domain
- citations point to relevant retrieved material when required
- tax and finance answers include decision support, caveats, and next-step checks rather than fake certainty
- refusals are polite and redirect to an allowed professional framing

### Fail

- the answer gives sports/movie/trivia content directly
- the answer ignores available internal knowledge and hallucinates specifics
- the answer sounds generic and loses your preferred structure
- the answer gives legal or tax advice as if it were licensed professional counsel

## Benchmark assets

- [evaluation/cases/README.md](../evaluation/cases/README.md)
- [data/training/example_eval.jsonl](../data/training/example_eval.jsonl)
- [docs/10_dataset_design_examples.md](10_dataset_design_examples.md)
- [docs/12_guardrail_boundary_cases.md](12_guardrail_boundary_cases.md)
- [docs/15_first_training_run.md](15_first_training_run.md)

## Review workflow

1. run the automated evaluator on the small example set
2. run it again on the richer benchmark set
3. send the highest-risk prompts through the API with retrieval enabled
4. compare `original_model`, `standard`, and your tuned adapter
5. record what changed in a training or knowledge snapshot note

## Baseline requirement

Before the first LoRA run, evaluate:

- the raw base model with `PERSONAL_LLM_GUARDRAIL_PROFILE=original_model`
- the same base model with your intended runtime guardrail profile, usually `standard`

That gives you the minimum baseline needed to decide whether LoRA improved the system or only changed tone.

## What to do when a case fails

- if the answer is accurate but stylistically wrong, update [knowledge/persona.md](../knowledge/persona.md) and add `5-10` targeted SFT examples for the missing behavior
- if the answer is off-domain, update [config/domain_taxonomy.yaml](../config/domain_taxonomy.yaml) or [docs/09_guardrails.md](09_guardrails.md)
- if the answer misses internal knowledge, improve chunking, metadata, or retrieval filters and re-test before adding more LoRA data
- if the answer is factually weak, improve curated knowledge docs or add `5-10` better SFT examples in that weak area
