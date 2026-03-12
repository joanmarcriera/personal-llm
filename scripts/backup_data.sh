#!/usr/bin/env bash
set -euo pipefail

timestamp="$(date +%Y%m%d-%H%M%S)"
mkdir -p backups
tar -czf "backups/personal-llm-${timestamp}.tar.gz" config prompts data/training evaluation

