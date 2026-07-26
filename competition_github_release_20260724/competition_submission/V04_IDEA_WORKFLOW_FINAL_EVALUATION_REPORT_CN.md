# V0.4 科研 Idea 工作流最终评价报告

生成时间：2026-07-12

## 1. 报告定位

本报告是当前阶段的 v0.4 最终评价报告，目标不是证明某一个具体 CV 算法已经完成实验，而是证明我们的科研自动化工作流已经具备：

```text
方向/任务输入
-> baseline-grounded idea 生成
-> schema 校验
-> 规则评分
-> GPT judge
-> 本地 judge
-> 人工 reviewer
-> critic-repair dry-run
-> 最终候选 idea 选择
```

本报告最终纳入两个方向：

1. IAD + Agent 工作流；
2. 物理属性预测。

Human Motion 方向不纳入本次最终 GPT judge 对比。原因是当前阶段主动收敛到两个更适合展示“工作流鲁棒性”的方向：IAD 作为稳定 MVP 候选，物理属性预测作为 judge 分歧与人工复核案例。Human Motion 保留为前期探索材料。

## 2. 当前评价体系

本阶段采用的是 hybrid idea evaluation：

```text
规则评分
+ GPT judge
+ 本地 judge
+ 人工 reviewer
+ critic-repair dry-run
```

其中：

- 规则评分来自 `evaluate_idea_quality.py`；
- GPT judge 使用 Estelle `gpt-5.5`；
- 本地 judge 使用 Ollama `minicpm-v:latest`；
- 人工 reviewer 使用 Si et al. 风格维度；
- critic-repair 暂时只做 dry-run，不覆盖原始 idea。

注意：由于 Estelle 的 Claude/Claude-Max 通道目前不稳定，本阶段没有把 Claude 结果纳入最终对比。后续如果 Claude key 稳定，可以继续补跑并扩展为真正的 multi-LLM judge ensemble。

## 3. 关键输出文件

### 3.1 IAD + Agent

```text
outputs/benchmark_cv_runs_20260711_150957/05_iad_agent_workflow
```

关键文件：

- `idea_quality_report_CN.md`
- `multi_llm_judge_gpt_only_v0_4/multi_judge_summary_CN.md`
- `multi_llm_judge_local_only_v0_4/multi_judge_summary_CN.md`
- `review_ready_ideas/IDEAS_MANUAL_REVIEW_CN.md`
- `si2025_review_reviewer01.json`
- `repair_runs/repair_20260711_222611/repair_summary_CN.md`

### 3.2 物理属性预测

```text
outputs/benchmark_cv_runs_20260711_150309/01_physical_property_prediction
```

关键文件：

- `idea_quality_report_CN.md`
- `multi_llm_judge_gpt_only_v0_4/multi_judge_summary_CN.md`
- `multi_llm_judge_local_only_v0_4/multi_judge_summary_CN.md`
- `review_ready_ideas/IDEAS_MANUAL_REVIEW_CN.md`
- `repair_runs/repair_20260711_222611/repair_summary_CN.md`

## 4. 总体结果

| 方向 | 规则评分平均分 | 规则评分 Top Idea | GPT Judge Top Idea | 本地 Judge Top Idea | 结论 |
|---|---:|---|---|---|---|
| IAD + Agent | 90.5 | Reference-Consistency Agent | Reference-Consistency Agent | Reference-Consistency Agent | 最稳定，推荐作为比赛 MVP 候选 |
| 物理属性预测 | 87.0 | Evidence-Weighted Material Mixture Intervals | Evidence-Weighted Material Mixture Intervals | Conformal Property Calibration | 有分歧，适合作为人工复核案例 |

## 5. IAD + Agent 评价结果

### 5.1 规则评分

规则评分结果：

```text
Average quality score: 90.5/100
Top idea: Reference-Consistency Agent for Shift-Resistant PatchCore Inspection
Top score: 95.0/100
```

### 5.2 GPT Judge

| Rank | Idea | GPT Overall |
|---:|---|---:|
| 1 | Reference-Consistency Agent for Shift-Resistant PatchCore Inspection | 8 |
| 2 | Disagreement-Calibrated Inspection Agent for Selective Human Escalation | 7 |
| 3 | Claim-Grounded Defect Report Agent with Region-Reference Evidence Checking | 7 |

### 5.3 本地 Judge

| Rank | Idea | Local Overall |
|---:|---|---:|
| 1 | Reference-Consistency Agent for Shift-Resistant PatchCore Inspection | 8 |
| 2 | Disagreement-Calibrated Inspection Agent for Selective Human Escalation | 7 |
| 3 | Claim-Grounded Defect Report Agent with Region-Reference Evidence Checking | 7 |

### 5.4 人工 Reviewer

人工 reviewer 结论：

| Rank | Idea | Overall | 判断 |
|---:|---|---:|---|
| 1 | Reference-Consistency Agent | 9 | 推荐作为第一阶段 MVP 主线 |
| 2 | Claim-Grounded Defect Report Agent | 8 | 适合作为展示增强模块 |
| 3 | Disagreement-Calibrated Inspection Agent | 8 | 适合作为第二阶段增强 |

### 5.5 IAD 结论

IAD 方向是当前最稳定的方向。规则评分、GPT judge、本地 judge、人工 reviewer 都一致认为：

```text
Reference-Consistency Agent for Shift-Resistant PatchCore Inspection
```

是最值得优先保留的候选 idea。

它的优势是：

- baseline 清楚：PatchCore、PaDiM、FastFlow；
- failure mode 清楚：正常库偏移、污染、光照纹理误报；
- agent 机制清楚：检索正常参考、参考一致性评分、污染审计、接受/抑制/升级决策；
- 指标清楚：false_alarm_reduction、pixel_level_auroc、evidence_grounding_score；
- 展示清楚：适合三分钟视频演示 agent 如何做决策。

因此，IAD 可作为比赛 MVP 候选方向，也可作为最终文档中的主案例。

## 6. 物理属性预测评价结果

### 6.1 规则评分

规则评分结果：

```text
Average quality score: 87.0/100
Top idea: Evidence-Weighted Material Mixture Intervals for Object Physical Properties
Top score: 89.0/100
```

### 6.2 GPT Judge

| Rank | Idea | GPT Overall |
|---:|---|---:|
| 1 | Evidence-Weighted Material Mixture Intervals for Object Physical Properties | 7 |
| 2 | Property-Aware Retrieval With Consistency Verification for Hidden Material Ambiguity | 6 |
| 3 | Conformal Property Calibration From Weak and Synthetic Interval Labels | 6 |

### 6.3 本地 Judge

| Rank | Idea | Local Overall |
|---:|---|---:|
| 1 | Conformal Property Calibration From Weak and Synthetic Interval Labels | 7 |
| 2 | Evidence-Weighted Material Mixture Intervals for Object Physical Properties | 6 |
| 3 | Property-Aware Retrieval With Consistency Verification for Hidden Material Ambiguity | 6 |

### 6.4 物理属性方向结论

物理属性预测方向出现了有价值的 judge 分歧：

- 规则评分和 GPT judge 都偏好 `Evidence-Weighted Material Mixture Intervals`；
- 本地 judge 偏好 `Conformal Property Calibration`。

这个分歧不一定是坏事。它说明 v0.4 的评价体系能发现“模型偏好差异”：

- 规则评分更重视最小新增模块、工程产物和实施细节；
- GPT judge 更认可材料混合区间的机制完整性；
- 本地 judge 更偏好评价目标明确、风险表达更保守的 calibration idea。

因此，物理属性方向更适合作为“高分歧进入人工复核”的展示案例，而不是当前比赛 MVP 主线。

## 7. Critic-Repair Dry-Run

本阶段使用：

```text
REPAIR_MIN_SCORE=90
```

筛选需要修复的 idea。

| 方向 | Repair Targets | 解释 |
|---|---:|---|
| IAD + Agent | 2 | Idea 2/3 仍可补强 MVP 显式性、阈值和负对照 |
| 物理属性预测 | 3 | 三个 idea 都低于 90，需要进一步补强数据、proxy label 和评价闭环 |

本阶段只生成 repair prompt，没有实际覆盖原始 idea。

这说明 v0.4 已经具备 critic-repair 闭环入口：

```text
评分 -> 定位低分项 -> 生成修复 prompt -> 后续可重写 -> 再评分
```

## 8. 对比赛提交物的意义

### 8.1 智能体详细设计文档

最终文档建议写成：

```text
科研 Idea 生成与评价智能体
```

而不是单独写 IAD 智能体。

核心模块：

```text
Task Spec Parser
Baseline Card Generator
Focused Idea Generator
Schema Validator
Rule-based Quality Evaluator
GPT Judge
Local Judge
Human Review Interface
Critic-Repair Agent
Final Candidate Selector
Report Exporter
```

### 8.2 Docker 镜像部署包或远程调用接口

接口可以围绕工作流设计：

```text
POST /generate_ideas
POST /evaluate_ideas
POST /repair_ideas
POST /export_report
```

其中 `evaluate_ideas` 输出：

```text
rule_scores
gpt_judge_scores
local_judge_scores
judge_disagreement
repair_targets
```

### 8.3 三分钟演示视频

推荐演示主线：

1. 输入一个方向和任务约束，例如 IAD + Agent；
2. 系统生成 baseline cards；
3. 系统生成三个 focused ideas；
4. 系统进行 schema 校验；
5. 系统进行规则评分；
6. 系统调用 GPT judge；
7. 系统调用本地 judge；
8. 系统发现低分或分歧 idea；
9. 系统生成 critic-repair prompt；
10. 系统输出最终候选 idea 和实验计划。

IAD 的 `Reference-Consistency Agent` 可作为视频里的最终候选 idea。

## 9. 当前最终结论

当前阶段可以得出三个结论：

1. v0.4 已经不只是 prompt 生成，而是具备完整的 idea 评价和修复闭环。
2. IAD + Agent 是当前最稳定的候选方向，适合作为比赛 MVP 或主案例。
3. 物理属性预测方向体现了 judge 分歧，适合作为展示“多源评价 + 人工复核必要性”的案例。

因此，下一阶段不建议继续扩展更多 CV 方向，而应开始写：

```text
科研 Idea 生成与评价智能体详细设计文档草案
```

并准备接口和演示视频脚本。

## 10. 下一步

建议下一步做三件事：

1. 写智能体详细设计文档草案：

```text
competition_submission/AGENT_DESIGN_DOC_DRAFT_CN.md
```

2. 写远程调用接口设计：

```text
competition_submission/API_DEPLOYMENT_PLAN_CN.md
```

3. 写三分钟演示视频脚本：

```text
competition_submission/DEMO_VIDEO_SCRIPT_3MIN_CN.md
```

这三份文档正好对应比赛要求：

```text
1. 智能体详细设计文档；
2. Docker 镜像部署包或远程调用接口；
3. 三分钟以内演示视频。
```

