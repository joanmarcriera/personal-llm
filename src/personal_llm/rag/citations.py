from __future__ import annotations

from personal_llm.core.schemas import ChunkRecord


def format_citations(chunks: list[ChunkRecord]) -> str:
    lines = []
    for chunk in chunks:
        title = str(chunk.metadata.get("title") or chunk.source_id)
        lines.append(f"[{chunk.chunk_index + 1}] {title} ({chunk.source_id})")
    return "\n".join(lines)
