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


def repair_localized_verifier(idea: dict) -> dict:
    objective = (
        "Algorithmic objective: verify each material claim with a localized evidence score "
        "S_evidence = 0.35*masked_crop_material_score + 0.20*mask_interior_texture_score "
        "+ 0.20*counterfactual_erasure_drop + 0.15*object_context_compatibility "
        "+ 0.10*VLM_evidence_consistency. A material/property claim is accepted only when "
        "S_evidence >= tau, the object-erasure counterfactual reduces confidence by at least delta, "
        "and the supporting pixels lie inside the predicted object mask. Otherwise the agent returns "
        "unsupported_claim or abstains before property lookup."
    )
    thresholds = [
        "MVP success: unsupported_material_claim_rate decreases by at least 20% relative to CLIP/VLM material scoring without localized verification.",
        "MVP success: material_claim_precision improves by at least 5 percentage points while material_claim_recall drops by no more than 3 percentage points.",
        "MVP success: object-erasure counterfactual lowers accepted material confidence by at least 15% on average for correctly localized claims.",
        "MVP success: evidence_localization_iou is at least 0.50 for objects with proxy material masks or visible surface annotations.",
        "Failure: context-only crops or swapped masks perform within 5% of the localized verifier on material_claim_precision or unsupported_claim_rate.",
    ]
    negative_controls = [
        "negative control: swap object masks between objects in the same image while keeping material prompts fixed",
        "negative control: erase object pixels and keep only surrounding scene context",
        "negative control: use a random crop with matched area instead of the predicted object mask",
        "negative control: assign visually incompatible material prompts to the localized crop",
        "negative control: keep VLM textual rationale but remove pixel-level evidence links",
    ]
    steps = [
        "MVP week 1 day 1: create localized_material_evidence_manifest.jsonl with image id, object mask, crop path, material candidates, evidence pixels, and proxy material labels.",
        "MVP week 1 day 2: implement scripts/build_local_evidence_crops.py to export masked crops, context-only crops, erased-object crops, and swapped-mask controls.",
        "MVP week 1 day 3: implement scripts/score_material_evidence.py with S_evidence, tau, delta, and abstention decisions.",
        "MVP week 1 day 4: implement scripts/run_material_verifier_controls.py for mask swap, context-only, random crop, incompatible prompt, and no-pixel-evidence controls.",
        "MVP week 1 day 5: compare CLIP/VLM material scoring, category-only priors, and localized verifier outputs in material_verifier_results.csv.",
        "MVP week 2: report material_claim_precision, material_claim_recall, unsupported_claim_rate, evidence_localization_iou, calibration_error, and selective risk.",
    ]
    idea["algorithmic_objective"] = objective
    idea["quantitative_success_thresholds"] = thresholds
    idea["negative_controls"] = negative_controls
    idea["new_component"] = (
        "A verifier that requires each predicted material and physical-property claim to be linked to localized crop evidence, "
        "such as mask interior texture, specular highlights, color, transparency, and object-scene compatibility. "
        + objective
    )
    module = idea.get("minimal_new_module") if isinstance(idea.get("minimal_new_module"), dict) else {}
    module["name"] = "Localized material-evidence verifier"
    module["input"] = "RGB image, object mask/box, masked crop, context-only crop, erased-object crop, material candidates, VLM/CLIP material scores"
    module["output"] = "accepted/unsupported material claims with evidence pixels, S_evidence, abstention flag, and downstream property lookup eligibility"
    module["algorithm_steps"] = append_unique(as_list(module.get("algorithm_steps")), steps[:5])
    module["training_or_inference_objective"] = objective
    module["why_baseline_cannot_do_this"] = (
        "Material recognition and VLM baselines can name plausible materials, but they do not force the claim to be supported by "
        "pixels inside the object mask or reject claims that survive object-erasure and mask-swap counterfactuals."
    )
    idea["minimal_new_module"] = module
    idea["implementation_plan"] = append_unique(as_list(idea.get("implementation_plan")), steps)
    idea["ablations"] = append_unique(as_list(idea.get("ablations")), negative_controls)
    idea["failure_criteria"] = append_unique(as_list(idea.get("failure_criteria")), thresholds[-2:])
    idea["risks"] = append_unique(
        as_list(idea.get("risks")),
        [
            "Visible surface evidence may support only coating material, not structural material.",
            "Transparent or reflective objects may produce weak localized cues even when the material class is known.",
        ],
    )
    idea["mvp_artifacts"] = {
        "required_scripts": [
            "scripts/build_local_evidence_crops.py",
            "scripts/score_material_evidence.py",
            "scripts/run_material_verifier_controls.py",
            "scripts/evaluate_material_claims.py",
        ],
        "required_data_files": [
            "localized_material_evidence_manifest.jsonl",
            "object_masks.jsonl",
            "material_candidate_scores.csv",
            "counterfactual_crop_index.jsonl",
        ],
        "expected_tables": [
            "material_verifier_results.csv",
            "localized_negative_control_results.csv",
            "unsupported_claim_breakdown.csv",
        ],
        "expected_figures": [
            "localized_evidence_examples.png",
            "counterfactual_erasure_curve.png",
            "unsupported_claim_examples.png",
        ],
        "success_threshold": "; ".join(thresholds[:4]),
    }
    idea["expected_outputs"] = append_unique(
        as_list(idea.get("expected_outputs")),
        idea["mvp_artifacts"]["expected_tables"] + idea["mvp_artifacts"]["expected_figures"],
    )
    return idea


def repair_proposal_uncertainty(idea: dict) -> dict:
    objective = (
        "Algorithmic objective: propagate detection and segmentation uncertainty into property predictions by sampling K object "
        "proposals from detector boxes, SAM masks, category scores, and material hypotheses. Cluster proposals by mask IoU and "
        "category agreement, then compute each object's property distribution as p(y|image)=sum_k w_k p(y|mask_k, category_k, material_k). "
        "A JSON record is accepted only if proposal entropy <= H_max or the record includes multi-hypothesis alternatives and a failure_warning."
    )
    thresholds = [
        "MVP success: visible_object_recall improves by at least 5 percentage points over single-top-proposal inference on difficult small/occluded objects.",
        "MVP success: duplicate_object_rate stays below 10% after proposal clustering.",
        "MVP success: prediction_interval_coverage improves without increasing average interval width by more than 15%.",
        "MVP success: selective_risk decreases monotonically as proposal entropy threshold becomes stricter.",
        "Failure: collapsing all proposal weights to the top detector output performs within 5% of the full uncertainty propagation module.",
    ]
    negative_controls = [
        "negative control: collapse all proposal weights to the highest-confidence detector output",
        "negative control: inject random low-overlap masks as object proposals",
        "negative control: shuffle material hypotheses across proposal clusters",
        "negative control: remove small or partially occluded objects from evaluation",
        "negative control: use uniform proposal weights instead of calibrated proposal weights",
    ]
    steps = [
        "MVP week 1 day 1: create proposal_uncertainty_manifest.jsonl with image id, all detector boxes, SAM masks, category scores, material scores, and object proxy labels.",
        "MVP week 1 day 2: implement scripts/sample_object_proposals.py to collect top-k boxes/masks/categories/material hypotheses per visible object.",
        "MVP week 1 day 3: implement scripts/cluster_proposals.py using mask IoU, box IoU, and category agreement to merge duplicate proposals.",
        "MVP week 1 day 4: implement scripts/propagate_property_uncertainty.py to marginalize property intervals over proposal clusters and compute proposal entropy.",
        "MVP week 1 day 5: implement scripts/run_proposal_uncertainty_controls.py for top-proposal collapse, random masks, shuffled materials, easy-object-only, and uniform weights.",
        "MVP week 2: report visible_object_recall, duplicate_object_rate, interval coverage, interval width, proposal entropy calibration, and selective risk.",
    ]
    idea["algorithmic_objective"] = objective
    idea["quantitative_success_thresholds"] = thresholds
    idea["negative_controls"] = negative_controls
    idea["new_component"] = (
        "A proposal ensemble and uncertainty propagator that samples boxes, masks, categories, and material hypotheses, "
        "then marginalizes physical-property predictions over those alternatives. "
        + objective
    )
    module = idea.get("minimal_new_module") if isinstance(idea.get("minimal_new_module"), dict) else {}
    module["name"] = "Proposal uncertainty propagation module"
    module["input"] = "RGB image, detector boxes, SAM masks, category scores, material scores, proposal confidence, and property prior tables"
    module["output"] = "object-level JSON with clustered proposals, marginalized property intervals, proposal entropy, confidence, and failure_warning"
    module["algorithm_steps"] = append_unique(as_list(module.get("algorithm_steps")), steps[:5])
    module["training_or_inference_objective"] = objective
    module["why_baseline_cannot_do_this"] = (
        "Detector/segmenter/material baselines usually pass only one box or mask downstream, so property uncertainty ignores missed objects, "
        "duplicate masks, category ambiguity, and material-hypothesis ambiguity."
    )
    idea["minimal_new_module"] = module
    idea["implementation_plan"] = append_unique(as_list(idea.get("implementation_plan")), steps)
    idea["ablations"] = append_unique(as_list(idea.get("ablations")), negative_controls)
    idea["failure_criteria"] = append_unique(as_list(idea.get("failure_criteria")), thresholds[-2:])
    idea["risks"] = append_unique(
        as_list(idea.get("risks")),
        [
            "Proposal sampling may improve coverage while increasing duplicate objects unless clustering is strict.",
            "Wide intervals may hide poor recognition, so coverage must be reported with interval width and selective risk.",
        ],
    )
    idea["mvp_artifacts"] = {
        "required_scripts": [
            "scripts/sample_object_proposals.py",
            "scripts/cluster_proposals.py",
            "scripts/propagate_property_uncertainty.py",
            "scripts/run_proposal_uncertainty_controls.py",
            "scripts/evaluate_property_json_uncertainty.py",
        ],
        "required_data_files": [
            "proposal_uncertainty_manifest.jsonl",
            "detector_boxes.jsonl",
            "sam_masks.jsonl",
            "material_candidate_scores.csv",
        ],
        "expected_tables": [
            "proposal_uncertainty_results.csv",
            "proposal_negative_control_results.csv",
            "coverage_width_tradeoff.csv",
        ],
        "expected_figures": [
            "proposal_cluster_examples.png",
            "entropy_selective_risk_curve.png",
            "missed_object_failure_cases.png",
        ],
        "success_threshold": "; ".join(thresholds[:4]),
    }
    idea["expected_outputs"] = append_unique(
        as_list(idea.get("expected_outputs")),
        idea["mvp_artifacts"]["expected_tables"] + idea["mvp_artifacts"]["expected_figures"],
    )
    return idea


def repair_plan(plan: dict, idea: dict) -> dict:
    plan["idea_title"] = idea.get("title", plan.get("idea_title", ""))
    plan["implementation_steps"] = append_unique(as_list(plan.get("implementation_steps")), as_list(idea.get("implementation_plan")))
    plan["ablation_studies"] = append_unique(as_list(plan.get("ablation_studies")), as_list(idea.get("negative_controls")))
    plan["success_criteria"] = append_unique(as_list(plan.get("success_criteria")), as_list(idea.get("quantitative_success_thresholds"))[:4])
    plan["failure_cases"] = append_unique(as_list(plan.get("failure_cases")), as_list(idea.get("quantitative_success_thresholds"))[-1:])
    plan["estimated_compute"] = "CPU or single GPU; target under 8 GPU-hours for physical-property v2 MVP validation."
    plan["estimated_timeline"] = "MVP in 1-2 weeks: week 1 module and negative controls, week 2 evaluation and failure analysis."
    if not plan.get("data_preparation"):
        plan["data_preparation"] = as_list(idea.get("datasets"))
    if not plan.get("baseline_to_compare"):
        plan["baseline_to_compare"] = as_list(idea.get("direct_baselines"))
    if not plan.get("evaluation_metrics"):
        plan["evaluation_metrics"] = as_list(idea.get("metrics"))
    plan["algorithmic_objective"] = idea.get("algorithmic_objective")
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply physical-property v2 repair for mechanism consistency.")
    parser.add_argument("--before-run", type=Path, required=True)
    parser.add_argument("--after-v1-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--skip-postprocess", action="store_true")
    args = parser.parse_args()

    before_run = args.before_run.resolve()
    after_v1_run = args.after_v1_run.resolve()
    ideas = load_json(after_v1_run / "focused_ideas.json")
    plans = load_json(after_v1_run / "experiment_plan.json")
    if not isinstance(ideas, list) or len(ideas) != 3:
        raise SystemExit("Expected exactly three physical-property ideas in after-v1 run.")
    if not isinstance(plans, list):
        plans = []

    repaired = []
    for idea in ideas:
        title = idea.get("title", "").lower()
        if "localized visual evidence verifier" in title:
            repaired.append(repair_localized_verifier(dict(idea)))
        elif "proposal uncertainty propagation" in title:
            repaired.append(repair_proposal_uncertainty(dict(idea)))
        else:
            repaired.append(dict(idea))

    plan_by_title = {p.get("idea_title"): dict(p) for p in plans if isinstance(p, dict)}
    repaired_plans = [repair_plan(plan_by_title.get(idea.get("title"), {}), idea) for idea in repaired]

    if args.output_dir:
        out = args.output_dir.resolve()
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = before_run / "repair_runs" / f"physical_v2_mechanism_repair_{stamp}" / "repaired_run"
    out.mkdir(parents=True, exist_ok=True)
    copy_base_files(after_v1_run, out)
    write_json(out / "focused_ideas.json", repaired)
    write_json(out / "experiment_plan.json", repaired_plans)

    if not args.skip_postprocess:
        run_postprocess(out)

    print("Physical-property v2 mechanism repair complete")
    print("Before run:", before_run)
    print("After v1 run:", after_v1_run)
    print("Repaired v2 run:", out)
    print("Ideas:", len(repaired))


if __name__ == "__main__":
    main()
