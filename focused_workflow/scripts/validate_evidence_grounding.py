#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_IDEA_FIELDS = [
    "evidence_paper_ids",
    "baseline_weakness_evidence",
    "unsupported_or_weak_claims",
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        rows.append(item)
    return rows


def normalize_pid(item) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return item.get("paper_id") or item.get("evidence_paper_id") or item.get("id") or ""
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate v0.5 evidence-grounded idea outputs.")
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--min-papers-per-idea", type=int, default=2)
    args = parser.parse_args()

    run_dir = args.run_dir
    ideas_path = run_dir / "focused_ideas.json"
    papers_path = run_dir / "papers.jsonl"
    cards_path = run_dir / "evidence_baseline_cards.jsonl"

    errors = []
    warnings = []

    if not ideas_path.exists():
        errors.append(f"missing {ideas_path}")
        ideas = []
    else:
        ideas = read_json(ideas_path)
        if not isinstance(ideas, list):
            errors.append("focused_ideas.json must be a JSON list")
            ideas = []

    if not papers_path.exists():
        errors.append(f"missing {papers_path}")
        paper_ids = set()
    else:
        papers = read_jsonl(papers_path)
        paper_ids = {p.get("paper_id") for p in papers if p.get("paper_id")}

    if not cards_path.exists():
        errors.append(f"missing {cards_path}")
        baseline_names = set()
    else:
        cards = read_jsonl(cards_path)
        baseline_names = {c.get("baseline_name") for c in cards if c.get("baseline_name")}

    idea_summaries = []
    all_used_papers = set()
    for idx, idea in enumerate(ideas, start=1):
        label = f"idea[{idx}]"
        if not isinstance(idea, dict):
            errors.append(f"{label} must be an object")
            continue

        for field in REQUIRED_IDEA_FIELDS:
            if field not in idea:
                errors.append(f"{label} missing required evidence field `{field}`")
            elif not isinstance(idea[field], list):
                errors.append(f"{label} field `{field}` must be a list")

        evidence_ids = [normalize_pid(x) for x in idea.get("evidence_paper_ids", [])]
        evidence_ids = [x for x in evidence_ids if x]
        unknown = sorted(set(evidence_ids) - paper_ids)
        if unknown:
            errors.append(f"{label} references unknown paper ids: {unknown}")
        if len(set(evidence_ids)) < args.min_papers_per_idea:
            errors.append(
                f"{label} uses {len(set(evidence_ids))} evidence papers, "
                f"expected at least {args.min_papers_per_idea}"
            )
        all_used_papers.update(evidence_ids)

        direct = idea.get("direct_baselines", [])
        if isinstance(direct, list):
            unmatched = [b for b in direct if isinstance(b, str) and b not in baseline_names]
            if unmatched:
                warnings.append(f"{label} direct_baselines not found in evidence cards: {unmatched}")
        else:
            errors.append(f"{label} direct_baselines must be a list")

        weakness = idea.get("baseline_weakness_evidence", [])
        if isinstance(weakness, list):
            if not weakness:
                errors.append(f"{label} has empty baseline_weakness_evidence")
            for item in weakness:
                pid = normalize_pid(item)
                if pid and pid not in paper_ids:
                    errors.append(f"{label} baseline_weakness_evidence references unknown paper id `{pid}`")

        idea_summaries.append(
            {
                "title": idea.get("title", f"idea_{idx}"),
                "evidence_papers": len(set(evidence_ids)),
                "unsupported_or_weak_claims": len(idea.get("unsupported_or_weak_claims", []))
                if isinstance(idea.get("unsupported_or_weak_claims", []), list)
                else None,
            }
        )

    summary = {
        "run_dir": str(run_dir),
        "ideas": len(ideas),
        "available_papers": len(paper_ids),
        "available_baseline_cards": len(baseline_names),
        "used_papers": len(all_used_papers),
        "schema_errors": len(errors),
        "warnings": len(warnings),
        "idea_summaries": idea_summaries,
    }

    (run_dir / "evidence_grounding_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# v0.5 Idea 证据绑定校验报告",
        "",
        f"- Run dir: `{run_dir}`",
        f"- Idea 数: {summary['ideas']}",
        f"- 可用论文证据数: {summary['available_papers']}",
        f"- 可用 baseline card 数: {summary['available_baseline_cards']}",
        f"- 被 idea 使用的论文数: {summary['used_papers']}",
        f"- 错误数: {summary['schema_errors']}",
        f"- 警告数: {summary['warnings']}",
        "",
        "## Idea 摘要",
    ]
    for item in idea_summaries:
        lines.append(
            f"- {item['title']}: evidence_papers={item['evidence_papers']}, "
            f"unsupported_or_weak_claims={item['unsupported_or_weak_claims']}"
        )
    lines.extend(["", "## Errors"])
    if errors:
        lines.extend(f"- {err}" for err in errors)
    else:
        lines.append("- 无。")
    lines.extend(["", "## Warnings"])
    if warnings:
        lines.extend(f"- {warn}" for warn in warnings)
    else:
        lines.append("- 无。")
    (run_dir / "evidence_grounding_report_CN.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Evidence grounding validation complete")
    print("Run dir:", run_dir)
    print("Ideas:", summary["ideas"])
    print("Available papers:", summary["available_papers"])
    print("Used papers:", summary["used_papers"])
    print("Errors:", summary["schema_errors"])
    print("Warnings:", summary["warnings"])

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
