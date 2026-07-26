# Mechanism-consistent physical property prediction plan：保留 Idea 1 的 calibrated interval mapper，将 Idea 2 修复为 localized material evidence verifier，将 Idea 3 修复为 proposal uncertainty propagation。

生成时间：2026-07-25T15:34:11

来源：Focused Workflow V10 final research plan package，经 bridge 转换为 ResearchArena resume workspace。

## 1. 研究任务

从单张 2D 室内场景图像中，为每个可见物体预测 density、Young's modulus、Poisson ratio、hardness、friction coefficient 等物理属性，并输出不确定性和失败警告。

## 2. Baseline 缺陷

- 检测/分割模型能给出 object mask 或 category，但不能直接给出可靠物理属性。
- CLIP/VLM/material recognition 可提供材料线索，但容易把可见材质和真实材料结构混淆。
- ObjectFolder/ObjectFolder2.0 等物理属性来源和真实室内图像之间存在 domain gap。
- 缺少 calibrated interval prediction，单点数值预测容易产生虚假精确性。

## 3. 论文证据与相关工作

- v0.7 evidence-card repair 后：papers 51，claims 15，pass rate 1.0。
- 证据链覆盖 ObjectFolder/ObjectFolder2.0、CLIP、SAM/SAM2、GroundingDINO、VLM material claim evidence 和 proposal uncertainty evidence。

### Baselines

- category-only property prior
- CLIP or VLM material classifier + property table lookup
- GroundingDINO/SAM2 mask + material lookup
- shuffled material-property table negative baseline

## 4. 核心 Idea

Mechanism-consistent physical property prediction plan：保留 Idea 1 的 calibrated interval mapper，将 Idea 2 修复为 localized material evidence verifier，将 Idea 3 修复为 proposal uncertainty propagation。

## 5. 核心假设

如果物理属性预测不直接输出单点值，而是把 object mask、category、material evidence、property table 和 uncertainty propagation 组合成 calibrated intervals，则可以降低虚假精确性，并通过 selective prediction 改善可靠性。

## 6. 方法概述

- 用 GroundingDINO/SAM2 或已有 segmentation 结果得到 object masks 和 categories。
- 用 CLIP/VLM/material recognizer 提取每个 object 的 material candidates 和 localized visual evidence。
- 构建 material-property table，把 density、Young's modulus、hardness、friction 等映射为 interval labels。
- 训练或规则化一个 calibrated interval mapper，输出 property interval 而不是单点预测。
- 用 proposal uncertainty propagation 聚合 detector、mask、material 和 table uncertainty，并在高风险样本上 abstain。

### Minimal New Module

localized material evidence verifier + calibrated property interval mapper + proposal uncertainty propagation

## 7. 实验计划

### E01 · Experiment step 1

- Phase: `data_preparation`
- Description: 构建 indoor_property_manifest.jsonl，包含 image id、object mask、category、material candidates 和 proxy interval labels。
- Expected artifact: `data/indoor_property_manifest.jsonl`

### E02 · Experiment step 2

- Phase: `main_experiment`
- Description: 实现 build_material_property_table.py，整理材料属性区间及证据来源。
- Expected artifact: `scripts/build_material_property_table.py`

### E03 · Experiment step 3

- Phase: `main_experiment`
- Description: 实现 predict_property_intervals.py，输出 calibrated interval、confidence 和 abstention decision。
- Expected artifact: `scripts/predict_property_intervals.py`

### E04 · Experiment step 4

- Phase: `baseline_reproduction`
- Description: 运行 category-only prior、CLIP/VLM material baseline 和 shuffled-table baseline。
- Expected artifact: `data/indoor_property_manifest.jsonl`

### E05 · Experiment step 5

- Phase: `main_experiment`
- Description: 汇总 density_log_mae、coverage、calibration_error 和 selective_risk。
- Expected artifact: `data/indoor_property_manifest.jsonl`

## 8. 数据集与指标

### Datasets

- ObjectFolder
- ObjectFolder2.0
- OpenSurfaces / MINC style material labels
- ScanNet / Matterport3D style indoor scene images
- engineering material property tables

### Metrics

- density_log_mae
- youngs_modulus_log_mae
- poisson_ratio_mae
- hardness ordinal error
- friction_coefficient_mae
- prediction_interval_coverage
- calibration_error
- selective_risk

## 9. 消融与负控制

### Ablations

- remove localized material evidence verifier
- remove calibrated interval loss and output midpoint only
- remove proposal uncertainty propagation
- use category-only prior without material evidence

### Negative Controls

- shuffle material-property table entries
- use random object categories
- use background masks instead of object masks
- permute material prompts across objects

## 10. 成功阈值、失败条件与风险

### Success Thresholds

- nominal 90% property intervals achieve at least 80% empirical coverage on proxy labels
- density_log_mae or youngs_modulus_log_mae improves by at least 5% over category-only priors
- calibration_error is less than 0.10 for accepted predictions
- selective_risk decreases as abstention threshold increases

### Failure Criteria

- shuffled material-property table performs within 5% of the real table on primary metrics
- interval coverage is not better than uncalibrated midpoint prediction
- uncertainty threshold does not reduce selective risk

### Risk and Mitigation

- 真实物理属性标签难获得：先使用 proxy interval labels 和 material table 做可证伪 MVP。
- 单张 RGB 难以观察隐藏结构：输出 interval 和 failure_warning，不做虚假精确预测。
- repair 曾出现机制错配：后续必须加入 mechanism consistency checker。

## 11. Judge 与证据校验状态

- Judge summary: v2 mechanism-consistent repair: 6 reviewers, 18/18 after wins, win rate 1.0。
- Evidence verification: v0.7 repaired evidence cards: pass rate 1.0, unsupported 0。

## 12. 下一步执行入口

实现 material-property table 与 interval prediction MVP，并跑 proxy-label calibration experiment。

## 13. Honest Boundary

当前完成最终研究方案生成；尚未执行真实训练/评测。
