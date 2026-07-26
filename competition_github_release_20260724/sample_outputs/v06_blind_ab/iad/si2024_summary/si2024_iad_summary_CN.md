# Si2024-style IAD Blind Review 汇总表

本表采用 Si et al. 风格的 research idea blind review 维度：novelty、excitement、feasibility、expected_effectiveness、overall，并加入 workflow 扩展维度。

## 使用的 reviewer

- `blind_review_si2024_gpt.json`
- `blind_review_si2024_claude.json`
- `blind_review_si2024_gemini.json`
- `blind_review_si2024_deepseek.json`
- `blind_review_si2024_qwen.json`

## A/B 偏好投票

| A votes | B votes | Tie votes | Total |
|---:|---:|---:|---:|
| 11 | 4 | 0 | 15 |

## 各维度均分表

| Dimension | A Mean | A Std | B Mean | B Std | B-A |
|---|---:|---:|---:|---:|---:|
| novelty | 6.87 | 0.81 | 6.27 | 1.12 | -0.60 |
| excitement | 7.33 | 0.87 | 6.40 | 1.45 | -0.93 |
| feasibility | 7.73 | 0.85 | 6.33 | 1.30 | -1.40 |
| expected_effectiveness | 7.07 | 1.00 | 6.20 | 1.38 | -0.87 |
| overall | 7.27 | 0.93 | 6.07 | 1.39 | -1.20 |
| baseline_grounding | 7.87 | 0.88 | 6.53 | 1.45 | -1.33 |
| experimental_rigor | 7.20 | 1.64 | 6.07 | 1.69 | -1.13 |
| mechanism_specificity | 7.13 | 1.59 | 5.93 | 1.91 | -1.20 |
| implementation_readiness | 7.27 | 1.81 | 5.60 | 1.40 | -1.67 |

## 每个 idea pair 的投票和 overall 对比

| Pair ID | A Votes | B Votes | Tie | A Overall | B Overall | B-A |
|---|---:|---:|---:|---:|---:|---:|
| iad_pair_01 | 5 | 0 | 0 | 8.00 | 6.20 | -1.80 |
| iad_pair_02 | 3 | 2 | 0 | 7.00 | 5.80 | -1.20 |
| iad_pair_03 | 3 | 2 | 0 | 6.80 | 6.20 | -0.60 |

## 解释说明

- 如果 `B-A` 为正，说明 B 在该维度平均更高。
- 如果 `B-A` 为负，说明 A 在该维度平均更高。
- A/B 具体对应 repair 前还是 repair 后，需要结合 `blind_ab_private_mapping.json` 解读。
- `blind_review_si2024_gpt_reviewer.json` 是重复/早期 GPT reviewer，本次正式汇总未纳入，避免 GPT 被重复计算。

