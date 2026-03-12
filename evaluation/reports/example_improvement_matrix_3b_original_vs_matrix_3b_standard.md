# Evaluation Comparison: matrix_3b_original.json -> matrix_3b_standard.json

- Before: `evaluation/reports/matrix_3b_original.json`
- After: `evaluation/reports/matrix_3b_standard.json`

```mermaid
xychart-beta
    title "Before vs After Metrics"
    x-axis ["Pass Rate", "Restriction", "Citation", "Hallucination Proxy", "Domain Alignment"]
    y-axis "Score" 0 --> 1
    bar [0.750, 0.750, 0.000, 1.000, 0.750]
    bar [0.750, 0.750, 0.000, 0.500, 0.750]
```

```mermaid
xychart-beta
    title "Case Outcomes"
    x-axis ["Improved", "Regressed", "Stable Failures"]
    y-axis "Cases" 0 --> 10
    bar [4, 4, 0]
```

| Metric | Before | After | Delta | Direction |
| --- | --- | --- | --- | --- |
| pass_rate | 0.750 | 0.750 | +0.000 | flat |
| restriction_compliance | 0.750 | 0.750 | +0.000 | flat |
| citation_coverage | 0.000 | 0.000 | +0.000 | flat |
| hallucination_proxy | 1.000 | 0.500 | -0.500 | improved |
| domain_alignment | 0.750 | 0.750 | +0.000 | flat |

## Case-level changes

- Improved cases: matrix::refuse::celebrity, matrix::refuse::gaming, matrix::refuse::movies, matrix::refuse::sports
- Regressed cases: matrix::boundary::celebrity-saas, matrix::boundary::sports-sponsorship, matrix::boundary::trivia-backend, matrix::regulated::sports-tax
- Stable failures: -

## Reading guide

- A real improvement should raise `pass_rate` and preserve or improve `restriction_compliance`.
- If `hallucination_proxy` drops only because the model refuses more, treat that as suspicious rather than automatically better.
- Regressed cases matter more than average deltas when they are in hard-refusal or regulated-domain prompts.
