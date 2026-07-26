#!/usr/bin/env python3
"""Combine decoded balanced blind-review results from multiple reviewers."""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DIMENSIONS = [
    "novelty", "excitement", "feasibility", "expected_effectiveness", "overall",
    "baseline_grounding", "experimental_rigor", "mechanism_specificity",
    "implementation_readiness",
]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.open(encoding="utf-8") if x.strip()]


def category(row: dict) -> str:
    if row["winner_method"] == "tie":
        return "tie"
    return "focused_full" if row["winner_method"] == "focused_full" else "comparator"


def credit(row: dict) -> float:
    return {"focused_full": 1.0, "comparator": 0.0, "tie": 0.5}[category(row)]


def percentile(xs: list[float], q: float) -> float:
    xs = sorted(xs)
    pos = (len(xs) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] * (hi - pos) + xs[hi] * (pos - lo)


def bootstrap(rows: list[dict], iterations: int = 10000) -> tuple[float, float]:
    clusters = defaultdict(list)
    for row in rows:
        clusters[(row["task"], row["replicate_id"])].append(row)
    groups = list(clusters.values())
    rng = random.Random(20260715)
    stats = []
    for _ in range(iterations):
        sample = [x for _ in groups for x in rng.choice(groups)]
        stats.append(sum(map(credit, sample)) / len(sample))
    return percentile(stats, .025), percentile(stats, .975)


def summarize(rows: list[dict], field: str | None = None) -> list[dict]:
    groups = defaultdict(list)
    for row in rows:
        groups[row[field] if field else "all"].append(row)
    output = []
    for name, items in sorted(groups.items(), key=lambda x: str(x[0])):
        counts = Counter(category(x) for x in items)
        lo, hi = bootstrap(items)
        result = {
            "group": name, "n": len(items), "wins": counts["focused_full"],
            "losses": counts["comparator"], "ties": counts["tie"],
            "win_rate_tie_half": sum(map(credit, items)) / len(items),
            "cluster_ci_low": lo, "cluster_ci_high": hi,
        }
        for dim in DIMENSIONS:
            result[f"mean_delta_{dim}"] = sum(x[f"delta_{dim}"] for x in items) / len(items)
        output.append(result)
    return output


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decoded", action="append", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--expected-items", type=int, default=120)
    args = parser.parse_args()
    reviewer_rows = [read_jsonl(ROOT / p) for p in args.decoded]
    item_sets = [{x["item_id"] for x in rows} for rows in reviewer_rows]
    if any(len(rows) != args.expected_items for rows in reviewer_rows) or any(s != item_sets[0] for s in item_sets[1:]):
        raise ValueError(f"Each reviewer must contain the same complete {args.expected_items}-item set")
    all_rows = [x for rows in reviewer_rows for x in rows]
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    overall, by_reviewer = summarize(all_rows), summarize(all_rows, "reviewer_id")
    by_task, by_comparison = summarize(all_rows, "task"), summarize(all_rows, "private_comparison")
    write_csv(out / "combined_overall.csv", overall)
    write_csv(out / "combined_by_reviewer.csv", by_reviewer)
    write_csv(out / "combined_by_task.csv", by_task)
    write_csv(out / "combined_by_comparison.csv", by_comparison)

    maps = [{x["item_id"]: category(x) for x in rows} for rows in reviewer_rows]
    pair_rows = []
    for i in range(len(maps)):
        for j in range(i + 1, len(maps)):
            ids = sorted(item_sets[0])
            agree = sum(maps[i][k] == maps[j][k] for k in ids) / len(ids)
            labels = ("focused_full", "comparator", "tie")
            p1, p2 = Counter(maps[i].values()), Counter(maps[j].values())
            expected = sum((p1[x] / len(ids)) * (p2[x] / len(ids)) for x in labels)
            kappa = (agree - expected) / (1 - expected) if expected < 1 else 1.0
            pair_rows.append({"reviewer_1": reviewer_rows[i][0]["reviewer_id"], "reviewer_2": reviewer_rows[j][0]["reviewer_id"], "agreement": agree, "cohen_kappa": kappa})
    write_csv(out / "reviewer_agreement.csv", pair_rows)

    o = overall[0]
    lines = [
        "# Multi-Reviewer Balanced Blind Evaluation",
        "", f"Reviewers: {len(reviewer_rows)}", f"Judgments: {len(all_rows)}", "",
        "## Pooled result", "",
        f"focused_full: {o['wins']} wins, {o['losses']} losses, {o['ties']} ties; "
        f"tie-half win rate={o['win_rate_tie_half']:.3f}; 95% task×replicate cluster bootstrap CI "
        f"[{o['cluster_ci_low']:.3f}, {o['cluster_ci_high']:.3f}].",
        "", "## By reviewer", "",
        "| reviewer | N | W/L/T | win rate | overall delta |", "| --- | ---: | ---: | ---: | ---: |",
    ]
    for x in by_reviewer:
        lines.append(f"| {x['group']} | {x['n']} | {x['wins']}/{x['losses']}/{x['ties']} | {x['win_rate_tie_half']:.3f} | {x['mean_delta_overall']:+.3f} |")
    lines.extend(["", "## Pairwise reviewer agreement", "", "| reviewer pair | agreement | Cohen's kappa |", "| --- | ---: | ---: |"])
    for x in pair_rows:
        lines.append(f"| {x['reviewer_1']} vs {x['reviewer_2']} | {x['agreement']:.3f} | {x['cohen_kappa']:.3f} |")
    lines.extend(["", "## Mean score deltas", "", "| dimension | focused_full - comparator |", "| --- | ---: |"])
    for dim in DIMENSIONS:
        lines.append(f"| {dim} | {o[f'mean_delta_{dim}']:+.3f} |")
    lines.extend(["", "## Boundary", "", "These are multi-LLM judgments, not human evaluations. The balanced pack controls aggregate A/B exposure, while reviewer-specific position effects must still be reported."])
    (out / "MULTI_REVIEWER_RESULTS_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out / 'MULTI_REVIEWER_RESULTS_SUMMARY.md'}")
    print(f"Summary: W/L/T={o['wins']}/{o['losses']}/{o['ties']}, win_rate={o['win_rate_tie_half']:.3f}")


if __name__ == "__main__":
    main()
