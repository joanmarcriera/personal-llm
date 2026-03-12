# 03 Training

## Scope

This repository uses adapter-based fine-tuning only. Full model retraining is intentionally out of scope.

## Local MLX LoRA

`MLX` is the Apple-Silicon-native ML framework used in this repository for local model execution and local LoRA training. It is the default local training path because it fits the MacBook Pro M4 goal better than a generic CUDA-first setup.

- Default target: `Qwen2.5-7B-Instruct`
- Fast dry-run target: `Qwen2.5-3B-Instruct`
- Recommended for quick iteration, refusal tuning, domain alignment, and prompt-format adaptation
- Output adapters are written under `adapters/output/`
- The training manager prepares an MLX-compatible dataset directory under `data/training/generated/mlx/` and writes a generated config under `adapters/generated/`

If your goal is to validate the full process quickly rather than produce the first serious model, start with `qwen2.5-3b-instruct`. Once the workflow is proven, move back to `qwen2.5-7b-instruct` for the real adapter.

### Example

```bash
uv run personal-llm train-local-mlx \
  --config config/training.yaml \
  --dataset data/training/example_sft.jsonl
```

## Dataset design

- Positive technical/professional conversations
- Refusal examples for disallowed domains
- RAG-grounded instruction/answer pairs
- Jurisdiction-aware finance and tax examples with explicit disclaimer behavior

Use [docs/10_dataset_design_examples.md](10_dataset_design_examples.md) and [data/training/examples/README.md](../data/training/examples/README.md) before building your own dataset. Those files show the expected JSONL schema, good and bad pair design, refusal examples, and boundary cases.

The selected guardrail profile affects generated training data:

- `strict` and `standard` include refusal examples
- `relaxed` and `original_model` do not

See `docs/09_guardrails.md` before generating adapters if you want to preserve more of the original base model behavior.
See [knowledge/persona.md](../knowledge/persona.md) and [docs/11_personal_knowledge.md](11_personal_knowledge.md) before generating domain examples if the model should reflect your own decision style rather than only source documents.

## Remote LoRA

Use RunPod for the default remote automation path when local training is too slow or you need 14B-class adapters.

`RunPod` is not part of the local system. It is only the optional rented-GPU path for remote adapter jobs.
