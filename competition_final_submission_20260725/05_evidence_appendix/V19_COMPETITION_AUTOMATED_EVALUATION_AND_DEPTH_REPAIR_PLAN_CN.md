# V19 比赛版自动评估与深度修复计划

生成日期：2026-07-25

## 1. 当前判断

当前项目优先完成比赛交付。已有工作包括：

- focused idea generation
- evidence-grounded retrieval
- targeted repair
- multi-LLM blind review
- reference claim verification
- IAD 真实数据 smoke test 和 execution-feedback repair case
- 少量领域专家人工盲评

但当前仍有三个明显短板：

1. 人工评审人数少，不能作为强统计证据。
2. 部分专家认为 idea 有一定意思，但技术深度不足，停留在表面组合。
3. 比赛展示不宜依赖人工审查闭环，应尽量自动化。

因此后续主线应从“更多人工评审”转为：

```text
自动深度检查
-> 自动可执行性检查
-> 自动 evidence/claim 检查
-> 自动 repair
-> 轻量真实执行反馈
-> 最终方案输出
```

## 2. 关键更正：当前 IAD 文件不是 indoor3D

文件：

```text
IAD评审答题表_最终版.xlsx
```

经 private answer key 核对，该文件中 20 个 item 全部对应：

```text
task = iad
```

因此它不能作为 indoor3D 专家评审表使用。若该文件由 indoor3D 同学填写，则说明发送或填写的评审包发生了任务错配。比赛材料中应避免把它写成 indoor3D 结果。

## 3. 人工评审如何定位

人工评审只作为 supplementary sanity check，而不是主评价依据。

可写：

```text
We collected a small domain-expert blind-review sanity check. Because each completed domain has only one expert, we do not use it as the main statistical evidence. Instead, it is used to identify failure modes and calibrate the automated evaluation pipeline.
```

中文：

```text
我们收集了小规模领域专家匿名盲评作为外部 sanity check。由于每个已完成方向只有一名专家，不能据此主张强统计结论；我们主要使用它发现失败模式，并校准自动评估模块。
```

## 4. 需要新增的自动模块

### 4.1 Idea Depth Checker

目标：解决“idea 有意思但深度不够”的问题。

每个 idea 必须自动检查以下字段：

| depth dimension | required evidence |
| --- | --- |
| mechanism specificity | 是否有明确机制，而不是泛泛组合模块 |
| algorithmic objective | 是否定义目标函数、优化信号或可测量代理目标 |
| implementation path | 是否说明输入、输出、关键模块、脚本入口 |
| experiment falsifiability | 是否有能推翻 idea 的 negative controls |
| baseline contrast | 是否明确区别于 baseline，而不是换描述 |
| data/metric grounding | 是否绑定数据集、指标、表格或图 |
| failure mode | 是否说明何时失败以及如何诊断 |

输出：

```text
idea_depth_scores.json
idea_depth_report_CN.md
```

低分 idea 自动进入 depth repair。

### 4.2 Execution Readiness Gate

参考 Ideation-Execution Gap 和 execution-grounded automated AI research 的思想：不要只评价 idea 看起来好不好，而要评价它能不能走向执行。

每个 idea 至少要通过：

- dataset availability check
- baseline availability check
- metric computability check
- 24-hour smoke-test path check
- required scripts/files check
- expected failure signal check

输出：

```text
execution_readiness_scores.json
execution_readiness_report_CN.md
```

### 4.3 Automated Claim/Evidence Gate

已有 v0.7 reference claim verification，后续要把它变成 final方案前的硬门槛：

- unsupported claim = fail
- declared unsupported but honest = warning
- weakly supported = allowed but需标注
- supported = pass

输出：

```text
claim_gate_report_CN.md
```

### 4.4 Automated Repair Loop

若 idea depth 或 execution readiness 不通过，则自动修复：

```text
fail reason
-> targeted repair prompt
-> repair output
-> re-check depth/readiness/evidence
-> pass/fail
```

修复不能只加长文字，必须补充：

- concrete mechanism
- pseudo-code or module interface
- measurable objective
- negative controls
- execution smoke-test plan

## 5. 推荐新增 benchmark

### Benchmark A：Depth Robustness Benchmark

目的：证明系统不是只生成漂亮文字，而是能生成细粒度、可执行、可检查的方案。

设置：

```text
3 tasks × 3 ideas × before/after repair
```

指标：

- depth score
- execution readiness score
- claim pass rate
- required-field completion rate

优点：不依赖人工评审，最适合比赛展示。

### Benchmark B：Task Perturbation Robustness Benchmark

目的：证明对不同任务表述鲁棒。

对每个任务构造三种输入：

```text
original task spec
underspecified task spec
strict engineering-constrained task spec
```

检查：

- idea 是否仍绑定 baseline/evidence
- 是否保持实验计划完整
- 是否出现 unsupported claims
- 是否能通过 depth/readiness gate

### Benchmark C：Execution Feedback Benchmark

目的：对齐 execution-grounded automated research 方向。

当前已有 IAD case：

```text
V1.5 global threshold failed
-> V1.6 per-category threshold calibration
-> FPR 0.574257 -> 0.009901
```

后续不必把所有任务都完整执行，只需把 IAD 作为 execution feedback case study，说明 workflow 能把真实执行失败转化为修复信号。

## 6. 与参考工作的对应关系

| reference direction | 对我们项目的启发 | 我们应强调的改进点 |
| --- | --- | --- |
| Ideation-Execution Gap | idea 盲评高不等于执行后有效 | 增加 execution readiness 和 IAD 真实执行反馈 |
| Towards Execution-Grounded Automated AI Research | 执行反馈比单纯 ideation 更可靠 | 我们做轻量 execution-feedback repair，不追求大规模 GPU search |
| AInstein | 评价 AI 是否能提出可行解，关注 success/rediscovery/novelty | 增加自动 feasibility/depth gate |
| HARPA | 文献 grounded、testable hypothesis、可执行性更重要 | 增加 testability-driven depth checker |
| AlphaResearch | propose -> program -> verify -> optimize | 我们采用 task-level workflow，不做算法竞赛式搜索，但保留 verify/repair 闭环 |

## 7. 最终比赛叙事建议

不要说：

```text
我们的 idea generation 已经 SOTA。
```

建议说：

```text
我们发现单纯 idea 盲评不足以支撑科研自动化，因此在 ResearchArena baseline 上加入 evidence grounding、depth checking、execution readiness、multi-LLM blind review、reference claim verification 和 IAD execution-feedback repair，形成一个可检查、可修复、可执行导向的科研自动化 workflow。
```

## 8. 下一步执行顺序

1. 不再继续扩人工评审作为主线。
2. 更正 human review 统计：当前完成的是 IAD 和 physical，不是 indoor3D。
3. 实现 `idea_depth_checker`。
4. 对 V10 final research plans 运行 depth/readiness gate。
5. 低分 idea 自动 repair。
6. 生成 V20 自动深度评估报告。
7. 把 V19/V20 作为比赛最终增强模块写进 GitHub 和 PPT。
