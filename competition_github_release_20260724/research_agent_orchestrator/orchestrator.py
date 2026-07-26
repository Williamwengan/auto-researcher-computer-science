#!/usr/bin/env python3
"""A small, auditable multi-agent research workflow orchestrator.

This module is intentionally conservative.  It does not fabricate paper hits or
claim that a new domain has a verified final idea before paper retrieval and
baseline-card extraction have actually happened.  Instead, for arbitrary user
tasks it creates a concrete workspace containing the next actionable artifacts:

  task_spec.yaml
  paper_retrieval_plan.json
  papers.jsonl                         # empty until a real retriever is enabled
  baseline_cards.jsonl                 # planned/unverified baseline cards
  focused_ideas.json                   # task-specific candidate ideas
  experiment_plan.json
  runner_plan.json
  agent_status.json
  RESEARCH_AGENT_REPORT_CN.md

The goal is to make the web demo a real workflow entrypoint, not a template
that pretends evidence exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / "execution_runs/research_agent_orchestrator"


TASK_MODE_PROFILES: dict[str, dict[str, Any]] = {
    "incremental_improvement": {
        "label": "增量改进",
        "goal": "在已有 strongest baseline 上增加一个最小、可开关、可消融的新模块。",
        "module_style": "minimal plug-in module",
        "idea_constraints": [
            "不推翻 baseline 主干训练/推理流程。",
            "新增模块必须能单独开关，便于 paired ablation。",
            "必须说明该模块改善了 baseline 的哪个具体弱点。",
        ],
        "metrics": ["delta_over_strongest_baseline", "paired_ablation_gain", "failure_case_count"],
    },
    "metric_improvement": {
        "label": "指标提升",
        "goal": "围绕主任务指标设计可量化提升，并控制副作用。",
        "module_style": "metric-targeted optimization module",
        "idea_constraints": [
            "明确 primary metric、secondary metric 和 trade-off。",
            "报告均值、方差和失败样例，不只展示单个好结果。",
            "设置不牺牲鲁棒性/校准/误报的约束。",
        ],
        "metrics": ["primary_metric_delta", "secondary_metric_drop", "robustness_delta"],
    },
    "engineering_integration": {
        "label": "工程拼接",
        "goal": "把多个已有工具/模型组合成可复现、可追踪、可替换的系统。",
        "module_style": "tool-orchestrated integration layer",
        "idea_constraints": [
            "每个工具必须有输入输出 schema。",
            "必须记录 provenance、失败原因和 fallback policy。",
            "要比较简单拼接 baseline，证明 agentic orchestration 的增益。",
        ],
        "metrics": ["tool_success_rate", "latency", "end_to_end_success_rate"],
    },
    "evaluation_protocol": {
        "label": "评价协议",
        "goal": "设计更可靠的 benchmark、评测指标或负控制协议。",
        "module_style": "benchmark and verification protocol",
        "idea_constraints": [
            "评价协议必须能区分真实能力和数据泄漏/提示偏置/伪相关。",
            "必须包含 negative controls 和 sanity checks。",
            "输出 result-to-claim 边界，避免过度结论。",
        ],
        "metrics": ["inter_rater_agreement", "false_positive_claim_rate", "stress_test_score"],
    },
    "system_optimization": {
        "label": "系统优化",
        "goal": "提升系统稳定性、效率、可解释性、可追踪性或失败恢复能力。",
        "module_style": "reliability and audit module",
        "idea_constraints": [
            "把失败分成 evidence mismatch、schema mismatch、threshold failure、execution failure。",
            "必须记录日志、状态和可恢复 checkpoint。",
            "优化目标不能只看速度，也要看正确性和可审计性。",
        ],
        "metrics": ["workflow_completion_rate", "tool_success_rate", "recovery_success_rate"],
    },
}


DOMAIN_HINTS: list[tuple[list[str], dict[str, Any]]] = [
    (
        ["遥感", "remote sensing", "变化检测", "change detection", "多时相"],
        {
            "domain": "遥感变化检测",
            "baseline_families": [
                "Siamese CNN / UNet-style change detection baseline",
                "Transformer-based change detection baseline",
                "foundation-model assisted change detection baseline",
            ],
            "datasets": ["LEVIR-CD / WHU-CD / CDD / SYSU-CD（需检索确认具体许可和划分）"],
            "metrics": ["F1", "IoU", "OA", "Kappa", "boundary_F1", "calibration_error"],
            "queries": [
                "remote sensing change detection transformer benchmark dataset metric",
                "multi-temporal remote sensing change detection explainability baseline",
                "evidence grounded explanation remote sensing change detection",
            ],
        },
    ),
    (
        ["医学", "medical", "影像", "segmentation", "分割"],
        {
            "domain": "医学影像分析",
            "baseline_families": [
                "UNet / nnUNet-style supervised baseline",
                "foundation-model or SAM-assisted medical baseline",
                "uncertainty/calibration baseline",
            ],
            "datasets": ["由用户数据或公开医学 benchmark 决定"],
            "metrics": ["Dice", "IoU", "HD95", "sensitivity", "specificity", "calibration_error"],
            "queries": [
                "medical image segmentation benchmark nnUNet SAM uncertainty calibration",
                "trustworthy medical image segmentation explanation baseline",
            ],
        },
    ),
    (
        ["蛋白", "protein", "分子", "molecule", "药物"],
        {
            "domain": "生物分子/蛋白质任务",
            "baseline_families": [
                "sequence/structure foundation model baseline",
                "graph neural network baseline",
                "physics-informed or docking/simulation baseline",
            ],
            "datasets": ["由任务指定，如 PDB/AlphaFold-derived/分子性质数据集等，需检索确认"],
            "metrics": ["RMSE", "MAE", "Spearman", "AUPRC", "success_rate"],
            "queries": [
                "protein property prediction foundation model benchmark baseline",
                "molecule property prediction graph neural network benchmark baseline",
            ],
        },
    ),
]


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def slugify(text: str, max_len: int = 64) -> str:
    base = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "_", text).strip("_")
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    if not base:
        base = "custom_task"
    return f"{base[:max_len]}_{digest}"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )


def yaml_scalar(value: Any) -> str:
    text = str(value).replace("\n", "\\n")
    return json.dumps(text, ensure_ascii=False)


def write_simple_yaml(path: Path, data: dict[str, Any]) -> None:
    lines: list[str] = []
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {yaml_scalar(item)}")
        elif isinstance(value, dict):
            lines.append(f"{key}:")
            for k, v in value.items():
                lines.append(f"  {k}: {yaml_scalar(v)}")
        else:
            lines.append(f"{key}: {yaml_scalar(value)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def detect_domain(task_type: str, direction: str) -> dict[str, Any]:
    text = f"{task_type} {direction}".lower()
    for keywords, profile in DOMAIN_HINTS:
        if any(k.lower() in text for k in keywords):
            return profile
    return {
        "domain": "自定义 AI4S 研究方向",
        "baseline_families": [
            "strongest published task-specific baseline after retrieval",
            "classical or simple lower-bound baseline",
            "foundation-model / tool-augmented baseline when applicable",
        ],
        "datasets": ["由论文检索和用户上传数据共同确定"],
        "metrics": ["primary_task_metric", "robustness_metric", "calibration_or_reliability_metric"],
        "queries": [
            f"{direction} benchmark baseline dataset metric",
            f"{task_type} state of the art method limitation",
            f"{direction} trustworthy explainable agent evaluation",
        ],
    }


@dataclass
class AgentContext:
    task_type: str
    research_direction: str
    task_mode: str
    workspace: Path
    enable_online_retrieval: bool = True

    @property
    def mode_profile(self) -> dict[str, Any]:
        return TASK_MODE_PROFILES.get(self.task_mode) or TASK_MODE_PROFILES["incremental_improvement"]

    @property
    def domain_profile(self) -> dict[str, Any]:
        return detect_domain(self.task_type, self.research_direction)


def abstract_from_openalex(inverted_index: dict[str, list[int]] | None) -> str:
    if not inverted_index:
        return ""
    positions: list[tuple[int, str]] = []
    for word, idxs in inverted_index.items():
        for idx in idxs:
            positions.append((idx, word))
    return " ".join(word for _, word in sorted(positions))[:2000]


def openalex_search(query: str, per_page: int = 5, timeout: int = 10) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({
        "search": query,
        "per-page": str(per_page),
    })
    url = f"https://api.openalex.org/works?{params}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "AI4S-ResearchAgent-Orchestrator/0.1 (competition-demo)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    papers: list[dict[str, Any]] = []
    for item in data.get("results", []):
        authors = []
        for authorship in item.get("authorships", [])[:6]:
            author = authorship.get("author") or {}
            if author.get("display_name"):
                authors.append(author["display_name"])
        primary_location = item.get("primary_location") or {}
        source = primary_location.get("source") or {}
        host = item.get("host_venue") or {}
        papers.append({
            "paper_id": item.get("id", ""),
            "source": "OpenAlex",
            "title": item.get("display_name") or "Untitled",
            "year": item.get("publication_year"),
            "doi": item.get("doi") or "",
            "url": primary_location.get("landing_page_url") or item.get("doi") or item.get("id") or "",
            "venue": source.get("display_name") or host.get("display_name") or "",
            "authors": authors,
            "abstract": abstract_from_openalex(item.get("abstract_inverted_index")),
            "cited_by_count": item.get("cited_by_count", 0),
            "retrieval_query": query,
        })
    return papers


def retrieve_online_papers(queries: list[str], max_papers: int = 10) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    seen: set[str] = set()
    papers: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    for query in queries:
        try:
            hits = openalex_search(query, per_page=5, timeout=10)
            events.append({"query": query, "status": "success", "hit_count": len(hits)})
        except Exception as exc:
            events.append({"query": query, "status": "failed", "error": str(exc)[:500]})
            continue
        for paper in hits:
            key = paper.get("doi") or paper.get("paper_id") or paper.get("title")
            if not key or key in seen:
                continue
            seen.add(key)
            papers.append(paper)
            if len(papers) >= max_papers:
                return papers, events
    return papers, events


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def infer_method_family_from_paper(title: str, abstract: str, fallback: str) -> str:
    text = f"{title} {abstract}".lower()
    if "transformer" in text:
        return "Transformer-based baseline"
    if "siamese" in text:
        return "Siamese-network baseline"
    if "u-net" in text or "unet" in text:
        return "UNet-style baseline"
    if "foundation" in text or "large language" in text or "vision-language" in text:
        return "foundation-model baseline"
    if "benchmark" in text:
        return "benchmark/evaluation baseline"
    return fallback


class TaskSpecAgent:
    name = "TaskSpecAgent"

    def run(self, ctx: AgentContext) -> dict[str, Any]:
        spec = {
            "task_type": ctx.task_type,
            "research_direction": ctx.research_direction,
            "task_mode": ctx.task_mode,
            "task_mode_label": ctx.mode_profile["label"],
            "domain_guess": ctx.domain_profile["domain"],
            "expected_outputs": [
                "papers.jsonl",
                "baseline_cards.jsonl",
                "focused_ideas.json",
                "experiment_plan.json",
                "runner_plan.json",
                "agent_status.json",
            ],
            "claim_policy": "Do not mark claims as verified until paper evidence and runner outputs exist.",
        }
        write_simple_yaml(ctx.workspace / "task_spec.yaml", spec)
        return {"status": "completed", "artifact": "task_spec.yaml", "summary": spec}


class PaperRetrievalAgent:
    name = "PaperRetrievalAgent"

    def run(self, ctx: AgentContext) -> dict[str, Any]:
        profile = ctx.domain_profile
        queries = profile["queries"]
        papers: list[dict[str, Any]] = []
        retrieval_events: list[dict[str, Any]] = []
        retrieval_backend = "OpenAlex"
        status = "needs_retrieval"
        if ctx.enable_online_retrieval:
            papers, retrieval_events = retrieve_online_papers(queries, max_papers=10)
            status = "retrieval_completed" if papers else "retrieval_attempted_no_hits"
        else:
            retrieval_backend = "disabled"
            retrieval_events = [{"status": "disabled", "reason": "online retrieval disabled by CLI flag"}]
        plan = {
            "status": status,
            "retrieval_backend": retrieval_backend,
            "queries": queries,
            "retrieval_events": retrieval_events,
            "paper_count": len(papers),
            "acceptance_criteria": [
                "paper must match task/domain keywords",
                "paper must expose method, dataset, metric or limitation useful for baseline cards",
                "claims remain unverified until title/abstract/source are stored",
            ],
            "next_online_sources": ["OpenAlex", "Semantic Scholar", "arXiv", "OpenReview", "TheCVF"],
        }
        write_json(ctx.workspace / "paper_retrieval_plan.json", plan)
        write_jsonl(ctx.workspace / "papers.jsonl", papers)
        return {"status": status, "artifact": "paper_retrieval_plan.json", "paper_count": len(papers), "summary": plan}


class BaselineCardAgent:
    name = "BaselineCardAgent"

    def run(self, ctx: AgentContext) -> dict[str, Any]:
        cards: list[dict[str, Any]] = []
        papers = read_jsonl(ctx.workspace / "papers.jsonl")
        if papers:
            for idx, paper in enumerate(papers[:8], 1):
                title = paper.get("title", "")
                abstract = paper.get("abstract", "")
                family = infer_method_family_from_paper(title, abstract, ctx.domain_profile["baseline_families"][0])
                cards.append({
                    "baseline_id": f"retrieved_baseline_{idx:02d}",
                    "method_family": family,
                    "evidence_status": "retrieved_unverified",
                    "paper_ids": [paper.get("paper_id", "")],
                    "paper_title": title,
                    "paper_year": paper.get("year"),
                    "paper_url": paper.get("url") or paper.get("doi") or "",
                    "paper_venue": paper.get("venue", ""),
                    "baseline_weakness_to_check": [
                        "extract exact reported datasets and metrics from the paper",
                        "verify whether the method is a fair strongest-baseline candidate",
                        "identify failure modes or limitations from abstract/full text before final claims",
                    ],
                    "reuse_plan": "Use this retrieved paper as a candidate baseline card; promote to verified only after claim verification.",
                })
        for idx, family in enumerate(ctx.domain_profile["baseline_families"], len(cards) + 1):
            cards.append({
                "baseline_id": f"planned_baseline_{idx:02d}",
                "method_family": family,
                "evidence_status": "planned_unverified",
                "paper_ids": [],
                "baseline_weakness_to_check": [
                    "verify whether this baseline reports the target metric on the selected dataset",
                    "extract failure modes and limitations from paper evidence",
                    "check whether the proposed module is a fair paired comparison",
                ],
                "reuse_plan": "Keep the baseline pipeline fixed; add only the proposed module or evaluation wrapper after evidence verification.",
            })
            if len(cards) >= 8:
                break
        write_jsonl(ctx.workspace / "baseline_cards.jsonl", cards)
        status = "retrieved_unverified" if papers else "planned_unverified"
        return {"status": status, "artifact": "baseline_cards.jsonl", "card_count": len(cards), "summary": cards}


def compact_paper_refs(papers: list[dict[str, Any]], limit: int = 5) -> list[str]:
    refs: list[str] = []
    for paper in papers[:limit]:
        title = paper.get("title") or "untitled"
        year = paper.get("year") or "?"
        venue = paper.get("venue") or paper.get("source") or ""
        refs.append(f"{title} ({year}{', ' + venue if venue else ''})")
    return refs


def baseline_names(cards: list[dict[str, Any]], limit: int = 6) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for card in cards:
        name = card.get("paper_title") or card.get("method_family") or card.get("baseline_id")
        if not name or name in seen:
            continue
        seen.add(name)
        names.append(name)
        if len(names) >= limit:
            break
    return names


def infer_concrete_design(ctx: AgentContext, papers: list[dict[str, Any]], cards: list[dict[str, Any]]) -> dict[str, Any]:
    text = f"{ctx.task_type} {ctx.research_direction} " + " ".join(p.get("title", "") for p in papers[:8])
    lower = text.lower()
    mode = ctx.mode_profile
    refs = compact_paper_refs(papers)
    baselines = baseline_names(cards) or ctx.domain_profile["baseline_families"]

    if any(k in lower for k in ["遥感", "remote sensing", "change detection", "变化检测", "多时相"]):
        return {
            "title": f"{mode['label']}：Evidence-Consistent Change Explanation Layer for 多时相遥感变化检测",
            "problem": (
                "多时相遥感变化检测 baseline 通常能输出 change mask 或 change probability，"
                "但解释往往停留在热力图/注意力可视化：它不能说明某个变化区域是否被时相配准误差、季节纹理差异、阴影/云层或背景变化误导。"
            ),
            "baseline_weakness": [
                "Transformer / state-space / Siamese change detection 方法重视 mask quality，但缺少面向 claim 的证据链。",
                "现有解释容易把相关区域可视化当成因果证据，缺少负控制和跨时相一致性检查。",
                "如果不显式区分 real change、registration artifact、seasonal/illumination shift，模型改进很难被可信解释。",
            ],
            "minimal_new_module": "Evidence-Consistent Change Explanation Layer (EC-CEL)",
            "mechanism": (
                "在不改动 baseline 主干的情况下，EC-CEL 接收 baseline 的 change logits/mask、pre/post image patches 和候选变化区域。"
                "它为每个区域构造三类证据：spatial evidence（边界/形状一致性）、temporal evidence（变化前后对象或纹理差异）、"
                "counter-evidence（相邻不变区域、疑似配准误差区域、季节/光照敏感区域）。"
                "模块输出 region-level explanation tuple: <change_type, supporting_evidence, counter_evidence, confidence, abstain_reason>。"
            ),
            "algorithmic_objective": (
                "maximize change-mask quality while minimizing unsupported explanation claims: "
                "score = task_metric + λ1*evidence_consistency - λ2*counter_evidence_violation - λ3*overclaim_rate。"
            ),
            "implementation_plan": [
                "复现或调用检索到的 strongest change-detection baseline，固定输入尺寸、数据划分和 metric parser。",
                "从 baseline mask 中抽取 connected components 或 top-k uncertain regions。",
                "对每个 region 计算 pre/post patch embedding difference、boundary overlap、neighbor unchanged contrast 和 registration-shift proxy。",
                "生成 explanation tuple，并在 confidence 不足时 abstain，而不是强行解释。",
                "用 paired comparison 比较 baseline-only vs baseline+EC-CEL。",
            ],
            "metrics": ["F1", "IoU", "OA", "Kappa", "boundary_F1", "explanation_support_rate", "overclaim_rate", "abstention_rate"],
            "datasets": ["LEVIR-CD", "WHU-CD", "CDD", "SYSU-CD（具体许可和划分由检索论文/用户数据确认）"],
            "ablations": [
                "remove counter-evidence branch",
                "remove temporal consistency score",
                "replace region-level explanation with raw attention map",
                "baseline mask only",
            ],
            "negative_controls": [
                "shuffle pre/post temporal order",
                "misalign post image by a small translation",
                "replace supporting evidence with unrelated unchanged region",
                "use cloud/shadow-like perturbation as false-change stress test",
            ],
            "success_thresholds": [
                "change detection F1/IoU 不低于 baseline-only，且 explanation overclaim_rate 明显下降。",
                "在 temporal shuffle / misregistration 负控制中，系统应降低 confidence 或 abstain。",
                "每个 final explanation claim 必须绑定 region evidence 和检索论文/实验指标之一。",
            ],
            "paper_refs": refs,
            "baseline_refs": baselines,
        }

    if any(k in lower for k in ["医学", "medical", "segmentation", "分割", "影像"]):
        return {
            "title": f"{mode['label']}：Claim-Calibrated Evidence Verifier for 医学影像任务",
            "problem": "医学影像模型即使获得高 Dice/IoU，也可能在边界、罕见病灶和低质量图像上产生过度自信解释。",
            "baseline_weakness": [
                "UNet/nnUNet-style baseline 强在分割精度，但解释和不确定性通常不是 result-to-claim 级别。",
                "foundation-model assisted baseline 可能产生貌似合理但缺少医学证据绑定的区域说明。",
            ],
            "minimal_new_module": "Claim-Calibrated Evidence Verifier (CCEV)",
            "mechanism": "对每个预测区域绑定 image evidence、uncertainty evidence 和 failure-type evidence，低证据区域自动标记为需要人工复核。",
            "algorithmic_objective": "maximize segmentation metric under calibrated selective-risk and evidence-support constraints。",
            "implementation_plan": [
                "固定 strongest segmentation baseline。",
                "抽取 lesion/organ connected components。",
                "计算 uncertainty、boundary agreement 和 evidence support score。",
                "生成 result-to-claim 报告，只允许 supported claim 进入论文草稿。",
            ],
            "metrics": ["Dice", "IoU", "HD95", "sensitivity", "specificity", "calibration_error", "selective_risk"],
            "datasets": ctx.domain_profile["datasets"],
            "ablations": ["remove uncertainty branch", "remove evidence verifier", "no selective abstention"],
            "negative_controls": ["shuffle mask provenance", "corrupt boundary labels", "claim generation without metrics"],
            "success_thresholds": ["Dice/IoU 不低于 baseline", "calibration_error 降低", "unsupported claim rate 降低"],
            "paper_refs": refs,
            "baseline_refs": baselines,
        }

    return {
        "title": f"{mode['label']}：Evidence-Bound Minimal Improvement Module for {ctx.task_type}",
        "problem": (
            f"用户任务“{ctx.research_direction}”已经检索到候选论文/基线，但这些证据仍未经过 claim verification。"
            "当前关键不是直接声称 SOTA，而是把 idea 设计成可复现、可消融、可绑定证据的最小改进。"
        ),
        "baseline_weakness": [
            "检索论文只能作为候选 evidence pool，需要进一步抽取 dataset、metric、limitation。",
            "baseline 改进如果没有 paired comparison，容易变成不可归因的系统堆叠。",
            "大模型生成的解释/结论必须绑定论文或实验指标，否则不能写入 final claim。",
        ],
        "minimal_new_module": "Evidence-Bound Minimal Improvement Module (EB-MIM)",
        "mechanism": (
            "在 strongest retrieved baseline 外侧增加一个 evidence-binding layer："
            "每个预测、解释或实验结论都必须绑定 paper evidence、baseline card、metric row 或 execution log。"
            "没有证据的结论进入 abstain/manual-check 队列。"
        ),
        "algorithmic_objective": mode["goal"],
        "implementation_plan": [
            "从 papers.jsonl 中筛选领域最相关的 5-10 篇论文。",
            "把论文转换成 baseline_cards.jsonl，抽取 dataset、metric、method family 和 limitations。",
            "固定 strongest baseline 主体，只增加 EB-MIM 模块。",
            "运行 baseline-only、baseline+EB-MIM 和 remove-evidence ablation。",
        ],
        "metrics": list(dict.fromkeys(ctx.domain_profile["metrics"] + mode["metrics"] + ["evidence_pass_rate", "claim_boundary_ok"])),
        "datasets": ctx.domain_profile["datasets"],
        "ablations": ["baseline only", "remove evidence binding", "remove task-mode constraint", "no critic repair"],
        "negative_controls": ["shuffle paper-to-claim mappings", "use unrelated baseline cards", "generate claims without metrics"],
        "success_thresholds": [
            "paper_count > 0 and baseline_card_count > 0 before verified-final status",
            "claim_boundary_ok = 1.0 in smoke runner",
            "unsupported claims are excluded from final paper draft",
        ],
        "paper_refs": refs,
        "baseline_refs": baselines,
    }


class IdeaGenerationAgent:
    name = "IdeaGenerationAgent"

    def run(self, ctx: AgentContext) -> dict[str, Any]:
        mode = ctx.mode_profile
        domain = ctx.domain_profile
        papers = read_jsonl(ctx.workspace / "papers.jsonl")
        baseline_cards = read_jsonl(ctx.workspace / "baseline_cards.jsonl")
        design = infer_concrete_design(ctx, papers, baseline_cards)
        baseline_dependency = [
            card.get("method_family", "")
            for card in baseline_cards
            if card.get("method_family")
        ] or domain["baseline_families"]
        evidence_status = "retrieved_unverified" if papers else "unverified_until_retrieval"
        ideas = [
            {
                "idea_id": "idea_01",
                "title": design["title"],
                "task_type": ctx.task_type,
                "research_direction": ctx.research_direction,
                "evidence_status": evidence_status,
                "problem": design["problem"],
                "core_idea": (
                    f"基于检索到的 {len(papers)} 篇候选论文和 {len(baseline_cards)} 张 baseline cards，"
                    f"本方案选择“{design['minimal_new_module']}”作为最小新增模块。"
                    f"它不是重写 baseline，而是在 {', '.join(design['baseline_refs'][:3]) or 'retrieved baseline'} 外侧加入可审计机制：{design['mechanism']}"
                ),
                "baseline_weakness": design["baseline_weakness"],
                "minimal_new_module": design["minimal_new_module"],
                "mechanism": design["mechanism"],
                "algorithmic_objective": design["algorithmic_objective"],
                "implementation_plan": design["implementation_plan"],
                "baseline_dependency": design["baseline_refs"],
                "evidence_paper_refs": design["paper_refs"],
                "required_data": design["datasets"],
                "metrics": design["metrics"],
                "ablations": design["ablations"],
                "negative_controls": design["negative_controls"],
                "success_thresholds": design["success_thresholds"],
            },
            {
                "idea_id": "idea_02",
                "title": f"{mode['label']}：Failure-Aware Evaluation Protocol for {ctx.task_type}",
                "task_type": ctx.task_type,
                "research_direction": ctx.research_direction,
                "evidence_status": evidence_status,
                "core_idea": (
                    "把研究贡献从单点提升扩展为失败诊断协议：记录 baseline 失败样例、证据缺口、"
                    "runner 失败和 result-to-claim 边界，避免只展示漂亮结果。"
                ),
                "problem": "候选 baseline 和 proposed module 即使在 smoke runner 中成功，也可能无法支持真实科学结论，因此需要把失败类型显式化。",
                "baseline_weakness": [
                    "缺少 failure taxonomy 时，实验失败只能变成日志，而不能反馈到 idea repair。",
                    "没有 result-to-claim checker 时，系统容易把 smoke metric 误写成领域 benchmark 结论。",
                ],
                "minimal_new_module": "failure taxonomy + result-to-claim checker",
                "mechanism": "把每次执行结果分为 data_missing、baseline_unreproduced、metric_parser_missing、evidence_mismatch、claim_overreach，并触发对应 repair action。",
                "algorithmic_objective": "turn execution failures into auditable repair signals",
                "baseline_dependency": baseline_dependency,
                "required_data": domain["datasets"],
                "metrics": list(dict.fromkeys(domain["metrics"] + ["claim_boundary_ok", "failure_case_count"])),
                "ablations": ["remove failure taxonomy", "remove claim checker"],
                "negative_controls": ["random failure labels", "claim generation without metrics"],
                "success_thresholds": [
                    "every reported claim must be linked to a metric, log, or paper evidence",
                    "failure analysis identifies at least one actionable repair target",
                ],
            },
            {
                "idea_id": "idea_03",
                "title": f"{mode['label']}：Runner-Ready Research Plan for {ctx.task_type}",
                "task_type": ctx.task_type,
                "research_direction": ctx.research_direction,
                "evidence_status": evidence_status,
                "core_idea": (
                    "把 idea 生成约束为 runner-ready：每个候选方案必须同时给出 dataset manifest、baseline command、"
                    "proposed command、metric parser 和 smoke test。"
                ),
                "problem": "很多自动生成 idea 看似合理，但没有 dataset manifest、baseline command 和 metric parser，因此无法进入实验阶段。",
                "baseline_weakness": [
                    "只生成文字实验计划不能保证可执行。",
                    "没有 runner scaffold 时，baseline/proposed/ablation 无法做 paired comparison。",
                ],
                "minimal_new_module": "runner-readiness planner",
                "mechanism": "对每个 idea 强制生成 prepare_manifest、run_baseline、run_proposed、evaluate、parse_result_to_claim 五个 runner 接口。",
                "algorithmic_objective": "reduce the ideation-execution gap",
                "baseline_dependency": baseline_dependency,
                "required_data": domain["datasets"],
                "metrics": list(dict.fromkeys(domain["metrics"] + ["tool_success_rate", "workflow_completion_rate"])),
                "ablations": ["no runner-readiness constraint", "no metric parser requirement"],
                "negative_controls": ["dummy runner with no metrics", "paper draft without execution artifact"],
                "success_thresholds": [
                    "runner_plan.json contains five required runner files",
                    "generic or domain runner outputs JSON/CSV metrics",
                ],
            },
        ]
        payload = {"ideas": ideas, "selection_policy": "not_final_until_evidence_verified", "recommended_idea_id": "idea_01"}
        write_json(ctx.workspace / "focused_ideas.json", payload)
        return {"status": "completed_unverified", "artifact": "focused_ideas.json", "idea_count": len(ideas), "summary": payload}


class ExperimentPlannerAgent:
    name = "ExperimentPlannerAgent"

    def run(self, ctx: AgentContext) -> dict[str, Any]:
        profile = ctx.domain_profile
        mode = ctx.mode_profile
        plan = {
            "status": "planned",
            "scope": "experiment plan scaffold; not executed benchmark",
            "steps": [
                "enable paper retrieval and populate papers.jsonl",
                "convert papers into evidence-backed baseline_cards.jsonl",
                "select strongest reproducible baseline",
                "prepare dataset manifest and fixed split",
                "run baseline with locked preprocessing and metric parser",
                "run proposed module under paired comparison",
                "run ablations and negative controls",
                "parse metrics into result_to_claim.md",
            ],
            "datasets": profile["datasets"],
            "metrics": list(dict.fromkeys(profile["metrics"] + mode["metrics"])),
            "ablations": [
                "baseline only",
                "baseline + proposed module",
                "baseline + proposed module without evidence checking",
                "baseline + proposed module without task-mode constraint",
            ],
            "negative_controls": [
                "shuffle paper-to-claim evidence",
                "replace domain baseline with unrelated baseline",
                "run idea generation without baseline weakness constraints",
            ],
        }
        write_json(ctx.workspace / "experiment_plan.json", plan)
        return {"status": "planned", "artifact": "experiment_plan.json", "summary": plan}


class RunnerBuilderAgent:
    name = "RunnerBuilderAgent"

    def run(self, ctx: AgentContext) -> dict[str, Any]:
        runner_dir = ctx.workspace / "runner_scaffold"
        runner_dir.mkdir(parents=True, exist_ok=True)
        self._write_runner_files(ctx, runner_dir)
        plan = {
            "status": "runner_scaffold_generated",
            "safe_execution_policy": "human authorization required before running any command",
            "required_runner_files": [
                "runner_scaffold/prepare_manifest.py",
                "runner_scaffold/run_baseline.py",
                "runner_scaffold/run_proposed.py",
                "runner_scaffold/evaluate.py",
                "runner_scaffold/parse_result_to_claim.py",
            ],
            "run_command": "bash runner_scaffold/run_all.sh",
            "available_demo_runner": "generic execution smoke runner",
            "not_claimed": [
                "generated scaffold is a smoke runner, not a real domain benchmark",
                "not a SOTA claim until baseline evidence and execution metrics exist",
            ],
        }
        write_json(ctx.workspace / "runner_plan.json", plan)
        return {"status": "generated", "artifact": "runner_plan.json", "summary": plan}

    def _write_runner_files(self, ctx: AgentContext, runner_dir: Path) -> None:
        task_meta = {
            "task_type": ctx.task_type,
            "research_direction": ctx.research_direction,
            "task_mode": ctx.task_mode,
            "domain": ctx.domain_profile["domain"],
            "metrics": ctx.domain_profile["metrics"],
        }
        write_json(runner_dir / "task_meta.json", task_meta)
        (runner_dir / "prepare_manifest.py").write_text("""#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--task-meta', default='task_meta.json')
    p.add_argument('--output', default='../data/manifest.jsonl')
    args=p.parse_args()
    meta=json.loads(Path(args.task_meta).read_text(encoding='utf-8'))
    out=Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    row={
      'sample_id':'smoke_001',
      'task_type':meta.get('task_type'),
      'research_direction':meta.get('research_direction'),
      'split':'smoke',
      'label_available':False,
      'note':'Synthetic manifest row for workflow execution smoke test; replace with real dataset manifest for benchmark.'
    }
    out.write_text(json.dumps(row, ensure_ascii=False)+'\\n', encoding='utf-8')
    print(f'Wrote {out}')
if __name__=='__main__': main()
""", encoding="utf-8")
        (runner_dir / "run_baseline.py").write_text("""#!/usr/bin/env python3
import argparse, csv, json
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--manifest', default='../data/manifest.jsonl')
    p.add_argument('--output', default='../outputs/baseline_scores.csv')
    args=p.parse_args()
    rows=[json.loads(x) for x in Path(args.manifest).read_text(encoding='utf-8').splitlines() if x.strip()]
    out=Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=['sample_id','plan_specificity','artifact_readiness','risk_control','note'])
        w.writeheader()
        for r in rows:
            w.writerow({'sample_id':r['sample_id'],'plan_specificity':0.58,'artifact_readiness':0.52,'risk_control':0.50,'note':'baseline scaffold; not domain benchmark'})
    print(f'Wrote {out}')
if __name__=='__main__': main()
""", encoding="utf-8")
        (runner_dir / "run_proposed.py").write_text("""#!/usr/bin/env python3
import argparse, csv
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--baseline', default='../outputs/baseline_scores.csv')
    p.add_argument('--output', default='../outputs/proposed_scores.csv')
    args=p.parse_args()
    rows=list(csv.DictReader(Path(args.baseline).open(encoding='utf-8')))
    out=Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=['sample_id','plan_specificity','artifact_readiness','risk_control','note'])
        w.writeheader()
        for r in rows:
            w.writerow({
              'sample_id':r['sample_id'],
              'plan_specificity':round(float(r['plan_specificity'])+0.10, 4),
              'artifact_readiness':round(float(r['artifact_readiness'])+0.12, 4),
              'risk_control':round(float(r['risk_control'])+0.16, 4),
              'note':'proposed scaffold; validates runner interface only'
            })
    print(f'Wrote {out}')
if __name__=='__main__': main()
""", encoding="utf-8")
        (runner_dir / "evaluate.py").write_text("""#!/usr/bin/env python3
import argparse, csv, json
from pathlib import Path

def avg(rows, key): return sum(float(r[key]) for r in rows)/max(1,len(rows))
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--baseline', default='../outputs/baseline_scores.csv')
    p.add_argument('--proposed', default='../outputs/proposed_scores.csv')
    p.add_argument('--output-json', default='../outputs/execution_metrics.json')
    args=p.parse_args()
    b=list(csv.DictReader(Path(args.baseline).open(encoding='utf-8')))
    q=list(csv.DictReader(Path(args.proposed).open(encoding='utf-8')))
    metrics={
      'status':'success',
      'evaluation_scope':'task-specific scaffold smoke test; not a domain benchmark',
      'plan_specificity_delta':round(avg(q,'plan_specificity')-avg(b,'plan_specificity'),4),
      'artifact_readiness_delta':round(avg(q,'artifact_readiness')-avg(b,'artifact_readiness'),4),
      'risk_control_delta':round(avg(q,'risk_control')-avg(b,'risk_control'),4),
      'workflow_completion_rate':1.0,
      'tool_success_rate':1.0,
      'claim_boundary_ok':1.0
    }
    out=Path(args.output_json); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'metrics':metrics}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote {out}')
if __name__=='__main__': main()
""", encoding="utf-8")
        (runner_dir / "parse_result_to_claim.py").write_text("""#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--metrics', default='../outputs/execution_metrics.json')
    p.add_argument('--output', default='../outputs/result_to_claim.md')
    args=p.parse_args()
    data=json.loads(Path(args.metrics).read_text(encoding='utf-8'))
    metrics=data.get('metrics', data)
    text='\\n'.join([
      '# Result-to-Claim Boundary',
      '',
      'This run validates the task-specific runner scaffold and workflow execution interface.',
      '',
      'It does not claim domain benchmark performance or SOTA.',
      '',
      '## Metrics',
      '',
      *[f'- {k}: {v}' for k,v in metrics.items()],
      '',
      '## Allowed claim',
      '',
      'The workflow can create and execute a human-authorized scaffold runner for this task.',
      '',
      '## Disallowed claim',
      '',
      'Do not claim scientific performance improvement until real data, real baselines, and verified metrics are connected.',
      ''
    ])
    out=Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding='utf-8')
    print(f'Wrote {out}')
if __name__=='__main__': main()
""", encoding="utf-8")
        (runner_dir / "run_all.sh").write_text("""#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python prepare_manifest.py
python run_baseline.py
python run_proposed.py
python evaluate.py
python parse_result_to_claim.py
echo "Task-specific scaffold smoke runner completed."
""", encoding="utf-8")


AGENTS = [
    TaskSpecAgent(),
    PaperRetrievalAgent(),
    BaselineCardAgent(),
    IdeaGenerationAgent(),
    ExperimentPlannerAgent(),
    RunnerBuilderAgent(),
]


def build_report(ctx: AgentContext, records: list[dict[str, Any]]) -> str:
    paper_record = next((x for x in records if x.get("agent") == "PaperRetrievalAgent"), {})
    paper_count = paper_record.get("paper_count", 0)
    lines = [
        "# Research Agent Orchestrator 工作区报告",
        "",
        f"生成时间：{now()}",
        "",
        f"- 具体任务：{ctx.task_type}",
        f"- 研究方向：{ctx.research_direction}",
        f"- 任务类型：{ctx.mode_profile['label']}",
        f"- 识别领域：{ctx.domain_profile['domain']}",
        "",
        "## 结论",
        "",
        "该工作区由多阶段 agent 生成。系统会尝试联网检索真实论文；检索失败时不会伪造论文、baseline 或实验结论。",
        "",
        f"- 当前论文检索数量：{paper_count}",
        f"- 在线检索开关：{'开启' if ctx.enable_online_retrieval else '关闭'}",
        "- runner scaffold：已生成，可用于授权执行链路 smoke test；真实 benchmark 仍需接入领域数据和 baseline。",
        "",
        "## Agent 执行记录",
        "",
    ]
    for item in records:
        lines.append(f"- **{item['agent']}**：{item['status']} → `{item.get('artifact', '')}`")
    lines += [
        "",
        "## 下一步",
        "",
        "1. 启用真实论文检索后填充 `papers.jsonl`。",
        "2. 将检索论文转换为 evidence-backed `baseline_cards.jsonl`。",
        "3. 重新运行 focused idea generation / critic repair / evidence verification。",
        "4. 为该领域实现 runner_plan.json 中列出的 runner 文件。",
        "5. 经网页人工授权后运行 baseline/proposed/ablation，并生成 result-to-claim。",
        "",
    ]
    return "\n".join(lines)


def run_orchestrator(
    task_type: str,
    research_direction: str,
    task_mode: str,
    output_root: Path,
    enable_online_retrieval: bool = True,
) -> dict[str, Any]:
    task_type = task_type.strip() or "自定义科研任务"
    research_direction = research_direction.strip() or "用户输入的研究方向"
    task_mode = task_mode.strip() or "incremental_improvement"
    workspace = output_root / slugify(f"{task_type}_{research_direction}_{task_mode}", 80)
    workspace.mkdir(parents=True, exist_ok=True)
    ctx = AgentContext(
        task_type=task_type,
        research_direction=research_direction,
        task_mode=task_mode,
        workspace=workspace,
        enable_online_retrieval=enable_online_retrieval,
    )

    records: list[dict[str, Any]] = []
    print(f"[ResearchAgent] workspace={workspace}", flush=True)
    for agent in AGENTS:
        print(f"[ResearchAgent] running {agent.name}", flush=True)
        result = agent.run(ctx)
        records.append({"agent": agent.name, **result})

    paper_record = next((x for x in records if x.get("agent") == "PaperRetrievalAgent"), {})
    paper_count = int(paper_record.get("paper_count") or 0)
    status = {
        "ok": True,
        "status": "new_task_onboarding_completed",
        "verified_final_idea": False,
        "reason": "online paper retrieval may populate evidence, but final scientific claims remain unverified until reference-claim verification and real runner metrics complete",
        "online_retrieval_enabled": enable_online_retrieval,
        "paper_count": paper_count,
        "generated_at": now(),
        "workspace": display_path(workspace),
        "task_type": task_type,
        "research_direction": research_direction,
        "task_mode": task_mode,
        "task_mode_label": ctx.mode_profile["label"],
        "domain_profile": ctx.domain_profile,
        "records": records,
        "artifacts": {
            "task_spec": display_path(workspace / "task_spec.yaml"),
            "paper_retrieval_plan": display_path(workspace / "paper_retrieval_plan.json"),
            "papers": display_path(workspace / "papers.jsonl"),
            "baseline_cards": display_path(workspace / "baseline_cards.jsonl"),
            "focused_ideas": display_path(workspace / "focused_ideas.json"),
            "experiment_plan": display_path(workspace / "experiment_plan.json"),
            "runner_plan": display_path(workspace / "runner_plan.json"),
            "runner_scaffold": display_path(workspace / "runner_scaffold"),
            "report": display_path(workspace / "RESEARCH_AGENT_REPORT_CN.md"),
        },
    }
    write_json(workspace / "agent_status.json", status)
    (workspace / "RESEARCH_AGENT_REPORT_CN.md").write_text(build_report(ctx, records), encoding="utf-8")
    return status


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the minimal AI4S research-agent orchestrator.")
    parser.add_argument("--task-type", required=True)
    parser.add_argument("--research-direction", required=True)
    parser.add_argument("--task-mode", default="incremental_improvement")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--result-json", type=Path, default=None)
    parser.add_argument("--disable-online-retrieval", action="store_true")
    args = parser.parse_args()

    output_root = args.output_root if args.output_root.is_absolute() else ROOT / args.output_root
    status = run_orchestrator(
        args.task_type,
        args.research_direction,
        args.task_mode,
        output_root,
        enable_online_retrieval=not args.disable_online_retrieval,
    )
    if args.result_json:
        result_json = args.result_json if args.result_json.is_absolute() else ROOT / args.result_json
        write_json(result_json, status)
    print(json.dumps(status, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
