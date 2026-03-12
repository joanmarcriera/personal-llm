# Prompts

Prompt assets in this directory are consumed by the runtime prompt loader in [src/personal_llm/prompts/loader.py](../src/personal_llm/prompts/loader.py).

## How these files are used

- `system_professional.md`: default guarded system prompt
- `system_professional_strict.md`: stronger professional-only behavior
- `system_professional_relaxed.md`: softer mixed-topic handling
- `system_original_model.md`: minimal repository steering
- `refusal_redirect.md`: default refusal and redirect wording
- `refusal_redirect_relaxed.md`: softer refusal wording
- `refusal_disabled.md`: near-original-model mode
- `legal_finance_disclaimer.md`: reusable caution text for regulated domains
- `topic_router.md`: topic-classification support prompt

## Relationship to the persona file

The user-facing voice should start in [knowledge/persona.md](../knowledge/persona.md), then be translated here into runtime prompts.

Best practice:

1. define the voice in `knowledge/persona.md`
2. keep these prompt files aligned with that voice
3. create SFT examples that reinforce the same behavior
4. compare prompt-only behavior against LoRA behavior during evaluation
