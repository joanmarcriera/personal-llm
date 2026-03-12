from __future__ import annotations

from pathlib import Path

from personal_llm.config.settings import AppSettings
from personal_llm.core.io import materialize_raw_copy, sha256_file
from personal_llm.core.schemas import SourceDocument, SourceType


INTERESTING_FILENAMES = {"Dockerfile", "Makefile", "README.md"}
INTERESTING_SUFFIXES = {".md", ".py", ".tf", ".yaml", ".yml", ".json", ".toml", ".sh"}


class CodeRepositoryConnector:
    def discover(
        self,
        settings: AppSettings,
        raw_dir: Path,
        connector_config: dict[str, object],
    ) -> list[SourceDocument]:
        paths = connector_config.get("paths", [])
        if not isinstance(paths, list):
            return []
        documents: list[SourceDocument] = []
        for path_string in paths:
            if not isinstance(path_string, str):
                continue
            root = settings.resolve(path_string)
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                if (
                    path.name not in INTERESTING_FILENAMES
                    and path.suffix.lower() not in INTERESTING_SUFFIXES
                ):
                    continue
                snapshot_path = materialize_raw_copy(path, raw_dir, "code_repositories")
                documents.append(
                    SourceDocument(
                        id=f"repo::{path.as_posix()}",
                        source_type=SourceType.CODE_REPOSITORY,
                        uri=path.as_uri(),
                        title=path.name,
                        content_path=str(snapshot_path),
                        checksum=sha256_file(path),
                        metadata={
                            "repository_root": str(root),
                            "extension": path.suffix.lower(),
                            "original_path": str(path),
                            "snapshot_path": str(snapshot_path),
                            "snapshot_strategy": "content_addressed_copy",
                        },
                    )
                )
        return documents
