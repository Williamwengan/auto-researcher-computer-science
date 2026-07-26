#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common_iad import image_feature, read_jsonl, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a lightweight normal-reference feature bank.")
    parser.add_argument("--manifest", type=Path, default=Path("iad_mvp/data/iad_reference_manifest.jsonl"))
    parser.add_argument("--output_dir", type=Path, default=Path("iad_mvp/data"))
    parser.add_argument("--feature_size", type=int, default=16)
    args = parser.parse_args()

    if not args.manifest.exists():
        raise SystemExit(f"Missing manifest: {args.manifest}")

    np, _ = __import__("common_iad").try_import_image_stack()
    rows = read_jsonl(args.manifest)
    refs = [row for row in rows if row.get("split") == "train" and int(row.get("label", 0)) == 0]
    if not refs:
        raise SystemExit("No train normal reference rows found.")

    features = []
    index_rows = []
    for idx, row in enumerate(refs):
        path = Path(row["image_path"])
        if not path.exists():
            raise SystemExit(f"Missing reference image: {path}")
        features.append(image_feature(path, size=args.feature_size))
        index_rows.append({
            "reference_id": f"ref_{idx:06d}",
            "image_id": row["image_id"],
            "product_category": row["product_category"],
            "image_path": row["image_path"],
            "provenance": row.get("provenance", "train_normal"),
        })

    args.output_dir.mkdir(parents=True, exist_ok=True)
    bank_path = args.output_dir / "iad_reference_bank.npz"
    index_path = args.output_dir / "iad_reference_index.jsonl"
    np.savez_compressed(bank_path, features=np.stack(features), image_ids=np.array([r["image_id"] for r in refs]))
    write_jsonl(index_path, index_rows)
    print(f"Saved: {bank_path}")
    print(f"Saved: {index_path}")
    print(f"References: {len(index_rows)}")


if __name__ == "__main__":
    main()
