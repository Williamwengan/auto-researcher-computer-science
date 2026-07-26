# Human Expert Blind Review Summary

This summary decodes completed human review workbooks using the private answer key. It should be reported as a small expert sanity check, not as a large-scale human study.

## Overall

| N | focused_full wins | losses | ties | tie-half win rate | 95% Wilson CI | mean confidence | mean familiarity |
| ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 60 | 39 | 15 | 6 | 70.0% | [57.5%, 80.1%] | 3.433 | 3.783 |

## By Task

| task | N | W/L/T | win rate | 95% CI | mean confidence |
| --- | ---: | --- | ---: | --- | ---: |
| iad | 20 | 15/2/3 | 82.5% | [61.1%, 93.4%] | 4.3 |
| indoor3d | 20 | 14/6/0 | 70.0% | [48.1%, 85.5%] | 3.0 |
| physical | 20 | 10/7/3 | 57.5% | [36.4%, 76.2%] | 3.0 |

## By Comparison

| comparison | N | W/L/T | win rate | mean confidence |
| --- | ---: | --- | ---: | ---: |
| focused_full_vs_no_evidence_portfolio | 15 | 3/8/4 | 33.3% | 3.267 |
| primary_focused_full_vs_researcharena_portfolio | 15 | 12/3/0 | 80.0% | 3.4 |
| repair_effect_full_vs_no_repair_idea | 15 | 13/2/0 | 86.7% | 3.467 |
| targeted_vs_generic_refine_idea | 15 | 11/2/2 | 80.0% | 3.6 |

## Interpretation Notes

- Current human evaluation has only one expert per completed domain, so it cannot establish inter-rater reliability.
- Confidence is part of the result and should be reported; low-confidence preferences should not be overstated.
- Missing domains should be reported as pending rather than silently ignored.
- This expert check is best used together with the larger multi-LLM blind review, position-swap controls, ablations, and claim verification.
