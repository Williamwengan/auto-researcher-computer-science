# RESEARCH_BRIEF

## Problem Statement

为工业异常检测构建 agentic inspection workflow，使系统能协调 normal reference retrieval、defect localization、self-checking、evidence-grounded report 和 human escalation。

## Selected Idea

Evidence-Grounded Reference-Consistency IAD Agent：以 normal reference retrieval 为核心，结合 anomaly heatmap、cross-model disagreement、region-reference consistency score、report checker 和 escalation policy。

## Core Hypothesis

如果 defect claim 必须同时绑定 anomaly region、normal reference contrast、model disagreement 和 evidence-grounded report check，则可以降低由 texture/lighting/reference shift 导致的 false alarms，并提高报告可信度。

## Baseline Gaps

- PatchCore/PaDiM/WinCLIP 等 IAD baseline 对 reference shift、texture/lighting variation 和 contaminated normal bank 敏感。
- VLM 生成的 defect description 可能没有绑定具体区域或 normal reference evidence。
- 异常标签稀缺，pixel-level labels 更稀缺，需要 negative controls 和 selective prediction。
- 普通 agent 报告容易成为文本生成器，缺少 tool success、evidence grounding 和 escalation metrics。

## Evidence Status

- v0.7 reference claim verification：papers 24，claims 21，pass rate 0.857，unsupported 0，manual 3。
- 证据状态允许保留 manual-check claims，但最终报告中不能把 manual-check 当成 fully supported。

- Evidence verification: v0.7 pass rate 0.857, unsupported 0, manual 3。
- Judge summary: v0.6 blind A/B: 3 reviewers, 7/9 after wins, win rate 0.778；Si-style benchmark after win rate 60%。

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
