# FINAL_PROPOSAL

## Title / Idea

Evidence-Grounded Reference-Consistency IAD Agent：以 normal reference retrieval 为核心，结合 anomaly heatmap、cross-model disagreement、region-reference consistency score、report checker 和 escalation policy。

## Motivation

如果 defect claim 必须同时绑定 anomaly region、normal reference contrast、model disagreement 和 evidence-grounded report check，则可以降低由 texture/lighting/reference shift 导致的 false alarms，并提高报告可信度。

## Proposed Approach

- 构建 normal reference bank，记录 product category、image id、patch embedding 和 provenance。
- 运行 PatchCore/PaDiM/WinCLIP/AnomalyCLIP 等 baseline 得到 anomaly score 和 region heatmap。
- 检索 normal reference patches，计算 reference consistency score。
- 用 cross-model disagreement 和 VLM report checker 验证 defect claim 是否绑定区域与参考图。
- 根据 confidence 和 evidence grounding score 做 accept/abstain/human escalation。

## Minimal New Module

reference-consistency scoring + evidence-grounded report checker + selective escalation policy

## Datasets

- MVTec AD
- VisA
- MVTec LOCO
- BTAD
- MPDD

## Baselines

- PatchCore
- PaDiM
- FastFlow
- DRAEM
- RD4AD
- WinCLIP
- AnomalyCLIP
- SAM/SAM2 assisted mask refinement

## Metrics

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

## Success Thresholds

- image_level_auroc improves by at least 2.0 percentage points over strongest direct baseline on same split
- pixel_level_auroc or PRO improves by at least 1.0 percentage point without increasing false alarms
- false_alarm_reduction is at least 10% on shifted or contaminated normal-bank stress tests
- evidence_grounding_score is at least 85% for accepted reports

## Failure Criteria

- negative controls reach within 5% of the full agent on primary metrics
- agent report correctness improves but detection/localization metrics degrade significantly
- manual-check claims remain unresolved in final report claims

## Risks and Mitigation

- Agent 输出可能变成普通报告生成：用 fixed schema、evidence ids 和 region masks 约束。
- normal reference bank 可能被污染：加入 contaminated-bank negative controls。
- v0.7 仍有 manual-check claims：保留人工复核标记，不把它们写成 fully supported。
