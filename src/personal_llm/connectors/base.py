from __future__ import annotations

from pathlib import Path
from typing import Protocol

from personal_llm.config.settings import AppSettings
from personal_llm.core.schemas import SourceDocument


class SourceConnector(Protocol):
    def discover(self, settings: AppSettings, raw_dir: Path, connector_config: dict[str, object]) -> list[SourceDocument]:
        ...

