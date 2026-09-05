from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from personal_llm.config.settings import AppSettings
from personal_llm.core.schemas import ChunkRecord
from personal_llm.rag.embeddings import EmbeddingService
from personal_llm.vector_db.base import VectorStore, build_vector_store


@dataclass(slots=True)
class Retriever:
    settings: AppSettings
    vector_store: VectorStore = field(init=False)
    embedding_service: EmbeddingService = field(init=False)

    def __post_init__(self) -> None:
        self.vector_store: VectorStore = build_vector_store(self.settings)
        self.embedding_service = EmbeddingService(self.settings)

    def retrieve(
        self,
        query: str,
        top_k: int = 6,
        metadata_filters: dict[str, Any] | None = None,
    ) -> list[ChunkRecord]:
        query_vector = self.embedding_service.embed_texts([query])[0]
        return self.vector_store.search(
            query_vector, top_k=top_k, metadata_filters=metadata_filters or {}
        )
