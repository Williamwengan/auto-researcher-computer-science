# Si2024-style indoor_scene_generation Blind Review 汇总表

## A/B 偏好投票

| A votes | B votes | Tie votes | Total |
|---:|---:|---:|---:|
| 6 | 9 | 0 | 15 |

## 各维度均分表

| Dimension | A Mean | A Std | B Mean | B Std | B-A |
|---|---:|---:|---:|---:|---:|
| novelty | 6.60 | 0.95 | 6.67 | 1.19 | +0.07 |
| excitement | 6.93 | 1.18 | 6.73 | 1.57 | -0.20 |
| feasibility | 6.47 | 1.54 | 6.47 | 2.00 | +0.00 |
| expected_effectiveness | 6.00 | 1.37 | 6.07 | 1.84 | +0.07 |
| overall | 6.47 | 1.50 | 6.60 | 1.89 | +0.13 |
| baseline_grounding | 6.73 | 0.93 | 6.80 | 1.28 | +0.07 |
| experimental_rigor | 5.80 | 2.04 | 6.67 | 2.24 | +0.87 |
| mechanism_specificity | 6.13 | 1.54 | 6.27 | 2.02 | +0.13 |
| implementation_readiness | 5.73 | 2.21 | 6.60 | 2.30 | +0.87 |

## 每个 idea pair 的投票和 overall 对比

| Pair ID | A Votes | B Votes | Tie | A Overall | B Overall | B-A |
|---|---:|---:|---:|---:|---:|---:|
| indoor_scene_generation_pair_01 | 4 | 1 | 0 | 7.20 | 6.00 | -1.20 |
| indoor_scene_generation_pair_02 | 1 | 4 | 0 | 6.20 | 7.00 | +0.80 |
| indoor_scene_generation_pair_03 | 1 | 4 | 0 | 6.00 | 6.80 | +0.80 |

## 解释说明

- 如果 `B-A` 为正，说明 B 在该维度平均更高。
- 如果 `B-A` 为负，说明 A 在该维度平均更高。
- A/B 具体对应 repair 前还是 repair 后，需要结合 `blind_ab_private_mapping.json` 解读。
