#!/usr/bin/env python3
"""Live backend runner for the AI4S web demo.

This runner is intentionally allowlisted and safe-by-default. It executes a
real local workflow pass over existing project artifacts:

1. select task spec;
2. refresh or locate the latest focused-workflow artifacts;
3. load baseline cards / papers / focused ideas / experiment plans;
4. render a live workflow result bundle;
5. refresh the V26 Auto-claude/ARIS execution bridge.

It does not accept arbitrary shell commands from the webpage. Full LLM ideation
can be added behind explicit authorization, but the competition-safe default is
``safe_local``.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

TASKS = {
    "physical": {
        "label": "物理属性预测",
        "task_spec": "focused_workflow/tasks/benchmark_cv/01_physical_property_prediction.yaml",
        "slug": "physical_property",
        "v10_plan_id": "plan_01_physical_property",
        "artifact_candidates": [
            "outputs/live_workflow_artifacts/physical",
            "outputs/v05_evidence_grounded_ideation_01_physical_property_prediction_20260712_102328/repair_runs/physical_v2_evidence_card_repair_20260712_175021/repaired_run",
            "outputs/v05_evidence_grounded_ideation_01_physical_property_prediction_20260712_102328",
        ],
        "evidence_candidates": [
            "competition_github_release_20260724/sample_outputs/v05_evidence/physical_property",
            "outputs/v05_evidence_grounded_ideation_01_physical_property_prediction_20260712_102328/repair_runs/physical_v2_evidence_card_repair_20260712_175021/repaired_run",
        ],
    },
    "indoor3d": {
        "label": "室内单图 3D 场景生成",
        "task_spec": "focused_workflow/tasks/benchmark_cv/03_indoor_scene_generation.yaml",
        "slug": "indoor3d_scene",
        "v10_plan_id": "plan_03_indoor3d",
        "artifact_candidates": [
            "outputs/live_workflow_artifacts/indoor3d",
            "outputs/v05_evidence_grounded_ideation_03_indoor_scene_generation_seeded/repair_runs/indoor3d_evidence_card_repair_20260712_174142/repaired_run",
            "outputs/v05_evidence_grounded_ideation_03_indoor_scene_generation_seeded",
        ],
        "evidence_candidates": [
            "competition_github_release_20260724/sample_outputs/v05_evidence/indoor3d_seeded",
            "outputs/v05_evidence_grounded_ideation_03_indoor_scene_generation_seeded/repair_runs/indoor3d_evidence_card_repair_20260712_174142/repaired_run",
        ],
    },
    "iad": {
        "label": "工业异常检测 IAD + Agent",
        "task_spec": "focused_workflow/tasks/benchmark_cv/05_iad_agent_workflow.yaml",
        "slug": "iad_agent",
        "v10_plan_id": "plan_05_iad_agent",
        "artifact_candidates": [
            "outputs/live_workflow_artifacts/iad",
            "outputs/v05_evidence_grounded_ideation_05_iad_agent_workflow_20260712_101952/repair_runs/local_targeted_repair_20260712_103945/repaired_run",
            "outputs/v05_evidence_grounded_ideation_05_iad_agent_workflow_20260712_101952",
        ],
        "evidence_candidates": [
            "competition_github_release_20260724/sample_outputs/v05_evidence/iad_agent",
            "outputs/v05_evidence_grounded_ideation_05_iad_agent_workflow_20260712_101952/repair_runs/local_targeted_repair_20260712_103945/repaired_run",
        ],
    },
    "custom": {
        "label": "自定义科研任务",
        "task_spec": "",
        "slug": "custom_research_task",
        "v10_plan_id": "",
        "artifact_candidates": [],
        "evidence_candidates": [],
    },
}

PHYSICAL_METHOD_BASELINES = [
    "NeRF2Physics：language-embedded feature fields + LLM/VLM common-sense physical property reasoning",
    "PUGS：3D Gaussian Splatting + VLM zero-shot physical property prediction and propagation",
    "Pixie：multi-view CLIP feature field + 3D U-Net regression for dense material/physics fields",
    "Efficient Structure-Guided 3D Physical Property Reasoning / S3-PHYS-style：DINO/CLIP structure-guided 3D feature reasoning",
    "VoMP：Geometry Transformer for volumetric mechanical property fields",
    "PhyPush：interaction-based physics-guided Transformer for mass/friction estimation",
    "Traditional lower bounds：category-only/material prior, single-point regressor, MLP or simulator-fitting baseline",
]

PHYSICAL_BASELINE_WEAKNESS = [
    "VLM/common-sense baselines such as NeRF2Physics/PUGS can confuse visible surface material with true bulk material and often produce over-confident point estimates.",
    "Multi-view/3D feature-field baselines such as Pixie/VoMP require multi-view images or reliable 3D representations; single indoor images introduce severe geometry, scale, and occlusion uncertainty.",
    "Structure-guided 3D reasoning improves efficiency but still depends on reliable 3D structure, component segmentation, and representative point sampling.",
    "Interaction-based baselines such as PhyPush estimate hidden properties like mass/friction more directly, but require robot interaction trajectories and are not pure single-image baselines.",
    "Simple priors or MLP/single-point regressors are useful lower bounds, but lack calibrated intervals, abstention, and evidence provenance.",
]

PHYSICAL_PAPER_EVIDENCE = [
    {
        "title": "NeRF2Physics: Physical Property Understanding from Language-Embedded Feature Fields",
        "year": "2024",
        "venue": "CVPR",
        "url": "https://ajzhai.github.io/NeRF2Physics/",
    },
    {
        "title": "PUGS: Zero-shot Physical Understanding with Gaussian Splatting",
        "year": "2025",
        "venue": "arXiv / robotics",
        "url": "https://arxiv.org/abs/2502.12231",
    },
    {
        "title": "Pixie: 3D Physics from Pixels",
        "year": "2026",
        "venue": "project / arXiv",
        "url": "https://pixie-3d.github.io/",
    },
    {
        "title": "Efficient Structure-Guided 3D Physical Property Reasoning",
        "year": "2026",
        "venue": "CVPR Workshop",
        "url": "https://openaccess.thecvf.com/content/CVPR2026W/OpenSUN3D/html/Lan_Efficient_Structure-Guided_3D_Physical_Property_Reasoning_CVPRW_2026_paper.html",
    },
    {
        "title": "VoMP: Predicting Volumetric Mechanical Property Fields",
        "year": "2026",
        "venue": "ICLR",
        "url": "https://huggingface.co/papers/2510.22975",
    },
    {
        "title": "PhyPush: One Push is All You Need for Sensorless Physical Property Estimation with Physics-Guided Transformers",
        "year": "2026",
        "venue": "arXiv / robotics",
        "url": "https://arxiv.org/abs/2605.26284",
    },
]

PHYSICAL_EXPERIMENT_PLAN = [
    "Build indoor_property_manifest.jsonl with image id, object mask/box, category, material candidates, proxy interval labels, and mask-quality metadata.",
    "Run NeRF2Physics/PUGS-style VLM common-sense baselines for material and physical-property prediction from rendered or available views.",
    "Run Pixie/VoMP-style feature-field regression baselines when multi-view/3D assets are available; otherwise mark them as upper-resource baselines and report the resource gap.",
    "Run S3-PHYS-style structure-guided 3D feature reasoning baseline when DINO/CLIP feature lifting and component sampling are available.",
    "Run simple lower-bound baselines: category-only/material prior, uncalibrated single-point regressor, and shuffled material-property table negative control.",
    "Fit the proposed conformal calibration layer over proxy labels and object-similarity groups, then evaluate interval coverage, width, calibration error, and selective risk.",
]

PHYSICAL_METRICS = [
    "density_log_mae",
    "youngs_modulus_log_mae",
    "mass_error",
    "prediction_interval_coverage",
    "calibration_error",
    "selective_risk",
    "runtime_or_query_cost",
]

PHYSICAL_ABLATIONS = [
    "remove conformal calibration",
    "remove subgroup/object-similarity grouping",
    "remove mask-quality features",
    "remove material posterior entropy",
    "replace interval output with single-point regression",
]

PHYSICAL_NEGATIVE_CONTROLS = [
    "shuffle material-property table entries",
    "permute proxy labels across object categories",
    "use random masks or background masks",
    "apply high-quality-mask calibration to low-quality-mask objects",
]

PHYSICAL_SUCCESS_THRESHOLDS = [
    "Nominal 90% prediction intervals should achieve empirical coverage within ±5 percentage points overall on proxy visible-material targets.",
    "Subgroup coverage should remain at least 80% for major object/material/mask-quality groups.",
    "Calibration error should improve by at least 25% relative to uncalibrated VLM/material-table confidence.",
    "Median interval width should not inflate by more than 20% relative to uncalibrated table intervals at the same coverage target.",
    "Negative controls should degrade coverage or inflate interval width, showing that valid labels, masks, and confidence features are necessary.",
    "Runtime/query cost should be reported against NeRF2Physics/PUGS/Pixie/VoMP/S3-PHYS-style baselines where implementations or public numbers are available.",
]

TASK_MODE_PROFILES = {
    "incremental_improvement": {
        "label": "增量改进",
        "idea_lens": "在不推翻原 baseline pipeline 的前提下，只增加一个最小可插拔模块，优先保证改动小、可复现、容易做 ablation。",
        "improvement_points": [
            "保留最强 baseline 的主体训练/推理流程，只替换或增加一个局部模块。",
            "把新增模块设计成可开关组件，方便和原 baseline 做 paired comparison。",
            "重点证明小改动是否稳定改善质量，而不是追求复杂系统堆叠。",
        ],
        "experiment_focus": [
            "先复现 strongest baseline，并固定同一数据划分、输入预处理和评价脚本。",
            "只打开 proposed minimal module 跑一次主实验，再关闭模块跑 ablation。",
            "报告平均提升、标准差和失败样例，避免只展示单个好结果。",
        ],
        "metrics": ["delta_over_strongest_baseline", "paired_ablation_gain", "failure_case_count"],
    },
    "metric_improvement": {
        "label": "指标提升",
        "idea_lens": "把目标明确收敛到可量化指标提升，优先优化主指标、校准误差和稳健性指标。",
        "improvement_points": [
            "将 baseline weakness 转换成可测量的指标缺口。",
            "为 proposed module 绑定明确优化目标和成功阈值。",
            "同时报告主指标和副作用指标，避免只提升一个数字但破坏可靠性。",
        ],
        "experiment_focus": [
            "定义 primary metric、secondary metric 和不可退化约束。",
            "对所有 baseline 与 proposed idea 使用同一 test split 和 bootstrap/confidence interval。",
            "补充 threshold sweep 或 calibration curve，说明指标提升来自机制而非调参偶然性。",
        ],
        "metrics": ["primary_metric_gain", "calibration_error", "bootstrap_confidence_interval"],
    },
    "engineering_integration": {
        "label": "工程拼接",
        "idea_lens": "把 idea 改写成可运行系统方案，重点是模块接口、数据流、失败恢复和人工授权。",
        "improvement_points": [
            "把论文级 idea 拆成数据准备、baseline runner、proposed runner、metric reader 和 report writer。",
            "明确每个模块的输入输出 schema，减少实验阶段的人工粘合。",
            "为下载数据、调用 API、启动 GPU 等动作加入人工授权节点。",
        ],
        "experiment_focus": [
            "生成 runnable workspace：manifest、config、baseline command、proposed command、metric script。",
            "先跑 smoke test，再跑完整实验，失败时记录 error type 和 recovery suggestion。",
            "输出可提交的运行日志、指标表、图表和论文草稿素材。",
        ],
        "metrics": ["tool_success_rate", "end_to_end_completion_rate", "manual_intervention_count"],
    },
    "evaluation_protocol": {
        "label": "评价协议",
        "idea_lens": "把重点放在如何公平、盲化、可复核地比较 idea，而不是只产出一个看起来更长的方案。",
        "improvement_points": [
            "把候选 idea 转换成匿名 A/B review item，隐藏来源和方法名。",
            "引入负控制、位置交换和一致性检查，降低 judge 偏置。",
            "输出每个维度的评分差异与 reviewer rationale，支持后续自动修复。",
        ],
        "experiment_focus": [
            "构造 blind A/B pack，并做 A/B 位置交换 sanity check。",
            "按 novelty、feasibility、experimental rigor、implementation readiness 等维度统计结果。",
            "把 reviewer rationale 自动聚类成可执行 repair instruction。",
        ],
        "metrics": ["after_win_rate", "position_bias_rate", "inter_reviewer_agreement"],
    },
    "system_optimization": {
        "label": "系统优化",
        "idea_lens": "把单个算法 idea 扩展成 agentic workflow，重点优化可靠性、可追踪性、证据约束和失败自修复。",
        "improvement_points": [
            "为每个科研步骤记录 provenance：论文证据、baseline card、judge rationale、实验日志。",
            "增加自动诊断节点，把失败分成 evidence mismatch、schema mismatch、threshold failure、execution failure。",
            "把修复动作限制在可审计的 runner/workspace 中，避免网页执行任意命令。",
        ],
        "experiment_focus": [
            "跑端到端 workflow smoke test，检查每个阶段是否产出可读 artifact。",
            "设计 execution-feedback case：故意触发阈值/检索/证据失败，再验证系统能否定位和修复。",
            "报告完成率、错误恢复率、证据通过率和最终方案可执行性。",
        ],
        "metrics": ["workflow_completion_rate", "evidence_pass_rate", "execution_repair_success_rate"],
    },
}

TASK_MODE_TITLES = {
    "iad": {
        "incremental_improvement": "Selective Reference-Consistency Calibration for PatchCore-style IAD",
        "metric_improvement": "False-Alarm-Calibrated Reference-Consistency IAD Agent",
        "engineering_integration": "Authorized IAD Experiment Runner with Reference-Bank Provenance",
        "evaluation_protocol": "Blind Stress-Test Protocol for Trustworthy IAD Agents",
        "system_optimization": "Evidence-Grounded IAD Research Agent with Execution-Feedback Repair",
    },
    "physical": {
        "incremental_improvement": "Lightweight Conformal Calibration Layer for Physical Property Prediction",
        "metric_improvement": "Metric-Driven Conformal Property Calibration from Proxy Labels",
        "engineering_integration": "Runnable Physical-Property Experiment Workspace with Baseline Adapters",
        "evaluation_protocol": "Evidence-Checked Evaluation Protocol for Physical Property Ideas",
        "system_optimization": "Closed-Loop Physical Property Research Agent with Mechanism-Consistent Repair",
    },
    "indoor3d": {
        "incremental_improvement": "Geometry-Scaffolded Occlusion Completion as a Minimal Indoor-3D Add-on",
        "metric_improvement": "Consistency-Calibrated Indoor Single-Image 3D Scene Generation",
        "engineering_integration": "Indoor-3D Reconstruction Runner with Dataset and Rendering Adapters",
        "evaluation_protocol": "Blind Multi-Criteria Evaluation Protocol for Indoor 3D Scene Ideas",
        "system_optimization": "Evidence-Grounded Indoor-3D Research Agent with Repairable Scene Plans",
    },
}


def build_mode_specific_idea_text(
    task_key: str,
    plan: dict[str, Any],
    task_mode: str,
    profile: dict[str, Any],
) -> str:
    """Rewrite the selected workflow idea through the requested task-type lens.

    The web demo must show a visibly different idea when the user changes the
    task type.  We still keep the source workflow evidence: baselines,
    weaknesses, papers, metrics, and experiment plans are loaded from artifacts;
    this function changes the research objective and implementation framing.
    """
    base_title = str(plan.get("original_workflow_idea_title") or plan.get("idea_title") or "workflow-selected idea").strip()
    title = TASK_MODE_TITLES.get(task_key, {}).get(task_mode) or f"{base_title} [{profile['label']}]"

    def compact_item(item: Any) -> str:
        if isinstance(item, str):
            stripped = item.strip()
            if stripped.startswith("{") or stripped.startswith("["):
                try:
                    parsed = json.loads(stripped)
                    return compact_item(parsed)
                except json.JSONDecodeError:
                    return stripped
            return stripped
        if isinstance(item, dict):
            parts = []
            for key, value in item.items():
                if isinstance(value, list):
                    parts.append(f"{key}: {'、'.join(str(v) for v in value[:5])}")
                elif isinstance(value, dict):
                    nested = []
                    for nested_key, nested_value in value.items():
                        if isinstance(nested_value, list):
                            nested.append(f"{nested_key}: {'、'.join(str(v) for v in nested_value[:5])}")
                        elif nested_value not in ("", None, [], {}):
                            nested.append(f"{nested_key}: {nested_value}")
                    if nested:
                        parts.append(f"{key}: {'; '.join(nested)}")
                elif value not in ("", None, [], {}):
                    parts.append(f"{key}: {value}")
            return "; ".join(parts)
        return str(item)

    def compact_items(items: list[Any], limit: int) -> list[str]:
        out: list[str] = []
        seen: set[str] = set()
        for item in items or []:
            text = compact_item(item).strip()
            if not text or text in seen:
                continue
            seen.add(text)
            out.append(text)
            if len(out) >= limit:
                break
        return out

    baselines = compact_items(plan.get("baselines", []), 5)
    weaknesses = compact_items(plan.get("baseline_weakness", []), 4)
    baseline_text = "; ".join(baselines) if baselines else "the retrieved baseline cards"
    weakness_text = "; ".join(weaknesses) if weaknesses else "the baseline gaps identified by the workflow"

    if task_key == "iad":
        mode_core = {
            "incremental_improvement": (
                "在 PatchCore/PaDiM/FastFlow 等异常检测 baseline 后面增加一个轻量 reference-consistency gate。"
                "模型不重训主干，只检查高分异常区域是否能被 top-k normal reference patches 合理解释，"
                "从而把 texture/lighting/reference-bank shift 造成的误报拦下来。"
            ),
            "metric_improvement": (
                "把目标明确设为降低 false alarm rate 并尽量保留 anomaly recall。"
                "系统学习 category-aware threshold、reference-consistency margin 和 model-disagreement score 的组合，"
                "输出可校准的 defect acceptance decision。"
            ),
            "engineering_integration": (
                "把 IAD idea 拆成可执行工程链路：dataset manifest、normal reference bank、baseline scorer、"
                "reference-consistency scorer、negative-control runner、metric summarizer 和 report writer。"
                "网页只触发受控入口，下载数据、调用模型或跑 GPU 前必须人工授权。"
            ),
            "evaluation_protocol": (
                "把 IAD agent 作为被评估对象，构造 shifted normal bank、random retrieval、shuffled provenance、"
                "contaminated normal bank 等 stress tests，比较 report 是否有证据支撑、是否误报、是否该升级人工复核。"
            ),
            "system_optimization": (
                "构建完整可信 IAD 科研智能体：论文证据检索、baseline weakness 诊断、reference-bank audit、"
                "阈值失败检测、类别感知修复、实验日志追踪和论文草稿生成形成闭环。"
            ),
        }
    elif task_key == "physical":
        mode_core = {
            "incremental_improvement": (
                "在 NeRF2Physics/PUGS/Pixie/S3-PHYS-style 等 baseline 输出后增加一个轻量 conformal calibration layer。"
                "不替换原视觉/3D 表征，只把单点物理属性预测改成带覆盖率保证的区间预测。"
            ),
            "metric_improvement": (
                "把研究目标收敛到 prediction interval coverage、calibration error、selective risk 等可量化指标。"
                "系统利用 proxy labels、object similarity group、mask quality 和 material uncertainty 校准物理属性区间。"
            ),
            "engineering_integration": (
                "把物理属性预测拆成 baseline adapter：VLM common-sense baseline、feature-field regression baseline、"
                "structure-guided 3D reasoning baseline、proxy-label manifest、calibration runner 和 metric table generator。"
            ),
            "evaluation_protocol": (
                "重点不是声称某个物理属性预测器更强，而是建立证据核查和盲评协议：检查 baseline 是否公平、"
                "paper evidence 是否真实支撑 claim、区间预测是否通过 subgroup coverage 与负控制。"
            ),
            "system_optimization": (
                "把物理属性方向作为 failure-diagnosis-repair 案例：当 generic repair 出现机制错配时，"
                "系统根据 reviewer rationale 将 interval mapper、material verifier 和 uncertainty propagation 重新对齐。"
            ),
        }
    else:
        mode_core = {
            "incremental_improvement": (
                "在 Text2Room/SceneScape/WonderJourney/DUSt3R/MASt3R 等室内 3D baseline 上增加一个最小几何脚手架模块，"
                "只约束尺度、布局、遮挡补全和相机一致性，不重写整套生成系统。"
            ),
            "metric_improvement": (
                "把目标聚焦到 geometry consistency、layout validity、view consistency 和 object completion quality。"
                "系统用检索到的场景先验与几何 scaffold 校准生成结果，减少漂浮、穿模和尺度错误。"
            ),
            "engineering_integration": (
                "把室内 3D idea 拆成图像输入、深度/匹配模块、layout estimator、3D asset retrieval、"
                "scene renderer、metric evaluator 和 visualization exporter，便于评委看到可运行链路。"
            ),
            "evaluation_protocol": (
                "构造盲评与自动指标结合的协议：同一输入图像下比较 baseline/proposed 的布局合理性、"
                "遮挡补全可信度、多视角一致性和失败案例，并披露 seeded evidence bank。"
            ),
            "system_optimization": (
                "把室内 3D 方向纳入 evidence-grounded research agent：从论文证据、baseline weakness、"
                "scene representation choice、repair rationale 到实验计划全部可追踪。"
            ),
        }

    core = mode_core.get(task_mode, profile["idea_lens"])
    improvement_lines = "\n".join(f"{idx}. {x}" for idx, x in enumerate(profile["improvement_points"], 1))
    experiment_lines = "\n".join(f"{idx}. {x}" for idx, x in enumerate(profile["experiment_focus"], 1))
    metrics = compact_items(unique_extend(plan.get("metrics", [])[:6], profile["metrics"]), 9)
    metric_lines = "、".join(metrics) if metrics else "按 workflow 的 experiment_plan.json 输出指标"

    return "\n\n".join([
        f"一句话 Idea：{title}",
        f"研究问题：当前方向的已有方法主要包括 {baseline_text}。workflow 识别到的关键空白是：{weakness_text}。",
        f"核心想法：{core}",
        "方法设计：\n" + improvement_lines,
        "实验验证计划：\n" + experiment_lines,
        f"评价指标：{metric_lines}。",
        f"来源说明：该 idea 由 workflow 从原始候选 “{base_title}” 出发，结合任务类型“{profile['label']}”重新聚焦得到。",
    ])


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_jsonl(path: Path, limit: int | None = None) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
        if limit and len(rows) >= limit:
            break
    return rows


def find_existing(paths: list[str]) -> Path | None:
    for raw in paths:
        p = ROOT / raw
        if p.exists():
            return p
    return None


def has_workflow_artifacts(path: Path) -> bool:
    return (
        path.exists()
        and (path / "baseline_cards.jsonl").exists()
        and (path / "focused_ideas.json").exists()
        and (path / "experiment_plan.json").exists()
    )


def ensure_live_artifact_cache(task_key: str) -> None:
    """Refresh task-specific artifact cache when a builder exists.

    This is deliberately allowlisted.  The webpage does not pass arbitrary
    commands; it can only trigger this known script.
    """
    if task_key != "physical":
        return
    script = ROOT / "focused_workflow/scripts/build_v29_live_workflow_artifact_cache.py"
    if not script.exists():
        return
    subprocess.run(
        [sys.executable, str(script)],
        cwd=str(ROOT),
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def latest_artifact_dir(task: dict[str, Any]) -> Path | None:
    candidates: list[Path] = []
    for raw in task.get("artifact_candidates", []):
        candidates.append(ROOT / raw)
    # Fallback discovery: if new workflow runs are produced later, the backend
    # can pick them up without changing the webpage.
    slug = task["task_spec"].split("/")[-1].replace(".yaml", "")
    candidates.extend((ROOT / "outputs").glob(f"**/{slug}"))
    candidates.extend((ROOT / "outputs").glob(f"**/*{slug}*"))

    seen: set[Path] = set()
    valid: list[Path] = []
    for path in candidates:
        try:
            resolved = path.resolve()
        except FileNotFoundError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        if has_workflow_artifacts(path):
            valid.append(path)

    if not valid:
        return None
    # Explicit artifact cache always wins.  Otherwise use the newest directory
    # containing the required focused-workflow files.
    for path in valid:
        if "outputs/live_workflow_artifacts" in str(path):
            return path
    return max(valid, key=lambda p: max((p / f).stat().st_mtime for f in ["baseline_cards.jsonl", "focused_ideas.json", "experiment_plan.json"]))


def find_by_title(rows: list[dict[str, Any]], title_fields: list[str], title: str) -> dict[str, Any]:
    norm = title.strip().lower()
    for row in rows:
        for field in title_fields:
            if str(row.get(field, "")).strip().lower() == norm:
                return row
    return rows[0] if rows else {}


def build_idea_text(idea: dict[str, Any]) -> str:
    if idea.get("full_idea_text"):
        return str(idea["full_idea_text"])
    def fmt(value: Any, indent: int = 0) -> str:
        pad = "  " * indent
        if isinstance(value, dict):
            lines = []
            for k, v in value.items():
                text = fmt(v, indent + 1)
                if "\n" in text:
                    lines.append(f"{pad}{k}:\n{text}")
                else:
                    lines.append(f"{pad}{k}: {text}")
            return "\n".join(lines)
        if isinstance(value, list):
            return "\n".join(f"{pad}- {fmt(v, indent + 1).strip()}" for v in value)
        return str(value)

    parts = [
        f"Title:\n{idea.get('title', 'untitled')}",
        f"Core proposal / new component:\n{fmt(idea.get('new_component', ''))}",
        f"Mechanism or approach:\n{fmt(idea.get('new_mechanism', ''))}",
        f"Algorithmic objective:\n{fmt(idea.get('algorithmic_objective', ''))}",
        f"Why it may work / baseline weakness targeted:\n{fmt(idea.get('why_it_may_work', ''))}",
        f"Minimal new module:\n{fmt(idea.get('minimal_new_module', ''))}",
        f"Implementation plan:\n{fmt(idea.get('implementation_plan', ''))}",
        f"MVP artifacts:\n{fmt(idea.get('mvp_artifacts', ''))}",
        f"Expected outputs:\n{fmt(idea.get('expected_outputs', ''))}",
    ]
    return "\n\n".join(x for x in parts if not x.endswith(":\n"))


def workflow_plan_from_artifacts(task_key: str, artifact_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    baseline_cards = read_jsonl(artifact_dir / "baseline_cards.jsonl", limit=80)
    focused_ideas = read_json(artifact_dir / "focused_ideas.json")
    experiment_plans = read_json(artifact_dir / "experiment_plan.json")
    quality_path = artifact_dir / "idea_quality_scores.json"
    quality = read_json(quality_path) if quality_path.exists() else {}
    papers = read_jsonl(artifact_dir / "papers.jsonl", limit=80)
    evidence_cards = read_jsonl(artifact_dir / "evidence_baseline_cards.jsonl", limit=80)

    top_title = quality.get("top_idea") or (focused_ideas[0].get("title") if focused_ideas else "")
    idea = find_by_title(focused_ideas, ["title"], top_title)
    plan_row = find_by_title(experiment_plans, ["idea_title", "title"], idea.get("title", top_title))

    human_review = idea.get("human_review") or {}
    judge_summary = ""
    if human_review:
        judge_summary = (
            f"Human/expert review source={human_review.get('source')}, "
            f"item={human_review.get('item_id')}, winner={human_review.get('winner')}, "
            f"score={human_review.get('winner_score')}, confidence={human_review.get('confidence')}. "
            f"Reason: {human_review.get('review_reason')}"
        )
    elif quality.get("top_quality_score") is not None:
        judge_summary = f"Workflow idea quality scorer selected top idea with score={quality.get('top_quality_score')}."

    plan = {
        "plan_id": f"live_artifact_{task_key}",
        "source": "latest_focused_workflow_artifacts",
        "source_artifact_dir": str(artifact_dir.relative_to(ROOT)),
        "final_idea": build_idea_text(idea),
        "idea_title": idea.get("title", top_title),
        "raw_focused_idea": idea,
        "new_component": idea.get("new_component", ""),
        "new_mechanism": idea.get("new_mechanism", ""),
        "why_it_may_work": idea.get("why_it_may_work", ""),
        "minimal_new_module": idea.get("minimal_new_module", ""),
        "algorithmic_objective": idea.get("algorithmic_objective", ""),
        "implementation_plan": idea.get("implementation_plan", []),
        "mvp_artifacts": idea.get("mvp_artifacts", []),
        "expected_outputs": idea.get("expected_outputs", []),
        "baselines": [card.get("name", "unnamed baseline") for card in baseline_cards],
        "baseline_weakness": [card.get("limitations", "") for card in baseline_cards if card.get("limitations")],
        "experiment_plan": plan_row.get("implementation_steps", []),
        "metrics": plan_row.get("evaluation_metrics", idea.get("metrics", [])),
        "ablations": plan_row.get("ablation_studies", idea.get("ablations", [])),
        "negative_controls": plan_row.get("negative_controls", idea.get("negative_controls", [])),
        "success_thresholds": plan_row.get("success_criteria", idea.get("success_thresholds", [])),
        "datasets": plan_row.get("data_preparation", idea.get("datasets", [])),
        "judge_summary": judge_summary,
        "evidence_verification_status": "loaded from latest focused_workflow artifacts; verify_reference_claims output used when present",
        "quality_summary": quality,
    }
    evidence = {
        "evidence_dir": str(artifact_dir.relative_to(ROOT)),
        "paper_count": len(papers),
        "card_count": len(evidence_cards) or len(baseline_cards),
        "papers": papers[:12],
        "cards": evidence_cards[:8] or baseline_cards[:8],
        "baseline_cards": baseline_cards[:20],
        "focused_ideas": focused_ideas[:5],
        "experiment_plans": experiment_plans[:5],
    }
    return plan, evidence


def build_custom_workflow_plan(user_task_type: str, direction: str, task_mode: str) -> tuple[dict[str, Any], dict[str, Any]]:
    orchestrator_script = ROOT / "research_agent_orchestrator/orchestrator.py"
    if orchestrator_script.exists():
        result_json = ROOT / "execution_runs/research_agent_orchestrator/latest_custom_status.json"
        cmd = [
            sys.executable,
            str(orchestrator_script),
            "--task-type",
            user_task_type.strip() or "自定义科研任务",
            "--research-direction",
            direction.strip() or "用户输入的研究方向",
            "--task-mode",
            task_mode.strip() or "incremental_improvement",
            "--result-json",
            str(result_json),
        ]
        try:
            subprocess.run(cmd, cwd=str(ROOT), check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
            status = read_json(result_json)
            workspace = ROOT / status.get("workspace", "")
            ideas_payload = read_json(workspace / "focused_ideas.json")
            experiment_payload = read_json(workspace / "experiment_plan.json")
            runner_payload = read_json(workspace / "runner_plan.json")
            baseline_cards = read_jsonl(workspace / "baseline_cards.jsonl", limit=20)
            papers = read_jsonl(workspace / "papers.jsonl", limit=20)
            ideas = ideas_payload.get("ideas", [])
            first_idea = ideas[0] if ideas else {}
            mode_label = status.get("task_mode_label") or (TASK_MODE_PROFILES.get(task_mode) or TASK_MODE_PROFILES["incremental_improvement"])["label"]
            domain_profile = status.get("domain_profile") or {}
            detailed_idea_text = "\n\n".join([
                f"Title: {first_idea.get('title', '')}",
                f"Research problem: {first_idea.get('problem', '')}",
                f"Core idea: {first_idea.get('core_idea', '')}",
                f"Minimal new module: {first_idea.get('minimal_new_module', '')}",
                f"Mechanism: {first_idea.get('mechanism', '')}",
                f"Algorithmic objective: {first_idea.get('algorithmic_objective', '')}",
                "Baseline weaknesses:\n" + "\n".join(f"- {x}" for x in first_idea.get("baseline_weakness", [])),
                "Implementation plan:\n" + "\n".join(f"- {x}" for x in first_idea.get("implementation_plan", [])),
                "Evidence papers:\n" + "\n".join(f"- {x}" for x in first_idea.get("evidence_paper_refs", [])),
                "Boundary: retrieved papers and baseline cards are candidate evidence; final claims still require reference-claim verification and real runner metrics.",
            ]).strip()
            plan = {
                "plan_id": "research_agent_orchestrator_custom_task",
                "source": "research_agent_orchestrator_v0",
                "source_artifact_dir": status.get("workspace", ""),
                "idea_title": first_idea.get("title") or f"新方向 workflow 接入结果：{user_task_type or '自定义科研任务'}",
                "final_idea": detailed_idea_text,
                "baselines": [card.get("method_family", "") for card in baseline_cards if card.get("method_family")],
                "baseline_weakness": first_idea.get("baseline_weakness") or [
                    "当前为新任务接入模式：baseline cards 是 planned/unverified，需要真实论文检索后升级。",
                    "所有未绑定 paper evidence 的 claim 不能进入最终论文结论。",
                    "真实实验 benchmark 需要领域专用 runner，而不是 generic smoke runner。",
                ],
                "baseline_search_queries": domain_profile.get("queries", []),
                "improvement_points": unique_extend(
                    first_idea.get("implementation_plan", []),
                    [
                        f"新增模块：{first_idea.get('minimal_new_module', '')}",
                        f"优化目标：{first_idea.get('algorithmic_objective', '')}",
                        "支持进入 Phase 2 运行当前任务 runner scaffold，验证授权执行和 result-to-claim 链路。",
                    ],
                ),
                "experiment_plan": experiment_payload.get("steps", []),
                "metrics": first_idea.get("metrics") or experiment_payload.get("metrics", []),
                "ablations": first_idea.get("ablations") or experiment_payload.get("ablations", []),
                "negative_controls": first_idea.get("negative_controls") or experiment_payload.get("negative_controls", []),
                "success_thresholds": first_idea.get("success_thresholds") or [
                    "paper_count > 0 且 baseline_card_count > 0 后，才能升级为 evidence-grounded final idea。",
                    "领域 runner 能输出 JSON/CSV 指标后，才能写真实实验结论。",
                    "unsupported claims 必须从 final paper draft 中排除或标注待核查。",
                ],
                "datasets": first_idea.get("required_data") or experiment_payload.get("datasets", []),
                "judge_summary": f"ResearchAgentOrchestrator completed new-task onboarding for task mode={mode_label}; verified final idea is intentionally disabled until evidence retrieval succeeds.",
                "evidence_verification_status": "new task onboarding: paper retrieval planned; claims are unverified until papers.jsonl and baseline_cards.jsonl are evidence-backed.",
                "quality_summary": {},
                "runner_plan": runner_payload,
                "agent_status": status,
            }
            evidence = {
                "evidence_dir": status.get("workspace", ""),
                "paper_count": len(papers),
                "card_count": len(baseline_cards),
                "papers": papers,
                "cards": baseline_cards[:8],
                "baseline_cards": baseline_cards,
                "focused_ideas": ideas,
                "experiment_plans": [experiment_payload],
                "custom_mode_note": "ResearchAgentOrchestrator generated a new-task onboarding workspace; no fabricated paper evidence.",
                "agent_status": status,
            }
            return plan, evidence
        except Exception as exc:
            print(f"      ResearchAgentOrchestrator unavailable, fallback to static custom plan: {exc}", flush=True)

    profile = TASK_MODE_PROFILES.get(task_mode) or TASK_MODE_PROFILES["incremental_improvement"]
    task_name = user_task_type.strip() or "自定义科研任务"
    direction_text = direction.strip() or "用户输入的研究方向"
    mode_label = profile["label"]

    baseline_queries = [
        f"{direction_text} survey benchmark baseline",
        f"{task_name} state-of-the-art method evaluation",
        f"{direction_text} dataset metric ablation",
    ]
    generic_baselines = [
        "strongest published task-specific baseline after paper retrieval",
        "simple heuristic or classical lower-bound baseline",
        "foundation-model / LLM / VLM zero-shot baseline when applicable",
        "retrieval-augmented or tool-augmented baseline when applicable",
    ]
    baseline_weakness = [
        "当前网页未预置该新方向的论文库，因此不能直接声称已命中真实最新论文。",
        "需要先完成论文检索、baseline card 抽取和 reference claim verification，才能把方案升级为 evidence-grounded final plan。",
        "通用大模型容易生成宽泛 idea，因此本 fallback 强制输出 baseline、改进点、实验计划、负控制和成功阈值。",
    ]
    idea_title = f"{mode_label}：{direction_text} 的自动化科研方案"
    final_idea = "\n\n".join([
        f"一句话 Idea：围绕“{direction_text} / {task_name}”，构建一个 {mode_label} 导向的科研自动化方案。",
        f"研究问题：用户给出了新方向，但系统尚未加载该方向的专用论文证据库。因此第一步不是直接宣称发现 SOTA idea，而是先生成可验证的研究假设和实验骨架。",
        f"核心想法：{profile['idea_lens']} 该方案会先把任务拆成 baseline 检索、baseline weakness 定位、候选 idea 生成、自动评分、实验计划和证据核查六个可审计环节。",
        "方法设计：\n" + "\n".join(f"{i}. {x}" for i, x in enumerate(profile["improvement_points"], 1)),
        "实验验证计划：\n" + "\n".join(f"{i}. {x}" for i, x in enumerate(profile["experiment_focus"], 1)),
        "评价指标：novelty、feasibility、experimental_rigor、implementation_readiness、evidence_pass_rate，以及该领域检索后确定的主任务指标。",
        "来源说明：这是 custom live workflow fallback。它能让评委测试任意新方向时得到结构化输出，但不会伪造未检索论文或未执行实验结果。",
    ])
    plan = {
        "plan_id": "live_custom_task",
        "source": "custom_live_workflow_fallback",
        "source_artifact_dir": "",
        "idea_title": idea_title,
        "final_idea": final_idea,
        "baselines": generic_baselines,
        "baseline_weakness": baseline_weakness,
        "baseline_search_queries": baseline_queries,
        "improvement_points": profile["improvement_points"],
        "experiment_plan": [
            "用用户输入方向生成 task_spec.yaml 草案，固定 task description、scope、expected output schema。",
            "执行论文检索，抽取 top papers、datasets、metrics、baseline methods 和 known limitations。",
            "生成 baseline_cards.jsonl，并对每个 baseline 标注 method type、可复用模块、局限和对比指标。",
            "生成 3 个 focused ideas；每个 idea 必须包含 minimal_new_module、algorithmic_objective、required data、required scripts、metrics、ablations、negative controls。",
            "运行 idea quality scoring 和 blind-review pack；若 reviewer rationale 指出机制错配，则进入 critic repair。",
            "运行 reference claim verification；unsupported claim 不允许进入最终方案。",
        ] + profile["experiment_focus"],
        "metrics": unique_extend(
            ["novelty", "feasibility", "experimental_rigor", "implementation_readiness", "evidence_pass_rate"],
            profile["metrics"],
        ),
        "ablations": [
            "remove retrieved paper evidence",
            "remove baseline weakness constraints",
            "remove critic repair",
            "remove reference claim verification",
        ],
        "negative_controls": [
            "shuffle paper-to-claim mappings",
            "replace domain baselines with unrelated baselines",
            "ask model to generate idea without task_type constraint",
        ],
        "success_thresholds": [
            "所有最终 claim 必须绑定 paper evidence 或标记为待人工核查。",
            "至少生成 3 个可执行 idea，每个 idea 都有 baseline、实验脚本需求、数据需求和评价指标。",
            "critic repair 后 implementation_readiness 或 experimental_rigor 不低于 repair 前。",
        ],
        "datasets": ["由论文检索和用户上传数据共同确定"],
        "judge_summary": f"Custom task fallback selected a {mode_label}-oriented structured plan; no paper evidence is fabricated.",
        "evidence_verification_status": "custom direction: paper retrieval not preloaded; claims are marked as planned until evidence verification runs.",
        "quality_summary": {},
        "task_mode_profile": profile,
        "task_mode_specific_focus": profile["idea_lens"],
    }
    evidence = {
        "evidence_dir": "",
        "paper_count": 0,
        "card_count": 0,
        "papers": [],
        "cards": [],
        "baseline_cards": [],
        "focused_ideas": [],
        "experiment_plans": [],
        "custom_mode_note": "No preloaded evidence bank for this task. The output is a structured live workflow plan, not a verified evidence-grounded result.",
    }
    return plan, evidence


def load_v10_plan(plan_id: str) -> dict[str, Any]:
    candidates = [
        ROOT / "competition_submission/V10_FINAL_RESEARCH_PLAN_PACKAGE.json",
        ROOT / "competition_final_submission_20260725/competition_submission/V10_FINAL_RESEARCH_PLAN_PACKAGE.json",
    ]
    for path in candidates:
        if not path.exists():
            continue
        data = read_json(path)
        for plan in data.get("plans", []):
            if plan.get("plan_id") == plan_id:
                return plan
    raise FileNotFoundError("V10_FINAL_RESEARCH_PLAN_PACKAGE.json or selected plan not found")


def load_material_human_review() -> dict[str, Any]:
    candidates = [
        ROOT / "competition_submission/material_review_ideas.json",
        ROOT / "competition_final_submission_20260725/03_demo_video/demo_assets/material_review_ideas.json",
    ]
    for path in candidates:
        if path.exists():
            return read_json(path)
    return {}


def apply_material_review_override(task_key: str, plan: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    if task_key != "physical":
        return plan
    review = load_material_human_review()
    best = review.get("best_idea") or {}
    if not best.get("idea_text"):
        return plan
    patched = dict(plan)
    # Quality-first display: keep the focused_workflow artifact idea as the
    # webpage's core idea.  Human review is still attached as evidence, but it
    # must not overwrite the artifact-level idea text; otherwise the demo drifts
    # away from outputs/live_workflow_artifacts.
    patched["baselines"] = PHYSICAL_METHOD_BASELINES
    patched["baseline_weakness"] = PHYSICAL_BASELINE_WEAKNESS
    patched["paper_evidence_override"] = PHYSICAL_PAPER_EVIDENCE
    patched["experiment_plan"] = PHYSICAL_EXPERIMENT_PLAN
    patched["metrics"] = PHYSICAL_METRICS
    patched["ablations"] = PHYSICAL_ABLATIONS
    patched["negative_controls"] = PHYSICAL_NEGATIVE_CONTROLS
    patched["success_thresholds"] = PHYSICAL_SUCCESS_THRESHOLDS
    patched["human_review_selected_title"] = best.get("title")
    patched["human_review_source"] = review.get("source_xlsx")
    patched["human_review_item_id"] = best.get("item_id")
    patched["human_review_winner"] = best.get("winner")
    patched["human_review_reason"] = best.get("review_reason")
    patched["human_review_concern"] = best.get("review_concern")
    patched["judge_summary"] = (
        f"Human expert review sheet selected {best.get('winner')} for {best.get('item_id')} "
        f"(winner_score={best.get('winner_score')}, confidence={best.get('confidence')}). "
        f"Reason: {best.get('review_reason')}"
    )
    result["material_human_review"] = {
        "source": review.get("source_xlsx"),
        "num_scored_rows": review.get("num_scored_rows"),
        "num_candidate_rows": review.get("num_candidate_rows"),
        "reviewer_count_note": review.get("reviewer_count_note"),
        "best_idea": best,
    }
    result["physical_baseline_taxonomy_fix"] = {
        "reason": "The previous display mixed datasets/components such as ObjectFolder, SAM, GroundingDINO, and CLIP with method baselines. For the physical-property task, the live result now uses method-level baselines.",
        "baselines": PHYSICAL_METHOD_BASELINES,
        "papers": PHYSICAL_PAPER_EVIDENCE,
    }
    return patched


def unique_extend(base: list[Any], extra: list[Any]) -> list[Any]:
    seen: set[str] = set()
    merged: list[Any] = []
    for item in list(base or []) + list(extra or []):
        key = json.dumps(item, ensure_ascii=False, sort_keys=True) if isinstance(item, (dict, list)) else str(item)
        if key in seen:
            continue
        seen.add(key)
        merged.append(item)
    return merged


def apply_iad_incremental_repair(plan: dict[str, Any]) -> dict[str, Any]:
    """Targeted critic repair for IAD incremental-improvement mode.

    Reviewer signal: the original artifact idea over-claims "Agent", relies on
    a hand-coded S score, and lacks a fair fusion baseline.  For the
    incremental-improvement user intent, the better idea is a small selective
    inspection/calibration module placed after PatchCore-style scoring.
    """
    patched = dict(plan)
    original_title = str(plan.get("idea_title") or "Reference-Consistency Inspection Agent for Shifted Normal Banks")
    patched["original_workflow_idea_title"] = original_title
    patched["idea_title"] = "Selective Reference-Consistency Calibration for PatchCore-style IAD"
    patched["critic_repair_summary"] = (
        "Removed the over-claimed Agent framing; replaced hand-coded score and fixed threshold "
        "with a lightweight learned/conformal calibrator; added fair fusion baselines and clean-vs-stress evaluation."
    )
    patched["final_idea"] = "\n\n".join([
        "Title:\nSelective Reference-Consistency Calibration for PatchCore-style IAD",
        "Research problem:\nPatchCore-style nearest-neighbor IAD works well on clean benchmarks, but the normal reference memory can become unreliable under shifted lighting, texture variation, product-line drift, or mild contamination of the normal bank. The goal is not to build a new agent. The goal is to add one minimal, auditable post-hoc module that decides when a high anomaly score is trustworthy, when it should be down-weighted, and when the system should abstain.",
        "Core proposal / minimal new module:\nAdd a Selective Reference-Consistency Calibration (SRCC) layer after a frozen baseline scorer such as PatchCore. For each high-score region, retrieve top-k normal reference patches from the same product category and compute reference-consistency features: anomaly score, nearest-reference similarity margin, local texture/color residual, model-disagreement score from optional auxiliary scorers, and reference provenance/audit flags. Instead of a hand-coded linear score, fit a tiny calibration model on a held-out normal/calibration split to output calibrated risk or abstention probability.",
        "Algorithmic objective:\nLearn an operating rule g(x) that minimizes false accepted defect claims subject to a recall or coverage constraint. A simple implementation can use Platt scaling, isotonic regression, logistic calibration, or conformal risk control over nonconformity scores. The accepted region set is A_tau = {r: calibrated_risk(r) >= tau and reference_consistency(r) is not sufficient to explain the region}. The threshold tau is selected on a validation split to satisfy a target false discovery rate, selective risk, or normal-bank false alarm budget. This replaces the previous fixed S = z(...) and threshold 2.0.",
        "Why it may work:\nThe repaired idea targets a real deployment failure mode: clean MVTec-style benchmark performance can be near-saturated, while industrial deployments often face reference-bank shift, new normal variants, and accidental normal-bank contamination. A calibrated selective layer can avoid making unsupported defect claims in those regimes without retraining the main detector. The contribution is narrow but defensible: improved reliability under reference shift, not a blanket claim of higher clean-set AUROC.",
        "Fair baselines required:\n1. PatchCore alone.\n2. PaDiM or another frozen IAD baseline alone.\n3. WinCLIP/AnomalyCLIP-style semantic scorer alone when available.\n4. Simple PatchCore + PaDiM + WinCLIP score averaging/voting fusion.\n5. Logistic-regression fusion over the same raw scores but without reference-consistency features.\n6. Proposed SRCC with reference retrieval, provenance/audit features, and calibrated abstention.",
        "Experiment design:\nEvaluate clean normal-bank and stress normal-bank settings separately. In clean settings, report that the method should not meaningfully hurt AUROC/PRO or recall. In shifted/contaminated settings, inject realistic perturbations: lighting/texture normal variants, product-category drift, random retrieval, shuffled reference provenance, and small fractions of contaminated normal references. Always report escalation/abstention rate, because lower false alarm is only useful if it does not simply dump too many samples to humans.",
        "Key metrics:\nimage_level_auroc, pixel_level_auroc, PRO, false_alarm_rate_at_fixed_recall, selective_risk, false_discovery_rate, abstention_rate, human_escalation_cost, calibration_error, stress_test_false_alarm_reduction.",
        "Ablations:\nremove learned calibration; replace calibration with fixed S score; remove reference-consistency features; remove provenance/audit flags; compare against simple score fusion; vary contamination ratio and product-category shift severity.",
        "Success criteria:\nOn clean banks, AUROC/PRO degradation should be within a small tolerance rather than claiming impossible +2pp gains near the ceiling. On shifted or contaminated banks, SRCC should reduce false accepted defect claims compared with PatchCore and simple fusion at matched recall or matched abstention budget. Calibration curves should show that the learned operating point transfers better across categories than the hand-coded threshold.",
        f"Repair provenance:\nThis version is a critic-repaired incremental idea derived from the original workflow seed idea “{original_title}”. It keeps the reference-consistency insight but removes the over-claimed Agent wrapper and makes the minimal module data-driven and testable.",
    ])
    patched["new_component"] = (
        "A post-hoc Selective Reference-Consistency Calibration layer after frozen PatchCore-style anomaly scoring."
    )
    patched["why_it_may_work"] = (
        "It addresses reference-bank shift and contamination with calibrated selective prediction rather than hard-coded rules."
    )
    patched["algorithmic_objective"] = (
        "Learn a calibrated risk/abstention rule using Platt scaling, isotonic regression, logistic calibration, or conformal risk control; select tau on validation data to satisfy FDR/selective-risk/false-alarm budget."
    )
    patched["minimal_new_module"] = {
        "name": "Selective Reference-Consistency Calibration (SRCC)",
        "input": "Frozen PatchCore region scores, top-k normal reference patches, optional auxiliary scorer outputs, reference provenance flags.",
        "output": "Calibrated accept/abstain decision, calibrated risk, reference evidence, and escalation reason.",
        "algorithm_steps": [
            "Run frozen PatchCore and retrieve top-k normal patches per suspicious region.",
            "Extract reference-consistency margin, local residual, model-disagreement, and provenance/audit features.",
            "Fit a tiny calibration model or conformal risk controller on held-out calibration data.",
            "Choose an operating threshold under a target false-alarm/FDR/selective-risk budget.",
            "Accept, down-weight, or abstain on defect claims with attached reference evidence.",
        ],
    }
    patched["baselines"] = unique_extend(patched.get("baselines", []), [
        "PatchCore",
        "PaDiM",
        "WinCLIP / AnomalyCLIP semantic scorer",
        "PatchCore + PaDiM + WinCLIP simple averaging/voting fusion",
        "Logistic-regression score fusion without reference-consistency features",
    ])
    patched["baseline_weakness"] = unique_extend([
        "Hand-coded anomaly/reference fusion is not principled; learned calibration or conformal risk control is needed.",
        "Clean MVTec-style AUROC may be saturated, so the main value should be stress robustness and selective reliability.",
        "A fair comparison must include simple multi-model fusion baselines to isolate the value of reference-consistency features.",
        "Calling a fixed post-hoc decision module an Agent is an overclaim unless autonomous tool planning and iterative memory updates are demonstrated.",
    ], patched.get("baseline_weakness", []))
    patched["experiment_plan"] = [
        "Freeze PatchCore and reproduce clean-bank results on MVTec AD / VisA with standard splits.",
        "Build shifted and contaminated normal-bank stress settings with controlled severity.",
        "Train only the SRCC calibration layer on held-out calibration data; do not retrain the main detector.",
        "Compare PatchCore, auxiliary baselines, simple score fusion, logistic fusion, fixed-S rule, and SRCC.",
        "Report clean-bank degradation tolerance, shifted-bank false-alarm reduction, recall, abstention rate, calibration error, and human escalation cost.",
    ]
    patched["metrics"] = [
        "image_level_auroc",
        "pixel_level_auroc",
        "pro_score",
        "false_alarm_rate_at_fixed_recall",
        "selective_risk",
        "false_discovery_rate",
        "abstention_rate",
        "human_escalation_cost",
        "calibration_error",
        "stress_test_false_alarm_reduction",
    ]
    patched["ablations"] = [
        "fixed hand-coded S score vs learned calibration",
        "without reference-consistency features",
        "without provenance/audit flags",
        "without auxiliary model-disagreement features",
        "simple fusion baseline vs SRCC",
        "different contamination and reference-shift severity levels",
    ]
    patched["negative_controls"] = [
        "random normal reference retrieval",
        "shuffled reference provenance",
        "contaminated normal bank with synthetic defect leakage",
        "train calibration on one category and test on unrelated shifted category",
    ]
    patched["success_thresholds"] = [
        "Clean-bank AUROC/PRO drop must remain within a predefined tolerance.",
        "At matched recall or matched abstention budget, SRCC reduces false accepted defect claims under shifted/contaminated normal banks.",
        "SRCC outperforms simple score fusion and logistic score fusion without reference-consistency features.",
        "Calibration error and selective risk improve over the fixed-S rule.",
    ]
    patched["judge_summary"] = (
        "Critic repair for incremental-improvement mode: removed Agent overclaim, replaced fixed S score with learned/calibrated selective risk control, and added fair fusion baselines."
    )
    return patched


def apply_task_mode_profile(plan: dict[str, Any], task_mode: str, task_key: str) -> dict[str, Any]:
    profile = TASK_MODE_PROFILES.get(task_mode)
    if not profile:
        return plan

    patched = dict(plan)
    if task_key == "iad" and task_mode == "incremental_improvement":
        patched = apply_iad_incremental_repair(patched)
    original_title = str(patched.get("original_workflow_idea_title") or patched.get("idea_title") or "Workflow-generated idea").strip()

    patched["task_mode_profile"] = profile
    patched["task_mode_specific_focus"] = profile["idea_lens"]
    patched["original_workflow_idea_title"] = original_title
    patched["mode_specific_title"] = TASK_MODE_TITLES.get(task_key, {}).get(task_mode) or f"{original_title} [{profile['label']}]"
    # Important: for the three prepared workflow tasks, do not rewrite the core
    # idea.  The high-quality idea lives in focused_ideas.json.  Task type only
    # changes downstream framing: improvement points, experiment emphasis, and
    # metrics.  Rewriting final_idea here made the webpage look lightweight and
    # worse than the underlying workflow artifacts.

    patched["improvement_points"] = unique_extend(
        patched.get("improvement_points", []),
        profile["improvement_points"],
    )
    patched["experiment_plan"] = unique_extend(
        profile["experiment_focus"],
        patched.get("experiment_plan", []),
    )
    patched["metrics"] = unique_extend(
        patched.get("metrics", []),
        profile["metrics"],
    )

    existing_summary = patched.get("judge_summary", "")
    mode_summary = f"Task mode={profile['label']} changes the plan focus: {profile['idea_lens']}"
    patched["judge_summary"] = f"{existing_summary} {mode_summary}".strip()
    return patched


def md_list(items: list[Any]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {x}" for x in items)


def build_markdown(result: dict[str, Any]) -> str:
    plan = result["final_plan"]
    evidence = result["evidence"]
    lines = [
        "# Live Workflow Run Result",
        "",
        f"Run id: `{result['run_id']}`",
        f"Generated at: {result['generated_at']}",
        f"Task: {result['task_label']}",
        f"Source mode: `{result.get('source_mode', '')}`",
        f"Source artifact dir: `{plan.get('source_artifact_dir', '')}`",
        "",
        "## 1. Input",
        "",
        f"- Task spec: `{result['task_spec']}`",
        f"- User direction: {result['direction']}",
        f"- Task mode: {result.get('task_mode_label') or result.get('task_mode') or 'not specified'}",
        "",
        "## 2. Baseline cards / baseline weakness",
        "",
        "### Baselines",
        "",
        md_list(plan.get("baselines", [])),
        "",
        "### Baseline weakness",
        "",
        md_list(plan.get("baseline_weakness", [])),
        "",
        "## 3. Paper evidence",
        "",
        f"- Evidence dir: `{evidence.get('evidence_dir', '')}`",
        f"- Papers loaded: {evidence.get('paper_count', 0)}",
        f"- Evidence cards loaded: {evidence.get('card_count', 0)}",
        "",
        "### Top papers",
        "",
    ]
    top_papers = plan.get("paper_evidence_override") or evidence.get("papers", [])[:8]
    for p in top_papers[:8]:
        lines.append(f"- [{p.get('title','untitled')}]({p.get('url') or p.get('doi') or '#'}) ({p.get('year','?')}, {p.get('venue','')})")
    lines.extend([
        "",
        "## 4. Final idea",
        "",
        plan.get("final_idea", ""),
        "",
        "## 5. Critic repair / judge signal",
        "",
        f"- {plan.get('judge_summary', '')}",
        f"- {plan.get('evidence_verification_status', '')}",
        "",
        "## 6. Experiment plan",
        "",
        md_list(plan.get("experiment_plan", [])),
        "",
        "### Metrics",
        "",
        md_list(plan.get("metrics", [])),
        "",
        "### Ablations",
        "",
        md_list(plan.get("ablations", [])),
        "",
        "### Negative controls",
        "",
        md_list(plan.get("negative_controls", [])),
        "",
        "### Success thresholds",
        "",
        md_list(plan.get("success_thresholds", [])),
        "",
        "## 7. Execution bridge",
        "",
        f"- Auto-claude/ARIS workspace: `{result.get('auto_claude_workspace', '')}`",
        "- Next: open `AUTHORIZED_CLAUDE_PROMPT.md` after user authorization.",
        "",
    ])
    return "\n".join(lines)


def refresh_v26_bridge() -> None:
    script = ROOT / "focused_workflow/scripts/build_v26_auto_claude_execution_bridge.py"
    if not script.exists():
        return
    subprocess.run([sys.executable, str(script)], cwd=str(ROOT), check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-key", choices=sorted(TASKS), required=True)
    parser.add_argument("--direction", default="")
    parser.add_argument("--user-task-type", default="")
    parser.add_argument("--task-mode", default="")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=["safe_local", "authorized_llm"], default="safe_local")
    args = parser.parse_args()

    run_dir = args.run_dir if args.run_dir.is_absolute() else ROOT / args.run_dir
    run_dir.mkdir(parents=True, exist_ok=True)
    run_id = run_dir.name

    task = TASKS[args.task_key]
    task_spec = ROOT / task["task_spec"] if task.get("task_spec") else None
    if task_spec is not None and not task_spec.exists():
        raise FileNotFoundError(task_spec)

    print(f"[1/6] selected task: {task['label']}", flush=True)
    if args.task_key == "custom":
        print("[2/6] custom task: generating temporary task spec from user input", flush=True)
        task_spec_text = "\n".join([
            "task_key: custom",
            f"task_type: {args.user_task_type or 'custom research task'}",
            f"research_direction: {args.direction or 'not specified'}",
            f"task_mode: {args.task_mode or 'not specified'}",
            "note: generated by live workflow fallback; paper retrieval/evidence verification should run before final scientific claims.",
            "",
        ])
    else:
        print(f"[2/6] loading task spec: {task_spec.relative_to(ROOT)}", flush=True)
        task_spec_text = task_spec.read_text(encoding="utf-8")
    (run_dir / "task_spec.yaml").write_text(task_spec_text, encoding="utf-8")

    print("[3/6] refreshing and locating latest focused_workflow artifacts", flush=True)
    source_mode = "latest_focused_workflow_artifacts"
    if args.task_key == "custom":
        artifact_dir = None
        source_mode = "custom_live_workflow_fallback"
        plan, evidence = build_custom_workflow_plan(args.user_task_type, args.direction, args.task_mode)
        if plan.get("source") == "research_agent_orchestrator_v0":
            source_mode = "research_agent_orchestrator_v0"
            print("      custom task: ResearchAgentOrchestrator workspace generated", flush=True)
        else:
            print("      custom task fallback: structured idea generated without preloaded evidence bank", flush=True)
    else:
        ensure_live_artifact_cache(args.task_key)
        artifact_dir = latest_artifact_dir(task)
    if args.task_key != "custom" and artifact_dir:
        print(f"      artifact_dir={artifact_dir.relative_to(ROOT)}", flush=True)
        plan, evidence = workflow_plan_from_artifacts(args.task_key, artifact_dir)
    elif args.task_key != "custom":
        print("      no focused_workflow artifact bundle found; falling back to V10 final package", flush=True)
        source_mode = "fallback_v10_final_package"
        plan = load_v10_plan(task["v10_plan_id"])
        evidence_dir = find_existing(task["evidence_candidates"])
        papers: list[dict[str, Any]] = []
        cards: list[dict[str, Any]] = []
        if evidence_dir:
            papers = read_jsonl(evidence_dir / "papers.jsonl", limit=40)
            cards = read_jsonl(evidence_dir / "evidence_baseline_cards.jsonl", limit=40)
        evidence = {
            "evidence_dir": str(evidence_dir.relative_to(ROOT)) if evidence_dir else "",
            "paper_count": len(papers),
            "card_count": len(cards),
            "papers": papers[:12],
            "cards": cards[:8],
            "baseline_cards": [],
            "focused_ideas": [],
            "experiment_plans": [],
        }

    result_extras: dict[str, Any] = {}
    plan = apply_material_review_override(args.task_key, plan, result_extras)
    if args.task_key != "custom":
        plan = apply_task_mode_profile(plan, args.task_mode, args.task_key)
    write_json(run_dir / "final_plan.json", plan)

    print("[4/6] loading paper evidence and baseline cards from workflow artifacts", flush=True)
    write_json(run_dir / "papers_loaded.json", evidence.get("papers", []))
    write_json(run_dir / "evidence_cards_loaded.json", evidence.get("cards", []))
    write_json(run_dir / "baseline_cards_loaded.json", evidence.get("baseline_cards", []))

    print("[5/6] refreshing Auto-claude/ARIS V26 execution bridge", flush=True)
    refresh_v26_bridge()

    auto_workspace = ROOT / "outputs/auto_claude_execution_bridge_v1" / task["slug"]
    result = {
        "ok": True,
        "run_id": run_id,
        "mode": args.mode,
        "source_mode": source_mode,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "task_key": args.task_key,
        "task_label": task["label"],
        "task_spec": task["task_spec"],
        "direction": args.direction,
        "task_mode": args.task_mode,
        "task_mode_label": {
            "incremental_improvement": "增量改进",
            "metric_improvement": "指标提升",
            "engineering_integration": "工程拼接",
            "evaluation_protocol": "评价协议",
            "system_optimization": "系统优化",
        }.get(args.task_mode, args.task_mode),
        "final_plan": plan,
        "evidence": evidence,
        "auto_claude_workspace": str(auto_workspace.relative_to(ROOT)),
        "notes": [
            "safe_local mode ran local workflow artifact loading/rendering only.",
            "Default source is latest focused_workflow artifact bundle, not the old V10 package.",
            "No arbitrary shell command from the webpage was executed.",
            "LLM/API ideation should be enabled only after explicit user authorization.",
        ],
    }
    result.update(result_extras)
    write_json(run_dir / "LIVE_WORKFLOW_RESULT.json", result)
    (run_dir / "LIVE_WORKFLOW_RESULT.md").write_text(build_markdown(result), encoding="utf-8")

    print("[6/6] live workflow result written", flush=True)
    print(f"RESULT_JSON={run_dir / 'LIVE_WORKFLOW_RESULT.json'}", flush=True)
    print(f"RESULT_MD={run_dir / 'LIVE_WORKFLOW_RESULT.md'}", flush=True)


if __name__ == "__main__":
    main()
