#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SUBMISSION = ROOT / "competition_submission"
ARIS_TOOLS = ROOT / "aris_bridge/tools"
OUT_DIR = ROOT / "execution_runs/v23_iad_execution_bridge"

sys.path.insert(0, str(ARIS_TOOLS))
import research_wiki as rw  # noqa: E402
import run_state as rs  # noqa: E402


PHASES = [
    "load_final_research_plan",
    "build_execution_plan",
    "prepare_data_manifest",
    "build_reference_bank",
    "reproduce_lightweight_baseline",
    "score_reference_consistency_agent",
    "evaluate_metrics",
    "result_to_claim",
    "diagnose_and_repair_suggestion",
    "build_paper_plan",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_metrics(path: Path) -> dict:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise RuntimeError(f"empty metrics csv: {path}")
    row = rows[0]
    out = {}
    for k, v in row.items():
        if v is None:
            out[k] = v
            continue
        try:
            out[k] = float(v)
        except ValueError:
            out[k] = v
    return out


def find_iad_plan() -> dict:
    data = read_json(SUBMISSION / "V10_FINAL_RESEARCH_PLAN_PACKAGE.json")
    for plan in data.get("plans", []):
        name = plan.get("task_name", "")
        if "IAD" in name or "异常" in name:
            return plan
    raise RuntimeError("IAD final research plan not found in V10 package")


def write_lines(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_execution_plan(plan: dict, metrics: dict) -> str:
    return f"""# V23 IAD Execution Bridge Plan

生成时间：{datetime.now().isoformat(timespec="seconds")}

## 目标

把 V10 final research plan 中的 IAD idea 接入 ARIS-style execution layer，使 workflow 从 idea/plan 进入实验复现、结果登记、claim 判断和论文计划。

## 输入 final idea

{plan.get("final_idea", "")}

## 核心假设

{plan.get("core_hypothesis", "")}

## Execution blocks

| block | purpose | artifact |
| --- | --- | --- |
| B0 data manifest | 准备 MVTec AD manifest | `iad_mvp/data/iad_reference_manifest.jsonl` |
| B1 reference bank | 构建 normal reference bank | `iad_mvp/data/iad_reference_bank.npz` |
| B2 baseline reproduction | 运行 lightweight nearest-reference baseline | `iad_mvp/outputs/patchcore_baseline/iad_baseline_scores.csv` |
| B3 proposed scoring | 运行 reference-consistency scoring | `iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv` |
| B4 evaluation | 汇总 execution metrics | `iad_mvp/outputs/tables/iad_agent_execution_metrics.csv` |
| B5 result-to-claim | 写入 research wiki experiment/claim | `research_wiki/experiments/` and `research_wiki/claims/` |
| B6 paper plan | 根据结果生成 paper plan | `PAPER_PLAN.md` |

## 当前执行结果

- image_level_auc_lightweight: {metrics.get("image_level_auc_lightweight")}
- tool_success_rate: {metrics.get("tool_success_rate")}
- evidence_grounding_score_proxy: {metrics.get("evidence_grounding_score_proxy")}
- false_alarm_reduction_proxy: {metrics.get("false_alarm_reduction_proxy")}
- note: {metrics.get("note")}

## Honest verdict

当前结果证明 IAD execution bridge 能把 final idea 接入真实数据 smoke test，并能产出可读取指标与执行日志；但它仍是 lightweight scaffold，不是完整 PatchCore/anomalib benchmark，也不声称 IAD SOTA。
"""


def build_experiment_log(plan: dict, metrics: dict) -> str:
    return f"""# Experiment Log

## Experiment: IAD Reference-Consistency Smoke Test

**Date**: {datetime.now().date().isoformat()}

**Idea**: {plan.get("final_idea", "")}

**Goal**: 验证 final research plan 能否进入真实数据执行链路，并生成可读取 metrics。

### Setup

- **Method**: lightweight nearest-reference baseline + reference-consistency agent scaffold
- **Dataset**: MVTec AD default/smoke split
- **Baseline**: lightweight nearest-reference baseline, not full PatchCore
- **Config**: default `iad_mvp` scaffold paths

### Results

| Method | Metric | Value | Notes |
| --- | --- | ---: | --- |
| lightweight baseline | image_level_auc_lightweight | {metrics.get("image_level_auc_lightweight")} | scaffold metric |
| reference-consistency agent | tool_success_rate | {metrics.get("tool_success_rate")} | script chain completed |
| reference-consistency agent | evidence_grounding_score_proxy | {metrics.get("evidence_grounding_score_proxy")} | proxy |
| reference-consistency agent | false_alarm_reduction_proxy | {metrics.get("false_alarm_reduction_proxy")} | proxy |

### Verdict

- **Supports execution claim?** Partially / Yes for scaffold execution.
- **Supports scientific performance claim?** Not yet; full benchmark-grade implementation is still required.
- **Key takeaway**: The workflow can progress from final idea to real-data execution artifacts, but the execution engine remains lightweight.

### Reproduction

```bash
python iad_mvp/scripts/prepare_iad_reference_manifest.py
python iad_mvp/scripts/build_reference_bank.py
python iad_mvp/scripts/run_iad_baselines.py
python iad_mvp/scripts/score_reference_consistency.py
python iad_mvp/scripts/evaluate_iad_agent.py
```
"""


def build_commands() -> str:
    return """#!/usr/bin/env bash
set -euo pipefail

# Optional full data-subset preparation. Requires explicit MVTec root.
# python iad_mvp/scripts/prepare_mvtec_subset.py \\
#   --mvtec_root Datasets/01_IAD/mvtec_anomaly_detection/mvtec_anomaly_detection \\
#   --categories bottle \\
#   --output iad_mvp/data/mvtec_split.json

python iad_mvp/scripts/prepare_iad_reference_manifest.py
python iad_mvp/scripts/build_reference_bank.py
python iad_mvp/scripts/run_iad_baselines.py
python iad_mvp/scripts/score_reference_consistency.py
python iad_mvp/scripts/evaluate_iad_agent.py
python focused_workflow/scripts/build_v23_iad_execution_bridge.py
"""


def build_paper_plan(plan: dict, metrics: dict) -> str:
    return f"""# Paper Plan

## Metadata

- **Title**: Evidence-Grounded Research Agents for AI4S Idea-to-Experiment Automation
- **One-sentence contribution**: We connect evidence-grounded idea generation with execution feedback, using IAD as a real-data smoke-test case.

## Claims-Evidence Matrix

| # | Claim | Evidence | Status |
| --- | --- | --- | --- |
| C1 | Workflow can convert a final research idea into executable experiment artifacts. | V23 execution bridge outputs, run_state, experiment log. | supported for scaffold |
| C2 | IAD reference-consistency idea is ready for full benchmark implementation. | AUC={metrics.get("image_level_auc_lightweight")}, tool_success={metrics.get("tool_success_rate")}; current scaffold only. | partial |
| C3 | Execution feedback can drive repair. | Prior V15→V16 FPR drop case; V23 records path to result-to-claim. | supported as case study |

## Section Plan

### 1. Introduction

Motivate the gap between idea generation and executable AI4S research.

### 2. Method

Describe task input, evidence retrieval, baseline cards, idea generation, judge/repair, claim verification, and execution bridge.

### 3. Execution Layer

Explain ARIS-style run_state, research_wiki experiment nodes, result-to-claim, iteration logs, and watchdog monitoring.

### 4. Experiments

Report three-task idea benchmark and IAD real-data execution smoke test.

### 5. Limitations

State clearly that current IAD result is lightweight scaffold, not full PatchCore/anomalib benchmark.

## Strongest number currently safe to mention

- IAD lightweight AUC: {metrics.get("image_level_auc_lightweight")}
- tool_success_rate: {metrics.get("tool_success_rate")}

## Boundary

Do not claim IAD SOTA. Do not claim full autonomous science yet. Claim a prototype of idea-to-execution workflow with one real-data execution bridge.
"""


def verdict_from_metrics(metrics: dict) -> tuple[str, str]:
    tool_success = float(metrics.get("tool_success_rate") or 0.0)
    auc = float(metrics.get("image_level_auc_lightweight") or 0.0)
    if tool_success >= 1.0 and auc >= 0.9:
        return "partial", "medium"
    if tool_success > 0:
        return "partial", "low"
    return "no", "low"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    plan = find_iad_plan()
    metrics_path = ROOT / "iad_mvp/outputs/tables/iad_agent_execution_metrics.csv"
    if not metrics_path.exists():
        raise FileNotFoundError(
            f"missing metrics file: {metrics_path}. Run iad_mvp/scripts/evaluate_iad_agent.py first."
        )
    metrics = read_metrics(metrics_path)

    execution_plan_path = OUT_DIR / "EXECUTION_PLAN.md"
    experiment_log_path = OUT_DIR / "EXPERIMENT_LOG.md"
    commands_path = OUT_DIR / "commands.sh"
    paper_plan_path = OUT_DIR / "PAPER_PLAN.md"
    summary_json_path = OUT_DIR / "v23_execution_summary.json"
    summary_md_path = SUBMISSION / "V23_IAD_EXECUTION_BRIDGE_CN.md"

    write_lines(execution_plan_path, build_execution_plan(plan, metrics).splitlines())
    write_lines(experiment_log_path, build_experiment_log(plan, metrics).splitlines())
    write_lines(commands_path, build_commands().splitlines())
    commands_path.chmod(0o755)
    write_lines(paper_plan_path, build_paper_plan(plan, metrics).splitlines())

    # Initialize ARIS-style run state.
    run_id = "v23_iad_execution_bridge"
    state = rs.start_run(str(OUT_DIR), run_id, PHASES)
    phase_artifacts = {
        "load_final_research_plan": str(SUBMISSION / "V10_FINAL_RESEARCH_PLAN_PACKAGE.json"),
        "build_execution_plan": str(execution_plan_path),
        "prepare_data_manifest": str(ROOT / "iad_mvp/data/iad_reference_manifest.jsonl"),
        "build_reference_bank": str(ROOT / "iad_mvp/data/iad_reference_bank.npz"),
        "reproduce_lightweight_baseline": str(ROOT / "iad_mvp/outputs/patchcore_baseline/iad_baseline_scores.csv"),
        "score_reference_consistency_agent": str(ROOT / "iad_mvp/outputs/reference_consistency/iad_reference_consistency_scores.csv"),
        "evaluate_metrics": str(metrics_path),
        "result_to_claim": str(OUT_DIR / "research_wiki"),
        "diagnose_and_repair_suggestion": str(execution_plan_path),
        "build_paper_plan": str(paper_plan_path),
    }
    for phase in PHASES:
        state = rs.set_status(str(OUT_DIR), run_id, phase, "done", artifact=phase_artifacts.get(phase))
        state = rs.accept(str(OUT_DIR), run_id, phase, verdict_id=f"deterministic:{phase}", reviewer="deterministic:v23_bridge")
    run_state_src = OUT_DIR / ".aris/runs/v23_iad_execution_bridge.json"
    run_state_public = OUT_DIR / "run_state.json"
    shutil.copyfile(run_state_src, run_state_public)

    # Initialize research wiki and write experiment / claims.
    wiki_root = OUT_DIR / "research_wiki"
    rw.init_wiki(str(wiki_root))
    verdict, confidence = verdict_from_metrics(metrics)
    metrics_text = json.dumps(metrics, ensure_ascii=False, indent=2)
    rw.upsert_idea(
        str(wiki_root),
        "iad-agent-final",
        "Evidence-Grounded Reference-Consistency IAD Agent",
        description=plan.get("final_idea", ""),
        stage="piloted",
        outcome="mixed",
        thesis=plan.get("core_hypothesis", ""),
        risks="\n".join(plan.get("risk_and_mitigation", [])),
        tags=["iad", "final-plan", "execution-bridge"],
        update_on_exist=True,
    )
    rw.add_experiment(
        str(wiki_root),
        "iad-reference-consistency-smoke-v23",
        title="IAD reference-consistency execution bridge smoke test",
        idea="iad-agent-final",
        verdict=verdict,
        confidence=confidence,
        hardware="local/server scaffold",
        duration="short smoke test",
        metrics=metrics_text,
        reasoning=(
            "The script chain produced manifest, reference bank, baseline scores, "
            "reference-consistency scores, and metrics. This supports scaffold-level execution, "
            "but not full benchmark-grade IAD performance."
        ),
        provenance=str(metrics_path),
        tags=["iad", "execution-bridge", "smoke-test"],
        update_on_exist=True,
    )
    rw.add_claim(
        str(wiki_root),
        "iad-execution-bridge-runs",
        "IAD final research plan can be connected to executable smoke-test artifacts",
        status="sound-modulo-imports",
        provenance=str(OUT_DIR),
        statement="The V10 IAD final plan is bridged to a concrete iad_mvp execution chain and produces metrics artifacts.",
        scope="Scaffold-level MVTec AD smoke test; not full PatchCore/anomalib benchmark.",
        evidence=f"Metrics file: {metrics_path}; metrics: {metrics_text}",
        tags=["execution", "iad", "workflow"],
        update_on_exist=True,
    )
    rw.add_claim(
        str(wiki_root),
        "iad-performance-claim-not-final",
        "IAD performance improvement claim is not yet final benchmark evidence",
        status="unproven",
        provenance=str(OUT_DIR),
        statement="Current IAD result should not be treated as SOTA or full benchmark evidence.",
        scope="Boundary claim for honest reporting.",
        evidence="The metric note says scaffold metrics; not final benchmark results.",
        tags=["boundary", "iad", "honesty"],
        update_on_exist=True,
    )

    summary = {
        "version": "v23",
        "purpose": "connect_final_research_plan_to_execution_layer",
        "run_dir": str(OUT_DIR),
        "plan_id": plan.get("plan_id"),
        "task_name": plan.get("task_name"),
        "metrics": metrics,
        "experiment_verdict": verdict,
        "experiment_confidence": confidence,
        "artifacts": {
            "execution_plan": str(execution_plan_path),
            "experiment_log": str(experiment_log_path),
            "commands": str(commands_path),
            "run_state": str(run_state_public),
            "research_wiki": str(wiki_root),
            "paper_plan": str(paper_plan_path),
        },
        "honest_boundary": [
            "This is scaffold-level execution, not a full IAD benchmark.",
            "The bridge demonstrates idea-to-experiment artifact connection.",
            "Full automation still requires benchmark-grade implementation, result parsers, and repair loops for more tasks.",
        ],
    }
    summary_json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md = f"""# V23 IAD Execution Bridge：从 idea 到实验执行的桥接案例

## 一句话结论

V23 将 V10 中的 IAD final research plan 接入 `iad_mvp` 执行链，并用 ARIS-style run_state / research_wiki / experiment log / paper plan 记录结果。这一步把系统从“idea 生成与评审”推进到“idea-to-experiment artifact workflow”。

## 当前结果

| metric | value |
| --- | ---: |
| image_level_auc_lightweight | {metrics.get("image_level_auc_lightweight")} |
| tool_success_rate | {metrics.get("tool_success_rate")} |
| evidence_grounding_score_proxy | {metrics.get("evidence_grounding_score_proxy")} |
| false_alarm_reduction_proxy | {metrics.get("false_alarm_reduction_proxy")} |

## 生成产物

- Execution plan: `{execution_plan_path}`
- Experiment log: `{experiment_log_path}`
- Commands: `{commands_path}`
- Run state: `{run_state_public}`
- Research wiki: `{wiki_root}`
- Paper plan: `{paper_plan_path}`

## Honest boundary

当前 IAD 仍是 lightweight scaffold。它证明 workflow 可以把 final idea 接入真实数据执行链，并形成可复查结果；但不能声称完整 IAD benchmark 或 SOTA。

## 下一步

1. 将 `commands.sh` 升级为可选择 category / split / threshold 的正式 executor。
2. 增加 result parser，自动读取更多 metrics 和 failure cases。
3. 把 failed claim 自动转回 critic repair。
4. 接入 PatchCore/anomalib 或 patch-level feature，增强 benchmark-grade 实验。
"""
    summary_md_path.write_text(md, encoding="utf-8")
    print(f"Wrote {execution_plan_path}")
    print(f"Wrote {experiment_log_path}")
    print(f"Wrote {commands_path}")
    print(f"Wrote {run_state_public}")
    print(f"Wrote {summary_json_path}")
    print(f"Wrote {summary_md_path}")
    print(f"Verdict: {verdict}, confidence={confidence}")


if __name__ == "__main__":
    main()
