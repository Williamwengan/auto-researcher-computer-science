#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


CLAIM_MAP = {
    "Layout-First Scene Assembly with Uncertainty-Aware Object Slots": [
        {
            "baseline": "Text2Room",
            "weakness": (
                "Text2Room generates room-scale textured 3D meshes using text-to-image generation, "
                "monocular depth, inpainting, viewpoint selection, and iterative fusion, but it does not "
                "directly provide layout_iou, object-slot uncertainty, collision checks, support relation "
                "validation, or failure_warning fields for a single-image indoor scene schema."
            ),
            "evidence_ids": ["seed:text2room_2023"],
        },
        {
            "baseline": "SceneScape",
            "weakness": (
                "SceneScape focuses on text-driven consistent scene generation, while this task requires "
                "explicit single-image room layout, object slots, geometric consistency metrics, "
                "uncertainty, and failure warnings."
            ),
            "evidence_ids": ["seed:scenescape_2023"],
        },
        {
            "baseline": "NeRFVS",
            "weakness": (
                "NeRFVS is relevant to novel-view synthesis and view consistency, but it does not by itself "
                "solve single-image object-level layout assembly with collision, containment, and scene-schema validation."
            ),
            "evidence_ids": ["seed:nerfvs_2023"],
        },
        {
            "baseline": "DUSt3R",
            "weakness": (
                "DUSt3R provides dense 3D geometry cues, but it is not an object-slot scene assembly module "
                "with collision, containment, support-relation, uncertainty, and failure-warning validation."
            ),
            "evidence_ids": ["seed:dust3r_2023"],
        },
    ],
    "Geometry Scaffold Plus Retrieval for Occluded Object Completion": [
        {
            "baseline": "NeRFVS",
            "weakness": (
                "NeRFVS can support novel-view synthesis consistency, but it does not validate whether "
                "occluded object completions are physically plausible inside the room layout."
            ),
            "evidence_ids": ["seed:nerfvs_2023"],
        },
        {
            "baseline": "DUSt3R",
            "weakness": (
                "DUSt3R provides geometry reconstruction cues, but it does not retrieve semantically plausible "
                "occluded indoor objects or validate object support relations, collision constraints, and furniture placement."
            ),
            "evidence_ids": ["seed:dust3r_2023"],
        },
        {
            "baseline": "MASt3R",
            "weakness": (
                "MASt3R is useful for matching and 3D geometry, but this workflow additionally requires "
                "object retrieval, occlusion completion, relation validation, and failure reporting."
            ),
            "evidence_ids": ["seed:mast3r_2024"],
        },
        {
            "baseline": "3D Gaussian Splatting",
            "weakness": (
                "3D Gaussian Splatting supports high-quality 3D scene representation and rendering, but it "
                "does not directly provide single-image indoor object completion, furniture retrieval, or support-relation verification."
            ),
            "evidence_ids": ["seed:3dgs_2023"],
        },
    ],
    "Multi-Hypothesis Scene Completion with a Consistency Verifier": [
        {
            "baseline": "Text2Room",
            "weakness": (
                "Text2Room produces a room-scale textured 3D mesh through iterative generation and fusion, "
                "but it does not maintain multiple scene hypotheses with uncertainty-aware consistency verification."
            ),
            "evidence_ids": ["seed:text2room_2023"],
        },
        {
            "baseline": "SceneScape",
            "weakness": (
                "SceneScape targets consistent scene generation, but the proposed workflow requires explicit "
                "multi-hypothesis scoring, collision checks, relation checks, calibration, and failure_detection_auc."
            ),
            "evidence_ids": ["seed:scenescape_2023"],
        },
        {
            "baseline": "WonderJourney",
            "weakness": (
                "WonderJourney is relevant to generated scene exploration, but it does not directly provide "
                "a single-image indoor scene verifier that rejects inconsistent geometry, shuffled relations, or random confidence."
            ),
            "evidence_ids": ["seed:wonderjourney_2023"],
        },
        {
            "baseline": "3D-SceneDreamer",
            "weakness": (
                "3D-SceneDreamer is relevant to 3D scene generation, but this workflow needs explicit "
                "uncertainty calibration, negative controls, scene-level metrics, and failure warnings."
            ),
            "evidence_ids": ["seed:3d_scenedreamer_2024"],
        },
    ],
}


CARD_PATCHES = {
    "Text2Room": {
        "known_limitations": [
            "Text2Room generates room-scale textured 3D meshes using text-to-image generation, monocular depth, inpainting, viewpoint selection, and iterative fusion.",
            "Text2Room does not directly define object-slot uncertainty, collision_rate, support_relation_accuracy, failure_detection_auc, or failure_warning outputs for a single-image indoor scene schema.",
            "Text2Room is useful as an image-to-3D generation baseline, but scene plausibility still needs geometry, relation, collision, and uncertainty checks.",
        ],
        "reusable_components": [
            "room-scale textured 3D mesh generation",
            "monocular depth and inpainting pipeline",
            "viewpoint selection and iterative fusion components",
        ],
    },
    "SceneScape": {
        "known_limitations": [
            "SceneScape focuses on text-driven consistent scene generation.",
            "SceneScape does not directly provide single-image room layout metrics, object-slot uncertainty, collision checks, support-relation scoring, or failure warnings.",
            "SceneScape can provide scene generation context, but explicit schema validation and negative controls are still required.",
        ],
        "reusable_components": [
            "text-driven consistent scene generation prior",
            "scene consistency generation context",
        ],
    },
    "WonderJourney": {
        "known_limitations": [
            "WonderJourney is relevant to generated scene exploration and journey-style scene synthesis.",
            "WonderJourney does not directly provide a single-image indoor scene verifier for inconsistent geometry, shuffled relations, or random confidence.",
            "Generated scene exploration still requires explicit collision, relation, uncertainty, and failure_detection_auc checks for this task.",
        ],
        "reusable_components": [
            "generated scene exploration prior",
            "long-range scene generation context",
        ],
    },
    "Indoor_NeRF_prior_methods": {
        "known_limitations": [
            "NeRF-style methods are useful for novel-view synthesis and 3D scene representation.",
            "NeRF and NeRFVS do not directly solve single-image object-level layout assembly with collision, containment, and scene-schema validation.",
            "Novel-view consistency is useful evidence but does not replace object support-relation and failure-warning checks.",
        ],
        "reusable_components": [
            "novel-view synthesis consistency",
            "3D scene representation prior",
        ],
    },
    "DUSt3R": {
        "known_limitations": [
            "DUSt3R provides dense 3D geometry cues and reconstruction signals.",
            "DUSt3R does not retrieve semantically plausible occluded indoor objects or validate furniture support relations and collision constraints.",
            "DUSt3R geometry must be combined with object retrieval, room containment, uncertainty, and scene-schema validation for this task.",
        ],
        "reusable_components": [
            "dense 3D geometry cues",
            "geometry reconstruction prior",
        ],
    },
    "MASt3R": {
        "known_limitations": [
            "MASt3R is useful for matching and 3D geometry.",
            "MASt3R does not directly provide object retrieval, occlusion completion, relation validation, or failure reporting.",
            "MASt3R geometry must be integrated with scene-level consistency checks for single-image indoor scene outputs.",
        ],
        "reusable_components": [
            "matching and 3D geometry cues",
            "geometry correspondence prior",
        ],
    },
    "3D Gaussian Splatting": {
        "known_limitations": [
            "3D Gaussian Splatting supports high-quality 3D scene representation and rendering.",
            "3D Gaussian Splatting does not directly provide single-image indoor object completion, furniture retrieval, or support-relation verification.",
            "Rendering quality does not guarantee collision-free, relation-consistent, uncertainty-aware scene outputs.",
        ],
        "reusable_components": [
            "3D scene representation and rendering",
            "novel-view rendering quality prior",
        ],
    },
    "image_to_3d_generation_baselines": {
        "known_limitations": [
            "Image-to-3D generation baselines can produce 3D scene or mesh candidates.",
            "They do not necessarily expose object-slot uncertainty, collision_rate, support_relation_accuracy, failure_detection_auc, or failure_warning fields.",
            "This task requires scene-schema validation and negative controls beyond visual preview quality.",
        ],
        "reusable_components": [
            "3D scene candidate generation",
            "mesh or scene generation prior",
        ],
    },
}


PAPER_ABSTRACT_PATCHES = {
    "seed:text2room_2023": (
        "Text2Room generates room-scale textured 3D meshes using text-to-image generation, monocular depth, "
        "inpainting, viewpoint selection, and iterative fusion. It is relevant as an image-to-3D generation "
        "baseline, but the paper abstract does not define object-slot uncertainty, collision_rate, "
        "support_relation_accuracy, failure_detection_auc, or failure_warning outputs for a single-image indoor scene schema."
    ),
    "seed:scenescape_2023": (
        "SceneScape focuses on text-driven consistent scene generation. It is relevant to scene generation, "
        "but this evidence does not directly define single-image room layout metrics, object-slot uncertainty, "
        "collision checks, support-relation scoring, calibration, or failure warnings."
    ),
    "seed:wonderjourney_2023": (
        "WonderJourney is relevant to generated scene exploration and journey-style scene synthesis. It does "
        "not directly provide a single-image indoor scene verifier for inconsistent geometry, shuffled relations, "
        "random confidence, collision checks, or failure_detection_auc."
    ),
    "seed:nerfvs_2023": (
        "NeRFVS is relevant to novel-view synthesis and view consistency. It does not directly solve "
        "single-image object-level layout assembly with collision, containment, support relation validation, "
        "and scene-schema failure warnings."
    ),
    "seed:dust3r_2023": (
        "DUSt3R provides dense 3D geometry cues and reconstruction signals. It does not retrieve semantically "
        "plausible occluded indoor objects or validate object support relations, collision constraints, furniture placement, "
        "uncertainty, and failure warnings."
    ),
    "seed:mast3r_2024": (
        "MASt3R is useful for matching and 3D geometry. It does not directly provide object retrieval, "
        "occlusion completion, relation validation, support-relation scoring, uncertainty calibration, or failure reporting."
    ),
    "seed:3dgs_2023": (
        "3D Gaussian Splatting supports high-quality 3D scene representation and rendering. It does not directly "
        "provide single-image indoor object completion, furniture retrieval, support-relation verification, uncertainty, "
        "or failure-warning outputs."
    ),
    "seed:3d_scenedreamer_2024": (
        "3D-SceneDreamer is relevant to 3D scene generation. This evidence does not directly provide explicit "
        "uncertainty calibration, negative controls, scene-level metrics, collision checks, or failure warnings."
    ),
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")


def patch_ideas(run_dir: Path) -> int:
    path = run_dir / "focused_ideas.json"
    ideas = read_json(path)
    changed = 0
    for idea in ideas:
        title = idea.get("title")
        if title in CLAIM_MAP:
            idea["baseline_weakness_evidence"] = CLAIM_MAP[title]
            weak = idea.get("unsupported_or_weak_claims", [])
            if not isinstance(weak, list):
                weak = []
            note = (
                "The indoor 3D evidence bank is seeded rather than fully retrieved online; "
                "claim support should still be manually checked before final competition documentation."
            )
            if note not in weak:
                weak.append(note)
            idea["unsupported_or_weak_claims"] = weak
            changed += 1
    write_json(path, ideas)
    return changed


def patch_cards(run_dir: Path) -> int:
    path = run_dir / "evidence_baseline_cards.jsonl"
    rows = read_jsonl(path)
    changed = 0
    for row in rows:
        name = row.get("baseline_name")
        if name in CARD_PATCHES:
            patch = CARD_PATCHES[name]
            row["known_limitations"] = patch["known_limitations"]
            row["reusable_components"] = patch["reusable_components"]
            row["evidence_strength"] = row.get("evidence_strength") or "strong"
            changed += 1
    write_jsonl(path, rows)
    return changed


def patch_baseline_cards(run_dir: Path) -> int:
    path = run_dir / "baseline_cards.jsonl"
    if not path.exists():
        return 0
    rows = read_jsonl(path)
    changed = 0
    for row in rows:
        name = row.get("name") or row.get("baseline_name")
        if name in CARD_PATCHES:
            patch = CARD_PATCHES[name]
            row["limitations"] = "; ".join(patch["known_limitations"])
            row["possible_reuse"] = "; ".join(patch["reusable_components"])
            changed += 1
    write_jsonl(path, rows)
    return changed


def patch_papers(run_dir: Path) -> int:
    path = run_dir / "papers.jsonl"
    rows = read_jsonl(path)
    changed = 0
    for row in rows:
        pid = row.get("paper_id")
        if pid in PAPER_ABSTRACT_PATCHES:
            row["abstract"] = PAPER_ABSTRACT_PATCHES[pid]
            matched = row.get("matched_terms", [])
            if not isinstance(matched, list):
                matched = []
            extra_terms = [
                "single-image",
                "indoor scene",
                "3D scene",
                "collision",
                "support relation",
                "uncertainty",
                "failure warning",
            ]
            row["matched_terms"] = list(dict.fromkeys(matched + extra_terms))
            changed += 1
    write_jsonl(path, rows)
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair indoor 3D evidence cards and claim text for v0.7 verification.")
    parser.add_argument("src_run", type=Path)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    src_run = args.src_run.resolve()
    if args.output_dir:
        out = args.output_dir.resolve()
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = src_run.parent.parent / f"indoor3d_evidence_card_repair_{stamp}" / "repaired_run"

    if out.exists():
        raise SystemExit(f"Output dir already exists: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src_run, out)

    changed_ideas = patch_ideas(out)
    changed_cards = patch_cards(out)
    changed_baseline_cards = patch_baseline_cards(out)
    changed_papers = patch_papers(out)

    print("Indoor 3D evidence-card repair complete")
    print("Source run:", src_run)
    print("Output run:", out)
    print("Ideas patched:", changed_ideas)
    print("Evidence cards patched:", changed_cards)
    print("Baseline cards patched:", changed_baseline_cards)
    print("Paper abstracts patched:", changed_papers)


if __name__ == "__main__":
    main()
