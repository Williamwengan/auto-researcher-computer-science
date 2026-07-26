#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build v1.1 experiment execution plans from v1.0 final research plans.

V1.1 is a planning stage only. It does not implement algorithms, run datasets,
or claim real benchmark results. It converts final research plans into concrete
execution checklists: data tasks, scripts, command templates, outputs, metrics,
validation checks, and failure checks.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List


@dataclass
class ScriptSpec:
    path: str
    purpose: str
    inputs: List[str]
    outputs: List[str]
    command_template: str
    validation_check: str


@dataclass
class ExperimentExecutionPlan:
    execution_plan_id: str
    source_plan_id: str
    task_name: str
    execution_scope: str
    why_this_scope: str
    data_preparation_tasks: List[str]
    scripts_to_implement: List[ScriptSpec]
    commands_to_run: List[str]
    expected_outputs: List[str]
    metrics_to_compute: List[str]
    validation_checks: List[str]
    failure_checks: List[str]
    compute_requirements: str
    manual_decisions_needed: List[str]
    not_in_scope: List[str]
    recommended_execution_priority: str


EXECUTION_PLAN_SCHEMA: Dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "ExperimentExecutionPlan",
    "type": "object",
    "required": [
        "execution_plan_id",
        "source_plan_id",
        "task_name",
        "execution_scope",
        "why_this_scope",
        "data_preparation_tasks",
        "scripts_to_implement",
        "commands_to_run",
        "expected_outputs",
        "metrics_to_compute",
        "validation_checks",
        "failure_checks",
        "compute_requirements",
        "manual_decisions_needed",
        "not_in_scope",
        "recommended_execution_priority",
    ],
    "properties": {
        "execution_plan_id": {"type": "string"},
        "source_plan_id": {"type": "string"},
        "task_name": {"type": "string"},
        "execution_scope": {"type": "string"},
        "why_this_scope": {"type": "string"},
        "data_preparation_tasks": {"type": "array", "items": {"type": "string"}},
        "scripts_to_implement": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["path", "purpose", "inputs", "outputs", "command_template", "validation_check"],
                "properties": {
                    "path": {"type": "string"},
                    "purpose": {"type": "string"},
                    "inputs": {"type": "array", "items": {"type": "string"}},
                    "outputs": {"type": "array", "items": {"type": "string"}},
                    "command_template": {"type": "string"},
                    "validation_check": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
        "commands_to_run": {"type": "array", "items": {"type": "string"}},
        "expected_outputs": {"type": "array", "items": {"type": "string"}},
        "metrics_to_compute": {"type": "array", "items": {"type": "string"}},
        "validation_checks": {"type": "array", "items": {"type": "string"}},
        "failure_checks": {"type": "array", "items": {"type": "string"}},
        "compute_requirements": {"type": "string"},
        "manual_decisions_needed": {"type": "array", "items": {"type": "string"}},
        "not_in_scope": {"type": "array", "items": {"type": "string"}},
        "recommended_execution_priority": {"type": "string"},
    },
    "additionalProperties": False,
}


def make_execution_plans() -> List[ExperimentExecutionPlan]:
    return [
        ExperimentExecutionPlan(
            execution_plan_id="exec_01_physical_property_proxy_interval_mvp",
            source_plan_id="plan_01_physical_property",
            task_name="物理属性预测",
            execution_scope="Proxy-label calibrated interval prediction MVP, not full physical-property SOTA training.",
            why_this_scope=(
                "真实物理属性标签难获取，所以 v1.1 先把执行范围限制在 material table + proxy interval labels + "
                "calibration evaluation。这样能验证 final plan 是否可执行，同时避免陷入大规模标注。"
            ),
            data_preparation_tasks=[
                "选择一个小型 indoor image subset，记录 image_id、object_id、category、mask_or_box 和 material candidates。",
                "整理 material_property_table.csv，至少包含 density、Young's modulus、Poisson ratio、hardness、friction 的 interval ranges 和 provenance。",
                "构建 indoor_property_manifest.jsonl，把每个 object 绑定 category、mask、material candidates 和 proxy interval labels。",
                "准备 shuffled material-property table，作为 negative control。",
            ],
            scripts_to_implement=[
                ScriptSpec(
                    path="scripts/prepare_indoor_property_manifest.py",
                    purpose="从图像/标注/检测结果构建 object-level manifest。",
                    inputs=["raw indoor images", "object masks or boxes", "material candidates"],
                    outputs=["data/indoor_property_manifest.jsonl"],
                    command_template="python scripts/prepare_indoor_property_manifest.py --images DATA_DIR --output data/indoor_property_manifest.jsonl",
                    validation_check="manifest 每行必须包含 image_id、object_id、category、mask_or_box、material_candidates。",
                ),
                ScriptSpec(
                    path="scripts/build_material_property_table.py",
                    purpose="整理材料到物理属性区间的映射表。",
                    inputs=["raw material property sources"],
                    outputs=["data/material_property_table.csv", "data/material_property_table_shuffled.csv"],
                    command_template="python scripts/build_material_property_table.py --output data/material_property_table.csv --make_shuffled_control",
                    validation_check="每个材料至少包含一个物理属性区间和 provenance 字段。",
                ),
                ScriptSpec(
                    path="scripts/predict_property_intervals.py",
                    purpose="根据 object category、material evidence 和属性表输出 calibrated intervals。",
                    inputs=["data/indoor_property_manifest.jsonl", "data/material_property_table.csv"],
                    outputs=["results/physical_property_interval_predictions.csv"],
                    command_template="python scripts/predict_property_intervals.py --manifest data/indoor_property_manifest.jsonl --table data/material_property_table.csv --output results/physical_property_interval_predictions.csv",
                    validation_check="输出必须包含 prediction_interval、confidence、abstain、failure_warning。",
                ),
                ScriptSpec(
                    path="scripts/evaluate_property_intervals.py",
                    purpose="计算 interval coverage、calibration error、selective risk 和 negative control 差异。",
                    inputs=["results/physical_property_interval_predictions.csv", "proxy labels", "shuffled-table predictions"],
                    outputs=["results/physical_property_calibration_table.csv", "results/physical_property_negative_control_report.csv"],
                    command_template="python scripts/evaluate_property_intervals.py --predictions results/physical_property_interval_predictions.csv --output_dir results",
                    validation_check="报告必须包含 coverage、calibration_error、selective_risk 和 shuffled-table control gap。",
                ),
            ],
            commands_to_run=[
                "python scripts/prepare_indoor_property_manifest.py --images DATA_DIR --output data/indoor_property_manifest.jsonl",
                "python scripts/build_material_property_table.py --output data/material_property_table.csv --make_shuffled_control",
                "python scripts/predict_property_intervals.py --manifest data/indoor_property_manifest.jsonl --table data/material_property_table.csv --output results/physical_property_interval_predictions.csv",
                "python scripts/evaluate_property_intervals.py --predictions results/physical_property_interval_predictions.csv --output_dir results",
            ],
            expected_outputs=[
                "data/indoor_property_manifest.jsonl",
                "data/material_property_table.csv",
                "data/material_property_table_shuffled.csv",
                "results/physical_property_interval_predictions.csv",
                "results/physical_property_calibration_table.csv",
                "results/physical_property_negative_control_report.csv",
            ],
            metrics_to_compute=[
                "prediction_interval_coverage",
                "calibration_error",
                "selective_risk",
                "density_log_mae or proxy interval error",
                "negative_control_gap_vs_shuffled_table",
            ],
            validation_checks=[
                "manifest row count > 0 and every row has object_id/category/material_candidates",
                "material table has non-empty interval ranges and provenance",
                "prediction file has one row per object unless abstained with reason",
                "coverage and calibration metrics are computed for accepted predictions",
            ],
            failure_checks=[
                "shuffled table performs within 5% of real table",
                "90% nominal intervals have less than 80% empirical coverage",
                "selective risk does not decrease when confidence threshold increases",
                "many predictions lack provenance or material evidence",
            ],
            compute_requirements="CPU is enough for table/interval MVP; single GPU optional if material candidates are produced by a VLM.",
            manual_decisions_needed=[
                "Which indoor image subset to use first",
                "Which material-property source is acceptable for proxy labels",
                "Whether object masks come from existing labels, SAM2, or manual samples",
                "Which properties are mandatory in the first MVP",
            ],
            not_in_scope=[
                "Full physical-property benchmark training",
                "Claiming true material property ground truth from RGB alone",
                "Large-scale dataset construction",
            ],
            recommended_execution_priority="Medium: scientifically strong, but proxy labels and material tables need careful manual setup.",
        ),
        ExperimentExecutionPlan(
            execution_plan_id="exec_03_indoor3d_scene_graph_verifier_mvp",
            source_plan_id="plan_03_indoor3d",
            task_name="室内单图 3D 场景生成",
            execution_scope="Lightweight scene-graph and geometry-consistency verifier MVP, not full 3D generation training.",
            why_this_scope=(
                "完整单图 3D 生成工程太重。v1.1 先规划一个 verifier MVP，验证 idea 中最核心的 support/collision/relation "
                "检查能否产生可度量输出。这样能保留复杂任务泛化证据，又不把项目拖进大型 3D 系统实现。"
            ),
            data_preparation_tasks=[
                "选择小型 indoor scene subset，准备 input image、visible objects、layout cues 和可用 depth/layout proxy labels。",
                "准备 seeded evidence bank 的披露说明，确保报告中透明标记。",
                "构建 indoor3d_scene_manifest.jsonl，包含 image_id、camera info if available、objects、layout/depth proxy。",
                "准备 random placement 和 shuffled relation negative controls。",
            ],
            scripts_to_implement=[
                ScriptSpec(
                    path="scripts/prepare_indoor3d_scene_manifest.py",
                    purpose="构建室内单图 3D verifier 的输入 manifest。",
                    inputs=["indoor RGB images", "object detections", "layout/depth proxy labels"],
                    outputs=["data/indoor3d_scene_manifest.jsonl"],
                    command_template="python scripts/prepare_indoor3d_scene_manifest.py --images DATA_DIR --output data/indoor3d_scene_manifest.jsonl",
                    validation_check="manifest 必须包含 image_id、visible_objects、layout_cues 和 available_proxy_labels。",
                ),
                ScriptSpec(
                    path="scripts/build_scene_graph_hypotheses.py",
                    purpose="生成 object relation、support relation 和 occluded region hypotheses。",
                    inputs=["data/indoor3d_scene_manifest.jsonl"],
                    outputs=["results/indoor3d_scene_graph_predictions.jsonl"],
                    command_template="python scripts/build_scene_graph_hypotheses.py --manifest data/indoor3d_scene_manifest.jsonl --output results/indoor3d_scene_graph_predictions.jsonl",
                    validation_check="每个 scene 至少输出 objects、relations、support_edges、uncertainty。",
                ),
                ScriptSpec(
                    path="scripts/verify_scene_geometry.py",
                    purpose="检查 collision、support、out-of-room 和 relation consistency。",
                    inputs=["results/indoor3d_scene_graph_predictions.jsonl"],
                    outputs=["results/indoor3d_geometry_consistency_table.csv"],
                    command_template="python scripts/verify_scene_geometry.py --scene_graphs results/indoor3d_scene_graph_predictions.jsonl --output results/indoor3d_geometry_consistency_table.csv",
                    validation_check="输出必须包含 collision_rate、support_relation_score、out_of_room_rate。",
                ),
                ScriptSpec(
                    path="scripts/evaluate_indoor3d_negative_controls.py",
                    purpose="对比 random placement 和 shuffled relation negative controls。",
                    inputs=["results/indoor3d_scene_graph_predictions.jsonl"],
                    outputs=["results/indoor3d_negative_control_report.csv"],
                    command_template="python scripts/evaluate_indoor3d_negative_controls.py --scene_graphs results/indoor3d_scene_graph_predictions.jsonl --output results/indoor3d_negative_control_report.csv",
                    validation_check="negative control 必须显著差于 verifier plan，否则说明 verifier 无效。",
                ),
            ],
            commands_to_run=[
                "python scripts/prepare_indoor3d_scene_manifest.py --images DATA_DIR --output data/indoor3d_scene_manifest.jsonl",
                "python scripts/build_scene_graph_hypotheses.py --manifest data/indoor3d_scene_manifest.jsonl --output results/indoor3d_scene_graph_predictions.jsonl",
                "python scripts/verify_scene_geometry.py --scene_graphs results/indoor3d_scene_graph_predictions.jsonl --output results/indoor3d_geometry_consistency_table.csv",
                "python scripts/evaluate_indoor3d_negative_controls.py --scene_graphs results/indoor3d_scene_graph_predictions.jsonl --output results/indoor3d_negative_control_report.csv",
            ],
            expected_outputs=[
                "data/indoor3d_scene_manifest.jsonl",
                "results/indoor3d_scene_graph_predictions.jsonl",
                "results/indoor3d_geometry_consistency_table.csv",
                "results/indoor3d_negative_control_report.csv",
                "competition_submission/indoor3d_seeded_evidence_disclosure.md",
            ],
            metrics_to_compute=[
                "support_relation_accuracy or proxy score",
                "collision_rate",
                "out_of_room_rate",
                "object_count_accuracy",
                "failure_detection_auc",
                "negative_control_gap_vs_random_placement",
            ],
            validation_checks=[
                "seeded evidence disclosure exists",
                "every scene graph has object nodes and relation edges",
                "geometry table contains collision/support/out_of_room metrics",
                "negative controls are generated and compared",
            ],
            failure_checks=[
                "random placement matches verifier on relation/collision metrics",
                "uncertainty fields are empty for most scenes",
                "scene graph verifier improves no metric over depth/layout-only baseline",
            ],
            compute_requirements="CPU is enough for symbolic verifier; single GPU optional if depth/object detectors are run from scratch.",
            manual_decisions_needed=[
                "Which small indoor dataset subset to use",
                "Whether to use existing detections/depth or generate them locally",
                "How to define proxy support/collision labels",
                "How to present seeded evidence disclosure in final materials",
            ],
            not_in_scope=[
                "Training a full single-image 3D generation model",
                "Rendering photorealistic novel views",
                "Claiming fully automatic paper retrieval for this direction",
            ],
            recommended_execution_priority="Low to Medium: visually valuable, but engineering risk is higher than IAD and physical-property proxy MVP.",
        ),
        ExperimentExecutionPlan(
            execution_plan_id="exec_05_iad_reference_consistency_mvp",
            source_plan_id="plan_05_iad_agent",
            task_name="工业异常检测 IAD + Agent",
            execution_scope="Reference-consistency IAD agent MVP with cached or lightweight baseline scores, not a full industrial deployment.",
            why_this_scope=(
                "IAD 的数据集和指标最标准，reference bank、negative controls、evidence-grounded report checker 也最容易做成一个闭环。"
                "因此如果后续要真正执行一个实验，IAD 是最低工程风险候选，但这不代表项目只做 IAD。"
            ),
            data_preparation_tasks=[
                "选择 MVTec AD 或 VisA 的小型 category subset，准备 train normal、test normal/anomaly split。",
                "构建 iad_reference_manifest.jsonl，记录 product_category、image_id、split、label、mask path 和 provenance。",
                "准备 baseline anomaly scores 和 heatmaps，可先使用已有 baseline/cached features。",
                "准备 contaminated normal bank、random retrieval、shuffled provenance 等 negative controls。",
            ],
            scripts_to_implement=[
                ScriptSpec(
                    path="scripts/prepare_iad_reference_manifest.py",
                    purpose="构建 IAD reference bank 和 test split manifest。",
                    inputs=["MVTec AD or VisA subset"],
                    outputs=["data/iad_reference_manifest.jsonl"],
                    command_template="python scripts/prepare_iad_reference_manifest.py --dataset DATA_DIR --category bottle --output data/iad_reference_manifest.jsonl",
                    validation_check="manifest 必须包含 split、label、image_path、product_category、provenance。",
                ),
                ScriptSpec(
                    path="scripts/build_reference_bank.py",
                    purpose="为 normal references 建立 patch/image embeddings 和 retrieval index。",
                    inputs=["data/iad_reference_manifest.jsonl"],
                    outputs=["data/iad_reference_bank.npz", "data/iad_reference_index.jsonl"],
                    command_template="python scripts/build_reference_bank.py --manifest data/iad_reference_manifest.jsonl --output_dir data",
                    validation_check="reference bank 只允许使用 train normal 或指定 normal references。",
                ),
                ScriptSpec(
                    path="scripts/run_iad_baselines.py",
                    purpose="运行或读取 PatchCore/PaDiM/WinCLIP 等 baseline anomaly scores。",
                    inputs=["data/iad_reference_manifest.jsonl"],
                    outputs=["results/iad_baseline_scores.csv", "results/iad_region_heatmaps.npz"],
                    command_template="python scripts/run_iad_baselines.py --manifest data/iad_reference_manifest.jsonl --output_dir results",
                    validation_check="baseline score 文件必须覆盖 test split 中的每张图。",
                ),
                ScriptSpec(
                    path="scripts/score_reference_consistency.py",
                    purpose="计算 anomaly/reference/disagreement/evidence 综合分和 accept/abstain 决策。",
                    inputs=["results/iad_baseline_scores.csv", "data/iad_reference_bank.npz", "results/iad_region_heatmaps.npz"],
                    outputs=["results/iad_reference_consistency_scores.csv"],
                    command_template="python scripts/score_reference_consistency.py --manifest data/iad_reference_manifest.jsonl --baseline results/iad_baseline_scores.csv --reference_bank data/iad_reference_bank.npz --output results/iad_reference_consistency_scores.csv",
                    validation_check="每个 accepted report 必须绑定 anomaly region 和 normal reference id。",
                ),
                ScriptSpec(
                    path="scripts/run_iad_negative_controls.py",
                    purpose="运行 random retrieval、shuffled provenance、contaminated normal bank 控制组。",
                    inputs=["data/iad_reference_manifest.jsonl", "results/iad_reference_consistency_scores.csv"],
                    outputs=["results/iad_negative_control_report.csv"],
                    command_template="python scripts/run_iad_negative_controls.py --manifest data/iad_reference_manifest.jsonl --scores results/iad_reference_consistency_scores.csv --output results/iad_negative_control_report.csv",
                    validation_check="negative controls 必须与 full agent 使用同一 test split。",
                ),
            ],
            commands_to_run=[
                "python scripts/prepare_iad_reference_manifest.py --dataset DATA_DIR --category bottle --output data/iad_reference_manifest.jsonl",
                "python scripts/build_reference_bank.py --manifest data/iad_reference_manifest.jsonl --output_dir data",
                "python scripts/run_iad_baselines.py --manifest data/iad_reference_manifest.jsonl --output_dir results",
                "python scripts/score_reference_consistency.py --manifest data/iad_reference_manifest.jsonl --baseline results/iad_baseline_scores.csv --reference_bank data/iad_reference_bank.npz --output results/iad_reference_consistency_scores.csv",
                "python scripts/run_iad_negative_controls.py --manifest data/iad_reference_manifest.jsonl --scores results/iad_reference_consistency_scores.csv --output results/iad_negative_control_report.csv",
            ],
            expected_outputs=[
                "data/iad_reference_manifest.jsonl",
                "data/iad_reference_bank.npz",
                "data/iad_reference_index.jsonl",
                "results/iad_baseline_scores.csv",
                "results/iad_region_heatmaps.npz",
                "results/iad_reference_consistency_scores.csv",
                "results/iad_negative_control_report.csv",
                "results/iad_agent_execution_summary.md",
            ],
            metrics_to_compute=[
                "image_level_auroc",
                "pixel_level_auroc or PRO score",
                "false_alarm_reduction",
                "evidence_grounding_score",
                "tool_success_rate",
                "selective_risk",
                "negative_control_gap_vs_random_retrieval",
            ],
            validation_checks=[
                "reference bank contains only allowed normal references",
                "baseline scores cover all test images",
                "accepted reports have region/reference/evidence ids",
                "negative controls use the same test split and metrics",
                "manual-check claims remain flagged in report text",
            ],
            failure_checks=[
                "random retrieval reaches within 5% of full agent",
                "contaminated reference bank does not reduce confidence or trigger warning",
                "evidence_grounding_score below 85% for accepted reports",
                "detection/localization metrics degrade while report quality improves",
            ],
            compute_requirements="Single GPU useful for baselines/embeddings; CPU possible if baseline scores and features are cached.",
            manual_decisions_needed=[
                "Which dataset and product category to start with",
                "Whether to compute baselines now or use cached scores",
                "Which region mask source to trust for evidence grounding",
                "How to define contaminated normal bank stress test",
            ],
            not_in_scope=[
                "Full industrial deployment",
                "Human-in-the-loop UI",
                "Large-scale multi-category benchmark",
                "Replacing all IAD baselines",
            ],
            recommended_execution_priority="High for first real execution: easiest to make runnable with public datasets and standard metrics.",
        ),
    ]


def md_table(headers: List[str], rows: List[List[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def bullet_list(items: Iterable[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def numbered_list(items: Iterable[str]) -> str:
    return "\n".join(f"{idx}. {item}" for idx, item in enumerate(items, start=1))


def script_table(scripts: List[ScriptSpec]) -> str:
    rows = []
    for script in scripts:
        rows.append([
            script.path,
            script.purpose,
            "<br>".join(script.inputs),
            "<br>".join(script.outputs),
        ])
    return md_table(["Script", "Purpose", "Inputs", "Outputs"], rows)


def plan_section(plan: ExperimentExecutionPlan) -> str:
    return f"""### {plan.execution_plan_id}: {plan.task_name}

执行范围：{plan.execution_scope}

为什么这样切：{plan.why_this_scope}

### 数据准备任务

{numbered_list(plan.data_preparation_tasks)}

### 待实现脚本

{script_table(plan.scripts_to_implement)}

### 命令模板

```bash
{chr(10).join(plan.commands_to_run)}
```

### 预期输出

{bullet_list(plan.expected_outputs)}

### 指标

{bullet_list(plan.metrics_to_compute)}

### 验证检查

{bullet_list(plan.validation_checks)}

### 失败检查

{bullet_list(plan.failure_checks)}

### 资源和人工决策

Compute：{plan.compute_requirements}

需要人工决定：

{bullet_list(plan.manual_decisions_needed)}

当前不做：

{bullet_list(plan.not_in_scope)}

执行优先级：{plan.recommended_execution_priority}
"""


def generate_report(plans: List[ExperimentExecutionPlan]) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    overview_rows = [
        [
            plan.execution_plan_id,
            plan.source_plan_id,
            plan.task_name,
            plan.execution_scope,
            plan.recommended_execution_priority,
        ]
        for plan in plans
    ]
    return f"""# V1.1 Experiment Execution Planning

生成时间：{generated_at}

生成脚本：`focused_workflow/scripts/build_v11_experiment_execution_plan.py`

## 为什么做 V1.1

V1.0 已经把经过生成、修复、盲评和证据校验的 idea 转换成 final research plans。V1.1 的任务是继续往前推进半步：把 final research plans 拆成可执行实验任务清单。

本阶段仍然不做三件事：

- 不真正写完整算法实现；
- 不运行真实 benchmark；
- 不声称得到实验结果。

它只回答：如果下一步要执行实验，应该准备哪些数据，写哪些脚本，跑哪些命令，产生哪些表格，以及怎样判断执行失败。报告中的命令是模板，不是当前立刻执行的命令；对应脚本需要在 v1.2 才真正实现。

## 总览

{md_table(["Execution Plan", "Source Plan", "任务", "执行范围", "建议优先级"], overview_rows)}

注意：这里的“建议优先级”只是工程执行优先级，不是项目方向选择。项目主张仍然是跨任务科研 idea generation workflow。

## Execution Plan Schema

每个 execution plan 必须包含以下字段：

{bullet_list(EXECUTION_PLAN_SCHEMA["required"])}

## 三个执行规划

{chr(10).join(plan_section(plan) for plan in plans)}

## 当前阶段状态

完成 V1.1 后，项目阶段可以表述为：

```text
已完成 final research plan -> experiment execution plan 的拆解。
尚未进入真实实验代码实现、benchmark 运行和结果表格生成。
```

下一步如果继续推进，应进入 v1.2：选择一个 execution plan，真正实现最小脚本和小规模数据闭环。
"""


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    out_dir = root / "competition_submission"
    out_dir.mkdir(parents=True, exist_ok=True)
    plans = make_execution_plans()

    report_path = out_dir / "V11_EXPERIMENT_EXECUTION_PLAN_CN.md"
    schema_path = out_dir / "EXPERIMENT_EXECUTION_PLAN_SCHEMA.json"
    json_path = out_dir / "V11_EXPERIMENT_EXECUTION_PLAN.json"

    report_path.write_text(generate_report(plans), encoding="utf-8")
    write_json(schema_path, EXECUTION_PLAN_SCHEMA)
    write_json(
        json_path,
        {
            "version": "v1.1",
            "purpose": "experiment_execution_planning_only",
            "plans": [asdict(plan) for plan in plans],
            "boundary": "No algorithm implementation, real benchmark run, or demo is claimed in v1.1.",
        },
    )

    print("V1.1 experiment execution planning files written:")
    print(f"- report: {report_path}")
    print(f"- schema: {schema_path}")
    print(f"- json: {json_path}")


if __name__ == "__main__":
    main()
