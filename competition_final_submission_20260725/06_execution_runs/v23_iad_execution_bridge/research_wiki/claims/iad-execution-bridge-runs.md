---
type: claim
node_id: claim:iad-execution-bridge-runs
name: "IAD final research plan can be connected to executable smoke-test artifacts"
description: ""
node_type: claim
status: sound-modulo-imports
provenance: "/data1/huangyuling/-A_HYL/AI4S/ResearchArena-main/execution_runs/v23_iad_execution_bridge"
tags: ["execution", "iad", "workflow"]
date: 2026-07-25
added: 2026-07-25T03:04:30Z
---

# IAD final research plan can be connected to executable smoke-test artifacts

**status:** `sound-modulo-imports`

## Statement
The V10 IAD final plan is bridged to a concrete iad_mvp execution chain and produces metrics artifacts.

## Honest scope
Scaffold-level MVTec AD smoke test; not full PatchCore/anomalib benchmark.

## Evidence chain
Metrics file: /data1/huangyuling/-A_HYL/AI4S/ResearchArena-main/iad_mvp/outputs/tables/iad_agent_execution_metrics.csv; metrics: {
  "image_level_auc_lightweight": 0.945238,
  "baseline_false_alarms_at_threshold": 0.0,
  "agent_false_alarms_at_threshold": 0.0,
  "false_alarm_reduction_proxy": 0.0,
  "evidence_grounding_score_proxy": 1.0,
  "tool_success_rate": 1.0,
  "note": "scaffold metrics; not final benchmark results"
}

## Connections
_Edges are recorded in `graph/edges.jsonl`; summarize here for human readers._

