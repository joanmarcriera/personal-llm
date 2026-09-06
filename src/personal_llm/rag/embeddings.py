from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass

import httpx

from personal_llm.config.settings import AppSettings
from personal_llm.core.schemas import ChunkRecord, EmbeddingRecord


@dataclass(slots=True)
class EmbeddingService:
    settings: AppSettings
    default_dimensions: int = 128

    def embed_chunks(self, chunks: Sequence[ChunkRecord]) -> list[EmbeddingRecord]:
        vectors = self.embed_texts([chunk.text for chunk in chunks])
        return [
            EmbeddingRecord(
                chunk_id=chunk.id,
                vector=vector,
                model_name=f"{self.settings.embedding_provider}-embedding",
                metadata=chunk.metadata
                | {
                    "source_id": chunk.source_id,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "token_estimate": chunk.token_estimate,
                    "classification_label": chunk.classification_label,
                    "text": chunk.text,
                },
                domains=chunk.domains,
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        provider = self.settings.embedding_provider
        if provider == "ollama":
            return self._embed_via_ollama(texts)
        return [self._hash_embedding(text) for text in texts]

    def _hash_embedding(self, text: str) -> list[float]:
        dimensions = self.default_dimensions
        vector = [0.0] * dimensions
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = digest[0] % dimensions
            value = (int.from_bytes(digest[1:3], "big") / 65535.0) * 2 - 1
            vector[index] += value
        norm = sum(component * component for component in vector) ** 0.5 or 1.0
        return [component / norm for component in vector]

    def _embed_via_ollama(self, texts: Sequence[str]) -> list[list[float]]:
        client = httpx.Client(base_url=self.settings.ollama_url, timeout=60.0)
        vectors: list[list[float]] = []
        for text in texts:
            response = client.post(
                "/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": text},
            )
            response.raise_for_status()
            payload = response.json()
            embedding = payload.get("embedding", [])
            if not isinstance(embedding, list):
                raise TypeError("Expected list embedding from Ollama")
            vectors.append([float(value) for value in embedding])
        return vectors
