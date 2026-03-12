PYTHON ?= uv run

.PHONY: bootstrap lint format typecheck test smoke docs-serve docs-build serve ingest extract classify embed evaluate train-local train-remote-runpod export-mermaid

bootstrap:
	uv sync --extra local --extra dev
	pre-commit install

lint:
	$(PYTHON) ruff check src tests scripts

format:
	$(PYTHON) ruff format src tests scripts

typecheck:
	$(PYTHON) mypy src

test:
	$(PYTHON) pytest tests

smoke:
	$(PYTHON) pytest tests/smoke

docs-serve:
	$(PYTHON) mkdocs serve

docs-build:
	$(PYTHON) mkdocs build

serve:
	$(PYTHON) personal-llm serve --reload

ingest:
	$(PYTHON) personal-llm ingest --config config/sources.yaml

extract:
	$(PYTHON) personal-llm extract

classify:
	$(PYTHON) personal-llm classify-domains

embed:
	$(PYTHON) personal-llm embed

evaluate:
	$(PYTHON) personal-llm evaluate

train-local:
	$(PYTHON) personal-llm train-local-mlx

train-remote-runpod:
	$(PYTHON) personal-llm train-remote-runpod

export-mermaid:
	bash scripts/export_mermaid.sh
