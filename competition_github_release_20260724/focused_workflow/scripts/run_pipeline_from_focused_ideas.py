#!/usr/bin/env python3
"""Bridge focused-workflow final ideas into ResearchArena resume workspaces.

This script does not call any LLM API and does not run experiments by default.
It materializes one ResearchArena-compatible workspace per selected final plan:

    idea.json
    plan.json
    proposal.md

ResearchArena's ``pipeline.resume(workspace)`` can then skip ideation and enter
self-review / experiments once the user explicitly authorizes execution.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "competition_submission" / "V10_FINAL_RESEARCH_PLAN_PACKAGE.json"
DEFAULT_OUT = ROOT / "outputs" / "pipeline_bridge_from_focused_ideas_v1"
DEFAULT_REPORT = ROOT / "competition_submission" / "V25_PIPELINE_BRIDGE_FROM_FOCUSED_IDEAS_CN.md"


TASK_ALIASES = {
    "all": "all",
    "iad": "iad",
    "iad_agent": "iad",
    "industrial": "iad",
    "physical": "physical",
    "material": "physical",
    "physical_property": "physical",
    "indoor3d": "indoor3d",
    "indoor": "indoor3d",
    "scene3d": "indoor3d",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def relpath(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def slugify(text: str, fallback: str) -> str:
    lowered = text.lower()
    if "iad" in lowered or "异常" in text or "industrial" in lowered:
        return "iad_agent"
    if "物理" in text or "physical" in lowered or "material" in lowered:
        return "physical_property"
    if "室内" in text or "3d" in lowered or "scene" in lowered:
        return "indoor3d_scene"

    ascii_slug = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    return ascii_slug or fallback


def task_key(plan: dict[str, Any]) -> str:
    identity = " ".join(
        str(plan.get(k, ""))
        for k in ["plan_id", "task_name", "task_spec"]
    ).lower()
    if "iad" in identity or "异常" in identity:
        return "iad"
    if "physical" in identity or "material" in identity or "物理" in identity:
        return "physical"
    if "indoor" in identity or "3d" in identity or "室内" in identity:
        return "indoor3d"

    text = " ".join(
        str(plan.get(k, ""))
        for k in ["research_problem", "final_idea", "minimal_new_module"]
    ).lower()
    if "iad" in text or "异常" in text:
        return "iad"
    if "physical" in text or "material" in text or "物理" in text:
        return "physical"
    if "indoor" in text or "3d" in text or "室内" in text:
        return "indoor3d"
    return "other"


def as_bullets(items: Any) -> str:
    if not items:
        return "- 未提供"
    if isinstance(items, str):
        return f"- {items}"
    if isinstance(items, dict):
        return "\n".join(f"- **{k}**: {v}" for k, v in items.items())
    return "\n".join(f"- {x}" for x in items)


def join_list(items: Any) -> str:
    if not items:
        return ""
    if isinstance(items, str):
        return items
    if isinstance(items, dict):
        return "; ".join(f"{k}: {v}" for k, v in items.items())
    return "\n".join(f"- {x}" for x in items)


def build_idea_json(plan: dict[str, Any]) -> dict[str, Any]:
    title = plan.get("final_idea") or plan.get("title") or plan.get("plan_id", "Untitled idea")

    description = "\n\n".join(
        part
        for part in [
            f"Task: {plan.get('task_name', '')}",
            f"Research problem: {plan.get('research_problem', '')}",
            f"Final idea: {plan.get('final_idea', '')}",
            f"Core hypothesis: {plan.get('core_hypothesis', '')}",
        ]
        if part.strip()
    )

    proposed_parts = [
        f"Minimal new module: {plan.get('minimal_new_module', '')}",
        "Method overview:",
        join_list(plan.get("method_overview")),
        "Implementation artifacts:",
        join_list(plan.get("implementation_artifacts")),
    ]
    proposed_approach = "\n".join(x for x in proposed_parts if x.strip())

    related_work_parts = [
        "Baseline weaknesses:",
        join_list(plan.get("baseline_weakness")),
        "Baselines:",
        join_list(plan.get("baselines")),
        "Paper evidence:",
        join_list(plan.get("paper_evidence")),
        f"Evidence verification: {plan.get('evidence_verification_status', '')}",
    ]
    related_work = "\n".join(x for x in related_work_parts if x.strip())

    return {
        "title": title,
        "description": description,
        "motivation": plan.get("core_hypothesis") or plan.get("research_problem", ""),
        "proposed_approach": proposed_approach,
        "related_work": related_work,
        "source": "focused_workflow_v10_final_research_plan_package",
        "source_plan_id": plan.get("plan_id"),
        "task_name": plan.get("task_name"),
        "task_spec": plan.get("task_spec"),
        "baseline_weakness": plan.get("baseline_weakness", []),
        "paper_evidence": plan.get("paper_evidence", []),
        "datasets": plan.get("datasets", []),
        "baselines": plan.get("baselines", []),
        "metrics": plan.get("metrics", []),
        "ablations": plan.get("ablations", []),
        "negative_controls": plan.get("negative_controls", []),
        "success_thresholds": plan.get("success_thresholds", []),
        "failure_criteria": plan.get("failure_criteria", []),
        "risk_and_mitigation": plan.get("risk_and_mitigation", []),
        "judge_summary": plan.get("judge_summary", ""),
        "next_execution_step": plan.get("next_execution_step", ""),
    }


def build_plan_json(plan: dict[str, Any]) -> list[dict[str, Any]]:
    steps = []
    raw_steps = plan.get("experiment_plan", [])
    if isinstance(raw_steps, str):
        raw_steps = [raw_steps]
    for idx, step in enumerate(raw_steps, start=1):
        steps.append(
            {
                "step_id": f"E{idx:02d}",
                "name": f"Experiment step {idx}",
                "description": str(step),
                "phase": infer_phase(str(step)),
                "expected_artifact": infer_artifact(str(step), plan),
                "metrics": plan.get("metrics", []),
                "success_criteria": plan.get("success_thresholds", []),
            }
        )

    if not steps:
        steps.append(
            {
                "step_id": "E01",
                "name": "Minimal execution plan",
                "description": plan.get("next_execution_step", "Implement the proposed MVP and evaluate it."),
                "phase": "execution",
                "expected_artifact": "results.json",
                "metrics": plan.get("metrics", []),
                "success_criteria": plan.get("success_thresholds", []),
            }
        )
    return steps


def infer_phase(text: str) -> str:
    lowered = text.lower()
    if any(k in lowered for k in ["manifest", "data", "dataset", "构建", "数据"]):
        return "data_preparation"
    if any(k in lowered for k in ["baseline", "基线"]):
        return "baseline_reproduction"
    if any(k in lowered for k in ["ablation", "消融"]):
        return "ablation"
    if any(k in lowered for k in ["metric", "evaluate", "评估", "报告"]):
        return "evaluation"
    return "main_experiment"


def infer_artifact(text: str, plan: dict[str, Any]) -> str:
    artifacts = plan.get("implementation_artifacts", [])
    if isinstance(artifacts, list) and artifacts:
        for artifact in artifacts:
            if isinstance(artifact, str) and artifact.split("/")[-1] in text:
                return artifact
        return str(artifacts[min(len(artifacts) - 1, 0)])
    return "results.json"


def build_proposal_md(plan: dict[str, Any], idea: dict[str, Any], plan_steps: list[dict[str, Any]]) -> str:
    lines = [
        f"# {idea.get('title', 'Untitled idea')}",
        "",
        f"生成时间：{datetime.now().isoformat(timespec='seconds')}",
        "",
        "来源：Focused Workflow V10 final research plan package，经 bridge 转换为 ResearchArena resume workspace。",
        "",
        "## 1. 研究任务",
        "",
        plan.get("research_problem", "未提供"),
        "",
        "## 2. Baseline 缺陷",
        "",
        as_bullets(plan.get("baseline_weakness")),
        "",
        "## 3. 论文证据与相关工作",
        "",
        as_bullets(plan.get("paper_evidence")),
        "",
        "### Baselines",
        "",
        as_bullets(plan.get("baselines")),
        "",
        "## 4. 核心 Idea",
        "",
        plan.get("final_idea", ""),
        "",
        "## 5. 核心假设",
        "",
        plan.get("core_hypothesis", ""),
        "",
        "## 6. 方法概述",
        "",
        as_bullets(plan.get("method_overview")),
        "",
        "### Minimal New Module",
        "",
        plan.get("minimal_new_module", ""),
        "",
        "## 7. 实验计划",
        "",
    ]
    for step in plan_steps:
        lines.extend(
            [
                f"### {step['step_id']} · {step['name']}",
                "",
                f"- Phase: `{step['phase']}`",
                f"- Description: {step['description']}",
                f"- Expected artifact: `{step['expected_artifact']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## 8. 数据集与指标",
            "",
            "### Datasets",
            "",
            as_bullets(plan.get("datasets")),
            "",
            "### Metrics",
            "",
            as_bullets(plan.get("metrics")),
            "",
            "## 9. 消融与负控制",
            "",
            "### Ablations",
            "",
            as_bullets(plan.get("ablations")),
            "",
            "### Negative Controls",
            "",
            as_bullets(plan.get("negative_controls")),
            "",
            "## 10. 成功阈值、失败条件与风险",
            "",
            "### Success Thresholds",
            "",
            as_bullets(plan.get("success_thresholds")),
            "",
            "### Failure Criteria",
            "",
            as_bullets(plan.get("failure_criteria")),
            "",
            "### Risk and Mitigation",
            "",
            as_bullets(plan.get("risk_and_mitigation")),
            "",
            "## 11. Judge 与证据校验状态",
            "",
            f"- Judge summary: {plan.get('judge_summary', '')}",
            f"- Evidence verification: {plan.get('evidence_verification_status', '')}",
            "",
            "## 12. 下一步执行入口",
            "",
            plan.get("next_execution_step", ""),
            "",
            "## 13. Honest Boundary",
            "",
            plan.get("current_boundary", "该 workspace 只表示已完成 idea/plan/proposal 初始化；实验阶段需要人工授权后执行。"),
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def load_plans(source: Path) -> list[dict[str, Any]]:
    data = read_json(source)
    if isinstance(data, dict) and isinstance(data.get("plans"), list):
        return data["plans"]
    if isinstance(data, list):
        return data
    raise ValueError(f"Unsupported source schema: {source}")


def filter_plans(plans: list[dict[str, Any]], task: str) -> list[dict[str, Any]]:
    normalized = TASK_ALIASES.get(task.lower(), task.lower())
    if normalized == "all":
        return plans
    return [p for p in plans if task_key(p) == normalized]


def materialize_workspace(base_dir: Path, plan: dict[str, Any], ordinal: int) -> dict[str, Any]:
    slug = slugify(str(plan.get("task_name") or plan.get("plan_id")), f"task_{ordinal:02d}")
    workspace = base_dir / slug / f"idea_{ordinal:02d}"
    workspace.mkdir(parents=True, exist_ok=True)

    idea = build_idea_json(plan)
    plan_steps = build_plan_json(plan)
    proposal = build_proposal_md(plan, idea, plan_steps)

    write_json(workspace / "idea.json", idea)
    write_json(workspace / "plan.json", plan_steps)
    (workspace / "proposal.md").write_text(proposal, encoding="utf-8")
    (workspace / "README_BRIDGE_CN.md").write_text(
        build_workspace_readme(workspace, plan, ordinal), encoding="utf-8"
    )

    return {
        "ordinal": ordinal,
        "plan_id": plan.get("plan_id"),
        "task_name": plan.get("task_name"),
        "task_key": task_key(plan),
        "workspace": relpath(workspace),
        "required_files": ["idea.json", "plan.json", "proposal.md"],
        "resume_command": f"python -m researcharena.cli run --config configs/default.yaml --resume {relpath(workspace)}",
        "safe_status": "materialized_only_no_api_called",
    }


def build_workspace_readme(workspace: Path, plan: dict[str, Any], ordinal: int) -> str:
    rel = relpath(workspace)
    return f"""# Bridge Workspace {ordinal:02d}: {plan.get('task_name', '')}

这个目录由 `focused_workflow/scripts/run_pipeline_from_focused_ideas.py` 自动生成。

## 已写入文件

- `idea.json`：ResearchArena ideation summary schema
- `plan.json`：ResearchArena experiment plan schema
- `proposal.md`：完整 proposal 文档

## 当前状态

已完成 bridge 初始化；尚未调用 API，尚未跑实验。

## 人工授权后可执行

```bash
python -m researcharena.cli run --config configs/default.yaml --resume {rel}
```

ResearchArena 会检测到 `idea.json + plan.json + proposal.md` 已存在，因此跳过 ideation，进入 self-review / experiments / paper / review 后续阶段。
"""


def build_summary_report(records: list[dict[str, Any]], source: Path, out_dir: Path) -> str:
    lines = [
        "# V25 Focused Ideas → ResearchArena Pipeline Bridge",
        "",
        f"生成时间：{datetime.now().isoformat(timespec='seconds')}",
        "",
        "## 一句话结论",
        "",
        "本步骤把 Focused Workflow 已经筛选出的最终研究方案，转换成 ResearchArena 可以 `--resume` 的实验工作区格式，使系统从“生成好 idea 和实验计划”进入“人工授权后自动跑实验、写论文、评审”的阶段。",
        "",
        "## 为什么现在发现了 bridge 问题",
        "",
        "之前两段流程各自成立，但文件 schema 不一致：",
        "",
        "- Focused Workflow 输出的是比赛友好的 `final research plan`，字段更细：baseline weakness、paper evidence、minimal module、metrics、negative controls 等。",
        "- ResearchArena 执行层期待的是每个 idea workspace 中的 `idea.json + plan.json + proposal.md`。",
        "- 因此唯一阻断点不是算法逻辑，而是字段映射和 workspace 初始化。",
        "",
        "这个脚本解决的就是：把 V10 final plan 映射成 ResearchArena resume workspace。",
        "",
        "## 生成的工作区",
        "",
        "| # | task | source plan | workspace | resume command |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for r in records:
        lines.append(
            f"| {r['ordinal']} | {r['task_name']} | `{r['plan_id']}` | `{r['workspace']}` | `{r['resume_command']}` |"
        )
    lines.extend(
        [
            "",
            "## 当前安全边界",
            "",
            "- 本脚本只写本地文件，不调用 API。",
            "- 本脚本不自动运行 Claude/Codex 实验阶段。",
            "- 真正执行 ResearchArena pipeline 时，需要用户显式授权，并配置相应模型/API。",
            "",
            "## 推荐下一步",
            "",
            "先在网页 demo 里展示 bridge 已经生成的 workspace；若现场需要演示实验执行，则选择一个轻量任务，例如 IAD scaffold，点击授权后再调用后续执行命令。",
            "",
            "## 输入与输出",
            "",
            f"- Source: `{relpath(source)}`",
            f"- Output dir: `{relpath(out_dir)}`",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--final-plan-package", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--task", default="all", help="all | iad | physical | indoor3d")
    parser.add_argument("--top-n", type=int, default=3)
    parser.add_argument("--clean", action="store_true", help="Remove output dir before materializing.")
    args = parser.parse_args()

    source = args.final_plan_package if args.final_plan_package.is_absolute() else ROOT / args.final_plan_package
    out_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    report = args.report if args.report.is_absolute() else ROOT / args.report

    if not source.exists():
        raise FileNotFoundError(source)

    if args.clean and out_dir.exists():
        shutil.rmtree(out_dir)

    plans = filter_plans(load_plans(source), args.task)[: args.top_n]
    if not plans:
        raise RuntimeError(f"No plans selected from {source} for task={args.task}")

    out_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for idx, plan in enumerate(plans, start=1):
        records.append(materialize_workspace(out_dir, plan, idx))

    manifest = {
        "version": "v25_pipeline_bridge_from_focused_ideas",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": relpath(source),
        "output_dir": relpath(out_dir),
        "records": records,
        "note": "No API calls or experiment execution were performed by this bridge script.",
    }
    write_json(out_dir / "bridge_manifest.json", manifest)
    (out_dir / "BRIDGE_SUMMARY_CN.md").write_text(
        build_summary_report(records, source, out_dir), encoding="utf-8"
    )

    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(build_summary_report(records, source, out_dir), encoding="utf-8")

    print(f"Wrote {out_dir / 'bridge_manifest.json'}")
    print(f"Wrote {out_dir / 'BRIDGE_SUMMARY_CN.md'}")
    print(f"Wrote {report}")
    for r in records:
        print(f"{r['task_name']}: {r['workspace']}")
    print("No API calls were made. Use resume_command only after user authorization.")


if __name__ == "__main__":
    main()
