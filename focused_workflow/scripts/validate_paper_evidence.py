#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


VALID_STRENGTHS = {"weak", "medium", "strong"}
VALID_RELEVANCE = {"weak", "medium", "strong", ""}


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        raise FileNotFoundError(path)
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        if not isinstance(item, dict):
            raise ValueError(f"{path}:{line_no}: expected JSON object")
        rows.append(item)
    return rows


def load_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_schema(rows: list[dict], schema: dict, label: str) -> list[str]:
    errors = []
    required = schema.get("required", [])
    list_fields = set(schema.get("list_fields", []))
    string_fields = set(schema.get("string_fields", []))
    for idx, row in enumerate(rows, start=1):
        for field in required:
            if field not in row:
                errors.append(f"{label}[{idx}] missing required field `{field}`")
        for field in list_fields:
            if field in row and not isinstance(row[field], list):
                errors.append(f"{label}[{idx}] field `{field}` must be a list")
        for field in string_fields:
            if field in row and not isinstance(row[field], str):
                errors.append(f"{label}[{idx}] field `{field}` must be a string")
    return errors


def resolve_evidence_dir(path: Path) -> Path:
    if path.name == "paper_evidence":
        return path
    if (path / "paper_evidence").is_dir():
        return path / "paper_evidence"
    return path


def validate(evidence_dir: Path, schema_dir: Path) -> tuple[dict, list[str], list[str]]:
    paper_schema = load_schema(schema_dir / "paper_evidence.schema.json")
    card_schema = load_schema(schema_dir / "evidence_baseline_card.schema.json")

    papers = read_jsonl(evidence_dir / "papers.jsonl")
    cards = read_jsonl(evidence_dir / "evidence_baseline_cards.jsonl")
    queries = read_jsonl(evidence_dir / "retrieval_queries.jsonl")
    errors_file = evidence_dir / "retrieval_errors.jsonl"
    retrieval_errors = read_jsonl(errors_file) if errors_file.exists() else []

    errors = []
    warnings = []
    errors.extend(check_schema(papers, paper_schema, "papers"))
    errors.extend(check_schema(cards, card_schema, "cards"))

    paper_ids = {p.get("paper_id") for p in papers}
    paper_source_count = Counter(p.get("source", "") for p in papers)
    relevance_count = Counter(p.get("task_relevance", "") for p in papers)
    strength_count = Counter(c.get("evidence_strength", "") for c in cards)

    papers_with_url = sum(1 for p in papers if p.get("url"))
    papers_with_abstract = sum(1 for p in papers if p.get("abstract"))
    papers_with_baseline = sum(1 for p in papers if p.get("baseline_tags"))

    for idx, paper in enumerate(papers, start=1):
        if paper.get("task_relevance") not in VALID_RELEVANCE:
            errors.append(f"papers[{idx}] invalid task_relevance `{paper.get('task_relevance')}`")
        if not paper.get("title"):
            warnings.append(f"papers[{idx}] has empty title")
        if not paper.get("url"):
            warnings.append(f"papers[{idx}] has no URL")
        if not paper.get("abstract"):
            warnings.append(f"papers[{idx}] has no abstract")
        if not paper.get("baseline_tags"):
            warnings.append(f"papers[{idx}] has no baseline_tags")

    weak_cards = []
    unsupported_cards = []
    cards_with_evidence = 0
    cards_with_strong_evidence = 0
    for idx, card in enumerate(cards, start=1):
        strength = card.get("evidence_strength", "")
        if strength not in VALID_STRENGTHS:
            errors.append(f"cards[{idx}] invalid evidence_strength `{strength}`")
        evidence_papers = card.get("evidence_papers") or []
        if evidence_papers:
            cards_with_evidence += 1
        if strength == "strong":
            cards_with_strong_evidence += 1
        if strength == "weak":
            weak_cards.append(card.get("baseline_name", f"card_{idx}"))
        if card.get("unsupported_claims"):
            unsupported_cards.append(card.get("baseline_name", f"card_{idx}"))
        for paper in evidence_papers:
            pid = paper.get("paper_id")
            if pid and pid not in paper_ids:
                errors.append(f"cards[{idx}] references missing paper_id `{pid}`")
        if strength in {"medium", "strong"} and not evidence_papers:
            errors.append(f"cards[{idx}] has {strength} evidence_strength but no evidence_papers")

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "evidence_dir": str(evidence_dir),
        "papers": len(papers),
        "queries": len(queries),
        "retrieval_errors": len(retrieval_errors),
        "baseline_cards": len(cards),
        "cards_with_evidence": cards_with_evidence,
        "cards_with_strong_evidence": cards_with_strong_evidence,
        "weak_cards": len(weak_cards),
        "unsupported_cards": len(unsupported_cards),
        "papers_with_url": papers_with_url,
        "papers_with_abstract": papers_with_abstract,
        "papers_with_baseline_tags": papers_with_baseline,
        "paper_source_count": dict(paper_source_count),
        "task_relevance_count": dict(relevance_count),
        "evidence_strength_count": dict(strength_count),
        "weak_card_names": weak_cards,
        "unsupported_card_names": unsupported_cards,
        "schema_errors": len(errors),
        "warnings": len(warnings),
    }
    return summary, errors, warnings


def write_report(path: Path, summary: dict, errors: list[str], warnings: list[str]) -> None:
    lines = [
        "# v0.5 论文证据绑定校验报告",
        "",
        f"- 证据目录: `{summary['evidence_dir']}`",
        f"- 生成时间: {summary['generated_at']}",
        f"- 检索 query 数: {summary['queries']}",
        f"- 论文记录数: {summary['papers']}",
        f"- baseline evidence card 数: {summary['baseline_cards']}",
        f"- 已绑定论文的 baseline card 数: {summary['cards_with_evidence']}",
        f"- strong evidence card 数: {summary['cards_with_strong_evidence']}",
        f"- weak evidence card 数: {summary['weak_cards']}",
        f"- unsupported claim card 数: {summary['unsupported_cards']}",
        f"- 有 URL 的论文数: {summary['papers_with_url']}",
        f"- 有摘要的论文数: {summary['papers_with_abstract']}",
        f"- 检索错误数: {summary['retrieval_errors']}",
        f"- schema 错误数: {summary['schema_errors']}",
        f"- warning 数: {summary['warnings']}",
        "",
        "## 证据强度分布",
        "",
    ]
    for key, value in summary["evidence_strength_count"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## 论文来源分布", ""])
    if summary["paper_source_count"]:
        for key, value in summary["paper_source_count"].items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- 暂无论文记录。")
    lines.extend(["", "## weak evidence baselines", ""])
    if summary["weak_card_names"]:
        for name in summary["weak_card_names"]:
            lines.append(f"- {name}")
    else:
        lines.append("- 无。")
    lines.extend(["", "## Schema Errors", ""])
    if errors:
        for err in errors[:80]:
            lines.append(f"- {err}")
    else:
        lines.append("- 无。")
    lines.extend(["", "## Warnings", ""])
    if warnings:
        for warn in warnings[:80]:
            lines.append(f"- {warn}")
        if len(warnings) > 80:
            lines.append(f"- ... 还有 {len(warnings) - 80} 条 warning")
    else:
        lines.append("- 无。")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate v0.5 paper evidence outputs.")
    parser.add_argument("evidence_dir", type=Path, help="Run directory or paper_evidence directory.")
    parser.add_argument("--schema-dir", type=Path, default=Path("focused_workflow/schemas"))
    parser.add_argument("--strict", action="store_true", help="Return non-zero if weak-only or paperless evidence is detected.")
    args = parser.parse_args()

    evidence_dir = resolve_evidence_dir(args.evidence_dir)
    summary, errors, warnings = validate(evidence_dir, args.schema_dir)

    (evidence_dir / "evidence_quality_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_report(evidence_dir / "evidence_quality_report_CN.md", summary, errors, warnings)

    print("Paper evidence validation complete")
    print("Evidence dir:", evidence_dir)
    print("Papers:", summary["papers"])
    print("Baseline cards:", summary["baseline_cards"])
    print("Cards with evidence:", summary["cards_with_evidence"])
    print("Weak cards:", summary["weak_cards"])
    print("Schema errors:", summary["schema_errors"])
    print("Warnings:", summary["warnings"])

    if errors:
        sys.exit(1)
    if args.strict and (summary["papers"] == 0 or summary["cards_with_evidence"] == 0 or summary["weak_cards"] > 0):
        sys.exit(2)


if __name__ == "__main__":
    main()
