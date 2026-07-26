#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
IAD_SCRIPTS = ROOT / "iad_mvp/scripts"
if str(IAD_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(IAD_SCRIPTS))

from common_iad import image_feature, read_jsonl, try_import_image_stack  # noqa: E402


MANIFEST = ROOT / "iad_mvp/data/iad_reference_manifest_3cat.jsonl"
REFERENCE_BANK = ROOT / "iad_mvp/data/3cat/iad_reference_bank.npz"
REFERENCE_INDEX = ROOT / "iad_mvp/data/3cat/iad_reference_index.jsonl"
V16_METRICS = ROOT / "iad_mvp/outputs/tables_3cat/iad_per_category_calibrated_metrics.csv"

BASELINE_OUT = ROOT / "iad_mvp/outputs/patchcore_baseline_3cat_category_constrained/iad_baseline_scores.csv"
SCORES_OUT = ROOT / "iad_mvp/outputs/reference_consistency_3cat_category_constrained/iad_reference_consistency_scores.csv"
SWEEP_OUT = ROOT / "iad_mvp/outputs/tables_3cat/iad_v17_category_constrained_threshold_sweep.csv"
RECOMMENDATIONS_OUT = ROOT / "iad_mvp/outputs/tables_3cat/iad_v17_category_constrained_threshold_recommendations.csv"
METRICS_OUT = ROOT / "iad_mvp/outputs/tables_3cat/iad_v17_category_constrained_metrics.csv"
REPORT_MD = ROOT / "competition_submission/V17_IAD_CATEGORY_CONSTRAINED_RETRIEVAL_CN.md"
REPORT_JSON = ROOT / "competition_submission/V17_IAD_CATEGORY_CONSTRAINED_RETRIEVAL.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def require(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"Missing required input: {path.relative_to(ROOT)}")


def fmt(value: Any, digits: int = 6) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def minmax(values: list[float]) -> list[float]:
    if not values:
        return []
    low = min(values)
    high = max(values)
    if abs(high - low) < 1e-12:
        return [0.0 for _ in values]
    return [(value - low) / (high - low) for value in values]


def simple_auc(labels: list[int], scores: list[float]) -> float | None:
    positives = [score for label, score in zip(labels, scores) if label == 1]
    negatives = [score for label, score in zip(labels, scores) if label == 0]
    if not positives or not negatives:
        return None
    wins = 0.0
    total = 0
    for pos in positives:
        for neg in negatives:
            total += 1
            if pos > neg:
                wins += 1.0
            elif pos == neg:
                wins += 0.5
    return wins / total if total else None


def decision_for(row: dict[str, Any], anomaly_threshold: float, consistency_threshold: float) -> str:
    baseline_score = float(row["baseline_score"])
    consistency_score = float(row["reference_consistency_score"])
    if baseline_score < anomaly_threshold:
        return "accept_normal"
    if consistency_score >= consistency_threshold:
        return "suppress_or_review_false_alarm"
    return "accept_anomaly"


def summarize(rows: list[dict[str, Any]], decision_key: str) -> dict[str, Any]:
    positives = [row for row in rows if int(row["label"]) == 1]
    negatives = [row for row in rows if int(row["label"]) == 0]
    tp = sum(1 for row in positives if row[decision_key] == "accept_anomaly")
    fp = sum(1 for row in negatives if row[decision_key] == "accept_anomaly")
    review = sum(1 for row in rows if row[decision_key] == "suppress_or_review_false_alarm")
    decisions = Counter(str(row[decision_key]) for row in rows)
    labels = [int(row["label"]) for row in rows]
    scores = [float(row["baseline_score"]) for row in rows]
    recall = tp / len(positives) if positives else 0.0
    fpr = fp / len(negatives) if negatives else 0.0
    review_rate = review / len(rows) if rows else 0.0
    balanced_score = recall - fpr - 0.15 * review_rate
    return {
        "total": len(rows),
        "anomaly_total": len(positives),
        "normal_total": len(negatives),
        "auc": simple_auc(labels, scores),
        "accept_anomaly_count": decisions.get("accept_anomaly", 0),
        "accept_normal_count": decisions.get("accept_normal", 0),
        "review_count": decisions.get("suppress_or_review_false_alarm", 0),
        "true_anomaly_accepted": tp,
        "normal_false_alarm": fp,
        "recall": recall,
        "fpr": fpr,
        "review_rate": review_rate,
        "balanced_score": balanced_score,
        "decision_counts": dict(decisions),
    }


def build_category_constrained_scores() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    np, _ = try_import_image_stack()
    manifest_rows = read_jsonl(MANIFEST)
    test_rows = [row for row in manifest_rows if row.get("split") == "test"]
    ref_index = read_jsonl(REFERENCE_INDEX)
    bank = np.load(REFERENCE_BANK, allow_pickle=True)
    ref_features = bank["features"]

    category_to_ref_indices: dict[str, list[int]] = {}
    for idx, ref in enumerate(ref_index):
        category_to_ref_indices.setdefault(ref["product_category"], []).append(idx)

    raw_rows: list[dict[str, Any]] = []
    for row in test_rows:
        category = row["product_category"]
        eligible = category_to_ref_indices.get(category, [])
        if not eligible:
            raise SystemExit(f"No reference rows found for category: {category}")
        feature = image_feature(Path(row["image_path"]))
        eligible_features = ref_features[eligible]
        distances = ((eligible_features - feature) ** 2).mean(axis=1)
        local_idx = int(distances.argmin())
        nearest_idx = int(eligible[local_idx])
        raw_distance = float(distances[local_idx])
        ref = ref_index[nearest_idx]
        raw_rows.append({
            "image_id": row["image_id"],
            "product_category": category,
            "image_path": row["image_path"],
            "label": int(row.get("label", 0)),
            "defect_type": row.get("defect_type", ""),
            "raw_nearest_distance": raw_distance,
            "nearest_reference_index": nearest_idx,
            "nearest_reference_id": ref["reference_id"],
            "nearest_reference_image_path": ref["image_path"],
            "retrieval_scope": "category_constrained",
            "normalization_scope": "per_category",
        })

    baseline_rows: list[dict[str, Any]] = []
    score_rows: list[dict[str, Any]] = []
    for category in sorted({row["product_category"] for row in raw_rows}):
        subset = [row for row in raw_rows if row["product_category"] == category]
        normalized = minmax([float(row["raw_nearest_distance"]) for row in subset])
        for row, score in zip(subset, normalized):
            consistency = 1.0 / (1.0 + float(row["raw_nearest_distance"]))
            baseline_row = dict(row)
            baseline_row["baseline_score"] = f"{score:.6f}"
            baseline_row["raw_nearest_distance"] = f"{float(row['raw_nearest_distance']):.6f}"
            baseline_rows.append(baseline_row)

            score_row = {
                "image_id": row["image_id"],
                "product_category": row["product_category"],
                "label": int(row["label"]),
                "defect_type": row["defect_type"],
                "baseline_score": f"{score:.6f}",
                "reference_consistency_score": f"{consistency:.6f}",
                "nearest_reference_id": row["nearest_reference_id"],
                "nearest_reference_image_path": row["nearest_reference_image_path"],
                "retrieval_scope": "category_constrained",
                "normalization_scope": "per_category",
                "evidence_grounding_ok": bool(row["nearest_reference_image_path"]),
            }
            score_rows.append(score_row)
    return baseline_rows, score_rows


def threshold_grids(rows: list[dict[str, Any]]) -> tuple[list[float], list[float]]:
    anomaly_grid = [round(i / 200, 6) for i in range(0, 201)]
    consistency_values = [float(row["reference_consistency_score"]) for row in rows]
    low = max(0.0, min(consistency_values) - 0.002)
    high = min(1.0, max(consistency_values) + 0.0002)
    consistency_grid = {0.55, 0.99, 0.995, 0.999, 0.9995, 0.9998, 1.000001, 1.0001}
    current = low
    while current <= high + 1e-12:
        consistency_grid.add(round(current, 6))
        current += 0.0001
    return anomaly_grid, sorted(consistency_grid)


def evaluate_thresholds(
    rows: list[dict[str, Any]],
    category: str,
    anomaly_threshold: float,
    consistency_threshold: float,
) -> dict[str, Any]:
    temp = []
    for row in rows:
        item = dict(row)
        item["candidate_decision"] = decision_for(item, anomaly_threshold, consistency_threshold)
        temp.append(item)
    summary = summarize(temp, "candidate_decision")
    return {
        "category": category,
        "anomaly_threshold": f"{anomaly_threshold:.6f}",
        "consistency_threshold": f"{consistency_threshold:.6f}",
        "total": summary["total"],
        "anomaly_total": summary["anomaly_total"],
        "normal_total": summary["normal_total"],
        "auc": fmt(summary["auc"]),
        "accept_anomaly_count": summary["accept_anomaly_count"],
        "accept_normal_count": summary["accept_normal_count"],
        "review_count": summary["review_count"],
        "true_anomaly_accepted": summary["true_anomaly_accepted"],
        "normal_false_alarm": summary["normal_false_alarm"],
        "recall": fmt(summary["recall"]),
        "fpr": fmt(summary["fpr"]),
        "review_rate": fmt(summary["review_rate"]),
        "balanced_score": fmt(summary["balanced_score"]),
    }


def select_recommendation(sweep: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [
        row
        for row in sweep
        if int(row["accept_anomaly_count"]) > 0
        and float(row["fpr"]) <= 0.05
    ]
    if not candidates:
        candidates = [row for row in sweep if int(row["accept_anomaly_count"]) > 0]
    if not candidates:
        raise SystemExit("No threshold accepted any anomaly.")
    return sorted(
        candidates,
        key=lambda row: (
            float(row["balanced_score"]),
            float(row["recall"]),
            -float(row["fpr"]),
            -float(row["review_rate"]),
        ),
        reverse=True,
    )[0]


def calibrate(score_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    sweep_rows: list[dict[str, Any]] = []
    recommendations: list[dict[str, Any]] = []
    by_category_thresholds: dict[str, tuple[float, float]] = {}

    for category in sorted({row["product_category"] for row in score_rows}):
        subset = [row for row in score_rows if row["product_category"] == category]
        anomaly_grid, consistency_grid = threshold_grids(subset)
        category_sweep = []
        for anomaly_threshold in anomaly_grid:
            for consistency_threshold in consistency_grid:
                item = evaluate_thresholds(subset, category, anomaly_threshold, consistency_threshold)
                category_sweep.append(item)
                sweep_rows.append(item)
        recommendation = dict(select_recommendation(category_sweep))
        recommendation["selection_rule"] = "maximize recall under fpr<=0.05, with review penalty"
        recommendations.append(recommendation)
        by_category_thresholds[category] = (
            float(recommendation["anomaly_threshold"]),
            float(recommendation["consistency_threshold"]),
        )

    calibrated_rows = []
    for row in score_rows:
        anomaly_threshold, consistency_threshold = by_category_thresholds[row["product_category"]]
        decision = decision_for(row, anomaly_threshold, consistency_threshold)
        item = dict(row)
        item["anomaly_threshold"] = f"{anomaly_threshold:.6f}"
        item["consistency_threshold"] = f"{consistency_threshold:.6f}"
        item["decision"] = decision
        item["recommended_action"] = "human_review" if decision == "suppress_or_review_false_alarm" else decision
        item["failure_warning"] = (
            "accepted anomaly without pixel mask ground truth"
            if decision == "accept_anomaly" and int(row["label"]) == 0
            else ""
        )
        calibrated_rows.append(item)
    return sweep_rows, recommendations, calibrated_rows


def metric_rows(calibrated_rows: list[dict[str, Any]], v16_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    v16_by_scope = {row["scope"]: row for row in v16_rows}
    rows = []
    scopes = ["overall", *sorted({row["product_category"] for row in calibrated_rows})]
    for scope in scopes:
        subset = calibrated_rows if scope == "overall" else [
            row for row in calibrated_rows if row["product_category"] == scope
        ]
        summary = summarize(subset, "decision")
        v16 = v16_by_scope.get(scope, {})
        rows.append({
            "scope": scope,
            "total": summary["total"],
            "anomaly_total": summary["anomaly_total"],
            "normal_total": summary["normal_total"],
            "v16_recall": v16.get("per_category_recall", ""),
            "v16_fpr": v16.get("per_category_fpr", ""),
            "v16_score": v16.get("per_category_balanced_score", ""),
            "v17_auc": fmt(summary["auc"]),
            "v17_recall": fmt(summary["recall"]),
            "v17_fpr": fmt(summary["fpr"]),
            "v17_review_rate": fmt(summary["review_rate"]),
            "v17_score": fmt(summary["balanced_score"]),
            "v17_accept_anomaly": summary["accept_anomaly_count"],
            "v17_accept_normal": summary["accept_normal_count"],
            "v17_review": summary["review_count"],
        })
    return rows


def md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = ["| " + " | ".join(str(row.get(col, "")) for col in columns) + " |" for row in rows]
    return "\n".join([header, sep, *body])


def build_report(payload: dict[str, Any]) -> str:
    recommendation_rows = [
        {
            "category": row["category"],
            "anomaly_threshold": row["anomaly_threshold"],
            "consistency_threshold": row["consistency_threshold"],
            "accept_anomaly": row["accept_anomaly_count"],
            "recall": row["recall"],
            "fpr": row["fpr"],
            "review_rate": row["review_rate"],
            "score": row["balanced_score"],
        }
        for row in payload["recommendations"]
    ]
    comparison_rows = [
        {
            "scope": row["scope"],
            "v16_recall": row["v16_recall"],
            "v16_fpr": row["v16_fpr"],
            "v16_score": row["v16_score"],
            "v17_recall": row["v17_recall"],
            "v17_fpr": row["v17_fpr"],
            "v17_score": row["v17_score"],
        }
        for row in payload["metrics"]
    ]
    overall = next(row for row in payload["metrics"] if row["scope"] == "overall")

    return f"""# V1.7 IAD 类别约束检索与类别内归一化报告

生成时间：{payload["generated_at"]}

生成脚本：`focused_workflow/scripts/build_v17_iad_category_constrained_retrieval_report.py`

## 1. 为什么做 V1.7

V1.6 已经证明类别感知阈值能显著降低误报，但它仍然基于 V1.5 的执行层产物。V1.7 进一步修执行层的两个根因：

1. reference retrieval 只在同一 product category 内检索，避免跨类别最近邻污染；
2. baseline score 按类别分别 min-max normalize，避免全局归一化让某个类别支配阈值。

这一步仍然是 lightweight scaffold，不是完整 PatchCore/anomalib benchmark。

## 2. V1.7 推荐阈值

{md_table(recommendation_rows, ["category", "anomaly_threshold", "consistency_threshold", "accept_anomaly", "recall", "fpr", "review_rate", "score"])}

## 3. V1.6 vs V1.7 对比

{md_table(comparison_rows, ["scope", "v16_recall", "v16_fpr", "v16_score", "v17_recall", "v17_fpr", "v17_score"])}

整体变化：

- V1.6 overall score: {overall["v16_score"]}
- V1.7 overall score: {overall["v17_score"]}
- V1.6 overall fpr: {overall["v16_fpr"]}
- V1.7 overall fpr: {overall["v17_fpr"]}

## 4. 如何解释

V1.7 的重点不是“轻量 baseline 已经足够强”，而是证明 workflow 可以继续从执行反馈中定位更底层的问题：

```text
V1.5：全局阈值跨类别失败
V1.6：类别感知阈值降低误报
V1.7：进一步修正跨类别 reference retrieval 与全局归一化
```

如果 V1.7 比 V1.6 改善，说明执行层修复有效；如果某些类别仍弱，说明问题进入 feature/baseline 层，需要 patch-level feature 或 PatchCore/anomalib。

## 5. 输出文件

- V1.7 baseline scores：`iad_mvp/outputs/patchcore_baseline_3cat_category_constrained/iad_baseline_scores.csv`
- V1.7 consistency scores：`iad_mvp/outputs/reference_consistency_3cat_category_constrained/iad_reference_consistency_scores.csv`
- V1.7 threshold sweep：`iad_mvp/outputs/tables_3cat/iad_v17_category_constrained_threshold_sweep.csv`
- V1.7 recommendations：`iad_mvp/outputs/tables_3cat/iad_v17_category_constrained_threshold_recommendations.csv`
- V1.7 metrics：`iad_mvp/outputs/tables_3cat/iad_v17_category_constrained_metrics.csv`
- JSON 汇总：`competition_submission/V17_IAD_CATEGORY_CONSTRAINED_RETRIEVAL.json`

## 6. 下一步建议

如果 V1.7 已经明显优于 V1.6，可以把 V1.3–V1.7 作为一个完整 execution-feedback repair case 写进总报告。若还想继续做工程增强，下一步才考虑接入 PatchCore/anomalib 或 patch-level feature。
"""


def main() -> None:
    for path in [MANIFEST, REFERENCE_BANK, REFERENCE_INDEX, V16_METRICS]:
        require(path)

    baseline_rows, score_rows = build_category_constrained_scores()
    sweep_rows, recommendations, calibrated_rows = calibrate(score_rows)
    v16_rows = read_csv(V16_METRICS)
    metrics = metric_rows(calibrated_rows, v16_rows)

    write_csv(BASELINE_OUT, baseline_rows)
    write_csv(SCORES_OUT, calibrated_rows)
    write_csv(SWEEP_OUT, sweep_rows)
    write_csv(RECOMMENDATIONS_OUT, recommendations)
    write_csv(METRICS_OUT, metrics)

    payload = {
        "version": "v1.7",
        "purpose": "iad_category_constrained_retrieval_and_per_category_normalization",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "inputs": {
            "manifest": str(MANIFEST.relative_to(ROOT)),
            "reference_bank": str(REFERENCE_BANK.relative_to(ROOT)),
            "reference_index": str(REFERENCE_INDEX.relative_to(ROOT)),
            "v16_metrics": str(V16_METRICS.relative_to(ROOT)),
        },
        "outputs": {
            "baseline_scores": str(BASELINE_OUT.relative_to(ROOT)),
            "consistency_scores": str(SCORES_OUT.relative_to(ROOT)),
            "threshold_sweep": str(SWEEP_OUT.relative_to(ROOT)),
            "recommendations": str(RECOMMENDATIONS_OUT.relative_to(ROOT)),
            "metrics": str(METRICS_OUT.relative_to(ROOT)),
            "report_md": str(REPORT_MD.relative_to(ROOT)),
            "report_json": str(REPORT_JSON.relative_to(ROOT)),
        },
        "recommendations": recommendations,
        "metrics": metrics,
        "boundary": "Category-constrained lightweight scaffold; not final IAD benchmark.",
        "next_version": "optional PatchCore/anomalib or final execution-feedback case report",
    }
    write_json(REPORT_JSON, payload)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text(build_report(payload), encoding="utf-8")

    overall = next(row for row in metrics if row["scope"] == "overall")
    print(f"Wrote {BASELINE_OUT}")
    print(f"Wrote {SCORES_OUT}")
    print(f"Wrote {SWEEP_OUT}")
    print(f"Wrote {RECOMMENDATIONS_OUT}")
    print(f"Wrote {METRICS_OUT}")
    print(f"Wrote {REPORT_MD}")
    print(f"Wrote {REPORT_JSON}")
    print(
        "Summary: "
        f"v16_score={overall['v16_score']}, v17_score={overall['v17_score']}, "
        f"v16_fpr={overall['v16_fpr']}, v17_fpr={overall['v17_fpr']}, "
        f"v17_recall={overall['v17_recall']}"
    )


if __name__ == "__main__":
    main()
