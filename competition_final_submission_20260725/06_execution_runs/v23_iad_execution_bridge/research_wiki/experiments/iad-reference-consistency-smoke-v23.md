---
type: experiment
node_id: exp:iad-reference-consistency-smoke-v23
title: "IAD reference-consistency execution bridge smoke test"
idea_id: "idea:iad-agent-final"
verdict: partial
confidence: medium
date: ""
hardware: "local/server scaffold"
duration: "short smoke test"
provenance: "/data1/huangyuling/-A_HYL/AI4S/ResearchArena-main/iad_mvp/outputs/tables/iad_agent_execution_metrics.csv"
added: 2026-07-25T03:04:30Z
tags: ["iad", "execution-bridge", "smoke-test"]
---

# IAD reference-consistency execution bridge smoke test

**verdict:** `partial`  ·  **confidence:** `medium`  ·  tests `idea:iad-agent-final`

## Metrics
{
  "image_level_auc_lightweight": 0.945238,
  "baseline_false_alarms_at_threshold": 0.0,
  "agent_false_alarms_at_threshold": 0.0,
  "false_alarm_reduction_proxy": 0.0,
  "evidence_grounding_score_proxy": 1.0,
  "tool_success_rate": 1.0,
  "note": "scaffold metrics; not final benchmark results"
}

## Reasoning
The script chain produced manifest, reference bank, baseline scores, reference-consistency scores, and metrics. This supports scaffold-level execution, but not full benchmark-grade IAD performance.

## Connections
_Edges are recorded in `graph/edges.jsonl`; summarize here for human readers._

