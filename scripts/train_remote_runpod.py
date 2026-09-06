#!/usr/bin/env python3
from __future__ import annotations

import json
import sys

from personal_llm.config.settings import get_settings
from personal_llm.training.runpod import RunPodTrainingManager


def main() -> None:
    settings = get_settings()
    manager = RunPodTrainingManager(settings=settings)
    result = manager.run(
        config_path=settings.resolve("config/training.yaml"), dataset_path=None, submit=False
    )
    sys.stdout.write(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
