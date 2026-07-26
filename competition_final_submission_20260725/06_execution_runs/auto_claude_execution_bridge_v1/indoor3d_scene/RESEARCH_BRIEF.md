# RESEARCH_BRIEF

## Problem Statement

从单张室内 RGB 图像推断 room layout、visible objects、occluded hypotheses、3D positions、geometry proxies、relations、materials/textures 和 renderable 3D scene representation。

## Selected Idea

Evidence-grounded single-image 3D scene hypothesis planner：用 layout/depth/reconstruction baselines 生成候选场景，再用 scene-graph relation、support/collision checker 和 uncertainty annotation 修复几何与物理不一致。

## Core Hypothesis

如果把单图 3D 生成拆成 visible evidence、layout/depth priors、scene graph hypotheses、physics/relation verification 和 uncertainty reporting，则可以比单纯生成式扩展更可检验、更适合下游任务。

## Baseline Gaps

- Text2Room/SceneScape/WonderJourney 等生成式方法可扩展场景，但容易缺少可验证的几何一致性。
- DUSt3R/MASt3R、monocular depth、NeRF/3DGS 等重建工具提供几何线索，但不直接保证 scene graph 和物理关系正确。
- 单图 3D 场景生成高度歧义，隐藏区域必须以 hypothesis + uncertainty 形式表达。
- 自动评估 scene plausibility 较难，需要 geometry、relation、collision、uncertainty 多维指标。

## Evidence Status

- v0.7 indoor3d evidence-card repair 后：papers 18，claims 18，pass rate 1.0。
- 证据库覆盖 Text2Room、SceneScape、WonderJourney、DUSt3R、MASt3R、3D Gaussian Splatting、NeRF、HorizonNet、MiDaS、3D-FRONT、Matterport3D、ScanNet、Structured3D、Hypersim。
- 注意：该方向使用 seeded evidence bank，最终材料必须透明披露。

- Evidence verification: v0.7 evidence-card repair: pass rate 1.0, unsupported 0；使用 seeded evidence bank。
- Judge summary: v0.6 blind A/B: 3 reviewers, 9/9 after wins, win rate 1.0；Si-style benchmark after win rate 80%。

## What I'm Looking For

Use Auto-claude/ARIS-style experiment execution to turn this idea into:

1. reproducible baseline code or reused baseline runner;
2. proposed-module implementation;
3. sanity and main experiment results;
4. ablation / negative-control evidence;
5. result-to-claim record;
6. paper draft grounded in actually executed results.

## Constraints

- Do not claim benchmark-grade SOTA unless full benchmark experiments actually run.
- Ask for human authorization before API calls, package installation, large downloads, or GPU jobs.
- If data is missing, stop and request dataset path or upload.
- Keep results machine-readable as JSON/CSV.
