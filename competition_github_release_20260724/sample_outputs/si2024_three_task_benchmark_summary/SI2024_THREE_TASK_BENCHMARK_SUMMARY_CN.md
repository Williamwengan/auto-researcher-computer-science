# Si et al.-style 三方向 Research Idea Benchmark 总结

本报告参考 Si et al. 的 research idea blind review 协议，对三个 CV 科研自动化任务进行多 LLM 盲评。评价维度包括 novelty、excitement、feasibility、expected_effectiveness、overall，并扩展 baseline grounding、experimental rigor、mechanism specificity、implementation readiness。

## 1. 三方向投票总表

| Task | Reviewers | Rows | Before Votes | After Votes | Tie | Unknown | After Win Rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| iad | 5 | 15 | 6 | 9 | 0 | 0 | 60.00% |
| physical_property | 5 | 15 | 8 | 7 | 0 | 0 | 46.67% |
| indoor_scene_generation | 5 | 15 | 3 | 12 | 0 | 0 | 80.00% |

## 2. Before/After 各维度均分差值


### iad

| Dimension | Before Mean | After Mean | After-Before |
|---|---:|---:|---:|
| novelty | 6.67 | 6.47 | -0.20 |
| excitement | 6.93 | 6.80 | -0.13 |
| feasibility | 7.20 | 6.87 | -0.33 |
| expected_effectiveness | 6.53 | 6.73 | +0.20 |
| overall | 6.67 | 6.67 | +0.00 |
| baseline_grounding | 7.33 | 7.07 | -0.27 |
| experimental_rigor | 6.13 | 7.13 | +1.00 |
| mechanism_specificity | 5.93 | 7.13 | +1.20 |
| implementation_readiness | 5.93 | 6.93 | +1.00 |

### physical_property

| Dimension | Before Mean | After Mean | After-Before |
|---|---:|---:|---:|
| novelty | 6.53 | 6.13 | -0.40 |
| excitement | 6.67 | 6.20 | -0.47 |
| feasibility | 7.13 | 6.40 | -0.73 |
| expected_effectiveness | 6.60 | 5.93 | -0.67 |
| overall | 6.53 | 6.00 | -0.53 |
| baseline_grounding | 7.27 | 6.87 | -0.40 |
| experimental_rigor | 6.13 | 6.47 | +0.33 |
| mechanism_specificity | 6.00 | 5.67 | -0.33 |
| implementation_readiness | 5.73 | 6.13 | +0.40 |

### indoor_scene_generation

| Dimension | Before Mean | After Mean | After-Before |
|---|---:|---:|---:|
| novelty | 6.60 | 6.67 | +0.07 |
| excitement | 6.80 | 6.87 | +0.07 |
| feasibility | 6.33 | 6.60 | +0.27 |
| expected_effectiveness | 5.87 | 6.20 | +0.33 |
| overall | 6.07 | 7.00 | +0.93 |
| baseline_grounding | 6.40 | 7.13 | +0.73 |
| experimental_rigor | 4.67 | 7.80 | +3.13 |
| mechanism_specificity | 5.47 | 6.93 | +1.47 |
| implementation_readiness | 4.47 | 7.87 | +3.40 |

## 3. 每个 Pair 的盲评偏好


### iad

| Pair ID | Before Votes | After Votes | Tie | Unknown |
|---|---:|---:|---:|---:|
| iad_pair_01 | 0 | 5 | 0 | 0 |
| iad_pair_02 | 3 | 2 | 0 | 0 |
| iad_pair_03 | 3 | 2 | 0 | 0 |

### physical_property

| Pair ID | Before Votes | After Votes | Tie | Unknown |
|---|---:|---:|---:|---:|
| physical_property_pair_01 | 0 | 5 | 0 | 0 |
| physical_property_pair_02 | 4 | 1 | 0 | 0 |
| physical_property_pair_03 | 4 | 1 | 0 | 0 |

### indoor_scene_generation

| Pair ID | Before Votes | After Votes | Tie | Unknown |
|---|---:|---:|---:|---:|
| indoor_scene_generation_pair_01 | 1 | 4 | 0 | 0 |
| indoor_scene_generation_pair_02 | 1 | 4 | 0 | 0 |
| indoor_scene_generation_pair_03 | 1 | 4 | 0 | 0 |

## 4. 初步结论模板

- 如果 After Win Rate 高且 overall / experimental_rigor / implementation_readiness 提升，说明 repair/evidence-grounded refinement 有效。
- 如果 after 在 experimental_rigor 和 implementation_readiness 上升，但 novelty/excitement 不升，说明 repair 主要改善可执行性，没有显著提升研究创新性。
- 如果 before 明显胜出，说明当前 repair 存在过度模板化或错误注入，需要增加一致性检查和 task-specific repair 约束。
- 该评测是 Si et al.-style benchmark，而不是复现其 100+ NLP researcher human study。我们使用 multi-LLM judge 替代大规模人工评审，并保留人工复核环节。

