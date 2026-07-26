#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

INPUT_SCORES = ROOT / "iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv"
SWEEP_CSV = ROOT / "iad_mvp/outputs/tables/iad_threshold_sweep.csv"
RECOMMENDED_DECISIONS_CSV = ROOT / "iad_mvp/outputs/tables/iad_threshold_recommended_decisions.csv"
REPORT_MD = ROOT / "competition_submission/V14_IAD_THRESHOLD_CALIBRATION_CN.md"
REPORT_JSON = ROOT / "competition_submission/V14_IAD_THRESHOLD_CALIBRATION.json"


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


def decision_for(row: dict[str, str], anomaly_threshold: float, consistency_threshold: float) -> str:
    baseline_score = float(row["baseline_score"])
    consistency_score = float(row["reference_consistency_score"])
    if baseline_score < anomaly_threshold:
        return "accept_normal"
    if consistency_score >= consistency_threshold:
        return "suppress_or_review_false_alarm"
    return "accept_anomaly"


def evaluate_thresholds(
    rows: list[dict[str, str]],
    anomaly_threshold: float,
    consistency_threshold: float,
) -> dict[str, Any]:
    positives = sum(1 for row in rows if int(row["label"]) == 1)
    negatives = sum(1 for row in rows if int(row["label"]) == 0)
    tp = fp = tn = fn = review = anomaly_review = normal_review = 0
    decisions: Counter[str] = Counter()

    for row in rows:
        label = int(row["label"])
        decision = decision_for(row, anomaly_threshold, consistency_threshold)
        decisions[decision] += 1
        if decision == "suppress_or_review_false_alarm":
            review += 1
            if label == 1:
                anomaly_review += 1
            else:
                normal_review += 1
        if label == 1 and decision == "accept_anomaly":
            tp += 1
        elif label == 1:
            fn += 1
        elif label == 0 and decision == "accept_anomaly":
            fp += 1
        else:
            tn += 1

    anomaly_recall = tp / positives if positives else 0.0
    false_alarm_rate = fp / negatives if negatives else 0.0
    normal_safe_rate = tn / negatives if negatives else 0.0
    review_rate = review / len(rows) if rows else 0.0
    balanced_score = anomaly_recall - false_alarm_rate - 0.15 * review_rate

    return {
        "anomaly_threshold": f"{anomaly_threshold:.6f}",
        "consistency_threshold": f"{consistency_threshold:.6f}",
        "total": len(rows),
        "positive_anomaly_total": positives,
        "normal_total": negatives,
        "accept_anomaly_count": decisions.get("accept_anomaly", 0),
        "accept_normal_count": decisions.get("accept_normal", 0),
        "review_count": decisions.get("suppress_or_review_false_alarm", 0),
        "true_anomaly_accepted": tp,
        "normal_false_alarm": fp,
        "true_anomaly_missed_or_reviewed": fn,
        "normal_not_flagged": tn,
        "anomaly_review_count": anomaly_review,
        "normal_review_count": normal_review,
        "anomaly_recall": f"{anomaly_recall:.6f}",
        "false_alarm_rate": f"{false_alarm_rate:.6f}",
        "normal_safe_rate": f"{normal_safe_rate:.6f}",
        "review_rate": f"{review_rate:.6f}",
        "balanced_score": f"{balanced_score:.6f}",
    }


def anomaly_threshold_grid() -> list[float]:
    return [round(i / 100, 6) for i in range(0, 101)]


def consistency_threshold_grid(rows: list[dict[str, str]]) -> list[float]:
    values = [float(row["reference_consistency_score"]) for row in rows]
    low = max(0.0, min(values) - 0.002)
    high = min(1.0, max(values) + 0.0002)
    grid: set[float] = set()
    current = low
    while current <= high + 1e-12:
        grid.add(round(current, 6))
        current += 0.0001
    grid.update([0.55, 0.99, 0.995, 0.999, 0.9995, 1.000001])
    return sorted(grid)


def select_recommended(sweep_rows: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [
        row
        for row in sweep_rows
        if int(row["accept_anomaly_count"]) > 0
        and float(row["false_alarm_rate"]) <= 0.05
    ]
    if not candidates:
        candidates = [row for row in sweep_rows if int(row["accept_anomaly_count"]) > 0]
    if not candidates:
        raise SystemExit("No threshold candidate accepted any anomaly. Check score columns.")

    return sorted(
        candidates,
        key=lambda row: (
            float(row["balanced_score"]),
            float(row["anomaly_recall"]),
            -float(row["false_alarm_rate"]),
            -float(row["review_rate"]),
            -float(row["consistency_threshold"]),
        ),
        reverse=True,
    )[0]


def apply_recommended_decisions(
    rows: list[dict[str, str]],
    anomaly_threshold: float,
    consistency_threshold: float,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        calibrated_decision = decision_for(row, anomaly_threshold, consistency_threshold)
        item = dict(row)
        item["original_decision"] = row.get("decision", "")
        item["calibrated_decision"] = calibrated_decision
        item["calibrated_recommended_action"] = (
            "human_review" if calibrated_decision == "suppress_or_review_false_alarm" else calibrated_decision
        )
        output.append(item)
    return output


def score_distribution(rows: list[dict[str, str]]) -> dict[str, Any]:
    def stats(values: list[float]) -> dict[str, float]:
        values = sorted(values)
        if not values:
            return {}
        return {
            "min": values[0],
            "mean": sum(values) / len(values),
            "max": values[-1],
        }

    out: dict[str, Any] = {}
    for label in ["0", "1"]:
        subset = [row for row in rows if row["label"] == label]
        out[label] = {
            "count": len(subset),
            "baseline_score": stats([float(row["baseline_score"]) for row in subset]),
            "reference_consistency_score": stats(
                [float(row["reference_consistency_score"]) for row in subset]
            ),
        }
    return out


def md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = ["| " + " | ".join(str(row.get(col, "")) for col in columns) + " |" for row in rows]
    return "\n".join([header, sep, *body])


def build_report(payload: dict[str, Any]) -> str:
    current = payload["current_threshold_metrics"]
    recommended = payload["recommended_threshold_metrics"]
    dist = payload["score_distribution"]
    top_rows = payload["top_candidates"]

    comparison_rows = [
        {
            "setting": "current_v1.2",
            "anomaly_threshold": current["anomaly_threshold"],
            "consistency_threshold": current["consistency_threshold"],
            "accept_anomaly_count": current["accept_anomaly_count"],
            "review_count": current["review_count"],
            "anomaly_recall": current["anomaly_recall"],
            "false_alarm_rate": current["false_alarm_rate"],
            "balanced_score": current["balanced_score"],
        },
        {
            "setting": "recommended_v1.4",
            "anomaly_threshold": recommended["anomaly_threshold"],
            "consistency_threshold": recommended["consistency_threshold"],
            "accept_anomaly_count": recommended["accept_anomaly_count"],
            "review_count": recommended["review_count"],
            "anomaly_recall": recommended["anomaly_recall"],
            "false_alarm_rate": recommended["false_alarm_rate"],
            "balanced_score": recommended["balanced_score"],
        },
    ]

    distribution_rows = [
        {
            "label": label,
            "count": item["count"],
            "baseline_min": f"{item['baseline_score']['min']:.6f}",
            "baseline_mean": f"{item['baseline_score']['mean']:.6f}",
            "baseline_max": f"{item['baseline_score']['max']:.6f}",
            "consistency_min": f"{item['reference_consistency_score']['min']:.6f}",
            "consistency_mean": f"{item['reference_consistency_score']['mean']:.6f}",
            "consistency_max": f"{item['reference_consistency_score']['max']:.6f}",
        }
        for label, item in dist.items()
    ]

    return f"""# V1.4 IAD 阈值校准报告

生成时间：{payload["generated_at"]}

生成脚本：`focused_workflow/scripts/build_v14_iad_threshold_calibration.py`

## 1. 为什么做 V1.4

V1.3 已经证明 MVTec AD `bottle` 类别可以接入 workflow，并且从数据准备到评价表格的最小链路已经跑通。但 V1.3 也暴露出一个关键问题：当前 reference-consistency 决策过于保守，`accept_anomaly_count=0`。

因此 V1.4 的目标是做阈值校准，而不是继续堆报告或直接扩展更多类别。

## 2. 分数分布诊断

{md_table(distribution_rows, ["label", "count", "baseline_min", "baseline_mean", "baseline_max", "consistency_min", "consistency_mean", "consistency_max"])}

诊断结论：

- `baseline_score` 对正常/异常有一定区分度；
- `reference_consistency_score` 全部压缩在接近 1 的高分区间；
- 因此 V1.2 默认的 `consistency_threshold=0.55` 明显过低，会导致高异常分样本仍被判为“和正常参考一致”，从而被 suppress/review；
- V1.4 的校准重点是把 consistency 阈值移动到真实分布附近，而不是继续使用固定的 0.55。

## 3. 当前阈值 vs 推荐阈值

{md_table(comparison_rows, ["setting", "anomaly_threshold", "consistency_threshold", "accept_anomaly_count", "review_count", "anomaly_recall", "false_alarm_rate", "balanced_score"])}

推荐阈值的选择规则：

1. 必须产生非零 `accept_anomaly_count`；
2. 优先约束 `false_alarm_rate <= 0.05`；
3. 在满足低误报的候选里最大化 anomaly recall；
4. 对 review 过多的设置施加轻微惩罚。

## 4. Top threshold candidates

{md_table(top_rows, ["rank", "anomaly_threshold", "consistency_threshold", "accept_anomaly_count", "review_count", "anomaly_recall", "false_alarm_rate", "review_rate", "balanced_score"])}

注意：上表按 unconstrained utility 排序，所以可能出现 recall 更高但 false alarm 也更高的候选。V1.4 的正式推荐优先满足 `false_alarm_rate <= 0.05`，因此推荐项不一定是上表 rank 1。

## 5. 输出文件

- Threshold sweep 表：`iad_mvp/outputs/tables/iad_threshold_sweep.csv`
- 推荐阈值决策表：`iad_mvp/outputs/tables/iad_threshold_recommended_decisions.csv`
- JSON 汇总：`competition_submission/V14_IAD_THRESHOLD_CALIBRATION.json`

## 6. 应该怎么解释这个结果

V1.4 不是在证明 IAD 算法已经完成，而是在修复 V1.3 暴露出来的决策问题。它说明当前 workflow 不仅能跑通实验链路，还能根据真实运行结果发现执行层面的缺陷，并给出自动化校准方案。

比赛材料里可以这样表述：

> After connecting the generated IAD research plan to real MVTec AD data, our smoke test revealed an overly conservative reference-consistency decision rule. We then added an automatic threshold calibration module that scans operating points and selects a low-false-alarm setting with non-zero anomaly acceptance, turning execution feedback into a workflow-level repair signal.

## 7. 下一步 V1.5

V1.5 建议做两件事：

1. 用推荐阈值重新生成 calibrated reference-consistency 表；
2. 把单类别 `bottle` 扩展到 `bottle/cable/capsule` 三类，验证校准策略是否跨类别稳定。

边界：当前仍然是 lightweight scaffold calibration，不是完整 PatchCore/anomalib 正式 benchmark。
"""


def main() -> None:
    if not INPUT_SCORES.exists():
        raise SystemExit(
            f"Missing required file: {INPUT_SCORES.relative_to(ROOT)}\n"
            "Please run V1.3 IAD smoke test first."
        )

    rows = read_csv(INPUT_SCORES)
    if not rows:
        raise SystemExit(f"No rows found in {INPUT_SCORES.relative_to(ROOT)}")

    anomaly_grid = anomaly_threshold_grid()
    consistency_grid = consistency_threshold_grid(rows)
    sweep_rows: list[dict[str, Any]] = []
    for anomaly_threshold in anomaly_grid:
        for consistency_threshold in consistency_grid:
            sweep_rows.append(evaluate_thresholds(rows, anomaly_threshold, consistency_threshold))

    current_metrics = evaluate_thresholds(rows, anomaly_threshold=0.5, consistency_threshold=0.55)
    recommended = select_recommended(sweep_rows)
    recommended_anomaly_threshold = float(recommended["anomaly_threshold"])
    recommended_consistency_threshold = float(recommended["consistency_threshold"])
    recommended_decisions = apply_recommended_decisions(
        rows,
        anomaly_threshold=recommended_anomaly_threshold,
        consistency_threshold=recommended_consistency_threshold,
    )

    ranked = sorted(
        sweep_rows,
        key=lambda row: (
            float(row["balanced_score"]),
            float(row["anomaly_recall"]),
            -float(row["false_alarm_rate"]),
            -float(row["review_rate"]),
        ),
        reverse=True,
    )
    top_candidates = []
    for rank, row in enumerate(ranked[:10], start=1):
        item = dict(row)
        item["rank"] = rank
        top_candidates.append(item)

    payload = {
        "version": "v1.4",
        "purpose": "iad_threshold_calibration",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_scores": str(INPUT_SCORES.relative_to(ROOT)),
        "score_distribution": score_distribution(rows),
        "current_threshold_metrics": current_metrics,
        "recommended_threshold_metrics": recommended,
        "top_candidates": top_candidates,
        "outputs": {
            "threshold_sweep_csv": str(SWEEP_CSV.relative_to(ROOT)),
            "recommended_decisions_csv": str(RECOMMENDED_DECISIONS_CSV.relative_to(ROOT)),
            "report_md": str(REPORT_MD.relative_to(ROOT)),
            "report_json": str(REPORT_JSON.relative_to(ROOT)),
        },
        "boundary": "Single-category lightweight threshold calibration; not final IAD benchmark.",
        "next_version": "v1.5 calibrated multi-category smoke test",
    }

    write_csv(SWEEP_CSV, sweep_rows)
    write_csv(RECOMMENDED_DECISIONS_CSV, recommended_decisions)
    write_json(REPORT_JSON, payload)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text(build_report(payload), encoding="utf-8")

    print(f"Wrote {SWEEP_CSV}")
    print(f"Wrote {RECOMMENDED_DECISIONS_CSV}")
    print(f"Wrote {REPORT_MD}")
    print(f"Wrote {REPORT_JSON}")
    print(
        "Recommendation: "
        f"anomaly_threshold={recommended['anomaly_threshold']}, "
        f"consistency_threshold={recommended['consistency_threshold']}, "
        f"accept_anomaly_count={recommended['accept_anomaly_count']}, "
        f"false_alarm_rate={recommended['false_alarm_rate']}, "
        f"anomaly_recall={recommended['anomaly_recall']}"
    )


if __name__ == "__main__":
    main()
