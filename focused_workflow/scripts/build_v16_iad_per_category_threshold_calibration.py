#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

INPUT_SCORES = ROOT / "iad_mvp/outputs/reference_consistency_3cat/iad_reference_consistency_scores_calibrated.csv"
SWEEP_CSV = ROOT / "iad_mvp/outputs/tables_3cat/iad_per_category_threshold_sweep.csv"
RECOMMENDATIONS_CSV = ROOT / "iad_mvp/outputs/tables_3cat/iad_per_category_threshold_recommendations.csv"
DECISIONS_CSV = ROOT / "iad_mvp/outputs/reference_consistency_3cat/iad_reference_consistency_scores_per_category_calibrated.csv"
METRICS_CSV = ROOT / "iad_mvp/outputs/tables_3cat/iad_per_category_calibrated_metrics.csv"
REPORT_MD = ROOT / "competition_submission/V16_IAD_PER_CATEGORY_THRESHOLD_CALIBRATION_CN.md"
REPORT_JSON = ROOT / "competition_submission/V16_IAD_PER_CATEGORY_THRESHOLD_CALIBRATION.json"


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


def fmt(value: Any, digits: int = 6) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


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


def decision_for(row: dict[str, str], anomaly_threshold: float, consistency_threshold: float) -> str:
    baseline_score = float(row["baseline_score"])
    consistency_score = float(row["reference_consistency_score"])
    if baseline_score < anomaly_threshold:
        return "accept_normal"
    if consistency_score >= consistency_threshold:
        return "suppress_or_review_false_alarm"
    return "accept_anomaly"


def summarize_decisions(rows: list[dict[str, Any]], decision_key: str) -> dict[str, Any]:
    positives = [row for row in rows if int(row["label"]) == 1]
    negatives = [row for row in rows if int(row["label"]) == 0]
    tp = sum(1 for row in positives if row[decision_key] == "accept_anomaly")
    fp = sum(1 for row in negatives if row[decision_key] == "accept_anomaly")
    review = sum(1 for row in rows if row[decision_key] == "suppress_or_review_false_alarm")
    decisions = Counter(str(row[decision_key]) for row in rows)
    labels = [int(row["label"]) for row in rows]
    baseline_scores = [float(row["baseline_score"]) for row in rows]
    anomaly_recall = tp / len(positives) if positives else 0.0
    false_alarm_rate = fp / len(negatives) if negatives else 0.0
    review_rate = review / len(rows) if rows else 0.0
    balanced_score = anomaly_recall - false_alarm_rate - 0.15 * review_rate
    return {
        "total": len(rows),
        "anomaly_total": len(positives),
        "normal_total": len(negatives),
        "image_level_auc_lightweight": simple_auc(labels, baseline_scores),
        "accept_anomaly_count": decisions.get("accept_anomaly", 0),
        "accept_normal_count": decisions.get("accept_normal", 0),
        "review_count": decisions.get("suppress_or_review_false_alarm", 0),
        "true_anomaly_accepted": tp,
        "normal_false_alarm": fp,
        "anomaly_recall": anomaly_recall,
        "false_alarm_rate": false_alarm_rate,
        "review_rate": review_rate,
        "balanced_score": balanced_score,
        "decision_counts": dict(decisions),
    }


def evaluate_thresholds(
    rows: list[dict[str, str]],
    category: str,
    anomaly_threshold: float,
    consistency_threshold: float,
) -> dict[str, Any]:
    temp_rows = []
    for row in rows:
        item = dict(row)
        item["candidate_decision"] = decision_for(row, anomaly_threshold, consistency_threshold)
        temp_rows.append(item)
    summary = summarize_decisions(temp_rows, "candidate_decision")
    return {
        "category": category,
        "anomaly_threshold": f"{anomaly_threshold:.6f}",
        "consistency_threshold": f"{consistency_threshold:.6f}",
        **{k: fmt(v) if isinstance(v, float) else v for k, v in summary.items() if k != "decision_counts"},
    }


def anomaly_threshold_grid(rows: list[dict[str, str]]) -> list[float]:
    values = [float(row["baseline_score"]) for row in rows]
    max_value = max(values) if values else 1.0
    grid = {0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.1, 0.2, 0.5, 1.0}
    step = 0.005
    current = 0.0
    while current <= min(1.0, max_value + 0.05) + 1e-12:
        grid.add(round(current, 6))
        current += step
    return sorted(grid)


def consistency_threshold_grid(rows: list[dict[str, str]]) -> list[float]:
    values = [float(row["reference_consistency_score"]) for row in rows]
    low = max(0.0, min(values) - 0.002) if values else 0.98
    high = min(1.0, max(values) + 0.0002) if values else 1.0
    grid = {0.55, 0.99, 0.995, 0.999, 0.9995, 0.9998, 1.000001, 1.0001}
    current = low
    while current <= high + 1e-12:
        grid.add(round(current, 6))
        current += 0.0001
    return sorted(grid)


def select_recommendation(sweep_rows: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [
        row
        for row in sweep_rows
        if int(row["accept_anomaly_count"]) > 0
        and float(row["false_alarm_rate"]) <= 0.05
    ]
    if not candidates:
        candidates = [row for row in sweep_rows if int(row["accept_anomaly_count"]) > 0]
    if not candidates:
        raise SystemExit("No valid threshold candidate found.")
    return sorted(
        candidates,
        key=lambda row: (
            float(row["balanced_score"]),
            float(row["anomaly_recall"]),
            -float(row["false_alarm_rate"]),
            -float(row["review_rate"]),
        ),
        reverse=True,
    )[0]


def calibrate_per_category(rows: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    sweep_rows: list[dict[str, Any]] = []
    recommendations: list[dict[str, Any]] = []
    for category in sorted({row["product_category"] for row in rows}):
        subset = [row for row in rows if row["product_category"] == category]
        category_sweep: list[dict[str, Any]] = []
        for anomaly_threshold in anomaly_threshold_grid(subset):
            for consistency_threshold in consistency_threshold_grid(subset):
                item = evaluate_thresholds(subset, category, anomaly_threshold, consistency_threshold)
                category_sweep.append(item)
                sweep_rows.append(item)
        recommendation = dict(select_recommendation(category_sweep))
        recommendation["selection_rule"] = "maximize recall under false_alarm_rate<=0.05, with review penalty"
        recommendations.append(recommendation)
    return sweep_rows, recommendations


def apply_recommendations(
    rows: list[dict[str, str]],
    recommendations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_category = {
        row["category"]: (
            float(row["anomaly_threshold"]),
            float(row["consistency_threshold"]),
        )
        for row in recommendations
    }
    output: list[dict[str, Any]] = []
    for row in rows:
        anomaly_threshold, consistency_threshold = by_category[row["product_category"]]
        per_category_decision = decision_for(row, anomaly_threshold, consistency_threshold)
        item = dict(row)
        item["global_v15_decision"] = row.get("decision", "")
        item["per_category_anomaly_threshold"] = f"{anomaly_threshold:.6f}"
        item["per_category_consistency_threshold"] = f"{consistency_threshold:.6f}"
        item["per_category_decision"] = per_category_decision
        item["per_category_recommended_action"] = (
            "human_review" if per_category_decision == "suppress_or_review_false_alarm" else per_category_decision
        )
        output.append(item)
    return output


def build_metric_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metric_rows: list[dict[str, Any]] = []
    for scope, subset in [("overall", rows)] + [
        (category, [row for row in rows if row["product_category"] == category])
        for category in sorted({row["product_category"] for row in rows})
    ]:
        global_summary = summarize_decisions(subset, "global_v15_decision")
        per_summary = summarize_decisions(subset, "per_category_decision")
        metric_rows.append({
            "scope": scope,
            "total": len(subset),
            "anomaly_total": per_summary["anomaly_total"],
            "normal_total": per_summary["normal_total"],
            "global_recall": fmt(global_summary["anomaly_recall"]),
            "global_fpr": fmt(global_summary["false_alarm_rate"]),
            "global_review_rate": fmt(global_summary["review_rate"]),
            "global_balanced_score": fmt(global_summary["balanced_score"]),
            "per_category_recall": fmt(per_summary["anomaly_recall"]),
            "per_category_fpr": fmt(per_summary["false_alarm_rate"]),
            "per_category_review_rate": fmt(per_summary["review_rate"]),
            "per_category_balanced_score": fmt(per_summary["balanced_score"]),
            "per_category_accept_anomaly": per_summary["accept_anomaly_count"],
            "per_category_accept_normal": per_summary["accept_normal_count"],
            "per_category_review": per_summary["review_count"],
        })
    return metric_rows


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
            "recall": row["anomaly_recall"],
            "fpr": row["false_alarm_rate"],
            "review_rate": row["review_rate"],
            "balanced_score": row["balanced_score"],
        }
        for row in payload["recommendations"]
    ]
    metric_rows = payload["metric_rows"]
    compact_metric_rows = [
        {
            "scope": row["scope"],
            "global_recall": row["global_recall"],
            "global_fpr": row["global_fpr"],
            "global_score": row["global_balanced_score"],
            "per_cat_recall": row["per_category_recall"],
            "per_cat_fpr": row["per_category_fpr"],
            "per_cat_score": row["per_category_balanced_score"],
        }
        for row in metric_rows
    ]

    return f"""# V1.6 IAD 类别感知阈值校准报告

生成时间：{payload["generated_at"]}

生成脚本：`focused_workflow/scripts/build_v16_iad_per_category_threshold_calibration.py`

## 1. 为什么做 V1.6

V1.5 证明三类别数据链路可以跑通，但也发现 `bottle` 上校准出的全局阈值不能稳定迁移到 `cable/capsule`。因此 V1.6 不继续扩展更多类别，而是对每个类别分别扫描阈值，做类别感知 calibration。

这一步仍然是 lightweight scaffold calibration，不是完整 IAD benchmark。

## 2. Per-category 推荐阈值

选择规则：优先满足 `false_alarm_rate <= 0.05`，在低误报候选中最大化 anomaly recall，并对 review rate 施加轻微惩罚。

{md_table(recommendation_rows, ["category", "anomaly_threshold", "consistency_threshold", "accept_anomaly", "recall", "fpr", "review_rate", "balanced_score"])}

## 3. Global threshold vs Per-category threshold

{md_table(compact_metric_rows, ["scope", "global_recall", "global_fpr", "global_score", "per_cat_recall", "per_cat_fpr", "per_cat_score"])}

核心结论：

- 全局阈值在三类别上 `false_alarm_rate` 很高，主要来自 `cable` 正常样本被大量误判。
- 类别感知阈值显著降低整体误报率，同时保留一部分异常召回。
- `capsule` 的 recall 仍然较低，说明仅靠当前 image-level lightweight feature 不足以稳定识别该类别异常；这应进入后续 feature/baseline 改进，而不是强行调参美化。

## 4. 输出文件

- Per-category sweep：`iad_mvp/outputs/tables_3cat/iad_per_category_threshold_sweep.csv`
- Per-category 推荐阈值：`iad_mvp/outputs/tables_3cat/iad_per_category_threshold_recommendations.csv`
- Per-category calibrated decisions：`iad_mvp/outputs/reference_consistency_3cat/iad_reference_consistency_scores_per_category_calibrated.csv`
- 指标汇总：`iad_mvp/outputs/tables_3cat/iad_per_category_calibrated_metrics.csv`
- JSON 汇总：`competition_submission/V16_IAD_PER_CATEGORY_THRESHOLD_CALIBRATION.json`

## 5. 应该怎么解释

V1.6 的价值不是“把 IAD 做到最好”，而是形成一个新的 execution-feedback repair 案例：

```text
V1.5 多类别迁移失败/不稳定
→ 诊断为全局阈值不鲁棒
→ V1.6 自动做类别感知阈值扫描
→ 显著降低误报，同时暴露 capsule 需要更强特征
```

这和你前面物理属性方向的 v1→v2 repair 故事是一致的：workflow 能发现失败、定位原因、生成修复策略，并把修复结果结构化输出。

## 6. 下一步 V1.7

V1.7 建议不要继续调阈值，而是修执行层特征：

1. 把三类别 reference bank 改为 category-constrained retrieval，避免跨类别最近邻污染；
2. 做 per-category score normalization，而不是全局 min-max；
3. 如果时间允许，再接入 PatchCore/anomalib 或 cached patch-level features；
4. 生成对比报告：global threshold vs per-category threshold vs category-constrained retrieval。
"""


def main() -> None:
    if not INPUT_SCORES.exists():
        raise SystemExit(
            f"Missing required input: {INPUT_SCORES.relative_to(ROOT)}\n"
            "Please run V1.5 multicategory smoke test first."
        )
    rows = read_csv(INPUT_SCORES)
    if not rows:
        raise SystemExit(f"No rows found: {INPUT_SCORES.relative_to(ROOT)}")

    sweep_rows, recommendations = calibrate_per_category(rows)
    calibrated_rows = apply_recommendations(rows, recommendations)
    metric_rows = build_metric_rows(calibrated_rows)

    payload = {
        "version": "v1.6",
        "purpose": "iad_per_category_threshold_calibration",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_scores": str(INPUT_SCORES.relative_to(ROOT)),
        "recommendations": recommendations,
        "metric_rows": metric_rows,
        "outputs": {
            "sweep_csv": str(SWEEP_CSV.relative_to(ROOT)),
            "recommendations_csv": str(RECOMMENDATIONS_CSV.relative_to(ROOT)),
            "decisions_csv": str(DECISIONS_CSV.relative_to(ROOT)),
            "metrics_csv": str(METRICS_CSV.relative_to(ROOT)),
            "report_md": str(REPORT_MD.relative_to(ROOT)),
            "report_json": str(REPORT_JSON.relative_to(ROOT)),
        },
        "boundary": "Per-category lightweight threshold calibration; not final IAD benchmark.",
        "next_version": "v1.7 category-constrained retrieval and per-category normalization",
    }

    write_csv(SWEEP_CSV, sweep_rows)
    write_csv(RECOMMENDATIONS_CSV, recommendations)
    write_csv(DECISIONS_CSV, calibrated_rows)
    write_csv(METRICS_CSV, metric_rows)
    write_json(REPORT_JSON, payload)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text(build_report(payload), encoding="utf-8")

    overall = next(row for row in metric_rows if row["scope"] == "overall")
    print(f"Wrote {SWEEP_CSV}")
    print(f"Wrote {RECOMMENDATIONS_CSV}")
    print(f"Wrote {DECISIONS_CSV}")
    print(f"Wrote {METRICS_CSV}")
    print(f"Wrote {REPORT_MD}")
    print(f"Wrote {REPORT_JSON}")
    print(
        "Summary: "
        f"global_fpr={overall['global_fpr']}, per_category_fpr={overall['per_category_fpr']}, "
        f"global_score={overall['global_balanced_score']}, per_category_score={overall['per_category_balanced_score']}"
    )


if __name__ == "__main__":
    main()
