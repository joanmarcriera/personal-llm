#!/usr/bin/env bash
set -euo pipefail

if ! command -v mmdc >/dev/null 2>&1; then
  echo "mmdc not found. Install @mermaid-js/mermaid-cli to export diagrams."
  exit 1
fi

for source in architecture/*.mmd; do
  target="${source%.mmd}.svg"
  mmdc -i "$source" -o "$target"
done

