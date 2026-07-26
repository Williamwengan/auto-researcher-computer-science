# FINAL_PROPOSAL

## Title / Idea

Evidence-grounded single-image 3D scene hypothesis planner：用 layout/depth/reconstruction baselines 生成候选场景，再用 scene-graph relation、support/collision checker 和 uncertainty annotation 修复几何与物理不一致。

## Motivation

如果把单图 3D 生成拆成 visible evidence、layout/depth priors、scene graph hypotheses、physics/relation verification 和 uncertainty reporting，则可以比单纯生成式扩展更可检验、更适合下游任务。

## Proposed Approach

- 从输入图像估计 room layout、visible object instances 和 monocular depth。
- 用 DUSt3R/MASt3R 或 depth/reconstruction baselines 生成几何候选。
- 生成 scene graph，包括 support relations、object relations、occluded region hypotheses。
- 用 collision/support/out-of-room checker 修复不合理 object placement。
- 输出 renderable proxy scene、uncertainty map 和 failure_warning。

## Minimal New Module

scene-graph hypothesis verifier with support/collision checks and uncertainty reporting

## Datasets

- 3D-FRONT
- Matterport3D
- ScanNet
- Structured3D
- Hypersim

## Baselines

- Text2Room
- SceneScape
- WonderJourney
- monocular depth estimation
- DUSt3R / MASt3R style reconstruction
- NeRF / 3D Gaussian Splatting style reconstruction

## Metrics

- depth_error
- layout_iou
- object_3d_iou
- object_count_accuracy
- support_relation_accuracy
- collision_rate
- out_of_room_rate
- novel_view_consistency
- failure_detection_auc

## Success Thresholds

- collision_rate decreases relative to generation-only baseline
- support_relation_accuracy improves over depth-only or random-placement baselines
- layout_iou or object_count_accuracy improves over a layout-only baseline
- failure_detection_auc exceeds a simple uncertainty baseline

## Failure Criteria

- random placement baseline matches the verifier on relation/collision metrics
- uncertainty report fails to identify ambiguous or occluded regions
- scene graph constraints reduce visual plausibility without improving geometry metrics

## Risks and Mitigation

- 完整 3D 生成工程较重：先做 proxy scene graph 和 geometry verifier，不承诺训练大型生成模型。
- 单图隐藏区域高度不确定：必须输出 hypothesis confidence 和 failure_warning。
- seeded evidence bank 可能被质疑：最终报告中透明披露其来源和用途。
