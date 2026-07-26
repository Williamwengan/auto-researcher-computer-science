#!/usr/bin/env python3
"""Build deterministic AAAI-27 planned-run manifests from the frozen protocol."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_DIR = ROOT / "aaai27" / "experiments" / "manifests"
TASKS = {
    "01_physical_property_prediction": {"short": "physical", "evidence_mode": "retrieved"},
    "03_indoor_scene_generation": {"short": "indoor3d", "evidence_mode": "seeded_disclosed"},
    "05_iad_agent_workflow": {"short": "iad", "evidence_mode": "retrieved"},
}
METHODS = [
    "direct_prompt",
    "researcharena",
    "focused_no_repair",
    "focused_generic_refine",
    "focused_full",
]
ABLATIONS = ["full", "no_evidence", "no_repair", "no_consistency_check", "no_claim_verification"]
REPLICATES = [11, 23, 37, 53, 71]


def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main():
    main_rows = []
    for task, meta in TASKS.items():
        for method in METHODS:
            for replicate in REPLICATES:
                main_rows.append(
                    {
                        "evidence_mode": meta["evidence_mode"],
                        "method": method,
                        "replicate_id": replicate,
                        "run_id": f"{meta['short']}_{method}_s{replicate}",
                        "api_seed_sent": False,
                        "status": "planned",
                        "task": task,
                    }
                )

    ablation_rows = []
    for task, meta in TASKS.items():
        for ablation in ABLATIONS:
            for replicate in REPLICATES:
                ablation_rows.append(
                    {
                        "ablation": ablation,
                        "base_method": "focused_full",
                        "evidence_mode": meta["evidence_mode"],
                        "replicate_id": replicate,
                        "run_id": f"{meta['short']}_ablation_{ablation}_s{replicate}",
                        "api_seed_sent": False,
                        "status": "planned",
                        "task": task,
                    }
                )

    write_jsonl(MANIFEST_DIR / "main_experiment_manifest.jsonl", main_rows)
    write_jsonl(MANIFEST_DIR / "ablation_manifest.jsonl", ablation_rows)
    print(f"Wrote main runs: {len(main_rows)}")
    print(f"Wrote ablation runs: {len(ablation_rows)}")


if __name__ == "__main__":
    main()
