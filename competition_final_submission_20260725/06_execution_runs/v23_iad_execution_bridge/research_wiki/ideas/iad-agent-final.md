---
type: idea
node_id: idea:iad-agent-final
title: "Evidence-Grounded Reference-Consistency IAD Agent"
stage: piloted
outcome: mixed
added: 2026-07-25T03:04:30Z
based_on: []
target_gaps: []
tags: ["iad", "final-plan", "execution-bridge"]
---

# Evidence-Grounded Reference-Consistency IAD Agent

**stage:** `piloted`  ·  **outcome:** `mixed`

Evidence-Grounded Reference-Consistency IAD Agent：以 normal reference retrieval 为核心，结合 anomaly heatmap、cross-model disagreement、region-reference consistency score、report checker 和 escalation policy。

## Thesis
如果 defect claim 必须同时绑定 anomaly region、normal reference contrast、model disagreement 和 evidence-grounded report check，则可以降低由 texture/lighting/reference shift 导致的 false alarms，并提高报告可信度。

## Key risks
Agent 输出可能变成普通报告生成：用 fixed schema、evidence ids 和 region masks 约束。
normal reference bank 可能被污染：加入 contaminated-bank negative controls。
v0.7 仍有 manual-check claims：保留人工复核标记，不把它们写成 fully supported。

## Connections
_Edges are recorded in `graph/edges.jsonl`; summarize here for human readers._

