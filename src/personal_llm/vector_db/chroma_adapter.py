from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import chromadb

from personal_llm.config.settings import AppSettings
from personal_llm.core.schemas import ChunkRecord, EmbeddingRecord


@dataclass(slots=True)
class ChromaVectorStore:
    settings: AppSettings
    client: chromadb.PersistentClient = field(init=False)
    collection: object = field(init=False)

    def __post_init__(self) -> None:
        self.client = chromadb.PersistentClient(path=str(self.settings.resolve(self.settings.chroma_path)))
        self.collection = self.client.get_or_create_collection("personal-llm")

    def bootstrap(self) -> None:
        self.collection = self.client.get_or_create_collection("personal-llm")

    def upsert(self, embeddings: list[EmbeddingRecord]) -> None:
        ids = [record.chunk_id for record in embeddings]
        documents = [str(record.metadata.get("text", "")) for record in embeddings]
        metadatas = [record.metadata | {"domains": ",".join(record.domains)} for record in embeddings]
        vectors = [record.vector for record in embeddings]
        self.collection.upsert(ids=ids, embeddings=vectors, documents=documents, metadatas=metadatas)

    def search(self, query_vector: list[float], top_k: int, metadata_filters: dict[str, Any]) -> list[ChunkRecord]:
        where = metadata_filters or None
        result = self.collection.query(query_embeddings=[query_vector], n_results=top_k, where=where)
        chunks: list[ChunkRecord] = []
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        for chunk_id, document, metadata in zip(ids, documents, metadatas, strict=True):
            if not isinstance(metadata, dict):
                metadata = {}
            chunks.append(
                ChunkRecord(
                    id=str(chunk_id),
                    document_id=str(metadata.get("document_id", chunk_id)),
                    source_id=str(metadata.get("source_id", "unknown")),
                    chunk_index=int(metadata.get("chunk_index", 0)),
                    text=str(document),
                    token_estimate=int(metadata.get("token_estimate", 0)),
                    metadata=metadata,
                    domains=str(metadata.get("domains", "")).split(",") if metadata.get("domains") else [],
                    classification_label=str(metadata.get("classification_label", "allowed")),
                )
            )
        return chunks

    def reset(self) -> None:
        try:
            self.client.delete_collection("personal-llm")
        except Exception:
            return None
        self.collection = self.client.get_or_create_collection("personal-llm")
