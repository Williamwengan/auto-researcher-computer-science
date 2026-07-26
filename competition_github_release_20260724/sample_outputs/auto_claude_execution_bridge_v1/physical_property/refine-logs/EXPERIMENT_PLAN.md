# EXPERIMENT_PLAN

## Source

- Source package: `competition_submission/V10_FINAL_RESEARCH_PLAN_PACKAGE.json`
- Source plan id: `plan_01_physical_property`
- Task: 物理属性预测

## Milestone 0 — Data and environment

1. Confirm dataset path or ask user to upload/download required data.
2. Build manifest files listed in implementation artifacts.
3. Verify train/test split and ground-truth labels.

Expected datasets:

- ObjectFolder
- ObjectFolder2.0
- OpenSurfaces / MINC style material labels
- ScanNet / Matterport3D style indoor scene images
- engineering material property tables

## Milestone 1 — Baseline reproduction

Reproduce or scaffold the following baselines:

- category-only property prior
- CLIP or VLM material classifier + property table lookup
- GroundingDINO/SAM2 mask + material lookup
- shuffled material-property table negative baseline

Output metrics as JSON/CSV. Do not use model predictions as ground truth.

## Milestone 2 — Proposed method

Implement:

localized material evidence verifier + calibrated property interval mapper + proposal uncertainty propagation

Method steps:

1. 用 GroundingDINO/SAM2 或已有 segmentation 结果得到 object masks 和 categories。
2. 用 CLIP/VLM/material recognizer 提取每个 object 的 material candidates 和 localized visual evidence。
3. 构建 material-property table，把 density、Young's modulus、hardness、friction 等映射为 interval labels。
4. 训练或规则化一个 calibrated interval mapper，输出 property interval 而不是单点预测。
5. 用 proposal uncertainty propagation 聚合 detector、mask、material 和 table uncertainty，并在高风险样本上 abstain。

## Milestone 3 — Main evaluation

Primary metrics:

- density_log_mae
- youngs_modulus_log_mae
- poisson_ratio_mae
- hardness ordinal error
- friction_coefficient_mae
- prediction_interval_coverage
- calibration_error
- selective_risk

Success thresholds:

- nominal 90% property intervals achieve at least 80% empirical coverage on proxy labels
- density_log_mae or youngs_modulus_log_mae improves by at least 5% over category-only priors
- calibration_error is less than 0.10 for accepted predictions
- selective_risk decreases as abstention threshold increases

## Milestone 4 — Ablation and negative controls

Ablations:

- remove localized material evidence verifier
- remove calibrated interval loss and output midpoint only
- remove proposal uncertainty propagation
- use category-only prior without material evidence

Negative controls:

- shuffle material-property table entries
- use random object categories
- use background masks instead of object masks
- permute material prompts across objects

## Milestone 5 — Result-to-claim and paper draft

After experiments finish:

1. Parse result JSON/CSV.
2. Decide which claims are supported, partially supported, or unsupported.
3. Write `RESULT_SUMMARY.md`.
4. Write `PAPER_DRAFT.md` with only evidence-backed claims.
