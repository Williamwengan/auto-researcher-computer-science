#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build v1.2 IAD MVP script scaffold.

V1.2 starts engineering, but only as a minimal scaffold. It creates small,
inspectable scripts for the highest-priority execution plan:
exec_05_iad_reference_consistency_mvp.

The generated scripts are intentionally lightweight. They can run with a small
MVTec-style split once data is provided, but they do not claim PatchCore SOTA or
full industrial deployment.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[2]
IAD_DIR = ROOT / "iad_mvp"
SCRIPT_DIR = IAD_DIR / "scripts"
SUBMISSION_DIR = ROOT / "competition_submission"


FILES = {
    "common_iad.py": r'''
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
''',
    "prepare_iad_reference_manifest.py": r'''
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
''',
    "build_reference_bank.py": r'''
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
''',
    "run_iad_baselines.py": r'''
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
''',
    "score_reference_consistency.py": r'''
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
''',
    "run_iad_negative_controls.py": r'''
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
from pathlib import Path

from common_iad import read_csv, write_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Run lightweight negative controls for IAD reference consistency.")
    parser.add_argument("--scores", type=Path, default=Path("iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv"))
    parser.add_argument("--output", type=Path, default=Path("iad_mvp/outputs/tables/iad_negative_control_report.csv"))
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    if not args.scores.exists():
        raise SystemExit(f"Missing score file: {args.scores}")
    rows = read_csv(args.scores)
    if not rows:
        raise SystemExit("No score rows found.")
    random.seed(args.seed)

    full_accepts = sum(1 for row in rows if row.get("decision") == "accept_anomaly")
    random_accepts = sum(1 for row in rows if random.random() > 0.5)
    shuffled_accepts = sum(1 for row in rows if float(row.get("baseline_score", 0.0)) > 0.5)
    contaminated_accepts = max(0, full_accepts - max(1, len(rows) // 10))

    report = [
        {"control": "full_reference_consistency", "accepted_anomaly_count": full_accepts, "note": "actual scaffold decision"},
        {"control": "random_retrieval", "accepted_anomaly_count": random_accepts, "note": "randomized decision baseline"},
        {"control": "shuffled_provenance", "accepted_anomaly_count": shuffled_accepts, "note": "baseline-score-only proxy"},
        {"control": "contaminated_normal_bank_proxy", "accepted_anomaly_count": contaminated_accepts, "note": "simulated reduced confidence"},
    ]
    write_csv(args.output, report)
    print(f"Saved: {args.output}")
    print("Note: controls are lightweight proxies; real contaminated-bank construction belongs to v1.3+.")


if __name__ == "__main__":
    main()
''',
    "evaluate_iad_agent.py": r'''
#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common_iad import read_csv, simple_auc, write_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate lightweight IAD agent scaffold outputs.")
    parser.add_argument("--baseline", type=Path, default=Path("iad_mvp/outputs/patchcore_baseline/iad_baseline_scores.csv"))
    parser.add_argument("--scores", type=Path, default=Path("iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv"))
    parser.add_argument("--output_dir", type=Path, default=Path("iad_mvp/outputs/tables"))
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args()

    if not args.baseline.exists():
        raise SystemExit(f"Missing baseline score file: {args.baseline}")
    if not args.scores.exists():
        raise SystemExit(f"Missing reference consistency score file: {args.scores}")

    baseline_rows = read_csv(args.baseline)
    score_rows = read_csv(args.scores)
    labels = [int(row["label"]) for row in baseline_rows]
    baseline_scores = [float(row["baseline_score"]) for row in baseline_rows]
    auc = simple_auc(labels, baseline_scores)

    normal_rows = [row for row in score_rows if int(row["label"]) == 0]
    baseline_false_alarms = sum(1 for row in normal_rows if float(row["baseline_score"]) >= args.threshold)
    agent_false_alarms = sum(1 for row in normal_rows if row["decision"] == "accept_anomaly")
    if baseline_false_alarms:
        false_alarm_reduction = (baseline_false_alarms - agent_false_alarms) / baseline_false_alarms
    else:
        false_alarm_reduction = 0.0

    evidence_grounding = sum(1 for row in score_rows if row.get("nearest_reference_image_path")) / len(score_rows)
    tool_success_rate = sum(1 for row in score_rows if row.get("decision")) / len(score_rows)
    summary_rows = [{
        "image_level_auc_lightweight": "" if auc is None else f"{auc:.6f}",
        "baseline_false_alarms_at_threshold": baseline_false_alarms,
        "agent_false_alarms_at_threshold": agent_false_alarms,
        "false_alarm_reduction_proxy": f"{false_alarm_reduction:.6f}",
        "evidence_grounding_score_proxy": f"{evidence_grounding:.6f}",
        "tool_success_rate": f"{tool_success_rate:.6f}",
        "note": "scaffold metrics; not final benchmark results",
    }]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / "iad_agent_execution_metrics.csv"
    md_path = args.output_dir / "iad_agent_execution_summary.md"
    write_csv(csv_path, summary_rows)
    md_path.write_text(
        "# IAD Agent Execution Summary (Scaffold)\\n\\n"
        "This file is generated by the v1.2 scaffold. It is not a final benchmark report.\\n\\n"
        + "\\n".join(f"- {key}: {value}" for key, value in summary_rows[0].items())
        + "\\n",
        encoding="utf-8",
    )
    print(f"Saved: {csv_path}")
    print(f"Saved: {md_path}")


if __name__ == "__main__":
    main()
''',
}


def normalize_script(text: str) -> str:
    return dedent(text).strip() + "\n"


def write_files() -> list[Path]:
    SCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, content in FILES.items():
        path = SCRIPT_DIR / name
        path.write_text(normalize_script(content), encoding="utf-8")
        path.chmod(0o755)
        written.append(path)
    return written


def write_report(written: list[Path]) -> Path:
    report_path = SUBMISSION_DIR / "V12_IAD_MVP_SCRIPT_SCAFFOLD_CN.md"
    rows = "\n".join(f"| `{path.relative_to(ROOT)}` | v1.2 scaffold |" for path in written)
    report = f"""# V1.2 IAD MVP Script Scaffold

生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

生成脚本：`focused_workflow/scripts/build_v12_iad_mvp_scaffold.py`

## 为什么做 V1.2

V1.1 已经把 final research plans 拆成 experiment execution plans。V1.2 开始进入工程，但只做最小脚本骨架，不跑真实 benchmark，不声明实验结果。

本阶段选择 IAD execution plan 作为第一个工程脚手架，原因是它已有 `iad_mvp/` 目录，数据结构和指标最标准，后续最容易用 MVTec AD / VisA 小子集跑通。

注意：这只是执行优先级，不代表项目变成只做 IAD。项目主线仍然是跨任务科研 idea generation workflow。

## 本阶段生成脚本

| 文件 | 作用 |
| --- | --- |
{rows}

## 推荐运行顺序

如果你已经有 MVTec AD 数据集：

```bash
python iad_mvp/scripts/check_env.py --mvtec_root /path/to/mvtec_anomaly_detection
python iad_mvp/scripts/prepare_mvtec_subset.py --mvtec_root /path/to/mvtec_anomaly_detection --categories bottle --output iad_mvp/data/mvtec_split.json
python iad_mvp/scripts/prepare_iad_reference_manifest.py --split iad_mvp/data/mvtec_split.json --output iad_mvp/data/iad_reference_manifest.jsonl
python iad_mvp/scripts/build_reference_bank.py --manifest iad_mvp/data/iad_reference_manifest.jsonl --output_dir iad_mvp/data
python iad_mvp/scripts/run_iad_baselines.py --manifest iad_mvp/data/iad_reference_manifest.jsonl --reference_bank iad_mvp/data/iad_reference_bank.npz --output_dir iad_mvp/outputs/patchcore_baseline
python iad_mvp/scripts/score_reference_consistency.py --manifest iad_mvp/data/iad_reference_manifest.jsonl --baseline iad_mvp/outputs/patchcore_baseline/iad_baseline_scores.csv --reference_bank iad_mvp/data/iad_reference_bank.npz --reference_index iad_mvp/data/iad_reference_index.jsonl --output iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv
python iad_mvp/scripts/run_iad_negative_controls.py --scores iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv --output iad_mvp/outputs/tables/iad_negative_control_report.csv
python iad_mvp/scripts/evaluate_iad_agent.py --baseline iad_mvp/outputs/patchcore_baseline/iad_baseline_scores.csv --scores iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv --output_dir iad_mvp/outputs/tables
```

## 当前边界

- `run_iad_baselines.py` 是 lightweight nearest-reference baseline，不是完整 PatchCore 复现。
- 负控制是轻量 proxy，不是完整 contaminated normal bank 实验。
- 如果没有 MVTec AD / VisA 数据，本阶段只能检查 `--help` 和脚本结构。
- 真实 benchmark 结果属于 v1.3 或后续阶段。
"""
    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    return report_path


def write_manifest(written: list[Path], report_path: Path) -> Path:
    manifest_path = SUBMISSION_DIR / "V12_IAD_MVP_SCRIPT_SCAFFOLD.json"
    payload = {
        "version": "v1.2",
        "purpose": "iad_mvp_script_scaffold",
        "generated_files": [str(path.relative_to(ROOT)) for path in written],
        "report": str(report_path.relative_to(ROOT)),
        "boundary": "Lightweight scaffold only; no real benchmark result is claimed.",
    }
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest_path


def main() -> None:
    written = write_files()
    report_path = write_report(written)
    manifest_path = write_manifest(written, report_path)
    print("V1.2 IAD MVP scaffold written:")
    for path in written:
        print(f"- {path}")
    print(f"- report: {report_path}")
    print(f"- manifest: {manifest_path}")


if __name__ == "__main__":
    main()
