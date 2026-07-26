# Experiment Log

## Experiment: IAD Reference-Consistency Smoke Test

**Date**: 2026-07-25

**Idea**: Evidence-Grounded Reference-Consistency IAD Agent：以 normal reference retrieval 为核心，结合 anomaly heatmap、cross-model disagreement、region-reference consistency score、report checker 和 escalation policy。

**Goal**: 验证 final research plan 能否进入真实数据执行链路，并生成可读取 metrics。

### Setup

- **Method**: lightweight nearest-reference baseline + reference-consistency agent scaffold
- **Dataset**: MVTec AD default/smoke split
- **Baseline**: lightweight nearest-reference baseline, not full PatchCore
- **Config**: default `iad_mvp` scaffold paths

### Results

| Method | Metric | Value | Notes |
| --- | --- | ---: | --- |
| lightweight baseline | image_level_auc_lightweight | 0.945238 | scaffold metric |
| reference-consistency agent | tool_success_rate | 1.0 | script chain completed |
| reference-consistency agent | evidence_grounding_score_proxy | 1.0 | proxy |
| reference-consistency agent | false_alarm_reduction_proxy | 0.0 | proxy |

### Verdict

- **Supports execution claim?** Partially / Yes for scaffold execution.
- **Supports scientific performance claim?** Not yet; full benchmark-grade implementation is still required.
- **Key takeaway**: The workflow can progress from final idea to real-data execution artifacts, but the execution engine remains lightweight.

### Reproduction

```bash
python iad_mvp/scripts/prepare_iad_reference_manifest.py
python iad_mvp/scripts/build_reference_bank.py
python iad_mvp/scripts/run_iad_baselines.py
python iad_mvp/scripts/score_reference_consistency.py
python iad_mvp/scripts/evaluate_iad_agent.py
```
