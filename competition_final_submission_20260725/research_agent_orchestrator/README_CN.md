# Research Agent Orchestrator

这是比赛 demo 的最小多阶段科研智能体。它的目标不是伪造任意方向的论文证据，而是把陌生任务接入到一个可审计 workflow。当前版本已经支持：

- 默认尝试通过 OpenAlex 联网检索真实论文；
- 检索成功后写入 `papers.jsonl`；
- 根据检索论文生成 retrieved/unverified baseline cards；
- 为每个陌生任务生成 task-specific runner scaffold；
- Phase 2 可经人工授权运行该 scaffold，输出 smoke metrics 和 result-to-claim。

```text
TaskSpecAgent
→ PaperRetrievalAgent
→ BaselineCardAgent
→ IdeaGenerationAgent
→ ExperimentPlannerAgent
→ RunnerBuilderAgent
```

运行示例：

```bash
python research_agent_orchestrator/orchestrator.py \
  --task-type "遥感变化检测可信解释" \
  --research-direction "多时相遥感图像变化检测中的证据驱动解释智能体" \
  --task-mode incremental_improvement
```

输出目录：

```text
execution_runs/research_agent_orchestrator/<task_id>/
```

关键边界：

- 对陌生方向，当前输出是“新任务接入状态”，不是 verified final idea。
- 如果服务器可访问 OpenAlex，`papers.jsonl` 会填入真实检索论文；如果网络失败，系统会记录失败原因而不是编造论文。
- 生成的 `runner_scaffold/` 是任务专属 smoke runner，用于验证执行接口；不等价于真实领域 benchmark。
- 没有接入真实数据集、真实 baseline 和 metric parser 前，不声称真实科学性能提升。
