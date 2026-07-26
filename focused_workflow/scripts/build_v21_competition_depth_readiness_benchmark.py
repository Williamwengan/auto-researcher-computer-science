#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SUBMISSION = ROOT / "competition_submission"
FINAL_DIR = ROOT / "competition_final_submission_20260725"


REQUIRED_PLAN_FIELDS = [
    "research_problem",
    "baseline_weakness",
    "paper_evidence",
    "final_idea",
    "core_hypothesis",
    "method_overview",
    "minimal_new_module",
    "experiment_plan",
    "datasets",
    "baselines",
    "metrics",
    "ablations",
    "negative_controls",
    "success_thresholds",
    "failure_criteria",
    "implementation_artifacts",
    "risk_and_mitigation",
    "evidence_verification_status",
    "judge_summary",
    "next_execution_step",
]

DEPTH_SIGNALS = {
    "mechanism_specificity": ["minimal_new_module", "core_hypothesis", "method_overview"],
    "experimental_rigor": ["experiment_plan", "metrics", "ablations", "negative_controls", "failure_criteria"],
    "execution_readiness": ["datasets", "baselines", "implementation_artifacts", "next_execution_step"],
    "evidence_grounding": ["paper_evidence", "evidence_verification_status", "baseline_weakness"],
    "risk_awareness": ["risk_and_mitigation", "failure_criteria", "success_thresholds"],
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def is_filled(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return len(value) > 0
    return True


def count_items(value) -> int:
    if isinstance(value, str):
        return 1 if value.strip() else 0
    if isinstance(value, (list, tuple, dict)):
        return len(value)
    return 1 if value else 0


def score_plan(plan: dict) -> dict:
    field_completion = {
        field: is_filled(plan.get(field))
        for field in REQUIRED_PLAN_FIELDS
    }
    completion_rate = sum(field_completion.values()) / len(field_completion)
    signal_scores = {}
    signal_details = {}
    for signal, fields in DEPTH_SIGNALS.items():
        filled = [field for field in fields if is_filled(plan.get(field))]
        richness = sum(min(count_items(plan.get(field)), 5) for field in fields)
        max_richness = 5 * len(fields)
        signal_scores[signal] = round(0.55 * (len(filled) / len(fields)) + 0.45 * (richness / max_richness), 3)
        signal_details[signal] = {
            "filled_fields": filled,
            "richness": richness,
            "max_richness": max_richness,
        }
    overall = round(0.4 * completion_rate + 0.6 * (sum(signal_scores.values()) / len(signal_scores)), 3)
    warnings = []
    if signal_scores["mechanism_specificity"] < 0.75:
        warnings.append("mechanism may still be shallow")
    if signal_scores["execution_readiness"] < 0.75:
        warnings.append("execution path may be under-specified")
    if signal_scores["evidence_grounding"] < 0.75:
        warnings.append("paper evidence grounding may be weak")
    if "当前完成最终研究方案生成" in str(plan.get("current_boundary", "")):
        warnings.append("not yet executed as a full benchmark")
    return {
        "plan_id": plan.get("plan_id"),
        "task_name": plan.get("task_name"),
        "field_completion_rate": round(completion_rate, 3),
        "signal_scores": signal_scores,
        "signal_details": signal_details,
        "overall_depth_readiness_score": overall,
        "warnings": warnings,
    }


def build_report() -> dict:
    package = read_json(SUBMISSION / "V10_FINAL_RESEARCH_PLAN_PACKAGE.json")
    scored = [score_plan(plan) for plan in package.get("plans", [])]
    averages = {}
    for signal in DEPTH_SIGNALS:
        vals = [row["signal_scores"][signal] for row in scored]
        averages[signal] = round(sum(vals) / len(vals), 3) if vals else 0
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "purpose": "competition_depth_and_execution_readiness_benchmark",
        "note": "This is an automated internal diagnostic for demo improvement, not a replacement for real scientific experiments.",
        "plans_scored": len(scored),
        "average_signal_scores": averages,
        "average_overall_depth_readiness_score": round(
            sum(row["overall_depth_readiness_score"] for row in scored) / len(scored), 3
        ) if scored else 0,
        "results": scored,
        "recommended_demo_message": (
            "The agent does not stop at idea text. It checks whether each research plan has mechanisms, "
            "datasets, metrics, negative controls, evidence grounding, failure criteria, and execution artifacts."
        ),
    }


def write_markdown(report: dict, path: Path) -> None:
    lines = [
        "# V21 自动深度与执行就绪度检查",
        "",
        f"生成时间：{report['generated_at']}",
        "",
        "## 目的",
        "",
        "该实验用于比赛 demo 改进：检查最终研究方案是否具备技术深度、执行路径和证据约束。它不是替代真实科学实验的最终指标，而是智能体内部的自动质量门。",
        "",
        "## 总体结果",
        "",
        f"- 检查方案数：{report['plans_scored']}",
        f"- 平均 depth/readiness score：{report['average_overall_depth_readiness_score']}",
        "",
        "## 信号均值",
        "",
        "| signal | average score |",
        "| --- | ---: |",
    ]
    for key, value in report["average_signal_scores"].items():
        lines.append(f"| {key} | {value} |")
    lines.extend(["", "## 分任务结果", "", "| task | completion | depth/readiness | warnings |", "| --- | ---: | ---: | --- |"])
    for row in report["results"]:
        warnings = "<br>".join(row["warnings"]) if row["warnings"] else "none"
        lines.append(
            f"| {row['task_name']} | {row['field_completion_rate']} | "
            f"{row['overall_depth_readiness_score']} | {warnings} |"
        )
    lines.extend(
        [
            "",
            "## Demo 中怎么讲",
            "",
            report["recommended_demo_message"],
            "",
            "中文表达：",
            "",
            "```text",
            "我们的系统不止生成 idea 文本，还会自动检查每个研究方案是否包含机制、数据集、指标、负对照、证据绑定、失败标准和执行产物，从而减少表面化 idea。",
            "```",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    json_path = SUBMISSION / "V21_COMPETITION_DEPTH_READINESS_BENCHMARK.json"
    md_path = SUBMISSION / "V21_COMPETITION_DEPTH_READINESS_BENCHMARK_CN.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(report, md_path)
    appendix = FINAL_DIR / "05_evidence_appendix"
    appendix.mkdir(parents=True, exist_ok=True)
    (appendix / md_path.name).write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"Wrote {appendix / md_path.name}")
    print(f"Average score: {report['average_overall_depth_readiness_score']}")


if __name__ == "__main__":
    main()
