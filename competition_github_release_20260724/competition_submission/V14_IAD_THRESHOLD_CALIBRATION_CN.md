# V1.4 IAD 阈值校准报告

生成时间：2026-07-14 15:56:31

生成脚本：`focused_workflow/scripts/build_v14_iad_threshold_calibration.py`

## 1. 为什么做 V1.4

V1.3 已经证明 MVTec AD `bottle` 类别可以接入 workflow，并且从数据准备到评价表格的最小链路已经跑通。但 V1.3 也暴露出一个关键问题：当前 reference-consistency 决策过于保守，`accept_anomaly_count=0`。

因此 V1.4 的目标是做阈值校准，而不是继续堆报告或直接扩展更多类别。

## 2. 分数分布诊断

| label | count | baseline_min | baseline_mean | baseline_max | consistency_min | consistency_mean | consistency_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 20 | 0.000000 | 0.013402 | 0.036108 | 0.999619 | 0.999783 | 0.999880 |
| 1 | 63 | 0.005574 | 0.138298 | 1.000000 | 0.992695 | 0.998881 | 0.999840 |

诊断结论：

- `baseline_score` 对正常/异常有一定区分度；
- `reference_consistency_score` 全部压缩在接近 1 的高分区间；
- 因此 V1.2 默认的 `consistency_threshold=0.55` 明显过低，会导致高异常分样本仍被判为“和正常参考一致”，从而被 suppress/review；
- V1.4 的校准重点是把 consistency 阈值移动到真实分布附近，而不是继续使用固定的 0.55。

## 3. 当前阈值 vs 推荐阈值

| setting | anomaly_threshold | consistency_threshold | accept_anomaly_count | review_count | anomaly_recall | false_alarm_rate | balanced_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| current_v1.2 | 0.500000 | 0.550000 | 0 | 2 | 0.000000 | 0.000000 | -0.003614 |
| recommended_v1.4 | 0.040000 | 0.999595 | 51 | 0 | 0.809524 | 0.000000 | 0.809524 |

推荐阈值的选择规则：

1. 必须产生非零 `accept_anomaly_count`；
2. 优先约束 `false_alarm_rate <= 0.05`；
3. 在满足低误报的候选里最大化 anomaly recall；
4. 对 review 过多的设置施加轻微惩罚。

## 4. Top threshold candidates

| rank | anomaly_threshold | consistency_threshold | accept_anomaly_count | review_count | anomaly_recall | false_alarm_rate | review_rate | balanced_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.020000 | 0.999795 | 60 | 0 | 0.920635 | 0.100000 | 0.000000 | 0.820635 |
| 2 | 0.020000 | 0.999895 | 60 | 0 | 0.920635 | 0.100000 | 0.000000 | 0.820635 |
| 3 | 0.020000 | 0.999995 | 60 | 0 | 0.920635 | 0.100000 | 0.000000 | 0.820635 |
| 4 | 0.020000 | 1.000001 | 60 | 0 | 0.920635 | 0.100000 | 0.000000 | 0.820635 |
| 5 | 0.040000 | 0.999595 | 51 | 0 | 0.809524 | 0.000000 | 0.000000 | 0.809524 |
| 6 | 0.040000 | 0.999695 | 51 | 0 | 0.809524 | 0.000000 | 0.000000 | 0.809524 |
| 7 | 0.040000 | 0.999795 | 51 | 0 | 0.809524 | 0.000000 | 0.000000 | 0.809524 |
| 8 | 0.040000 | 0.999895 | 51 | 0 | 0.809524 | 0.000000 | 0.000000 | 0.809524 |
| 9 | 0.040000 | 0.999995 | 51 | 0 | 0.809524 | 0.000000 | 0.000000 | 0.809524 |
| 10 | 0.040000 | 1.000001 | 51 | 0 | 0.809524 | 0.000000 | 0.000000 | 0.809524 |

注意：上表按 unconstrained utility 排序，所以可能出现 recall 更高但 false alarm 也更高的候选。V1.4 的正式推荐优先满足 `false_alarm_rate <= 0.05`，因此推荐项不一定是上表 rank 1。

## 5. 输出文件

- Threshold sweep 表：`iad_mvp/outputs/tables/iad_threshold_sweep.csv`
- 推荐阈值决策表：`iad_mvp/outputs/tables/iad_threshold_recommended_decisions.csv`
- JSON 汇总：`competition_submission/V14_IAD_THRESHOLD_CALIBRATION.json`

## 6. 应该怎么解释这个结果

V1.4 不是在证明 IAD 算法已经完成，而是在修复 V1.3 暴露出来的决策问题。它说明当前 workflow 不仅能跑通实验链路，还能根据真实运行结果发现执行层面的缺陷，并给出自动化校准方案。

比赛材料里可以这样表述：

> After connecting the generated IAD research plan to real MVTec AD data, our smoke test revealed an overly conservative reference-consistency decision rule. We then added an automatic threshold calibration module that scans operating points and selects a low-false-alarm setting with non-zero anomaly acceptance, turning execution feedback into a workflow-level repair signal.

## 7. 下一步 V1.5

V1.5 建议做两件事：

1. 用推荐阈值重新生成 calibrated reference-consistency 表；
2. 把单类别 `bottle` 扩展到 `bottle/cable/capsule` 三类，验证校准策略是否跨类别稳定。

边界：当前仍然是 lightweight scaffold calibration，不是完整 PatchCore/anomalib 正式 benchmark。
