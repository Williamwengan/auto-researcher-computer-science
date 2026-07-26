# V0.4 科研 Idea 工作流评价报告

生成时间：2026-07-11

## 1. 本阶段目标

本阶段目标不是继续推进某一个具体 CV 实验，而是增强“科研 idea 生成与评价智能体”本身。

v0.4 重点补上两个能力：

```text
multi-LLM judge
critic-repair
```

也就是让 pipeline 从：

```text
生成 idea -> 规则评分
```

升级为：

```text
生成 idea
-> schema 校验
-> 规则评分
-> LLM judge
-> 低分 idea 定位
-> critic-repair prompt
-> 后续可再次评分
```

## 2. 当前可用 Judge 状态

### 2.1 Estelle 远程模型

已验证：

- `gpt-5.5` 可通过 Codex + Estelle 正常调用。

未能直接启用：

- `claude`
- `claude-max`

原因：当前 `ESTELLE_API_KEY` 实际落在 `gpt` 通道，探测 `claude` 和 `claude-max` 时返回：

```text
No available channel for model claude under group gpt
No available channel for model claude-max under group gpt
```

判断：如果要使用 Claude judge，需要在 Estelle 后台新建 `claude` 或 `claude-max` 令牌组的 key，并在 `~/.estelle_api_env` 中切换对应 key。

另外，真实调用 Estelle multi-judge 时，系统安全策略阻止我把未公开 idea 内容发送到外部第三方服务。因此本报告没有代替你实际调用 Estelle judge，而是保留了脚本和命令，由你在终端里手动运行。

### 2.2 本地模型

已验证本地可用：

- Ollama binary：`/data1/huangyuling/-A_HYL/File_Project/bin/ollama`
- 本地模型：`minicpm-v:latest`
- Ollama 服务：`127.0.0.1:11434`

我已将 `minicpm-v:latest` 接入 `multi_llm_judge.py`，作为本地 judge。

本地 Qwen2.5-0.5B 也能加载，但在当前环境中作为 judge 生成较慢，因此默认关闭。

## 3. 新增和更新文件

| 文件 | 作用 |
|---|---|
| `focused_workflow/scripts/multi_llm_judge.py` | 支持 Codex/Estelle、Ollama、本地 HuggingFace 三类 judge 后端 |
| `focused_workflow/evaluation/judge_config.yaml` | 默认配置：`gpt-5.5` 启用，Claude 候选保留但禁用 |
| `focused_workflow/evaluation/judge_config_local_only.yaml` | 本地-only 配置：启用 Ollama `minicpm-v:latest` |
| `focused_workflow/scripts/repair_low_quality_ideas.py` | 根据规则评分生成 critic-repair prompt |
| `focused_workflow/prompts/idea_critic_repair_prompt.md` | critic-repair prompt 模板 |
| `focused_workflow/scripts/run_idea_quality_v0_4.sh` | 一键运行 v0.4 质量流程 |

## 4. 三个方向的 v0.4 本地 Judge 结果

本报告使用本地 Ollama `minicpm-v:latest` 跑了三个方向：

```text
01_physical_property_prediction
02_human_motion_generation
05_iad_agent_workflow
```

注意：本地 MiniCPM judge 只能作为安全 sanity check，不应作为最终论文级 judge。最终报告仍建议使用 GPT + Claude + 另一个模型做 multi-judge ensemble。

## 5. 规则评分 vs 本地 LLM Judge

| 方向 | 规则评分平均分 | 规则评分 Top Idea | 本地 Judge Top Idea | 本地 Judge Overall |
|---|---:|---|---|---:|
| 物理属性预测 | 87.0 | Evidence-Weighted Material Mixture Intervals for Object Physical Properties | Conformal Property Calibration From Weak and Synthetic Interval Labels | 7.0 |
| Human Motion 生成 | 91.5 | Contact-Calibrated Diffusion Guidance for Text-to-Motion | Scene-Affordance Verifier and Repair Loop for Object-Goal Motion Generation | 7.0 |
| IAD + Agent 工作流 | 90.5 | Reference-Consistency Agent for Shift-Resistant PatchCore Inspection | Reference-Consistency Agent for Shift-Resistant PatchCore Inspection | 8.0 |

## 6. 结果解读

### 6.1 IAD 方向

IAD 的规则评分和本地 judge 一致，都认为：

```text
Reference-Consistency Agent for Shift-Resistant PatchCore Inspection
```

是最强候选。

这说明 IAD Idea 1 的 baseline grounding、机制清晰度和 implementation readiness 比较稳定。

### 6.2 物理属性预测方向

规则评分更偏好：

```text
Evidence-Weighted Material Mixture Intervals
```

本地 judge 更偏好：

```text
Conformal Property Calibration
```

解释：本地 judge 可能更偏好“校准/区间预测”这种评价目标明确的 idea，而规则评分更重视最小新增模块和工程可执行性。

这类分歧是 multi-judge 的价值所在：它提示我们物理属性方向需要人工复核，不应只看一个分数。

### 6.3 Human Motion 方向

本地 MiniCPM judge 对 human motion 的两个 idea 给分明显偏低：

```text
Contact-Calibrated Diffusion Guidance: 2
Constraint-State Motion Decoder: 1
```

这不太符合我们之前的人工 reviewer 判断，也不符合规则评分结果。

判断：本地 MiniCPM 对 motion generation 专业任务理解较弱，不适合作为 human motion 的最终 judge。它可以作为安全 sanity judge，但不能替代 GPT/Claude 级别 judge。

## 7. Critic-Repair Dry-Run 结果

使用阈值：

```text
REPAIR_MIN_SCORE=90
```

三个方向的 repair targets：

| 方向 | repair targets 数量 | repair prompt |
|---|---:|---|
| 物理属性预测 | 3 | `outputs/benchmark_cv_runs_20260711_150309/01_physical_property_prediction/repair_runs/repair_20260711_222611/idea_critic_repair_prompt.rendered.md` |
| Human Motion 生成 | 1 | `outputs/benchmark_cv_runs_20260711_143630/02_human_motion_generation/repair_runs/repair_20260711_222611/idea_critic_repair_prompt.rendered.md` |
| IAD + Agent 工作流 | 2 | `outputs/benchmark_cv_runs_20260711_150957/05_iad_agent_workflow/repair_runs/repair_20260711_222611/idea_critic_repair_prompt.rendered.md` |

当前只做 dry-run，没有调用外部 LLM 修复，因此不会覆盖原始 idea。

## 8. 当前结论

v0.4 已经完成了工作流层面的关键增强：

- 支持 multi-judge 框架；
- 支持 Estelle/Codex judge；
- 支持 Ollama 本地 judge；
- 支持本地 HuggingFace judge；
- 支持规则评分后自动选择 repair targets；
- 支持生成 critic-repair prompt；
- 所有新增评估和修复产物都写入新目录，不覆盖原始 idea。

但当前还不能说完成了最终 multi-LLM judge ensemble，因为：

1. 当前 Estelle key 只能跑 `gpt-5.5`，不能跑 Claude；
2. 外部 API 调用涉及未公开 idea 内容，需由你在终端手动确认后执行；
3. 本地 MiniCPM judge 能跑，但能力有限，只适合作为安全补充 judge。

## 9. 下一步

建议下一步这样做：

1. 在 Estelle 后台新建或切换 `claude` / `claude-max` 令牌组 key。
2. 确认可用模型名后，修改 `focused_workflow/evaluation/judge_config.yaml`。
3. 由你在终端手动运行真实外部 multi-judge：

```bash
cd /data1/huangyuling/-A_HYL/AI4S/ResearchArena-main
source ~/.estelle_api_env
export PATH="/data1/huangyuling/.vscode-server/extensions/openai.chatgpt-26.707.41301-linux-x64/bin/linux-x86_64:/bin:/usr/bin:$PATH"
hash -r

RUN_MULTI_JUDGE=1 \
MULTI_JUDGE_DRY_RUN=0 \
bash focused_workflow/scripts/run_idea_quality_v0_4.sh \
  outputs/benchmark_cv_runs_20260711_150957/05_iad_agent_workflow
```

4. 如果不想外发 idea 内容，则继续使用本地-only judge：

```bash
python focused_workflow/scripts/multi_llm_judge.py \
  outputs/benchmark_cv_runs_20260711_150957/05_iad_agent_workflow \
  --config focused_workflow/evaluation/judge_config_local_only.yaml \
  --skip-pairwise
```

5. 等真实 GPT/Claude/local judge 都跑完后，再生成最终版：

```text
V04_IDEA_WORKFLOW_FINAL_EVALUATION_REPORT_CN.md
```

该最终报告可以作为比赛“智能体详细设计文档”的评价模块依据。

