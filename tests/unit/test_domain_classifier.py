from __future__ import annotations

from pathlib import Path

from personal_llm.pipelines.domain_classifier import DomainClassifier


def test_classifier_marks_professional_text_as_allowed() -> None:
    classifier = DomainClassifier(Path("config/domain_taxonomy.yaml"))
    result = classifier.classify_text(
        "Terraform and OIDC reduce operational drift in cloud platforms."
    )
    assert result.label == "allowed"
    assert (
        "infrastructure" in result.primary_allowed
        or "identity_management" in result.primary_allowed
    )


def test_classifier_marks_sports_text_as_disallowed() -> None:
    classifier = DomainClassifier(Path("config/domain_taxonomy.yaml"))
    result = classifier.classify_text(
        "Who will win the football league and which striker will score most goals?"
    )
    assert result.label == "disallowed"
    assert "sports" in result.primary_disallowed
