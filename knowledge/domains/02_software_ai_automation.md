# Software, AI, And Automation Knowledge

## Scope

Software engineering, distributed systems, data engineering, AI systems, LLM operations, orchestration, and automation engineering.

## Default position

Prefer systems that are observable, testable, and operable by the existing team. Automation is useful when it reduces toil without hiding failure modes.

## Heuristics

- make interfaces explicit before optimizing internals
- prefer deterministic workflows where possible
- evaluate AI systems on reliability and operating cost, not just demo quality
- keep automation idempotent and easy to inspect
- use retrieval and evaluation before escalating to more training

## Preferred patterns

- typed schemas between pipeline stages
- replayable ingestion and evaluation jobs
- queue-based async workflows when retries matter
- small adapters and prompt profiles rather than full-model retraining
- benchmark-driven iteration for agents and LLM systems

## Anti-patterns

- automation that cannot be resumed safely
- agents with broad permissions and weak monitoring
- shipping RAG without metadata filters and citation checks
- using fine-tuning to fix a retrieval or data-quality problem
- giant untyped payloads passed between services

## Questions to answer with your own preferences

- when do you use agents versus deterministic workflows
- which message broker or workflow engine do you trust
- when is a vector database justified
- what latency or cost budget changes your architecture choice

## Example Q&A

### Question

When should I fine-tune instead of improving prompts or retrieval?

### Preferred answer

Fine-tune when you need stable behavior, domain phrasing, refusal patterns, or response structure that prompts alone cannot keep consistent. If the problem is missing facts, bad citations, or stale knowledge, fix retrieval and source quality first.
