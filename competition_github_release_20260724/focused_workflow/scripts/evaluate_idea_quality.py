import argparse
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path


DIMENSIONS = [
    ("baseline_grounding_score", 0.15),
    ("failure_mode_specificity_score", 0.15),
    ("mechanism_specificity_score", 0.15),
    ("metric_alignment_score", 0.10),
    ("experiment_executability_score", 0.15),
    ("falsifiability_score", 0.10),
    ("novelty_proxy_score", 0.05),
    ("distinctness_score", 0.05),
    ("risk_awareness_score", 0.05),
    ("implementation_readiness_score", 0.05),
]


REQUIRED_IDEA_FIELDS = [
    "title",
    "task_type",
    "direct_baselines",
    "transfer_baselines",
    "borrowed_components",
    "new_component",
    "why_it_may_work",
    "datasets",
    "metrics",
    "ablations",
    "risks",
    "failure_criteria",
    "minimal_new_module",
    "mvp_artifacts",
    "implementation_plan",
    "expected_outputs",
]


REQUIRED_PLAN_FIELDS = [
    "idea_title",
    "baseline_to_compare",
    "data_preparation",
    "implementation_steps",
    "evaluation_metrics",
    "ablation_studies",
    "success_criteria",
    "failure_cases",
    "estimated_compute",
    "estimated_timeline",
]


FAILURE_TERMS = [
    "weakness",
    "failure",
    "fails",
    "error",
    "risk",
    "limitation",
    "miss",
    "over",
    "under",
    "false",
    "shift",
    "noise",
    "ambiguous",
    "uncertain",
    "hallucinat",
    "collision",
    "penetration",
    "sliding",
    "calibration",
    "contamination",
    "occluded",
]


MECHANISM_TERMS = [
    "input",
    "output",
    "state",
    "memory",
    "algorithm",
    "steps",
    "module",
    "decoder",
    "adapter",
    "calibrator",
    "verifier",
    "retrieval",
    "audit",
    "policy",
    "loss",
    "objective",
    "training",
    "sampling",
    "confidence",
    "threshold",
]


METRIC_TERMS = [
    "improve",
    "reduce",
    "increase",
    "decrease",
    "coverage",
    "accuracy",
    "error",
    "risk",
    "auroc",
    "fid",
    "precision",
    "recall",
    "score",
    "rate",
    "mae",
    "iou",
]


NEGATIVE_CONTROL_TERMS = [
    "negative control",
    "random",
    "shuffled",
    "without",
    "remove",
    "no ",
    "disable",
    "ablation",
    "oracle",
    "unverified",
]


SHALLOW_PATTERNS = [
    ("baseline_plus_vlm_only", re.compile(r"\b(vlm|llava|qwen|gpt|clip)\b.*\breport\b", re.I)),
    ("baseline_plus_sam_only", re.compile(r"\b(sam|sam2)\b.*\b(refine|segment|mask)\b", re.I)),
    ("baseline_plus_retrieval_only", re.compile(r"\bretrieval\b|\bretrieve\b", re.I)),
]


def load_json(path: Path):
    return json.loads(path.read_text())


def load_jsonl(path: Path):
    items = []
    if not path.exists():
        return items
    for line in path.read_text().splitlines():
        if line.strip():
            items.append(json.loads(line))
    return items


def nonempty(value):
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return len(value) > 0
    return True


def text_blob(*values):
    parts = []
    for value in values:
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(str(item) for item in value)
        elif isinstance(value, dict):
            parts.append(json.dumps(value, ensure_ascii=False))
        elif value is not None:
            parts.append(str(value))
    return "\n".join(parts)


def count_terms(text, terms):
    low = text.lower()
    return sum(1 for term in terms if term.lower() in low)


def clamp_score(value):
    return int(max(1, min(10, round(value))))


def score_from_count(count, base=4, step=1, cap=10):
    return clamp_score(min(cap, base + count * step))


def list_count(idea, key):
    value = idea.get(key)
    return len(value) if isinstance(value, list) else 0


def find_matching_plan(idea, plans):
    title = idea.get("title")
    for plan in plans:
        if plan.get("idea_title") == title:
            return plan
    return {}


def compute_required_coverage(item, required_fields):
    if not required_fields:
        return 1.0
    present = sum(1 for field in required_fields if nonempty(item.get(field)))
    return present / len(required_fields)


def has_time_bound(text):
    return bool(re.search(r"\b(1-2|1|2|3|4|5|7|14)\s*(week|weeks|day|days)\b", text, re.I))


def has_precise_mvp_artifacts(text):
    patterns = [
        r"\b(required_files|expected_tables|output_dir|manifest|script|checkpoint|config|jsonl|csv)\b",
        r"\b(day\s*1|day\s*2|day_1|week\s*1|week_1)\b",
        r"\b(train|val|test)\s*(split|set)\b",
        r"\b\d+\s*(samples|objects|clips|prompts|scenes|categories|images)\b",
    ]
    return sum(1 for pattern in patterns if re.search(pattern, text, re.I))


def has_algorithmic_objective(text):
    patterns = [
        r"\b(loss|objective|gradient|likelihood|conformal|calibration|ranker|classifier|adapter|decoder)\b",
        r"\b(input|output|state|memory)\b",
        r"\bthreshold|confidence|interval|score|policy\b",
    ]
    return sum(1 for pattern in patterns if re.search(pattern, text, re.I))


def distinctness_scores(ideas):
    token_sets = []
    for idea in ideas:
        blob = text_blob(
            idea.get("title"),
            idea.get("new_component"),
            idea.get("why_it_may_work"),
            idea.get("direct_baselines"),
            idea.get("metrics"),
        ).lower()
        tokens = set(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]{2,}", blob))
        stop = {
            "the",
            "and",
            "for",
            "with",
            "that",
            "this",
            "from",
            "into",
            "using",
            "baseline",
            "baselines",
            "metrics",
            "score",
            "scores",
        }
        token_sets.append(tokens - stop)

    scores = []
    for idx, tokens in enumerate(token_sets):
        if len(token_sets) == 1:
            scores.append(10)
            continue
        similarities = []
        for jdx, other in enumerate(token_sets):
            if idx == jdx:
                continue
            denom = len(tokens | other) or 1
            similarities.append(len(tokens & other) / denom)
        max_sim = max(similarities) if similarities else 0
        scores.append(clamp_score(10 - max_sim * 10))
    return scores


def anti_shallow_flags(idea):
    flags = []
    blob = text_blob(
        idea.get("title"),
        idea.get("new_component"),
        idea.get("why_it_may_work"),
        idea.get("implementation_plan"),
    )
    low = blob.lower()

    for name, pattern in SHALLOW_PATTERNS:
        if pattern.search(blob):
            has_mechanism = count_terms(low, MECHANISM_TERMS) >= 4
            has_ablation = list_count(idea, "ablations") >= 3
            if not (has_mechanism and has_ablation):
                flags.append(name)

    if count_terms(blob, MECHANISM_TERMS) < 4:
        flags.append("no_minimal_new_module")
    if list_count(idea, "failure_criteria") == 0:
        flags.append("no_failure_criteria")
    if count_terms(text_blob(idea.get("ablations")), NEGATIVE_CONTROL_TERMS) < 2:
        flags.append("no_negative_control")
    if list_count(idea, "metrics") == 0:
        flags.append("no_metric_alignment")
    if not has_time_bound(blob):
        flags.append("no_mvp")
    if "baseline weakness" not in low and count_terms(blob, FAILURE_TERMS) < 3:
        flags.append("unclear_baseline_difference")

    return sorted(set(flags))


def score_idea(idea, plan, distinctness_score):
    idea_blob = text_blob(
        idea.get("title"),
        idea.get("task_type"),
        idea.get("direct_baselines"),
        idea.get("transfer_baselines"),
        idea.get("borrowed_components"),
        idea.get("new_component"),
        idea.get("why_it_may_work"),
        idea.get("metrics"),
        idea.get("ablations"),
        idea.get("risks"),
        idea.get("failure_criteria"),
        idea.get("minimal_new_module"),
        idea.get("mvp_artifacts"),
        idea.get("implementation_plan"),
    )
    plan_blob = text_blob(*plan.values()) if plan else ""
    all_blob = idea_blob + "\n" + plan_blob

    baseline_count = list_count(idea, "direct_baselines")
    metric_count = list_count(idea, "metrics")
    ablation_count = list_count(idea, "ablations")
    failure_count = list_count(idea, "failure_criteria")
    implementation_step_count = list_count(idea, "implementation_plan")
    plan_step_count = list_count(plan, "implementation_steps") if plan else 0

    flags = anti_shallow_flags(idea)

    baseline_grounding = clamp_score(
        3
        + min(3, baseline_count)
        + min(2, count_terms(all_blob, FAILURE_TERMS))
        + (1 if "baseline weakness" in all_blob.lower() else 0)
        + (1 if plan.get("baseline_to_compare") else 0)
    )

    failure_specificity = clamp_score(
        3
        + min(3, count_terms(all_blob, FAILURE_TERMS))
        + min(2, failure_count)
        + (1 if any(ch.isdigit() for ch in text_blob(idea.get("failure_criteria"))) else 0)
        + (1 if plan.get("failure_cases") else 0)
    )

    mechanism_specificity = clamp_score(
        3
        + min(4, count_terms(text_blob(idea.get("new_component")), MECHANISM_TERMS))
        + min(2, implementation_step_count // 2)
        + (1 if "input" in all_blob.lower() or "output" in all_blob.lower() else 0)
    )

    metric_alignment = clamp_score(
        3
        + min(3, metric_count // 3)
        + min(2, count_terms(text_blob(idea.get("why_it_may_work")), METRIC_TERMS))
        + (1 if plan.get("evaluation_metrics") else 0)
        + (1 if plan.get("success_criteria") else 0)
    )

    experiment_executability = clamp_score(
        3
        + min(2, list_count(idea, "datasets"))
        + min(2, (implementation_step_count + plan_step_count) // 4)
        + (1 if has_time_bound(all_blob) else 0)
        + (1 if plan.get("estimated_compute") else 0)
        + (1 if plan.get("data_preparation") else 0)
    )

    falsifiability = clamp_score(
        3
        + min(3, failure_count)
        + min(2, count_terms(text_blob(idea.get("ablations")), NEGATIVE_CONTROL_TERMS))
        + (1 if plan.get("success_criteria") else 0)
        + (1 if plan.get("ablation_studies") else 0)
    )

    novelty_proxy = clamp_score(
        8
        - min(3, len(flags))
        + (1 if "not trivial" in all_blob.lower() or "why not trivial" in all_blob.lower() else 0)
        + (1 if count_terms(text_blob(idea.get("new_component")), MECHANISM_TERMS) >= 5 else 0)
    )

    risk_awareness = clamp_score(
        3
        + min(4, list_count(idea, "risks"))
        + min(2, count_terms(text_blob(idea.get("risks")), FAILURE_TERMS))
        + (1 if plan.get("failure_cases") else 0)
    )

    implementation_readiness = clamp_score(
        3
        + min(3, implementation_step_count // 2)
        + min(2, plan_step_count // 3)
        + (1 if plan.get("estimated_timeline") else 0)
        + (1 if plan.get("estimated_compute") else 0)
    )

    dims = {
        "baseline_grounding_score": baseline_grounding,
        "failure_mode_specificity_score": failure_specificity,
        "mechanism_specificity_score": mechanism_specificity,
        "metric_alignment_score": metric_alignment,
        "experiment_executability_score": experiment_executability,
        "falsifiability_score": falsifiability,
        "novelty_proxy_score": novelty_proxy,
        "distinctness_score": distinctness_score,
        "risk_awareness_score": risk_awareness,
        "implementation_readiness_score": implementation_readiness,
    }
    raw_quality = sum(dims[name] * weight for name, weight in DIMENSIONS) * 10
    penalty, penalty_reasons = granularity_penalty(idea, plan)
    if isinstance(idea.get("minimal_new_module"), dict):
        penalty = max(0.0, penalty - 4.0)
        if "mvp_artifacts_not_precise" in penalty_reasons:
            pass
    if isinstance(idea.get("mvp_artifacts"), dict):
        penalty = max(0.0, penalty - 6.0)
        penalty_reasons = [
            reason
            for reason in penalty_reasons
            if reason not in {"mvp_artifacts_not_precise"}
        ]
    if penalty <= 0:
        penalty = 0.0
        penalty_reasons = []
    quality = max(1.0, raw_quality - penalty)

    return {
        "title": idea.get("title", ""),
        "task_type": idea.get("task_type", ""),
        "schema_field_coverage": round(compute_required_coverage(idea, REQUIRED_IDEA_FIELDS), 3),
        "plan_field_coverage": round(compute_required_coverage(plan, REQUIRED_PLAN_FIELDS), 3) if plan else 0,
        "counts": {
            "direct_baselines": baseline_count,
            "metrics": metric_count,
            "ablations": ablation_count,
            "failure_criteria": failure_count,
            "implementation_steps": implementation_step_count,
            "plan_implementation_steps": plan_step_count,
        },
        "anti_shallow_flags": flags,
        "dimension_scores": dims,
        "raw_quality_score": round(raw_quality, 1),
        "granularity_penalty": round(penalty, 1),
        "granularity_penalty_reasons": penalty_reasons,
        "idea_quality_score": round(quality, 1),
        "quality_band": quality_band(quality),
    }


def quality_band(score):
    if score >= 85:
        return "mainline_candidate"
    if score >= 70:
        return "usable_with_repair"
    if score >= 55:
        return "needs_repair"
    return "reject"


def granularity_penalty(idea, plan):
    """Penalty for proposal-shaped ideas that are complete but not implementation-ready."""
    blob = text_blob(
        idea.get("new_component"),
        idea.get("why_it_may_work"),
        idea.get("implementation_plan"),
        plan.get("implementation_steps") if plan else [],
        plan.get("data_preparation") if plan else [],
        plan.get("estimated_timeline") if plan else "",
    )
    penalty = 0.0
    reasons = []

    if has_precise_mvp_artifacts(blob) < 2:
        penalty += 6.0
        reasons.append("mvp_artifacts_not_precise")
    if has_algorithmic_objective(blob) < 2:
        penalty += 6.0
        reasons.append("algorithmic_objective_not_explicit")
    if "minimum viable experiment" not in blob.lower() and "mvp" not in blob.lower():
        penalty += 4.0
        reasons.append("mvp_not_explicit")
    if not re.search(r"\b\d+(\.\d+)?\s*%|\bat least\s+\d+|\bless than\s+\d+|\bmore than\s+\d+", blob, re.I):
        penalty += 4.0
        reasons.append("quantitative_thresholds_weak")
    if not re.search(r"\bnegative control\b|\brandom\b|\bshuffled\b|\boracle\b|\bunverified\b", blob, re.I):
        penalty += 4.0
        reasons.append("negative_control_weak")

    return penalty, reasons


def pairwise_rank(scores):
    results = []
    for i, left in enumerate(scores):
        wins = 0
        losses = 0
        ties = 0
        comparisons = []
        for j, right in enumerate(scores):
            if i == j:
                continue
            left_score = left["idea_quality_score"]
            right_score = right["idea_quality_score"]
            if math.isclose(left_score, right_score, abs_tol=1.0):
                winner = "tie"
                ties += 1
            elif left_score > right_score:
                winner = left["title"]
                wins += 1
            else:
                winner = right["title"]
                losses += 1
            comparisons.append(
                {
                    "against": right["title"],
                    "winner": winner,
                    "score_delta": round(left_score - right_score, 1),
                }
            )
        total = wins + losses + ties
        win_rate = (wins + 0.5 * ties) / total if total else 1.0
        results.append(
            {
                "title": left["title"],
                "wins": wins,
                "losses": losses,
                "ties": ties,
                "pairwise_win_rate": round(win_rate, 3),
                "insight_like_score": round(win_rate * 100, 1),
                "comparisons": comparisons,
            }
        )
    return sorted(results, key=lambda item: item["insight_like_score"], reverse=True)


def unique_output_path(path: Path, overwrite: bool):
    if overwrite or not path.exists():
        return path
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return path.with_name(f"{path.stem}_{stamp}{path.suffix}")


def write_report(run_dir, scores, pairwise, output_path):
    ranked = sorted(scores, key=lambda item: item["idea_quality_score"], reverse=True)
    avg = sum(item["idea_quality_score"] for item in scores) / len(scores) if scores else 0
    top = ranked[0] if ranked else None

    lines = [
        "# Idea Quality 自动评价报告",
        "",
        f"Run dir: `{run_dir}`",
        "",
        "## 总览",
        "",
        f"- Ideas: {len(scores)}",
        f"- Average quality score: {avg:.1f}/100",
        f"- Top idea: {top['title'] if top else 'N/A'}",
        f"- Top score: {top['idea_quality_score'] if top else 'N/A'}/100",
        "",
        "## 排名",
        "",
        "| Rank | Idea | Quality | Band | Flags |",
        "|---:|---|---:|---|---|",
    ]

    for idx, item in enumerate(ranked, start=1):
        flags = ", ".join(item["anti_shallow_flags"]) if item["anti_shallow_flags"] else "-"
        lines.append(
            f"| {idx} | {item['title']} | {item['idea_quality_score']} | {item['quality_band']} | {flags} |"
        )

    lines.extend(
        [
            "",
            "## 维度评分",
            "",
        ]
    )
    for item in ranked:
        lines.extend(
            [
                f"### {item['title']}",
                "",
                f"- Raw structural score: {item['raw_quality_score']}/100",
                f"- Granularity penalty: -{item['granularity_penalty']}",
                f"- Penalty reasons: {', '.join(item['granularity_penalty_reasons']) if item['granularity_penalty_reasons'] else '无'}",
                f"- Quality Score: {item['idea_quality_score']}/100",
                f"- Quality Band: `{item['quality_band']}`",
                f"- Schema field coverage: {item['schema_field_coverage']}",
                f"- Plan field coverage: {item['plan_field_coverage']}",
                f"- Anti-shallow flags: {', '.join(item['anti_shallow_flags']) if item['anti_shallow_flags'] else '无'}",
                "",
                "| Dimension | Score |",
                "|---|---:|",
            ]
        )
        for name, _weight in DIMENSIONS:
            lines.append(f"| {name} | {item['dimension_scores'][name]} |")
        lines.extend(
            [
                "",
                "Counts:",
                "",
            ]
        )
        for key, value in item["counts"].items():
            lines.append(f"- {key}: {value}")
        lines.append("")

    lines.extend(
        [
            "## Pairwise Ranking",
            "",
            "| Idea | Win Rate | Insight-like Score |",
            "|---|---:|---:|",
        ]
    )
    for item in pairwise:
        lines.append(
            f"| {item['title']} | {item['pairwise_win_rate']} | {item['insight_like_score']} |"
        )

    lines.extend(
        [
            "",
            "## 解读",
            "",
            "- `mainline_candidate`：可以直接进入 MVP 计划。",
            "- `usable_with_repair`：有价值，但需要补机制或实验细节。",
            "- `needs_repair`：结构完整但仍偏泛，应进入 critic/repair。",
            "- `reject`：不建议保留，应重新生成。",
            "",
            "注意：这是规则启发式自动评分，不替代人工审查。它用于发现低分项，并指导下一轮 prompt/schema 改进。",
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Evaluate focused research idea quality without modifying generated ideas.")
    parser.add_argument("run_dir", help="Directory containing focused_ideas.json, experiment_plan.json, baseline_cards.jsonl")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing score/report files instead of timestamping")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    if not run_dir.exists():
        raise FileNotFoundError(f"Missing run_dir: {run_dir}")

    ideas_path = run_dir / "focused_ideas.json"
    plans_path = run_dir / "experiment_plan.json"
    baselines_path = run_dir / "baseline_cards.jsonl"
    if not ideas_path.exists() or not plans_path.exists() or not baselines_path.exists():
        raise FileNotFoundError("run_dir must contain focused_ideas.json, experiment_plan.json, and baseline_cards.jsonl")

    ideas = load_json(ideas_path)
    plans = load_json(plans_path)
    baselines = load_jsonl(baselines_path)

    if not isinstance(ideas, list) or not isinstance(plans, list):
        raise ValueError("focused_ideas.json and experiment_plan.json must be JSON lists")

    distinctness = distinctness_scores(ideas)
    scores = []
    for idx, idea in enumerate(ideas):
        plan = find_matching_plan(idea, plans)
        scores.append(score_idea(idea, plan, distinctness[idx]))

    pairwise = pairwise_rank(scores)
    avg = sum(item["idea_quality_score"] for item in scores) / len(scores) if scores else 0
    top = max(scores, key=lambda item: item["idea_quality_score"]) if scores else None

    payload = {
        "run_dir": str(run_dir),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rubric_version": "focused_workflow_v0_3",
        "source_files_preserved": True,
        "baseline_cards": len(baselines),
        "ideas": len(ideas),
        "experiment_plans": len(plans),
        "average_quality_score": round(avg, 1),
        "top_idea": top["title"] if top else None,
        "top_quality_score": top["idea_quality_score"] if top else None,
        "scores": scores,
    }

    score_path = unique_output_path(run_dir / "idea_quality_scores.json", args.overwrite)
    pairwise_path = unique_output_path(run_dir / "pairwise_ranking.json", args.overwrite)
    report_path = unique_output_path(run_dir / "idea_quality_report_CN.md", args.overwrite)

    score_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pairwise_path.write_text(json.dumps(pairwise, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(run_dir, scores, pairwise, report_path)

    print("Saved:", score_path)
    print("Saved:", pairwise_path)
    print("Saved:", report_path)
    print()
    print(f"Average quality score: {avg:.1f}/100")
    if top:
        print(f"Top idea: {top['title']} ({top['idea_quality_score']}/100)")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
