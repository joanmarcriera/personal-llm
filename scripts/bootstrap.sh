#!/usr/bin/env bash
set -euo pipefail

uv sync --extra local --extra dev
uv run pre-commit install

