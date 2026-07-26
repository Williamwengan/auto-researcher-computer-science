# v0.5 论文检索与 Baseline 证据绑定阶段报告

## 1. 当前结论

当前不写最终智能体设计文档，先完成 v0.5 的核心闭环是合理的。

本阶段已经实现并离线验证了第一个关键模块：

```text
任务约束 YAML
-> 自动生成论文检索 query
-> 检索/整理候选论文
-> 生成 evidence-grounded baseline cards
-> 生成证据上下文
-> 自动校验证据质量
```

这一步的作用是减少 idea generation 的空泛问题。后续生成 idea 时，系统不再只依赖 prompt 或模型常识，而是可以要求每个 baseline、改进点和实验计划都绑定到真实论文、代码线索或 baseline 缺陷。

## 2. 新增文件

### 2.1 论文证据检索脚本

```text
focused_workflow/scripts/retrieve_paper_evidence.py
```

功能：

- 读取 task spec 中的 `candidate_baselines`、`focus_area`、`research_goal`。
- 为每个 baseline 自动构造检索 query。
- 支持 OpenAlex、arXiv、Semantic Scholar 三类公开论文检索源。
- 生成论文记录 `papers.jsonl`。
- 生成证据绑定 baseline card：`evidence_baseline_cards.jsonl`。
- 生成给后续 idea agent 使用的上下文：`evidence_context.md`。
- 生成引用校验报告：`reference_verification_report.md`。
- 支持 `--no-network` 离线模式，先验证 pipeline，不访问外网。

### 2.2 证据质量校验脚本

```text
focused_workflow/scripts/validate_paper_evidence.py
```

功能：

- 校验 `papers.jsonl` 和 `evidence_baseline_cards.jsonl` 的字段完整性。
- 检查 baseline card 是否真实绑定论文。
- 统计 weak / medium / strong evidence card 数量。
- 统计论文 URL、摘要、baseline tags 是否存在。
- 输出中文质量报告：`evidence_quality_report_CN.md`。
- 输出机器可读汇总：`evidence_quality_summary.json`。

### 2.3 v0.5 一键运行脚本

```text
focused_workflow/scripts/run_paper_evidence_v0_5.sh
```

功能：

- 一条命令完成 evidence retrieval + evidence validation。
- 默认使用时间戳输出目录，避免覆盖之前结果。
- 默认 `--no-network`，需要真实论文检索时显式加 `--network`。
- 支持 `--strict`，用于正式评测时拒绝 weak-only 结果。

### 2.4 新增 schema

```text
focused_workflow/schemas/paper_evidence.schema.json
focused_workflow/schemas/evidence_baseline_card.schema.json
```

作用：

- 固定论文证据和 baseline evidence card 的结构。
- 让后续自动校验、自动评分、critic-repair 可以读取统一格式。

### 2.5 新增 evidence-grounded prompt

```text
focused_workflow/prompts/evidence_grounded_ideation_prompt.md
```

作用：

- 后续 idea generation 必须读取 `evidence_context.md`。
- 每个 idea 必须说明基于哪些 baseline 证据、发现了什么 baseline 缺陷、改进点由哪条证据支撑。
- 如果没有证据，必须显式标记 unsupported，不允许伪装成确定事实。

## 3. 已完成的验证

### 3.0 最新联网检索结论

已经将默认检索源收敛为：

```text
OpenAlex
```

原因：

- OpenAlex 在当前服务器环境中可稳定访问。
- arXiv 和 Semantic Scholar 在前一轮运行中出现连接拒绝，导致大量非关键错误日志。
- 使用 OpenAlex-only 后，日志更干净，也更适合作为比赛演示中的默认配置。

同时，已为 ObjectFolder / ObjectFolder2.0 增加专门 query：

```text
ObjectFolder dataset implicit visual auditory tactile representations
ObjectFolder 2.0 multisensory object dataset sim2real transfer
ObjectFolder 2.0 visual tactile acoustic household objects
ObjectFolder 2.0 contact localization shape reconstruction object scale estimation
```

这解决了上一轮物理属性方向中 ObjectFolder2.0 没有证据绑定的问题。

### 3.1 最新 IAD + Agent Workflow 联网结果

最新输出目录：

```text
outputs/v05_paper_evidence_05_iad_agent_workflow_20260712_100802/paper_evidence
```

结果：

```text
Queries: 24
Papers: 24
Evidence baseline cards: 12
Cards with evidence: 12
Strong evidence cards: 11
Medium evidence cards: 1
Weak evidence cards: 0
Unsupported claim cards: 0
Schema errors: 0
Retrieval errors: 1
```

说明：

- IAD 的 12 个 baseline 全部绑定到了论文证据。
- 唯一检索错误是 OpenAlex 对 CLIP 的一个 query 返回 `HTTP 429 Too Many Requests`。
- 该错误不影响最终证据覆盖，因为 CLIP 仍然绑定了 3 篇论文证据。
- 因此 IAD 方向可以进入 evidence-grounded idea generation。

### 3.2 最新 Physical Property Prediction 联网结果

最新输出目录：

```text
outputs/v05_paper_evidence_01_physical_property_prediction_20260712_100653/paper_evidence
```

结果：

```text
Queries: 29
Papers: 51
Evidence baseline cards: 12
Cards with evidence: 12
Strong evidence cards: 12
Weak evidence cards: 0
Unsupported claim cards: 0
Schema errors: 0
Retrieval errors: 0
```

说明：

- 物理属性方向的 12 个 baseline 全部绑定到了论文证据。
- ObjectFolder2.0 已从 weak evidence 修复为 strong evidence。
- ObjectFolder2.0 当前绑定到的关键论文包括：

```text
ObjectFolder 2.0: A Multisensory Object Dataset for Sim2Real Transfer
```

因此物理属性方向也可以进入 evidence-grounded idea generation。

## 4. 早期离线验证记录

### 4.1 IAD + Agent Workflow

运行输出：

```text
outputs/v05_paper_evidence_05_iad_agent_workflow_20260712_094533/paper_evidence
```

结果：

```text
Queries: 24
Papers: 0
Evidence baseline cards: 12
Schema errors: 0
Weak cards: 12
```

解释：

- schema 和目录结构已经跑通。
- 因为使用 `--no-network`，没有真实论文，因此 12 个 baseline card 都是 weak evidence。
- 这不是失败，而是离线模式的预期结果。

### 4.2 Physical Property Prediction

运行输出：

```text
outputs/v05_paper_evidence_01_physical_property_prediction_20260712_094541/paper_evidence
```

结果：

```text
Queries: 24
Papers: 0
Evidence baseline cards: 12
Schema errors: 0
Weak cards: 12
```

解释：

- 物理属性方向也完成了同样的离线结构验证。
- 说明 v0.5 evidence module 对不同任务 YAML 是可复用的。

## 5. 当前还没有完成的部分

当前已经完成 IAD 和物理属性两个方向的真实论文证据绑定。

下一步不再是继续做普通检索，而是把证据上下文接入 idea generation。

如需重新运行 evidence retrieval，可使用：

```bash
cd /data1/huangyuling/-A_HYL/AI4S/ResearchArena-main

bash focused_workflow/scripts/run_paper_evidence_v0_5.sh \
  --task-spec focused_workflow/tasks/benchmark_cv/05_iad_agent_workflow.yaml \
  --network --strict

bash focused_workflow/scripts/run_paper_evidence_v0_5.sh \
  --task-spec focused_workflow/tasks/benchmark_cv/01_physical_property_prediction.yaml \
  --network --strict
```

理想结果应该保持：

```text
Papers > 0
Cards with evidence > 0
Weak cards 下降
Strong / medium evidence cards 上升
Schema errors = 0
```

如果 `--strict` 失败，说明检索结果不足，不能进入 evidence-grounded idea generation，需要调整 query 或补充人工 baseline 文献。

## 6. v0.5 对比赛方案的意义

这个模块让 workflow 从：

```text
模型根据任务描述直接生成 idea
```

升级为：

```text
先检索 baseline 与论文证据
再基于 evidence cards 生成 idea
再校验每个 idea 是否真的 grounded
```

这对比赛很重要，因为你们可以证明：

- idea 不是凭空生成的；
- baseline 来源可追踪；
- 每个改进点需要绑定论文证据或 baseline 缺陷；
- unsupported claim 会被显式暴露；
- 系统可以量化 evidence coverage，而不是只靠人工感觉。

## 7. 下一步

下一步不写最终设计文档。

下一步应该做：

```text
把 evidence_context.md 接入 idea generation prompt
-> 重新生成 IAD 和物理属性两个方向的 evidence-grounded ideas
-> 校验每个 idea 是否引用了 evidence card
-> 对比 v0.4 idea 与 v0.5 evidence-grounded idea
```

v0.5 的下一阶段是：

```text
Evidence-grounded Idea Generation
```

也就是让系统读取真实论文证据后重新生成 IAD 和物理属性两个方向的 idea，并和 v0.4 的 idea 做对比。
