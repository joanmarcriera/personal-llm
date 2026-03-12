# 09 Guardrails

## Purpose

This repository applies guardrails in several independent layers. This guide explains:

- where the guardrails live
- how to make them stronger
- how to make them weaker
- how to use the original model behavior with minimal repository guardrails

For difficult mixed-topic decisions, also read [docs/12_guardrail_boundary_cases.md](12_guardrail_boundary_cases.md).

## Guardrail layers

The repository uses five guardrail layers:

1. domain taxonomy in `config/domain_taxonomy.yaml`
2. runtime policy in `src/personal_llm/core/policy.py`
3. system and refusal prompts in `prompts/`
4. retrieval filtering in the RAG path
5. refusal examples in the LoRA training dataset

This matters because changing only one layer does not fully change system behavior.

Example:

- if you weaken the system prompt but leave runtime policy enabled, the API will still refuse disallowed topics
- if you disable runtime policy but keep refusal-heavy LoRA adapters, the model may still refuse because the adapter learned that behavior

## Built-in guardrail profiles

The repository includes these profiles in `config/guardrails.yaml`:

- `strict`
- `standard`
- `relaxed`
- `original_model`

Select one with:

```bash
export PERSONAL_LLM_GUARDRAIL_PROFILE=standard
```

or by setting it in `.env`.

### strict

Use when:

- you want a strongly domain-restricted assistant
- you prefer refusal over ambiguity
- you are handling sensitive professional workflows

Behavior:

- runtime policy enabled
- mixed-domain prompts refused
- disallowed retrieval excluded
- refusal examples included in training-set generation
- stricter system prompt

### standard

Use when:

- you want the recommended default
- you want professional-domain steering without refusing every mixed query

Behavior:

- runtime policy enabled
- clearly disallowed prompts refused
- mixed-domain prompts allowed unless the classifier marks them disallowed
- disallowed retrieval excluded
- refusal examples included in training-set generation

### relaxed

Use when:

- you still want professional steering
- you want fewer refusals
- you want the model to keep more of its original breadth

Behavior:

- runtime policy enabled
- mixed-domain prompts not automatically refused
- disallowed retrieval not automatically excluded
- refusal examples omitted from generated LoRA training sets
- softer system and refusal prompts

### original_model

Use when:

- you want the base model behavior with minimal repository guardrails
- you are comparing the raw base model against guarded variants
- you want to test how much the surrounding stack changes behavior

Behavior:

- runtime policy disabled
- no repository-level refusal enforcement
- disallowed retrieval not automatically excluded
- refusal examples omitted from generated LoRA training sets
- minimal repository system prompt

Important:

- this does not change the base model weights by itself
- if you use a previously trained adapter with refusal-heavy fine-tuning, the model may still behave like a guarded model
- for the cleanest baseline, use the original base model without a guardrail-heavy adapter

## How to strengthen guardrails

Use this order:

1. switch to `strict`
2. expand `disallowed_domains` and tighten keywords in `config/domain_taxonomy.yaml`
3. add more refusal examples to your training dataset
4. regenerate training data and retrain the adapter
5. re-run evaluation with refusal-compliance cases

### Add a new blocked topic

Edit `config/domain_taxonomy.yaml`:

```yaml
disallowed_domains:
  politics:
    keywords: [election, candidate, campaign, senate, parliament]
```

Then run:

```bash
uv run personal-llm classify-domains
uv run personal-llm build-training-set
uv run personal-llm embed
uv run personal-llm evaluate
```

### Make mixed-topic handling stricter

Use the `strict` profile. That profile refuses mixed-domain prompts instead of trying to salvage the professional part.

## How to weaken guardrails

Use this order:

1. switch to `relaxed`
2. reduce refusal examples in your training data
3. retrain or stop using a strongly guarded adapter
4. only if needed, switch to `original_model`

### Reduce runtime refusals without removing all guardrails

Set:

```bash
export PERSONAL_LLM_GUARDRAIL_PROFILE=relaxed
```

This keeps professional steering but removes the most aggressive repository-level restrictions.

### Keep the professional prompt but stop filtering retrieval

Use the `relaxed` profile. It stops automatically forcing `classification_label=allowed` at retrieval time.

## How to use the original model

If you want the original model with minimal repository guardrails:

1. choose the base model profile you want
2. set `PERSONAL_LLM_GUARDRAIL_PROFILE=original_model`
3. do not use a heavily guardrailed LoRA adapter
4. avoid training with refusal-heavy datasets unless you intentionally want that behavior

Example:

```bash
export PERSONAL_LLM_MODEL_PROFILE=qwen2.5-7b-instruct
export PERSONAL_LLM_GUARDRAIL_PROFILE=original_model
uv run personal-llm serve --reload
```

## How LoRA training changes guardrails

The generated training set changes with the selected guardrail profile:

- `strict` and `standard`: refusal examples are included
- `relaxed` and `original_model`: refusal examples are omitted

This means the same base model can end up behaving very differently depending on the training profile.

Best practice:

- tune runtime guardrails first
- only encode stronger guardrails into LoRA training when you are confident you want that behavior long-term

## Safe experimentation workflow

For a first-time user, use this sequence:

1. start with the base model and `standard`
2. test real prompts
3. if too restrictive, switch to `relaxed`
4. if still too restrictive, test `original_model`
5. only after that, decide whether the LoRA dataset should include refusal examples

That order avoids baking unwanted refusal behavior into adapters too early.

## Files to edit

- `config/guardrails.yaml`: choose or define profiles
- `config/domain_taxonomy.yaml`: add or remove blocked/allowed domains
- `prompts/system_professional_strict.md`: stricter top-level behavior
- `prompts/system_professional.md`: default behavior
- `prompts/system_professional_relaxed.md`: softer professional steering
- `prompts/system_original_model.md`: near-original model behavior
- `prompts/refusal_redirect.md`: default refusal wording
- `prompts/refusal_redirect_relaxed.md`: softer refusal wording
- `src/personal_llm/core/policy.py`: runtime allow/refuse logic
- `src/personal_llm/pipelines/dataset_builder.py`: training-set refusal inclusion

## Removing guardrails completely

That is possible, but I do not recommend it if your goal is a domain-specialized professional assistant.

If you still want the closest thing to that:

1. use `original_model`
2. disable or ignore any refusal-heavy adapter
3. avoid disallowed-topic filtering in retrieval
4. keep evaluation separate so you can compare behaviors clearly

The repository is designed for specialization, so fully removing every guardrail works against the main design goal.

## Related files and examples

- [config/guardrails.yaml](../config/guardrails.yaml)
- [config/domain_taxonomy.yaml](../config/domain_taxonomy.yaml)
- [docs/10_dataset_design_examples.md](10_dataset_design_examples.md)
- [docs/12_guardrail_boundary_cases.md](12_guardrail_boundary_cases.md)
- [knowledge/persona.md](../knowledge/persona.md)
