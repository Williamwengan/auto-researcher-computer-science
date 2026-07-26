#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build v0.9 deliverables for the idea-generation core benchmark.

V0.9 does not add new benchmark tasks. It packages the three already validated
samples into a competition-facing story about the idea-generation module:
task_spec -> structured idea -> targeted repair -> blind A/B judge ->
reference claim verification.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable, List


@dataclass
class EvidenceSlice:
    task_id: str
    task_name: str
    role: str
    proves: str
    blind_ab: str
    claim_verification: str
    repair_story: str
    limits: List[str] = field(default_factory=list)
    demo_use: str = ""


def evidence_slices() -> List[EvidenceSlice]:
    return [
        EvidenceSlice(
            task_id="01",
            task_name="物理属性预测",
            role="failure diagnosis and second-round repair",
            proves="idea generation 模块能发现机制错配，并通过 targeted repair 生成更一致、更可实现的 idea。",
            blind_ab="v2: 6 reviewers, 18/18 after wins, win rate 1.0, agreement 1.0",
            claim_verification="v2 evidence-card repair: papers 51, claims 15, pass rate 1.0",
            repair_story=(
                "v1 repair 后 after win rate 只有 0.556。reviewer rationale 指出 Idea 2 和 Idea 3 "
                "错误套用了 Idea 1 的 interval-mapper loss。v2 将三个 idea 的机制拆开："
                "interval mapper、localized material evidence verifier、proposal uncertainty propagation。"
            ),
            limits=[
                "真实物理属性标签和可控实验验证仍然较难。",
                "适合证明 idea repair 能力，不应包装成已经完成物理属性预测算法 SOTA。",
            ],
            demo_use="作为最强技术闭环案例，展示系统能从失败中定位原因并二次修复。",
        ),
        EvidenceSlice(
            task_id="03",
            task_name="室内单图 3D 场景生成",
            role="complex generation/reconstruction generalization",
            proves="idea generation 模块能迁移到复杂 3D/generation/reconstruction 任务，并用 evidence bank 限制空泛想法。",
            blind_ab="3 reviewers, 9/9 after wins, win rate 1.0, agreement 1.0",
            claim_verification="evidence-card repair: papers 18, claims 18, pass rate 1.0",
            repair_story=(
                "初始联网检索阶段 evidence bank 为空，后续构造 seeded evidence bank，覆盖 Text2Room、"
                "SceneScape、WonderJourney、DUSt3R、MASt3R、3D Gaussian Splatting、NeRF、HorizonNet、"
                "MiDaS、3D-FRONT、Matterport3D、ScanNet、Structured3D、Hypersim 等代表性证据。"
            ),
            limits=[
                "使用 seeded evidence bank，最终材料必须透明披露。",
                "完整 3D 工程实现较重，当前主要作为 idea generation 泛化样例。",
            ],
            demo_use="作为视觉化和复杂任务泛化样例，证明 workflow 不局限于工程 agent 任务。",
        ),
        EvidenceSlice(
            task_id="05",
            task_name="工业异常检测 IAD + Agent",
            role="agentic workflow and implementation readiness",
            proves="idea generation 模块能处理 agent workflow、retrieval、verification loop、human escalation 和工业指标。",
            blind_ab="3 reviewers, 7/9 after wins, win rate 0.778, agreement 0.778",
            claim_verification="papers 24, claims 21, pass rate 0.857, unsupported 0, manual 3",
            repair_story=(
                "targeted repair 将 IAD idea 约束到 normal reference retrieval、reference consistency score、"
                "cross-model disagreement、evidence-grounded report checker、negative controls 和 success thresholds。"
            ),
            limits=[
                "仍有 3 个 needs_manual_check claim，适合保留为诚实不确定性。",
                "不要把它写成项目唯一方向；它是 agent/workflow 类任务的代表样本。",
            ],
            demo_use="作为工程可读性样例，展示输出字段如何服务实验计划和后续 workflow。",
        ),
    ]


PIPELINE_STAGES = [
    ["v0.2", "固定 task_spec 输入和结构化输出", "baseline_cards.jsonl、focused_ideas.json、experiment_plan.json"],
    ["v0.3", "让 idea 可实现", "minimal_new_module、algorithmic_objective、required scripts/data、expected tables/figures、success thresholds、negative controls"],
    ["v0.4", "加入 idea quality scoring 和 judge 规划", "把 idea 从“生成”推进到“可评价”"],
    ["v0.5", "evidence-grounded ideation + targeted repair", "paper evidence、evidence baseline cards、evidence critic repair"],
    ["v0.6", "multi-LLM anonymous blind A/B judge", "验证 repair 后 idea 是否真的更好"],
    ["v0.7", "reference claim verification", "检查 claim 是否有 paper id 和 title/abstract/card 支撑"],
    ["v0.8", "cross-task benchmark robustness summary", "纠正为 benchmark 样本视角，不是单任务选择器"],
    ["v0.9", "idea generation core benchmark report", "把 3 个强样本收束成核心模块证据"],
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


def generate_core_report(slices: List[EvidenceSlice]) -> str:
    rows = [
        [
            item.task_id,
            item.task_name,
            item.role,
            item.proves,
            item.blind_ab,
            item.claim_verification,
        ]
        for item in slices
    ]
    stage_rows = [[stage, goal, output] for stage, goal, output in PIPELINE_STAGES]

    details = []
    for item in slices:
        details.append(
            "\n".join(
                [
                    f"### {item.task_id} {item.task_name}",
                    "",
                    f"证明能力：{item.proves}",
                    "",
                    f"修复/验证故事：{item.repair_story}",
                    "",
                    f"盲评结果：{item.blind_ab}",
                    "",
                    f"证据校验：{item.claim_verification}",
                    "",
                    "边界：",
                    "",
                    bullet_list(item.limits),
                    "",
                    f"展示用途：{item.demo_use}",
                ]
            )
        )

    return f"""# V0.9 Idea Generation Core Benchmark Report

生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

生成脚本：`focused_workflow/scripts/build_v09_idea_generation_core_benchmark_report.py`

## 一句话定位

V0.9 的目标不是新增任务，也不是选择一个任务作为比赛方向，而是把已经完成闭环的 3 个 benchmark 样本收束成一个清楚的结论：

> 本项目的核心贡献是一个跨任务、证据驱动、可修复、可评价的科研 idea generation 模块。给定不同 task_spec，它能生成更细粒度、更可实现、更可验证的 focused ideas，并通过 targeted repair、multi-LLM blind A/B judge 和 reference claim verification 形成闭环。

## 为什么先不管 02/04

02 Human Motion 和 04 3D Reconstruction 仍然保留为 held-out benchmark samples，但当前阶段先不继续消耗 API 或扩任务。原因是：已有 01/03/05 三个样本已经覆盖了三类关键能力：

- 01 物理属性预测：机制错配诊断和二次修复。
- 03 室内单图 3D：复杂生成/重建任务上的 evidence-grounded ideation。
- 05 IAD + Agent：agentic workflow 和工程可执行字段。

这三个样本足够支撑“idea generation 模块已经成型”的阶段性论证。后续 02/04 的价值是进一步验证泛化，而不是当前阶段的阻塞项。

## Pipeline 演进

{md_table(["版本", "目标", "产物/能力"], stage_rows)}

## 三个强样本的证据表

{md_table(["ID", "样本任务", "角色", "证明能力", "v0.6 blind A/B", "v0.7 claim verification"], rows)}

## 样本详情

{chr(10).join(details)}

## 相比 ResearchArena baseline 的改进点

原始 ResearchArena baseline 更像开放式 proposal generation，容易出现 idea 太长、太泛、缺少最小实验和量化评价的问题。Focused Workflow 的改进点是：

- 输入层：固定 task_spec schema，让不同任务都能被同一套 workflow 接收。
- 生成层：要求 focused ideas 必须绑定 baseline weakness、direct baselines、transfer baselines 和 minimal_new_module。
- 实验层：每个 idea 必须给出 required scripts/data、expected tables/figures、success thresholds 和 negative controls。
- 修复层：用 critic/repair prompt 和后处理脚本定位机制错配、证据不足、评价缺口。
- 评价层：用 multi-LLM anonymous blind A/B judge 判断 repair 是否真的提高 idea 质量。
- 证据层：用 reference claim verification 检查 claim 是否有真实 paper id 和 title/abstract/card 支撑。

因此，当前贡献不应表述为“某个 CV 算法更强”，而应表述为“科研 idea generation 被改造成可控、可评价、可修复的跨任务 pipeline”。

## 当前可主张与不可主张

可以主张：

- 已经完成一个跨任务 idea generation workflow 雏形。
- 已经在 3 个代表性 benchmark 样本上验证生成、修复、盲评、证据校验闭环。
- 物理属性样本提供最强 failure -> diagnosis -> repair -> re-evaluation 案例。
- IAD + Agent 样本证明输出字段能支持工程 workflow。
- 室内 3D 样本证明复杂生成/重建方向也能进入同一套 evidence-grounded ideation 流程。

不应主张：

- 不应说已经完成所有 5 个 benchmark 的完整闭环。
- 不应说已经证明全球意义上的 idea generation SOTA。
- 不应把 IAD、物理属性或室内 3D 表述成唯一比赛方向。
- 不应隐瞒室内 3D 使用 seeded evidence bank。

## 下一步进入完整工作流

V0.9 之后，建议从 idea generation core 进入 end-to-end workflow demo：

1. 固定一个小型 task_spec 输入样例。
2. 展示 baseline cards、focused ideas 和 experiment plan 的结构化输出。
3. 展示 targeted repair 前后差异。
4. 展示 blind A/B judge 和 reference claim verification 如何反馈到 idea 修复。
5. 进一步连接到实验执行 planning、代码/数据 artifact planning 和最终报告生成。

这一步才是从“idea generation 模块强”走向“完整 AI 科研自动化 workflow 可运行”。
"""


def generate_module_card(slices: List[EvidenceSlice]) -> str:
    return f"""# Idea Generation Module Card

生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 模块名称

Evidence-Grounded Focused Idea Generation

## 模块定位

该模块不是单个 CV 算法，而是 AI 科研自动化 workflow 的 idea generation 核心。它接收不同任务的 task_spec 和 baseline/evidence context，输出结构化、可执行、可评价、可修复的科研 idea。

## 输入

- `task_spec.yaml`：任务目标、输入输出、baseline、metrics、constraints、idea requirements。
- `baseline_cards.jsonl`：从已有 baseline 或论文中抽取的能力、弱点、可借鉴组件。
- `paper evidence / evidence_baseline_cards.jsonl`：论文证据、baseline weakness、支持或不支持的 claim。
- 可选：已有 idea quality score、reviewer rationale、repair history。

## 输出

- `focused_ideas.json`：多个结构化 idea。
- `experiment_plan.json`：可执行实验计划。
- repaired ideas：经过 targeted repair 的改进版本。
- judge summaries：multi-LLM blind A/B 评价结果。
- claim verification summaries：claim 是否被 paper evidence 支持。

## 强制字段

- direct baselines
- transfer baselines
- borrowed components
- minimal_new_module
- algorithmic_objective
- datasets
- metrics
- ablations
- negative controls
- success thresholds
- required scripts
- required data files
- expected tables/figures
- risks and failure criteria

## 评价方式

- rule-based idea quality scoring
- Si et al. 2025 style LLM review rubric
- multi-LLM anonymous blind A/B judge
- reference claim verification
- unsupported/manual-check claim accounting

## 已验证样本

{md_table(["任务", "证明能力", "关键结果"], [[item.task_name, item.proves, item.blind_ab + "；" + item.claim_verification] for item in slices])}

## 已知边界

- 当前完整闭环集中在 01/03/05 三个样本，02/04 暂作为 held-out benchmark。
- 室内 3D 使用 seeded evidence bank，需透明披露。
- 该模块证明的是 idea generation workflow 的质量提升，不等同于完成所有下游实验。
- “SOTA”需要谨慎表述，应限定在当前 benchmark 和当前对比设置内。
"""


def generate_storyline(slices: List[EvidenceSlice]) -> str:
    return f"""# Final Storyline for Competition

生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 30 秒开场

我们做的不是某一个 CV 算法，而是一个面向 AI4Sci 的科研自动化 workflow。我们发现，很多自动科研系统最大的问题不是不会写代码，而是第一步 idea generation 就容易空泛：没有明确 baseline、没有最小实验、没有 negative control，也缺少论文证据校验。

## 核心方法

我们基于 ResearchArena baseline，构建了 focused idea generation workflow：

1. 用 task_spec 固定任务输入。
2. 用 baseline cards 约束 idea 必须针对真实 baseline weakness。
3. 用 evidence-grounded ideation 绑定论文证据。
4. 用 targeted repair 修复空泛、机制错配和证据不足。
5. 用 multi-LLM blind A/B judge 检查 repair 后 idea 是否真的更好。
6. 用 reference claim verification 检查 claim 是否被论文证据支持。

## 三个证据样本

物理属性预测：这是最强闭环案例。v1 repair 曾经失败，after win rate 只有 0.556。我们没有掩盖失败，而是用 reviewer rationale 定位问题：Idea 2 和 Idea 3 错误套用了 Idea 1 的 interval-mapper loss。v2 修复后，6 个 judge 共 18 票全部选择 after，证据校验 pass rate 也达到 1.0。

IAD + Agent：这个样本说明我们的 idea 不是空泛文本，而能落成 agent workflow 字段：normal reference retrieval、verification loop、evidence-grounded report checker、negative controls、success thresholds。它的 v0.6 after win rate 是 0.778，v0.7 pass rate 是 0.857，unsupported 为 0。

室内单图 3D：这个样本说明 workflow 可以迁移到复杂生成/重建任务。我们也透明说明：初始检索 evidence bank 为空，因此使用 seeded evidence bank 补齐代表性论文；该方向 9/9 after wins，证据校验 pass rate 1.0。

## 评委可能问的问题

Q：你们是不是只做了 IAD 或某一个任务？

A：不是。IAD、物理属性和室内 3D 都是 benchmark samples，用来测试同一个 idea generation pipeline。我们的贡献是跨任务 workflow，而不是单点算法。

Q：为什么 02 Human Motion 和 04 3D Reconstruction 暂时不跑？

A：它们作为 held-out benchmark 保留。当前阶段先用 01/03/05 三个已完成闭环的样本证明模块能力，避免继续消耗 API 和堆结果。后续会用 02/04 验证进一步泛化。

Q：你们能说 idea generation 已经 SOTA 吗？

A：我们会谨慎表述。当前可以说：在我们的 benchmark 样本和对比设置下，相比 ResearchArena baseline，idea 输出在结构化、可实现性、repair 后质量和证据可校验性上显著增强。全球意义的 SOTA 需要更大规模 benchmark 和人工评审。

Q：室内 3D 的 seeded evidence bank 会不会影响可信度？

A：我们会透明披露。它不作为唯一结论，而是作为复杂任务上的 workflow demonstration。核心证据仍来自生成、修复、盲评和 claim verification 的闭环。

## 收束句

我们的系统把 idea generation 从“生成一段看起来合理的想法”，推进为“可约束、可修复、可盲评、可证据校验的科研工作流模块”。这为后续自动实验规划、代码执行和论文报告生成打下基础。
"""


def write_json(output: Path, slices: List[EvidenceSlice]) -> None:
    payload = {
        "version": "v0.9",
        "purpose": "idea_generation_core_benchmark_report",
        "completed_evidence_slices": [asdict(item) for item in slices],
        "held_out_tasks": ["02_human_motion_generation", "04_3d_reconstruction"],
        "core_claim": (
            "The focused workflow improves research idea generation by making ideas "
            "baseline-grounded, implementable, repairable, judgeable, and evidence-verifiable."
        ),
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    out_dir = root / "competition_submission"
    out_dir.mkdir(parents=True, exist_ok=True)
    slices = evidence_slices()

    paths = {
        "report": out_dir / "V09_IDEA_GENERATION_CORE_BENCHMARK_REPORT_CN.md",
        "module_card": out_dir / "IDEA_GENERATION_MODULE_CARD_CN.md",
        "storyline": out_dir / "FINAL_STORYLINE_FOR_COMPETITION_CN.md",
        "json": out_dir / "V09_IDEA_GENERATION_CORE_BENCHMARK_SUMMARY.json",
    }
    paths["report"].write_text(generate_core_report(slices), encoding="utf-8")
    paths["module_card"].write_text(generate_module_card(slices), encoding="utf-8")
    paths["storyline"].write_text(generate_storyline(slices), encoding="utf-8")
    write_json(paths["json"], slices)

    print("V0.9 idea generation core benchmark deliverables written:")
    for label, path in paths.items():
        print(f"- {label}: {path}")


if __name__ == "__main__":
    main()
