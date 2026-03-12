from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable, Sequence
from pathlib import Path
from shutil import copy2
from typing import Any, TypeVar

import pandas as pd
from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_jsonl(path: Path, rows: Iterable[BaseModel | dict[str, Any]]) -> None:
    ensure_directory(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            payload = row.model_dump(mode="json") if isinstance(row, BaseModel) else row
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            loaded = json.loads(stripped)
            if not isinstance(loaded, dict):
                raise TypeError(f"Expected object rows in {path}")
            rows.append(loaded)
    return rows


def write_parquet(path: Path, rows: Sequence[BaseModel | dict[str, Any]]) -> None:
    ensure_directory(path.parent)
    payloads = [row.model_dump(mode="json") if isinstance(row, BaseModel) else row for row in rows]
    frame = pd.DataFrame(payloads)
    frame.to_parquet(path, index=False)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def materialize_raw_copy(source_path: Path, raw_dir: Path, namespace: str) -> Path:
    checksum = sha256_file(source_path)
    target_dir = ensure_directory(raw_dir / namespace / checksum[:2])
    safe_suffix = re.sub(r"[^A-Za-z0-9.]+", "", source_path.suffix.lower())
    destination = target_dir / f"{checksum}{safe_suffix}"
    if not destination.exists():
        copy2(source_path, destination)
    return destination
