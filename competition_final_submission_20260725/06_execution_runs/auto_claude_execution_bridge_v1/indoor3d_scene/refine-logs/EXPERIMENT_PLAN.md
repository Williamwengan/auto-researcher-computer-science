# EXPERIMENT_PLAN

## Source

- Source package: `competition_submission/V10_FINAL_RESEARCH_PLAN_PACKAGE.json`
- Source plan id: `plan_03_indoor3d`
- Task: 室内单图 3D 场景生成

## Milestone 0 — Data and environment

1. Confirm dataset path or ask user to upload/download required data.
2. Build manifest files listed in implementation artifacts.
3. Verify train/test split and ground-truth labels.

Expected datasets:

- 3D-FRONT
- Matterport3D
- ScanNet
- Structured3D
- Hypersim

## Milestone 1 — Baseline reproduction

Reproduce or scaffold the following baselines:

- Text2Room
- SceneScape
- WonderJourney
- monocular depth estimation
- DUSt3R / MASt3R style reconstruction
- NeRF / 3D Gaussian Splatting style reconstruction

Output metrics as JSON/CSV. Do not use model predictions as ground truth.

## Milestone 2 — Proposed method

Implement:

scene-graph hypothesis verifier with support/collision checks and uncertainty reporting

Method steps:

1. 从输入图像估计 room layout、visible object instances 和 monocular depth。
2. 用 DUSt3R/MASt3R 或 depth/reconstruction baselines 生成几何候选。
3. 生成 scene graph，包括 support relations、object relations、occluded region hypotheses。
4. 用 collision/support/out-of-room checker 修复不合理 object placement。
5. 输出 renderable proxy scene、uncertainty map 和 failure_warning。

## Milestone 3 — Main evaluation

Primary metrics:

- depth_error
- layout_iou
- object_3d_iou
- object_count_accuracy
- support_relation_accuracy
- collision_rate
- out_of_room_rate
- novel_view_consistency
- failure_detection_auc

Success thresholds:

- collision_rate decreases relative to generation-only baseline
- support_relation_accuracy improves over depth-only or random-placement baselines
- layout_iou or object_count_accuracy improves over a layout-only baseline
- failure_detection_auc exceeds a simple uncertainty baseline

## Milestone 4 — Ablation and negative controls

Ablations:

- remove scene graph verifier
- remove support/collision checker
- remove uncertainty reporting
- use depth-only reconstruction without relation constraints

Negative controls:

- random object placement within the room
- shuffled scene graph relations
- use visible object count but random support relations
- disable occluded-region hypotheses

## Milestone 5 — Result-to-claim and paper draft

After experiments finish:

1. Parse result JSON/CSV.
2. Decide which claims are supported, partially supported, or unsupported.
3. Write `RESULT_SUMMARY.md`.
4. Write `PAPER_DRAFT.md` with only evidence-backed claims.
