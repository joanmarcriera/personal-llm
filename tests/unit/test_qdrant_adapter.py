from __future__ import annotations

from personal_llm.config.settings import get_settings
from personal_llm.core.schemas import EmbeddingRecord
from personal_llm.vector_db.qdrant_adapter import QdrantVectorStore


def test_qdrant_point_id_is_stable_for_same_chunk_id() -> None:
    chunk_id = "doc::sample::chunk::0"

    first = QdrantVectorStore._point_id(chunk_id)
    second = QdrantVectorStore._point_id(chunk_id)

    assert first == second


def test_qdrant_point_id_differs_for_different_chunk_ids() -> None:
    first = QdrantVectorStore._point_id("doc::sample::chunk::0")
    second = QdrantVectorStore._point_id("doc::sample::chunk::1")

    assert first != second


def test_qdrant_upsert_uses_chunk_derived_point_ids() -> None:
    class FakeClient:
        def __init__(self) -> None:
            self.collection_name: str | None = None
            self.points: list[object] = []

        def upsert(self, *, collection_name: str, points: list[object]) -> None:
            self.collection_name = collection_name
            self.points = points

    store = QdrantVectorStore(settings=get_settings())
    fake_client = FakeClient()
    store.client = fake_client
    embeddings = [
        EmbeddingRecord(chunk_id="doc::alpha::chunk::0", vector=[0.1, 0.2], model_name="test"),
        EmbeddingRecord(chunk_id="doc::beta::chunk::0", vector=[0.3, 0.4], model_name="test"),
    ]

    store.upsert(embeddings)

    assert fake_client.collection_name == store.collection_name
    assert [point.id for point in fake_client.points] == [
        QdrantVectorStore._point_id("doc::alpha::chunk::0"),
        QdrantVectorStore._point_id("doc::beta::chunk::0"),
    ]
