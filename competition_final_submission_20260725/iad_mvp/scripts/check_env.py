#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def check_mvtec(root: Path) -> dict:
    info = {"root": str(root), "exists": root.exists(), "categories": []}
    if not root.exists():
        return info
    for cat in sorted([p for p in root.iterdir() if p.is_dir()]):
        train_good = cat / "train" / "good"
        test_dir = cat / "test"
        gt_dir = cat / "ground_truth"
        if train_good.exists() and test_dir.exists():
            info["categories"].append({
                "name": cat.name,
                "train_good_images": len(list(train_good.glob("*"))),
                "test_subdirs": sorted([p.name for p in test_dir.iterdir() if p.is_dir()]) if test_dir.exists() else [],
                "has_ground_truth": gt_dir.exists(),
            })
    return info


def main() -> None:
    parser = argparse.ArgumentParser(description="Check environment for IAD MVP.")
    parser.add_argument("--mvtec_root", type=Path, default=None, help="Optional MVTec AD root directory.")
    args = parser.parse_args()

    print("Python:", sys.executable)
    print("Version:", sys.version.replace("\n", " "))

    modules = ["torch", "torchvision", "numpy", "sklearn", "PIL", "cv2", "timm", "scipy", "matplotlib", "pandas", "skimage", "faiss", "anomalib"]
    print("\nModules:")
    for m in modules:
        print(f"  {m}: {'OK' if has_module(m) else 'MISSING'}")

    if has_module("torch"):
        import torch
        print("\nTorch:", torch.__version__)
        print("CUDA available:", torch.cuda.is_available())
        print("CUDA version:", torch.version.cuda)
        print("GPU count:", torch.cuda.device_count())
        for i in range(min(torch.cuda.device_count(), 8)):
            print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")

    if args.mvtec_root:
        print("\nMVTec check:")
        info = check_mvtec(args.mvtec_root)
        print(json.dumps(info, ensure_ascii=False, indent=2))
        if not info["categories"]:
            raise SystemExit("No valid MVTec categories found. Please check --mvtec_root.")


if __name__ == "__main__":
    main()
