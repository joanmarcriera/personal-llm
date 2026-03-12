from __future__ import annotations

from pathlib import Path

from personal_llm.config.settings import AppSettings
from personal_llm.core.io import materialize_raw_copy, sha256_file
from personal_llm.core.schemas import SourceDocument, SourceType


class LocalFilesConnector:
    def discover(
        self,
        settings: AppSettings,
        raw_dir: Path,
        connector_config: dict[str, object],
    ) -> list[SourceDocument]:
        include_extensions = {
            ext.lower()
            for ext in connector_config.get("include_extensions", [])
            if isinstance(ext, str)
        }
        paths = connector_config.get("paths", [])
        if not isinstance(paths, list):
            return []
        documents: list[SourceDocument] = []
        for candidate in paths:
            if not isinstance(candidate, str):
                continue
            root = settings.resolve(candidate)
            if root.is_file():
                files = [root]
            else:
                files = [path for path in root.rglob("*") if path.is_file()]
            for path in files:
                if include_extensions and path.suffix.lower() not in include_extensions:
                    continue
                snapshot_path = materialize_raw_copy(path, raw_dir, "local_files")
                documents.append(
                    SourceDocument(
                        id=f"local::{path.as_posix()}",
                        source_type=SourceType.LOCAL_FILE,
                        uri=path.as_uri(),
                        title=path.name,
                        content_path=str(snapshot_path),
                        checksum=sha256_file(path),
                        metadata={
                            "extension": path.suffix.lower(),
                            "original_path": str(path),
                            "snapshot_path": str(snapshot_path),
                            "snapshot_strategy": "content_addressed_copy",
                            "file_size_bytes": path.stat().st_size,
                            "source_modified_at": path.stat().st_mtime,
                        },
                    )
                )
        return documents
