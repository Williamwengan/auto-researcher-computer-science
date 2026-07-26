# IAD MVP：Reference-Consistency Inspection Agent

这是比赛第一阶段 MVP 的最小工程目录。当前目标不是复现完整 PatchCore 论文，而是先搭出可运行、可评估、可展示的 IAD agent 闭环。

## 目标

输入一张工业检测图像和产品类别，输出：

- `anomaly_score`
- `anomaly_mask_or_region`
- `normal_reference_used`
- `confidence`
- `recommended_action`
- `failure_warning`

## 第一阶段模块

1. PatchCore-style baseline：提取正常图 patch feature，计算测试图异常热力图。
2. Reference consistency auditor：为可疑区域检索 top-k 正常参考 patch，并计算一致性/漂移/污染风险。
3. Structured report writer：输出结构化 JSON 报告。
4. Evaluator：比较 baseline 与 agent 的检测、定位、误报抑制和证据可信度。

## 当前状态

已完成环境检查。当前还缺 MVTec AD 或其他 IAD 数据集路径。

先运行：

```bash
cd /data1/huangyuling/-A_HYL/AI4S/ResearchArena-main
python iad_mvp/scripts/check_env.py
```

如果你已有 MVTec AD：

```bash
python iad_mvp/scripts/check_env.py --mvtec_root /path/to/mvtec_anomaly_detection
python iad_mvp/scripts/prepare_mvtec_subset.py --mvtec_root /path/to/mvtec_anomaly_detection --categories bottle cable capsule --output iad_mvp/data/mvtec_split.json
```

## 建议数据结构

MVTec AD 通常类似：

```text
mvtec_anomaly_detection/
  bottle/
    train/good/*.png
    test/good/*.png
    test/broken_large/*.png
    ground_truth/broken_large/*.png
```

## 后续脚本规划

- `run_patchcore_baseline.py`：跑 baseline heatmap 和 score。
- `score_reference_consistency.py`：计算 reference consistency。
- `run_reference_consistency_agent.py`：输出 agent inspection report。
- `evaluate_iad_agent.py`：生成指标表和可视化。
