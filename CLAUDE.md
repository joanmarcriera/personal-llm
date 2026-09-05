# personal-llm — Claude Code onboarding

## Purpose
Production-oriented scaffolding for a personal domain-specialized LLM focused on professional/technical knowledge (infrastructure, DevOps, cloud, finance, AI systems). The system ingests personal knowledge from Google Drive, NFS, email, Linkwarden, local files, and code repos; normalizes and tags data for RAG and LoRA fine-tuning; enforces strict topic boundaries (professional domains only); and serves an OpenAI-compatible API with citations and configurable backends.

## Quick start
```bash
uv sync --extra local --extra dev    # Install deps (MLX for Apple Silicon)
cp .env.example .env                 # Setup environment
make bootstrap                        # Install pre-commit hooks
make lint format typecheck           # Verify code quality
make test                            # Run tests (19 units + integration)
uv run personal-llm ingest --config config/sources.yaml  # Ingest sources
uv run personal-llm extract         # Extract documents
uv run personal-llm classify-domains # Domain classification
uv run personal-llm embed           # Build vector embeddings
make serve                           # Start FastAPI server (localhost:8000)
```

## Layout
| Path | Content |
|------|---------|
| `src/personal_llm/` | Main package: cli, api (FastAPI), connectors (GDrive/NFS/email/Linkwarden), pipelines (ETL), training (MLX/RunPod), rag, evaluation, vector_db |
| `config/` | YAML configs: models, sources, training, evaluation, security, domain_taxonomy |
| `data/raw/` | Immutable source snapshots (copied before extraction) |
| `data/processed/` | Normalized chunks, embeddings, manifests |
| `docs/` | 19+ step-by-step guides and operational runbooks (see 01_installation.md → 19_github_pages.md) |
| `knowledge/` | Curated personal knowledge, persona.md, domain opinions |
| `scripts/` | Bootstrap, sync, retrain, backup, remote-training helpers |
| `tests/` | Unit, integration, smoke tests; 19 passing |
| `Makefile` | Common commands: lint, format, typecheck, test, serve, ingest, extract, classify, embed, evaluate, train-local, train-remote-runpod |
| `mkdocs.yml`, `site-docs/` | MkDocs documentation site (deploy to GitHub Pages on main push) |

## How to run/test
- **Quick lint/format**: `make lint`, `make format` (ruff; 0 errors post-PR#1)
- **Type check**: `make typecheck` (mypy; 32 pre-existing errors, tracked separately as Vikunja blocker #1768)
- **Tests**: `make test` (pytest; 19 passing), `make smoke` (smoke tests only)
- **CLI commands**: `uv run personal-llm [ingest|extract|classify-domains|embed|reindex|evaluate|train-local-mlx|train-remote-runpod|serve]`
- **API server**: `make serve` (FastAPI on 127.0.0.1:8000, --reload for dev)
- **Docs**: `make docs-serve` (mkdocs serve), `make docs-build` (build site)

## Conventions
- **Python 3.12+**, uv for package management, setuptools for build
- **Code style**: ruff (line-length=100, E/F/I/UP/B/N/S/A/C4/T20), mypy (strict mode), pre-commit hooks
- **Commits**: Conventional Commits (feat/fix/chore/docs/style/refactor)
- **Tests**: pytest + pytest-asyncio; fixtures in conftest.py; smoke tests for end-to-end flows
- **Config**: Pydantic v2 models in `src/personal_llm/config/settings.py`, YAML sources in `config/`
- **CLI**: Typer with Path/Annotated options; output to stdout (typer.echo)
- **Secrets**: `.env` or sops+age encrypted overlay; never commit `.env` or API keys
- **Docs**: MkDocs with Material theme; 19 docs (01–19), architecture diagrams in mermaid

## Gotchas
1. **PR #1 not merged**: Recent ruff cleanup is on `fix/ruff-lint-672`, awaiting review before merge (auto-deploys docs to GitHub Pages on main push, so Marc reviews first)
2. **mypy debt**: 32 pre-existing type errors (pandas/yaml/datasketch/google libs missing stubs). Out of scope for PR#1; tracked as Vikunja blocker #1768
3. **Model profiles & guardrail profiles**: Set via env vars (`PERSONAL_LLM_MODEL_PROFILE`, `PERSONAL_LLM_GUARDRAIL_PROFILE`); defaults are qwen2.5-7b-instruct + standard. Fast dry runs use qwen2.5-3b-instruct
4. **Vector backend**: Defaults to Chroma (`PERSONAL_LLM_VECTOR_BACKEND=chroma`); Qdrant optional upgrade
5. **Inference backends**: MLX (default, Apple Silicon), Ollama, llama.cpp; set `PERSONAL_LLM_MODEL_BACKEND=auto` to auto-select
6. **Data immutability**: `data/raw/` is intentionally immutable (content-addressed snapshots); processed outputs go to `data/processed/`
7. **Google Drive & IMAP**: Optional; require client secrets and tokens in `.env`; see `.env.example`
8. **Runpod remote training**: Requires API key + template ID; dry-run by default (`--dry-run` flag)
9. **Docs deployment**: CI auto-builds and publishes to GitHub Pages on `main` push (`.github/workflows/pages.yml`)
10. **Embedding provider**: Defaults to 'hash' (deterministic); production uses embedding models

## Vikunja / Blockers
- **Task #672** (ruff lint): DONE, PR #1 awaiting merge
- **BLOCKER task #1768** (mypy): 32 type errors, CI red, explicitly out of scope for PR#1; needs dedicated type-stub/constraint work

## Dependencies
- Core: beautifulsoup4, chromadb, datasketch, fastapi, google-api-python-client, jinja2, pandas, pydantic, qdrant-client, rich, typer, uvicorn
- Local (Apple Silicon): mlx, mlx-lm
- Remote: axolotl, peft, transformers
- Serving: llama-cpp-python, ollama
- Dev: mypy, mkdocs-material, pytest, pytest-asyncio, pytest-cov, ruff, pre-commit

## Key files to know
- `src/personal_llm/cli.py` — Typer CLI entry point (main commands)
- `src/personal_llm/config/settings.py` — Pydantic AppSettings (env var binding)
- `src/personal_llm/pipelines/orchestrator.py` — PipelineOrchestrator (ingestion→embedding→evaluation)
- `src/personal_llm/api/app.py` — FastAPI app factory
- `config/sources.yaml` — Data source definitions (GDrive, NFS, email, etc.)
- `config/models.yaml` — Model profiles (qwen2.5-7b, llama-3.1-8b, etc.)
- `config/domain_taxonomy.yaml` — Topic filtering rules (allowed: infrastructure/DevOps/finance/AI; refused: sports/entertainment/trivia)
- `docs/01_installation.md` — Installation walkthrough
- `tests/integration/test_orchestrator.py` — Integration tests for full pipeline
