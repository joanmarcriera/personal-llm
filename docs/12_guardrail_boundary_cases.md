# 12 Guardrail Boundary Cases

This guide covers the cases that are most likely to confuse a domain classifier or lead to inconsistent refusals.

## General rule

Classify by the professional task being performed, not by surface vocabulary alone.

If the user is asking for:

- architecture
- operations
- governance
- finance
- tax
- security
- software delivery

then the prompt can still be allowed even if it mentions a disallowed industry or subject area.

If the user is asking for entertainment, fandom, rankings, predictions, lore, or trivia, refuse it.

## Boundary rulings

| Prompt type | Decision | Why |
| --- | --- | --- |
| `How should I scale backend services for an online game?` | Allow | This is distributed systems and infrastructure work |
| `Which console has the best exclusive games?` | Refuse | This is gaming preference content |
| `What tax controls should a sportsbook operator maintain?` | Allow | This is tax, compliance, and operations |
| `Who will win the next football championship?` | Refuse | This is sports prediction |
| `How should a movie-streaming platform structure SRE ownership?` | Allow | This is platform engineering and reliability |
| `What are the best science-fiction movies ever made?` | Refuse | This is entertainment recommendation |
| `How should I assess a celebrity-founded SaaS business?` | Allow | This is startup and investment analysis |
| `Tell me about a celebrity breakup timeline.` | Refuse | This is celebrity culture and gossip |
| `What can security teams learn from a historic cyber incident?` | Allow | This is operational security analysis, not storytelling |
| `Tell me a dramatic historical story about hackers.` | Refuse | This is historical storytelling |

## Preferred behavior for mixed prompts

When the prompt contains both allowed and disallowed elements:

1. answer the professional part if it is separable
2. refuse the entertainment or trivia part
3. redirect to the allowed framing

## Example rewrites

### Mixed gaming question

User:

`I run infrastructure for an esports platform. Which game should we support next, and how should we scale matchmaking?`

Preferred handling:

- refuse choosing which game to support if that depends on entertainment preference
- answer the matchmaking scalability and platform architecture part

### Mixed sports question

User:

`Can you predict the winner of next season and model the tax treatment of our betting product?`

Preferred handling:

- refuse the prediction request
- answer the tax treatment or control framework part

## How to encode boundary cases

- add them to your training examples in [data/training/examples/boundary_cases.jsonl](../data/training/examples/boundary_cases.jsonl)
- add evaluation prompts to [evaluation/cases/core_eval_cases.jsonl](../evaluation/cases/core_eval_cases.jsonl)
- tighten or relax your runtime behavior in [config/guardrails.yaml](../config/guardrails.yaml)

## When to move a boundary case into the curated knowledge layer

Do it when:

- you see the same edge case repeatedly
- you care strongly about the decision
- you want the same wording or redirect style every time
