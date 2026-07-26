# EXPERIMENT_PLAN

## Source

- Source package: `competition_submission/V10_FINAL_RESEARCH_PLAN_PACKAGE.json`
- Source plan id: `plan_05_iad_agent`
- Task: 工业异常检测 IAD + Agent

## Milestone 0 — Data and environment

1. Confirm dataset path or ask user to upload/download required data.
2. Build manifest files listed in implementation artifacts.
3. Verify train/test split and ground-truth labels.

Expected datasets:

- MVTec AD
- VisA
- MVTec LOCO
- BTAD
- MPDD

## Milestone 1 — Baseline reproduction

Reproduce or scaffold the following baselines:

- PatchCore
- PaDiM
- FastFlow
- DRAEM
- RD4AD
- WinCLIP
- AnomalyCLIP
- SAM/SAM2 assisted mask refinement

Output metrics as JSON/CSV. Do not use model predictions as ground truth.

## Milestone 2 — Proposed method

Implement:

reference-consistency scoring + evidence-grounded report checker + selective escalation policy

Method steps:

1. 构建 normal reference bank，记录 product category、image id、patch embedding 和 provenance。
2. 运行 PatchCore/PaDiM/WinCLIP/AnomalyCLIP 等 baseline 得到 anomaly score 和 region heatmap。
3. 检索 normal reference patches，计算 reference consistency score。
4. 用 cross-model disagreement 和 VLM report checker 验证 defect claim 是否绑定区域与参考图。
5. 根据 confidence 和 evidence grounding score 做 accept/abstain/human escalation。

## Milestone 3 — Main evaluation

Primary metrics:

- image_level_auroc
- pixel_level_auroc
- aupr
- pro_score
- mask_iou
- false_alarm_reduction
- evidence_grounding_score
- tool_success_rate
- human_escalation_precision
- calibration_error
- selective_risk

Success thresholds:

- image_level_auroc improves by at least 2.0 percentage points over strongest direct baseline on same split
- pixel_level_auroc or PRO improves by at least 1.0 percentage point without increasing false alarms
- false_alarm_reduction is at least 10% on shifted or contaminated normal-bank stress tests
- evidence_grounding_score is at least 85% for accepted reports

## Milestone 4 — Ablation and negative controls

Ablations:

- remove normal reference retrieval
- remove cross-model disagreement score
- remove evidence-grounded report checker
- remove escalation policy

Negative controls:

- random normal reference retrieval
- shuffled reference provenance
- contaminated normal bank with synthetic defect leakage
- report generation without region/reference verification

## Milestone 5 — Result-to-claim and paper draft

After experiments finish:

1. Parse result JSON/CSV.
2. Decide which claims are supported, partially supported, or unsupported.
3. Write `RESULT_SUMMARY.md`.
4. Write `PAPER_DRAFT.md` with only evidence-backed claims.
