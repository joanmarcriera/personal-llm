from __future__ import annotations

from pathlib import Path

from personal_llm.config.settings import get_settings
from personal_llm.pipelines.orchestrator import PipelineOrchestrator


def test_orchestrator_can_process_fixture_corpus(tmp_path: Path) -> None:
    settings = get_settings().model_copy(update={"home": tmp_path})
    for relative in [
        Path("config"),
        Path("tests/fixtures/markdown"),
        Path("tests/fixtures/html"),
        Path("tests/fixtures/spreadsheets"),
        Path("tests/fixtures/email"),
        Path("tests/fixtures/linkwarden"),
        Path("tests/fixtures/code"),
    ]:
        (settings.home / relative).mkdir(parents=True, exist_ok=True)
    (settings.home / "config/domain_taxonomy.yaml").write_text(
        Path("config/domain_taxonomy.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (settings.home / "config/sources.yaml").write_text(
        Path("config/sources.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (settings.home / "config/guardrails.yaml").write_text(
        Path("config/guardrails.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (settings.home / "prompts").mkdir(exist_ok=True)
    for name in [
        "system_professional_strict.md",
        "system_professional.md",
        "system_professional_relaxed.md",
        "system_original_model.md",
        "refusal_redirect.md",
        "refusal_redirect_relaxed.md",
        "refusal_disabled.md",
        "topic_router.md",
        "legal_finance_disclaimer.md",
    ]:
        (settings.home / "prompts" / name).write_text(
            (Path("prompts") / name).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    fixture_files = {
        "tests/fixtures/markdown/sample.md": "# Platform Notes\nTerraform and Kubernetes underpin the delivery platform.",
        "tests/fixtures/html/sample.html": "<html><body><h1>IAM</h1><p>OIDC and SCIM reduce provisioning drift.</p></body></html>",
        "tests/fixtures/spreadsheets/sample.csv": "metric,value\nmrr,12000\nburn,8000\n",
        "tests/fixtures/linkwarden/export.json": '{"links":[{"name":"Solar note","url":"https://example.com","description":"Tariff optimisation","textContent":"Battery tariffs and inverter constraints matter."}]}',
        "tests/fixtures/code/README.md": "# Infra Repo\nGitHub Actions deploy Terraform to staging and production.\n",
        "tests/fixtures/email/sample.mbox": "From nobody@example.com Fri Jan  1 00:00:00 2026\nSubject: Incident review\nFrom: ops@example.com\nTo: team@example.com\n\nWe updated our Kubernetes ingress and rotated certificates.\n",
    }
    for relative, content in fixture_files.items():
        destination = settings.home / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")

    orchestrator = PipelineOrchestrator(settings=settings)
    sources = orchestrator.sync_sources(Path("config/sources.yaml"))
    documents = orchestrator.extract_documents()
    chunks = orchestrator.classify_and_chunk_documents()
    training = orchestrator.build_training_dataset()

    assert len(sources) >= 4
    assert len(documents) >= 4
    assert len(chunks) >= 4
    assert len(training) >= 2
