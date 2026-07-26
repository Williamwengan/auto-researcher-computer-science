# Pipeline v0.4：Multi-LLM Judge + Critic-Repair 闭环方案

生成时间：2026-07-11

定位：本阶段不继续推进某个具体 CV 实验 MVP，而是增强“科研 idea 生成与评价智能体”本身。目标是让系统从 `生成 idea -> 规则评分` 升级为：

```text
生成 idea
-> schema 校验
-> 规则评分
-> multi-LLM judge
-> pairwise ranking
-> critic-repair
-> 再评价
-> 输出最终候选 idea
```

这更符合你们现在想做的比赛主线：不是做一个 IAD 算法，也不是做一个 human motion 算法，而是做一个能自动生成、评价、修复科研 idea 的智能体工作流。

## 1. 为什么现在做 v0.4

v0.3 已经解决了一个重要问题：idea 不再只是空泛 proposal，而是开始包含：

- 具体 baseline；
- baseline failure mode；
- 最小新增模块；
- 输入输出；
- 算法步骤；
- 实验计划；
- MVP artifacts；
- 成功阈值；
- 风险和失败标准。

但 v0.3 还有三个不足：

1. 主要依赖规则评分和单个人工 reviewer，评价可信度还不够。
2. 生成后只能打分，还不能自动把低质量 idea 修好。
3. 没有 multi-judge agreement / disagreement 统计，无法证明评价鲁棒性。

所以 v0.4 的目标是补上：

```text
multi-LLM judge + critic-repair + before/after quality comparison
```

这会比“prompt 优化后 idea 更长”更有说服力，因为我们可以量化：

- 平均分是否提升；
- penalty 是否下降；
- judge 方差是否可控；
- pairwise win rate 是否稳定；
- repair 前后 implementation readiness 是否提升。

## 2. 新增文件

| 文件 | 作用 |
|---|---|
| `focused_workflow/scripts/multi_llm_judge.py` | 多 LLM judge 评分、均值/方差聚合、pairwise ranking |
| `focused_workflow/evaluation/judge_config.yaml` | judge 模型配置，默认启用 `gpt-5.5`，其他模型需要确认后开启 |
| `focused_workflow/scripts/repair_low_quality_ideas.py` | 根据 `idea_quality_scores.json` 找低分或高 penalty idea，生成 critic-repair prompt 或调用 LLM 修复 |
| `focused_workflow/prompts/idea_critic_repair_prompt.md` | critic-repair prompt 模板 |
| `focused_workflow/scripts/run_idea_quality_v0_4.sh` | 一键运行 v0.4 idea quality pipeline |

## 3. 当前验证结果

我已经在 IAD v0.3 输出目录上完成 dry-run：

```text
outputs/benchmark_cv_runs_20260711_150957/05_iad_agent_workflow
```

已验证：

- `validate_outputs.py` 通过；
- `evaluate_idea_quality.py` 正常输出规则评分；
- IAD v0.3 平均规则分数为 `90.5/100`；
- top idea 是 `Reference-Consistency Agent for Shift-Resistant PatchCore Inspection`，分数为 `95.0/100`；
- `multi_llm_judge.py --dry-run` 可以生成 multi-judge prompts 和汇总文件；
- `repair_low_quality_ideas.py --dry-run --min-score 90` 可以自动选择需要修复的 idea，并生成 repair prompt；
- 所有 dry-run 都不会调用 API，不会扣费，不会覆盖原始 idea。

关键输出包括：

```text
outputs/benchmark_cv_runs_20260711_150957/05_iad_agent_workflow/multi_llm_judge/multi_judge_scores.json
outputs/benchmark_cv_runs_20260711_150957/05_iad_agent_workflow/multi_llm_judge/multi_judge_summary_CN.md
outputs/benchmark_cv_runs_20260711_150957/05_iad_agent_workflow/multi_llm_judge/prompts/score_prompt.md
outputs/benchmark_cv_runs_20260711_150957/05_iad_agent_workflow/repair_runs/repair_20260711_155355/idea_critic_repair_prompt.rendered.md
```

## 4. Multi-LLM Judge 设计

### 4.1 评价维度

每个 judge 都使用同一套 rubric：

```json
{
  "novelty": 1,
  "feasibility": 1,
  "expected_effectiveness": 1,
  "experimental_rigor": 1,
  "baseline_grounding": 1,
  "mechanism_specificity": 1,
  "implementation_readiness": 1,
  "overall": 1
}
```

这些维度分别解决：

- `novelty`：idea 是否真的有新意；
- `feasibility`：短期能不能实现；
- `expected_effectiveness`：是否可能带来指标提升或科研价值；
- `experimental_rigor`：是否有 baseline、指标、消融、失败标准；
- `baseline_grounding`：是否基于具体 baseline 和 failure mode；
- `mechanism_specificity`：是否有具体机制，而不是工具堆叠；
- `implementation_readiness`：是否能直接进入工程实现；
- `overall`：综合优先级。

### 4.2 聚合指标

脚本会输出：

```text
mean_score
std_score
min_score
max_score
judge_agreement
pairwise_win_rate
```

解释规则：

| std | 含义 |
|---:|---|
| `< 0.8` | judge 比较一致 |
| `0.8 - 1.5` | 有分歧，需要人工复核 |
| `> 1.5` | 高分歧，不能直接采用自动分 |

这可以支撑比赛中的说法：

```text
我们不是用单个 LLM judge 打分，而是使用 multi-judge ensemble，
并通过均值、方差和 pairwise win rate 判断 idea 质量与评价一致性。
```

## 5. Critic-Repair 设计

v0.3 的流程是：

```text
生成 idea -> 打分
```

v0.4 改成：

```text
生成 idea -> 打分 -> 找低分项 -> 生成 repair prompt -> 修复 idea -> 再打分
```

`repair_low_quality_ideas.py` 会读取：

```text
focused_ideas.json
experiment_plan.json
idea_quality_scores.json
task_spec.yaml
```

然后自动筛选：

- `idea_quality_score` 低于阈值的 idea；
- `granularity_penalty` 高于阈值的 idea；
- 缺少具体机制、负对照、成功阈值或 MVP artifacts 的 idea。

修复时要求：

- 不换任务方向；
- 不换 baseline 家族；
- 不把 idea 写成泛泛而谈；
- 只修复低分项；
- 输出新的 `focused_ideas_repaired.json` 和 `experiment_plan_repaired.json`；
- 不覆盖原始 `focused_ideas.json`。

## 6. 如何运行

### 6.1 只跑规则评分

```bash
cd /data1/huangyuling/-A_HYL/AI4S/ResearchArena-main

bash focused_workflow/scripts/run_idea_quality_v0_4.sh \
  outputs/benchmark_cv_runs_20260711_150957/05_iad_agent_workflow
```

### 6.2 跑 multi-judge dry-run + repair dry-run

不会调用 API，不会扣费，只生成 prompt：

```bash
cd /data1/huangyuling/-A_HYL/AI4S/ResearchArena-main

RUN_MULTI_JUDGE=1 \
MULTI_JUDGE_DRY_RUN=1 \
RUN_REPAIR=1 \
REPAIR_DRY_RUN=1 \
REPAIR_MIN_SCORE=90 \
bash focused_workflow/scripts/run_idea_quality_v0_4.sh \
  outputs/benchmark_cv_runs_20260711_150957/05_iad_agent_workflow
```

### 6.3 实际调用 multi-LLM judge

先编辑：

```bash
nano focused_workflow/evaluation/judge_config.yaml
```

确认 API 支持的模型名后，把多个 judge 的 `enabled` 改成 `true`。

然后运行：

```bash
cd /data1/huangyuling/-A_HYL/AI4S/ResearchArena-main
source ~/.estelle_api_env

export PATH="/data1/huangyuling/.vscode-server/extensions/openai.chatgpt-26.707.41301-linux-x64/bin/linux-x86_64:/bin:/usr/bin:$PATH"
hash -r

RUN_MULTI_JUDGE=1 \
MULTI_JUDGE_DRY_RUN=0 \
bash focused_workflow/scripts/run_idea_quality_v0_4.sh <run_dir>
```

说明：我尝试查询 Estelle `/v1/models`，但接口返回 Cloudflare `403`，因此模型名需要你在 Estelle 后台或文档中确认。脚本默认用 `codex exec --model ...` 后端，因为你之前已验证 Codex + Estelle 的 `gpt-5.5` 能正常运行。

### 6.4 实际调用 critic-repair

```bash
cd /data1/huangyuling/-A_HYL/AI4S/ResearchArena-main
source ~/.estelle_api_env

export PATH="/data1/huangyuling/.vscode-server/extensions/openai.chatgpt-26.707.41301-linux-x64/bin/linux-x86_64:/bin:/usr/bin:$PATH"
hash -r

RUN_REPAIR=1 \
REPAIR_DRY_RUN=0 \
REPAIR_MIN_SCORE=90 \
bash focused_workflow/scripts/run_idea_quality_v0_4.sh <run_dir>
```

修复输出会写入：

```text
<run_dir>/repair_runs/repair_<timestamp>/
```

不会覆盖原始 `focused_ideas.json`。

## 7. 建议实验流程

接下来建议用三个方向验证 v0.4：

```text
01_physical_property_prediction
02_human_motion_generation
05_iad_agent_workflow
```

每个方向都跑：

```text
v0.3 idea generation
-> rule-based quality score
-> multi-LLM judge
-> critic-repair
-> repaired idea quality score
```

最终比较：

| 指标 | 含义 |
|---|---|
| average_quality_score | 规则评分平均值 |
| granularity_penalty | 空泛/不具体惩罚 |
| multi_judge_mean_overall | 多 judge 平均分 |
| multi_judge_std_overall | 多 judge 分歧 |
| pairwise_win_rate | idea 相对优先级 |
| repair_score_gain | repair 后分数提升 |
| repair_penalty_drop | repair 后 penalty 降低 |
| human_accept_rate | 人工最终接受率 |

## 8. 比赛叙事方式

最终可以这样讲：

```text
我们提出一个面向 AI4Sci 的科研 idea 生成与评估智能体。
系统输入研究方向和具体任务约束，输出 baseline-grounded idea、最小新增模块、实验计划和 MVP artifacts。
为避免单一 LLM judge 偏差，系统引入 multi-LLM judge ensemble，计算均值、方差和 pairwise win rate。
当规则评分或多 judge 发现 idea 空泛、机制不清或实验不可执行时，critic-repair agent 会自动重写并再次评价。
```

这比“让模型生成几个 idea”更像一个完整的科研自动化 workflow。

## 9. 与比赛提交物的关系

### 9.1 智能体详细设计文档

最终设计文档应该写“科研 idea 生成与评估智能体”，而不是只写 IAD 智能体。

核心模块可以写成：

```text
Task Spec Parser
Baseline Card Generator
Focused Idea Generator
Schema Validator
Rule-based Quality Evaluator
Multi-LLM Judge
Pairwise Ranker
Critic-Repair Agent
Final Candidate Selector
Report Exporter
```

### 9.2 Docker 镜像部署包或远程调用接口

接口可以设计为：

```text
POST /generate_ideas
input: domain, task, task_type, constraints
output: baseline_cards, focused_ideas, experiment_plans

POST /evaluate_ideas
input: run_dir or ideas
output: rule_scores, multi_judge_scores, pairwise_ranking

POST /repair_ideas
input: run_dir, score_threshold
output: repaired_ideas, repaired_experiment_plans, before_after_report
```

### 9.3 三分钟演示视频

演示流程可以是：

1. 输入一个 CV 研究方向和任务约束；
2. 系统生成 baseline cards；
3. 系统生成三个 focused ideas；
4. 系统进行 schema 校验；
5. 系统进行规则评分；
6. 系统进行 multi-LLM judge；
7. 系统发现低分项；
8. 系统自动 critic-repair；
9. 系统输出最终候选 idea 和实验计划。

这个视频比单独演示 IAD 检测更贴合“AI 科研自动化工作流”。

## 10. 下一步

下一步建议：

1. 在 Estelle 后台确认可用模型名，至少启用 3 个 judge；
2. 对 IAD、human motion、physical property 三个方向各跑一次 multi-judge；
3. 对低分或高分歧 idea 跑 critic-repair；
4. 生成统一报告：`V04_IDEA_WORKFLOW_EVALUATION_REPORT_CN.md`；
5. 再开始写最终版“科研 idea 生成与评估智能体详细设计文档”。

