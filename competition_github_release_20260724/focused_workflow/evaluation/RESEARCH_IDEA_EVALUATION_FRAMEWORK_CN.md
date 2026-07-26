# Research Idea 质量评价框架（Focused Workflow v0.3）

本文件用于定义我们后续评价 idea generation pipeline 的量化指标。目标不是只让 idea 写得更长，而是证明 workflow 生成的 idea 在 **baseline grounding、机制细节、实验可执行性、评价指标对齐、实现准备度** 上有可量化提升。

## 1. 核心结论

论文 idea 的“创新性/质量”目前没有像分类准确率一样完全客观的统一指标。更稳妥的评价方式是组合使用：

1. 专家或 LLM judge 按 rubric 打分。
2. 和已有论文、baseline、参考文献做对齐度、差异度、可行性比较。
3. 检查 idea 是否能落到实验、baseline、指标、ablation、失败标准和实现计划。
4. 对自动评分结果做人工抽查，避免 LLM-as-a-Judge 的 novelty mirage。

因此我们采用：

```text
规则校验 + LLM/人工 rubric 评分 + pairwise ranking + baseline/reference grounding + implementation readiness
```

## 2. 可参考的 Benchmark 与指标来源

| 来源 | 适合借鉴的部分 | 我们如何使用 |
|---|---|---|
| Si et al., Can LLMs Generate Novel Research Ideas? | Novelty、Excitement、Feasibility、Expected Effectiveness、Overall Score，1-10 分并写 rationale | 作为基础 reviewer 评分维度 |
| IdeaBench | 让模型在论文标题、摘要、参考文献上下文中生成 idea，再用 pairwise ranking 和 Insight Score 量化 | 借鉴 pairwise ranking / relative score，而不是只给绝对分 |
| AI Idea Bench 2025 | ground-truth alignment 与 general reference judgment 双维度评价 | 用于以后引入相关论文集后，衡量 idea 与真实论文贡献的接近程度和差异 |
| Can Large Language Models Unlock Novel Scientific Research Ideas? | Idea Alignment Score、Idea Distinctness Index、人工 novelty/relevance/feasibility | 借鉴 alignment 与 distinctness，避免 idea 重复 |
| ResearchArena | 端到端科研 agent 的 peer review：novelty、soundness、significance、clarity、reproducibility、experimental rigor、references、reference integrity、results integrity | 借鉴 experimental rigor、reference integrity、results integrity，防止只生成漂亮 idea |
| PaperBench / ScienceAgentBench | 评估科研执行、代码、实验复现与成本 | 不作为 idea 阶段主指标，作为后续实验执行阶段指标 |
| RQ-Bench / novelty mirage 警告 | LLM judge 可能高估模型生成问题的新颖性，专家更偏好作者锚定问题 | 自动 novelty 分必须搭配人工抽查和 reference grounding |

## 3. 我们的三层评价指标

### 3.1 格式与约束指标

这些指标主要由脚本自动计算，用来检查生成物是否完整。

| 指标 | 含义 | 推荐计算方式 |
|---|---|---|
| schema_pass | JSON/JSONL 是否通过 schema | 0/1 |
| required_field_coverage | 必需字段覆盖率 | 已填字段数 / 必需字段数 |
| baseline_count | 每个 idea 引用的 direct baselines 数量 | count |
| metric_count | 每个 idea 的评价指标数量 | count |
| ablation_count | 消融实验数量 | count |
| failure_criteria_count | 失败标准数量 | count |
| implementation_step_count | 实施步骤数量 | count |
| focus_drift_flag | 是否偏离 task spec | 0/1，由规则或 judge 判定 |

这些指标只能证明“结构完整”，不能证明 idea 真的好。

### 3.2 Idea 内容质量指标

这些指标用于判断 idea 是否细、是否聚焦、是否能落地。

| 指标 | 分数范围 | 评价重点 |
|---|---:|---|
| baseline_grounding_score | 1-10 | 是否说明 baseline 完成什么任务、怎么评价、哪里失败 |
| failure_mode_specificity_score | 1-10 | 是否指出具体失败模式，而不是泛泛说“不鲁棒” |
| mechanism_specificity_score | 1-10 | 新方法是否有输入、输出、状态、算法步骤、训练目标或决策策略 |
| metric_alignment_score | 1-10 | 指标是否能验证 idea 的核心贡献 |
| experiment_executability_score | 1-10 | 1-2 周 MVP 是否真实可做，数据/代码/算力是否明确 |
| falsifiability_score | 1-10 | 是否有明确失败标准和负控实验 |
| novelty_proxy_score | 1-10 | 是否不是 baseline + VLM/SAM/retrieval 的简单拼接 |
| distinctness_score | 1-10 | 三个 idea 之间是否足够不同 |
| risk_awareness_score | 1-10 | 是否正视标签噪声、不可观测性、数据缺失、域偏移等风险 |
| implementation_readiness_score | 1-10 | 是否能直接分工实现，有模块、输入输出和时间表 |

### 3.3 Pipeline 鲁棒性指标

这些指标用于比较不同 pipeline 版本，例如旧 prompt vs 新 prompt。

| 指标 | 含义 |
|---|---|
| pass_rate | 完整生成并通过 schema 的比例 |
| average_quality_score | 所有 idea 的平均质量分 |
| top1_quality_score | 每轮最好 idea 的质量分 |
| human_accept_rate | 人工审查后愿意保留或进入下一阶段的比例 |
| redundancy_rate | 三个 idea 是否重复或高度相似 |
| rerun_consistency | 同一输入多次运行是否稳定聚焦 |
| repair_success_rate | critic/repair 后分数是否提升 |
| cost_per_valid_idea | token/费用除以有效 idea 数 |
| reference_integrity_rate | baseline/论文/数据集是否真实存在、引用是否可信 |

## 4. 推荐综合分数

我们定义一个 0-100 的 Idea Quality Score：

```text
Idea Quality Score =
  0.15 * baseline_grounding_score
+ 0.15 * failure_mode_specificity_score
+ 0.15 * mechanism_specificity_score
+ 0.10 * metric_alignment_score
+ 0.15 * experiment_executability_score
+ 0.10 * falsifiability_score
+ 0.05 * novelty_proxy_score
+ 0.05 * distinctness_score
+ 0.05 * risk_awareness_score
+ 0.05 * implementation_readiness_score
```

每个子项是 1-10 分，最终乘以 10 得到 0-100 分。

建议解释：

| 分数 | 含义 |
|---:|---|
| 85-100 | 可作为主线推进，适合写 MVP 实施计划 |
| 70-84 | 有价值，但需要补细节或合并到其他 idea |
| 55-69 | 结构完整但偏泛，需要 critic/repair |
| <55 | 不建议保留，应该重新生成 |

## 5. Pairwise Ranking / Insight Score 思路

绝对分容易漂移，因此借鉴 IdeaBench，再加入 pairwise ranking：

1. 对同一 task 的所有 ideas 两两比较。
2. judge 只能选择哪个 idea 更好，并说明理由。
3. 统计每个 idea 的胜率。
4. 将胜率作为相对质量分：

```text
Pairwise Win Rate = wins / comparisons
Insight-like Score = average_pairwise_win_rate * 100
```

最终排序时使用：

```text
Final Rank Score = 0.7 * Idea Quality Score + 0.3 * Insight-like Score
```

## 6. Reference / Baseline Grounding 检查

每个 idea 必须回答：

```text
1. baseline 是哪个？
2. baseline 原本完成什么任务？
3. baseline 用什么指标评价？
4. baseline 的具体失败模式是什么？
5. 新 idea 改 baseline 的哪一个模块？
6. 哪个实验能证明新模块有用？
7. 哪个负控能证明它不是无效拼接？
```

如果回答不清楚，则 baseline_grounding_score 和 mechanism_specificity_score 降分。

## 7. Anti-Shallow 规则

以下 idea 应该被自动标记为低质量：

- 只说 “baseline + VLM report”。
- 只说 “baseline + SAM”。
- 只说 “baseline + retrieval”。
- 只写一个大系统，没有最小新增模块。
- 没有失败标准。
- 没有负控实验。
- 没有明确指标验证新模块。
- 没有 1-2 周 MVP。
- 没有说明和已有 baseline 的具体差异。

## 8. 用于挑战杯汇报的说法

我们可以这样描述改进目标：

```text
我们不是简单优化 prompt 让 idea 更长，而是引入了 research-idea quality evaluation framework。
该框架结合 Si et al. 的专家评分维度、IdeaBench 的 pairwise ranking 思路、ResearchArena 的 experimental rigor / reference integrity 维度，
从格式完整性、baseline grounding、机制细粒度、实验可执行性、指标对齐、可证伪性、idea 多样性和实现准备度多个维度量化评价 idea。
```

我们最终要证明：

```text
改进前：schema PASS，但 idea 泛、人工接受率低。
改进后：schema PASS，同时 baseline_grounding、mechanism_specificity、experiment_executability、implementation_readiness 分数提高，human_accept_rate 提高。
```

## 9. 后续脚本目标

下一步建议实现：

```text
focused_workflow/scripts/evaluate_idea_quality.py
```

输入：

```text
outputs/benchmark_cv_runs_xxx/task_name
```

输出：

```text
idea_quality_scores.json
idea_quality_report_CN.md
pairwise_ranking.json
```

第一版先做规则评分和人工/LLM reviewer 字段汇总；第二版再加入 pairwise ranking 和 reference integrity 检查。
