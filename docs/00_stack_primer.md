# 00 Stack Primer

This repository uses a few tools whose roles are easy to confuse when you first encounter them. This document explains what each one does in plain language, when you need it, and when you can ignore it.

## The simplest mental model

Your personal LLM system has five separate jobs:

1. collect and clean your documents
2. capture your own stable opinions and response style
3. search documents when the model needs context
4. run or fine-tune the model
5. expose the whole thing through a local API

The named tools in this repo map to those jobs like this:

- `MLX`: runs and fine-tunes models on Apple Silicon
- `Ollama`: runs local models behind a simple HTTP API
- `Qdrant`: stores embeddings so the system can retrieve relevant chunks later
- `RunPod`: rents remote GPU machines when your laptop is not enough

The curated knowledge layer for job 2 lives in [knowledge/README.md](../knowledge/README.md). That layer is what makes the system personal rather than just document-aware.

## What each tool is

### MLX

`MLX` is Apple’s machine learning framework for Apple Silicon. In this repository it is the default local path for model execution and local LoRA fine-tuning because it is designed for Apple Silicon and uses the Mac’s unified memory model well.

Use MLX when:

- you want to run and tune models locally on your Mac
- you want the most Apple-native path in this repo

You can ignore MLX when:

- you only want to call a model managed by Ollama
- you move training entirely to remote GPUs

### Ollama

`Ollama` is a local model runner. Think of it as a convenient local model server with a simple API. It downloads and serves models for you and exposes endpoints you can call from code.

Use Ollama when:

- you want a simple local API for chat or embeddings
- you want easier model management than wiring every backend yourself

You can ignore Ollama when:

- you are happy with the MLX-first local path
- you do not need a separate local model server yet

### Qdrant

`Qdrant` is a vector database. It stores embeddings plus metadata so the RAG system can retrieve relevant chunks such as “only infrastructure notes from the last six months” or “only finance documents tagged confidential”.

Use Qdrant when:

- you want stronger metadata filtering and a more production-style retrieval backend
- your corpus is growing and you want a dedicated vector store

You can ignore Qdrant when:

- you are starting with the easier local path
- Chroma is good enough for your first version

### RunPod

`RunPod` is a GPU cloud service. In this repository it is only for optional remote training. It is not required for local RAG or local inference.

Use RunPod when:

- local training on your Mac is too slow
- you want to train a larger adapter job, especially 14B-class models

You can ignore RunPod when:

- you are building your first local version
- you are staying with local MLX LoRA training

## What you actually need for v1

For a first complete local build, you only need:

- your documents on local disk or an NFS mount
- your emails as `mbox` or `.eml`
- your curated knowledge files in `knowledge/`
- `MLX`
- `Chroma`
- `FastAPI`

Everything else is optional.

## Recommended best practices

For a first-time user, I recommend:

- profile-driven model selection
- snapshot-based ingestion

Profile-driven means you pick a model profile such as `qwen2.5-7b-instruct`, and the repository chooses the matching backend for that profile. This avoids invalid combinations such as pointing an MLX-only model name at an Ollama runtime by accident.

For a fast full-process dry run, use `qwen2.5-3b-instruct`. It is the smallest practical real-model path in the repo and keeps you in the same Qwen family as the default 7B target.

Snapshot-based ingestion means the system copies local and NFS files into `data/raw/` before extraction. This is the best default for reproducibility because your processed corpus can always be traced back to the exact raw bytes that were indexed or used for training.

## NFS and email archives

If your documents live on a standard NFS share, mount it on macOS and point the `local_files` connector to that path. The ingestion pipeline treats it as normal local storage.

Best practice: do not extract directly from the live mount. This repository snapshots mounted files into `data/raw/` first so later processing is reproducible even if the NFS share changes.

If you do not want IMAP, use one of these formats instead:

- `mbox`: best for whole-mailbox exports
- a directory of `.eml` files: best for simple file-based ingestion
- Gmail Takeout archives: supported through the email connector

## Official documentation

- MLX: <https://github.com/ml-explore/mlx>
- MLX LM: <https://github.com/ml-explore/mlx-lm>
- Ollama docs: <https://docs.ollama.com/>
- Ollama API: <https://docs.ollama.com/api/introduction>
- Qdrant overview: <https://qdrant.tech/documentation/overview/>
- RunPod pods overview: <https://docs.runpod.io/pods/overview>
