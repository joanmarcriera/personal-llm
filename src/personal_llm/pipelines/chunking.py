from __future__ import annotations

from dataclasses import dataclass

from personal_llm.core.schemas import ChunkRecord, ExtractedDocument


@dataclass(slots=True)
class Chunker:
    chunk_size_chars: int = 1200
    overlap_chars: int = 120

    def chunk_document(self, document: ExtractedDocument) -> list[ChunkRecord]:
        text = document.text.strip()
        if not text:
            return []
        chunks: list[ChunkRecord] = []
        start = 0
        index = 0
        label = document.classification.label if document.classification else "mixed"
        domains = document.classification.primary_allowed if document.classification else []
        while start < len(text):
            end = min(len(text), start + self.chunk_size_chars)
            snippet = text[start:end].strip()
            if snippet:
                chunks.append(
                    ChunkRecord(
                        id=f"{document.id}::chunk::{index}",
                        document_id=document.id,
                        source_id=document.source_id,
                        chunk_index=index,
                        text=snippet,
                        token_estimate=max(1, len(snippet.split())),
                        metadata=document.metadata,
                        domains=domains,
                        classification_label=label,
                        sensitivity=document.sensitivity,
                    )
                )
            if end == len(text):
                break
            start = max(end - self.overlap_chars, start + 1)
            index += 1
        return chunks
