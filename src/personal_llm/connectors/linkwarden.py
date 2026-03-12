from __future__ import annotations

from pathlib import Path
from typing import Any

from personal_llm.config.settings import AppSettings
from personal_llm.core.io import materialize_raw_copy, sha256_file
from personal_llm.core.schemas import SourceDocument, SourceType


class LinkwardenConnector:
    def discover(
        self,
        settings: AppSettings,
        raw_dir: Path,
        connector_config: dict[str, Any],
    ) -> list[SourceDocument]:
        export_path = connector_config.get("export_path")
        if not isinstance(export_path, str):
            return []
        path = settings.resolve(export_path)
        if not path.exists():
            return []
        snapshot_path = materialize_raw_copy(path, raw_dir, "linkwarden")
        return [
            SourceDocument(
                id=f"linkwarden::{path.as_posix()}",
                source_type=SourceType.LINKWARDEN_EXPORT,
                uri=path.as_uri(),
                title=path.name,
                content_path=str(snapshot_path),
                checksum=sha256_file(path),
                metadata={
                    "format": path.suffix.lower().lstrip("."),
                    "original_path": str(path),
                    "snapshot_path": str(snapshot_path),
                    "snapshot_strategy": "content_addressed_copy",
                },
            )
        ]
