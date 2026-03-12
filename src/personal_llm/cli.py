from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
import uvicorn
from rich.console import Console

from personal_llm.api.app import create_app
from personal_llm.config.settings import AppSettings, get_settings
from personal_llm.evaluation.runner import EvaluationRunner
from personal_llm.pipelines.orchestrator import PipelineOrchestrator
from personal_llm.training.mlx_lora import MLXTrainingManager
from personal_llm.training.runpod import RunPodTrainingManager

app = typer.Typer(add_completion=False, help="Personal professional-domain LLM toolkit.")
console = Console()


def _settings() -> AppSettings:
    return get_settings()


def _orchestrator() -> PipelineOrchestrator:
    return PipelineOrchestrator(settings=_settings())


@app.command()
def ingest(
    config: Annotated[Path, typer.Option("--config", exists=True, file_okay=True, dir_okay=False)] = Path(
        "config/sources.yaml"
    ),
) -> None:
    orchestrator = _orchestrator()
    sources = orchestrator.sync_sources(config_path=config)
    typer.echo(f"ingested={len(sources)} manifest={orchestrator.source_manifest_path}")


@app.command()
def extract() -> None:
    orchestrator = _orchestrator()
    documents = orchestrator.extract_documents()
    typer.echo(f"documents={len(documents)} output={orchestrator.documents_manifest_path}")


@app.command("classify-domains")
def classify_domains() -> None:
    orchestrator = _orchestrator()
    chunks = orchestrator.classify_and_chunk_documents()
    typer.echo(f"chunks={len(chunks)} output={orchestrator.chunks_manifest_path}")


@app.command("build-training-set")
def build_training_set() -> None:
    orchestrator = _orchestrator()
    training_examples = orchestrator.build_training_dataset()
    typer.echo(f"training_examples={len(training_examples)}")


@app.command()
def embed() -> None:
    orchestrator = _orchestrator()
    embedding_records = orchestrator.embed_chunks()
    typer.echo(f"embeddings={len(embedding_records)}")


@app.command()
def reindex() -> None:
    orchestrator = _orchestrator()
    embedding_records = orchestrator.reindex()
    typer.echo(f"reindexed={len(embedding_records)}")


@app.command("sync-sources")
def sync_sources() -> None:
    orchestrator = _orchestrator()
    result = orchestrator.full_sync()
    typer.echo(json.dumps(result, indent=2))


@app.command()
def evaluate(
    cases: Annotated[Path | None, typer.Option("--cases", file_okay=True, dir_okay=False)] = None,
) -> None:
    settings = _settings()
    runner = EvaluationRunner(settings=settings)
    report = runner.run(cases_path=cases)
    typer.echo(json.dumps(report.model_dump(mode="json"), indent=2))


@app.command("train-local-mlx")
def train_local_mlx(
    config: Annotated[Path, typer.Option("--config", exists=True)] = Path("config/training.yaml"),
    dataset: Annotated[Path | None, typer.Option("--dataset", file_okay=True, dir_okay=False)] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
) -> None:
    manager = MLXTrainingManager(settings=_settings())
    command = manager.run(config_path=config, dataset_path=dataset, dry_run=dry_run)
    typer.echo(" ".join(command))


@app.command("train-remote-runpod")
def train_remote_runpod(
    config: Annotated[Path, typer.Option("--config", exists=True)] = Path("config/training.yaml"),
    dataset: Annotated[Path | None, typer.Option("--dataset", file_okay=True, dir_okay=False)] = None,
    submit: Annotated[bool, typer.Option("--submit")] = False,
) -> None:
    manager = RunPodTrainingManager(settings=_settings())
    result = manager.run(config_path=config, dataset_path=dataset, submit=submit)
    typer.echo(json.dumps(result, indent=2))


@app.command()
def serve(
    host: Annotated[str, typer.Option("--host")] = "127.0.0.1",
    port: Annotated[int, typer.Option("--port")] = 8000,
    reload: Annotated[bool, typer.Option("--reload")] = False,
) -> None:
    settings = _settings()
    settings.host = host
    settings.port = port
    if reload:
        uvicorn.run("personal_llm.api.app:create_app", factory=True, host=host, port=port, reload=True)
        return
    uvicorn.run(create_app(settings=settings), host=host, port=port)


def main() -> None:
    app()


if __name__ == "__main__":
    main()

