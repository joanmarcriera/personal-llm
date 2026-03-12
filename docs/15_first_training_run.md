# 15 First Training Run

This guide turns the repository into a real first LoRA experiment instead of just a scaffold.

## Goal

Run a small, disciplined first cycle:

1. create curated knowledge
2. generate a small training set
3. run a baseline evaluation on the unadapted base model
4. train a first adapter
5. compare results against the baseline

## Recommended model choice for a dry run versus a real run

Use these defaults:

- `qwen2.5-3b-instruct` for a fast end-to-end dry run of the entire process
- `qwen2.5-7b-instruct` for the first serious personalized adapter

Why:

- the 3B profile is faster and cheaper to iterate with
- the 7B profile is a better target for the model you actually want to use for work
- both stay in the same Qwen family, so the prompts and overall behavior transfer more cleanly than switching to a very different model family

## Before you train

You should have:

- [knowledge/persona.md](../knowledge/persona.md) edited to match your preferred style
- at least three populated files listed in [knowledge/domains/README.md](../knowledge/domains/README.md)
- source documents ingested and embedded
- guardrail profile chosen
- evaluation prompts ready in [evaluation/cases/README.md](../evaluation/cases/README.md), especially `core_eval_cases.jsonl`

Important:

- the retrieval-grounded evaluation cases in `core_eval_cases.jsonl` only make sense if you have ingested matching internal documents
- if you have not loaded policy notes, IAM notes, finance notes, or architecture notes yet, replace those prompts with retrieval cases that match your real corpus before using the suite as a quality gate

## Recommended first dataset size

Do not start with a giant dataset.

For the first real run, target:

- `25-40` high-quality SFT examples
- `8-12` refusal examples if using `standard` or `strict`
- `10-15` boundary cases

Quality matters more than volume at this stage.

## Step 1: record the baseline

You need a pre-LoRA reference point. Otherwise you will not know whether the adapter helped or only changed style.

### Baseline A: original base model behavior

```bash
export PERSONAL_LLM_MODEL_PROFILE=qwen2.5-3b-instruct
export PERSONAL_LLM_GUARDRAIL_PROFILE=original_model
uv run personal-llm evaluate --cases evaluation/cases/core_eval_cases.jsonl
```

### Baseline B: base model plus your chosen runtime guardrails

```bash
export PERSONAL_LLM_MODEL_PROFILE=qwen2.5-3b-instruct
export PERSONAL_LLM_GUARDRAIL_PROFILE=standard
uv run personal-llm evaluate --cases evaluation/cases/core_eval_cases.jsonl
```

Why use both:

- Baseline A tells you what the raw model does
- Baseline B tells you what the surrounding prompt and policy stack already fixes before training

Record both in a snapshot note under [knowledge/snapshots/README.md](../knowledge/snapshots/README.md).

After the dry run is complete, repeat the same baseline steps with `qwen2.5-7b-instruct` before the serious adapter run.

## Step 2: run a dry run before the real adapter

Use a tiny dry run first:

- `10-12` examples
- one or two examples from each major domain you care about
- at least two refusal cases
- at least two boundary cases

Purpose:

- confirm your JSONL format
- confirm the answers sound right
- catch prompt or guardrail mismatches early

If you want to compare multiple guardrail profiles quickly before choosing one, use [docs/16_guardrail_matrix.md](16_guardrail_matrix.md).

## Step 3: train the first adapter

Use local MLX first unless you already know you need remote GPUs.

```bash
uv run personal-llm train-local-mlx \
  --config config/training.yaml \
  --dataset data/training/generated/train.jsonl
```

## Step 4: evaluate again

Run the same evaluation suite after training.

```bash
export PERSONAL_LLM_GUARDRAIL_PROFILE=standard
uv run personal-llm evaluate --cases evaluation/cases/core_eval_cases.jsonl
```

Then send a small set of high-risk prompts through the API:

```bash
uv run personal-llm serve --reload
curl -s http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d @evaluation/cases/sample_request.json
```

## What success looks like

- answers are more aligned with your persona
- the model is more consistent on your core domains
- refusals remain clean
- boundary cases improve rather than becoming over-refused
- regulated-domain answers become more structured and cautious

## Common failure modes

- `too generic`: add `5-10` persona-aligned SFT examples focused on the missing style, then re-evaluate
- `too restrictive`: remove or rewrite `3-5` refusal-heavy or over-aggressive boundary examples, or move to `relaxed`
- `not restrictive enough`: add `5-8` refusal examples and `3-5` boundary cases, then retrain
- `factual weakness`: improve retrieval and curated knowledge before adding more LoRA data
- `style improved but substance did not`: add `5-10` domain examples tied to your real heuristics or source evidence
- `retrieval-grounded prompts fail`: verify the matching docs were ingested, chunked, and embedded before changing LoRA data

## What to document after the run

Create a snapshot note with:

- date
- model profile
- guardrail profile
- dataset path
- prompt profile
- adapter output path
- baseline result summary
- post-training result summary
- what changed next

## Important caution

Do not assume a better-feeling answer means a better model. Compare against the baseline and keep the same eval cases across runs.

## When to stop tuning the first iteration

Ship the first iteration and move to real usage when:

- hard refusal cases pass
- boundary-case behavior is acceptably clean
- your persona checks are at or above the target in [docs/07_evaluation.md](07_evaluation.md)
- the model is clearly more useful than the baseline on your core domains

Do not keep tuning just because a few answers could still be better. Once the first iteration clears the quality bar, start using it for real work and collect the next wave of improvements from actual usage.
