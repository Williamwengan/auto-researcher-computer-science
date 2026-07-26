#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V0.8 cross-task benchmark robustness summary for focused idea generation.

The five CV directions are benchmark samples, not mutually exclusive project
candidates. This script summarizes how the idea-generation module behaves across
those task specs, tracks evidence maturity, and recommends what to run next.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional


@dataclass
class BenchmarkTask:
    task_id: str
    name_cn: str
    task_spec: str
    focus: str
    benchmark_role: str
    current_evidence: str
    blind_ab: Optional[str] = None
    claim_verification: Optional[str] = None
    idea_quality: Optional[str] = None
    evidence_maturity: str = "task_spec_ready"
    presentation_role: str = "benchmark sample"
    next_action: str = "run full v0.5-v0.7 loop"
    notes: List[str] = field(default_factory=list)


def benchmark_tasks() -> List[BenchmarkTask]:
    return [
        BenchmarkTask(
            task_id="01",
            name_cn="物理属性预测",
            task_spec="focused_workflow/tasks/benchmark_cv/01_physical_property_prediction.yaml",
            focus="object-level physical property prediction from 2D indoor scene images",
            benchmark_role="检验 idea generation 是否能处理跨模态、数值属性、弱标签、uncertainty calibration 和机制可解释性。",
            current_evidence="已完成 v0.6 blind A/B、v0.7 claim verification，并形成 v1 -> v2 二次修复闭环。",
            blind_ab="v2: 6 reviewers, 18/18 after wins, win rate 1.0, agreement 1.0",
            claim_verification="v2 evidence-card repair: papers 51, claims 15, pass rate 1.0",
            idea_quality="v1 repair 暴露机制错配；v2 将 interval mapper、localized material evidence verifier、proposal uncertainty propagation 拆开后显著提升。",
            evidence_maturity="full_closed_loop",
            presentation_role="机制修复与 failure diagnosis 的最强案例",
            next_action="保留为技术亮点样例；继续补充可复现实验数据或 proxy label 说明。",
        ),
        BenchmarkTask(
            task_id="02",
            name_cn="Human Motion 生成",
            task_spec="focused_workflow/tasks/benchmark_cv/02_human_motion_generation.yaml",
            focus="human motion generation from text, scene, pose, or action conditions",
            benchmark_role="检验 idea generation 是否能处理生成式任务、物理一致性、scene affordance、motion metrics 和可控性。",
            current_evidence="已作为 5-task benchmark task spec 准备；早期 v0.4 记录中出现过 idea-quality / local judge 评估，尚未完成 v0.6/v0.7 闭环。",
            blind_ab="pending full v0.6 blind A/B",
            claim_verification="pending v0.7 reference claim verification",
            idea_quality="v0.4 早期评估显示可生成高分 motion idea，但还需要 evidence-grounded repair 和 reference verification。",
            evidence_maturity="partial_idea_quality",
            presentation_role="跨到生成式时序任务的泛化样本",
            next_action="作为下一轮必跑任务之一，补齐 evidence retrieval、targeted repair、blind A/B 和 claim verification。",
        ),
        BenchmarkTask(
            task_id="03",
            name_cn="室内单图 3D 场景生成",
            task_spec="focused_workflow/tasks/benchmark_cv/03_indoor_scene_generation.yaml",
            focus="single-image 3D indoor scene generation and reconstruction",
            benchmark_role="检验 idea generation 是否能处理高度歧义的 3D/geometry/generation 任务，以及 evidence-grounded ideation 对复杂论文脉络的约束能力。",
            current_evidence="已完成 seeded evidence bank、v0.6 blind A/B 和 v0.7 evidence-card repair。",
            blind_ab="3 reviewers, 9/9 after wins, win rate 1.0, agreement 1.0",
            claim_verification="evidence-card repair: papers 18, claims 18, pass rate 1.0",
            idea_quality="视觉效果直观，但工程实现重；适合证明 workflow 可迁移到复杂生成/重建类任务。",
            evidence_maturity="full_closed_loop_seeded_evidence",
            presentation_role="视觉化与复杂任务泛化样例",
            next_action="保留 seeded evidence bank 披露；不把它表述为唯一主任务。",
            notes=["室内 3D 初始联网检索 evidence bank 为空，后续使用 seeded evidence bank，最终材料必须显式说明。"],
        ),
        BenchmarkTask(
            task_id="04",
            name_cn="鲁棒 3D 重建",
            task_spec="focused_workflow/tasks/benchmark_cv/04_3d_reconstruction.yaml",
            focus="robust 3D reconstruction from images, videos, or sparse views",
            benchmark_role="检验 idea generation 是否能处理 geometry metrics、sparse-view robustness、pose noise、uncertainty 和工程部署约束。",
            current_evidence="已作为 5-task benchmark task spec 准备；尚未完成完整 v0.5-v0.7 闭环。",
            blind_ab="pending full v0.6 blind A/B",
            claim_verification="pending v0.7 reference claim verification",
            idea_quality="pending structured run summary",
            evidence_maturity="task_spec_ready",
            presentation_role="下一轮 held-out benchmark 样本",
            next_action="作为 held-out task 跑一次完整 pipeline，用来证明不是只对前三个样本调参。",
        ),
        BenchmarkTask(
            task_id="05",
            name_cn="工业异常检测 IAD + Agent",
            task_spec="focused_workflow/tasks/benchmark_cv/05_iad_agent_workflow.yaml",
            focus="industrial anomaly detection with agentic inspection workflow",
            benchmark_role="检验 idea generation 是否能处理 agent workflow、retrieval、verification loop、human escalation 和工业指标。",
            current_evidence="已完成 v0.5 targeted repair、v0.6 blind A/B 和 v0.7 claim verification。",
            blind_ab="3 reviewers, 7/9 after wins, win rate 0.778, agreement 0.778",
            claim_verification="papers 24, claims 21, pass rate 0.857, unsupported 0, manual 3",
            idea_quality="工程闭环短，适合作为现场演示样例，但不是项目唯一方向。",
            evidence_maturity="full_closed_loop",
            presentation_role="agent/workflow 落地样例",
            next_action="用于演示 workflow 字段结构和可运行性；同时保留 manual-check claims 的诚实不确定性。",
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


def status_for_spec(root: Path, task: BenchmarkTask) -> str:
    return "已找到" if (root / task.task_spec).exists() else "未找到"


def make_report(root: Path, tasks: List[BenchmarkTask]) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    overview_rows = [
        [
            task.task_id,
            task.name_cn,
            task.focus,
            task.evidence_maturity,
            task.presentation_role,
            status_for_spec(root, task),
        ]
        for task in tasks
    ]
    evidence_rows = [
        [
            task.name_cn,
            task.current_evidence,
            task.blind_ab or "pending",
            task.claim_verification or "pending",
            task.next_action,
        ]
        for task in tasks
    ]
    benchmark_role_rows = [
        [task.name_cn, task.benchmark_role]
        for task in tasks
    ]
    notes = []
    for task in tasks:
        notes.extend(task.notes)

    return f"""# V0.8 跨任务 Benchmark 鲁棒性与候选 Idea 汇总报告

生成时间：{generated_at}

生成脚本：`focused_workflow/scripts/select_final_candidates_v0_8.py`

## 关键纠偏

V0.8 不是为了从多个任务方向里选一个作为项目本体。`focused_workflow/tasks/benchmark_cv/` 下的 5 个方向是 benchmark samples，用来测试同一个 idea-generation workflow 在不同任务形态上的泛化能力、细粒度程度和鲁棒性。

因此，正确表述应为：

> 我们不是针对某一个 CV 任务做单点算法，而是在 ResearchArena baseline 之上构建一个跨任务的 AI 科研自动化 workflow。5 个 CV task spec 是 benchmark，用来验证 idea generation 是否能在不同任务上稳定地产生 baseline-grounded、可实现、可评价、可修复、证据可校验的科研 idea。

V0.8 的作用也相应改为：汇总 5 个 benchmark 样本的覆盖情况、已验证证据、待补齐闭环，并选择适合在答辩中展示的代表性 evidence slices，而不是宣布“最终只做某一个任务”。

## 五个 Benchmark 样本

{md_table(["ID", "任务", "focus", "当前证据成熟度", "展示角色", "task spec"], overview_rows)}

## 每个任务在 Benchmark 中测试什么

{md_table(["任务", "测试的 idea-generation 能力"], benchmark_role_rows)}

## 已有证据与待补齐闭环

{md_table(["任务", "当前证据", "v0.6 blind A/B", "v0.7 claim verification", "下一步"], evidence_rows)}

## 现在能主张什么

当前可以主张的是：

- 系统已经把 ResearchArena baseline 的开放式 proposal generation 改造成结构化、可评审、可排序、可修复的 idea-generation workflow。
- idea 输出不再只是一段想法，而是包含 baseline cards、focused ideas、experiment plan、minimal_new_module、algorithmic_objective、required scripts/data、expected tables/figures、success thresholds 和 negative controls。
- 在三个代表性任务上已经形成较强闭环：IAD + Agent、物理属性预测、室内单图 3D 场景生成。
- 物理属性方向证明了系统不只是“修饰文本”：v1 repair 失败后，multi-LLM blind judge 和 reviewer rationale 发现机制错配，v2 targeted repair 后 18/18 after wins，reference claim verification pass rate 达到 1.0。
- 室内 3D 方向证明 workflow 可迁移到复杂生成/重建任务，但必须诚实披露 seeded evidence bank。
- IAD + Agent 方向证明 workflow 可以落到 agentic inspection 这类工程型任务，但它只是展示样例，不是项目唯一方向。

当前不应主张的是：

- 不应说项目最终只选择 IAD、物理属性或室内 3D 之一作为唯一研究方向。
- 不应把五个 benchmark 样本当作互斥候选赛道。
- 不应在 02 Human Motion 和 04 3D Reconstruction 尚未完成 v0.6/v0.7 闭环前，声称 5/5 任务都已经完整验证。
- 不应声称全球意义上的 idea generation SOTA，除非后续补齐与 ResearchArena baseline、Auto-claude baseline、人工/LLM judge 的系统对比。更稳妥的表述是：在当前 benchmark 样本上，相比原 baseline，idea generation 的结构化、可实现性、修复能力和证据校验能力显著增强。

## 答辩中的正确展示策略

答辩时可以展示三个代表性样例，但话术必须是“benchmark evidence slices”：

1. 物理属性预测：展示 failure diagnosis and second-round repair，证明 idea generation 有自我诊断和 targeted repair 能力。
2. IAD + Agent：展示 workflow 可运行字段和工程任务适配能力，证明输出不是空泛 idea。
3. 室内单图 3D：展示复杂生成/重建任务上的 evidence-grounded ideation，并透明披露 seeded evidence bank。

这三个样例不是三选一，而是共同支撑一个主张：同一个 pipeline 可以跨任务生成更细粒度、更可执行、更可验证的科研 idea。

## 下一步工作建议

下一阶段建议从“选方向”转成“补齐 benchmark 与端到端工作流”：

1. 对 02 Human Motion 和 04 3D Reconstruction 跑完整 v0.5 -> v0.6 -> v0.7 闭环，避免 benchmark 只停留在 3 个任务。
2. 增加一个跨任务汇总脚本，统一输出每个 task 的 baseline_cards、focused_ideas、repair status、blind A/B、claim verification、unsupported/manual-check claims。
3. 把 idea-generation 模块作为核心贡献单独写清楚：输入 task spec，输出高质量 structured idea set，并通过 judge / evidence verification 闭环评估。
4. 再推进整个 workflow 端到端运行：idea generation -> experiment planning -> code/data artifact planning -> evaluation -> repair -> final report。
5. 最终比赛材料应突出“任何给定任务方向都能进入同一套科研自动化流程”，而不是“我们挑了一个任务做算法”。

## 建议更新后的项目定位

推荐项目定位：

> 面向 AI4Sci 的跨任务科研 idea generation 与自动化验证工作流：基于 ResearchArena baseline，实现 baseline-grounded ideation、targeted repair、multi-LLM blind evaluation 与 reference claim verification。

推荐核心卖点：

> 不管输入的是物理属性预测、Human Motion、室内 3D、3D 重建还是 IAD Agent，系统都按照统一 schema 生成细粒度 idea，并通过 repair、judge 和 evidence verification 检查 idea 是否真的更好、更可实现、更有论文支撑。

## 备注

{bullet_list(notes) if notes else "- 无"}
"""


def write_json_summary(output: Path, tasks: List[BenchmarkTask]) -> None:
    payload = {
        "version": "v0.8",
        "purpose": "cross_task_benchmark_robustness_for_idea_generation",
        "not_a_single_task_selector": True,
        "benchmark_tasks": [asdict(task) for task in tasks],
        "recommended_framing": {
            "project_objective": "robust cross-task AI research idea-generation workflow",
            "representative_evidence_slices": [
                "physical_property_failure_diagnosis_and_v2_repair",
                "iad_agent_workflow_structured_demo",
                "indoor3d_seeded_evidence_grounded_ideation",
            ],
            "next_tasks_to_complete": ["02_human_motion_generation", "04_3d_reconstruction"],
        },
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    script_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Summarize v0.8 cross-task benchmark robustness.")
    parser.add_argument("--repo-root", type=Path, default=script_root, help="Repository root.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Markdown output path. Defaults to competition_submission/V08_FINAL_CANDIDATE_SELECTION_CN.md.",
    )
    parser.add_argument("--json-output", type=Path, default=None, help="Optional JSON summary output path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.repo_root.resolve()
    output = args.output or (root / "competition_submission" / "V08_FINAL_CANDIDATE_SELECTION_CN.md")
    tasks = benchmark_tasks()

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(make_report(root, tasks), encoding="utf-8")

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        write_json_summary(args.json_output, tasks)

    print(f"Wrote {output}")
    print("V0.8 framing: cross-task benchmark robustness, not single-task competition selection.")
    print("Benchmark tasks: 01 physical property, 02 human motion, 03 indoor 3D, 04 3D reconstruction, 05 IAD agent")
    print("Next: complete v0.5-v0.7 loops for 02 human motion and 04 3D reconstruction; then run end-to-end workflow.")


if __name__ == "__main__":
    main()
