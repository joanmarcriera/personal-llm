from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from personal_llm.config.settings import AppSettings
from personal_llm.core.schemas import ChunkRecord, EmbeddingRecord, coerce_classification_label


class VectorStore(Protocol):
    def bootstrap(self) -> None: ...

    def upsert(self, embeddings: list[EmbeddingRecord]) -> None: ...

    def search(
        self, query_vector: list[float], top_k: int, metadata_filters: dict[str, Any]
    ) -> list[ChunkRecord]: ...

    def reset(self) -> None: ...


@dataclass(slots=True)
class InMemoryVectorStore:
    records: dict[str, EmbeddingRecord] = field(default_factory=dict)
    chunks: dict[str, ChunkRecord] = field(default_factory=dict)

    def bootstrap(self) -> None:
        return None

    def upsert(self, embeddings: list[EmbeddingRecord]) -> None:
        for record in embeddings:
            self.records[record.chunk_id] = record
            self.chunks[record.chunk_id] = ChunkRecord(
                id=record.chunk_id,
                document_id=record.metadata.get("document_id", record.chunk_id),
                source_id=record.metadata.get("source_id", "unknown"),
                chunk_index=int(record.metadata.get("chunk_index", 0)),
                text=str(record.metadata.get("text", "")),
                token_estimate=int(record.metadata.get("token_estimate", 0)),
                metadata=record.metadata,
                domains=record.domains,
                classification_label=coerce_classification_label(
                    record.metadata.get("classification_label")
                ),
            )

    def search(
        self, query_vector: list[float], top_k: int, metadata_filters: dict[str, Any]
    ) -> list[ChunkRecord]:
        scored: list[tuple[float, ChunkRecord]] = []
        for chunk_id, record in self.records.items():
            score = self._cosine(query_vector, record.vector)
            chunk = self.chunks[chunk_id]
            if metadata_filters and not self._matches(chunk.metadata, metadata_filters):
                continue
            scored.append((score, chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in scored[:top_k]]

    def reset(self) -> None:
        self.records.clear()
        self.chunks.clear()

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        limit = min(len(a), len(b))
        dot = sum(a[index] * b[index] for index in range(limit))
        a_norm = sum(value * value for value in a[:limit]) ** 0.5 or 1.0
        b_norm = sum(value * value for value in b[:limit]) ** 0.5 or 1.0
        return dot / (a_norm * b_norm)

    @staticmethod
    def _matches(metadata: dict[str, Any], filters: dict[str, Any]) -> bool:
        for key, value in filters.items():
            if metadata.get(key) != value:
                return False
        return True


def build_vector_store(settings: AppSettings) -> VectorStore:
    if settings.vector_backend == "chroma":
        from personal_llm.vector_db.chroma_adapter import ChromaVectorStore

        return ChromaVectorStore(settings=settings)
    if settings.vector_backend == "qdrant":
        from personal_llm.vector_db.qdrant_adapter import QdrantVectorStore

        return QdrantVectorStore(settings=settings)
    return InMemoryVectorStore()
