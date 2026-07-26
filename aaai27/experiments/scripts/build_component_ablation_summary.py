#!/usr/bin/env python3
"""Build the combined component-ablation table from decoded reviews."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from combine_multi_reviewer_results import bootstrap, category, credit


ROOT = Path(__file__).resolve().parents[3]
DIMENSIONS = [
    "novelty", "excitement", "feasibility", "expected_effectiveness", "overall",
    "baseline_grounding", "experimental_rigor", "mechanism_specificity", "implementation_readiness",
]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.open(encoding="utf-8") if x.strip()]


def aggregate(rows: list[dict], fields: list[str]) -> list[dict]:
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[x] for x in fields)].append(row)
    output = []
    for key, items in sorted(groups.items(), key=lambda x: tuple(str(v) for v in x[0])):
        counts = Counter(category(x) for x in items)
        lo, hi = bootstrap(items)
        result = {field: value for field, value in zip(fields, key)}
        result.update({
            "n": len(items), "wins": counts["focused_full"], "losses": counts["comparator"],
            "ties": counts["tie"], "win_rate_tie_half": sum(map(credit, items)) / len(items),
            "cluster_ci_low": lo, "cluster_ci_high": hi,
        })
        for dim in DIMENSIONS:
            result[f"mean_delta_{dim}"] = sum(x[f"delta_{dim}"] for x in items) / len(items)
        output.append(result)
    return output


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--main-decoded", action="append", required=True)
    parser.add_argument("--no-evidence-decoded", action="append", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    if len(args.main_decoded) != len(args.no_evidence_decoded):
        raise ValueError("Reviewer counts must match")
    rows = []
    mapping = {
        "repair_effect_full_vs_no_repair_idea": "remove_repair",
        "targeted_vs_generic_refine_idea": "remove_consistency_aware_targeting",
    }
    for path in args.main_decoded:
        for row in read_jsonl(ROOT / path):
            component = mapping.get(row["private_comparison"])
            if component:
                row = dict(row); row["ablation"] = component; rows.append(row)
    for path in args.no_evidence_decoded:
        for row in read_jsonl(ROOT / path):
            row = dict(row); row["ablation"] = "remove_paper_evidence"; rows.append(row)
    summary = aggregate(rows, ["ablation"])
    by_reviewer = aggregate(rows, ["ablation", "reviewer_id"])
    by_task = aggregate(rows, ["ablation", "task"])
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "component_ablation_summary.csv", summary)
    write_csv(out / "component_ablation_by_reviewer.csv", by_reviewer)
    write_csv(out / "component_ablation_by_task.csv", by_task)
    lines = [
        "# Component Ablation Summary", "",
        "The table reports preference for the complete focused workflow over the matched component-removed condition. Ties receive half credit.", "",
        "| Removed component | N judgments | W/L/T | Full workflow win rate | 95% task×replicate cluster CI | Δ overall | Δ baseline grounding | Δ experimental rigor | Δ mechanism specificity |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for x in summary:
        lines.append(
            f"| {x['ablation']} | {x['n']} | {x['wins']}/{x['losses']}/{x['ties']} | {x['win_rate_tie_half']:.3f} | "
            f"[{x['cluster_ci_low']:.3f}, {x['cluster_ci_high']:.3f}] | {x['mean_delta_overall']:+.3f} | "
            f"{x['mean_delta_baseline_grounding']:+.3f} | {x['mean_delta_experimental_rigor']:+.3f} | "
            f"{x['mean_delta_mechanism_specificity']:+.3f} |"
        )
    lines.extend([
        "", "## Interpretation", "",
        "- `remove_repair` uses the exactly paired focused-no-repair initial ideas.",
        "- `remove_consistency_aware_targeting` uses the compute-matched generic refinement branch from the same initial ideas.",
        "- `remove_paper_evidence` uses independently generated, length-matched three-idea portfolios with no paper records or paper IDs.",
        "- Claim verification is a post-generation filter and is evaluated separately through claim-error detection, not preference scores.",
        "- These are multi-LLM judgments, not human evaluations.",
    ])
    (out / "COMPONENT_ABLATION_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out / 'COMPONENT_ABLATION_SUMMARY.md'}")
    for x in summary:
        print(f"{x['ablation']}: N={x['n']} win_rate={x['win_rate_tie_half']:.3f}")


if __name__ == "__main__":
    main()
