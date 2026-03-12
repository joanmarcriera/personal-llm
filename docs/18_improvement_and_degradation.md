# 18 Improvement And Degradation

Use this page to decide whether a change should be kept.

## Improvement checklist

Keep a change when most of these are true:

- hard-refusal cases did not regress
- mixed-domain professional prompts improved or stayed stable
- persona cases improved
- regulated-domain caution stayed stable or improved
- the average scores did not improve only because the model refused more

## Degradation checklist

Treat a change as a regression when any of these happen:

- the model starts answering sports, movie, gaming, or celebrity prompts directly
- mixed-domain professional prompts are now refused more often
- the assistant loses your preferred direct, practical style
- tax or finance answers become more confident without more evidence

## Common examples

### Good change

- before: `standard` profile fails `celebrity-saas` and `sports-sponsorship`
- after: same hard-refusal performance, but those boundary cases now pass

That is a real improvement.

See a real comparison file:

- [evaluation/reports/example_improvement_matrix_3b_original_vs_matrix_3b_standard.md](../evaluation/reports/example_improvement_matrix_3b_original_vs_matrix_3b_standard.md)

### Bad change

- before: `standard` passes all hard-refusal cases and fails four mixed-domain prompts
- after: `strict` still passes hard-refusal cases but now fails seven mixed-domain prompts

That is degradation by over-refusal.

See a real comparison file:

- [evaluation/reports/example_degradation_matrix_3b_standard_vs_matrix_3b_strict.md](../evaluation/reports/example_degradation_matrix_3b_standard_vs_matrix_3b_strict.md)

### Fake improvement

- before: the model answers many prompts without citations
- after: the model refuses more often, so `hallucination_proxy` drops

That may not be real improvement. It may only mean the model became less willing to answer.

## Best practice

Change one thing at a time:

- one guardrail profile
- one prompt change
- one small batch of new SFT examples

Then compare before and after. If you change many things at once, you will not know what helped.

## Recommended first comparison cycle

1. baseline with `qwen2.5-3b-instruct`
2. compare `standard` vs `strict` vs `relaxed`
3. keep the best profile
4. add a small targeted example batch
5. compare again
6. once the pattern is clear, repeat on `qwen2.5-7b-instruct`
