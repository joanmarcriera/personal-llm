# 01 Installation

## Goals

Set up a reproducible local environment for ingestion, RAG, LoRA training, and model serving on Apple Silicon.

If the stack names are unfamiliar, read [docs/00_stack_primer.md](00_stack_primer.md) first.

## Prerequisites

- macOS on Apple Silicon, ideally a MacBook Pro M4 with 48 GB RAM
- Xcode Command Line Tools
- `uv`
- `git`
- Optional: `ollama`, `docker`, `qdrant`, `age`, `sops`

## Step-by-step

1. Clone the repository and enter it.
2. Install dependencies:

   ```bash
   uv sync --extra local --extra dev
   ```

3. Copy `.env.example` to `.env`.
4. Review the config files in `/config`.
5. Before you train anything, review and edit the curated knowledge files in `/knowledge`. Start with [knowledge/persona.md](../knowledge/persona.md) and [docs/11_personal_knowledge.md](11_personal_knowledge.md).
6. If your documents are on a normal local disk or an NFS mount, point `config/sources.yaml` at that path and skip Google Drive entirely.
7. If you want to use Google Drive, create OAuth desktop credentials and place the client secret in `./secrets/google-client-secret.json`.
8. If your emails already exist as `mbox` files or `.eml` files, configure those paths and skip IMAP entirely.
9. If you want to use IMAP, set the host and credentials in `.env`.
10. If you want the optional production-style vector backend locally, start Qdrant:

   ```bash
   docker compose -f deployment/docker-compose.qdrant.yml up -d
   ```

11. Run smoke validation:

   ```bash
   python -m compileall src tests scripts
   ```

## Recommended local setup profiles

- Easiest first build: local/NFS documents + `mbox` or `.eml` email + MLX + Chroma + FastAPI
- Optional upgrade: Ollama or llama.cpp + Qdrant + FastAPI

## Plain-English tool summary

- `MLX`: the Apple-Silicon-native ML framework used here for local inference and LoRA fine-tuning
- `Ollama`: an optional local model server that makes local model management easier
- `Qdrant`: an optional vector database used for larger or more filter-heavy RAG setups
- `RunPod`: an optional remote GPU service for training jobs that are too large or slow on the Mac

## Default selection strategy

For a first-time user, the recommended setup is:

- backend selection: profile-driven
- source handling: snapshot-based

That means you normally set `PERSONAL_LLM_MODEL_PROFILE`, not `PERSONAL_LLM_MODEL_BACKEND`. The backend override exists for advanced use, but the default path is to let the chosen profile decide the correct backend.

## Notes

- Keep the repository private.
- Enable FileVault.
- Do not commit `.env`, secrets, or raw personal documents.
