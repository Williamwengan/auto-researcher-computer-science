# V1.6 IAD 类别感知阈值校准报告

生成时间：2026-07-14 20:54:37

生成脚本：`focused_workflow/scripts/build_v16_iad_per_category_threshold_calibration.py`

## 1. 为什么做 V1.6

V1.5 证明三类别数据链路可以跑通，但也发现 `bottle` 上校准出的全局阈值不能稳定迁移到 `cable/capsule`。因此 V1.6 不继续扩展更多类别，而是对每个类别分别扫描阈值，做类别感知 calibration。

这一步仍然是 lightweight scaffold calibration，不是完整 IAD benchmark。

## 2. Per-category 推荐阈值

选择规则：优先满足 `false_alarm_rate <= 0.05`，在低误报候选中最大化 anomaly recall，并对 review rate 施加轻微惩罚。

| category | anomaly_threshold | consistency_threshold | accept_anomaly | recall | fpr | review_rate | balanced_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bottle | 0.020000 | 0.999595 | 51 | 0.809524 | 0.000000 | 0.000000 | 0.809524 |
| cable | 0.365000 | 0.992815 | 42 | 0.445652 | 0.017241 | 0.000000 | 0.428411 |
| capsule | 0.005000 | 0.999800 | 22 | 0.201835 | 0.000000 | 0.045455 | 0.195017 |

## 3. Global threshold vs Per-category threshold

| scope | global_recall | global_fpr | global_score | per_cat_recall | per_cat_fpr | per_cat_score |
| --- | --- | --- | --- | --- | --- | --- |
| overall | 0.496212 | 0.574257 | -0.078045 | 0.431818 | 0.009901 | 0.419451 |
| bottle | 0.507937 | 0.000000 | 0.507937 | 0.809524 | 0.000000 | 0.809524 |
| cable | 1.000000 | 1.000000 | 0.000000 | 0.445652 | 0.017241 | 0.428411 |
| capsule | 0.064220 | 0.000000 | 0.064220 | 0.201835 | 0.000000 | 0.195017 |

核心结论：

- 全局阈值在三类别上 `false_alarm_rate` 很高，主要来自 `cable` 正常样本被大量误判。
- 类别感知阈值显著降低整体误报率，同时保留一部分异常召回。
- `capsule` 的 recall 仍然较低，说明仅靠当前 image-level lightweight feature 不足以稳定识别该类别异常；这应进入后续 feature/baseline 改进，而不是强行调参美化。

## 4. 输出文件

- Per-category sweep：`iad_mvp/outputs/tables_3cat/iad_per_category_threshold_sweep.csv`
- Per-category 推荐阈值：`iad_mvp/outputs/tables_3cat/iad_per_category_threshold_recommendations.csv`
- Per-category calibrated decisions：`iad_mvp/outputs/reference_consistency_3cat/iad_reference_consistency_scores_per_category_calibrated.csv`
- 指标汇总：`iad_mvp/outputs/tables_3cat/iad_per_category_calibrated_metrics.csv`
- JSON 汇总：`competition_submission/V16_IAD_PER_CATEGORY_THRESHOLD_CALIBRATION.json`

## 5. 应该怎么解释

V1.6 的价值不是“把 IAD 做到最好”，而是形成一个新的 execution-feedback repair 案例：

```text
V1.5 多类别迁移失败/不稳定
→ 诊断为全局阈值不鲁棒
→ V1.6 自动做类别感知阈值扫描
→ 显著降低误报，同时暴露 capsule 需要更强特征
```

这和你前面物理属性方向的 v1→v2 repair 故事是一致的：workflow 能发现失败、定位原因、生成修复策略，并把修复结果结构化输出。

## 6. 下一步 V1.7

V1.7 建议不要继续调阈值，而是修执行层特征：

1. 把三类别 reference bank 改为 category-constrained retrieval，避免跨类别最近邻污染；
2. 做 per-category score normalization，而不是全局 min-max；
3. 如果时间允许，再接入 PatchCore/anomalib 或 cached patch-level features；
4. 生成对比报告：global threshold vs per-category threshold vs category-constrained retrieval。
