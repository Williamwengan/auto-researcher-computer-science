# AI4S Research Agent 智能体详细设计文档

生成日期：2026-07-26

项目名称：AI4S Research Agent

提交方向：推动 AI for Science 发展，促进人工智能赋能科学发现

## 1. 一句话说明

AI4S Research Agent 是一个面向科研自动化的智能体系统。用户只需要输入“研究方向、具体想做的任务、任务类型”，系统会自动完成论文证据检索、baseline 缺陷分析、细粒度 idea 生成、自动评分、多模型评审、critic repair、证据校验、实验计划生成，并进一步进入授权实验执行与论文草稿生成。

本项目的核心不是单独提出某一个 CV 算法，而是搭建一个可审计、可修复、可评价、可进入实验执行阶段的科研工作流智能体。

## 2. 设计目标

传统大模型生成科研 idea 时常见问题包括：

- idea 太宽泛，只像选题描述，不像可执行研究方案；
- 与已有论文、baseline 和数据集缺少明确绑定；
- 缺少实验计划、消融实验、负控制和成功阈值；
- 生成后没有独立评审和修复闭环；
- idea 与后续实验执行脱节，难以从“想法”走向“结果”和“论文”。

本系统针对这些问题设计了完整 pipeline：

```text
输入科研任务
→ 论文检索和证据整理
→ baseline cards 与 baseline weakness 分析
→ 生成细粒度候选 idea
→ 生成实验计划
→ 自动质量评分
→ multi-LLM anonymous blind review
→ critic repair
→ reference claim verification
→ 输出最终候选 idea 与实验计划
→ 授权进入实验执行对话舱
→ 准备 runner / 数据 / baseline / proposed module
→ 读取指标
→ result-to-claim
→ 论文草稿
```

## 3. 用户输入与系统输出

### 3.1 用户输入

网页端输入包含三个字段：

| 字段 | 含义 | 示例 |
| --- | --- | --- |
| 研究方向 | 用户希望探索的科研问题背景 | 工业异常检测中的可信科研智能体 |
| 具体想做的任务 | 更具体的任务对象 | 工业异常检测 IAD + Agent |
| 任务类型 | 约束 idea 的改进方式 | 增量改进、指标提升、工程拼接、评价协议、系统优化 |

其中“任务类型”用于约束 idea 的形态。例如：

- 增量改进：在已有 baseline 上增加一个最小新模块；
- 指标提升：围绕主指标和失败样例设计增强模块；
- 工程拼接：把多个成熟模块组合成可运行 pipeline；
- 评价协议：设计 benchmark、负控制、评测维度或审查协议；
- 系统优化：提升鲁棒性、效率、可解释性或自动化程度。

### 3.2 系统输出

系统输出不是一句话 idea，而是一组可审计研究方案：

| 输出 | 说明 |
| --- | --- |
| 详细 idea 解释 | 说明方案到底想解决什么问题、核心假设是什么 |
| 相关 baseline | 系统检索或加载到的已有方法、论文和可复用组件 |
| baseline 空白/弱点 | 说明已有方法为什么不够、改进空间在哪里 |
| 改进点 | 相对 baseline 新增了什么模块、目标函数或验证机制 |
| 实验方案计划 | 数据集、脚本、指标、消融实验、负控制和成功阈值 |
| 证据摘要 | 论文数量、baseline card 数量、claim verification 状态 |
| 实验入口 | 进入实验执行对话舱，授权后运行 scaffold 或任务 runner |

## 4. 系统总体架构

系统由两层组成：

### 4.1 Phase 1：自动化 Idea 挖掘

Phase 1 负责从科研任务生成高质量研究方案。主要模块如下：

```text
Task Spec Parser
→ Paper Retrieval Agent
→ Baseline Card Agent
→ Focused Idea Generator
→ Idea Quality Scorer
→ Blind Review / Critic Agent
→ Repair Agent
→ Reference Claim Verifier
→ Final Plan Selector
```

### 4.2 Phase 2：实验执行对话舱

Phase 2 负责把最终方案推进到实验执行。主要模块如下：

```text
Final Plan Reader
→ Experiment Workspace Builder
→ Dataset / Environment Checker
→ Human Authorization Gate
→ Baseline Runner
→ Proposed Runner
→ Metrics Reader
→ Result-to-Claim Mapper
→ Paper Draft Writer
```

网页端不会执行用户输入的任意 shell 命令。所有执行动作都通过 allowlist 后端接口和人工授权触发，避免不受控运行。

## 5. 核心模块设计

### 5.1 Task Spec Parser

该模块把用户自然语言输入转换成结构化科研任务，包括：

- task name；
- research direction；
- task mode；
- expected output schema；
- candidate datasets；
- candidate metrics；
- baseline retrieval query。

这样做的原因是：如果直接把一句话交给大模型生成 idea，很容易得到泛泛的“套话式科研方案”。结构化 task spec 能把任务空间收紧，让后续模块知道应该生成哪种类型的 idea。

### 5.2 Paper Retrieval Agent

该模块负责检索并整理论文证据。对已验证的三个方向，系统会优先加载本项目已经整理好的 evidence artifacts；对陌生方向，系统会尝试在线检索候选论文，并生成 retrieved / unverified 状态的 papers。

输出包括：

- `papers.jsonl`；
- 论文标题、年份、来源、链接；
- paper-to-claim 候选证据；
- baseline 方法线索；
- dataset / metric 线索。

重要边界：陌生方向的在线检索结果在完成 reference claim verification 前，只能作为候选证据，不能直接写成强结论。

### 5.3 Baseline Card Agent

该模块把论文和已有 artifacts 组织成 baseline cards。每张 baseline card 描述：

- baseline 名称；
- 方法类型；
- 可复用组件；
- 已知局限；
- 可对比指标；
- 关联论文证据。

baseline cards 是后续 idea generation 的“地基”。系统不是直接问模型“有什么好 idea”，而是先问：已有方法是什么？它们哪里不够？哪些模块可以复用？哪些缺陷值得针对性改进？

### 5.4 Focused Idea Generator

该模块生成细粒度候选 idea。每个 idea 必须包含：

- title；
- core hypothesis；
- minimal new module；
- algorithmic objective；
- baseline weakness addressed；
- required datasets；
- required scripts；
- metrics；
- ablations；
- negative controls；
- success thresholds；
- risks and fallback。

这一步是本项目相对普通大模型 idea generation 的关键改进：系统强制 idea 绑定 baseline、数据、脚本、指标和失败检查，减少“只会讲愿景”的问题。

### 5.5 Idea Quality Scorer

系统对候选 idea 进行自动评分，维度包括：

- novelty；
- excitement；
- feasibility；
- expected effectiveness；
- overall；
- baseline grounding；
- experimental rigor；
- mechanism specificity；
- implementation readiness。

评分不是为了替代真实评审，而是为了自动筛选、排序，并为后续 repair 提供诊断信号。

### 5.6 Multi-LLM Anonymous Blind Review

系统把 repair 前后的 idea 构造成匿名 A/B 评审包，让评审模型不知道哪个是 before，哪个是 after。评审维度采用 Si et al. (2024)-style research idea benchmark 的核心思想，并扩展到科研自动化场景。

已经完成的代表性结果：

| 方向 | 结果摘要 |
| --- | --- |
| IAD + Agent | v0.6 blind A/B：7/9 after wins；Si-style 5 judge 报告中 after win rate 60% |
| 物理属性预测 | v1 repair 失败后定位机制错配；v2 repair 后 18/18 after wins |
| 室内单图 3D 场景 | v0.6/v0.7 结果强，需透明披露 seeded evidence bank |

### 5.7 Critic Repair Agent

该模块不是简单润色，而是根据 reviewer rationale 定位具体问题，例如：

- 机制与任务错配；
- baseline 对比不公平；
- 实验计划缺少负控制；
- claim 缺少论文证据；
- implementation path 不清楚；
- 任务类型约束没有真正影响 idea。

修复后系统会再次 blind review，检查 repair 是否真的提高质量。

### 5.8 Reference Claim Verifier

该模块检查 idea 中的 claim 是否有论文证据支持。输出类别包括：

- supported；
- weakly_supported；
- needs_manual_check；
- unsupported；
- declared_unsupported。

最终报告中的 claim 必须满足两类条件之一：

1. 绑定明确论文证据；
2. 明确标记为待核查、计划项或未验证假设。

### 5.9 Research Agent Orchestrator

为了支持评委输入陌生方向，系统新增了 `research_agent_orchestrator`：

```text
TaskSpecAgent
→ PaperRetrievalAgent
→ BaselineCardAgent
→ IdeaGenerationAgent
→ ExperimentPlannerAgent
→ RunnerBuilderAgent
```

它能为任意新方向生成：

- `task_spec.yaml`；
- `paper_retrieval_plan.json`；
- `papers.jsonl`；
- `baseline_cards.jsonl`；
- `focused_ideas.json`；
- `experiment_plan.json`；
- `runner_plan.json`；
- `runner_scaffold/run_all.sh`；
- `RESEARCH_AGENT_REPORT_CN.md`。

陌生方向当前可以完成 workflow 接入、候选论文检索、baseline cards、idea 和实验计划草案生成，并生成 runner scaffold。真实 benchmark 级实验仍需要补充该领域数据集、baseline 代码和 metric parser。

## 6. 网页 Demo 设计

网页分为两个互斥视图。

### 6.1 Phase 1：自动化 Idea 挖掘视图

左侧为输入控制中心：

- 研究方向；
- 具体想做的任务；
- 任务类型；
- 进度追踪时间轴。

右侧只展示最终候选方案，不堆叠冗长中间卡片。输出包括：

- idea 标题；
- 详细 idea；
- baseline；
- 命中论文；
- 改进点；
- 实验计划；
- 证据摘要；
- 进入实验对话舱按钮。

### 6.2 Phase 2：实验执行对话舱

Phase 2 是对话式实验执行界面，包含：

- 模型选择；
- API Base URL；
- API Key 模式；
- 实验工作区；
- 数据集路径；
- 执行模式；
- 对话输入框；
- 授权按钮；
- 实验日志和结果气泡。

该视图用于展示“科研方案如何进入实验执行”，而不是静态报告展示。

## 7. 已验证方向与陌生方向的处理差异

| 输入类型 | 系统行为 | 输出可信度 |
| --- | --- | --- |
| 已验证方向：IAD、物理属性、室内 3D | 读取已完成的 workflow artifacts，展示完整 idea、baseline、评审、repair、证据校验和实验计划 | 已验证 workflow 结果 |
| 陌生方向 | 实时解析任务，尝试在线论文检索，生成 baseline cards、focused idea、实验计划和 runner scaffold | 候选方案，证据为 retrieved/unverified |
| 陌生方向真实实验 | 需要用户提供数据集、baseline 实现、metric parser 或授权 agent 继续构建 runner | 不伪造实验结论 |

这种设计保证系统在比赛演示中可泛化到新输入，同时不把未验证内容包装成已验证结论。

## 8. 代表性结果

### 8.1 Idea Generation + Repair + Evaluation

| 方向 | 关键结果 |
| --- | --- |
| IAD + Agent | v0.6 blind A/B：7/9 after wins；后续接入 MVTec AD smoke test |
| 物理属性预测 | v1 repair 失败后通过 rationale 定位机制错配；v2 repair 获得 18/18 after wins |
| 室内 3D 场景生成 | after idea 在 blind review 中明显优于 before；evidence-card repair 后 claim verification pass rate 1.0 |

### 8.2 Reference Claim Verification

| 方向 | Claims | Pass Rate | 说明 |
| --- | ---: | ---: | --- |
| IAD + Agent | 21 | 0.857 | unsupported=0，保留 needs_manual_check |
| 物理属性预测 v2 | 15 | 1.0 | evidence-card repair 后通过 |
| 室内 3D 场景 | 18 | 1.0 | 使用 seeded evidence bank，报告中透明披露 |

### 8.3 Execution Feedback Case

IAD 方向接入 MVTec AD 数据后，系统从执行反馈中发现全局阈值迁移失败：

```text
V1.5 global threshold FPR = 0.574257
```

随后进行类别感知阈值校准：

```text
V1.6 per-category FPR = 0.009901
```

这说明系统不仅能生成 idea，还能把真实执行失败转化为诊断与修复信号。

## 9. 技术创新点

| 痛点 | 本系统设计 |
| --- | --- |
| idea 空泛 | 强制 minimal module、objective、data、scripts、metrics、negative controls |
| 缺少论文证据 | paper retrieval、baseline cards、reference claim verification |
| repair 越修越差 | blind A/B review + reviewer rationale diagnosis |
| 只生成不执行 | final plan 转实验工作区，支持授权 runner 和 result-to-claim |
| 陌生方向不可测 | Research Agent Orchestrator 实时生成任务接入、论文检索、baseline cards、idea、runner scaffold |
| 安全风险 | 网页不执行任意命令，实验动作通过固定 allowlist 与人工授权触发 |

## 10. 工程结构

核心目录如下：

```text
competition_final_submission_20260725/
├── 01_design_doc/
│   └── AI4S_AGENT_DETAILED_DESIGN_CN.md / .docx
├── 02_deployment/
│   └── DEPLOYMENT_AND_API_GUIDE_CN.md / .docx
├── 03_demo_video/
│   └── demo_assets/
│       ├── AI4S_RESEARCH_AGENT_DEMO.html
│       └── start_demo_server.py
├── focused_workflow/
│   ├── scripts/
│   └── tasks/
├── research_agent_orchestrator/
├── iad_mvp/
├── generic_mvp/
├── outputs/
├── execution_runs/
└── Dockerfile
```

## 11. 安全与边界说明

本项目明确不声称：

- 已完成所有 AI4S 方向的真实 benchmark；
- 陌生方向可以在没有数据、没有 baseline 代码、没有 metric parser 时直接获得真实实验结论；
- IAD scaffold 是完整 PatchCore/anomalib SOTA benchmark；
- 小规模专家评审具有大样本统计显著性；
- 未完成 verification 的论文 claim 是最终事实。

系统会诚实地区分：

- verified workflow result；
- retrieved / unverified evidence；
- planned experiment；
- smoke runner result；
- real benchmark result。

## 12. 评审使用建议

评委可以按以下方式测试：

1. 输入已验证方向，例如“工业异常检测 IAD + Agent”，查看完整 workflow 输出；
2. 输入陌生方向，例如“遥感变化检测可信解释”，查看系统是否能实时生成候选论文、baseline cards、idea 和实验计划；
3. 点击进入实验对话舱，查看授权执行、runner scaffold、指标读取和论文草稿流程；
4. 通过 HTTP API 直接调用 `/api/live_workflow/start` 和 `/api/live_workflow/status` 获取 JSON 结果。

本系统更适合被评价为“科研自动化智能体工作流”，而不是单点算法 demo。
