#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

MVTEC_SPLIT = ROOT / "iad_mvp/data/mvtec_split.json"
IAD_MANIFEST = ROOT / "iad_mvp/data/iad_reference_manifest.jsonl"
REFERENCE_BANK = ROOT / "iad_mvp/data/iad_reference_bank.npz"
REFERENCE_INDEX = ROOT / "iad_mvp/data/iad_reference_index.jsonl"
BASELINE_SCORES = ROOT / "iad_mvp/outputs/patchcore_baseline/iad_baseline_scores.csv"
REFERENCE_CONSISTENCY = ROOT / "iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv"
METRICS = ROOT / "iad_mvp/outputs/tables/iad_agent_execution_metrics.csv"
NEGATIVE_CONTROLS = ROOT / "iad_mvp/outputs/tables/iad_negative_control_report.csv"

REPORT_MD = ROOT / "competition_submission/V13_IAD_DATA_READINESS_AND_SMOKE_TEST_CN.md"
REPORT_JSON = ROOT / "competition_submission/V13_IAD_DATA_READINESS_AND_SMOKE_TEST.json"


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


def require(path: Path) -> None:
    if not path.exists():
        raise SystemExit(
            f"Missing required input: {path.relative_to(ROOT)}\n"
            "Please run the V1.2 IAD smoke-test command chain first."
        )


def count_split(split: dict[str, Any]) -> dict[str, Any]:
    categories: dict[str, Any] = {}
    total_train_good = 0
    total_test = 0
    total_masks = 0
    for category, item in split.get("categories", {}).items():
        train_good = len(item.get("train_good", []))
        test_by_type = {name: len(paths) for name, paths in item.get("test", {}).items()}
        mask_by_type = {name: len(paths) for name, paths in item.get("ground_truth", {}).items()}
        test_total = sum(test_by_type.values())
        mask_total = sum(mask_by_type.values())
        categories[category] = {
            "train_good": train_good,
            "test_total": test_total,
            "mask_total": mask_total,
            "test_by_defect_type": test_by_type,
            "mask_by_defect_type": mask_by_type,
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
    by_split = Counter(str(row.get("split", "")) for row in rows)
    by_label = Counter(str(row.get("label", "")) for row in rows)
    by_category = Counter(str(row.get("product_category", "")) for row in rows)
    references = sum(1 for row in rows if row.get("is_reference"))
    with_masks = sum(1 for row in rows if row.get("mask_path"))
    return {
        "rows": len(rows),
        "by_split": dict(by_split),
        "by_label": dict(by_label),
        "by_category": dict(by_category),
        "reference_rows": references,
        "rows_with_masks": with_masks,
    }


def summarize_scores(rows: list[dict[str, str]]) -> dict[str, Any]:
    decisions = Counter(row.get("decision", "") for row in rows)
    labels = Counter(row.get("label", "") for row in rows)
    defect_types = Counter(row.get("defect_type", "") for row in rows)
    grounded = sum(1 for row in rows if row.get("nearest_reference_image_path"))
    warnings = Counter(row.get("failure_warning", "") for row in rows if row.get("failure_warning"))
    return {
        "rows": len(rows),
        "decisions": dict(decisions),
        "labels": dict(labels),
        "defect_types": dict(defect_types),
        "evidence_grounded_rows": grounded,
        "failure_warnings": dict(warnings),
    }


def pipeline_status() -> list[dict[str, str]]:
    files = [
        ("MVTec split", MVTEC_SPLIT),
        ("IAD manifest", IAD_MANIFEST),
        ("Reference bank", REFERENCE_BANK),
        ("Reference index", REFERENCE_INDEX),
        ("Lightweight baseline scores", BASELINE_SCORES),
        ("Reference consistency scores", REFERENCE_CONSISTENCY),
        ("Execution metrics", METRICS),
        ("Negative control report", NEGATIVE_CONTROLS),
    ]
    return [
        {
            "step": name,
            "file": str(path.relative_to(ROOT)),
            "status": "exists" if path.exists() else "missing",
        }
        for name, path in files
    ]


def md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(str(row.get(col, "")) for col in columns) + " |")
    return "\n".join([header, sep, *body])


def build_report(payload: dict[str, Any]) -> str:
    split_summary = payload["split_summary"]
    manifest_summary = payload["manifest_summary"]
    score_summary = payload["reference_consistency_summary"]
    metrics = payload["metrics"][0] if payload["metrics"] else {}
    controls = payload["negative_controls"]
    categories = split_summary["categories"]
    category_names = ", ".join(categories.keys()) or "N/A"

    category_rows = [
        {
            "category": name,
            "train_good": item["train_good"],
            "test_total": item["test_total"],
            "mask_total": item["mask_total"],
        }
        for name, item in categories.items()
    ]

    status_rows = payload["pipeline_status"]
    control_rows = [
        {
            "control": row.get("control", ""),
            "accepted_anomaly_count": row.get("accepted_anomaly_count", ""),
            "note": row.get("note", ""),
        }
        for row in controls
    ]

    decision_rows = [
        {"decision": decision or "(empty)", "count": count}
        for decision, count in score_summary["decisions"].items()
    ]

    return f"""# V1.3 IAD 数据接入与 Smoke Test 报告

生成时间：{payload["generated_at"]}

生成脚本：`focused_workflow/scripts/build_v13_iad_smoke_test_report.py`

## 1. 本阶段目标

V1.3 的目标不是证明 IAD 算法达到 SOTA，而是证明从 V1.0/V1.1 产出的最终研究方案已经可以接入真实数据，并完整产出实验中间文件和评价表格。

本次使用 MVTec AD 数据集中的 `{category_names}` 类别做最小 smoke test。该阶段结果应被表述为“真实数据接入与可执行性验证”，不能表述为正式 benchmark 结论。

## 2. 数据接入情况

- MVTec root: `{split_summary["mvtec_root"]}`
- 使用类别：`{category_names}`
- train good 总数：{split_summary["total_train_good"]}
- test 总数：{split_summary["total_test"]}
- ground-truth mask 总数：{split_summary["total_masks"]}

{md_table(category_rows, ["category", "train_good", "test_total", "mask_total"])}

## 3. Pipeline 产物检查

{md_table(status_rows, ["step", "status", "file"])}

## 4. Manifest 与覆盖情况

- Manifest rows: {manifest_summary["rows"]}
- Split counts: {manifest_summary["by_split"]}
- Label counts: {manifest_summary["by_label"]}
- Reference rows: {manifest_summary["reference_rows"]}
- Rows with masks: {manifest_summary["rows_with_masks"]}
- Baseline score rows: {payload["baseline_rows"]}
- Reference consistency rows: {score_summary["rows"]}

## 5. Smoke Test 指标

当前指标来自 lightweight nearest-reference scaffold，不是完整 PatchCore/anomalib benchmark。

- image_level_auc_lightweight: {metrics.get("image_level_auc_lightweight", "")}
- baseline_false_alarms_at_threshold: {metrics.get("baseline_false_alarms_at_threshold", "")}
- agent_false_alarms_at_threshold: {metrics.get("agent_false_alarms_at_threshold", "")}
- false_alarm_reduction_proxy: {metrics.get("false_alarm_reduction_proxy", "")}
- evidence_grounding_score_proxy: {metrics.get("evidence_grounding_score_proxy", "")}
- tool_success_rate: {metrics.get("tool_success_rate", "")}

## 6. Reference Consistency 决策分布

{md_table(decision_rows, ["decision", "count"])}

解释：如果 `accept_anomaly` 数量过低，不能解释为系统已经完美过滤异常；更合理的解释是当前 scaffold 的 consistency 阈值和决策逻辑偏保守。V1.4 需要进行阈值校准，并引入更强 baseline 或更细粒度 patch-level 特征。

## 7. 负控制结果

{md_table(control_rows, ["control", "accepted_anomaly_count", "note"])}

负控制目前仍是 proxy 版本，用来检查流程是否能生成对照表，不代表完整 contaminated-normal-bank 实验已经完成。

## 8. 当前可以得出的结论

1. MVTec AD 数据已经成功接入当前项目目录。
2. `bottle` 类别 smoke test 已经跑通，包含 split、manifest、reference bank、baseline score、reference consistency、negative control 和 execution metrics。
3. 当前 workflow 已经从“研究方案文本”推进到“真实数据可执行性验证”。
4. 当前结果不能被写成正式 IAD benchmark，因为 baseline 是 lightweight nearest-reference scaffold，不是完整 PatchCore/PaDiM/WinCLIP/anomalib 复现。

## 9. 下一步 V1.4 建议

V1.4 不应该再写泛泛报告，而应该解决当前 smoke test 暴露出的工程问题：

1. 校准 `anomaly_threshold` 和 `consistency_threshold`，避免 reference-consistency 过度 suppress anomaly。
2. 把 lightweight image-level feature 替换为更合理的 patch-level feature 或接入 cached PatchCore/anomalib 分数。
3. 从 `bottle` 扩展到 3 个类别，例如 `bottle`、`cable`、`capsule`。
4. 输出正式一点的多类别表格：image-level AUROC、false alarm proxy、evidence grounding、tool success rate、negative control gap。
5. 保持边界说明：这是 workflow execution validation，不是单独发明一个 IAD SOTA 算法。
"""


def main() -> None:
    for path in [
        MVTEC_SPLIT,
        IAD_MANIFEST,
        REFERENCE_BANK,
        REFERENCE_INDEX,
        BASELINE_SCORES,
        REFERENCE_CONSISTENCY,
        METRICS,
        NEGATIVE_CONTROLS,
    ]:
        require(path)

    split = read_json(MVTEC_SPLIT)
    manifest_rows = read_jsonl(IAD_MANIFEST)
    baseline_rows = read_csv(BASELINE_SCORES)
    reference_consistency_rows = read_csv(REFERENCE_CONSISTENCY)
    metric_rows = read_csv(METRICS)
    negative_control_rows = read_csv(NEGATIVE_CONTROLS)

    payload = {
        "version": "v1.3",
        "purpose": "iad_data_readiness_and_smoke_test",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "inputs": {
            "mvtec_split": str(MVTEC_SPLIT.relative_to(ROOT)),
            "iad_manifest": str(IAD_MANIFEST.relative_to(ROOT)),
            "reference_bank": str(REFERENCE_BANK.relative_to(ROOT)),
            "reference_index": str(REFERENCE_INDEX.relative_to(ROOT)),
            "baseline_scores": str(BASELINE_SCORES.relative_to(ROOT)),
            "reference_consistency": str(REFERENCE_CONSISTENCY.relative_to(ROOT)),
            "metrics": str(METRICS.relative_to(ROOT)),
            "negative_controls": str(NEGATIVE_CONTROLS.relative_to(ROOT)),
        },
        "split_summary": count_split(split),
        "manifest_summary": summarize_manifest(manifest_rows),
        "baseline_rows": len(baseline_rows),
        "reference_consistency_summary": summarize_scores(reference_consistency_rows),
        "metrics": metric_rows,
        "negative_controls": negative_control_rows,
        "pipeline_status": pipeline_status(),
        "boundary": "Smoke test only; lightweight scaffold metrics are not final benchmark results.",
        "next_version": "v1.4 threshold calibration and stronger baseline/multi-category expansion",
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_MD.write_text(build_report(payload), encoding="utf-8")

    print(f"Wrote {REPORT_MD}")
    print(f"Wrote {REPORT_JSON}")
    print(
        "Summary: "
        f"categories={','.join(payload['split_summary']['categories'].keys())}, "
        f"train_good={payload['split_summary']['total_train_good']}, "
        f"test={payload['split_summary']['total_test']}, "
        f"metrics_auc={metric_rows[0].get('image_level_auc_lightweight', '') if metric_rows else ''}"
    )


if __name__ == "__main__":
    main()
