#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common_iad import image_feature, minmax_normalize, read_jsonl, write_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a lightweight nearest-reference IAD baseline.")
    parser.add_argument("--manifest", type=Path, default=Path("iad_mvp/data/iad_reference_manifest.jsonl"))
    parser.add_argument("--reference_bank", type=Path, default=Path("iad_mvp/data/iad_reference_bank.npz"))
    parser.add_argument("--output_dir", type=Path, default=Path("iad_mvp/outputs/patchcore_baseline"))
    parser.add_argument("--feature_size", type=int, default=16)
    args = parser.parse_args()

    if not args.manifest.exists():
        raise SystemExit(f"Missing manifest: {args.manifest}")
    if not args.reference_bank.exists():
        raise SystemExit(f"Missing reference bank: {args.reference_bank}")

    np, _ = __import__("common_iad").try_import_image_stack()
    bank = np.load(args.reference_bank, allow_pickle=True)
    ref_features = bank["features"]
    rows = [row for row in read_jsonl(args.manifest) if row.get("split") == "test"]
    if not rows:
        raise SystemExit("No test rows found in manifest.")

    raw_distances = []
    nearest_indices = []
    for row in rows:
        feature = image_feature(Path(row["image_path"]), size=args.feature_size)
        distances = ((ref_features - feature) ** 2).mean(axis=1)
        nearest_idx = int(distances.argmin())
        raw_distances.append(float(distances[nearest_idx]))
        nearest_indices.append(nearest_idx)

    scores = minmax_normalize(raw_distances)
    output_rows = []
    heatmaps = {}
    for row, score, distance, nearest_idx in zip(rows, scores, raw_distances, nearest_indices):
        output_rows.append({
            "image_id": row["image_id"],
            "product_category": row["product_category"],
            "image_path": row["image_path"],
            "label": int(row.get("label", 0)),
            "defect_type": row.get("defect_type", ""),
            "baseline_score": f"{score:.6f}",
            "raw_nearest_distance": f"{distance:.6f}",
            "nearest_reference_index": nearest_idx,
        })
        heatmaps[row["image_id"]] = np.full((16, 16), score, dtype="float32")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    scores_path = args.output_dir / "iad_baseline_scores.csv"
    heatmap_path = args.output_dir / "iad_region_heatmaps.npz"
    write_csv(scores_path, output_rows)
    np.savez_compressed(heatmap_path, **heatmaps)
    print(f"Saved: {scores_path}")
    print(f"Saved: {heatmap_path}")
    print("Note: this is a lightweight nearest-reference baseline, not full PatchCore.")


if __name__ == "__main__":
    main()
