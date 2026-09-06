from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection

from personal_llm.config.settings import AppSettings
from personal_llm.core.schemas import ChunkRecord, EmbeddingRecord, coerce_classification_label


def _as_int(value: object, default: int = 0) -> int:
    return int(value) if isinstance(value, int | float | str) else default


@dataclass(slots=True)
class ChromaVectorStore:
    settings: AppSettings
    client: ClientAPI = field(init=False)
    collection: Collection = field(init=False)

    def __post_init__(self) -> None:
        self.client = chromadb.PersistentClient(
            path=str(self.settings.resolve(self.settings.chroma_path))
        )
        self.collection = self.client.get_or_create_collection("personal-llm")

    def bootstrap(self) -> None:
        self.collection = self.client.get_or_create_collection("personal-llm")

    def upsert(self, embeddings: list[EmbeddingRecord]) -> None:
        ids = [record.chunk_id for record in embeddings]
        documents = [str(record.metadata.get("text", "")) for record in embeddings]
        # Metadata values come from arbitrary source-document metadata, so their shape
        # can't be pinned to Chroma's narrow Metadata value union statically.
        metadatas: Any = [
            record.metadata | {"domains": ",".join(record.domains)} for record in embeddings
        ]
        vectors: list[Sequence[float] | Sequence[int]] = [record.vector for record in embeddings]
        self.collection.upsert(
            ids=ids, embeddings=vectors, documents=documents, metadatas=metadatas
        )

    def search(
        self, query_vector: list[float], top_k: int, metadata_filters: dict[str, Any]
    ) -> list[ChunkRecord]:
        where = metadata_filters or None
        query_embeddings: list[Sequence[float] | Sequence[int]] = [query_vector]
        result = self.collection.query(
            query_embeddings=query_embeddings, n_results=top_k, where=where
        )
        chunks: list[ChunkRecord] = []
        ids = (result.get("ids") or [[]])[0]
        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        for chunk_id, document, metadata in zip(ids, documents, metadatas, strict=True):
            if not isinstance(metadata, dict):
                metadata = {}
            chunks.append(
                ChunkRecord(
                    id=str(chunk_id),
                    document_id=str(metadata.get("document_id", chunk_id)),
                    source_id=str(metadata.get("source_id", "unknown")),
                    chunk_index=_as_int(metadata.get("chunk_index")),
                    text=str(document),
                    token_estimate=_as_int(metadata.get("token_estimate")),
                    metadata=metadata,
                    domains=str(metadata.get("domains", "")).split(",")
                    if metadata.get("domains")
                    else [],
                    classification_label=coerce_classification_label(
                        metadata.get("classification_label")
                    ),
                )
            )
        return chunks

    def reset(self) -> None:
        try:
            self.client.delete_collection("personal-llm")
        except Exception:
            return None
        self.collection = self.client.get_or_create_collection("personal-llm")
