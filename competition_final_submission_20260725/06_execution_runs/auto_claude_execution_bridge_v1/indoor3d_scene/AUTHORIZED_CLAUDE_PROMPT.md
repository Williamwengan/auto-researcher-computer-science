# Paste this into Claude Code / Codex after user authorization

You are now in an Auto-claude/ARIS-style experiment workspace.

Workspace:

```bash
cd /data1/huangyuling/-A_HYL/AI4S/ResearchArena-main/outputs/auto_claude_execution_bridge_v1/indoor3d_scene
```

Task:

```text
室内单图 3D 场景生成
```

Selected focused idea:

```text
Evidence-grounded single-image 3D scene hypothesis planner：用 layout/depth/reconstruction baselines 生成候选场景，再用 scene-graph relation、support/collision checker 和 uncertainty annotation 修复几何与物理不一致。
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
