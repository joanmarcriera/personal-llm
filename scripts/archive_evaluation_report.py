from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Archive evaluation/reports/latest.json under a stable name."
    )
    parser.add_argument(
        "--label", required=True, help="Short label like baseline_3b_standard or post_lora_run_001"
    )
    parser.add_argument(
        "--source",
        default="evaluation/reports/latest.json",
        help="Path to the latest evaluation report JSON.",
    )
    parser.add_argument(
        "--output-dir",
        default="evaluation/reports",
        help="Directory where the archived report should be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = Path(args.source)
    if not source.exists():
        raise FileNotFoundError(f"Source report not found: {source}")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"{args.label}.json"
    shutil.copy2(source, target)
    print(f"Archived report: {target}")


if __name__ == "__main__":
    main()
