# V1.3 IAD 数据接入与 Smoke Test 报告

生成时间：2026-07-14 15:48:50

生成脚本：`focused_workflow/scripts/build_v13_iad_smoke_test_report.py`

## 1. 本阶段目标

V1.3 的目标不是证明 IAD 算法达到 SOTA，而是证明从 V1.0/V1.1 产出的最终研究方案已经可以接入真实数据，并完整产出实验中间文件和评价表格。

本次使用 MVTec AD 数据集中的 `bottle` 类别做最小 smoke test。该阶段结果应被表述为“真实数据接入与可执行性验证”，不能表述为正式 benchmark 结论。

## 2. 数据接入情况

- MVTec root: `Datasets/01_IAD/mvtec_anomaly_detection/mvtec_anomaly_detection`
- 使用类别：`bottle`
- train good 总数：209
- test 总数：83
- ground-truth mask 总数：63

| category | train_good | test_total | mask_total |
| --- | --- | --- | --- |
| bottle | 209 | 83 | 63 |

## 3. Pipeline 产物检查

| step | status | file |
| --- | --- | --- |
| MVTec split | exists | iad_mvp/data/mvtec_split.json |
| IAD manifest | exists | iad_mvp/data/iad_reference_manifest.jsonl |
| Reference bank | exists | iad_mvp/data/iad_reference_bank.npz |
| Reference index | exists | iad_mvp/data/iad_reference_index.jsonl |
| Lightweight baseline scores | exists | iad_mvp/outputs/patchcore_baseline/iad_baseline_scores.csv |
| Reference consistency scores | exists | iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv |
| Execution metrics | exists | iad_mvp/outputs/tables/iad_agent_execution_metrics.csv |
| Negative control report | exists | iad_mvp/outputs/tables/iad_negative_control_report.csv |

## 4. Manifest 与覆盖情况

- Manifest rows: 292
- Split counts: {'train': 209, 'test': 83}
- Label counts: {'0': 229, '1': 63}
- Reference rows: 209
- Rows with masks: 63
- Baseline score rows: 83
- Reference consistency rows: 83

## 5. Smoke Test 指标

当前指标来自 lightweight nearest-reference scaffold，不是完整 PatchCore/anomalib benchmark。

- image_level_auc_lightweight: 0.945238
- baseline_false_alarms_at_threshold: 0
- agent_false_alarms_at_threshold: 0
- false_alarm_reduction_proxy: 0.000000
- evidence_grounding_score_proxy: 1.000000
- tool_success_rate: 1.000000

## 6. Reference Consistency 决策分布

| decision | count |
| --- | --- |
| accept_normal | 81 |
| suppress_or_review_false_alarm | 2 |

解释：如果 `accept_anomaly` 数量过低，不能解释为系统已经完美过滤异常；更合理的解释是当前 scaffold 的 consistency 阈值和决策逻辑偏保守。V1.4 需要进行阈值校准，并引入更强 baseline 或更细粒度 patch-level 特征。

## 7. 负控制结果

| control | accepted_anomaly_count | note |
| --- | --- | --- |
| full_reference_consistency | 0 | actual scaffold decision |
| random_retrieval | 38 | randomized decision baseline |
| shuffled_provenance | 2 | baseline-score-only proxy |
| contaminated_normal_bank_proxy | 0 | simulated reduced confidence |

负控制目前仍是 proxy 版本，用来检查流程是否能生成对照表，不代表完整 contaminated-normal-bank 实验已经完成。

## 8. 当前可以得出的结论

1. MVTec AD 数据已经成功接入当前项目目录。
2. `bottle` 类别 smoke test 已经跑通，包含 split、manifest、reference bank、baseline score、reference consistency、negative control 和 execution metrics。
3. 当前 workflow 已经从“研究方案文本”推进到“真实数据可执行性验证”。
4. 当前结果不能被写成正式 IAD benchmark，因为 baseline 是 lightweight nearest-reference scaffold，不是完整 PatchCore/PaDiM/WinCLIP/anomalib 复现。

## 9. 下一步 V1.4 建议

V1.4 不应该再写泛泛报告，而应该解决当前 smoke test 暴露出的工程问题：

1. 校准 `anomaly_threshold` 和 `consistency_threshold`，避免 reference-consistency 过度 suppress anomaly。
2. 把 lightweight image-level feature 替换为更合理的 patch-level feature 或接入 cached PatchCore/anomalib 分数。
3. 从 `bottle` 扩展到 3 个类别，例如 `bottle`、`cable`、`capsule`。
4. 输出正式一点的多类别表格：image-level AUROC、false alarm proxy、evidence grounding、tool success rate、negative control gap。
5. 保持边界说明：这是 workflow execution validation，不是单独发明一个 IAD SOTA 算法。
