from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MetricDelta:
    name: str
    before: float
    after: float
    delta: float
    higher_is_better: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare two evaluation report JSON files.")
    parser.add_argument("--before", required=True, help="Earlier evaluation report JSON")
    parser.add_argument("--after", required=True, help="Later evaluation report JSON")
    parser.add_argument(
        "--output-prefix",
        default="evaluation/reports/comparison",
        help="Output prefix for generated Markdown report.",
    )
    return parser.parse_args()


def load_report(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise TypeError(f"Expected object report in {path}")
    return loaded


def pass_rate(report: dict[str, Any]) -> float:
    total = int(report.get("total_cases", 0))
    passed = int(report.get("passed_cases", 0))
    return (passed / total) if total else 0.0


def case_pass_map(report: dict[str, Any]) -> dict[str, bool]:
    details = report.get("details", [])
    if not isinstance(details, list):
        raise TypeError("details must be a list")
    result: dict[str, bool] = {}
    for item in details:
        if not isinstance(item, dict):
            continue
        case_id = item.get("id")
        passed = item.get("passed")
        if isinstance(case_id, str) and isinstance(passed, bool):
            result[case_id] = passed
    return result


def build_deltas(before: dict[str, Any], after: dict[str, Any]) -> list[MetricDelta]:
    return [
        MetricDelta(
            "pass_rate",
            pass_rate(before),
            pass_rate(after),
            pass_rate(after) - pass_rate(before),
            True,
        ),
        MetricDelta(
            "restriction_compliance",
            float(before.get("restriction_compliance", 0.0)),
            float(after.get("restriction_compliance", 0.0)),
            float(after.get("restriction_compliance", 0.0))
            - float(before.get("restriction_compliance", 0.0)),
            True,
        ),
        MetricDelta(
            "citation_coverage",
            float(before.get("citation_coverage", 0.0)),
            float(after.get("citation_coverage", 0.0)),
            float(after.get("citation_coverage", 0.0))
            - float(before.get("citation_coverage", 0.0)),
            True,
        ),
        MetricDelta(
            "hallucination_proxy",
            float(before.get("hallucination_proxy", 0.0)),
            float(after.get("hallucination_proxy", 0.0)),
            float(after.get("hallucination_proxy", 0.0))
            - float(before.get("hallucination_proxy", 0.0)),
            False,
        ),
        MetricDelta(
            "domain_alignment",
            float(before.get("domain_alignment", 0.0)),
            float(after.get("domain_alignment", 0.0)),
            float(after.get("domain_alignment", 0.0)) - float(before.get("domain_alignment", 0.0)),
            True,
        ),
    ]


def build_case_sets(
    before: dict[str, Any], after: dict[str, Any]
) -> tuple[list[str], list[str], list[str]]:
    before_map = case_pass_map(before)
    after_map = case_pass_map(after)
    common_ids = sorted(set(before_map) & set(after_map))
    improved = [case_id for case_id in common_ids if not before_map[case_id] and after_map[case_id]]
    regressed = [
        case_id for case_id in common_ids if before_map[case_id] and not after_map[case_id]
    ]
    stable_failures = [
        case_id for case_id in common_ids if not before_map[case_id] and not after_map[case_id]
    ]
    return improved, regressed, stable_failures


def delta_word(delta: MetricDelta) -> str:
    if delta.delta == 0:
        return "flat"
    good_direction = delta.delta > 0 if delta.higher_is_better else delta.delta < 0
    return "improved" if good_direction else "worsened"


def render_markdown(
    before_path: Path,
    after_path: Path,
    deltas: list[MetricDelta],
    improved: list[str],
    regressed: list[str],
    stable_failures: list[str],
) -> str:
    metric_names = [
        '"Pass Rate"',
        '"Restriction"',
        '"Citation"',
        '"Hallucination Proxy"',
        '"Domain Alignment"',
    ]
    before_values = ", ".join(f"{delta.before:.3f}" for delta in deltas)
    after_values = ", ".join(f"{delta.after:.3f}" for delta in deltas)
    lines = [
        f"# Evaluation Comparison: {before_path.name} -> {after_path.name}",
        "",
        f"- Before: `{before_path}`",
        f"- After: `{after_path}`",
        "",
        "```mermaid",
        "xychart-beta",
        '    title "Before vs After Metrics"',
        "    x-axis [" + ", ".join(metric_names) + "]",
        '    y-axis "Score" 0 --> 1',
        f"    bar [{before_values}]",
        f"    bar [{after_values}]",
        "```",
        "",
        "```mermaid",
        "xychart-beta",
        '    title "Case Outcomes"',
        '    x-axis ["Improved", "Regressed", "Stable Failures"]',
        '    y-axis "Cases" 0 --> 10',
        f"    bar [{len(improved)}, {len(regressed)}, {len(stable_failures)}]",
        "```",
        "",
        "| Metric | Before | After | Delta | Direction |",
        "| --- | --- | --- | --- | --- |",
    ]
    for delta in deltas:
        lines.append(
            f"| {delta.name} | {delta.before:.3f} | {delta.after:.3f} | "
            f"{delta.delta:+.3f} | {delta_word(delta)} |"
        )
    lines.extend(
        [
            "",
            "## Case-level changes",
            "",
            f"- Improved cases: {', '.join(improved) if improved else '-'}",
            f"- Regressed cases: {', '.join(regressed) if regressed else '-'}",
            f"- Stable failures: {', '.join(stable_failures) if stable_failures else '-'}",
            "",
            "## Reading guide",
            "",
            "- A real improvement should raise `pass_rate` and preserve or improve "
            "`restriction_compliance`.",
            "- If `hallucination_proxy` drops only because the model refuses more, treat "
            "that as suspicious rather than automatically better.",
            "- Regressed cases matter more than average deltas when they are in "
            "hard-refusal or regulated-domain prompts.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    before_path = Path(args.before)
    after_path = Path(args.after)
    before = load_report(before_path)
    after = load_report(after_path)
    deltas = build_deltas(before, after)
    improved, regressed, stable_failures = build_case_sets(before, after)
    markdown = render_markdown(
        before_path, after_path, deltas, improved, regressed, stable_failures
    )
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    markdown_path = output_prefix.with_name(
        f"{output_prefix.name}_{before_path.stem}_vs_{after_path.stem}.md"
    )
    markdown_path.write_text(markdown, encoding="utf-8")
    print(markdown)
    print(f"Comparison report: {markdown_path}")


if __name__ == "__main__":
    main()
