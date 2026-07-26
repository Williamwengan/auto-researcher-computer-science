# V20 比赛评分维度对齐与演示增强报告

生成时间：2026-07-25T09:47:23

## 一句话定位

面向 AI for Science 科研发现的自动化智能体，支持论文证据检索、baseline 缺陷分析、细粒度 idea 生成、实验计划、多模型盲评、targeted repair、论文证据核查和 IAD 执行反馈。

## 评分维度对齐

| 维度 | 权重 | 核心表达 | 证据 |
| --- | ---: | --- | --- |
| 科学与应用价值 | 30% | 把大模型从泛泛生成 idea 推向证据驱动、可验证、可执行导向的科研方案生成。 | - 覆盖 3 个代表性 AI4S/CV 科研任务：物理属性预测、室内单图 3D 场景生成、工业异常检测 IAD + Agent<br>- 解决科研自动化中的核心问题：idea 空泛、缺少 baseline grounding、缺少实验计划和证据核查。<br>- IAD 方向已接入 MVTec AD 真实数据 smoke test，形成执行反馈案例。 |
| 技术深度 | 30% | 不是单轮 prompt，而是多模块科研智能体 workflow。 | - evidence-grounded ideation：每个 idea 绑定 paper evidence 和 baseline weakness。<br>- targeted repair：根据 blind review rationale 定位机制错配和实验不足。<br>- multi-LLM anonymous blind A/B judge：隐藏 before/after 来源，验证 repair 是否真实提升。<br>- reference claim verification：自动检查 claim 是否被论文证据支持。<br>- depth/readiness quality gate：自动检查机制、指标、负对照、证据绑定、失败标准和执行产物，减少表面化 idea。<br>- execution-feedback repair：IAD 从全局阈值失败进入类别感知校准。 |
| 技术落地性 | 20% | 已有脚本、schema、报告、Docker/调用说明和真实数据 smoke-test scaffold。 | - 提供 focused_workflow、researcharena、iad_mvp 三类代码入口。<br>- 提供 Dockerfile、部署说明和本地脚本调用流程。<br>- IAD V1.5->V1.6：FPR 0.574257 -> 0.009901。<br>- 明确声明 lightweight scaffold 边界，不虚称 IAD SOTA。 |
| 演示效果 | 20% | 三分钟展示完整闭环：任务输入、证据、idea、评审修复、证据核查、执行反馈。 | - 已生成三分钟视频脚本和静态 demo 页面。<br>- 演示主线聚焦 IAD execution-feedback case，视觉上清楚展示失败->诊断->修复。<br>- 辅助展示三任务 blind review sanity check，但不把少量人工评审包装成主证据。 |

## 关键数字

- 最终研究方案数：3
- 自动 depth/readiness 质量门均分：0.905
- IAD FPR 修复：0.574257 -> 0.009901
- IAD V1.7 balanced score：0.425705
- 三方向辅助评审 sanity check：39/15/6 wins/losses/ties, tie-half win rate=0.7

## 三分钟演示主线

1. 输入科研任务：IAD / 物理属性 / 室内 3D。
2. 系统检索论文并形成 evidence baseline cards。
3. 生成细粒度 idea 和实验计划。
4. 多模型匿名盲评发现问题，targeted repair 修复 idea。
5. reference claim verification 检查论文证据。
6. 自动 depth/readiness gate 检查方案是否足够细粒度和可执行。
7. IAD 接入真实数据，发现全局阈值失败并自动修复。

## 诚实边界

- 人工评审样本小，只作为 sanity check。
- IAD 是 lightweight execution-feedback scaffold，不声称完整 IAD benchmark 或 SOTA。
- 室内 3D 使用 seeded evidence bank，需透明披露。
- 当前重点是科研自动化 workflow，而不是单点 CV 算法。
