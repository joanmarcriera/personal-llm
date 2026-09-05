from __future__ import annotations

import re
from dataclasses import dataclass

from datasketch import MinHash

from personal_llm.core.schemas import ExtractedDocument

TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_]+")


@dataclass(slots=True)
class DuplicateDetector:
    near_duplicate_threshold: float = 0.92

    def filter_documents(self, documents: list[ExtractedDocument]) -> list[ExtractedDocument]:
        seen_checksums: set[str] = set()
        accepted: list[ExtractedDocument] = []
        signatures: list[tuple[ExtractedDocument, MinHash]] = []
        for document in documents:
            if document.checksum in seen_checksums:
                continue
            signature = self._signature(document.text)
            if any(
                signature.jaccard(existing) >= self.near_duplicate_threshold
                for _, existing in signatures
            ):
                continue
            seen_checksums.add(document.checksum)
            accepted.append(document)
            signatures.append((document, signature))
        return accepted

    def _signature(self, text: str) -> MinHash:
        minhash = MinHash(num_perm=64)
        for token in TOKEN_PATTERN.findall(text.lower()):
            minhash.update(token.encode("utf-8"))
        return minhash
