#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def unwrap_ideas(data) -> list[dict]:
    if isinstance(data, dict):
        data = data.get("ideas", [])
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def unwrap_plans(data) -> list[dict]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ["experiments", "idea_specific_experiments", "idea_experiments", "plans"]:
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def is_iad(run_dir: Path, ideas: list[dict]) -> bool:
    blob = (str(run_dir) + " " + json.dumps(ideas[:1], ensure_ascii=False)).lower()
    return "iad" in blob or "anomaly" in blob or "patchcore" in blob


def is_indoor_scene(run_dir: Path, ideas: list[dict]) -> bool:
    blob = (str(run_dir) + " " + json.dumps(ideas[:2], ensure_ascii=False)).lower()
    terms = [
        "indoor_scene",
        "indoor scene",
        "3d indoor",
        "single-image 3d",
        "scene generation",
        "scene reconstruction",
        "3d-front",
        "structured3d",
        "hypersim",
        "text2room",
        "scenescape",
        "dust3r",
        "mast3r",
    ]
    return any(term in blob for term in terms)


def as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def append_unique(items: list, additions: list) -> list:
    out = list(items)
    seen = {json.dumps(x, ensure_ascii=False, sort_keys=True) for x in out}
    for item in additions:
        key = json.dumps(item, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            out.append(item)
            seen.add(key)
    return out


def repair_iad_idea(idea: dict, idx: int) -> dict:
    title = idea.get("title", f"IAD idea {idx}")
    objective = (
        "Algorithmic objective: compute a region-level evidence score "
        "S = z(anomaly_score) + 0.5*z(reference_inconsistency) + 0.5*z(model_disagreement) "
        "- 0.5*z(normal_reference_similarity). A defect claim is accepted only when S >= 2.0, "
        "the region overlaps at least one anomaly heatmap by IoU >= 0.3, and the retrieved normal "
        "reference does not explain the region. Otherwise the agent abstains or escalates."
    )
    thresholds = [
        "MVP success: image_level_auroc improves by at least 2.0 percentage points over the strongest direct baseline on the same split.",
        "MVP success: pixel_level_auroc or PRO score improves by at least 1.0 percentage point without increasing false alarms.",
        "MVP success: false_alarm_reduction is at least 10% on shifted or contaminated normal-bank stress tests.",
        "MVP success: evidence_grounding_score is at least 85%, measured as accepted reports with a valid region mask and retrieved normal reference.",
        "Failure: any negative control reaches within 5% of the repaired agent on the primary metric.",
    ]
    negative_controls = [
        "negative control: random normal reference retrieval instead of top-k nearest normal patches",
        "negative control: shuffled reference-bank provenance while keeping anomaly scores fixed",
        "negative control: unverified VLM report generated without region-reference evidence",
        "negative control: contaminated normal bank with 5%, 10%, and 20% synthetic defect leakage",
    ]
    steps = [
        "MVP week 1 day 1: create iad_reference_manifest.jsonl with train/val/test product splits and normal reference provenance.",
        "MVP week 1 day 2: implement scripts/build_reference_bank.py to store patch embeddings, reference image ids, and retrieval ranks.",
        "MVP week 1 day 3: implement scripts/score_reference_consistency.py with the explicit S score, threshold policy, and abstention rule.",
        "MVP week 1 day 4: run PatchCore/PaDiM/WinCLIP baselines and export baseline_scores.csv plus region_heatmaps.npz.",
        "MVP week 1 day 5: run negative controls: random retrieval, shuffled provenance, unverified report, and contaminated normal bank.",
        "MVP week 2: report AUROC, PRO, false_alarm_reduction, evidence_grounding_score, and selective risk in iad_v05_repair_results.csv.",
    ]
    idea["algorithmic_objective"] = objective
    idea["quantitative_success_thresholds"] = thresholds
    idea["negative_controls"] = negative_controls
    idea["new_component"] = f"{idea.get('new_component', '')} {objective}".strip()
    module = idea.get("minimal_new_module") if isinstance(idea.get("minimal_new_module"), dict) else {}
    module["name"] = module.get("name") or f"{title} verifier module"
    module["input"] = module.get("input") or "anomaly heatmaps, patch embeddings, top-k normal references, VLM defect claims, product split metadata"
    module["output"] = module.get("output") or "accepted/escalated defect claims with region masks, evidence ids, scores, and failure warnings"
    module["algorithm_steps"] = append_unique(as_list(module.get("algorithm_steps")), steps[:5])
    module["training_or_inference_objective"] = objective
    module["why_baseline_cannot_do_this"] = (
        "The direct baselines produce anomaly scores, masks, prompts, or reports, but they do not jointly audit "
        "normal-reference consistency, reject unsupported claims, and quantify selective escalation under shifted references."
    )
    idea["minimal_new_module"] = module
    idea["implementation_plan"] = append_unique(as_list(idea.get("implementation_plan")), steps)
    idea["ablations"] = append_unique(as_list(idea.get("ablations")), negative_controls)
    idea["failure_criteria"] = append_unique(as_list(idea.get("failure_criteria")), thresholds[-2:])
    idea["risks"] = append_unique(
        as_list(idea.get("risks")),
        [
            "Reference retrieval may overfit repeated textures and hide true defects.",
            "Threshold S >= 2.0 may require per-category calibration if score distributions shift.",
        ],
    )
    idea["mvp_artifacts"] = {
        "required_scripts": [
            "scripts/build_reference_bank.py",
            "scripts/score_reference_consistency.py",
            "scripts/run_iad_negative_controls.py",
            "scripts/evaluate_iad_agent.py",
        ],
        "required_data_files": [
            "iad_reference_manifest.jsonl",
            "baseline_scores.csv",
            "region_heatmaps.npz",
            "retrieved_reference_pairs.jsonl",
        ],
        "expected_tables": [
            "iad_v05_repair_results.csv",
            "negative_control_results.csv",
            "selective_risk_table.csv",
        ],
        "expected_figures": [
            "reference_consistency_examples.png",
            "false_alarm_reduction_curve.png",
            "selective_risk_curve.png",
        ],
        "success_threshold": "; ".join(thresholds[:4]),
    }
    idea["expected_outputs"] = append_unique(
        as_list(idea.get("expected_outputs")),
        idea["mvp_artifacts"]["expected_tables"] + idea["mvp_artifacts"]["expected_figures"],
    )
    return idea


def repair_physical_idea(idea: dict, idx: int) -> dict:
    title = idea.get("title", f"Physical idea {idx}")
    objective = (
        "Algorithmic objective: predict an object-level property interval distribution by minimizing "
        "calibrated interval loss L = log_MAE(midpoint, proxy_label) + 0.5*coverage_penalty + "
        "0.2*width_penalty. The module accepts a property only when material confidence >= 0.6 "
        "or returns an abstention/failure_warning."
    )
    thresholds = [
        "MVP success: nominal 90% property intervals achieve at least 80% empirical coverage on proxy labels.",
        "MVP success: density_log_mae or youngs_modulus_log_mae improves by at least 5% over category-only priors.",
        "MVP success: calibration_error is less than 0.10 for accepted object predictions.",
        "MVP success: selective_risk decreases monotonically as abstention threshold increases from 0.3 to 0.7.",
        "Failure: shuffled material-property tables perform within 5% of the real mapper on primary metrics.",
    ]
    negative_controls = [
        "negative control: shuffled material-property table assignments within broad material families",
        "negative control: random object category replacement with same-frequency categories",
        "negative control: background masks treated as objects",
        "negative control: wrong material prompt set with material labels permuted across objects",
    ]
    steps = [
        "MVP week 1 day 1: create indoor_property_manifest.jsonl with image id, object mask, category, material candidates, and proxy interval labels.",
        "MVP week 1 day 2: implement scripts/build_material_property_table.py with density, Young's modulus, Poisson ratio, hardness, and friction ranges plus provenance.",
        "MVP week 1 day 3: implement scripts/predict_property_intervals.py with the calibrated interval loss, confidence threshold, and abstention rule.",
        "MVP week 1 day 4: run GroundingDINO/SAM2/OpenSurfaces/ObjectFolder2.0 baselines and export baseline_property_predictions.csv.",
        "MVP week 1 day 5: run negative controls: shuffled tables, random categories, background masks, and permuted material prompts.",
        "MVP week 2: report coverage, log-MAE, calibration_error, interval width, and selective_risk in physical_v05_repair_results.csv.",
    ]
    idea["algorithmic_objective"] = objective
    idea["quantitative_success_thresholds"] = thresholds
    idea["negative_controls"] = negative_controls
    idea["new_component"] = f"{idea.get('new_component', '')} {objective}".strip()
    module = idea.get("minimal_new_module") if isinstance(idea.get("minimal_new_module"), dict) else {}
    module["name"] = module.get("name") or f"{title} interval module"
    module["input"] = module.get("input") or "RGB image, object masks/boxes, category, material scores, evidence-grounded property tables"
    module["output"] = module.get("output") or "object-level JSON with property intervals, confidence, evidence ids, and failure_warning"
    module["algorithm_steps"] = append_unique(as_list(module.get("algorithm_steps")), steps[:5])
    module["training_or_inference_objective"] = objective
    module["why_baseline_cannot_do_this"] = (
        "The direct baselines provide detection, segmentation, material recognition, or object-property priors, "
        "but they do not propagate material uncertainty into calibrated physical-property intervals with abstention."
    )
    idea["minimal_new_module"] = module
    idea["implementation_plan"] = append_unique(as_list(idea.get("implementation_plan")), steps)
    idea["ablations"] = append_unique(as_list(idea.get("ablations")), negative_controls)
    idea["failure_criteria"] = append_unique(as_list(idea.get("failure_criteria")), thresholds[-2:])
    idea["risks"] = append_unique(
        as_list(idea.get("risks")),
        [
            "Proxy interval labels may be too broad to prove fine-grained property recovery.",
            "Single RGB can hide coatings or internal material composition, so abstention must be preserved.",
        ],
    )
    idea["mvp_artifacts"] = {
        "required_scripts": [
            "scripts/build_material_property_table.py",
            "scripts/predict_property_intervals.py",
            "scripts/run_physical_negative_controls.py",
            "scripts/evaluate_property_intervals.py",
        ],
        "required_data_files": [
            "indoor_property_manifest.jsonl",
            "material_property_table.csv",
            "object_masks.jsonl",
            "baseline_property_predictions.csv",
        ],
        "expected_tables": [
            "physical_v05_repair_results.csv",
            "negative_control_results.csv",
            "coverage_width_tradeoff.csv",
        ],
        "expected_figures": [
            "interval_coverage_curve.png",
            "selective_risk_curve.png",
            "qualitative_object_property_json_examples.png",
        ],
        "success_threshold": "; ".join(thresholds[:4]),
    }
    idea["expected_outputs"] = append_unique(
        as_list(idea.get("expected_outputs")),
        idea["mvp_artifacts"]["expected_tables"] + idea["mvp_artifacts"]["expected_figures"],
    )
    return idea


def repair_indoor_scene_idea(idea: dict, idx: int) -> dict:
    title = idea.get("title", f"Indoor scene idea {idx}")
    objective = (
        "Algorithmic objective: produce a scene-level candidate only if it passes a consistency score "
        "S_scene = 0.25*layout_iou + 0.20*support_relation_accuracy + 0.20*(1-collision_rate) "
        "+ 0.15*novel_view_consistency + 0.10*(1-calibration_error) + 0.10*failure_detection_auc. "
        "The agent must keep multiple hypotheses for occluded regions and attach a failure_warning when "
        "layout, depth, relation, or uncertainty evidence is insufficient."
    )
    thresholds = [
        "MVP success: layout_iou improves by at least 5% over a layout-only baseline on the same validation split.",
        "MVP success: collision_rate is below 10% or decreases by at least 20% relative to the strongest direct baseline.",
        "MVP success: support_relation_accuracy improves by at least 5% over single-sample scene generation.",
        "MVP success: failure_detection_auc is at least 0.75 for corrupted geometry, shuffled relations, and random confidence controls.",
        "MVP success: confidence_calibration error is below 0.10 for accepted scene hypotheses.",
        "Failure: any negative control reaches within 5% of the repaired agent on S_scene or the primary relation/geometry metric.",
    ]
    negative_controls = [
        "negative control: shuffled scene-graph support relations while keeping object categories fixed",
        "negative control: randomized object positions preserving object count and room layout",
        "negative control: depth map shuffled across input images",
        "negative control: random confidence scores attached to otherwise unchanged scene hypotheses",
        "negative control: retrieved furniture assets replaced by generic boxes with matched bounding-box size",
    ]
    steps = [
        "MVP week 1 day 1: create indoor3d_scene_manifest.jsonl with image id, camera metadata, room layout label/proxy, object boxes, and available scene-graph relations.",
        "MVP week 1 day 2: implement scripts/build_scene_schema.py to export a common scene JSON with layout, objects, 3D boxes, relations, uncertainty, and failure_warning.",
        "MVP week 1 day 3: implement scripts/score_scene_consistency.py with the explicit S_scene objective, collision checks, room containment checks, and relation scoring.",
        "MVP week 1 day 4: implement scripts/run_indoor3d_negative_controls.py for shuffled relations, randomized positions, shuffled depth, random confidence, and generic-box replacement.",
        "MVP week 1 day 5: run layout/depth/scene-generation baselines and export baseline_scene_predictions.jsonl plus baseline_scene_scores.csv.",
        "MVP week 2: report layout_iou, collision_rate, out_of_room_rate, support_relation_accuracy, novel_view_consistency, calibration_error, and failure_detection_auc in indoor3d_v05_repair_results.csv.",
    ]
    idea["algorithmic_objective"] = objective
    idea["quantitative_success_thresholds"] = thresholds
    idea["negative_controls"] = negative_controls
    idea["new_component"] = f"{idea.get('new_component', '')} {objective}".strip()
    module = idea.get("minimal_new_module") if isinstance(idea.get("minimal_new_module"), dict) else {}
    module["name"] = module.get("name") or f"{title} scene consistency module"
    module["input"] = module.get("input") or "single RGB indoor image, candidate layout/depth/object hypotheses, retrieved evidence papers, and scene priors"
    module["output"] = module.get("output") or "scene JSON with layout, object 3D boxes, support relations, uncertainty, consistency score, and failure_warning"
    module["algorithm_steps"] = append_unique(as_list(module.get("algorithm_steps")), steps[:5])
    module["training_or_inference_objective"] = objective
    module["why_baseline_cannot_do_this"] = (
        "The cited baselines provide layout, depth, scene priors, or generation components, but they do not jointly "
        "validate geometry, support relations, uncertainty calibration, negative controls, and failure warnings for "
        "single-image indoor 3D scene outputs."
    )
    idea["minimal_new_module"] = module
    idea["implementation_plan"] = append_unique(as_list(idea.get("implementation_plan")), steps)
    idea["ablations"] = append_unique(as_list(idea.get("ablations")), negative_controls)
    idea["failure_criteria"] = append_unique(as_list(idea.get("failure_criteria")), thresholds[-2:])
    idea["risks"] = append_unique(
        as_list(idea.get("risks")),
        [
            "Single-image 3D indoor reconstruction is under-constrained, so multiple plausible occluded layouts may exist.",
            "Dataset layout annotations and rendered geometry may not match real-world clutter or camera calibration.",
            "Scene plausibility metrics can be gamed unless negative controls are included.",
        ],
    )
    idea["mvp_artifacts"] = {
        "required_scripts": [
            "scripts/build_scene_schema.py",
            "scripts/score_scene_consistency.py",
            "scripts/run_indoor3d_negative_controls.py",
            "scripts/evaluate_indoor3d_scene.py",
        ],
        "required_data_files": [
            "indoor3d_scene_manifest.jsonl",
            "baseline_scene_predictions.jsonl",
            "baseline_scene_scores.csv",
            "scene_relation_labels_or_proxies.jsonl",
        ],
        "expected_tables": [
            "indoor3d_v05_repair_results.csv",
            "negative_control_results.csv",
            "scene_failure_breakdown.csv",
        ],
        "expected_figures": [
            "scene_consistency_examples.png",
            "collision_and_relation_failure_cases.png",
            "calibration_vs_failure_detection_curve.png",
        ],
        "success_threshold": "; ".join(thresholds[:5]),
    }
    idea["expected_outputs"] = append_unique(
        as_list(idea.get("expected_outputs")),
        idea["mvp_artifacts"]["expected_tables"] + idea["mvp_artifacts"]["expected_figures"],
    )
    return idea


def repair_plan(plan: dict, idea: dict, mode: str) -> dict:
    thresholds = idea.get("quantitative_success_thresholds", [])
    neg = idea.get("negative_controls", [])
    module = idea.get("minimal_new_module", {})
    plan["idea_title"] = idea.get("title", plan.get("idea_title", ""))
    plan["implementation_steps"] = append_unique(as_list(plan.get("implementation_steps")), as_list(idea.get("implementation_plan")))
    plan["ablation_studies"] = append_unique(as_list(plan.get("ablation_studies")), neg)
    plan["success_criteria"] = append_unique(as_list(plan.get("success_criteria")), thresholds[:4])
    plan["failure_cases"] = append_unique(as_list(plan.get("failure_cases")), thresholds[-1:])
    plan["estimated_timeline"] = "MVP in 1-2 weeks: week 1 implementation and negative controls, week 2 evaluation and report."
    compute_by_mode = {
        "iad": "CPU or single GPU; target under 8 GPU-hours for MVP.",
        "physical": "CPU or single GPU; target under 6 GPU-hours for MVP with frozen detectors/material models.",
        "indoor_scene": "Single GPU preferred; target under 10 GPU-hours for MVP with frozen layout/depth/scene components.",
    }
    plan["estimated_compute"] = compute_by_mode.get(mode, "CPU or single GPU; target under 8 GPU-hours for MVP.")
    if not plan.get("data_preparation"):
        plan["data_preparation"] = as_list(idea.get("datasets"))
    if not plan.get("baseline_to_compare"):
        plan["baseline_to_compare"] = as_list(idea.get("direct_baselines"))
    if not plan.get("evaluation_metrics"):
        plan["evaluation_metrics"] = as_list(idea.get("metrics"))
    plan["algorithmic_objective"] = idea.get("algorithmic_objective") or module.get("training_or_inference_objective")
    return plan


def run_postprocess(repaired_run: Path) -> None:
    root = project_root()
    commands = [
        ["python", "focused_workflow/scripts/validate_outputs.py", str(repaired_run)],
        ["python", "focused_workflow/scripts/validate_evidence_grounding.py", str(repaired_run)],
        ["python", "focused_workflow/scripts/format_ideas_for_review.py", str(repaired_run)],
        ["python", "focused_workflow/scripts/evaluate_idea_quality.py", str(repaired_run), "--overwrite"],
        ["python", "focused_workflow/scripts/make_si2025_review_sheet.py", str(repaired_run)],
    ]
    for cmd in commands:
        subprocess.run(cmd, cwd=root, check=True)


def copy_base_files(src: Path, dst: Path) -> None:
    names = [
        "task_spec.yaml",
        "baseline_cards.jsonl",
        "evidence_baseline_cards.jsonl",
        "papers.jsonl",
        "prompt_papers.jsonl",
        "evidence_context.md",
        "evidence_quality_summary.json",
    ]
    for name in names:
        path = src / name
        if path.exists():
            shutil.copy2(path, dst / name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply deterministic local v0.5 targeted repair without external API calls.")
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--skip-postprocess", action="store_true")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    ideas = unwrap_ideas(load_json(run_dir / "focused_ideas.json"))
    plans = unwrap_plans(load_json(run_dir / "experiment_plan.json"))
    if not ideas:
        raise SystemExit(f"No ideas found in {run_dir / 'focused_ideas.json'}")
    if is_iad(run_dir, ideas):
        mode = "iad"
    elif is_indoor_scene(run_dir, ideas):
        mode = "indoor_scene"
    else:
        mode = "physical"

    repaired_ideas = []
    for idx, idea in enumerate(ideas, start=1):
        if mode == "iad":
            repaired_ideas.append(repair_iad_idea(dict(idea), idx))
        elif mode == "indoor_scene":
            repaired_ideas.append(repair_indoor_scene_idea(dict(idea), idx))
        else:
            repaired_ideas.append(repair_physical_idea(dict(idea), idx))

    plan_by_title = {p.get("idea_title"): dict(p) for p in plans if isinstance(p, dict)}
    repaired_plans = []
    for idea in repaired_ideas:
        plan = plan_by_title.get(idea.get("title"), {})
        repaired_plans.append(repair_plan(dict(plan), idea, mode))

    if args.output_dir:
        repaired_run = args.output_dir.resolve()
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        repaired_run = run_dir / "repair_runs" / f"local_targeted_repair_{timestamp}" / "repaired_run"
    repaired_run.mkdir(parents=True, exist_ok=True)
    copy_base_files(run_dir, repaired_run)
    write_json(repaired_run / "focused_ideas.json", repaired_ideas)
    write_json(repaired_run / "experiment_plan.json", repaired_plans)

    if not args.skip_postprocess:
        run_postprocess(repaired_run)

    print("Local v0.5 targeted repair complete")
    print("Source run:", run_dir)
    print("Repaired run:", repaired_run)
    print("Mode:", mode)
    print("Ideas:", len(repaired_ideas))


if __name__ == "__main__":
    main()
