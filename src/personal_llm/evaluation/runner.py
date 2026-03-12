from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from personal_llm.config.settings import AppSettings
from personal_llm.core.io import read_jsonl, write_jsonl
from personal_llm.core.policy import PolicyEngine
from personal_llm.core.schemas import EvalCase, EvaluationResult
from personal_llm.evaluation.scorers import score_case
from personal_llm.models.registry import ModelRegistry
from personal_llm.prompts.loader import PromptLibrary


@dataclass(slots=True)
class EvaluationRunner:
    settings: AppSettings
    policy: PolicyEngine = field(init=False)
    prompts: PromptLibrary = field(init=False)
    registry: ModelRegistry = field(init=False)

    def __post_init__(self) -> None:
        self.policy = PolicyEngine(self.settings)
        self.prompts = PromptLibrary(self.settings)
        self.registry = ModelRegistry(self.settings)

    def run(self, cases_path: Path | None = None) -> EvaluationResult:
        target = self.settings.resolve(cases_path or Path("data/training/example_eval.jsonl"))
        cases = [EvalCase.model_validate(row) for row in read_jsonl(target)]
        backend = self.registry.build_backend()
        details: list[dict[str, object]] = []
        passed = 0
        restriction_hits = 0
        citations = 0
        hallucination_total = 0.0
        domain_alignment_total = 0.0
        for case in cases:
            decision = self.policy.route_query(case.prompt)
            refused = not decision.allow
            if refused:
                answer = self.policy.refusal_message()
            else:
                answer = backend.generate(self.prompts.system_prompt(), case.prompt)
            score = score_case(case, answer, refused)
            passed += int(score.passed)
            restriction_hits += int(score.restriction_compliant)
            citations += int(score.cited)
            hallucination_total += score.hallucination_proxy
            domain_alignment_total += score.domain_alignment
            details.append(
                {
                    "id": case.id,
                    "expected_behavior": case.expected_behavior,
                    "refused": refused,
                    "passed": score.passed,
                    "cited": score.cited,
                }
            )
        result = EvaluationResult(
            total_cases=len(cases),
            passed_cases=passed,
            restriction_compliance=(restriction_hits / len(cases)) if cases else 0.0,
            citation_coverage=(citations / len(cases)) if cases else 0.0,
            hallucination_proxy=(hallucination_total / len(cases)) if cases else 0.0,
            domain_alignment=(domain_alignment_total / len(cases)) if cases else 0.0,
            details=details,
        )
        report_path = self.settings.resolve(Path("evaluation/reports/latest.json"))
        write_jsonl(report_path.with_suffix(".jsonl"), [result.model_dump(mode="json")])
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        return result
