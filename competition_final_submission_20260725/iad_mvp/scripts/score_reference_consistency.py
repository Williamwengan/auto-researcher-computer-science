#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common_iad import image_feature, read_csv, read_jsonl, write_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Score reference consistency and produce accept/suppress/escalate decisions.")
    parser.add_argument("--manifest", type=Path, default=Path("iad_mvp/data/iad_reference_manifest.jsonl"))
    parser.add_argument("--baseline", type=Path, default=Path("iad_mvp/outputs/patchcore_baseline/iad_baseline_scores.csv"))
    parser.add_argument("--reference_bank", type=Path, default=Path("iad_mvp/data/iad_reference_bank.npz"))
    parser.add_argument("--reference_index", type=Path, default=Path("iad_mvp/data/iad_reference_index.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv"))
    parser.add_argument("--anomaly_threshold", type=float, default=0.5)
    parser.add_argument("--consistency_threshold", type=float, default=0.55)
    parser.add_argument("--feature_size", type=int, default=16)
    args = parser.parse_args()

    np, _ = __import__("common_iad").try_import_image_stack()
    for path in [args.manifest, args.baseline, args.reference_bank, args.reference_index]:
        if not path.exists():
            raise SystemExit(f"Missing required file: {path}")

    manifest_by_id = {row["image_id"]: row for row in read_jsonl(args.manifest)}
    ref_index = read_jsonl(args.reference_index)
    bank = np.load(args.reference_bank, allow_pickle=True)
    ref_features = bank["features"]
    baseline_rows = read_csv(args.baseline)
    output_rows = []

    for base in baseline_rows:
        row = manifest_by_id[base["image_id"]]
        feature = image_feature(Path(row["image_path"]), size=args.feature_size)
        distances = ((ref_features - feature) ** 2).mean(axis=1)
        nearest_idx = int(distances.argmin())
        raw_distance = float(distances[nearest_idx])
        consistency_score = 1.0 / (1.0 + raw_distance)
        anomaly_score = float(base["baseline_score"])

        if anomaly_score < args.anomaly_threshold:
            decision = "accept_normal"
        elif consistency_score >= args.consistency_threshold:
            decision = "suppress_or_review_false_alarm"
        else:
            decision = "accept_anomaly"

        failure_warning = ""
        if decision == "suppress_or_review_false_alarm":
            failure_warning = "high anomaly score but visually close to normal reference"
        elif decision == "accept_anomaly" and not row.get("mask_path"):
            failure_warning = "accepted anomaly without pixel mask ground truth"

        ref = ref_index[nearest_idx]
        output_rows.append({
            "image_id": row["image_id"],
            "product_category": row["product_category"],
            "label": int(row.get("label", 0)),
            "defect_type": row.get("defect_type", ""),
            "baseline_score": f"{anomaly_score:.6f}",
            "reference_consistency_score": f"{consistency_score:.6f}",
            "nearest_reference_id": ref["reference_id"],
            "nearest_reference_image_path": ref["image_path"],
            "decision": decision,
            "recommended_action": "human_review" if "review" in decision else decision,
            "evidence_grounding_ok": bool(ref.get("image_path")),
            "failure_warning": failure_warning,
        })

    write_csv(args.output, output_rows)
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
