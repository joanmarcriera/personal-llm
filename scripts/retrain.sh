#!/usr/bin/env bash
set -euo pipefail

uv run personal-llm build-training-set
uv run personal-llm train-local-mlx --config config/training.yaml

