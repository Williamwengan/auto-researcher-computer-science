# v0.5 Evidence-Grounded Idea Generation 结果分析

## 1. 本轮运行结论

本轮已经完成两个方向的 v0.5 evidence-grounded idea generation：

```text
IAD + Agent Workflow
Physical Property Prediction
```

两个方向都成功生成了：

```text
baseline_cards.jsonl
focused_ideas.json
experiment_plan.json
review_ready_ideas/
idea_quality_scores.json
evidence_grounding_report_CN.md
si2025_manual_review_sheet.json
```

但需要注意：Codex 原始输出没有完全符合旧 schema，主要问题是：

- `focused_ideas.json` 外面多包了一层 `ideas`；
- `experiment_plan.json` 是总计划对象，不是 list；
- `baseline_cards.jsonl` 使用了 evidence card 字段，而不是旧 baseline card 字段；
- 部分 artifact 字段用 list 表示，而不是旧 schema 要求的 object。

因此已新增规范化脚本：

```text
focused_workflow/scripts/normalize_v05_ideation_outputs.py
```

该脚本会保留原始文件为 `.raw`，再生成兼容旧校验器和评分器的标准格式。

## 2. 最新输出目录

### IAD + Agent Workflow

```text
outputs/v05_evidence_grounded_ideation_05_iad_agent_workflow_20260712_101952
```

关键结果：

```text
Validation: PASSED
Evidence grounding errors: 0
Evidence grounding warnings: 0
Ideas: 3
Available papers: 24
Used papers: 18
Average quality score: 78.3/100
Top idea: Reference-Consistency Inspection Agent for Shifted Normal Banks
Top score: 80.5/100
```

### Physical Property Prediction

```text
outputs/v05_evidence_grounded_ideation_01_physical_property_prediction_20260712_102328
```

关键结果：

```text
Validation: PASSED
Evidence grounding errors: 0
Evidence grounding warnings: 0
Ideas: 3
Available papers: 51
Used papers: 24
Average quality score: 78.3/100
Top idea: Object-Conditioned Material Interval Mapper
Top score: 83.0/100
```

## 3. v0.5 最重要的成功点

v0.5 已经证明：

```text
idea generation 不再只是 prompt 约束，
而是可以强制绑定真实论文证据。
```

### IAD 证据绑定

```text
3 个 idea 共使用 18 篇论文证据
每个 idea 使用 8-10 篇 evidence papers
证据绑定错误数为 0
```

### 物理属性证据绑定

```text
3 个 idea 共使用 24 篇论文证据
每个 idea 使用 10-11 篇 evidence papers
证据绑定错误数为 0
```

这说明 v0.5 相比 v0.4 的关键提升不是“分数更高”，而是：

- baseline 来源可追踪；
- idea 改进点可以关联 evidence paper；
- unsupported claim 被显式暴露；
- 后续 critic-repair 可以针对证据和失败点做修复。

## 4. v0.4 vs v0.5 对比

### IAD

| 版本 | 平均分 | Top idea | Top 分数 | 证据绑定 |
|---|---:|---|---:|---|
| v0.4 | 90.5 | Reference-Consistency Agent for Shift-Resistant PatchCore Inspection | 95.0 | 无强制证据校验 |
| v0.5 | 78.3 | Reference-Consistency Inspection Agent for Shifted Normal Banks | 80.5 | 通过，18 篇证据被使用 |

### Physical Property Prediction

| 版本 | 平均分 | Top idea | Top 分数 | 证据绑定 |
|---|---:|---|---:|---|
| v0.4 | 87.0 | Evidence-Weighted Material Mixture Intervals for Object Physical Properties | 89.0 | 无强制证据校验 |
| v0.5 | 78.3 | Object-Conditioned Material Interval Mapper | 83.0 | 通过，24 篇证据被使用 |

## 5. 为什么 v0.5 规则分比 v0.4 低

这不是简单退步，主要有三个原因。

### 5.1 v0.5 加入了真实证据约束

v0.4 可以更自由地生成“看起来完整”的方案。

v0.5 必须围绕检索到的 baseline card 和 paper evidence 生成，因此输出更保守，也更容易暴露 unsupported 或 weak claims。

### 5.2 旧评分器还不完全适配 v0.5

旧评分器仍然主要按 v0.3/v0.4 的结构字段评分。

本轮 v0.5 原始输出中，`minimal_new_module` 和 `mvp_artifacts` 的语义是存在的，但格式和旧 schema 不完全一致，因此触发了部分：

```text
no_minimal_new_module
no_mvp
```

这些是格式兼容性问题，不完全等价于 idea 内容真的没有模块或 MVP。

### 5.3 v0.5 的实验阈值仍不够硬

两个方向的主要扣分原因集中在：

```text
quantitative_thresholds_weak
negative_control_weak
algorithmic_objective_not_explicit
```

这说明下一步应该做 targeted critic-repair，而不是重新从零生成 idea。

## 6. 当前最好候选

### IAD 最好候选

```text
Reference-Consistency Inspection Agent for Shifted Normal Banks
Score: 80.5/100
Evidence papers: 8
Direct baselines: PatchCore, PaDiM, WinCLIP
```

优点：

- 与之前 v0.4 最强方向一致，说明候选稳定；
- 有明确 agent workflow：reference retrieval、bank audit、calibration、report generation、human escalation；
- 很适合比赛演示，因为 IAD 可视化直观，PatchCore/MVTec AD 也更容易做 MVP。

需要修复：

- 加强量化成功阈值；
- 加强 negative controls；
- 把 algorithmic objective 写成更明确的优化目标或评分函数。

### 物理属性最好候选

```text
Object-Conditioned Material Interval Mapper
Score: 83.0/100
Evidence papers: 10
Direct baselines: GroundingDINO, SAM2, OpenSurfaces, ObjectFolder2.0
```

优点：

- 证据绑定充分；
- 与用户原始研究方向贴合；
- 指标比 IAD 更完整，包括 interval coverage、calibration error、log-MAE。

风险：

- 物理属性真实标签难；
- 容易退化成 proxy-label / lookup-table 系统；
- 比赛短期演示不如 IAD 直观。

## 7. 下一步

下一步不应该直接写最终文档，也不应该重新检索论文。

下一步应该做：

```text
v0.5 targeted critic-repair
```

具体修复目标：

1. 为每个 idea 增加明确算法目标：

```text
objective / loss / scoring function / decision rule
```

2. 为每个 idea 增加强量化成功阈值：

```text
例如 AUROC 提升多少、PRO 提升多少、coverage 达到多少、false alarm 降低多少
```

3. 为每个 idea 增加更强 negative controls：

```text
随机检索、打乱证据、替换 reference bank、背景 mask、错误类别 prompt
```

4. 保持 evidence_paper_ids 不丢失：

```text
repair 后必须再次通过 evidence_grounding validation
```

完成 repair 后，再比较：

```text
v0.5 before repair
v0.5 after repair
v0.4 baseline
```

这比单纯追求一次生成高分更符合“鲁棒科研自动化 workflow”的比赛叙事。
