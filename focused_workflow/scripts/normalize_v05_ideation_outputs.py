#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")


def backup(path: Path) -> None:
    raw_path = path.with_suffix(path.suffix + ".raw")
    if not raw_path.exists() and path.exists():
        shutil.copy2(path, raw_path)


def as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def as_str(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return ", ".join(as_str(v) for v in value if as_str(v))
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def baseline_name(item) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return item.get("name") or item.get("baseline_name") or item.get("id") or as_str(item)
    return as_str(item)


def normalize_baseline_cards(run_dir: Path) -> None:
    source = run_dir / "evidence_baseline_cards.jsonl"
    target = run_dir / "baseline_cards.jsonl"
    if not source.exists():
        return
    backup(target)
    rows = read_jsonl(source)
    normalized = []
    for row in rows:
        papers = row.get("evidence_papers", []) or []
        paper_titles = [p.get("title", "") for p in papers if isinstance(p, dict)]
        normalized.append(
            {
                "name": row.get("baseline_name", ""),
                "type": row.get("baseline_type", ""),
                "main_task": row.get("claimed_task", ""),
                "input": "See task specification and evidence context.",
                "output": "Baseline output or reusable component for the target workflow.",
                "metrics": row.get("supported_metrics", []),
                "why_relevant": (
                    f"Evidence strength: {row.get('evidence_strength', '')}. "
                    f"Evidence papers: {', '.join(paper_titles[:3])}"
                ),
                "limitations": "; ".join(row.get("known_limitations", []) or []),
                "possible_reuse": "; ".join(row.get("reusable_components", []) or []),
                "evidence_papers": papers,
                "evidence_strength": row.get("evidence_strength", ""),
                "unsupported_claims": row.get("unsupported_claims", []),
            }
        )
    write_jsonl(target, normalized)


def normalize_idea(idea: dict) -> dict:
    direct = [baseline_name(x) for x in as_list(idea.get("direct_baselines"))]
    transfer = [baseline_name(x) for x in as_list(idea.get("transfer_baselines"))]

    normalized = dict(idea)
    normalized["task_type"] = as_str(idea.get("task_type"))
    normalized["direct_baselines"] = [x for x in direct if x]
    normalized["transfer_baselines"] = [x for x in transfer if x]
    normalized["borrowed_components"] = [as_str(x) for x in as_list(idea.get("borrowed_components")) if as_str(x)]
    normalized["datasets"] = [as_str(x) for x in as_list(idea.get("datasets")) if as_str(x)]
    normalized["metrics"] = [as_str(x) for x in as_list(idea.get("metrics")) if as_str(x)]
    normalized["ablations"] = [as_str(x) for x in as_list(idea.get("ablations")) if as_str(x)]
    normalized["risks"] = [as_str(x) for x in as_list(idea.get("risks")) if as_str(x)]
    normalized["failure_criteria"] = [as_str(x) for x in as_list(idea.get("failure_criteria")) if as_str(x)]
    normalized["implementation_plan"] = [as_str(x) for x in as_list(idea.get("implementation_plan")) if as_str(x)]
    normalized["expected_outputs"] = [as_str(x) for x in as_list(idea.get("expected_outputs")) if as_str(x)]

    if not normalized["expected_outputs"]:
        artifacts = idea.get("mvp_artifacts", {})
        if isinstance(artifacts, dict):
            normalized["expected_outputs"] = [
                as_str(x)
                for key in ["expected_tables", "expected_figures", "required_scripts"]
                for x in as_list(artifacts.get(key))
                if as_str(x)
            ]
        elif isinstance(artifacts, list):
            normalized["expected_outputs"] = [as_str(x) for x in artifacts if as_str(x)]
    if not normalized["expected_outputs"]:
        normalized["expected_outputs"] = [
            "standardized idea JSON",
            "experiment result table",
            "qualitative failure case report",
        ]

    minimal = idea.get("minimal_new_module")
    if not isinstance(minimal, dict):
        minimal = {}
    normalized["minimal_new_module"] = {
        "name": as_str(minimal.get("name") or idea.get("new_component") or idea.get("title")),
        "input": as_str(minimal.get("input") or "Task input and baseline evidence context."),
        "output": as_str(minimal.get("output") or "Evidence-grounded idea module output."),
        "algorithm_steps": [
            as_str(x)
            for x in as_list(minimal.get("algorithm_steps") or idea.get("implementation_plan"))
            if as_str(x)
        ],
        "training_or_inference_objective": as_str(
            minimal.get("training_or_inference_objective")
            or minimal.get("objective")
            or "Improve the target metrics while preserving evidence-grounded failure handling."
        ),
        "why_baseline_cannot_do_this": as_str(
            minimal.get("why_baseline_cannot_do_this")
            or "The cited baselines provide reusable components but do not implement the proposed evidence-grounded mechanism end to end."
        ),
    }
    if not normalized["minimal_new_module"]["algorithm_steps"]:
        normalized["minimal_new_module"]["algorithm_steps"] = ["Implement the proposed module and compare against direct baselines."]

    mvp = idea.get("mvp_artifacts")
    if isinstance(mvp, list):
        mvp = {
            "required_scripts": [],
            "required_data_files": [],
            "expected_tables": mvp,
            "expected_figures": [],
            "success_threshold": "",
        }
    if not isinstance(mvp, dict):
        mvp = {}
    normalized["mvp_artifacts"] = {
        "required_scripts": [as_str(x) for x in as_list(mvp.get("required_scripts")) if as_str(x)]
        or ["run_experiment.py"],
        "required_data_files": [as_str(x) for x in as_list(mvp.get("required_data_files")) if as_str(x)]
        or ["dataset_manifest.jsonl"],
        "expected_tables": [as_str(x) for x in as_list(mvp.get("expected_tables")) if as_str(x)]
        or ["main_results.csv"],
        "expected_figures": [as_str(x) for x in as_list(mvp.get("expected_figures")) if as_str(x)]
        or ["qualitative_examples.png"],
        "success_threshold": as_str(mvp.get("success_threshold") or "Improve at least one primary metric without violating failure criteria."),
    }

    normalized["new_component"] = as_str(idea.get("new_component"))
    normalized["why_it_may_work"] = as_str(idea.get("why_it_may_work"))
    normalized["evidence_paper_ids"] = [as_str(x) for x in as_list(idea.get("evidence_paper_ids")) if as_str(x)]
    normalized["baseline_weakness_evidence"] = as_list(idea.get("baseline_weakness_evidence"))
    normalized["unsupported_or_weak_claims"] = as_list(idea.get("unsupported_or_weak_claims"))
    return normalized


def normalize_ideas(run_dir: Path) -> list[dict]:
    path = run_dir / "focused_ideas.json"
    backup(path)
    data = load_json(path)
    ideas = data.get("ideas", []) if isinstance(data, dict) else data
    if not isinstance(ideas, list):
        ideas = []
    normalized = [normalize_idea(idea) for idea in ideas if isinstance(idea, dict)]
    write_json(path, normalized)
    return normalized


def normalize_plan_item(idea: dict, raw_plan: dict | None) -> dict:
    raw_plan = raw_plan or {}
    return {
        "idea_title": idea.get("title", raw_plan.get("idea_title", "")),
        "baseline_to_compare": [
            as_str(x)
            for x in as_list(
                raw_plan.get("baseline_to_compare")
                or raw_plan.get("primary_comparison")
                or raw_plan.get("direct_comparisons")
                or idea.get("direct_baselines")
            )
            if as_str(x)
        ],
        "data_preparation": [
            as_str(x)
            for x in as_list(raw_plan.get("data_preparation") or raw_plan.get("datasets") or idea.get("datasets"))
            if as_str(x)
        ],
        "implementation_steps": [
            as_str(x)
            for x in as_list(raw_plan.get("implementation_steps") or idea.get("implementation_plan"))
            if as_str(x)
        ],
        "evaluation_metrics": [
            as_str(x)
            for x in as_list(raw_plan.get("evaluation_metrics") or raw_plan.get("primary_metrics") or idea.get("metrics"))
            if as_str(x)
        ],
        "ablation_studies": [
            as_str(x)
            for x in as_list(raw_plan.get("ablation_studies") or raw_plan.get("ablations") or idea.get("ablations"))
            if as_str(x)
        ],
        "success_criteria": [
            as_str(x)
            for x in as_list(raw_plan.get("success_criteria") or idea.get("mvp_artifacts", {}).get("success_threshold"))
            if as_str(x)
        ],
        "failure_cases": [
            as_str(x)
            for x in as_list(raw_plan.get("failure_cases") or raw_plan.get("failure_criteria") or idea.get("failure_criteria"))
            if as_str(x)
        ],
        "estimated_compute": as_str(raw_plan.get("estimated_compute") or "CPU or single GPU preferred; exact cost to be measured in MVP."),
        "estimated_timeline": as_str(raw_plan.get("estimated_timeline") or "1-2 weeks for MVP validation."),
    }


def normalize_experiment_plans(run_dir: Path, ideas: list[dict]) -> None:
    path = run_dir / "experiment_plan.json"
    backup(path)
    data = load_json(path)
    if isinstance(data, list):
        plans = data
    else:
        raw_items = []
        if isinstance(data, dict):
            raw_items = data.get("idea_specific_experiments") or data.get("idea_experiments") or []
        raw_by_title = {}
        raw_by_id = {}
        for item in raw_items:
            if not isinstance(item, dict):
                continue
            title = item.get("idea_title") or item.get("title")
            if title:
                raw_by_title[title] = item
            idea_id = item.get("idea_id")
            if idea_id:
                raw_by_id[idea_id] = item
        plans = []
        for idea in ideas:
            raw = raw_by_title.get(idea.get("title")) or raw_by_id.get(idea.get("idea_id")) or idea.get("experiment_plan")
            plans.append(normalize_plan_item(idea, raw if isinstance(raw, dict) else None))
    write_json(path, plans)


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize v0.5 evidence-grounded ideation outputs for legacy validators.")
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()

    normalize_baseline_cards(args.run_dir)
    ideas = normalize_ideas(args.run_dir)
    normalize_experiment_plans(args.run_dir, ideas)
    print("Normalized v0.5 ideation outputs")
    print("Run dir:", args.run_dir)
    print("Ideas:", len(ideas))
    print("Backups use .raw suffix when first normalized.")


if __name__ == "__main__":
    main()
