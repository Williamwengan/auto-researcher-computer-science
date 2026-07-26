# V0.9 Idea Generation Core Benchmark Report

生成时间：2026-07-13 08:51:51

生成脚本：`focused_workflow/scripts/build_v09_idea_generation_core_benchmark_report.py`

## 一句话定位

V0.9 的目标不是新增任务，也不是选择一个任务作为比赛方向，而是把已经完成闭环的 3 个 benchmark 样本收束成一个清楚的结论：

> 本项目的核心贡献是一个跨任务、证据驱动、可修复、可评价的科研 idea generation 模块。给定不同 task_spec，它能生成更细粒度、更可实现、更可验证的 focused ideas，并通过 targeted repair、multi-LLM blind A/B judge 和 reference claim verification 形成闭环。

## 为什么先不管 02/04

02 Human Motion 和 04 3D Reconstruction 仍然保留为 held-out benchmark samples，但当前阶段先不继续消耗 API 或扩任务。原因是：已有 01/03/05 三个样本已经覆盖了三类关键能力：

- 01 物理属性预测：机制错配诊断和二次修复。
- 03 室内单图 3D：复杂生成/重建任务上的 evidence-grounded ideation。
- 05 IAD + Agent：agentic workflow 和工程可执行字段。

这三个样本足够支撑“idea generation 模块已经成型”的阶段性论证。后续 02/04 的价值是进一步验证泛化，而不是当前阶段的阻塞项。

## Pipeline 演进

| 版本 | 目标 | 产物/能力 |
| --- | --- | --- |
| v0.2 | 固定 task_spec 输入和结构化输出 | baseline_cards.jsonl、focused_ideas.json、experiment_plan.json |
| v0.3 | 让 idea 可实现 | minimal_new_module、algorithmic_objective、required scripts/data、expected tables/figures、success thresholds、negative controls |
| v0.4 | 加入 idea quality scoring 和 judge 规划 | 把 idea 从“生成”推进到“可评价” |
| v0.5 | evidence-grounded ideation + targeted repair | paper evidence、evidence baseline cards、evidence critic repair |
| v0.6 | multi-LLM anonymous blind A/B judge | 验证 repair 后 idea 是否真的更好 |
| v0.7 | reference claim verification | 检查 claim 是否有 paper id 和 title/abstract/card 支撑 |
| v0.8 | cross-task benchmark robustness summary | 纠正为 benchmark 样本视角，不是单任务选择器 |
| v0.9 | idea generation core benchmark report | 把 3 个强样本收束成核心模块证据 |

## 三个强样本的证据表

| ID | 样本任务 | 角色 | 证明能力 | v0.6 blind A/B | v0.7 claim verification |
| --- | --- | --- | --- | --- | --- |
| 01 | 物理属性预测 | failure diagnosis and second-round repair | idea generation 模块能发现机制错配，并通过 targeted repair 生成更一致、更可实现的 idea。 | v2: 6 reviewers, 18/18 after wins, win rate 1.0, agreement 1.0 | v2 evidence-card repair: papers 51, claims 15, pass rate 1.0 |
| 03 | 室内单图 3D 场景生成 | complex generation/reconstruction generalization | idea generation 模块能迁移到复杂 3D/generation/reconstruction 任务，并用 evidence bank 限制空泛想法。 | 3 reviewers, 9/9 after wins, win rate 1.0, agreement 1.0 | evidence-card repair: papers 18, claims 18, pass rate 1.0 |
| 05 | 工业异常检测 IAD + Agent | agentic workflow and implementation readiness | idea generation 模块能处理 agent workflow、retrieval、verification loop、human escalation 和工业指标。 | 3 reviewers, 7/9 after wins, win rate 0.778, agreement 0.778 | papers 24, claims 21, pass rate 0.857, unsupported 0, manual 3 |

## 样本详情

### 01 物理属性预测

证明能力：idea generation 模块能发现机制错配，并通过 targeted repair 生成更一致、更可实现的 idea。

修复/验证故事：v1 repair 后 after win rate 只有 0.556。reviewer rationale 指出 Idea 2 和 Idea 3 错误套用了 Idea 1 的 interval-mapper loss。v2 将三个 idea 的机制拆开：interval mapper、localized material evidence verifier、proposal uncertainty propagation。

盲评结果：v2: 6 reviewers, 18/18 after wins, win rate 1.0, agreement 1.0

证据校验：v2 evidence-card repair: papers 51, claims 15, pass rate 1.0

边界：

- 真实物理属性标签和可控实验验证仍然较难。
- 适合证明 idea repair 能力，不应包装成已经完成物理属性预测算法 SOTA。

展示用途：作为最强技术闭环案例，展示系统能从失败中定位原因并二次修复。
### 03 室内单图 3D 场景生成

证明能力：idea generation 模块能迁移到复杂 3D/generation/reconstruction 任务，并用 evidence bank 限制空泛想法。

修复/验证故事：初始联网检索阶段 evidence bank 为空，后续构造 seeded evidence bank，覆盖 Text2Room、SceneScape、WonderJourney、DUSt3R、MASt3R、3D Gaussian Splatting、NeRF、HorizonNet、MiDaS、3D-FRONT、Matterport3D、ScanNet、Structured3D、Hypersim 等代表性证据。

盲评结果：3 reviewers, 9/9 after wins, win rate 1.0, agreement 1.0

证据校验：evidence-card repair: papers 18, claims 18, pass rate 1.0

边界：

- 使用 seeded evidence bank，最终材料必须透明披露。
- 完整 3D 工程实现较重，当前主要作为 idea generation 泛化样例。

展示用途：作为视觉化和复杂任务泛化样例，证明 workflow 不局限于工程 agent 任务。
### 05 工业异常检测 IAD + Agent

证明能力：idea generation 模块能处理 agent workflow、retrieval、verification loop、human escalation 和工业指标。

修复/验证故事：targeted repair 将 IAD idea 约束到 normal reference retrieval、reference consistency score、cross-model disagreement、evidence-grounded report checker、negative controls 和 success thresholds。

盲评结果：3 reviewers, 7/9 after wins, win rate 0.778, agreement 0.778

证据校验：papers 24, claims 21, pass rate 0.857, unsupported 0, manual 3

边界：

- 仍有 3 个 needs_manual_check claim，适合保留为诚实不确定性。
- 不要把它写成项目唯一方向；它是 agent/workflow 类任务的代表样本。

展示用途：作为工程可读性样例，展示输出字段如何服务实验计划和后续 workflow。

## 相比 ResearchArena baseline 的改进点

原始 ResearchArena baseline 更像开放式 proposal generation，容易出现 idea 太长、太泛、缺少最小实验和量化评价的问题。Focused Workflow 的改进点是：

- 输入层：固定 task_spec schema，让不同任务都能被同一套 workflow 接收。
- 生成层：要求 focused ideas 必须绑定 baseline weakness、direct baselines、transfer baselines 和 minimal_new_module。
- 实验层：每个 idea 必须给出 required scripts/data、expected tables/figures、success thresholds 和 negative controls。
- 修复层：用 critic/repair prompt 和后处理脚本定位机制错配、证据不足、评价缺口。
- 评价层：用 multi-LLM anonymous blind A/B judge 判断 repair 是否真的提高 idea 质量。
- 证据层：用 reference claim verification 检查 claim 是否有真实 paper id 和 title/abstract/card 支撑。

因此，当前贡献不应表述为“某个 CV 算法更强”，而应表述为“科研 idea generation 被改造成可控、可评价、可修复的跨任务 pipeline”。

## 当前可主张与不可主张

可以主张：

- 已经完成一个跨任务 idea generation workflow 雏形。
- 已经在 3 个代表性 benchmark 样本上验证生成、修复、盲评、证据校验闭环。
- 物理属性样本提供最强 failure -> diagnosis -> repair -> re-evaluation 案例。
- IAD + Agent 样本证明输出字段能支持工程 workflow。
- 室内 3D 样本证明复杂生成/重建方向也能进入同一套 evidence-grounded ideation 流程。

不应主张：

- 不应说已经完成所有 5 个 benchmark 的完整闭环。
- 不应说已经证明全球意义上的 idea generation SOTA。
- 不应把 IAD、物理属性或室内 3D 表述成唯一比赛方向。
- 不应隐瞒室内 3D 使用 seeded evidence bank。

## 下一步进入完整工作流

V0.9 之后，建议从 idea generation core 进入 end-to-end workflow demo：

1. 固定一个小型 task_spec 输入样例。
2. 展示 baseline cards、focused ideas 和 experiment plan 的结构化输出。
3. 展示 targeted repair 前后差异。
4. 展示 blind A/B judge 和 reference claim verification 如何反馈到 idea 修复。
5. 进一步连接到实验执行 planning、代码/数据 artifact planning 和最终报告生成。

这一步才是从“idea generation 模块强”走向“完整 AI 科研自动化 workflow 可运行”。
