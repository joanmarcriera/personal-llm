from __future__ import annotations

from pathlib import Path

from personal_llm.config.settings import get_settings
from personal_llm.connectors.local_files import LocalFilesConnector


def test_local_files_connector_materializes_snapshot(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    raw_dir = tmp_path / "raw"
    source_dir.mkdir()
    document = source_dir / "notes.md"
    document.write_text("# Notes\nKubernetes and Terraform.\n", encoding="utf-8")

    settings = get_settings().model_copy(update={"home": tmp_path})
    connector = LocalFilesConnector()
    results = connector.discover(
        settings=settings,
        raw_dir=raw_dir,
        connector_config={
            "paths": [str(source_dir)],
            "include_extensions": [".md"],
        },
    )

    assert len(results) == 1
    source = results[0]
    assert source.uri == document.resolve().as_uri()
    assert source.content_path != str(document.resolve())
    assert Path(source.content_path).exists()
    assert source.metadata["snapshot_strategy"] == "content_addressed_copy"
    assert source.metadata["original_path"] == str(document.resolve())

