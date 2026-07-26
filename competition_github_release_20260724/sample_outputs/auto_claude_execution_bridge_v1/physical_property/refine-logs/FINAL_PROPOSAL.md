# FINAL_PROPOSAL

## Title / Idea

Mechanism-consistent physical property prediction plan：保留 Idea 1 的 calibrated interval mapper，将 Idea 2 修复为 localized material evidence verifier，将 Idea 3 修复为 proposal uncertainty propagation。

## Motivation

如果物理属性预测不直接输出单点值，而是把 object mask、category、material evidence、property table 和 uncertainty propagation 组合成 calibrated intervals，则可以降低虚假精确性，并通过 selective prediction 改善可靠性。

## Proposed Approach

- 用 GroundingDINO/SAM2 或已有 segmentation 结果得到 object masks 和 categories。
- 用 CLIP/VLM/material recognizer 提取每个 object 的 material candidates 和 localized visual evidence。
- 构建 material-property table，把 density、Young's modulus、hardness、friction 等映射为 interval labels。
- 训练或规则化一个 calibrated interval mapper，输出 property interval 而不是单点预测。
- 用 proposal uncertainty propagation 聚合 detector、mask、material 和 table uncertainty，并在高风险样本上 abstain。

## Minimal New Module

localized material evidence verifier + calibrated property interval mapper + proposal uncertainty propagation

## Datasets

- ObjectFolder
- ObjectFolder2.0
- OpenSurfaces / MINC style material labels
- ScanNet / Matterport3D style indoor scene images
- engineering material property tables

## Baselines

- category-only property prior
- CLIP or VLM material classifier + property table lookup
- GroundingDINO/SAM2 mask + material lookup
- shuffled material-property table negative baseline

## Metrics

- density_log_mae
- youngs_modulus_log_mae
- poisson_ratio_mae
- hardness ordinal error
- friction_coefficient_mae
- prediction_interval_coverage
- calibration_error
- selective_risk

## Success Thresholds

- nominal 90% property intervals achieve at least 80% empirical coverage on proxy labels
- density_log_mae or youngs_modulus_log_mae improves by at least 5% over category-only priors
- calibration_error is less than 0.10 for accepted predictions
- selective_risk decreases as abstention threshold increases

## Failure Criteria

- shuffled material-property table performs within 5% of the real table on primary metrics
- interval coverage is not better than uncalibrated midpoint prediction
- uncertainty threshold does not reduce selective risk

## Risks and Mitigation

- 真实物理属性标签难获得：先使用 proxy interval labels 和 material table 做可证伪 MVP。
- 单张 RGB 难以观察隐藏结构：输出 interval 和 failure_warning，不做虚假精确预测。
- repair 曾出现机制错配：后续必须加入 mechanism consistency checker。
