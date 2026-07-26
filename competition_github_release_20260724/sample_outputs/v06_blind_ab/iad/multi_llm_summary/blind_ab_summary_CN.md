# v0.6 匿名 A/B 盲评统计报告

- Domain: iad
- Reviewers: 3
- Total votes: 9
- After wins: 7
- Before wins: 2
- Ties: 0
- After win rate with ties half: 0.778
- Mean pair agreement: 0.778

## Reviewer Summary

| Reviewer | Completed | Invalid | After Wins | Before Wins | Ties | After Win Rate |
|---|---:|---:|---:|---:|---:|---:|
| blind_review_gpt_reviewer | 3 | 0 | 1 | 2 | 0 | 0.333 |
| blind_review_claude_reviewer | 3 | 0 | 3 | 0 | 0 | 1.0 |
| blind_review_claude_max_reviewer | 3 | 0 | 3 | 0 | 0 | 1.0 |

## Pair Summary

| Pair | Idea | Majority | Agreement | Votes |
|---|---|---|---:|---|
| iad_pair_01 | Reference-Consistency Inspection Agent for Shifted Normal Banks | after | 1.0 | {"after": 3} |
| iad_pair_02 | Disagreement-Guided Mask Selection Agent for Weak Pixel Labels | after | 0.667 | {"before": 1, "after": 2} |
| iad_pair_03 | Evidence-Linked Report Checker with Selective Human Escalation | after | 0.667 | {"before": 1, "after": 2} |

## Dimension Delta

`mean_after_minus_before > 0` means after-repair is rated higher.

| Dimension | Mean After-Before | N | Positive | Negative | Tie |
|---|---:|---:|---:|---:|---:|
| novelty | -0.111 | 9 | 1 | 2 | 6 |
| feasibility | -0.333 | 9 | 2 | 5 | 2 |
| expected_effectiveness | 0.333 | 9 | 4 | 2 | 3 |
| experimental_rigor | 1.889 | 9 | 7 | 0 | 2 |
| baseline_grounding | 0.111 | 9 | 3 | 2 | 4 |
| mechanism_specificity | 2.0 | 9 | 7 | 2 | 0 |
| implementation_readiness | 2.222 | 9 | 6 | 1 | 2 |
| overall | 1.0 | 9 | 6 | 2 | 1 |
