# V23 IAD Execution Bridge：从 idea 到实验执行的桥接案例

## 一句话结论

V23 将 V10 中的 IAD final research plan 接入 `iad_mvp` 执行链，并用 ARIS-style run_state / research_wiki / experiment log / paper plan 记录结果。这一步把系统从“idea 生成与评审”推进到“idea-to-experiment artifact workflow”。

## 当前结果

| metric | value |
| --- | ---: |
| image_level_auc_lightweight | 0.945238 |
| tool_success_rate | 1.0 |
| evidence_grounding_score_proxy | 1.0 |
| false_alarm_reduction_proxy | 0.0 |

## 生成产物

- Execution plan: `/data1/huangyuling/-A_HYL/AI4S/ResearchArena-main/execution_runs/v23_iad_execution_bridge/EXECUTION_PLAN.md`
- Experiment log: `/data1/huangyuling/-A_HYL/AI4S/ResearchArena-main/execution_runs/v23_iad_execution_bridge/EXPERIMENT_LOG.md`
- Commands: `/data1/huangyuling/-A_HYL/AI4S/ResearchArena-main/execution_runs/v23_iad_execution_bridge/commands.sh`
- Run state: `/data1/huangyuling/-A_HYL/AI4S/ResearchArena-main/execution_runs/v23_iad_execution_bridge/run_state.json`
- Research wiki: `/data1/huangyuling/-A_HYL/AI4S/ResearchArena-main/execution_runs/v23_iad_execution_bridge/research_wiki`
- Paper plan: `/data1/huangyuling/-A_HYL/AI4S/ResearchArena-main/execution_runs/v23_iad_execution_bridge/PAPER_PLAN.md`

## Honest boundary

当前 IAD 仍是 lightweight scaffold。它证明 workflow 可以把 final idea 接入真实数据执行链，并形成可复查结果；但不能声称完整 IAD benchmark 或 SOTA。

## 下一步

1. 将 `commands.sh` 升级为可选择 category / split / threshold 的正式 executor。
2. 增加 result parser，自动读取更多 metrics 和 failure cases。
3. 把 failed claim 自动转回 critic repair。
4. 接入 PatchCore/anomalib 或 patch-level feature，增强 benchmark-grade 实验。
