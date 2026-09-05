from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from personal_llm.config.settings import AppSettings
from personal_llm.core.schemas import PolicyDecision
from personal_llm.pipelines.domain_classifier import DomainClassifier
from personal_llm.prompts.loader import PromptLibrary


@dataclass(slots=True)
class PolicyEngine:
    settings: AppSettings
    classifier: DomainClassifier = field(init=False)
    prompts: PromptLibrary = field(init=False)

    def __post_init__(self) -> None:
        self.classifier = DomainClassifier(
            self.settings.resolve(Path("config/domain_taxonomy.yaml"))
        )
        self.prompts = PromptLibrary(self.settings)

    def route_query(self, query: str) -> PolicyDecision:
        classification = self.classifier.classify_text(query)
        if not self.prompts.runtime_policy_enabled():
            return PolicyDecision(
                allow=True,
                reason="Runtime policy is disabled for the selected guardrail profile.",
                redirect_domains=[],
                classifier=classification,
            )
        if classification.label == "disallowed":
            return PolicyDecision(
                allow=False,
                reason="Query falls outside the approved professional-domain scope.",
                redirect_domains=[
                    "IT infrastructure",
                    "DevOps",
                    "finance and accounting",
                    "AI systems and agent orchestration",
                ],
                classifier=classification,
            )
        if classification.label == "mixed" and self.prompts.refuse_mixed_queries():
            return PolicyDecision(
                allow=False,
                reason=(
                    "Query mixes approved and disallowed topics under the "
                    "selected guardrail profile."
                ),
                redirect_domains=[
                    "IT infrastructure",
                    "DevOps",
                    "finance and accounting",
                    "AI systems and agent orchestration",
                ],
                classifier=classification,
            )
        return PolicyDecision(
            allow=True,
            reason="Query is within the approved professional-domain scope.",
            redirect_domains=[],
            classifier=classification,
        )

    def refusal_message(self) -> str:
        return self.prompts.refusal_prompt()
