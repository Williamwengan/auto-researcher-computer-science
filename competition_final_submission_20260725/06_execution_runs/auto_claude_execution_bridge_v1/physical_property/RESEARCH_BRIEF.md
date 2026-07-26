# RESEARCH_BRIEF

## Problem Statement

从单张 2D 室内场景图像中，为每个可见物体预测 density、Young's modulus、Poisson ratio、hardness、friction coefficient 等物理属性，并输出不确定性和失败警告。

## Selected Idea

Mechanism-consistent physical property prediction plan：保留 Idea 1 的 calibrated interval mapper，将 Idea 2 修复为 localized material evidence verifier，将 Idea 3 修复为 proposal uncertainty propagation。

## Core Hypothesis

如果物理属性预测不直接输出单点值，而是把 object mask、category、material evidence、property table 和 uncertainty propagation 组合成 calibrated intervals，则可以降低虚假精确性，并通过 selective prediction 改善可靠性。

## Baseline Gaps

- 检测/分割模型能给出 object mask 或 category，但不能直接给出可靠物理属性。
- CLIP/VLM/material recognition 可提供材料线索，但容易把可见材质和真实材料结构混淆。
- ObjectFolder/ObjectFolder2.0 等物理属性来源和真实室内图像之间存在 domain gap。
- 缺少 calibrated interval prediction，单点数值预测容易产生虚假精确性。

## Evidence Status

- v0.7 evidence-card repair 后：papers 51，claims 15，pass rate 1.0。
- 证据链覆盖 ObjectFolder/ObjectFolder2.0、CLIP、SAM/SAM2、GroundingDINO、VLM material claim evidence 和 proposal uncertainty evidence。

- Evidence verification: v0.7 repaired evidence cards: pass rate 1.0, unsupported 0。
- Judge summary: v2 mechanism-consistent repair: 6 reviewers, 18/18 after wins, win rate 1.0。

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
