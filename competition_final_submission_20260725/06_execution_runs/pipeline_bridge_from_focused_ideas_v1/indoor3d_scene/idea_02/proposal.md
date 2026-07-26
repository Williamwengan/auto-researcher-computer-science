# Evidence-grounded single-image 3D scene hypothesis planner：用 layout/depth/reconstruction baselines 生成候选场景，再用 scene-graph relation、support/collision checker 和 uncertainty annotation 修复几何与物理不一致。

生成时间：2026-07-25T15:34:11

来源：Focused Workflow V10 final research plan package，经 bridge 转换为 ResearchArena resume workspace。

## 1. 研究任务

从单张室内 RGB 图像推断 room layout、visible objects、occluded hypotheses、3D positions、geometry proxies、relations、materials/textures 和 renderable 3D scene representation。

## 2. Baseline 缺陷

- Text2Room/SceneScape/WonderJourney 等生成式方法可扩展场景，但容易缺少可验证的几何一致性。
- DUSt3R/MASt3R、monocular depth、NeRF/3DGS 等重建工具提供几何线索，但不直接保证 scene graph 和物理关系正确。
- 单图 3D 场景生成高度歧义，隐藏区域必须以 hypothesis + uncertainty 形式表达。
- 自动评估 scene plausibility 较难，需要 geometry、relation、collision、uncertainty 多维指标。

## 3. 论文证据与相关工作

- v0.7 indoor3d evidence-card repair 后：papers 18，claims 18，pass rate 1.0。
- 证据库覆盖 Text2Room、SceneScape、WonderJourney、DUSt3R、MASt3R、3D Gaussian Splatting、NeRF、HorizonNet、MiDaS、3D-FRONT、Matterport3D、ScanNet、Structured3D、Hypersim。
- 注意：该方向使用 seeded evidence bank，最终材料必须透明披露。

### Baselines

- Text2Room
- SceneScape
- WonderJourney
- monocular depth estimation
- DUSt3R / MASt3R style reconstruction
- NeRF / 3D Gaussian Splatting style reconstruction

## 4. 核心 Idea

Evidence-grounded single-image 3D scene hypothesis planner：用 layout/depth/reconstruction baselines 生成候选场景，再用 scene-graph relation、support/collision checker 和 uncertainty annotation 修复几何与物理不一致。

## 5. 核心假设

如果把单图 3D 生成拆成 visible evidence、layout/depth priors、scene graph hypotheses、physics/relation verification 和 uncertainty reporting，则可以比单纯生成式扩展更可检验、更适合下游任务。

## 6. 方法概述

- 从输入图像估计 room layout、visible object instances 和 monocular depth。
- 用 DUSt3R/MASt3R 或 depth/reconstruction baselines 生成几何候选。
- 生成 scene graph，包括 support relations、object relations、occluded region hypotheses。
- 用 collision/support/out-of-room checker 修复不合理 object placement。
- 输出 renderable proxy scene、uncertainty map 和 failure_warning。

### Minimal New Module

scene-graph hypothesis verifier with support/collision checks and uncertainty reporting

## 7. 实验计划

### E01 · Experiment step 1

- Phase: `data_preparation`
- Description: 构建 indoor3d_scene_manifest.jsonl，记录 input image、layout cues、visible objects 和 available GT/proxy labels。
- Expected artifact: `data/indoor3d_scene_manifest.jsonl`

### E02 · Experiment step 2

- Phase: `main_experiment`
- Description: 实现 build_scene_graph_hypotheses.py，生成 layout/object/relation candidates。
- Expected artifact: `scripts/build_scene_graph_hypotheses.py`

### E03 · Experiment step 3

- Phase: `main_experiment`
- Description: 实现 verify_scene_geometry.py，检查 support relation、collision、out-of-room 和 occlusion consistency。
- Expected artifact: `scripts/verify_scene_geometry.py`

### E04 · Experiment step 4

- Phase: `baseline_reproduction`
- Description: 对比 Text2Room/SceneScape/WonderJourney、depth-only、DUSt3R/MASt3R-style baselines。
- Expected artifact: `data/indoor3d_scene_manifest.jsonl`

### E05 · Experiment step 5

- Phase: `main_experiment`
- Description: 汇总 layout_iou、object_count_accuracy、relation_accuracy、collision_rate 和 failure_detection_auc。
- Expected artifact: `data/indoor3d_scene_manifest.jsonl`

## 8. 数据集与指标

### Datasets

- 3D-FRONT
- Matterport3D
- ScanNet
- Structured3D
- Hypersim

### Metrics

- depth_error
- layout_iou
- object_3d_iou
- object_count_accuracy
- support_relation_accuracy
- collision_rate
- out_of_room_rate
- novel_view_consistency
- failure_detection_auc

## 9. 消融与负控制

### Ablations

- remove scene graph verifier
- remove support/collision checker
- remove uncertainty reporting
- use depth-only reconstruction without relation constraints

### Negative Controls

- random object placement within the room
- shuffled scene graph relations
- use visible object count but random support relations
- disable occluded-region hypotheses

## 10. 成功阈值、失败条件与风险

### Success Thresholds

- collision_rate decreases relative to generation-only baseline
- support_relation_accuracy improves over depth-only or random-placement baselines
- layout_iou or object_count_accuracy improves over a layout-only baseline
- failure_detection_auc exceeds a simple uncertainty baseline

### Failure Criteria

- random placement baseline matches the verifier on relation/collision metrics
- uncertainty report fails to identify ambiguous or occluded regions
- scene graph constraints reduce visual plausibility without improving geometry metrics

### Risk and Mitigation

- 完整 3D 生成工程较重：先做 proxy scene graph 和 geometry verifier，不承诺训练大型生成模型。
- 单图隐藏区域高度不确定：必须输出 hypothesis confidence 和 failure_warning。
- seeded evidence bank 可能被质疑：最终报告中透明披露其来源和用途。

## 11. Judge 与证据校验状态

- Judge summary: v0.6 blind A/B: 3 reviewers, 9/9 after wins, win rate 1.0；Si-style benchmark after win rate 80%。
- Evidence verification: v0.7 evidence-card repair: pass rate 1.0, unsupported 0；使用 seeded evidence bank。

## 12. 下一步执行入口

实现 scene graph hypothesis verifier 的轻量 MVP，并用公开数据做 proxy consistency evaluation。

## 13. Honest Boundary

当前完成 idea-generation 方案级验证；尚未实现完整 3D 系统。
