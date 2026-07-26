# V0.6 Multi-LLM 匿名 A/B 评估总报告

本报告汇总 IAD、物理属性预测、室内单图 3D 场景生成三个方向的匿名 A/B 盲评结果。
评估目标是判断 v0.5 targeted repair 是否真的提升 idea 质量，而不是只提高规则评分。

## 1. 总体结果

| 方向 | Reviewers | Votes | After Wins | Before Wins | Ties | After Win Rate | Mean Agreement | 结论 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 工业异常检测 IAD + Agent | 3 | 9 | 7 | 2 | 0 | 0.778 | 0.778 | repair 后较优，但仍需复核 |
| 物理属性预测 | 3 | 9 | 5 | 4 | 0 | 0.556 | 0.778 | 结果接近，不能强说显著提升 |
| 室内单图 3D 场景生成 | 3 | 9 | 9 | 0 | 0 | 1.0 | 1.0 | repair 后明显更优 |

## 2. 各方向维度提升

### 工业异常检测 IAD + Agent

| Dimension | Mean After-Before | Positive | Negative | Tie |
|---|---:|---:|---:|---:|
| implementation_readiness | 2.222 | 6 | 1 | 2 |
| mechanism_specificity | 2.0 | 7 | 2 | 0 |
| experimental_rigor | 1.889 | 7 | 0 | 2 |
| overall | 1.0 | 6 | 2 | 1 |
| expected_effectiveness | 0.333 | 4 | 2 | 3 |

### 物理属性预测

| Dimension | Mean After-Before | Positive | Negative | Tie |
|---|---:|---:|---:|---:|
| implementation_readiness | 1.889 | 7 | 1 | 1 |
| experimental_rigor | 1.444 | 5 | 1 | 3 |
| mechanism_specificity | 0.667 | 3 | 5 | 1 |
| overall | 0.556 | 4 | 4 | 1 |
| expected_effectiveness | 0.111 | 4 | 3 | 2 |

### 室内单图 3D 场景生成

| Dimension | Mean After-Before | Positive | Negative | Tie |
|---|---:|---:|---:|---:|
| implementation_readiness | 3.889 | 9 | 0 | 0 |
| experimental_rigor | 3.667 | 9 | 0 | 0 |
| mechanism_specificity | 2.556 | 9 | 0 | 0 |
| overall | 1.889 | 9 | 0 | 0 |
| baseline_grounding | 1.111 | 7 | 0 | 2 |

## 3. Pairwise 结果

### 工业异常检测 IAD + Agent

| Pair | Idea | Majority | Agreement | Votes |
|---|---|---|---:|---|
| iad_pair_01 | Reference-Consistency Inspection Agent for Shifted Normal Banks | after | 1.0 | `{"after": 3}` |
| iad_pair_02 | Disagreement-Guided Mask Selection Agent for Weak Pixel Labels | after | 0.667 | `{"before": 1, "after": 2}` |
| iad_pair_03 | Evidence-Linked Report Checker with Selective Human Escalation | after | 0.667 | `{"before": 1, "after": 2}` |

### 物理属性预测

| Pair | Idea | Majority | Agreement | Votes |
|---|---|---|---:|---|
| physical_property_pair_01 | Object-Conditioned Material Interval Mapper | after | 1.0 | `{"after": 3}` |
| physical_property_pair_02 | Localized Visual Evidence Verifier for Material Claims | before | 0.667 | `{"before": 2, "after": 1}` |
| physical_property_pair_03 | Proposal Uncertainty Propagation for Object-Level Property JSON | before | 0.667 | `{"before": 2, "after": 1}` |

### 室内单图 3D 场景生成

| Pair | Idea | Majority | Agreement | Votes |
|---|---|---|---:|---|
| indoor_scene_generation_pair_01 | Layout-First Scene Assembly with Uncertainty-Aware Object Slots | after | 1.0 | `{"after": 3}` |
| indoor_scene_generation_pair_02 | Geometry Scaffold Plus Retrieval for Occluded Object Completion | after | 1.0 | `{"after": 3}` |
| indoor_scene_generation_pair_03 | Multi-Hypothesis Scene Completion with a Consistency Verifier | after | 1.0 | `{"after": 3}` |

## 4. 关键观察

- IAD 方向：repair 后整体胜率为 7/9，说明改进有效，但 GPT reviewer 对部分 pair 有不同意见，后续需要看 rationale，不能只看总胜率。
- 物理属性预测方向：repair 后胜率为 5/9，提升不稳定，说明该方向仍然是当前 pipeline 的薄弱点。尤其 pair 02 和 pair 03 多数 judge 偏向 before，后续需要重新做 critic-repair，而不是直接进入最终方案。
- 室内单图 3D 场景生成方向：repair 后 9/9 全胜，且 agreement 为 1.0，说明 v0.5 targeted repair 对实验严谨性、机制细节和实现可行性提升明显。
- 三个方向共同显示：repair 对 experimental_rigor、mechanism_specificity、implementation_readiness 的提升最明显；对 novelty 的提升较弱，说明当前 repair 更像“让 idea 更可执行”，还不是“显著提高创新性”。

## 5. 是否能证明不是单纯规则刷分

可以初步证明，但不能完全证明。理由如下：
- 支持证据：评估采用匿名 A/B，reviewer 不知道 before/after，且 GPT、Claude、Claude-max 三个 judge 独立评分。
- 支持证据：IAD 和室内 3D 场景方向在 blind judge 下多数或全部偏向 after，说明不是只有本地规则评分上涨。
- 保留风险：物理属性方向结果接近，说明 repair 仍可能存在模板化补强、指标迎合或机制不够真实的问题。
- 保留风险：LLM judge 仍可能偏好结构更完整、更长的文本，因此还需要人工 reviewer 和额外模型 judge 做鲁棒性检查。

## 6. 当前风险

- LLM judge 不是专家审稿人，可能高估格式完整的 idea。
- 每个方向只有 3 个 idea，样本量仍小。
- 03 室内 3D 场景方向使用 seeded evidence bank，需要在报告中说明这是检索失败后的 fallback，不应伪装成完全自动联网检索。
- 物理属性方向尚未证明 repair 稳定有效，不能作为当前最强展示方向。
- 当前结果证明的是 idea 质量和可执行性提升，还没有证明真实实验指标提升。

## 7. 下一步建议

1. 优先对物理属性预测方向做二次 critic-repair，因为它的 blind A/B 结果最弱。
2. 使用云雾 API 的 Qwen/Gemini 作为额外 judge，优先评估物理属性方向，检查 GPT/Claude 系 judge 是否存在偏差。
3. 对 IAD 和室内 3D 场景方向保留当前结果，作为 v0.5 repair 有效的主要证据。
4. 后续 v0.7 应加入 reference claim verification，检查 evidence 是否真的支持每个 baseline weakness。
5. 比赛文档暂时不要写最终版，可以把本报告作为技术路线和阶段性验证材料。
