from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PERSONAL_LLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    home: Path = Field(default=Path("."))
    config_dir: Path = Field(default=Path("config"))
    data_dir: Path = Field(default=Path("data"))
    vector_backend: str = Field(default="chroma")
    model_backend: str = Field(default="auto")
    model_profile: str = Field(default="qwen2.5-7b-instruct")
    guardrail_profile: str = Field(default="standard")
    embedding_provider: str = Field(default="hash")
    chroma_path: Path = Field(default=Path("data/processed/chroma"))
    qdrant_url: str = Field(default="http://127.0.0.1:6333")
    ollama_url: str = Field(default="http://127.0.0.1:11434")
    google_drive_client_secret: Path = Field(default=Path("secrets/google-client-secret.json"))
    google_drive_token: Path = Field(default=Path("secrets/google-drive-token.json"))
    imap_host: str | None = None
    imap_port: int = 993
    imap_username: str | None = None
    imap_password: str | None = None
    runpod_api_key: str | None = None
    runpod_template_id: str | None = None
    remote_bucket: str | None = None
    log_level: str = "INFO"
    host: str = "127.0.0.1"
    port: int = 8000

    def resolve(self, path: Path | str) -> Path:
        candidate = Path(path)
        if candidate.is_absolute():
            return candidate
        return (self.home / candidate).resolve()

    def load_yaml(self, relative_path: str | Path) -> dict[str, Any]:
        target = self.resolve(relative_path)
        with target.open("r", encoding="utf-8") as handle:
            loaded = yaml.safe_load(handle) or {}
        if not isinstance(loaded, dict):
            raise TypeError(f"Expected dict in {target}")
        return loaded


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()
