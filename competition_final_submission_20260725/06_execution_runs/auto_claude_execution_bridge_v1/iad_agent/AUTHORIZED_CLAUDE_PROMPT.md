# Paste this into Claude Code / Codex after user authorization

You are now in an Auto-claude/ARIS-style experiment workspace.

Workspace:

```bash
cd /data1/huangyuling/-A_HYL/AI4S/ResearchArena-main/outputs/auto_claude_execution_bridge_v1/iad_agent
```

Task:

```text
工业异常检测 IAD + Agent
```

Selected focused idea:

```text
Evidence-Grounded Reference-Consistency IAD Agent：以 normal reference retrieval 为核心，结合 anomaly heatmap、cross-model disagreement、region-reference consistency score、report checker 和 escalation policy。
```

Please run the ARIS experiment bridge:

```text
/experiment-bridge refine-logs/EXPERIMENT_PLAN.md
```

Rules:

1. Read `CLAUDE.md`, `RESEARCH_BRIEF.md`, `refine-logs/FINAL_PROPOSAL.md`, and `refine-logs/EXPERIMENT_PLAN.md`.
2. Before downloading datasets, installing packages, using API keys, or launching GPU jobs, ask for human authorization.
3. First run the smallest sanity experiment.
4. Save logs and metrics under `runs/`.
5. After results are available, create `RESULT_SUMMARY.md`, update `research-wiki/experiments/`, create claim records, and draft `PAPER_DRAFT.md`.
