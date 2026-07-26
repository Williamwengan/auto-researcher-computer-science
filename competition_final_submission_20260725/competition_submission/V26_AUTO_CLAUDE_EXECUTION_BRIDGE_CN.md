# V26 Auto-claude / ARIS 实验执行 Bridge

生成时间：2026-07-26T15:58:08

## 结论

V25 的 ResearchArena resume bridge 只能说明 schema 能接回 ResearchArena；但比赛 demo 真正需要的是 Auto-claude/ARIS 风格的实验执行舱：用户授权后，由 Claude/Codex 对话式实现 baseline、运行实验、记录结果并生成论文草稿。

本 V26 已把 V10 final research plans 转换成 Auto-claude/ARIS-style workspaces。

## 生成的实验执行工作区

| task | workspace | authorization prompt | entry |
| --- | --- | --- | --- |
| 物理属性预测 | `outputs/auto_claude_execution_bridge_v1/physical_property` | `outputs/auto_claude_execution_bridge_v1/physical_property/AUTHORIZED_CLAUDE_PROMPT.md` | `/experiment-bridge refine-logs/EXPERIMENT_PLAN.md` |
| 室内单图 3D 场景生成 | `outputs/auto_claude_execution_bridge_v1/indoor3d_scene` | `outputs/auto_claude_execution_bridge_v1/indoor3d_scene/AUTHORIZED_CLAUDE_PROMPT.md` | `/experiment-bridge refine-logs/EXPERIMENT_PLAN.md` |
| 工业异常检测 IAD + Agent | `outputs/auto_claude_execution_bridge_v1/iad_agent` | `outputs/auto_claude_execution_bridge_v1/iad_agent/AUTHORIZED_CLAUDE_PROMPT.md` | `/experiment-bridge refine-logs/EXPERIMENT_PLAN.md` |

## 每个 workspace 包含什么

- `RESEARCH_BRIEF.md`：任务、问题、约束和最终 idea。
- `CLAUDE.md` / `AGENTS.md`：Auto-claude/ARIS 执行规则与人工授权边界。
- `refine-logs/FINAL_PROPOSAL.md`：方法提案。
- `refine-logs/EXPERIMENT_PLAN.md`：可交给 `/experiment-bridge` 的实验计划。
- `refine-logs/EXPERIMENT_TRACKER.md`：实验进度表。
- `research-wiki/`：papers/ideas/experiments/claims/graph 结构。
- `.aris/runs/focused_to_experiment.json`：可恢复的执行状态。
- `AUTHORIZED_CLAUDE_PROMPT.md`：网页端授权后可送入 Claude/Codex 对话舱的提示。

## 安全边界

本脚本只生成文件，不调用 API、不下载数据、不运行 GPU、不执行 shell 实验命令。真正执行需要用户在网页或 Claude/Codex 对话中确认授权。

## 推荐 demo 讲法

Phase 1 展示：输入科研任务后，系统完成论文证据、baseline 空白、idea 生成、评分、盲评、repair 和最终方案选择。

Phase 2 展示：点击授权进入 Auto-claude/ARIS 实验舱，系统读取 `EXPERIMENT_PLAN.md`，询问数据集/API/GPU 授权，然后开始 baseline reproduction、proposed module、ablation、result-to-claim 和 paper draft。
