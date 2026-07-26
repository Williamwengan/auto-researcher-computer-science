#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def images_in(path: Path) -> list[str]:
    if not path.exists():
        return []
    return sorted(str(p) for p in path.rglob("*") if p.suffix.lower() in IMAGE_EXTS)


def build_split(root: Path, categories: list[str]) -> dict:
    split = {"mvtec_root": str(root), "categories": {}}
    for cat in categories:
        cdir = root / cat
        if not cdir.exists():
            raise FileNotFoundError(f"Missing category: {cdir}")
        train_good = images_in(cdir / "train" / "good")
        tests = {}
        for sub in sorted((cdir / "test").iterdir()) if (cdir / "test").exists() else []:
            if sub.is_dir():
                tests[sub.name] = images_in(sub)
        masks = {}
        gt_root = cdir / "ground_truth"
        if gt_root.exists():
            for sub in sorted(gt_root.iterdir()):
                if sub.is_dir():
                    masks[sub.name] = images_in(sub)
        split["categories"][cat] = {
            "train_good": train_good,
            "test": tests,
            "ground_truth": masks,
        }
    return split


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a small MVTec split manifest for IAD MVP.")
    parser.add_argument("--mvtec_root", type=Path, required=True)
    parser.add_argument("--categories", nargs="+", required=True)
    parser.add_argument("--output", type=Path, default=Path("iad_mvp/data/mvtec_split.json"))
    args = parser.parse_args()

    split = build_split(args.mvtec_root, args.categories)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(split, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Saved: {args.output}")
    for cat, item in split["categories"].items():
        n_test = sum(len(v) for v in item["test"].values())
        n_mask = sum(len(v) for v in item["ground_truth"].values())
        print(f"{cat}: train_good={len(item['train_good'])}, test={n_test}, masks={n_mask}")


if __name__ == "__main__":
    main()
