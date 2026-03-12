#!/usr/bin/env bash
set -euo pipefail

cd /workspace/personal-llm-job
python -m pip install --upgrade pip
python -m pip install axolotl peft transformers datasets
python -m axolotl.cli.train training.yaml

