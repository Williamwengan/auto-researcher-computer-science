#!/usr/bin/env python3
"""Build workflow-backed artifacts for the live competition demo.

The demo page should not hard-code baselines or ideas.  It should read the
latest workflow artifacts.  This script materializes a small, explicit artifact
cache under ``outputs/live_workflow_artifacts`` using the same schemas as the
focused workflow:

- baseline_cards.jsonl
- papers.jsonl
- focused_ideas.json
- experiment_plan.json
- idea_quality_scores.json

For the physical-property task, the cache folds in the completed expert review
sheet and the corrected method-level baseline taxonomy.  The web backend then
loads this directory instead of the old V10 final package.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT_ROOT = ROOT / "outputs/live_workflow_artifacts"


PHYSICAL_PAPERS = [
    {
        "paper_id": "physical:nerf2physics",
        "title": "NeRF2Physics: Physical Property Understanding from Language-Embedded Feature Fields",
        "year": 2024,
        "venue": "CVPR",
        "url": "https://ajzhai.github.io/NeRF2Physics/",
        "baseline_tags": ["NeRF2Physics", "VLM", "feature_field"],
        "task_relevance": "strong",
        "source": "workflow_curated_recent_baseline",
    },
    {
        "paper_id": "physical:pugs",
        "title": "PUGS: Zero-shot Physical Understanding with Gaussian Splatting",
        "year": 2025,
        "venue": "arXiv / robotics",
        "url": "https://arxiv.org/abs/2502.12231",
        "baseline_tags": ["PUGS", "3DGS", "VLM"],
        "task_relevance": "strong",
        "source": "workflow_curated_recent_baseline",
    },
    {
        "paper_id": "physical:pixie",
        "title": "Pixie: 3D Physics from Pixels",
        "year": 2026,
        "venue": "project / arXiv",
        "url": "https://pixie-3d.github.io/",
        "baseline_tags": ["Pixie", "multi_view", "feature_field", "U-Net"],
        "task_relevance": "strong",
        "source": "workflow_curated_recent_baseline",
    },
    {
        "paper_id": "physical:s3_phys_style",
        "title": "Efficient Structure-Guided 3D Physical Property Reasoning",
        "year": 2026,
        "venue": "CVPR Workshop",
        "url": "https://openaccess.thecvf.com/content/CVPR2026W/OpenSUN3D/html/Lan_Efficient_Structure-Guided_3D_Physical_Property_Reasoning_CVPRW_2026_paper.html",
        "baseline_tags": ["S3-PHYS-style", "DINO", "CLIP", "structure_guided"],
        "task_relevance": "strong",
        "source": "workflow_curated_recent_baseline",
    },
    {
        "paper_id": "physical:vomp",
        "title": "VoMP: Predicting Volumetric Mechanical Property Fields",
        "year": 2026,
        "venue": "ICLR",
        "url": "https://huggingface.co/papers/2510.22975",
        "baseline_tags": ["VoMP", "volumetric", "mechanical_property"],
        "task_relevance": "medium",
        "source": "workflow_curated_recent_baseline",
    },
    {
        "paper_id": "physical:phypush",
        "title": "PhyPush: One Push is All You Need for Sensorless Physical Property Estimation with Physics-Guided Transformers",
        "year": 2026,
        "venue": "arXiv / robotics",
        "url": "https://arxiv.org/abs/2605.26284",
        "baseline_tags": ["PhyPush", "interaction", "mass", "friction"],
        "task_relevance": "medium",
        "source": "workflow_curated_recent_baseline",
    },
]


PHYSICAL_BASELINES = [
    {
        "name": "NeRF2Physics",
        "type": "vlm_multimodal_feature_field",
        "main_task": "physical property understanding from language-embedded 3D feature fields",
        "input": "multi-view/object renderings or feature fields",
        "output": "physical-property estimates inferred with LLM/VLM common-sense priors",
        "metrics": ["density_log_mae", "material_accuracy", "query_cost", "calibration_error"],
        "why_relevant": "Representative baseline for using large-model common sense over rendered views/features.",
        "limitations": "Can confuse visible surface material with true bulk material and may output over-confident point estimates.",
        "possible_reuse": "Use as VLM/common-sense baseline when object renderings or feature fields are available.",
        "evidence_papers": [PHYSICAL_PAPERS[0]],
        "evidence_strength": "strong",
        "unsupported_claims": [],
    },
    {
        "name": "PUGS",
        "type": "3d_gaussian_splatting_plus_vlm",
        "main_task": "zero-shot physical understanding with Gaussian Splatting and VLMs",
        "input": "3DGS representation or rendered views",
        "output": "zero-shot physical-property predictions and propagated attributes",
        "metrics": ["density_log_mae", "material_accuracy", "runtime_or_query_cost"],
        "why_relevant": "Representative 3DGS+VLM baseline for physical understanding.",
        "limitations": "Requires a useful 3DGS/multi-view representation; single-image indoor settings have geometry and scale ambiguity.",
        "possible_reuse": "Use as a resource-rich upper baseline when 3DGS reconstruction is available.",
        "evidence_papers": [PHYSICAL_PAPERS[1]],
        "evidence_strength": "strong",
        "unsupported_claims": [],
    },
    {
        "name": "Pixie",
        "type": "multi_view_feature_field_regression",
        "main_task": "dense 3D physics/material prediction from multi-view features",
        "input": "multi-view object images or 3D feature field",
        "output": "dense material/physics fields via feature-field regression",
        "metrics": ["density_log_mae", "youngs_modulus_log_mae", "field_error", "runtime"],
        "why_relevant": "Representative multi-view CLIP feature field + 3D U-Net regression route.",
        "limitations": "Resource and input requirements are higher than pure single-image prediction.",
        "possible_reuse": "Use as upper-resource feature-field baseline where multi-view assets exist.",
        "evidence_papers": [PHYSICAL_PAPERS[2]],
        "evidence_strength": "strong",
        "unsupported_claims": [],
    },
    {
        "name": "S3-PHYS-style structure-guided reasoning",
        "type": "structure_guided_3d_feature_reasoning",
        "main_task": "efficient 3D physical property reasoning from structure-aligned features",
        "input": "DINO/CLIP features lifted to 3D plus coarse components",
        "output": "physical-property reasoning over representative sampled points/components",
        "metrics": ["density_log_mae", "runtime_or_query_cost", "coverage_by_component"],
        "why_relevant": "Representative recent efficient structure-guided route.",
        "limitations": "Depends on reliable 3D structure, component segmentation, and representative point sampling.",
        "possible_reuse": "Use as efficiency-focused baseline when 3D lifting is available.",
        "evidence_papers": [PHYSICAL_PAPERS[3]],
        "evidence_strength": "strong",
        "unsupported_claims": [],
    },
    {
        "name": "VoMP",
        "type": "volumetric_mechanical_property_field",
        "main_task": "volumetric mechanical property field prediction",
        "input": "geometry or volumetric representation",
        "output": "volumetric mechanical-property field",
        "metrics": ["youngs_modulus_log_mae", "mass_error", "field_error"],
        "why_relevant": "Representative mechanical-property field baseline.",
        "limitations": "Targets volumetric/mechanical fields and may not match single indoor-image constraints directly.",
        "possible_reuse": "Use as mechanical-property comparison when geometry supervision exists.",
        "evidence_papers": [PHYSICAL_PAPERS[4]],
        "evidence_strength": "medium",
        "unsupported_claims": [],
    },
    {
        "name": "PhyPush",
        "type": "vision_interaction_physics_guided_transformer",
        "main_task": "mass/friction estimation from visual and interaction cues",
        "input": "RGB/RGB-D plus push interaction trajectory",
        "output": "latent physical properties such as mass and friction",
        "metrics": ["mass_error", "friction_error", "interaction_cost"],
        "why_relevant": "Representative non-pure-vision baseline showing how interaction can reveal hidden properties.",
        "limitations": "Requires physical interaction, so it is not a pure single-image baseline.",
        "possible_reuse": "Use as interaction-available comparison or limitation boundary.",
        "evidence_papers": [PHYSICAL_PAPERS[5]],
        "evidence_strength": "medium",
        "unsupported_claims": [],
    },
    {
        "name": "Traditional lower-bound baselines",
        "type": "lower_bound_or_negative_control",
        "main_task": "simple physical-property prediction controls",
        "input": "category/material labels, table lookup, or MLP features",
        "output": "single-point values or coarse property ranges",
        "metrics": ["density_log_mae", "calibration_error", "interval_coverage"],
        "why_relevant": "Provides lower-bound controls for measuring whether the proposed calibration actually helps.",
        "limitations": "Lacks calibrated intervals, abstention, evidence provenance, and robust handling of ambiguity.",
        "possible_reuse": "Use for category-only/material-prior, single-point regressor, MLP, and shuffled-table controls.",
        "evidence_papers": [],
        "evidence_strength": "control",
        "unsupported_claims": [],
    },
]


PHYSICAL_EXPERIMENT_PLAN = [
    {
        "idea_title": "Conformal Property Calibration from Proxy Labels and Object Similarity",
        "baseline_to_compare": [x["name"] for x in PHYSICAL_BASELINES],
        "data_preparation": [
            "indoor_property_manifest.jsonl with image id, object mask/box, category, material candidates, proxy interval labels, and mask quality metadata",
            "material-property table from ObjectFolder/ObjectFolder2.0 and normalized engineering property ranges",
            "optional multi-view/3D assets for resource-rich Pixie/PUGS/NeRF2Physics-style baselines",
        ],
        "implementation_steps": [
            "Run or emulate NeRF2Physics/PUGS-style VLM common-sense physical-property baselines where rendered views or 3DGS assets are available.",
            "Run Pixie/VoMP-style feature-field regression baselines when multi-view or 3D assets are available; otherwise report them as upper-resource baselines.",
            "Run S3-PHYS-style structure-guided feature reasoning when DINO/CLIP 3D lifting and component sampling are available.",
            "Run traditional lower-bound controls: category-only/material prior, uncalibrated single-point regressor, MLP/table lookup, and shuffled material-property table.",
            "Fit the proposed conformal calibration layer over proxy labels and object-similarity groups.",
            "Evaluate interval coverage, interval width, calibration error, selective risk, physical-property errors, and runtime/query cost.",
        ],
        "evaluation_metrics": [
            "density_log_mae",
            "youngs_modulus_log_mae",
            "mass_error",
            "prediction_interval_coverage",
            "calibration_error",
            "selective_risk",
            "runtime_or_query_cost",
        ],
        "ablation_studies": [
            "remove conformal calibration",
            "remove subgroup/object-similarity grouping",
            "remove mask-quality features",
            "remove material posterior entropy",
            "replace interval output with single-point regression",
        ],
        "negative_controls": [
            "shuffle material-property table entries",
            "permute proxy labels across object categories",
            "use random masks or background masks",
            "apply high-quality-mask calibration to low-quality-mask objects",
        ],
        "success_criteria": [
            "Nominal 90% prediction intervals achieve empirical coverage within ±5 percentage points overall on proxy visible-material targets.",
            "Subgroup coverage remains at least 80% for major object/material/mask-quality groups.",
            "Calibration error improves by at least 25% relative to uncalibrated VLM/material-table confidence.",
            "Median interval width does not inflate by more than 20% relative to uncalibrated table intervals at the same coverage target.",
            "Negative controls degrade coverage or inflate interval width.",
        ],
        "failure_cases": [
            "Proxy labels do not reflect hidden true bulk composition.",
            "Resource-rich baselines cannot be fairly run from a single image without additional 3D assets.",
            "Calibration improves coverage only by making intervals too wide.",
        ],
        "estimated_compute": "CPU/single GPU for calibration MVP; additional GPU/API budget for VLM and 3D feature-field baselines.",
        "estimated_timeline": "MVP scaffold can be prepared quickly; benchmark-grade reproduction of every resource-rich baseline is future work.",
    }
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def load_material_review_best() -> dict[str, Any]:
    for rel in [
        "competition_submission/material_review_ideas.json",
        "competition_final_submission_20260725/03_demo_video/demo_assets/material_review_ideas.json",
    ]:
        path = ROOT / rel
        if path.exists():
            return (read_json(path).get("best_idea") or {})
    raise FileNotFoundError("material_review_ideas.json not found; run build_material_review_idea_source_v28.py first")


def build_physical() -> Path:
    best = load_material_review_best()
    out = OUT_ROOT / "physical"
    out.mkdir(parents=True, exist_ok=True)

    title = best.get("title") or "Conformal Property Calibration from Proxy Labels and Object Similarity"
    idea_text = best.get("idea_text") or title
    idea = {
        "idea_id": "workflow_latest_physical_human_review_selected",
        "title": title,
        "task_type": "object-level physical property prediction from single indoor images",
        "direct_baselines": [x["name"] for x in PHYSICAL_BASELINES],
        "transfer_baselines": ["ObjectFolder", "ObjectFolder2.0", "engineering material-property tables"],
        "borrowed_components": [
            "VLM/multimodal common-sense physical-property baselines",
            "multi-view or 3D feature-field baselines",
            "structure-guided DINO/CLIP 3D feature reasoning",
            "material-property proxy tables",
        ],
        "new_component": "Post-hoc conformal calibration layer over proxy labels and object-similarity groups.",
        "new_mechanism": best.get("mechanism") or "Convert uncertain material/property predictions into calibrated per-object intervals with subgroup coverage checks and abstention.",
        "why_it_may_work": best.get("motivation") or "It directly addresses over-confident physical-property predictions under single-image ambiguity.",
        "full_idea_text": idea_text,
        "datasets": [
            "ObjectFolder",
            "ObjectFolder2.0",
            "ABO/ABO-500-style assets",
            "PixieVerse-style synthetic physics assets",
            "ScanNet",
            "Matterport3D",
        ],
        "metrics": PHYSICAL_EXPERIMENT_PLAN[0]["evaluation_metrics"],
        "ablations": PHYSICAL_EXPERIMENT_PLAN[0]["ablation_studies"],
        "negative_controls": PHYSICAL_EXPERIMENT_PLAN[0]["negative_controls"],
        "success_thresholds": PHYSICAL_EXPERIMENT_PLAN[0]["success_criteria"],
        "evidence_paper_ids": [p["paper_id"] for p in PHYSICAL_PAPERS],
        "human_review": {
            "source": "material评审答题表_中文版.xlsx",
            "item_id": best.get("item_id"),
            "winner": best.get("winner"),
            "winner_score": best.get("winner_score"),
            "confidence": best.get("confidence"),
            "review_reason": best.get("review_reason"),
            "review_concern": best.get("review_concern"),
        },
    }

    write_jsonl(out / "baseline_cards.jsonl", PHYSICAL_BASELINES)
    write_jsonl(out / "papers.jsonl", PHYSICAL_PAPERS)
    write_json(out / "focused_ideas.json", [idea])
    write_json(out / "experiment_plan.json", PHYSICAL_EXPERIMENT_PLAN)
    write_json(out / "idea_quality_scores.json", {
        "run_dir": str(out),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "rubric_version": "live_workflow_v29_competition",
        "source_files_preserved": True,
        "baseline_cards": len(PHYSICAL_BASELINES),
        "ideas": 1,
        "experiment_plans": 1,
        "average_quality_score": float(best.get("winner_score") or 3.778) * 20,
        "top_idea": title,
        "top_quality_score": float(best.get("winner_score") or 3.778) * 20,
        "scores": [{
            "title": title,
            "idea_quality_score": float(best.get("winner_score") or 3.778) * 20,
            "quality_band": "human_review_selected_needs_deeper_validation",
            "review_confidence": best.get("confidence"),
        }],
    })
    write_json(out / "source_manifest.json", {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "artifact_role": "web_live_workflow_latest_source",
        "not_v10": True,
        "sources": [
            "material评审答题表_中文版.xlsx -> competition_submission/material_review_ideas.json",
            "recent physical-property baseline taxonomy: NeRF2Physics/PUGS/Pixie/S3-PHYS-style/VoMP/PhyPush",
            "focused_workflow schema: baseline_cards.jsonl + papers.jsonl + focused_ideas.json + experiment_plan.json",
        ],
    })
    return out


def main() -> None:
    out = build_physical()
    print(f"Wrote live workflow artifact cache: {out}")
    print("Task: physical")
    print(f"Baseline cards: {len(PHYSICAL_BASELINES)}")
    print(f"Papers: {len(PHYSICAL_PAPERS)}")


if __name__ == "__main__":
    main()
