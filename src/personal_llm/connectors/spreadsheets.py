from __future__ import annotations

from pathlib import Path

from personal_llm.config.settings import AppSettings
from personal_llm.core.io import materialize_raw_copy, sha256_file
from personal_llm.core.schemas import SourceDocument, SourceType


class SpreadsheetConnector:
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
        for item in paths:
            if not isinstance(item, str):
                continue
            root = settings.resolve(item)
            for path in root.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in {".xlsx", ".csv"}:
                    continue
                snapshot_path = materialize_raw_copy(path, raw_dir, "spreadsheets")
                documents.append(
                    SourceDocument(
                        id=f"sheet::{path.as_posix()}",
                        source_type=SourceType.SPREADSHEET,
                        uri=path.as_uri(),
                        title=path.name,
                        content_path=str(snapshot_path),
                        checksum=sha256_file(path),
                        metadata={
                            "extension": path.suffix.lower(),
                            "original_path": str(path),
                            "snapshot_path": str(snapshot_path),
                            "snapshot_strategy": "content_addressed_copy",
                        },
                    )
                )
        return documents
