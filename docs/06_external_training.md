# 06 External Training

## Default provider: RunPod

RunPod is the primary provider with end-to-end automation in this repository.

In plain language, RunPod is a service that gives you rented GPU machines on demand. In this repository, you use it only when your Mac is not the right place to train the adapter job.

## GPU guidance

- 7B LoRA: L4 or A10G 24 GB class GPUs
- 14B LoRA: L40S or A100 40 GB+ class GPUs

## Cost and time bands

- 7B LoRA on L4/A10G: typically low tens of USD for moderate-size adapter jobs, often completed within a few hours
- 14B LoRA on L40S/A100: higher tens to low hundreds of USD depending on dataset size, epochs, context length, and storage overhead

Treat these as planning ranges rather than fixed prices.

## Included automation

- package dataset and config
- upload training bundle
- submit RunPod job spec
- poll job state
- pull back adapter artifacts and metrics

## When you do and do not need RunPod

Use RunPod when:

- you want to train a larger adapter faster than your Mac can handle
- you want to use 14B-class models more comfortably

Do not use RunPod when:

- you are still validating the ingestion and RAG pipeline
- local MLX LoRA is fast enough for your current dataset

## Additional providers

The repository includes guidance and config templates for:

- Lambda Labs
- Modal
- Together AI
- Replicate
- Hugging Face
- Vast.ai

These are documented but not fully automated in v1.
