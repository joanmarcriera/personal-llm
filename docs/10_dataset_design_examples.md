# 10 Dataset Design Examples

This guide shows what good training data looks like for this repository.

## Purpose

The model quality will depend far more on the quality of the instruction pairs than on the volume of random source text. Good examples teach:

- domain focus
- your preferred reasoning style
- refusal behavior
- regulated-domain caution
- how to use retrieved evidence without hallucinating

## Training example schema

The starter JSONL files use this structure:

```json
{
  "id": "sft::1",
  "system": "You are a professional-domain assistant.",
  "user": "Explain how OIDC and SCIM complement each other in platform identity management.",
  "assistant": "OIDC handles user authentication...",
  "allowed_domains": ["identity_management", "platform_engineering"],
  "refusal": false,
  "source_chunk_ids": ["doc::sample-1::chunk::0"],
  "metadata": {"jurisdiction": "global"}
}
```

## What makes a good example

- the question is realistic
- the answer is domain-specific rather than generic
- the answer reflects your persona and operating style
- the answer either cites source chunks or clearly stands on curated knowledge
- the answer does not wander into disallowed topics

## What makes a bad example

- vague educational prompts with no real professional context
- answers that repeat raw documents verbatim
- answers that sound like generic AI filler
- training pairs that mix policy, persona, and factual grounding without clear intent

## Example groups

The repository now includes concrete files under [data/training/examples/README.md](../data/training/examples/README.md):

- `sft_domain_examples.jsonl`
- `refusal_examples.jsonl`
- `boundary_cases.jsonl`

## Design pattern 1: core professional answer

Use when the model should learn your default framing and structure.

Good characteristics:

- answer starts with the recommendation
- tradeoffs are explicit
- implementation steps are concrete

## Design pattern 2: regulated-domain caution

Use when the model should help without pretending to be a licensed adviser.

Good characteristics:

- assumptions are called out
- the answer identifies verification steps
- the answer avoids false certainty

## Design pattern 3: refusal and redirect

Use when you want the model to decline off-topic requests politely and then redirect toward a professional angle.

Good characteristics:

- short refusal
- no direct answer to the disallowed topic
- optional redirect to an allowed framing

## Design pattern 4: boundary case

Use when the wording includes a disallowed domain but the real task is still professional.

Examples:

- gaming infrastructure
- sports betting tax treatment
- streaming-platform reliability

Train the model on these cases explicitly. Boundary handling is where generic classifiers usually make mistakes.

## Design pattern 5: RAG-grounded answer

Use when the answer should reflect internal documents rather than only general knowledge.

Good characteristics:

- `source_chunk_ids` are present
- the answer stays close to the retrieved evidence
- the answer summarizes or synthesizes rather than copying raw text

## Suggested dataset mix for a first adapter

- `55-65%` core professional Q&A
- `10-15%` regulated-domain caution examples
- `10-15%` RAG-grounded synthesis examples
- `10-15%` refusal and boundary examples

Use the lower end of refusal-heavy examples if you want a less restrictive assistant.

## Relationship to the knowledge layer

Use [knowledge/persona.md](../knowledge/persona.md) and the files listed in [knowledge/domains/README.md](../knowledge/domains/README.md) as the main source for:

- the way answers should sound
- your default architectural or financial positions
- stable heuristics worth encoding into LoRA

Use raw corpora mainly for:

- citations
- retrieval
- document-specific synthesis

## Review checklist before training

- does each example teach one clear behavior
- are the answers written in the style you want long-term
- do regulated-domain answers stay cautious enough
- do refusals avoid leaking the forbidden answer
- do boundary cases reflect your actual policy decisions

## Next steps

- write or refine [knowledge/persona.md](../knowledge/persona.md)
- fill in the domain files in [knowledge/domains/README.md](../knowledge/domains/README.md)
- compare your examples against [docs/12_guardrail_boundary_cases.md](12_guardrail_boundary_cases.md)
- validate the resulting model with [docs/07_evaluation.md](07_evaluation.md)
