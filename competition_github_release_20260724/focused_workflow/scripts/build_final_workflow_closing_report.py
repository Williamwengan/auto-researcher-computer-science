#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

V09 = ROOT / "competition_submission/V09_IDEA_GENERATION_CORE_BENCHMARK_SUMMARY.json"
V10 = ROOT / "competition_submission/V10_FINAL_RESEARCH_PLAN_PACKAGE.json"
V18 = ROOT / "competition_submission/V18_IAD_EXECUTION_FEEDBACK_REPAIR_CASE.json"

SI2024_MD = ROOT / "competition_submission/SI2024_BENCHMARK_EVALUATION_REPORT_CN.md"
V07_MD = ROOT / "competition_submission/V07_REFERENCE_CLAIM_VERIFICATION_FINAL_SUMMARY_CN.md"
V09_MD = ROOT / "competition_submission/V09_IDEA_GENERATION_CORE_BENCHMARK_REPORT_CN.md"
V10_MD = ROOT / "competition_submission/V10_FINAL_RESEARCH_PLAN_PACKAGE_CN.md"
V18_MD = ROOT / "competition_submission/V18_IAD_EXECUTION_FEEDBACK_REPAIR_CASE_CN.md"

REPORT_MD = ROOT / "competition_submission/FINAL_WORKFLOW_END_TO_END_CLOSING_REPORT_CN.md"
REPORT_JSON = ROOT / "competition_submission/FINAL_WORKFLOW_END_TO_END_CLOSING_REPORT.json"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Missing required input: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def require(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"Missing required input: {path.relative_to(ROOT)}")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = ["| " + " | ".join(str(row.get(col, "")) for col in columns) + " |" for row in rows]
    return "\n".join([header, sep, *body])


def build_payload() -> dict[str, Any]:
    for path in [V09, V10, V18, SI2024_MD, V07_MD, V09_MD, V10_MD, V18_MD]:
        require(path)

    v09 = read_json(V09)
    v10 = read_json(V10)
    v18 = read_json(V18)

    workflow_stages = [
        {
            "stage": "Task input",
            "status": "done",
            "evidence": "v0.2 固定 task_spec 输入和 baseline_cards/focused_ideas/experiment_plan 输出格式。",
        },
        {
            "stage": "Paper evidence and baseline weakness",
            "status": "done",
            "evidence": "v0.5 evidence-grounded ideation；v0.7 reference claim verification。",
        },
        {
            "stage": "Focused idea generation",
            "status": "done",
            "evidence": "v0.3–v0.5 约束 minimal_new_module、algorithmic objective、实验字段、negative controls。",
        },
        {
            "stage": "Multi-LLM blind review and repair",
            "status": "done",
            "evidence": "v0.6 multi-LLM anonymous blind A/B judge；物理属性 v1→v2 二次修复。",
        },
        {
            "stage": "Reference claim verification",
            "status": "done",
            "evidence": "v0.7 对 IAD/Physical/Indoor3D claim-evidence alignment 做自动检查。",
        },
        {
            "stage": "Final research plan package",
            "status": "done",
            "evidence": "v1.0 输出 final research plan schema/package。",
        },
        {
            "stage": "Experiment execution planning",
            "status": "done",
            "evidence": "v1.1 将 final plans 拆成数据准备、脚本、指标和失败检查。",
        },
        {
            "stage": "Real-data execution feedback",
            "status": "partially done",
            "evidence": "v1.3–v1.8 IAD 接入 MVTec AD，形成 execution-feedback repair case。",
        },
        {
            "stage": "Full benchmark-grade algorithm implementation",
            "status": "not claimed",
            "evidence": "当前 IAD 是 lightweight scaffold，不声称 PatchCore/anomalib 正式 benchmark 或 SOTA。",
        },
    ]

    idea_benchmark_rows = [
        {
            "task": "IAD + Agent",
            "si2024_style_result": "After win rate 60.00% in 5-judge Si-style report; earlier v0.6 repair 7/9 after wins.",
            "core_value": "agentic workflow、reference retrieval、evidence-grounded report checker、implementation readiness。",
        },
        {
            "task": "Physical Property",
            "si2024_style_result": "Si-style report shows task-dependent repair failure; later v2 repair achieved 18/18 after wins.",
            "core_value": "最强 failure → rationale diagnosis → mechanism-consistent v2 repair 案例。",
        },
        {
            "task": "Indoor 3D Scene",
            "si2024_style_result": "After win rate 80.00% in Si-style report; v0.6/v0.7 evidence-card repaired case reached strong results.",
            "core_value": "复杂 3D/generation/reconstruction 任务上的 evidence-grounded ideation 泛化；需披露 seeded evidence bank。",
        },
    ]

    evidence_rows = [
        {
            "task": "IAD + Agent",
            "papers": 24,
            "claims": 21,
            "pass_rate": "0.857",
            "note": "unsupported=0, needs_manual_check=3，保留诚实不确定性。",
        },
        {
            "task": "Physical Property v2",
            "papers": 51,
            "claims": 15,
            "pass_rate": "1.0",
            "note": "evidence-card repair 后 claim verification pass rate 1.0。",
        },
        {
            "task": "Indoor 3D Scene",
            "papers": 18,
            "claims": 18,
            "pass_rate": "1.0",
            "note": "使用 seeded evidence bank，最终材料必须透明披露。",
        },
    ]

    execution_rows = v18["timeline"]
    final_metrics = v18["final_metrics"]

    final_claims = [
        "已经完成一个基于 ResearchArena baseline 的跨任务 AI 科研自动化 workflow 雏形。",
        "核心贡献不是单点 CV 算法，而是 baseline-grounded、evidence-grounded、可修复、可评价的 idea generation 和 research-plan generation pipeline。",
        "workflow 已在 IAD、物理属性预测、室内单图 3D 场景三个代表性任务上完成 idea generation + repair + evaluation + evidence verification 闭环。",
        "IAD 方向进一步接入真实 MVTec AD 数据，形成真实执行反馈与自动修复案例。",
    ]

    non_claims = [
        "不声称已经完成所有 5 个 benchmark 方向的完整闭环；02 Human Motion 和 04 3D Reconstruction 当前仍是 held-out samples。",
        "不声称 idea generation 达到全球意义上的 SOTA；当前是 Si et al.-style protocol + multi-LLM judge + 人工复核近似评估。",
        "不声称 IAD 是最终唯一比赛方向；IAD 是 execution-feedback case study。",
        "不声称当前 IAD 结果是完整 PatchCore/anomalib benchmark 或 IAD SOTA。",
        "不隐瞒室内 3D 使用 seeded evidence bank。",
    ]

    recommended_next_steps = [
        {
            "priority": "High",
            "step": "把本报告作为最终主线报告，和 V09/V10/V18 一起组成比赛材料核心证据。",
            "why": "现在已经形成 end-to-end story，再继续堆 IAD 会偏离通用 workflow 主线。",
        },
        {
            "priority": "High",
            "step": "制作 8–10 页答辩 PPT：问题、系统流程、三任务 benchmark、证据校验、IAD execution-feedback case、边界与展望。",
            "why": "比赛评审更需要清楚故事线，而不是阅读所有版本报告。",
        },
        {
            "priority": "Medium",
            "step": "整理一个 deliverables index，标出每个报告/脚本/输出表对应 workflow 哪一环。",
            "why": "避免材料多而散，让评审快速找到证据。",
        },
        {
            "priority": "Optional",
            "step": "如果必须增强工程深度，再考虑 PatchCore/anomalib 或 patch-level feature。",
            "why": "这会增强 IAD 工程证据，但也会消耗时间并偏向单任务算法。",
        },
    ]

    return {
        "version": "final_end_to_end_closing",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "inputs": {
            "v09_summary": str(V09.relative_to(ROOT)),
            "v10_package": str(V10.relative_to(ROOT)),
            "v18_case": str(V18.relative_to(ROOT)),
            "si2024_report": str(SI2024_MD.relative_to(ROOT)),
            "v07_reference_claim_report": str(V07_MD.relative_to(ROOT)),
        },
        "source_versions": {
            "v09": v09.get("version", "v0.9"),
            "v10": v10.get("version", "v1.0"),
            "v18": v18.get("version", "v1.8"),
        },
        "workflow_stages": workflow_stages,
        "idea_benchmark_rows": idea_benchmark_rows,
        "evidence_rows": evidence_rows,
        "execution_feedback_rows": execution_rows,
        "execution_final_metrics": final_metrics,
        "final_claims": final_claims,
        "non_claims": non_claims,
        "recommended_next_steps": recommended_next_steps,
        "boundary": "Final closing report for workflow evidence; not a new experiment and not a single-task algorithm benchmark.",
    }


def build_report(payload: dict[str, Any]) -> str:
    metrics = payload["execution_final_metrics"]
    return f"""# AI 科研自动化 Workflow 端到端收束报告

生成时间：{payload["generated_at"]}

生成脚本：`focused_workflow/scripts/build_final_workflow_closing_report.py`

## 1. 一句话结论

本项目已经从 ResearchArena baseline 出发，形成了一个跨任务、证据驱动、可修复、可评价的 AI 科研自动化 workflow 雏形。它的核心贡献不是某一个 CV 算法，而是：

```text
输入科研任务
→ 检索和整理论文
→ 分析 baseline 缺陷
→ 生成细粒度 idea
→ 生成实验计划
→ 多模型匿名评审
→ 根据意见修复 idea
→ 再次盲评
→ 核查论文证据
→ 输出最终研究方案
→ 接入真实数据执行反馈
→ 自动诊断和修复执行层问题
```

当前最重要的新增证据是：IAD 方向已经从“生成研究方案”推进到 MVTec AD 真实数据 smoke test，并形成 V1.3–V1.8 的 execution-feedback repair case。

## 2. Workflow 阶段完成情况

{md_table(payload["workflow_stages"], ["stage", "status", "evidence"])}

## 3. Idea Generation 核心证据

{md_table(payload["idea_benchmark_rows"], ["task", "si2024_style_result", "core_value"])}

解释：

- Si et al.-style benchmark 复用的是 blind review protocol 和评分维度，不是复现 100+ NLP researcher human study。
- 结果是任务依赖的，不能写成“全面提升”。
- 物理属性方向的失败和 v2 修复，反而是本 workflow 最有说服力的 failure-diagnosis-repair 案例之一。

## 4. Reference Claim Verification 证据

{md_table(payload["evidence_rows"], ["task", "papers", "claims", "pass_rate", "note"])}

这说明 idea 并不是凭空生成，而是和 paper evidence、baseline weakness、proposed mechanism 建立了可检查的绑定关系。

## 5. Final Research Plan 与真实执行反馈

V1.0 已经把经过生成、修复、盲评和证据校验的 ideas 转换成 final research plans。V1.1–V1.2 将其拆成执行计划和 IAD MVP scaffold。V1.3–V1.8 则进一步证明：至少在 IAD 方向，workflow 可以接入真实 MVTec AD 数据并从执行反馈中自动修复。

{md_table(payload["execution_feedback_rows"], ["version", "stage", "input", "finding", "key_metric", "repair_or_next"])}

关键指标：

- V1.3 单类别 bottle lightweight AUC：{metrics["v13_single_category_auc"]}
- V1.4 bottle accepted anomaly：{metrics["v14_bottle_accept_anomaly_before"]} → {metrics["v14_bottle_accept_anomaly_after"]}
- V1.5 全局阈值三类别 FPR：{metrics["v15_global_threshold_fpr"]}
- V1.6 类别感知阈值三类别 FPR：{metrics["v16_per_category_fpr"]}
- V1.6 balanced score：{metrics["v16_global_to_per_category_score"]["before"]} → {metrics["v16_global_to_per_category_score"]["after"]}
- V1.7 score / recall / FPR：{metrics["v17_score"]} / {metrics["v17_recall"]} / {metrics["v17_fpr"]}

最值得放进答辩的一句话：

> V1.5 发现全局阈值跨类别迁移失败，FPR 达到 0.574257；V1.6 自动做类别感知阈值校准，将 FPR 降到 0.009901。这证明 workflow 能将真实执行失败转化为自动诊断和修复信号。

## 6. 当前可以主张什么

{chr(10).join(f"- {item}" for item in payload["final_claims"])}

## 7. 当前不能主张什么

{chr(10).join(f"- {item}" for item in payload["non_claims"])}

## 8. 推荐最终材料组织方式

建议把最终材料组织成四层：

1. **主线报告**：本报告，说明端到端 workflow 已经闭环。
2. **核心 idea generation 报告**：`V09_IDEA_GENERATION_CORE_BENCHMARK_REPORT_CN.md`。
3. **最终研究方案包**：`V10_FINAL_RESEARCH_PLAN_PACKAGE_CN.md`。
4. **真实执行反馈案例**：`V18_IAD_EXECUTION_FEEDBACK_REPAIR_CASE_CN.md`。

辅助证据包括：

- `SI2024_BENCHMARK_EVALUATION_REPORT_CN.md`
- `V07_REFERENCE_CLAIM_VERIFICATION_FINAL_SUMMARY_CN.md`
- `V13–V17` IAD execution reports
- `V06_MULTI_LLM_BLIND_AB_EVALUATION_REPORT_V2_CN.md`

## 9. 下一步怎么做

{md_table(payload["recommended_next_steps"], ["priority", "step", "why"])}

## 10. 最终建议

现在不要继续陷入 IAD 算法工程。最优路线是开始整理比赛交付材料：

```text
Final report
PPT
deliverables index
workflow diagram
关键表格截图/附录
```

如果后续还有时间，再把 PatchCore/anomalib 作为附加工程增强，而不是主线。
"""


def main() -> None:
    payload = build_payload()
    write_json(REPORT_JSON, payload)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text(build_report(payload), encoding="utf-8")
    print(f"Wrote {REPORT_MD}")
    print(f"Wrote {REPORT_JSON}")
    print(
        "Summary: final workflow closing report created; "
        f"IAD V15 FPR={payload['execution_final_metrics']['v15_global_threshold_fpr']} -> "
        f"V16 FPR={payload['execution_final_metrics']['v16_per_category_fpr']}"
    )


if __name__ == "__main__":
    main()
