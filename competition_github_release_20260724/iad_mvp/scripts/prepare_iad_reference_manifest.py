#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common_iad import read_json, write_jsonl


def match_mask(mask_paths: list[str], image_path: str) -> str | None:
    stem = Path(image_path).stem
    for mask in mask_paths:
        if Path(mask).stem.startswith(stem) or stem.startswith(Path(mask).stem):
            return mask
    return None


def build_manifest(split: dict) -> list[dict]:
    rows: list[dict] = []
    for category, item in split.get("categories", {}).items():
        for idx, image_path in enumerate(item.get("train_good", [])):
            rows.append({
                "image_id": f"{category}_train_good_{idx:05d}",
                "product_category": category,
                "split": "train",
                "label": 0,
                "defect_type": "good",
                "image_path": image_path,
                "mask_path": None,
                "is_reference": True,
                "provenance": "mvtec_train_good",
            })
        for defect_type, images in item.get("test", {}).items():
            mask_paths = item.get("ground_truth", {}).get(defect_type, [])
            label = 0 if defect_type == "good" else 1
            for idx, image_path in enumerate(images):
                rows.append({
                    "image_id": f"{category}_test_{defect_type}_{idx:05d}",
                    "product_category": category,
                    "split": "test",
                    "label": label,
                    "defect_type": defect_type,
                    "image_path": image_path,
                    "mask_path": match_mask(mask_paths, image_path) if label else None,
                    "is_reference": False,
                    "provenance": "mvtec_test",
                })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Build IAD reference/test manifest from iad_mvp/data/mvtec_split.json.")
    parser.add_argument("--split", type=Path, default=Path("iad_mvp/data/mvtec_split.json"))
    parser.add_argument("--output", type=Path, default=Path("iad_mvp/data/iad_reference_manifest.jsonl"))
    args = parser.parse_args()

    if not args.split.exists():
        raise SystemExit(
            f"Missing split file: {args.split}\n"
            "First run: python iad_mvp/scripts/prepare_mvtec_subset.py --mvtec_root DATA_DIR --categories bottle --output iad_mvp/data/mvtec_split.json"
        )
    rows = build_manifest(read_json(args.split))
    if not rows:
        raise SystemExit("No rows generated. Check split categories and image paths.")
    write_jsonl(args.output, rows)
    n_train = sum(1 for row in rows if row["split"] == "train")
    n_test = sum(1 for row in rows if row["split"] == "test")
    print(f"Saved: {args.output}")
    print(f"Rows: {len(rows)} train={n_train} test={n_test}")


if __name__ == "__main__":
    main()
