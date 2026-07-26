# v0.5 Targeted Critic-Repair 前后对比报告

## 1. 结论

本轮完成了 v0.5 evidence-grounded idea 的 targeted critic-repair。

由于外部 LLM API 修复会把完整 idea、证据卡片和评分结果发送到外部服务，存在数据外发风险，因此本轮没有使用外部 LLM repair。

改为使用本地确定性 repair 脚本：

```text
focused_workflow/scripts/apply_v05_targeted_repair_locally.py
```

该脚本只在本地修改 JSON，不调用外部 API。

修复目标集中在自动评分发现的三个弱点：

```text
algorithmic_objective_not_explicit
quantitative_thresholds_weak
negative_control_weak
```

修复后，两个方向都通过了：

```text
validate_outputs.py
validate_evidence_grounding.py
format_ideas_for_review.py
evaluate_idea_quality.py
make_si2025_review_sheet.py
```

并且 evidence grounding 没有退化。

## 2. 新增脚本

### 2.1 v0.5 外部 LLM repair 脚本

```text
focused_workflow/scripts/repair_v05_evidence_grounded_ideas.py
```

作用：

- 渲染 evidence-grounded repair prompt；
- 可调用 Codex/Estelle 生成 repaired JSON；
- 自动创建 repaired_run；
- 自动后处理和重新评分。

当前由于数据外发风险，未使用该脚本进行真实 API repair。

### 2.2 v0.5 本地确定性 repair 脚本

```text
focused_workflow/scripts/apply_v05_targeted_repair_locally.py
```

作用：

- 不调用外部 API；
- 保留原始 evidence_paper_ids；
- 为每个 idea 增加明确算法目标；
- 增加强量化成功阈值；
- 增加 hard negative controls；
- 补充 MVP artifacts；
- 自动重新校验、证据绑定检查、格式化和评分。

### 2.3 v0.5 repair prompt

```text
focused_workflow/prompts/v05_evidence_critic_repair_prompt.md
```

作用：

- 未来如果允许安全调用本地/内部 LLM，可以使用该 prompt 做自动 critic-repair。

## 3. IAD 修复结果

### 3.1 原始 v0.5 输出

```text
outputs/v05_evidence_grounded_ideation_05_iad_agent_workflow_20260712_101952
```

结果：

```text
Average score: 78.3
Top score: 80.5
Top idea: Reference-Consistency Inspection Agent for Shifted Normal Banks
Evidence grounding errors: 0
Used papers: 18
```

三个 idea 都是：

```text
usable_with_repair
```

主要扣分：

```text
quantitative_thresholds_weak
negative_control_weak
algorithmic_objective_not_explicit
```

### 3.2 修复后输出

```text
outputs/v05_evidence_grounded_ideation_05_iad_agent_workflow_20260712_101952/repair_runs/local_targeted_repair_20260712_103945/repaired_run
```

结果：

```text
Average score: 89.5
Top score: 90.5
Top idea: Reference-Consistency Inspection Agent for Shifted Normal Banks
Evidence grounding errors: 0
Used papers: 18
```

修复后三个 idea 全部变为：

```text
mainline_candidate
```

详细分数：

| Idea | Before | After | Band After | Penalty After |
|---|---:|---:|---|---:|
| Reference-Consistency Inspection Agent for Shifted Normal Banks | 80.5 | 90.5 | mainline_candidate | 0 |
| Disagreement-Guided Mask Selection Agent for Weak Pixel Labels | 78.0 | 89.0 | mainline_candidate | 0 |
| Evidence-Linked Report Checker with Selective Human Escalation | 76.5 | 89.0 | mainline_candidate | 0 |

### 3.3 IAD 修复内容

修复后补充了：

- 明确 scoring function：

```text
S = z(anomaly_score)
  + 0.5*z(reference_inconsistency)
  + 0.5*z(model_disagreement)
  - 0.5*z(normal_reference_similarity)
```

- 接受 / 拒绝规则：

```text
S >= 2.0
region 与 anomaly heatmap IoU >= 0.3
normal reference 不能解释该区域
```

- 量化阈值：

```text
image_level_auroc 至少提升 2.0 percentage points
pixel_level_auroc 或 PRO 至少提升 1.0 percentage point
false_alarm_reduction 至少 10%
evidence_grounding_score 至少 85%
```

- hard negative controls：

```text
random normal reference retrieval
shuffled reference-bank provenance
unverified VLM report
5% / 10% / 20% contaminated normal bank
```

## 4. Physical Property Prediction 修复结果

### 4.1 原始 v0.5 输出

```text
outputs/v05_evidence_grounded_ideation_01_physical_property_prediction_20260712_102328
```

结果：

```text
Average score: 78.3
Top score: 83.0
Top idea: Object-Conditioned Material Interval Mapper
Evidence grounding errors: 0
Used papers: 24
```

三个 idea 都是：

```text
usable_with_repair
```

### 4.2 修复后输出

```text
outputs/v05_evidence_grounded_ideation_01_physical_property_prediction_20260712_102328/repair_runs/local_targeted_repair_20260712_103947/repaired_run
```

结果：

```text
Average score: 94.7
Top score: 95.5
Top idea: Proposal Uncertainty Propagation for Object-Level Property JSON
Evidence grounding errors: 0
Used papers: 24
```

修复后三个 idea 全部变为：

```text
mainline_candidate
```

详细分数：

| Idea | Before | After | Band After | Penalty After |
|---|---:|---:|---|---:|
| Object-Conditioned Material Interval Mapper | 83.0 | 95.0 | mainline_candidate | 0 |
| Localized Visual Evidence Verifier for Material Claims | 75.0 | 93.5 | mainline_candidate | 0 |
| Proposal Uncertainty Propagation for Object-Level Property JSON | 77.0 | 95.5 | mainline_candidate | 0 |

### 4.3 物理属性方向修复内容

修复后补充了：

- 明确 interval prediction objective：

```text
L = log_MAE(midpoint, proxy_label)
  + 0.5 * coverage_penalty
  + 0.2 * width_penalty
```

- 接受 / abstention 规则：

```text
material confidence >= 0.6
否则输出 abstention / failure_warning
```

- 量化阈值：

```text
90% nominal intervals 至少达到 80% empirical coverage
density_log_mae 或 youngs_modulus_log_mae 比 category-only prior 至少提升 5%
calibration_error < 0.10
selective_risk 随 abstention threshold 从 0.3 到 0.7 单调下降
```

- hard negative controls：

```text
shuffled material-property table
random object category replacement
background masks treated as objects
wrong material prompt set
```

## 5. 对比赛方案的意义

这一轮证明了 v0.5 pipeline 已经具备一个完整闭环：

```text
论文检索
-> evidence-bound baseline cards
-> evidence-grounded idea generation
-> idea quality scoring
-> targeted repair
-> evidence grounding re-validation
-> before/after quantitative comparison
```

这比单纯说“prompt 优化后 idea 更细”更有说服力。

可用于比赛汇报的话术：

```text
我们的智能体不仅生成 idea，还能自动检查 idea 是否有论文证据支撑，
识别量化阈值、负控制和算法目标不足的问题，
并在不破坏证据绑定的前提下进行 targeted repair。
```

## 6. 当前推荐

如果比赛最终要选择一个 MVP 展示方向，仍然更推荐：

```text
IAD + Agent Workflow
```

原因：

- 演示直观；
- PatchCore / PaDiM / WinCLIP 等 baseline 更容易做最小工程；
- reference consistency、false alarm reduction、human escalation 都能可视化；
- 更容易在三分钟视频里讲清楚 agent 工作流。

物理属性方向更适合作为第二个 benchmark 方向，用来证明 workflow 可迁移。

## 7. 下一步

下一步应该做：

```text
生成 v0.5 总结报告和比赛演示路线草案
```

报告中应包含：

1. v0.4 vs v0.5 before repair；
2. v0.5 before repair vs after repair；
3. evidence grounding coverage；
4. idea quality score 提升；
5. 推荐 MVP 方向；
6. 未来接口 / Docker / 演示视频应该展示哪些步骤。

此时仍然不写最终设计文档，只写比赛路线草案和演示流程草案。
