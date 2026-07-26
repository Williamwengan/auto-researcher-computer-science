# V24 Authorized Experiment Executor：人工授权实验执行器

## 一句话结论

V24 将当前 ResearchArena workflow 的后半段扩展为“人工授权后执行实验”的模式：系统先生成实验命令预览和授权请求；获得授权后，自动运行 baseline reproduction、agent scoring 和 metric evaluation，并记录 run_state、日志和结果。

## 当前状态

已授权并执行完成

## 接入 Auto-claude 的能力点

| Auto-claude capability | 当前接入方式 |
| --- | --- |
| baseline reproduction | 调用 `iad_mvp/scripts/run_iad_baselines.py` 复现 lightweight baseline |
| run experiment | 调用 reference-consistency agent 和 evaluation 脚本 |
| human authorization | 默认 dry-run；只有 `--approve --approval-note` 才执行 |
| resumable run state | 使用 `aris_bridge/tools/run_state.py` 记录 phase 状态 |
| monitoring hook | 输出 `watchdog_loop_state.json`，后续可被 watchdog 监控 |
| execution logs | 每个阶段写入 `logs/<phase>.log` |
| result-to-report | 自动生成本 V24 报告和 `execution_summary.json` |

## 执行阶段

| # | phase | artifact |
| ---: | --- | --- |
| 1 | `prepare_mvtec_split` | `iad_mvp/data/mvtec_split.json` |
| 2 | `prepare_reference_manifest` | `iad_mvp/data/iad_reference_manifest.jsonl` |
| 3 | `build_reference_bank` | `iad_mvp/data/iad_reference_bank.npz` |
| 4 | `reproduce_lightweight_baseline` | `iad_mvp/outputs/patchcore_baseline/iad_baseline_scores.csv` |
| 5 | `run_reference_consistency_agent` | `iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv` |
| 6 | `evaluate_execution_metrics` | `iad_mvp/outputs/tables/iad_agent_execution_metrics.csv` |


## 当前 metrics

授权执行后生成的 metrics

| metric | value |
| --- | --- |
| image_level_auc_lightweight | 0.945238 |
| baseline_false_alarms_at_threshold | 0.0 |
| agent_false_alarms_at_threshold | 0.0 |
| false_alarm_reduction_proxy | 0.0 |
| evidence_grounding_score_proxy | 1.0 |
| tool_success_rate | 1.0 |
| note | scaffold metrics; not final benchmark results |

## 关键产物

- 授权请求：`execution_runs/v24_authorized_iad_executor/EXPERIMENT_AUTHORIZATION_REQUEST.md`
- 命令预览：`execution_runs/v24_authorized_iad_executor/commands_preview.sh`
- 实验 manifest：`execution_runs/v24_authorized_iad_executor/experiment_manifest.json`
- run_state：`execution_runs/v24_authorized_iad_executor/run_state.json`
- watchdog state：`execution_runs/v24_authorized_iad_executor/watchdog_loop_state.json`
- logs：`execution_runs/v24_authorized_iad_executor/logs`
- summary：`execution_runs/v24_authorized_iad_executor/execution_summary.json`

## Honest boundary

当前 V24 证明的是“从 idea/plan 到授权实验执行”的系统能力，不证明 IAD 算法达到 SOTA。它是把 Auto-claude 的实验执行思想接到 ResearchArena workflow 的第一版工程入口。

## 下一步扩展

1. 将 IAD scaffold 替换或并联到 PatchCore/anomalib 正式 benchmark。
2. 增加 experiment queue，支持多 seed、多 category、多 GPU。
3. 增加 result-to-claim-to-repair：失败指标自动转成 critic repair prompt。
4. 接入 paper writing loop，把 verified claims 自动转成论文实验段落。
