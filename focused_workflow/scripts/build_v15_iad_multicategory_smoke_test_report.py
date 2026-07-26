#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

SPLIT_3CAT = ROOT / "iad_mvp/data/mvtec_split_3cat.json"
MANIFEST_3CAT = ROOT / "iad_mvp/data/iad_reference_manifest_3cat.jsonl"
REFERENCE_BANK_3CAT = ROOT / "iad_mvp/data/3cat/iad_reference_bank.npz"
REFERENCE_INDEX_3CAT = ROOT / "iad_mvp/data/3cat/iad_reference_index.jsonl"
BASELINE_3CAT = ROOT / "iad_mvp/outputs/patchcore_baseline_3cat/iad_baseline_scores.csv"
SCORES_3CAT = ROOT / "iad_mvp/outputs/reference_consistency_3cat/iad_reference_consistency_scores_calibrated.csv"
METRICS_3CAT = ROOT / "iad_mvp/outputs/tables_3cat/iad_agent_execution_metrics.csv"
NEGATIVE_3CAT = ROOT / "iad_mvp/outputs/tables_3cat/iad_negative_control_report_3cat.csv"
V14_JSON = ROOT / "competition_submission/V14_IAD_THRESHOLD_CALIBRATION.json"

REPORT_MD = ROOT / "competition_submission/V15_IAD_MULTICATEGORY_SMOKE_TEST_CN.md"
REPORT_JSON = ROOT / "competition_submission/V15_IAD_MULTICATEGORY_SMOKE_TEST.json"


def require(path: Path) -> None:
    if not path.exists():
        raise SystemExit(
            f"Missing required input: {path.relative_to(ROOT)}\n"
            "Please run the V1.5 three-category smoke-test commands first."
        )


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


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


def stats(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"min": None, "mean": None, "max": None}
    return {
        "min": min(values),
        "mean": sum(values) / len(values),
        "max": max(values),
    }


def summarize_split(split: dict[str, Any]) -> dict[str, Any]:
    categories: dict[str, Any] = {}
    total_train_good = total_test = total_masks = 0
    for category, item in split.get("categories", {}).items():
        train_good = len(item.get("train_good", []))
        test_total = sum(len(paths) for paths in item.get("test", {}).values())
        mask_total = sum(len(paths) for paths in item.get("ground_truth", {}).values())
        categories[category] = {
            "train_good": train_good,
            "test_total": test_total,
            "mask_total": mask_total,
            "test_by_defect_type": {
                name: len(paths) for name, paths in item.get("test", {}).items()
            },
        }
        total_train_good += train_good
        total_test += test_total
        total_masks += mask_total
    return {
        "mvtec_root": split.get("mvtec_root", ""),
        "categories": categories,
        "total_train_good": total_train_good,
        "total_test": total_test,
        "total_masks": total_masks,
    }


def summarize_manifest(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "rows": len(rows),
        "by_split": dict(Counter(str(row.get("split", "")) for row in rows)),
        "by_label": dict(Counter(str(row.get("label", "")) for row in rows)),
        "by_category": dict(Counter(str(row.get("product_category", "")) for row in rows)),
        "reference_rows": sum(1 for row in rows if row.get("is_reference")),
        "rows_with_masks": sum(1 for row in rows if row.get("mask_path")),
    }


def summarize_by_category(score_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for category in sorted({row["product_category"] for row in score_rows}):
        subset = [row for row in score_rows if row["product_category"] == category]
        positives = [row for row in subset if int(row["label"]) == 1]
        negatives = [row for row in subset if int(row["label"]) == 0]
        decisions = Counter(row["decision"] for row in subset)
        tp = sum(1 for row in positives if row["decision"] == "accept_anomaly")
        fp = sum(1 for row in negatives if row["decision"] == "accept_anomaly")
        labels = [int(row["label"]) for row in subset]
        baseline_scores = [float(row["baseline_score"]) for row in subset]
        anomaly_recall = tp / len(positives) if positives else None
        false_alarm_rate = fp / len(negatives) if negatives else None

        label_stats = {}
        for label in ["0", "1"]:
            label_subset = [row for row in subset if row["label"] == label]
            label_stats[label] = {
                "baseline_score": stats([float(row["baseline_score"]) for row in label_subset]),
                "reference_consistency_score": stats(
                    [float(row["reference_consistency_score"]) for row in label_subset]
                ),
            }

        summaries.append({
            "category": category,
            "test_total": len(subset),
            "anomaly_total": len(positives),
            "normal_total": len(negatives),
            "image_level_auc_lightweight": simple_auc(labels, baseline_scores),
            "accept_anomaly_count": decisions.get("accept_anomaly", 0),
            "accept_normal_count": decisions.get("accept_normal", 0),
            "review_count": decisions.get("suppress_or_review_false_alarm", 0),
            "anomaly_recall": anomaly_recall,
            "false_alarm_rate": false_alarm_rate,
            "decision_counts": dict(decisions),
            "score_distribution": label_stats,
        })
    return summaries


def summarize_overall(score_rows: list[dict[str, str]]) -> dict[str, Any]:
    labels = [int(row["label"]) for row in score_rows]
    baseline_scores = [float(row["baseline_score"]) for row in score_rows]
    positives = [row for row in score_rows if int(row["label"]) == 1]
    negatives = [row for row in score_rows if int(row["label"]) == 0]
    tp = sum(1 for row in positives if row["decision"] == "accept_anomaly")
    fp = sum(1 for row in negatives if row["decision"] == "accept_anomaly")
    decisions = Counter(row["decision"] for row in score_rows)
    return {
        "rows": len(score_rows),
        "anomaly_total": len(positives),
        "normal_total": len(negatives),
        "image_level_auc_lightweight": simple_auc(labels, baseline_scores),
        "accept_anomaly_count": decisions.get("accept_anomaly", 0),
        "accept_normal_count": decisions.get("accept_normal", 0),
        "review_count": decisions.get("suppress_or_review_false_alarm", 0),
        "anomaly_recall": tp / len(positives) if positives else None,
        "false_alarm_rate": fp / len(negatives) if negatives else None,
        "decision_counts": dict(decisions),
    }


def fmt(value: Any, digits: int = 6) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = ["| " + " | ".join(str(row.get(col, "")) for col in columns) + " |" for row in rows]
    return "\n".join([header, sep, *body])


def build_report(payload: dict[str, Any]) -> str:
    split = payload["split_summary"]
    manifest = payload["manifest_summary"]
    threshold = payload["applied_threshold"]
    overall = payload["overall_summary"]
    category_rows = [
        {
            "category": category,
            "train_good": item["train_good"],
            "test_total": item["test_total"],
            "mask_total": item["mask_total"],
        }
        for category, item in split["categories"].items()
    ]
    per_category_rows = [
        {
            "category": row["category"],
            "test_total": row["test_total"],
            "anomaly_total": row["anomaly_total"],
            "normal_total": row["normal_total"],
            "auc_lightweight": fmt(row["image_level_auc_lightweight"]),
            "accept_anomaly": row["accept_anomaly_count"],
            "accept_normal": row["accept_normal_count"],
            "review": row["review_count"],
            "anomaly_recall": fmt(row["anomaly_recall"]),
            "false_alarm_rate": fmt(row["false_alarm_rate"]),
        }
        for row in payload["per_category_summary"]
    ]
    control_rows = [
        {
            "control": row.get("control", ""),
            "accepted_anomaly_count": row.get("accepted_anomaly_count", ""),
            "note": row.get("note", ""),
        }
        for row in payload["negative_controls"]
    ]

    return f"""# V1.5 IAD 三类别 Calibrated Smoke Test 报告

生成时间：{payload["generated_at"]}

生成脚本：`focused_workflow/scripts/build_v15_iad_multicategory_smoke_test_report.py`

## 1. 本阶段目标

V1.5 的目标是把 V1.4 在 `bottle` 上得到的校准阈值迁移到 `bottle/cable/capsule` 三个类别，检查单类别校准是否具备跨类别稳定性。

这一步仍然是 lightweight smoke test，不是完整 PatchCore/anomalib benchmark。

## 2. 使用的数据与阈值

- MVTec root: `{split["mvtec_root"]}`
- 类别：`{", ".join(split["categories"].keys())}`
- train good 总数：{split["total_train_good"]}
- test 总数：{split["total_test"]}
- mask 总数：{split["total_masks"]}
- anomaly_threshold: {threshold["anomaly_threshold"]}
- consistency_threshold: {threshold["consistency_threshold"]}

{md_table(category_rows, ["category", "train_good", "test_total", "mask_total"])}

## 3. 产物覆盖情况

- Manifest rows: {manifest["rows"]}
- Split counts: {manifest["by_split"]}
- Label counts: {manifest["by_label"]}
- Reference rows: {manifest["reference_rows"]}
- Rows with masks: {manifest["rows_with_masks"]}
- Baseline rows: {payload["baseline_rows"]}
- Calibrated score rows: {payload["score_rows"]}

## 4. 三类别整体结果

- overall image_level_auc_lightweight: {fmt(overall["image_level_auc_lightweight"])}
- overall anomaly_recall: {fmt(overall["anomaly_recall"])}
- overall false_alarm_rate: {fmt(overall["false_alarm_rate"])}
- accept_anomaly_count: {overall["accept_anomaly_count"]}
- accept_normal_count: {overall["accept_normal_count"]}
- review_count: {overall["review_count"]}

## 5. 按类别结果

{md_table(per_category_rows, ["category", "test_total", "anomaly_total", "normal_total", "auc_lightweight", "accept_anomaly", "accept_normal", "review", "anomaly_recall", "false_alarm_rate"])}

## 6. 关键诊断

V1.5 发现：V1.4 的 `bottle` 阈值不能直接作为跨类别全局阈值使用。

- `bottle`：误报率为 0，但 anomaly recall 下降，说明三类别 reference bank / 全局归一化改变了 bottle 的分数分布。
- `cable`：正常样本也大量被判为异常，说明该类别的正常图像在当前 lightweight feature 下与 reference bank 的距离偏高。
- `capsule`：异常 recall 很低，说明该类别异常在当前 image-level feature 中不够可分。

这说明问题不在 idea generation 本身，而在执行层 scaffold 的特征、归一化和阈值策略。当前最合理的下一步不是继续扩展更多类别，而是做类别感知校准。

## 7. 负控制结果

{md_table(control_rows, ["control", "accepted_anomaly_count", "note"])}

## 8. 当前结论

1. 三类别数据链路已经跑通，说明 workflow 产物可以扩展到多类别真实数据。
2. 单类别 bottle 阈值直接迁移到多类别时不稳定，暴露出执行层 calibration 问题。
3. 这正好补强了项目叙事：workflow 不只是生成研究方案，还能通过真实执行反馈发现和定位实验层缺陷。
4. 不能把 V1.5 写成“多类别 IAD 性能很好”；应该写成“多类别 smoke test 暴露出跨类别校准需求”。

## 9. 下一步 V1.6

V1.6 应该做类别感知校准：

1. 对每个类别分别扫描 `anomaly_threshold` 和 `consistency_threshold`；
2. 输出 per-category recommended thresholds；
3. 重新生成 calibrated decisions；
4. 比较 global threshold 与 per-category threshold；
5. 如果 per-category 明显更稳，再写成 workflow 的 execution-feedback repair 案例。

边界：V1.6 仍然可以保持 lightweight scaffold，不必立刻接入完整 PatchCore。
"""


def main() -> None:
    for path in [
        SPLIT_3CAT,
        MANIFEST_3CAT,
        REFERENCE_BANK_3CAT,
        REFERENCE_INDEX_3CAT,
        BASELINE_3CAT,
        SCORES_3CAT,
        METRICS_3CAT,
        NEGATIVE_3CAT,
        V14_JSON,
    ]:
        require(path)

    split = read_json(SPLIT_3CAT)
    manifest_rows = read_jsonl(MANIFEST_3CAT)
    baseline_rows = read_csv(BASELINE_3CAT)
    score_rows = read_csv(SCORES_3CAT)
    metric_rows = read_csv(METRICS_3CAT)
    negative_rows = read_csv(NEGATIVE_3CAT)
    v14 = read_json(V14_JSON)
    recommended = v14["recommended_threshold_metrics"]

    payload = {
        "version": "v1.5",
        "purpose": "iad_multicategory_calibrated_smoke_test",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "applied_threshold": {
            "source": "V14_IAD_THRESHOLD_CALIBRATION",
            "anomaly_threshold": recommended["anomaly_threshold"],
            "consistency_threshold": recommended["consistency_threshold"],
        },
        "inputs": {
            "split": str(SPLIT_3CAT.relative_to(ROOT)),
            "manifest": str(MANIFEST_3CAT.relative_to(ROOT)),
            "reference_bank": str(REFERENCE_BANK_3CAT.relative_to(ROOT)),
            "reference_index": str(REFERENCE_INDEX_3CAT.relative_to(ROOT)),
            "baseline": str(BASELINE_3CAT.relative_to(ROOT)),
            "scores": str(SCORES_3CAT.relative_to(ROOT)),
            "metrics": str(METRICS_3CAT.relative_to(ROOT)),
            "negative_controls": str(NEGATIVE_3CAT.relative_to(ROOT)),
        },
        "split_summary": summarize_split(split),
        "manifest_summary": summarize_manifest(manifest_rows),
        "baseline_rows": len(baseline_rows),
        "score_rows": len(score_rows),
        "metric_rows": metric_rows,
        "negative_controls": negative_rows,
        "overall_summary": summarize_overall(score_rows),
        "per_category_summary": summarize_by_category(score_rows),
        "boundary": "Three-category lightweight calibrated smoke test; not final IAD benchmark.",
        "next_version": "v1.6 per-category threshold calibration",
    }

    write_json(REPORT_JSON, payload)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text(build_report(payload), encoding="utf-8")

    print(f"Wrote {REPORT_MD}")
    print(f"Wrote {REPORT_JSON}")
    print(
        "Summary: "
        f"categories={','.join(payload['split_summary']['categories'].keys())}, "
        f"test={payload['split_summary']['total_test']}, "
        f"overall_auc={fmt(payload['overall_summary']['image_level_auc_lightweight'])}, "
        f"overall_recall={fmt(payload['overall_summary']['anomaly_recall'])}, "
        f"overall_fpr={fmt(payload['overall_summary']['false_alarm_rate'])}"
    )


if __name__ == "__main__":
    main()
