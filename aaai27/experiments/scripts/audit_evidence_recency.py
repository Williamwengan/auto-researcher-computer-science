#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path


DEFAULT_EVIDENCE_PATHS = {
    "physical_property": Path(
        "outputs/v05_evidence_grounded_ideation_01_physical_property_prediction_20260712_102328/papers.jsonl"
    ),
    "indoor3d_seeded": Path(
        "outputs/v05_evidence_grounded_ideation_03_indoor_scene_generation_seeded/papers.jsonl"
    ),
    "iad_agent": Path(
        "outputs/v05_evidence_grounded_ideation_05_iad_agent_workflow_20260712_101952/papers.jsonl"
    ),
}


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def summarize(name: str, path: Path, recent_year: int, stale_year: int) -> dict:
    rows = read_jsonl(path) if path.exists() else []
    years = [row.get("year") for row in rows if isinstance(row.get("year"), int)]
    by_year = Counter(years)
    recent = sum(1 for year in years if year >= recent_year)
    stale = sum(1 for year in years if year < stale_year)
    total = len(rows)
    year_total = len(years)
    recent_ratio = recent / year_total if year_total else 0.0
    stale_ratio = stale / year_total if year_total else 0.0
    return {
        "task": name,
        "path": str(path),
        "papers": total,
        "papers_with_year": year_total,
        "min_year": min(years) if years else None,
        "max_year": max(years) if years else None,
        "recent_year_threshold": recent_year,
        "recent_papers": recent,
        "recent_ratio": round(recent_ratio, 4),
        "stale_year_threshold": stale_year,
        "stale_papers": stale,
        "stale_ratio": round(stale_ratio, 4),
        "by_year": {str(year): by_year[year] for year in sorted(by_year)},
    }


def risk_label(summary: dict, min_recent_ratio: float, min_recent_count: int) -> str:
    if summary["papers"] == 0:
        return "missing"
    if summary["recent_papers"] < min_recent_count or summary["recent_ratio"] < min_recent_ratio:
        return "needs_refresh"
    return "ok"


def write_markdown(path: Path, summaries: list[dict], args: argparse.Namespace) -> None:
    lines = [
        "# Evidence Recency Audit",
        "",
        f"Generated at: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "This audit checks whether the evidence bank is recent enough for an AAAI-style paper. "
        "Classic papers should remain for historical baselines, but each active task should also "
        "contain enough recent papers to ground claims about current methods.",
        "",
        "## Summary",
        "",
        "| task | papers | year range | recent papers | recent ratio | stale papers | risk |",
        "| --- | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for item in summaries:
        risk = risk_label(item, args.min_recent_ratio, args.min_recent_count)
        year_range = "NA" if item["min_year"] is None else f"{item['min_year']}-{item['max_year']}"
        lines.append(
            "| {task} | {papers} | {year_range} | {recent_papers} | {recent_ratio:.1%} | {stale_papers} | {risk} |".format(
                task=item["task"],
                papers=item["papers"],
                year_range=year_range,
                recent_papers=item["recent_papers"],
                recent_ratio=item["recent_ratio"],
                stale_papers=item["stale_papers"],
                risk=risk,
            )
        )

    lines.extend(
        [
            "",
            "## Recommended Action",
            "",
            "- Keep classic foundational papers, but do not let them dominate the evidence pool.",
            "- Refresh any `needs_refresh` task with recency-aware retrieval.",
            "- For the refreshed pool, report both `classic/foundation` and `recent/current` evidence strata.",
            "- Re-run reference claim verification after changing any evidence cards.",
            "",
            "Suggested refresh command template:",
            "",
            "```bash",
            "python focused_workflow/scripts/retrieve_paper_evidence.py \\",
            "  --task-spec focused_workflow/tasks/benchmark_cv/03_indoor_scene_generation.yaml \\",
            "  --output-dir outputs/v05_paper_evidence_03_indoor_scene_generation_recent_refresh_$(date +%Y%m%d_%H%M%S) \\",
            "  --sources openalex,arxiv \\",
            "  --per-query 5 \\",
            "  --max-baselines 12 \\",
            "  --top-k-per-baseline 4 \\",
            "  --include-recency-queries \\",
            "  --min-year 2023 \\",
            "  --recency-weight 2.0 \\",
            "  --recent-bonus-year 2024 \\",
            "  --recent-bonus 1.5",
            "```",
            "",
        ]
    )

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit evidence bank recency for AAAI experiments.")
    parser.add_argument("--output-dir", type=Path, default=Path("aaai27/experiments/results/derived/evidence_recency_audit_v1"))
    parser.add_argument("--recent-year", type=int, default=2024)
    parser.add_argument("--stale-year", type=int, default=2021)
    parser.add_argument("--min-recent-ratio", type=float, default=0.35)
    parser.add_argument("--min-recent-count", type=int, default=6)
    parser.add_argument(
        "--evidence",
        action="append",
        default=[],
        help="Optional task=path override. Can be passed multiple times.",
    )
    args = parser.parse_args()

    evidence_paths = dict(DEFAULT_EVIDENCE_PATHS)
    for spec in args.evidence:
        if "=" not in spec:
            raise ValueError(f"--evidence must be task=path, got: {spec}")
        name, raw_path = spec.split("=", 1)
        evidence_paths[name] = Path(raw_path)

    summaries = [
        summarize(name, path, args.recent_year, args.stale_year)
        for name, path in evidence_paths.items()
    ]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "evidence_recency_audit.json"
    md_path = args.output_dir / "EVIDENCE_RECENCY_AUDIT.md"
    json_path.write_text(json.dumps(summaries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(md_path, summaries, args)

    print(f"Wrote {md_path}")
    print(f"Wrote {json_path}")
    for item in summaries:
        risk = risk_label(item, args.min_recent_ratio, args.min_recent_count)
        print(
            f"{item['task']}: papers={item['papers']} recent>={args.recent_year}="
            f"{item['recent_papers']} ratio={item['recent_ratio']:.1%} risk={risk}"
        )


if __name__ == "__main__":
    main()
