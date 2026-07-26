# V1.7 IAD 类别约束检索与类别内归一化报告

生成时间：2026-07-14 20:59:07

生成脚本：`focused_workflow/scripts/build_v17_iad_category_constrained_retrieval_report.py`

## 1. 为什么做 V1.7

V1.6 已经证明类别感知阈值能显著降低误报，但它仍然基于 V1.5 的执行层产物。V1.7 进一步修执行层的两个根因：

1. reference retrieval 只在同一 product category 内检索，避免跨类别最近邻污染；
2. baseline score 按类别分别 min-max normalize，避免全局归一化让某个类别支配阈值。

这一步仍然是 lightweight scaffold，不是完整 PatchCore/anomalib benchmark。

## 2. V1.7 推荐阈值

| category | anomaly_threshold | consistency_threshold | accept_anomaly | recall | fpr | review_rate | score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bottle | 0.040000 | 0.999595 | 51 | 0.809524 | 0.000000 | 0.000000 | 0.809524 |
| cable | 0.295000 | 0.992815 | 42 | 0.445652 | 0.017241 | 0.000000 | 0.428411 |
| capsule | 0.055000 | 0.999872 | 23 | 0.211009 | 0.000000 | 0.000000 | 0.211009 |

## 3. V1.6 vs V1.7 对比

| scope | v16_recall | v16_fpr | v16_score | v17_recall | v17_fpr | v17_score |
| --- | --- | --- | --- | --- | --- | --- |
| overall | 0.431818 | 0.009901 | 0.419451 | 0.435606 | 0.009901 | 0.425705 |
| bottle | 0.809524 | 0.000000 | 0.809524 | 0.809524 | 0.000000 | 0.809524 |
| cable | 0.445652 | 0.017241 | 0.428411 | 0.445652 | 0.017241 | 0.428411 |
| capsule | 0.201835 | 0.000000 | 0.195017 | 0.211009 | 0.000000 | 0.211009 |

整体变化：

- V1.6 overall score: 0.419451
- V1.7 overall score: 0.425705
- V1.6 overall fpr: 0.009901
- V1.7 overall fpr: 0.009901

## 4. 如何解释

V1.7 的重点不是“轻量 baseline 已经足够强”，而是证明 workflow 可以继续从执行反馈中定位更底层的问题：

```text
V1.5：全局阈值跨类别失败
V1.6：类别感知阈值降低误报
V1.7：进一步修正跨类别 reference retrieval 与全局归一化
```

如果 V1.7 比 V1.6 改善，说明执行层修复有效；如果某些类别仍弱，说明问题进入 feature/baseline 层，需要 patch-level feature 或 PatchCore/anomalib。

## 5. 输出文件

- V1.7 baseline scores：`iad_mvp/outputs/patchcore_baseline_3cat_category_constrained/iad_baseline_scores.csv`
- V1.7 consistency scores：`iad_mvp/outputs/reference_consistency_3cat_category_constrained/iad_reference_consistency_scores.csv`
- V1.7 threshold sweep：`iad_mvp/outputs/tables_3cat/iad_v17_category_constrained_threshold_sweep.csv`
- V1.7 recommendations：`iad_mvp/outputs/tables_3cat/iad_v17_category_constrained_threshold_recommendations.csv`
- V1.7 metrics：`iad_mvp/outputs/tables_3cat/iad_v17_category_constrained_metrics.csv`
- JSON 汇总：`competition_submission/V17_IAD_CATEGORY_CONSTRAINED_RETRIEVAL.json`

## 6. 下一步建议

如果 V1.7 已经明显优于 V1.6，可以把 V1.3–V1.7 作为一个完整 execution-feedback repair case 写进总报告。若还想继续做工程增强，下一步才考虑接入 PatchCore/anomalib 或 patch-level feature。
