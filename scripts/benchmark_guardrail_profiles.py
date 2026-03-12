from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from personal_llm.config.settings import AppSettings
from personal_llm.evaluation.runner import EvaluationRunner


@dataclass(slots=True)
class MatrixRow:
    guardrail_profile: str
    total_cases: int
    passed_cases: int
    pass_rate: float
    restriction_compliance: float
    citation_coverage: float
    hallucination_proxy: float
    domain_alignment: float
    failed_case_ids: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark guardrail profiles against one evaluation case file.")
    parser.add_argument("--model-profile", required=True, help="Model profile from config/models.yaml")
    parser.add_argument(
        "--cases",
        default="evaluation/cases/guardrail_profile_matrix.jsonl",
        help="Path to the evaluation cases JSONL file.",
    )
    parser.add_argument(
        "--profiles",
        nargs="+",
        default=["original_model", "relaxed", "standard", "strict"],
        help="Guardrail profiles to benchmark in order.",
    )
    parser.add_argument(
        "--output-prefix",
        default="evaluation/reports/guardrail_matrix",
        help="Output file prefix for JSON and Markdown reports.",
    )
    return parser.parse_args()


def markdown_table(rows: list[MatrixRow], model_profile: str, cases_path: str) -> str:
    pass_rate_values = ", ".join(f"{row.pass_rate:.3f}" for row in rows)
    restriction_values = ", ".join(f"{row.restriction_compliance:.3f}" for row in rows)
    hallucination_values = ", ".join(f"{row.hallucination_proxy:.3f}" for row in rows)
    lines = [
        f"# Guardrail Matrix: {model_profile}",
        "",
        f"- Cases: `{cases_path}`",
        "",
        "```mermaid",
        "xychart-beta",
        '    title "Guardrail Profile Pass Rate"',
        '    x-axis ["' + '", "'.join(row.guardrail_profile for row in rows) + '"]',
        '    y-axis "Pass Rate" 0 --> 1',
        f"    bar [{pass_rate_values}]",
        "```",
        "",
        "```mermaid",
        "xychart-beta",
        '    title "Restriction Compliance vs Hallucination Proxy"',
        '    x-axis ["' + '", "'.join(row.guardrail_profile for row in rows) + '"]',
        '    y-axis "Score" 0 --> 1',
        f"    bar [{restriction_values}]",
        f"    line [{hallucination_values}]",
        "```",
        "",
        "| Profile | Pass Rate | Passed | Restriction | Citation | Hallucination Proxy | Domain Alignment | Failed Cases |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row.guardrail_profile} | "
            f"{row.pass_rate:.3f} | "
            f"{row.passed_cases}/{row.total_cases} | "
            f"{row.restriction_compliance:.3f} | "
            f"{row.citation_coverage:.3f} | "
            f"{row.hallucination_proxy:.3f} | "
            f"{row.domain_alignment:.3f} | "
            f"{', '.join(row.failed_case_ids) if row.failed_case_ids else '-'} |"
        )
    lines.extend(
        [
            "",
            "## How to read this",
            "",
            "- Use this matrix to compare guardrail behavior quickly.",
            "- Use the full `evaluation/cases/core_eval_cases.jsonl` suite only after you pick the best candidate profile.",
            "- `citation_coverage` and `hallucination_proxy` here are directional because the current scorer is intentionally lightweight.",
            "",
            "## Quick interpretation",
            "",
            "- Higher `Pass Rate`, `Restriction`, and `Domain Alignment` are better.",
            "- Lower `Hallucination Proxy` is better, but it can also improve simply because the model refused more often.",
            "- If `strict` lowers pass rate sharply, it is usually over-refusing mixed professional prompts.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    rows: list[MatrixRow] = []
    for guardrail_profile in args.profiles:
        settings = AppSettings(model_profile=args.model_profile, guardrail_profile=guardrail_profile)
        runner = EvaluationRunner(settings)
        result = runner.run(Path(args.cases))
        failed_case_ids = [str(item["id"]) for item in result.details if not bool(item["passed"])]
        rows.append(
            MatrixRow(
                guardrail_profile=guardrail_profile,
                total_cases=result.total_cases,
                passed_cases=result.passed_cases,
                pass_rate=(result.passed_cases / result.total_cases) if result.total_cases else 0.0,
                restriction_compliance=result.restriction_compliance,
                citation_coverage=result.citation_coverage,
                hallucination_proxy=result.hallucination_proxy,
                domain_alignment=result.domain_alignment,
                failed_case_ids=failed_case_ids,
            )
        )

    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = output_prefix.with_name(f"{output_prefix.name}_{args.model_profile}.json")
    markdown_path = output_prefix.with_name(f"{output_prefix.name}_{args.model_profile}.md")
    json_path.write_text(json.dumps([asdict(row) for row in rows], indent=2), encoding="utf-8")
    markdown_path.write_text(markdown_table(rows, args.model_profile, args.cases), encoding="utf-8")
    print(markdown_table(rows, args.model_profile, args.cases))
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {markdown_path}")


if __name__ == "__main__":
    main()
