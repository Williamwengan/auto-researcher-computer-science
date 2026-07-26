#!/usr/bin/env python3
"""Build Auto-claude/ARIS-style execution workspaces from V10 final plans.

This is the correct experiment-layer bridge for the competition demo:

    Focused Workflow final plan
      -> ARIS/Auto-claude project workspace
      -> human-authorized Claude/Codex experiment conversation
      -> baseline reproduction / experiment / result-to-claim / paper draft

The script is intentionally safe: it only writes local files. It does not call
Claude, Codex, APIs, shell experiment commands, or GPU jobs.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
AUTO_CLAUDE_ROOT = Path("/data1/huangyuling/-A_HYL/AI4S/Auto-claude-code-research-in-sleep-main")
SOURCE = ROOT / "competition_submission" / "V10_FINAL_RESEARCH_PLAN_PACKAGE.json"
OUT_DIR = ROOT / "outputs" / "auto_claude_execution_bridge_v1"
REPORT = ROOT / "competition_submission" / "V26_AUTO_CLAUDE_EXECUTION_BRIDGE_CN.md"


PHASES = [
    "load_focused_final_plan",
    "prepare_dataset_and_environment",
    "implement_or_reuse_baseline",
    "implement_proposed_module",
    "run_sanity_experiment",
    "run_main_experiments",
    "run_ablations_and_negative_controls",
    "analyze_results",
    "result_to_claim",
    "write_paper_draft",
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def relpath(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def slugify(plan: dict[str, Any], fallback: str) -> str:
    identity = " ".join(str(plan.get(k, "")) for k in ["plan_id", "task_name", "task_spec"]).lower()
    if "iad" in identity or "异常" in identity:
        return "iad_agent"
    if "physical" in identity or "物理" in identity or "material" in identity:
        return "physical_property"
    if "indoor" in identity or "室内" in identity or "3d" in identity:
        return "indoor3d_scene"
    return re.sub(r"[^a-zA-Z0-9]+", "_", str(plan.get("task_name", fallback))).strip("_").lower() or fallback


def bullets(items: Any) -> str:
    if not items:
        return "- 未提供"
    if isinstance(items, str):
        return f"- {items}"
    if isinstance(items, dict):
        return "\n".join(f"- **{k}**: {v}" for k, v in items.items())
    return "\n".join(f"- {x}" for x in items)


def numbered(items: Any) -> str:
    if not items:
        return "1. 未提供"
    if isinstance(items, str):
        items = [items]
    return "\n".join(f"{i}. {x}" for i, x in enumerate(items, start=1))


def build_research_brief(plan: dict[str, Any]) -> str:
    return f"""# RESEARCH_BRIEF

## Problem Statement

{plan.get("research_problem", "")}

## Selected Idea

{plan.get("final_idea", "")}

## Core Hypothesis

{plan.get("core_hypothesis", "")}

## Baseline Gaps

{bullets(plan.get("baseline_weakness"))}

## Evidence Status

{bullets(plan.get("paper_evidence"))}

- Evidence verification: {plan.get("evidence_verification_status", "")}
- Judge summary: {plan.get("judge_summary", "")}

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
"""


def build_final_proposal(plan: dict[str, Any]) -> str:
    return f"""# FINAL_PROPOSAL

## Title / Idea

{plan.get("final_idea", "")}

## Motivation

{plan.get("core_hypothesis", "")}

## Proposed Approach

{bullets(plan.get("method_overview"))}

## Minimal New Module

{plan.get("minimal_new_module", "")}

## Datasets

{bullets(plan.get("datasets"))}

## Baselines

{bullets(plan.get("baselines"))}

## Metrics

{bullets(plan.get("metrics"))}

## Success Thresholds

{bullets(plan.get("success_thresholds"))}

## Failure Criteria

{bullets(plan.get("failure_criteria"))}

## Risks and Mitigation

{bullets(plan.get("risk_and_mitigation"))}
"""


def build_experiment_plan(plan: dict[str, Any]) -> str:
    return f"""# EXPERIMENT_PLAN

## Source

- Source package: `competition_submission/V10_FINAL_RESEARCH_PLAN_PACKAGE.json`
- Source plan id: `{plan.get("plan_id", "")}`
- Task: {plan.get("task_name", "")}

## Milestone 0 — Data and environment

1. Confirm dataset path or ask user to upload/download required data.
2. Build manifest files listed in implementation artifacts.
3. Verify train/test split and ground-truth labels.

Expected datasets:

{bullets(plan.get("datasets"))}

## Milestone 1 — Baseline reproduction

Reproduce or scaffold the following baselines:

{bullets(plan.get("baselines"))}

Output metrics as JSON/CSV. Do not use model predictions as ground truth.

## Milestone 2 — Proposed method

Implement:

{plan.get("minimal_new_module", "")}

Method steps:

{numbered(plan.get("method_overview"))}

## Milestone 3 — Main evaluation

Primary metrics:

{bullets(plan.get("metrics"))}

Success thresholds:

{bullets(plan.get("success_thresholds"))}

## Milestone 4 — Ablation and negative controls

Ablations:

{bullets(plan.get("ablations"))}

Negative controls:

{bullets(plan.get("negative_controls"))}

## Milestone 5 — Result-to-claim and paper draft

After experiments finish:

1. Parse result JSON/CSV.
2. Decide which claims are supported, partially supported, or unsupported.
3. Write `RESULT_SUMMARY.md`.
4. Write `PAPER_DRAFT.md` with only evidence-backed claims.
"""


def build_tracker(plan: dict[str, Any]) -> str:
    rows = [
        ("M0", "data/environment", "pending", "dataset path/user upload required if missing"),
        ("M1", "baseline reproduction", "pending", ", ".join(map(str, plan.get("baselines", [])[:3]))),
        ("M2", "proposed module implementation", "pending", str(plan.get("minimal_new_module", ""))),
        ("M3", "main evaluation", "pending", ", ".join(map(str, plan.get("metrics", [])[:4]))),
        ("M4", "ablation and negative controls", "pending", "validate mechanism, not just longer idea"),
        ("M5", "result-to-claim and paper draft", "pending", "only write claims supported by executed results"),
    ]
    lines = [
        "# EXPERIMENT_TRACKER",
        "",
        "| id | milestone | status | notes |",
        "| --- | --- | --- | --- |",
    ]
    lines.extend(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows)
    return "\n".join(lines) + "\n"


def build_claude_md(plan: dict[str, Any]) -> str:
    return f"""<!-- ARIS:BEGIN -->
## ARIS Skill Scope

This workspace is generated for Auto-claude/ARIS-style experiment execution.
Use project-local ARIS skills if installed. The intended execution skill is:

- `/experiment-bridge refine-logs/EXPERIMENT_PLAN.md`
- then `/run-experiment` or `/experiment-queue` after human authorization.

<!-- ARIS:END -->

# Project Instructions

## Goal

Run experiments for the focused AI4S research idea:

{plan.get("final_idea", "")}

## Safety / Authorization

- Ask the user before running shell commands that download data, install packages, call APIs, or launch GPU jobs.
- If a dataset is missing, ask for a path or upload.
- Keep all outputs under this workspace unless the user authorizes otherwise.
- Save metrics as JSON/CSV and logs as plain text.

## Environment

- gpu: local
- code_sync: local
- wandb: false

## Required Reading Order

1. `RESEARCH_BRIEF.md`
2. `refine-logs/FINAL_PROPOSAL.md`
3. `refine-logs/EXPERIMENT_PLAN.md`
4. `refine-logs/EXPERIMENT_TRACKER.md`

## Non-claims

Do not claim SOTA or full benchmark completion unless the corresponding experiments are actually executed.
"""


def build_authorized_prompt(workspace: Path, plan: dict[str, Any]) -> str:
    return f"""# Paste this into Claude Code / Codex after user authorization

You are now in an Auto-claude/ARIS-style experiment workspace.

Workspace:

```bash
cd {workspace}
```

Task:

```text
{plan.get("task_name", "")}
```

Selected focused idea:

```text
{plan.get("final_idea", "")}
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
"""


def build_run_state(run_id: str) -> dict[str, Any]:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "run_id": run_id,
        "created": now,
        "updated": now,
        "phases": [
            {
                "phase": ph,
                "status": "pending",
                "artifact": None,
                "verdict_id": None,
                "reviewer": None,
                "updated": now,
            }
            for ph in PHASES
        ],
    }


def init_research_wiki(root: Path, plan: dict[str, Any]) -> None:
    wiki = root / "research-wiki"
    for sub in ["papers", "ideas", "experiments", "claims", "graph"]:
        (wiki / sub).mkdir(parents=True, exist_ok=True)
    (wiki / "index.md").write_text(
        f"# Research Wiki Index\n\nTask: {plan.get('task_name', '')}\n\nIdea: {plan.get('final_idea', '')}\n",
        encoding="utf-8",
    )
    (wiki / "gap_map.md").write_text(
        "# Gap Map\n\n" + bullets(plan.get("baseline_weakness")) + "\n",
        encoding="utf-8",
    )
    (wiki / "query_pack.md").write_text(
        "# Query Pack\n\n"
        + f"Problem: {plan.get('research_problem', '')}\n\n"
        + f"Idea: {plan.get('final_idea', '')}\n\n"
        + "Evidence:\n"
        + bullets(plan.get("paper_evidence"))
        + "\n",
        encoding="utf-8",
    )
    (wiki / "log.md").write_text(
        f"# Research Wiki Log\n\n- {datetime.now().isoformat(timespec='seconds')} bridge initialized.\n",
        encoding="utf-8",
    )
    (wiki / "graph" / "edges.jsonl").write_text("", encoding="utf-8")
    idea_slug = slugify(plan, "idea")
    (wiki / "ideas" / f"{idea_slug}.md").write_text(build_final_proposal(plan), encoding="utf-8")


def materialize(plan: dict[str, Any], idx: int, out_dir: Path) -> dict[str, Any]:
    slug = slugify(plan, f"task_{idx:02d}")
    workspace = out_dir / slug
    (workspace / "refine-logs").mkdir(parents=True, exist_ok=True)
    (workspace / "idea-stage").mkdir(parents=True, exist_ok=True)
    (workspace / "runs").mkdir(parents=True, exist_ok=True)
    (workspace / ".aris" / "runs").mkdir(parents=True, exist_ok=True)

    (workspace / "RESEARCH_BRIEF.md").write_text(build_research_brief(plan), encoding="utf-8")
    (workspace / "CLAUDE.md").write_text(build_claude_md(plan), encoding="utf-8")
    (workspace / "AGENTS.md").write_text(build_claude_md(plan), encoding="utf-8")
    (workspace / "refine-logs" / "FINAL_PROPOSAL.md").write_text(build_final_proposal(plan), encoding="utf-8")
    (workspace / "refine-logs" / "EXPERIMENT_PLAN.md").write_text(build_experiment_plan(plan), encoding="utf-8")
    (workspace / "refine-logs" / "EXPERIMENT_TRACKER.md").write_text(build_tracker(plan), encoding="utf-8")
    (workspace / "idea-stage" / "IDEA_CANDIDATES.md").write_text(build_final_proposal(plan), encoding="utf-8")
    (workspace / "AUTHORIZED_CLAUDE_PROMPT.md").write_text(build_authorized_prompt(workspace, plan), encoding="utf-8")
    write_json(workspace / "focused_final_plan.json", plan)
    write_json(workspace / ".aris" / "runs" / "focused_to_experiment.json", build_run_state("focused_to_experiment"))
    init_research_wiki(workspace, plan)

    return {
        "task_name": plan.get("task_name"),
        "plan_id": plan.get("plan_id"),
        "workspace": relpath(workspace),
        "authorization_prompt": relpath(workspace / "AUTHORIZED_CLAUDE_PROMPT.md"),
        "entry_skill": "/experiment-bridge refine-logs/EXPERIMENT_PLAN.md",
        "safe_status": "workspace_prepared_no_experiment_run",
    }


def build_report(records: list[dict[str, Any]]) -> str:
    lines = [
        "# V26 Auto-claude / ARIS 实验执行 Bridge",
        "",
        f"生成时间：{datetime.now().isoformat(timespec='seconds')}",
        "",
        "## 结论",
        "",
        "V25 的 ResearchArena resume bridge 只能说明 schema 能接回 ResearchArena；但比赛 demo 真正需要的是 Auto-claude/ARIS 风格的实验执行舱：用户授权后，由 Claude/Codex 对话式实现 baseline、运行实验、记录结果并生成论文草稿。",
        "",
        "本 V26 已把 V10 final research plans 转换成 Auto-claude/ARIS-style workspaces。",
        "",
        "## 生成的实验执行工作区",
        "",
        "| task | workspace | authorization prompt | entry |",
        "| --- | --- | --- | --- |",
    ]
    for r in records:
        lines.append(
            f"| {r['task_name']} | `{r['workspace']}` | `{r['authorization_prompt']}` | `{r['entry_skill']}` |"
        )
    lines.extend(
        [
            "",
            "## 每个 workspace 包含什么",
            "",
            "- `RESEARCH_BRIEF.md`：任务、问题、约束和最终 idea。",
            "- `CLAUDE.md` / `AGENTS.md`：Auto-claude/ARIS 执行规则与人工授权边界。",
            "- `refine-logs/FINAL_PROPOSAL.md`：方法提案。",
            "- `refine-logs/EXPERIMENT_PLAN.md`：可交给 `/experiment-bridge` 的实验计划。",
            "- `refine-logs/EXPERIMENT_TRACKER.md`：实验进度表。",
            "- `research-wiki/`：papers/ideas/experiments/claims/graph 结构。",
            "- `.aris/runs/focused_to_experiment.json`：可恢复的执行状态。",
            "- `AUTHORIZED_CLAUDE_PROMPT.md`：网页端授权后可送入 Claude/Codex 对话舱的提示。",
            "",
            "## 安全边界",
            "",
            "本脚本只生成文件，不调用 API、不下载数据、不运行 GPU、不执行 shell 实验命令。真正执行需要用户在网页或 Claude/Codex 对话中确认授权。",
            "",
            "## 推荐 demo 讲法",
            "",
            "Phase 1 展示：输入科研任务后，系统完成论文证据、baseline 空白、idea 生成、评分、盲评、repair 和最终方案选择。",
            "",
            "Phase 2 展示：点击授权进入 Auto-claude/ARIS 实验舱，系统读取 `EXPERIMENT_PLAN.md`，询问数据集/API/GPU 授权，然后开始 baseline reproduction、proposed module、ablation、result-to-claim 和 paper draft。",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()

    source = args.source if args.source.is_absolute() else ROOT / args.source
    out_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    report = args.report if args.report.is_absolute() else ROOT / args.report

    if args.clean and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    data = read_json(source)
    plans = data.get("plans", [])
    records = [materialize(plan, i, out_dir) for i, plan in enumerate(plans, start=1)]

    manifest = {
        "version": "v26_auto_claude_execution_bridge",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "auto_claude_reference_root": str(AUTO_CLAUDE_ROOT),
        "source": relpath(source),
        "output_dir": relpath(out_dir),
        "records": records,
        "note": "No API calls, downloads, shell experiment commands, or GPU jobs were executed.",
    }
    write_json(out_dir / "auto_claude_bridge_manifest.json", manifest)
    (out_dir / "AUTO_CLAUDE_BRIDGE_SUMMARY_CN.md").write_text(build_report(records), encoding="utf-8")
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(build_report(records), encoding="utf-8")

    print(f"Wrote {out_dir / 'auto_claude_bridge_manifest.json'}")
    print(f"Wrote {out_dir / 'AUTO_CLAUDE_BRIDGE_SUMMARY_CN.md'}")
    print(f"Wrote {report}")
    for r in records:
        print(f"{r['task_name']}: {r['workspace']}")
    print("No experiments were run. Use AUTHORIZED_CLAUDE_PROMPT.md after human authorization.")


if __name__ == "__main__":
    main()
