from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

from personal_llm.core.schemas import DomainClassification


class DomainClassifier:
    def __init__(self, taxonomy_path: Path) -> None:
        self.taxonomy_path = taxonomy_path
        with taxonomy_path.open("r", encoding="utf-8") as handle:
            taxonomy = yaml.safe_load(handle) or {}
        if not isinstance(taxonomy, dict):
            raise TypeError(f"Expected dict in {taxonomy_path}")
        self.allowed_domains = taxonomy.get("allowed_domains", {})
        self.disallowed_domains = taxonomy.get("disallowed_domains", {})
        self.mixed_threshold = float(taxonomy.get("mixed_domain_threshold", 0.15))
        self.disallowed_multiplier = float(taxonomy.get("disallowed_priority_multiplier", 1.4))

    def classify_text(self, text: str) -> DomainClassification:
        haystack = text.lower()
        allowed_scores = self._score_groups(haystack, self.allowed_domains)
        disallowed_scores = self._score_groups(haystack, self.disallowed_domains)
        allowed_total = sum(allowed_scores.values())
        disallowed_total = sum(disallowed_scores.values()) * self.disallowed_multiplier
        allowed_ranked = sorted(allowed_scores.items(), key=lambda item: item[1], reverse=True)
        disallowed_ranked = sorted(
            disallowed_scores.items(), key=lambda item: item[1], reverse=True
        )

        if disallowed_total > 0 and disallowed_total >= max(allowed_total, 0.01):
            label = "disallowed"
        elif (
            allowed_total > 0
            and disallowed_total > 0
            and min(allowed_total, disallowed_total) / max(allowed_total, disallowed_total)
            >= self.mixed_threshold
        ):
            label = "mixed"
        elif allowed_total > 0:
            label = "allowed"
        else:
            label = "mixed"

        return DomainClassification(
            label=label,
            allowed_scores=dict(allowed_scores),
            disallowed_scores=dict(disallowed_scores),
            primary_allowed=[name for name, score in allowed_ranked[:3] if score > 0],
            primary_disallowed=[name for name, score in disallowed_ranked[:3] if score > 0],
        )

    @staticmethod
    def _score_groups(text: str, groups: dict[str, Any]) -> dict[str, float]:
        scores: dict[str, float] = defaultdict(float)
        for group_name, payload in groups.items():
            if not isinstance(payload, dict):
                continue
            keywords = payload.get("keywords", [])
            if not isinstance(keywords, list):
                continue
            for keyword in keywords:
                if not isinstance(keyword, str):
                    continue
                if keyword.lower() in text:
                    scores[group_name] += 1.0
        return scores
