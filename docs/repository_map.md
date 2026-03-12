# Repository Map

This document mirrors the folder overview in the root README and is intended for contributors who need to understand how the code and operational assets are split.

- `src/personal_llm/`: Python implementation
- `config/`: environment-independent config
- `docs/`: user guides
- `site-docs/`: GitHub Pages build root that points back to the canonical markdown files
- `architecture/`: diagrams
- `knowledge/`: curated personal knowledge, persona, domain files, and knowledge snapshots tied to training runs
- `scripts/`: operational helpers
- `deployment/`: serving manifests
- `tests/`: fixtures and validation
- `data/`: managed data lifecycle paths
- `config/guardrails.yaml`: built-in guardrail profiles
- `data/training/examples/`: concrete SFT, refusal, and boundary-case training examples
- `evaluation/cases/`: benchmark cases for scripted and manual acceptance checks
