#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        keys: list[str] = []
        for row in rows:
            for key in row:
                if key not in keys:
                    keys.append(key)
        fieldnames = keys
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require_file(path: Path, message: str | None = None) -> None:
    if not path.exists():
        raise SystemExit(message or f"Missing required file: {path}")


def try_import_image_stack():
    try:
        import numpy as np
        from PIL import Image
    except Exception as exc:
        raise SystemExit(
            "This script needs numpy and Pillow for lightweight image features. "
            "Run iad_mvp/scripts/check_env.py first."
        ) from exc
    return np, Image


def image_feature(path: Path, size: int = 16):
    np, Image = try_import_image_stack()
    try:
        image = Image.open(path).convert("RGB").resize((size, size))
    except Exception as exc:
        raise RuntimeError(f"Could not read image: {path}") from exc
    arr = np.asarray(image, dtype="float32") / 255.0
    return arr.reshape(-1)


def minmax_normalize(values: list[float]) -> list[float]:
    if not values:
        return []
    low = min(values)
    high = max(values)
    if abs(high - low) < 1e-12:
        return [0.0 for _ in values]
    return [(value - low) / (high - low) for value in values]


def simple_auc(labels: list[int], scores: list[float]) -> float | None:
    positives = [(score, label) for score, label in zip(scores, labels) if label == 1]
    negatives = [(score, label) for score, label in zip(scores, labels) if label == 0]
    if not positives or not negatives:
        return None
    wins = 0.0
    total = 0
    for ps, _ in positives:
        for ns, _ in negatives:
            total += 1
            if ps > ns:
                wins += 1.0
            elif ps == ns:
                wins += 0.5
    return wins / total if total else None
