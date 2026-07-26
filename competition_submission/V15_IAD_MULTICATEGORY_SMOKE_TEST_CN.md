# V1.5 IAD 三类别 Calibrated Smoke Test 报告

生成时间：2026-07-14 16:09:39

生成脚本：`focused_workflow/scripts/build_v15_iad_multicategory_smoke_test_report.py`

## 1. 本阶段目标

V1.5 的目标是把 V1.4 在 `bottle` 上得到的校准阈值迁移到 `bottle/cable/capsule` 三个类别，检查单类别校准是否具备跨类别稳定性。

这一步仍然是 lightweight smoke test，不是完整 PatchCore/anomalib benchmark。

## 2. 使用的数据与阈值

- MVTec root: `Datasets/01_IAD/mvtec_anomaly_detection/mvtec_anomaly_detection`
- 类别：`bottle, cable, capsule`
- train good 总数：652
- test 总数：365
- mask 总数：264
- anomaly_threshold: 0.040000
- consistency_threshold: 0.999595

| category | train_good | test_total | mask_total |
| --- | --- | --- | --- |
| bottle | 209 | 83 | 63 |
| cable | 224 | 150 | 92 |
| capsule | 219 | 132 | 109 |

## 3. 产物覆盖情况

- Manifest rows: 1017
- Split counts: {'train': 652, 'test': 365}
- Label counts: {'0': 753, '1': 264}
- Reference rows: 652
- Rows with masks: 264
- Baseline rows: 365
- Calibrated score rows: 365

## 4. 三类别整体结果

- overall image_level_auc_lightweight: 0.490512
- overall anomaly_recall: 0.496212
- overall false_alarm_rate: 0.574257
- accept_anomaly_count: 189
- accept_normal_count: 176
- review_count: 0

## 5. 按类别结果

| category | test_total | anomaly_total | normal_total | auc_lightweight | accept_anomaly | accept_normal | review | anomaly_recall | false_alarm_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bottle | 83 | 63 | 20 | 0.945238 | 32 | 51 | 0 | 0.507937 | 0.000000 |
| cable | 150 | 92 | 58 | 0.833583 | 150 | 0 | 0 | 1.000000 | 1.000000 |
| capsule | 132 | 109 | 23 | 0.610690 | 7 | 125 | 0 | 0.064220 | 0.000000 |

## 6. 关键诊断

V1.5 发现：V1.4 的 `bottle` 阈值不能直接作为跨类别全局阈值使用。

- `bottle`：误报率为 0，但 anomaly recall 下降，说明三类别 reference bank / 全局归一化改变了 bottle 的分数分布。
- `cable`：正常样本也大量被判为异常，说明该类别的正常图像在当前 lightweight feature 下与 reference bank 的距离偏高。
- `capsule`：异常 recall 很低，说明该类别异常在当前 image-level feature 中不够可分。

这说明问题不在 idea generation 本身，而在执行层 scaffold 的特征、归一化和阈值策略。当前最合理的下一步不是继续扩展更多类别，而是做类别感知校准。

## 7. 负控制结果

| control | accepted_anomaly_count | note |
| --- | --- | --- |
| full_reference_consistency | 189 | actual scaffold decision |
| random_retrieval | 176 | randomized decision baseline |
| shuffled_provenance | 15 | baseline-score-only proxy |
| contaminated_normal_bank_proxy | 153 | simulated reduced confidence |

## 8. 当前结论

1. 三类别数据链路已经跑通，说明 workflow 产物可以扩展到多类别真实数据。
2. 单类别 bottle 阈值直接迁移到多类别时不稳定，暴露出执行层 calibration 问题。
3. 这正好补强了项目叙事：workflow 不只是生成研究方案，还能通过真实执行反馈发现和定位实验层缺陷。
4. 不能把 V1.5 写成“多类别 IAD 性能很好”；应该写成“多类别 smoke test 暴露出跨类别校准需求”。

## 9. 下一步 V1.6

V1.6 应该做类别感知校准：

1. 对每个类别分别扫描 `anomaly_threshold` 和 `consistency_threshold`；
2. 输出 per-category recommended thresholds；
3. 重新生成 calibrated decisions；
4. 比较 global threshold 与 per-category threshold；
5. 如果 per-category 明显更稳，再写成 workflow 的 execution-feedback repair 案例。

边界：V1.6 仍然可以保持 lightweight scaffold，不必立刻接入完整 PatchCore。
