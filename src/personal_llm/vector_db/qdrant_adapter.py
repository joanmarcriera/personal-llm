from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from personal_llm.config.settings import AppSettings
from personal_llm.core.schemas import ChunkRecord, EmbeddingRecord, coerce_classification_label


@dataclass(slots=True)
class QdrantVectorStore:
    settings: AppSettings
    collection_name: str = "personal-llm"
    client: QdrantClient = field(init=False)

    def __post_init__(self) -> None:
        self.client = QdrantClient(url=self.settings.qdrant_url)

    def bootstrap(self) -> None:
        if self.client.collection_exists(self.collection_name):
            return
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=qmodels.VectorParams(size=128, distance=qmodels.Distance.COSINE),
        )

    def upsert(self, embeddings: list[EmbeddingRecord]) -> None:
        points = [
            qmodels.PointStruct(
                id=self._point_id(record.chunk_id),
                vector=record.vector,
                payload={"chunk_id": record.chunk_id, **record.metadata, "domains": record.domains},
            )
            for record in embeddings
        ]
        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(
        self, query_vector: list[float], top_k: int, metadata_filters: dict[str, Any]
    ) -> list[ChunkRecord]:
        filter_obj = None
        if metadata_filters:
            filter_obj = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(key=key, match=qmodels.MatchValue(value=value))
                    for key, value in metadata_filters.items()
                ]
            )
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            query_filter=filter_obj,
        )
        chunks: list[ChunkRecord] = []
        for hit in response.points:
            payload = hit.payload or {}
            chunks.append(
                ChunkRecord(
                    id=str(payload.get("chunk_id", hit.id)),
                    document_id=str(payload.get("document_id", hit.id)),
                    source_id=str(payload.get("source_id", "unknown")),
                    chunk_index=int(payload.get("chunk_index", 0)),
                    text=str(payload.get("text", "")),
                    token_estimate=int(payload.get("token_estimate", 0)),
                    metadata=dict(payload),
                    domains=list(payload.get("domains", [])),
                    classification_label=coerce_classification_label(
                        payload.get("classification_label")
                    ),
                )
            )
        return chunks

    def reset(self) -> None:
        if self.client.collection_exists(self.collection_name):
            self.client.delete_collection(self.collection_name)
        self.bootstrap()

    @staticmethod
    def _point_id(chunk_id: str) -> str:
        return str(uuid5(NAMESPACE_URL, chunk_id))
