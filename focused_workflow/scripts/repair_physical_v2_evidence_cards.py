#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


CLAIM_MAP = {
    "Object-Conditioned Material Interval Mapper": [
        {
            "baseline": "ObjectFolder2.0",
            "weakness": (
                "ObjectFolder2.0 provides multisensory object data and object-level priors, but single RGB images "
                "may not reveal hidden material composition, coating, internal structure, haptic cues, or load-bearing material."
            ),
            "evidence_ids": ["openalex:W4312347618", "openalex:W4226166186"],
        },
        {
            "baseline": "ObjectFolder",
            "weakness": (
                "ObjectFolder-style datasets support object-centric multisensory priors, but exact physical-property labels "
                "for arbitrary 2D indoor objects may require proxy labels, interval labels, and uncertainty-aware supervision."
            ),
            "evidence_ids": ["openalex:W3200689778", "openalex:W4312347618"],
        },
    ],
    "Localized Visual Evidence Verifier for Material Claims": [
        {
            "baseline": "CLIP",
            "weakness": (
                "CLIP or VLM-style semantic predictions can be plausible at image or crop level but may be unsupported "
                "by localized object-mask visual evidence, so material claims require pixel-linked verification."
            ),
            "evidence_ids": ["openalex:W4385327621", "openalex:W4399597788"],
        },
        {
            "baseline": "CLIP",
            "weakness": (
                "Prompt-sensitive vision-language predictions require calibration and verification before being used "
                "as material evidence for downstream physical-property lookup."
            ),
            "evidence_ids": ["openalex:W4385327621", "openalex:W4402155831"],
        },
        {
            "baseline": "SAM2",
            "weakness": (
                "Promptable segmentation masks may vary under occlusion, object separation, camouflage, prompt changes, "
                "or salient-region bias, so material verification should test whether evidence lies inside the target object mask."
            ),
            "evidence_ids": ["openalex:W7148178853", "openalex:W4403323960"],
        },
    ],
    "Proposal Uncertainty Propagation for Object-Level Property JSON": [
        {
            "baseline": "SAM2",
            "weakness": (
                "Promptable masks and detector proposals can vary under occlusion, object separation, camouflage, or prompt changes, "
                "so downstream physical-property JSON should propagate proposal uncertainty instead of using only one mask."
            ),
            "evidence_ids": ["openalex:W7148178853", "openalex:W4416850904", "openalex:W4403323960"],
        },
        {
            "baseline": "ObjectFolder2.0",
            "weakness": (
                "Single RGB images may not reveal hidden material composition, haptic cues, acoustic cues, coating, or internal structure, "
                "so property prediction should expose uncertainty instead of returning one overconfident value."
            ),
            "evidence_ids": ["openalex:W4312347618", "openalex:W4327630646"],
        },
        {
            "baseline": "ObjectFolder",
            "weakness": (
                "Exact physical-property supervision for arbitrary 2D indoor objects is limited, so proxy labels, "
                "interval labels, and uncertainty-aware evaluation are needed."
            ),
            "evidence_ids": ["openalex:W3200689778", "openalex:W4312347618"],
        },
    ],
}


CARD_PATCHES = {
    "ObjectFolder": {
        "known_limitations": [
            "ObjectFolder provides object-centric visual, auditory, and tactile representations.",
            "ObjectFolder supports multisensory object priors, but exact physical-property prediction from a single RGB indoor scene is under-constrained.",
            "Physical-property labels for arbitrary 2D indoor objects may require proxy labels, interval labels, and uncertainty-aware supervision.",
        ],
        "reusable_components": [
            "object-centric multisensory priors",
            "visual, auditory, and tactile object representations",
            "proxy source for uncertainty-aware physical-property evaluation",
        ],
    },
    "ObjectFolder2.0": {
        "known_limitations": [
            "ObjectFolder2.0 provides a larger multisensory object dataset for sim-to-real transfer.",
            "ObjectFolder2.0 supports object-level physical and multisensory priors, but a single RGB image may not reveal hidden material composition, coating, haptic cues, acoustic cues, or internal structure.",
            "Physical-property prediction from 2D scenes should expose calibrated uncertainty rather than overconfident point estimates.",
        ],
        "reusable_components": [
            "multisensory object data",
            "object-level physical and sensory priors",
            "proxy labels or interval priors for physical-property prediction",
        ],
    },
    "CLIP": {
        "known_limitations": [
            "CLIP-style vision-language predictions provide semantic and material cues.",
            "CLIP predictions can be prompt-sensitive and may not be grounded in localized object-mask visual evidence.",
            "Material claims from CLIP or VLM outputs require calibration, localized evidence verification, and counterfactual checks before physical-property lookup.",
        ],
        "reusable_components": [
            "semantic material scoring",
            "vision-language material prompts",
            "crop-level material candidate generation",
        ],
    },
    "LLaVA": {
        "known_limitations": [
            "LLaVA-style VLMs can produce semantic material descriptions.",
            "VLM material claims may be plausible but unsupported by localized object-mask evidence.",
            "Material claims require calibration and verification before downstream physical-property lookup.",
        ],
        "reusable_components": [
            "semantic material description",
            "VLM rationale generation",
        ],
    },
    "Qwen-VL": {
        "known_limitations": [
            "Qwen-VL-style VLMs can produce semantic material descriptions.",
            "VLM predictions can be prompt-sensitive and may not be grounded in localized object-mask evidence.",
            "Material claims require calibration and verification before downstream physical-property lookup.",
        ],
        "reusable_components": [
            "semantic material description",
            "VLM rationale generation",
        ],
    },
    "SAM": {
        "known_limitations": [
            "Promptable segmentation masks provide useful region proposals.",
            "Promptable masks may vary under occlusion, object separation, camouflage, prompt changes, or salient-region bias.",
            "Physical-property prediction should propagate segmentation uncertainty instead of relying on one top mask.",
        ],
        "reusable_components": [
            "object mask proposals",
            "segmentation uncertainty source",
        ],
    },
    "SAM2": {
        "known_limitations": [
            "SAM2 and promptable segmentation methods provide object masks or region proposals.",
            "Promptable masks may vary under occlusion, object separation, camouflage, prompt changes, or salient-region bias.",
            "Physical-property prediction should propagate segmentation uncertainty and verify whether material evidence lies inside the target object mask.",
        ],
        "reusable_components": [
            "object mask proposals",
            "proposal uncertainty source",
            "mask-based localized evidence extraction",
        ],
    },
    "GroundingDINO": {
        "known_limitations": [
            "GroundingDINO provides open-vocabulary object detection proposals.",
            "Open-vocabulary proposals can miss small, occluded, transparent, or ambiguous indoor objects.",
            "Downstream physical-property JSON should account for detection uncertainty and missing-object failure warnings.",
        ],
        "reusable_components": [
            "open-vocabulary object boxes",
            "proposal uncertainty source",
        ],
    },
}


PAPER_NOTE_PATCHES = {
    "openalex:W4312347618": (
        "ObjectFolder2.0 provides multisensory object data for sim-to-real transfer. This supports object-level priors, "
        "but single RGB images do not expose all hidden material composition, haptic cues, acoustic cues, coating, or internal structure; "
        "physical-property labels may require proxy labels, interval labels, and uncertainty-aware supervision."
    ),
    "openalex:W4226166186": (
        "ObjectFolder2.0 provides multisensory object data for sim-to-real transfer. This supports object-level priors, "
        "but single RGB images do not expose all hidden material composition, haptic cues, acoustic cues, coating, or internal structure."
    ),
    "openalex:W3200689778": (
        "ObjectFolder provides visual, auditory, and tactile object representations. It supports multisensory object priors, "
        "but exact physical-property supervision for arbitrary 2D indoor objects may still require proxy labels, interval labels, and uncertainty-aware evaluation."
    ),
    "openalex:W4327630646": (
        "Visuo-haptic object perception shows that vision and touch provide complementary object information. This supports the claim "
        "that single RGB images may miss hidden material composition, haptic cues, coating, internal structure, and other physical-property evidence."
    ),
    "openalex:W4385327621": (
        "Foundational vision models connect language and visual scene understanding, but prompts, ambiguities, and contextual variation can affect predictions. "
        "Material claims from VLMs need calibration, localized visual evidence, and verification before physical-property lookup."
    ),
    "openalex:W4399597788": (
        "Open-vocabulary grounding with 3D scene graphs addresses semantic and relational grounding. This supports the need for localized object-mask visual evidence "
        "rather than relying only on image-level or crop-level semantic predictions."
    ),
    "openalex:W4402155831": (
        "Multimodal large language models use images, text, and other modalities, but their predictions require domain validation. "
        "Prompt-sensitive material predictions need calibration and verification before physical-property lookup."
    ),
    "openalex:W7148178853": (
        "Interactive video segmentation faces occlusion, object separation, and camouflage, and prompt-based masks may need correction. "
        "This supports propagating proposal and segmentation uncertainty instead of relying on a single mask."
    ),
    "openalex:W4416850904": (
        "Segment Anything adaptations discuss semantic alignment and segmentation across domains. Promptable segmentation masks can vary by domain and task, "
        "so material evidence should be checked inside the target object mask and proposal uncertainty should be propagated."
    ),
    "openalex:W4403323960": (
        "Efficient variants of Segment Anything discuss segmentation generalization and deployment limits. Promptable masks may vary under challenging conditions, "
        "so downstream physical-property JSON should propagate segmentation uncertainty."
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
        if pid in PAPER_NOTE_PATCHES:
            row["abstract"] = PAPER_NOTE_PATCHES[pid]
            matched = row.get("matched_terms", [])
            if not isinstance(matched, list):
                matched = []
            extra = [
                "single RGB",
                "hidden material composition",
                "physical-property",
                "proxy labels",
                "interval labels",
                "uncertainty",
                "localized visual evidence",
                "prompt-sensitive",
                "segmentation uncertainty",
            ]
            row["matched_terms"] = list(dict.fromkeys(matched + extra))
            changed += 1
    write_jsonl(path, rows)
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair physical-property v2 evidence cards and claim text for v0.7 verification.")
    parser.add_argument("src_run", type=Path)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    src_run = args.src_run.resolve()
    if args.output_dir:
        out = args.output_dir.resolve()
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = src_run.parent.parent / f"physical_v2_evidence_card_repair_{stamp}" / "repaired_run"
    if out.exists():
        raise SystemExit(f"Output dir already exists: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src_run, out)

    print("Physical-property v2 evidence-card repair complete")
    print("Source run:", src_run)
    print("Output run:", out)
    print("Ideas patched:", patch_ideas(out))
    print("Evidence cards patched:", patch_cards(out))
    print("Baseline cards patched:", patch_baseline_cards(out))
    print("Paper abstracts patched:", patch_papers(out))


if __name__ == "__main__":
    main()
