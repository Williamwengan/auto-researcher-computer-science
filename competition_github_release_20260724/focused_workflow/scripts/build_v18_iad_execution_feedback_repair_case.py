#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

V13 = ROOT / "competition_submission/V13_IAD_DATA_READINESS_AND_SMOKE_TEST.json"
V14 = ROOT / "competition_submission/V14_IAD_THRESHOLD_CALIBRATION.json"
V15 = ROOT / "competition_submission/V15_IAD_MULTICATEGORY_SMOKE_TEST.json"
V16 = ROOT / "competition_submission/V16_IAD_PER_CATEGORY_THRESHOLD_CALIBRATION.json"
V17 = ROOT / "competition_submission/V17_IAD_CATEGORY_CONSTRAINED_RETRIEVAL.json"

REPORT_MD = ROOT / "competition_submission/V18_IAD_EXECUTION_FEEDBACK_REPAIR_CASE_CN.md"
REPORT_JSON = ROOT / "competition_submission/V18_IAD_EXECUTION_FEEDBACK_REPAIR_CASE.json"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Missing required input: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = ["| " + " | ".join(str(row.get(col, "")) for col in columns) + " |" for row in rows]
    return "\n".join([header, sep, *body])


def build_payload() -> dict[str, Any]:
    v13 = read_json(V13)
    v14 = read_json(V14)
    v15 = read_json(V15)
    v16 = read_json(V16)
    v17 = read_json(V17)

    v13_metrics = v13["metrics"][0]
    v14_current = v14["current_threshold_metrics"]
    v14_recommended = v14["recommended_threshold_metrics"]
    v15_overall = v15["overall_summary"]
    v16_overall = next(row for row in v16["metric_rows"] if row["scope"] == "overall")
    v17_overall = next(row for row in v17["metrics"] if row["scope"] == "overall")

    timeline = [
        {
            "version": "V1.3",
            "stage": "真实数据接入与单类别 smoke test",
            "input": "MVTec AD bottle",
            "finding": "链路可以跑通，但 reference-consistency 决策没有接受任何异常。",
            "key_metric": f"AUC={v13_metrics['image_level_auc_lightweight']}; accepted_anomaly=0",
            "repair_or_next": "进入阈值校准，而不是继续跑更多模型。",
        },
        {
            "version": "V1.4",
            "stage": "单类别阈值校准",
            "input": "bottle scores",
            "finding": "默认 consistency_threshold=0.55 明显过低，导致异常被过度 suppress。",
            "key_metric": (
                f"accepted_anomaly {v14_current['accept_anomaly_count']}→"
                f"{v14_recommended['accept_anomaly_count']}; "
                f"recall {v14_current['anomaly_recall']}→{v14_recommended['anomaly_recall']}; "
                f"FPR={v14_recommended['false_alarm_rate']}"
            ),
            "repair_or_next": "用自动 threshold sweep 选择低误报 operating point。",
        },
        {
            "version": "V1.5",
            "stage": "三类别迁移 smoke test",
            "input": "bottle/cable/capsule",
            "finding": "bottle 阈值不能直接作为跨类别全局阈值。",
            "key_metric": (
                f"overall_auc={fmt(v15_overall['image_level_auc_lightweight'])}; "
                f"overall_recall={fmt(v15_overall['anomaly_recall'])}; "
                f"overall_fpr={fmt(v15_overall['false_alarm_rate'])}"
            ),
            "repair_or_next": "定位为全局阈值不鲁棒，进入类别感知校准。",
        },
        {
            "version": "V1.6",
            "stage": "类别感知阈值校准",
            "input": "three-category scores",
            "finding": "per-category threshold 显著降低误报。",
            "key_metric": (
                f"FPR {v16_overall['global_fpr']}→{v16_overall['per_category_fpr']}; "
                f"score {v16_overall['global_balanced_score']}→{v16_overall['per_category_balanced_score']}"
            ),
            "repair_or_next": "保留低误报，同时暴露 capsule 需要更强特征。",
        },
        {
            "version": "V1.7",
            "stage": "类别约束检索与类别内归一化",
            "input": "three-category manifest/reference bank",
            "finding": "修正跨类别 retrieval 和全局归一化后有小幅提升，但瓶颈转向 feature/baseline。",
            "key_metric": (
                f"score {v17_overall['v16_score']}→{v17_overall['v17_score']}; "
                f"FPR {v17_overall['v16_fpr']}→{v17_overall['v17_fpr']}; "
                f"recall={v17_overall['v17_recall']}"
            ),
            "repair_or_next": "停止继续调轻量阈值，下一步可接 patch-level/PatchCore 或收束为案例。",
        },
    ]

    capability_map = [
        {
            "workflow_capability": "研究方案可执行性验证",
            "evidence": "V1.3 接入 MVTec AD 并生成 split/manifest/reference bank/baseline/metrics。",
        },
        {
            "workflow_capability": "执行反馈诊断",
            "evidence": "V1.3 发现 accept_anomaly=0；V1.5 发现全局阈值跨类别失败。",
        },
        {
            "workflow_capability": "自动修复策略生成",
            "evidence": "V1.4 自动 threshold sweep；V1.6 自动 per-category threshold calibration。",
        },
        {
            "workflow_capability": "修复效果量化",
            "evidence": "V1.6 将 overall FPR 从 0.574257 降到 0.009901，balanced score 从 -0.078045 提升到 0.419451。",
        },
        {
            "workflow_capability": "诚实边界识别",
            "evidence": "V1.7 显示类别约束检索只有小幅提升，说明瓶颈进入 lightweight feature 层。",
        },
    ]

    final_metrics = {
        "v13_single_category_auc": v13_metrics["image_level_auc_lightweight"],
        "v14_bottle_accept_anomaly_before": v14_current["accept_anomaly_count"],
        "v14_bottle_accept_anomaly_after": v14_recommended["accept_anomaly_count"],
        "v15_global_threshold_fpr": fmt(v15_overall["false_alarm_rate"]),
        "v16_per_category_fpr": v16_overall["per_category_fpr"],
        "v16_global_to_per_category_score": {
            "before": v16_overall["global_balanced_score"],
            "after": v16_overall["per_category_balanced_score"],
        },
        "v17_score": v17_overall["v17_score"],
        "v17_recall": v17_overall["v17_recall"],
        "v17_fpr": v17_overall["v17_fpr"],
    }

    return {
        "version": "v1.8",
        "purpose": "iad_execution_feedback_repair_case_summary",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "inputs": {
            "v13": str(V13.relative_to(ROOT)),
            "v14": str(V14.relative_to(ROOT)),
            "v15": str(V15.relative_to(ROOT)),
            "v16": str(V16.relative_to(ROOT)),
            "v17": str(V17.relative_to(ROOT)),
        },
        "timeline": timeline,
        "capability_map": capability_map,
        "final_metrics": final_metrics,
        "recommended_next_step": (
            "Use V1.3–V1.7 as an execution-feedback repair case in the workflow report; "
            "only move to PatchCore/anomalib if more engineering depth is required."
        ),
        "boundary": (
            "This is a workflow execution-feedback case based on lightweight IAD scaffold metrics; "
            "it is not a final IAD SOTA or full PatchCore benchmark."
        ),
    }


def build_report(payload: dict[str, Any]) -> str:
    timeline_rows = payload["timeline"]
    capability_rows = payload["capability_map"]
    metrics = payload["final_metrics"]

    return f"""# V1.8 IAD Execution-Feedback Repair Case 总结

生成时间：{payload["generated_at"]}

生成脚本：`focused_workflow/scripts/build_v18_iad_execution_feedback_repair_case.py`

## 1. 这一阶段到底完成了什么

V1.3–V1.7 不是为了把 IAD 做成一个独立 SOTA 算法，而是为了验证我们的科研自动化 workflow 是否能从“生成研究方案”继续走到“真实数据执行反馈”，并在执行失败时自动诊断和修复。

这组实验形成了一个完整闭环：

```text
最终研究方案
→ 接入真实 MVTec AD 数据
→ 运行 lightweight scaffold
→ 发现执行层失败
→ 自动阈值/类别校准
→ 再次评估
→ 输出结构化修复证据
```

## 2. V1.3–V1.7 时间线

{md_table(timeline_rows, ["version", "stage", "input", "finding", "key_metric", "repair_or_next"])}

## 3. 对 workflow 能力的证明

{md_table(capability_rows, ["workflow_capability", "evidence"])}

## 4. 关键指标摘要

- V1.3 单类别 bottle lightweight AUC：{metrics["v13_single_category_auc"]}
- V1.4 bottle accepted anomaly：{metrics["v14_bottle_accept_anomaly_before"]} → {metrics["v14_bottle_accept_anomaly_after"]}
- V1.5 全局阈值三类别 FPR：{metrics["v15_global_threshold_fpr"]}
- V1.6 类别感知阈值三类别 FPR：{metrics["v16_per_category_fpr"]}
- V1.6 balanced score：{metrics["v16_global_to_per_category_score"]["before"]} → {metrics["v16_global_to_per_category_score"]["after"]}
- V1.7 score / recall / FPR：{metrics["v17_score"]} / {metrics["v17_recall"]} / {metrics["v17_fpr"]}

最重要的结果不是某个 IAD 分数，而是这个修复链：

```text
V1.5 global FPR = 0.574257
V1.6 per-category FPR = 0.009901
```

说明 workflow 能把“跨类别阈值不鲁棒”定位出来，并通过类别感知校准显著降低误报。

## 5. 这应该如何写进比赛材料

建议表述：

> We use IAD as an execution-feedback case study, not as a standalone algorithmic endpoint. After the generated research plan was connected to real MVTec AD data, the initial scaffold exposed two failures: overly conservative anomaly acceptance and poor cross-category threshold transfer. The workflow then produced threshold calibration, per-category calibration, and category-constrained retrieval repairs, turning execution feedback into structured workflow-level improvements.

中文表述：

> 我们不是把 IAD 当成唯一比赛方向，而是把它作为自动科研 workflow 的真实执行反馈案例。系统先生成研究方案，再接入 MVTec AD 数据执行，随后自动发现异常接受率为 0、全局阈值跨类别失败等问题，并进一步生成阈值校准、类别感知校准和类别约束检索等修复策略，最终形成可量化的执行反馈闭环。

## 6. 边界与诚实声明

必须保留以下边界：

1. 当前 IAD 实验是 lightweight scaffold，不是完整 PatchCore/anomalib benchmark。
2. 当前结果不能写成 IAD SOTA。
3. V1.7 只有小幅提升，说明下一层瓶颈已经进入 feature/baseline，而不是继续调阈值。
4. 该案例的核心价值是 workflow 能力证明：生成、执行、失败诊断、修复、再评估。

## 7. 下一步建议

现在有两条路：

### 推荐路线：收束总报告

把 V1.8 写入最终 workflow 报告，作为“真实执行反馈闭环案例”。这条最符合你当前项目主线，因为你的主线是 AI 科研自动化工作流，不是单点 IAD 算法。

### 工程增强路线：继续做 V1.9

如果还想增强 IAD 证据，再做：

```text
V1.9：PatchCore/anomalib or patch-level feature integration
```

但这会把工作重心推向 IAD 算法工程，容易偏离“通用科研 workflow”的主线。

我的建议：先做总报告收束，不要继续陷进 IAD。
"""


def main() -> None:
    payload = build_payload()
    write_json(REPORT_JSON, payload)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text(build_report(payload), encoding="utf-8")
    print(f"Wrote {REPORT_MD}")
    print(f"Wrote {REPORT_JSON}")
    print(
        "Summary: "
        f"V15 global FPR={payload['final_metrics']['v15_global_threshold_fpr']}, "
        f"V16 per-category FPR={payload['final_metrics']['v16_per_category_fpr']}, "
        f"V17 score={payload['final_metrics']['v17_score']}"
    )


if __name__ == "__main__":
    main()
