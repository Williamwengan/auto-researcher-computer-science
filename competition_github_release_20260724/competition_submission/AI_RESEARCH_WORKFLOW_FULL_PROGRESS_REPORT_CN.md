# AI 科研自动化工作流项目完整进展汇报

## 1. 项目背景

本项目最初的目标是参加 AI4Sci / 挑战杯类比赛，希望基于已有科研自动化项目搭建一个自己的 AI 科研工作流。早期我们考虑过复现和改进 `Auto-claude-code-research-in-sleep-main`，但在实际使用中发现，该项目的 idea 生成阶段存在明显问题：

1. 生成的 idea 容易空泛；
2. 缺少明确 baseline；
3. 缺少可执行实验计划；
4. 缺少量化评价指标；
5. 缺少论文证据链；
6. 难以证明生成的 idea 真的比原始流程更好。

因此，我们后续将重点转向老师提供的 ResearchArena baseline，并在其基础上搭建自己的 focused research workflow。我们的目标不是单独提出一个 CV 算法，而是构建一个可以辅助科研团队完成 idea 生成、修复、评估和证据校验的智能体工作流。

## 2. 总体目标

我们希望系统输入：

```text
研究方向 + 具体任务类型 + baseline / 约束条件
```

系统输出：

```text
baseline-grounded idea
详细机制解释
实验计划
评价指标
negative controls
多模型评审结果
论文证据支持检查结果
```

也就是说，我们不是简单让 LLM 生成一段研究想法，而是让系统形成完整闭环：

```text
生成 idea
→ 证据绑定
→ 定向修复
→ 多模型匿名评估
→ 证据 claim 验证
→ 失败诊断
→ 二次修复
```

## 3. Baseline 选择：从 Auto-claude 转向 ResearchArena

老师给出的主要 baseline 是 ResearchArena。我们将其克隆到：

```text
/data1/huangyuling/-A_HYL/AI4S/ResearchArena-main
```

我们首先尝试跑通 ResearchArena 的基本流程，然后基于它构建自己的 focused workflow。

选择 ResearchArena 的原因是：它比普通 prompt-based idea generation 更接近科研自动化 benchmark，关注 agent 在科研任务中的完整表现。但原始 ResearchArena 仍存在以下不足：

1. idea 生成不够聚焦；
2. 输出不够细；
3. 缺少严格 schema；
4. 缺少多模型评估；
5. 缺少 repair 闭环；
6. 缺少论文证据验证。

因此，我们没有直接把 ResearchArena 当成最终方案，而是把它作为 baseline，在其基础上逐步加入 focused task spec、evidence grounding、targeted repair、multi-LLM judge 和 reference claim verification。

## 4. 环境和 API 配置

### 4.1 Codex 路径问题

最初运行 ResearchArena 时出现：

```text
Error running agent: [Errno 2] No such file or directory: 'codex'
```

原因是服务器环境中的 `codex` 不在 `PATH` 中。后来我们在 VSCode 插件目录中找到了 Codex binary，例如：

```text
/data1/huangyuling/.vscode-server/extensions/openai.chatgpt-.../bin/linux-x86_64/codex
```

并通过设置 `PATH` 解决。

### 4.2 API 额度问题

由于 Codex 周额度有限，我们配置了外部 API 中转：

1. EstelleCode：用于 GPT、Claude、Claude-max；
2. 云雾 API：用于 Gemini、DeepSeek、Qwen3-thinking。

最终我们可以用于评估的模型包括：

```text
gpt-5.5
claude-sonnet-4-6
claude-max
gemini-2.5-pro
deepseek-r1
qwen3-235b-a22b-thinking
```

这样做的作用是：

1. 节省 Codex 额度；
2. 让大规模 judge 评估不依赖单一模型；
3. 支持 multi-LLM evaluation；
4. 提高评估可信度。

## 5. focused workflow v0.2：固定输入格式和结构化输出

我们首先构建了 focused workflow，让输入不再是随便一句研究方向，而是结构化任务规范。

任务文件包括：

```text
domain
focus_area
research_goal
input
output
task_types
candidate_baselines
metrics
constraints
```

最早验证方向是：

```text
object-level physical property prediction from 2D indoor scene images
```

后来扩展到多个 CV 方向：

```text
01 physical property prediction
02 human motion generation
03 single-image 3D indoor scene generation
05 IAD + agent workflow
```

v0.2 要求输出三个核心文件：

```text
baseline_cards.jsonl
focused_ideas.json
experiment_plan.json
```

这样后续才能进行自动检查、自动评分和 review-ready markdown 生成。

v0.2 主要解决的问题是：

1. idea 太散；
2. 没有 baseline；
3. 没有指标；
4. 没有实验计划；
5. 输出格式不稳定。

但 v0.2 仍然存在问题：它只是让输出结构化，idea 仍然可能空泛。

## 6. focused workflow v0.3：让 idea 更可实现

为了解决 idea 只是 proposal、不够落地的问题，我们在 v0.3 中要求每个 idea 必须包含：

```text
minimal_new_module
algorithmic objective
required scripts
required data files
expected tables
expected figures
success thresholds
negative controls
```

也就是说，每个 idea 必须回答：

1. 新模块是什么；
2. 输入是什么；
3. 输出是什么；
4. 怎么实现；
5. 需要哪些脚本；
6. 用哪些数据；
7. 怎么评估；
8. 失败标准是什么。

v0.3 的作用是把 idea 从：

```text
proposal
```

推进到：

```text
implementation-ready plan
```

但实际测试发现，部分方向的 idea 仍然有时偏空泛，或者只是把 baseline 拼接起来，因此我们继续加入评估和修复机制。

## 7. focused workflow v0.4：idea 质量评估和 multi-LLM judge

### 7.1 规则评分体系

我们构建了 idea quality 评估体系，包括：

```text
baseline_grounding
failure_mode_specificity
mechanism_specificity
metric_alignment
experiment_executability
falsifiability
novelty_proxy
distinctness
risk_awareness
implementation_readiness
```

规则评分可以检查 idea 是否完整、是否有 baseline、是否有实验计划、是否有 negative control。

### 7.2 为什么还需要 multi-LLM judge

规则评分有一个问题：可能被“刷分”。

例如，系统可以通过增加字段、增加脚本名、增加指标来提高规则分，但 idea 的机制不一定真的变好。因此，我们加入了 multi-LLM blind A/B judge。

### 7.3 匿名 A/B 盲评机制

对每个 idea，我们构造：

```text
before = 修复前 idea
after = 修复后 idea
```

然后随机打乱成：

```text
Version A
Version B
```

judge 不知道哪个是修复前，哪个是修复后。每个 judge 从以下维度评分：

```text
novelty
feasibility
expected_effectiveness
experimental_rigor
baseline_grounding
mechanism_specificity
implementation_readiness
overall
```

最终统计：

```text
after wins
before wins
ties
after win rate
mean pair agreement
dimension delta
```

这样可以避免我们只凭主观感觉说“修复后更好”。

## 8. focused workflow v0.5：论文检索和 evidence-grounded idea

v0.5 的核心目标是让 idea 不再只依赖模型常识，而是基于论文证据和 baseline card。

我们加入了以下脚本：

```text
retrieve_paper_evidence.py
run_paper_evidence_v0_5.sh
validate_paper_evidence.py
run_evidence_grounded_ideation_v0_5.sh
```

v0.5 会生成：

```text
papers.jsonl
evidence_baseline_cards.jsonl
evidence_quality_summary.json
evidence_quality_report_CN.md
```

每个 baseline card 包括：

1. baseline 名称；
2. baseline 类型；
3. 相关论文；
4. supported metrics；
5. known limitations；
6. reusable components；
7. evidence strength。

这样 idea 生成时可以明确知道：

```text
baseline 是什么
baseline 能做什么
baseline 的不足是什么
我们的 idea 改进在哪里
```

## 9. 三个主要验证方向

我们最终保留三个主要方向：

```text
1. 工业异常检测 IAD + Agent
2. 物理属性预测
3. 室内单图 3D 场景生成
```

选择原因：

1. IAD + Agent：工程 agent 工作流，容易展示；
2. 物理属性预测：多模态物理推理，贴近研究方向；
3. 室内 3D 场景生成：生成/重建类复杂 CV 任务，能测试 pipeline 鲁棒性。

这三个方向覆盖了不同类型的科研任务，有利于证明 workflow 的跨任务稳定性。

## 10. v0.5 targeted repair：第一次修复

我们对生成的 idea 进行 targeted repair，补充：

```text
algorithmic_objective
quantitative_success_thresholds
negative_controls
minimal_new_module
mvp_artifacts
implementation_plan
```

IAD 和室内 3D 的修复效果较好，但物理属性方向出现了一个关键问题。

## 11. 关键失败案例：物理属性 v1 repair 机制错配

物理属性方向第一次 repair 后，规则分看起来较高，但 blind A/B judge 结果不稳定：

```text
After wins: 5/9
Before wins: 4/9
After win rate: 0.556
```

特别是以下两个 idea 多数 judge 更喜欢 before：

```text
Idea 2: Localized Visual Evidence Verifier
Idea 3: Proposal Uncertainty Propagation
```

通过查看 reviewer rationale，我们发现原因是：

```text
v1 repair 把 Idea 1 的 interval-mapper loss 硬套到了 Idea 2 和 Idea 3 上。
```

Idea 1 是：

```text
Object-Conditioned Material Interval Mapper
```

它适合使用：

```text
calibrated interval loss
coverage penalty
width penalty
```

但 Idea 2 应关注：

```text
localized crop evidence
mask interior texture
counterfactual erasure
unsupported material claim detection
```

Idea 3 应关注：

```text
proposal ensemble
mask uncertainty
duplicate object rate
proposal entropy
visible object recall
```

因此，v1 repair 的问题不是不够详细，而是机制错配。

这个失败案例非常重要，因为它证明：

```text
规则评分高不等于 idea 真好。
```

如果没有 blind A/B judge，我们可能会误以为 v1 repair 成功。

## 12. 物理属性 v2：机制一致性二次修复

针对 v1 的失败，我们写了专门的二次修复脚本：

```text
apply_physical_property_v2_repair.py
```

修复策略：

1. Idea 1 保留 interval mapper 逻辑；
2. Idea 2 改为 localized material evidence verifier；
3. Idea 3 改为 proposal uncertainty propagation module。

物理属性 v2 重新进行 blind A/B judge，并使用 6 个模型：

```text
GPT
Claude
Claude-max
Gemini
DeepSeek
Qwen3-thinking
```

结果：

```text
Reviewers: 6
Total votes: 18
After wins: 18
Before wins: 0
After win rate: 1.0
Mean pair agreement: 1.0
```

维度提升：

```text
mechanism_specificity +4.611
experimental_rigor +3.833
implementation_readiness +3.667
overall +2.833
```

这说明系统不仅能生成 idea，还能：

1. 发现 repair 失败；
2. 根据 reviewer rationale 定位问题；
3. 进行二次机制一致性修复；
4. 用 multi-LLM blind judge 验证修复有效。

## 13. 室内 3D 方向：evidence bank 为空的问题

室内单图 3D 场景生成方向一开始论文检索失败：

```text
Available papers: 0
Used papers: 0
Errors: 3
Warnings: 3
```

原因是联网检索 OpenAlex / arXiv / Semantic Scholar 时出现 429 或空结果。

为避免 workflow 被检索失败卡死，我们引入 seeded evidence fallback，手动构造一批可靠 baseline evidence：

```text
Text2Room
SceneScape
WonderJourney
3D-SceneDreamer
DUSt3R
MASt3R
3D Gaussian Splatting
NeRF
NeRFVS
HorizonNet
MiDaS
3D-FRONT
Matterport3D
ScanNet
Structured3D
Hypersim
```

最终形成：

```text
18 papers
12 baseline evidence cards
```

需要注意：这个方向使用了 seeded evidence bank，最终比赛文档中必须如实说明。

## 14. v0.6 三方向 multi-LLM blind A/B 结果

v0.6 汇总报告位于：

```text
competition_submission/V06_MULTI_LLM_BLIND_AB_EVALUATION_REPORT_V2_CN.md
```

结果如下：

| 方向 | Reviewers | Votes | After Wins | Before Wins | After Win Rate | 结论 |
|---|---:|---:|---:|---:|---:|---|
| IAD + Agent | 3 | 9 | 7 | 2 | 0.778 | repair 后较优 |
| 物理属性预测 v2 | 6 | 18 | 18 | 0 | 1.0 | repair 后显著更优 |
| 室内单图 3D 场景生成 | 3 | 9 | 9 | 0 | 1.0 | repair 后显著更优 |

该结果说明：

1. targeted repair 在三个方向总体有效；
2. 物理属性方向经过 v2 修复后效果最明显；
3. 室内 3D 方向 repair 后也被所有 judge 认可；
4. IAD 方向有效，但仍存在少量分歧。

## 15. v0.7 Reference Claim Verification

v0.6 证明 repair 后 idea 在 blind judge 下更好，但仍有一个问题：

```text
idea 里说某个 baseline 有某个缺陷，这句话到底有没有论文证据支持？
```

因此我们实现了：

```text
verify_reference_claims.py
```

它会检查：

1. claim 是否绑定 paper id；
2. paper id 是否真实存在于 `papers.jsonl`；
3. claim 文本是否和论文 title / abstract / baseline card 有支持关系；
4. unsupported_or_weak_claims 是否被诚实保留；
5. proposed mechanism 是否只是相关组件支持，而不是被伪装成前人已证明。

状态分为：

```text
supported
weakly_supported
needs_manual_check
unsupported
declared_unsupported
```

## 16. v0.7 初始问题和 evidence-card repair

v0.7 初始结果显示：

```text
IAD pass rate = 0.857
物理属性 v2 pass rate = 0.533
室内 3D pass rate = 0.2
```

这说明 idea 质量已经提高，但证据链不够干净。

### 16.1 室内 3D evidence-card repair

室内 3D 的问题是 `baseline_weakness_evidence` 里很多只是 paper id，例如：

```text
seed:text2room_2023
```

系统不知道这篇论文支持哪个 baseline 缺陷，因此只能判为 `needs_manual_check`。

我们写了：

```text
repair_indoor3d_evidence_cards.py
```

它做了：

1. 把 paper id 改成结构化 claim；
2. 给 evidence_baseline_cards.jsonl 补 known_limitations；
3. 给 papers.jsonl 补更明确的 abstract note；
4. 重新跑 v0.7。

结果：

```text
修复前 pass rate = 0.2
修复后 pass rate = 1.0
supported = 12
weakly_supported = 3
needs_manual_check = 0
unsupported = 0
```

### 16.2 物理属性 v2 evidence-card repair

物理属性 v2 的问题是 claim 写得太抽象，证据 card 没有明确支持关系。

我们写了：

```text
repair_physical_v2_evidence_cards.py
```

修复对象包括：

```text
ObjectFolder / ObjectFolder2.0
CLIP
SAM / SAM2
GroundingDINO
VLM material claim evidence
proposal uncertainty evidence
```

结果：

```text
修复前 pass rate = 0.533
修复后 pass rate = 1.0
supported = 8
weakly_supported = 3
needs_manual_check = 0
unsupported = 0
```

## 17. 当前最终 v0.7 三方向结果

最终报告位于：

```text
competition_submission/V07_REFERENCE_CLAIM_VERIFICATION_FINAL_SUMMARY_CN.md
```

结果如下：

| 方向 | Ideas | Papers | Claims | Supported | Weak | Manual | Unsupported | Pass Rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| IAD + Agent | 3 | 24 | 21 | 8 | 4 | 3 | 0 | 0.857 |
| 物理属性预测 v2 | 3 | 51 | 15 | 8 | 3 | 0 | 0 | 1.0 |
| 室内单图 3D 场景生成 | 3 | 18 | 18 | 12 | 3 | 0 | 0 | 1.0 |

当前说明：

1. 物理属性和室内 3D 的证据链已修到 pass rate 1.0；
2. IAD 还有 3 个 manual check，但没有 unsupported claim；
3. 整体证据链可靠性明显提高。

## 18. 当前形成的完整 workflow

目前完整 workflow 为：

```text
Step 1：输入研究方向和任务约束
Step 2：检索 / 构造 paper evidence
Step 3：生成 baseline evidence cards
Step 4：生成 focused ideas
Step 5：规则评分 idea quality
Step 6：targeted repair
Step 7：生成匿名 A/B review pack
Step 8：multi-LLM blind judge
Step 9：根据 reviewer rationale 发现问题
Step 10：必要时二次 repair
Step 11：reference claim verification
Step 12：evidence-card repair
Step 13：生成阶段性总结报告
```

它比普通 prompt-based idea generation 更强，因为它具备：

```text
生成
评估
修复
再评估
证据验证
失败诊断
二次修复
```

## 19. 已生成的重要文件

阶段性总报告：

```text
competition_submission/AI_RESEARCH_WORKFLOW_STAGE_REPORT_CN.md
```

完整进展汇报：

```text
competition_submission/AI_RESEARCH_WORKFLOW_FULL_PROGRESS_REPORT_CN.md
```

v0.6 多模型盲评报告：

```text
competition_submission/V06_MULTI_LLM_BLIND_AB_EVALUATION_REPORT_V2_CN.md
```

v0.7 最终证据链验证报告：

```text
competition_submission/V07_REFERENCE_CLAIM_VERIFICATION_FINAL_SUMMARY_CN.md
```

关键脚本：

```text
focused_workflow/scripts/apply_physical_property_v2_repair.py
focused_workflow/scripts/repair_physical_v2_evidence_cards.py
focused_workflow/scripts/repair_indoor3d_evidence_cards.py
focused_workflow/scripts/verify_reference_claims.py
```

## 20. 当前项目价值

当前项目已经可以说明：

```text
我们不是简单调用 LLM 生成 idea；
我们构建的是一个科研 idea 自动化工作流。
```

它具备：

1. 方向聚焦；
2. baseline-grounded；
3. 输出结构化；
4. 有实验计划；
5. 有 negative controls；
6. 有 multi-LLM judge；
7. 有匿名 A/B 防偏差；
8. 有失败诊断；
9. 有二次修复；
10. 有 reference claim verification；
11. 有 evidence-card repair。

这对于比赛很重要，因为比赛要求的是一个智能体系统，而不只是一个单点算法。

## 21. 当前不足

当前仍未完成最终比赛交付，主要不足包括：

1. 还没有真实跑某个 CV 实验；
2. v0.7 仍主要是词面证据验证，不等于专家读论文；
3. 室内 3D 使用 seeded evidence bank，需要在最终文档诚实说明；
4. IAD 还有 3 个 needs_manual_check；
5. 还没有最终候选 idea 自动选择模块；
6. 还没有 Docker / 接口 / 演示视频；
7. 还没有最终比赛设计文档。

## 22. 下一步计划

下一步进入 v0.8：

```text
final candidate selector
```

该模块要读取：

```text
v0.6 blind judge 结果
v0.7 claim verification 结果
idea quality scores
实现成本
展示价值
比赛要求
```

输出：

```text
最终推荐方向
最终推荐 idea
适合比赛演示的 MVP
风险说明
分工建议
```

也就是说，下一步要回答：

```text
我们最终比赛到底展示哪个方向？
为什么选它？
证据是什么？
风险是什么？
怎么做演示？
```

## 23. 一句话总结

从 0 到现在，我们完成了一个从 ResearchArena baseline 出发的 AI 科研自动化 workflow 雏形。

它能生成 baseline-grounded idea，能自动修复 idea，能用多模型匿名盲评验证修复是否有效，还能检查论文证据是否真的支持 idea 中的 claim。

目前最重要的成果是：

1. 物理属性方向通过 v1 失败、v2 二次修复、6 judge 全胜，证明系统能发现并修复机制错配；
2. 室内 3D 方向通过 evidence-card repair，将 claim verification pass rate 从 0.2 提升到 1.0；
3. 物理属性方向通过 evidence-card repair，将 pass rate 从 0.533 提升到 1.0；
4. 整体系统从“生成 idea”升级为“生成-评估-修复-证据验证”的闭环。
