# V23 IAD Execution Bridge Plan

生成时间：2026-07-25T11:04:30

## 目标

把 V10 final research plan 中的 IAD idea 接入 ARIS-style execution layer，使 workflow 从 idea/plan 进入实验复现、结果登记、claim 判断和论文计划。

## 输入 final idea

Evidence-Grounded Reference-Consistency IAD Agent：以 normal reference retrieval 为核心，结合 anomaly heatmap、cross-model disagreement、region-reference consistency score、report checker 和 escalation policy。

## 核心假设

如果 defect claim 必须同时绑定 anomaly region、normal reference contrast、model disagreement 和 evidence-grounded report check，则可以降低由 texture/lighting/reference shift 导致的 false alarms，并提高报告可信度。

## Execution blocks

| block | purpose | artifact |
| --- | --- | --- |
| B0 data manifest | 准备 MVTec AD manifest | `iad_mvp/data/iad_reference_manifest.jsonl` |
| B1 reference bank | 构建 normal reference bank | `iad_mvp/data/iad_reference_bank.npz` |
| B2 baseline reproduction | 运行 lightweight nearest-reference baseline | `iad_mvp/outputs/patchcore_baseline/iad_baseline_scores.csv` |
| B3 proposed scoring | 运行 reference-consistency scoring | `iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv` |
| B4 evaluation | 汇总 execution metrics | `iad_mvp/outputs/tables/iad_agent_execution_metrics.csv` |
| B5 result-to-claim | 写入 research wiki experiment/claim | `research_wiki/experiments/` and `research_wiki/claims/` |
| B6 paper plan | 根据结果生成 paper plan | `PAPER_PLAN.md` |

## 当前执行结果

- image_level_auc_lightweight: 0.945238
- tool_success_rate: 1.0
- evidence_grounding_score_proxy: 1.0
- false_alarm_reduction_proxy: 0.0
- note: scaffold metrics; not final benchmark results

## Honest verdict

当前结果证明 IAD execution bridge 能把 final idea 接入真实数据 smoke test，并能产出可读取指标与执行日志；但它仍是 lightweight scaffold，不是完整 PatchCore/anomalib benchmark，也不声称 IAD SOTA。
