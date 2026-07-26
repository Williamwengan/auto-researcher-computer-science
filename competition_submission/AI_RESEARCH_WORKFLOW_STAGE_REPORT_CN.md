# AI 科研自动化工作流阶段性报告

## 1. 项目目标

本项目目标不是单独提出一个 CV 算法，而是构建一个面向科研 idea 生成、评估、修复和证据校验的 AI 科研自动化工作流。

输入为：

```text
研究方向 + 具体任务类型 + baseline / 约束
```

输出为：

```text
baseline-grounded idea
详细机制解释
实验计划
评估指标
negative controls
多模型评审结果
论文证据支持检查结果
```

## 2. Baseline 问题

初始 ResearchArena / focused workflow 能生成结构化 idea，但存在几个问题：

1. idea 容易空泛；
2. baseline grounding 不够细；
3. 修复可能只是在补字段，而不是真正改进机制；
4. 缺少匿名 A/B 盲评；
5. 缺少检查 evidence 是否真的支持 claim 的模块；
6. 难以证明 idea 不是单纯“写得更长”。

## 3. 当前改进模块

| 模块 | 作用 |
|---|---|
| v0.5 Evidence-grounded ideation | 基于论文证据和 baseline card 生成 idea |
| Targeted repair | 针对低质量 idea 补机制、实验计划、负控和阈值 |
| v0.6 Multi-LLM blind A/B judge | 用 GPT、Claude、Claude-max、Gemini、DeepSeek、Qwen 等 judge 做匿名 A/B 评估 |
| v0.7 Reference claim verification | 检查 baseline weakness / proposed mechanism 是否真的有论文证据支持 |
| Evidence-card repair | 修复 evidence card 和 claim 格式，使证据链可验证 |

## 4. 三个验证方向

当前选择三个 CV 科研方向进行验证：

1. 工业异常检测 IAD + Agent；
2. 物理属性预测；
3. 室内单图 3D 场景生成。

这三个方向覆盖了工程 agent 工作流、多模态物理属性推理、生成/重建类复杂 CV 任务。

## 5. v0.6 多模型匿名 A/B 评估结果

v0.6 评估目标是判断 targeted repair 是否真的提升 idea 质量，而不是只提高规则评分。

| 方向 | 版本说明 | Reviewers | Votes | After Wins | Before Wins | After Win Rate | Agreement | 结论 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 工业异常检测 IAD + Agent | v0.5 repair | 3 | 9 | 7 | 2 | 0.778 | 0.778 | repair 后较优 |
| 物理属性预测 | v2 mechanism-consistent repair, 6 judge | 6 | 18 | 18 | 0 | 1.0 | 1.0 | repair 后显著更优 |
| 室内单图 3D 场景生成 | v0.5 repair with seeded evidence bank | 3 | 9 | 9 | 0 | 1.0 | 1.0 | repair 后显著更优 |

关键观察：

- 物理属性方向 v1 repair 曾经失败，因为 Idea 2 和 Idea 3 被错误套用了 Idea 1 的 interval-mapper loss。
- v2 将 Idea 2 改为局部视觉证据验证目标，将 Idea 3 改为 proposal uncertainty propagation 目标。
- v2 修复后，6 个 judge 在 3 个 pair 上全部选择 after，说明系统能发现失败并完成二次修复。

## 6. v0.7 论文证据链验证结果

v0.7 评估目标是检查 idea 中的 baseline weakness / proposed mechanism 是否真的有论文证据支持。

| 方向 | Ideas | Papers | Claims | Supported | Weak | Manual | Unsupported | Declared Unsupported | Pass Rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 工业异常检测 IAD + Agent | 3 | 24 | 21 | 8 | 4 | 3 | 0 | 6 | 0.857 |
| 物理属性预测 v2 evidence-card repair | 3 | 51 | 15 | 8 | 3 | 0 | 0 | 4 | 1.0 |
| 室内单图 3D 场景 evidence-card repair | 3 | 18 | 18 | 12 | 3 | 0 | 0 | 3 | 1.0 |

关键观察：

- 物理属性方向通过 evidence-card repair，将 pass rate 从 0.533 提升到 1.0。
- 室内 3D 方向通过 evidence-card repair，将 pass rate 从 0.2 提升到 1.0。
- IAD 方向仍有 3 个 needs_manual_check，但 unsupported 为 0，可以作为诚实不确定性保留。

## 7. 当前结论

当前 pipeline 已经从单纯 idea 生成，升级为：

```text
生成 idea
→ 证据绑定
→ 定向修复
→ 多模型匿名评估
→ 证据 claim 验证
```

阶段性结果说明：

1. 系统能生成 baseline-grounded idea；
2. 系统能通过 reviewer rationale 定位 repair 失败原因；
3. 系统能进行二次机制一致性修复；
4. 系统能通过 multi-LLM blind judge 验证修复是否有效；
5. 系统能检查 evidence 是否真的支持 claim；
6. 系统能把证据链薄弱点转化为可修复的 evidence-card 问题。

## 8. 当前不足

1. v0.7 目前主要是词面证据校验，不等同于真正专家审稿；
2. seeded evidence bank 仍需要在最终文档中如实说明；
3. IAD 方向仍有 3 个 needs_manual_check；
4. 当前还没有真实执行某个 CV 实验；
5. 系统还缺少最终候选 idea 自动排序模块。

## 9. 下一步 v0.8

下一步应实现：

```text
final candidate selector
```

该模块输入：

```text
v0.6 blind judge 结果
v0.7 claim verification 结果
idea quality scores
风险和实现成本
```

输出：

```text
最终推荐方向
推荐 idea
适合比赛演示的 MVP
风险说明
分工建议
```

## 10. 阶段性结论

本阶段结果说明，该科研自动化工作流已经具备 baseline-grounded idea generation、targeted repair、multi-LLM independent evaluation、evidence claim verification、failure diagnosis and second-round repair。

因此，下一步可以进入 v0.8 最终候选方案选择，而不是继续无目的地生成更多 idea。
