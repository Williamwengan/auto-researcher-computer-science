#!/usr/bin/env python3
"""Decode and summarize a completed anonymous pairwise review run.

This script keeps the public review pack and private answer key separate until
evaluation is complete. Confidence intervals use a deterministic cluster
bootstrap over task-by-replicate groups, which avoids treating the multiple
comparisons inside one generated portfolio as fully independent replicates.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
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
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def percentile(values: list[float], q: float) -> float:
    values = sorted(values)
    if not values:
        return float("nan")
    pos = (len(values) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return values[lo]
    return values[lo] * (hi - pos) + values[hi] * (pos - lo)


def focal_credit(row: dict) -> float:
    return 0.5 if row["preference"] == "tie" else float(row["winner_method"] == "focused_full")


def cluster_bootstrap_ci(rows: list[dict], iterations: int = 10000, seed: int = 20260715) -> tuple[float, float]:
    clusters: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        clusters[(row["task"], row["replicate_id"])].append(row)
    groups = list(clusters.values())
    rng = random.Random(seed)
    estimates = []
    for _ in range(iterations):
        sample = [item for _ in groups for item in rng.choice(groups)]
        estimates.append(sum(focal_credit(x) for x in sample) / len(sample))
    return percentile(estimates, 0.025), percentile(estimates, 0.975)


def exact_two_sided_binomial(k: int, n: int, p: float = 0.5) -> float:
    if n == 0:
        return float("nan")
    observed = math.comb(n, k) * p**k * (1 - p) ** (n - k)
    return min(1.0, sum(
        math.comb(n, i) * p**i * (1 - p) ** (n - i)
        for i in range(n + 1)
        if math.comb(n, i) * p**i * (1 - p) ** (n - i) <= observed + 1e-15
    ))


def decode(results: list[dict], keys: list[dict]) -> list[dict]:
    key_by_id = {x["item_id"]: x for x in keys}
    if len(key_by_id) != len(keys):
        raise ValueError("Duplicate item_id in private answer key")
    if len({x["item_id"] for x in results}) != len(results):
        raise ValueError("Duplicate item_id in review results")
    missing = sorted(set(key_by_id) - {x["item_id"] for x in results})
    extra = sorted({x["item_id"] for x in results} - set(key_by_id))
    if missing or extra:
        raise ValueError(f"Result/key mismatch: missing={len(missing)}, extra={len(extra)}")

    decoded = []
    for result in results:
        key = key_by_id[result["item_id"]]
        review = result["review"]
        mapping = key["candidate_mapping"]
        focal_position = next(side for side in ("A", "B") if mapping[side]["method"] == "focused_full")
        other_position = "B" if focal_position == "A" else "A"
        preference = review["preference"]
        winner = "tie" if preference == "tie" else mapping[preference]["method"]
        row = {
            "item_id": result["item_id"],
            "reviewer_id": result["reviewer_id"],
            "task": key["task"],
            "replicate_id": key["replicate_id"],
            "comparison": key["comparison"],
            "private_comparison": key["private_comparison"],
            "unit": key["unit"],
            "focal_method": "focused_full",
            "comparison_method": mapping[other_position]["method"],
            "focal_position": focal_position,
            "preference": preference,
            "winner_method": winner,
            "wall_time_seconds": result.get("wall_time_seconds", 0),
            "prompt_tokens": result.get("usage", {}).get("prompt_tokens", 0),
            "completion_tokens": result.get("usage", {}).get("completion_tokens", 0),
            "total_tokens": result.get("usage", {}).get("total_tokens", 0),
            "overall_rationale": review.get("overall_rationale", ""),
        }
        for dim in DIMENSIONS:
            scores = review["scores"][dim]
            row[f"focused_full_{dim}"] = scores[focal_position]
            row[f"comparison_{dim}"] = scores[other_position]
            row[f"delta_{dim}"] = scores[focal_position] - scores[other_position]
        decoded.append(row)
    return decoded


def aggregate(rows: list[dict], group_fields: list[str]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[tuple(row[field] for field in group_fields)].append(row)
    output = []
    for group, items in sorted(groups.items(), key=lambda x: tuple(str(v) for v in x[0])):
        wins = sum(x["winner_method"] == "focused_full" for x in items)
        losses = sum(x["winner_method"] not in {"focused_full", "tie"} for x in items)
        ties = sum(x["winner_method"] == "tie" for x in items)
        lo, hi = cluster_bootstrap_ci(items)
        row = {field: value for field, value in zip(group_fields, group)}
        row.update({
            "n": len(items), "focused_full_wins": wins, "losses": losses, "ties": ties,
            "win_rate_tie_half": (wins + 0.5 * ties) / len(items),
            "cluster_bootstrap_ci_low": lo, "cluster_bootstrap_ci_high": hi,
        })
        for dim in DIMENSIONS:
            row[f"mean_delta_{dim}"] = sum(x[f"delta_{dim}"] for x in items) / len(items)
        output.append(row)
    return output


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", required=True)
    parser.add_argument("--answer-key", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--expected-items", type=int, default=120)
    args = parser.parse_args()
    results_path, key_path = ROOT / args.results, ROOT / args.answer_key
    out_dir = ROOT / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    results, keys = read_jsonl(results_path), read_jsonl(key_path)
    decoded = decode(results, keys)
    if len(decoded) != args.expected_items:
        raise ValueError(f"Expected complete {args.expected_items}-item review, found {len(decoded)}")

    overall = aggregate(decoded, [])
    by_comparison = aggregate(decoded, ["private_comparison"])
    by_task = aggregate(decoded, ["task"])
    by_task_comparison = aggregate(decoded, ["task", "private_comparison"])
    by_replicate = aggregate(decoded, ["replicate_id"])
    write_jsonl(out_dir / "decoded_review_results.jsonl", decoded)
    write_csv(out_dir / "decoded_review_results.csv", decoded)
    write_csv(out_dir / "summary_overall.csv", overall)
    write_csv(out_dir / "summary_by_comparison.csv", by_comparison)
    write_csv(out_dir / "summary_by_task.csv", by_task)
    write_csv(out_dir / "summary_by_task_comparison.csv", by_task_comparison)
    write_csv(out_dir / "summary_by_replicate.csv", by_replicate)

    pref = Counter(x["preference"] for x in decoded)
    focal_pos = Counter(x["focal_position"] for x in decoded)
    focal_by_pos = {side: [x for x in decoded if x["focal_position"] == side] for side in ("A", "B")}
    a_non_tie = pref["A"] + pref["B"]
    p_position = exact_two_sided_binomial(pref["A"], a_non_tie) if a_non_tie else float("nan")
    total_tokens = sum(x["total_tokens"] for x in decoded)
    o = overall[0]
    reviewer_label = decoded[0]["reviewer_id"]
    model_label = results[0].get("model", "unknown")
    lines = [
        f"# {model_label} Balanced Blind Review Results",
        "",
        "## Integrity and position audit",
        "",
        f"- Reviewer ID: {reviewer_label}",
        f"- Model: {model_label}",
        f"- Completed unique items: {len(decoded)}/{args.expected_items}",
        f"- focused_full position: A={focal_pos['A']}, B={focal_pos['B']}",
        f"- Raw reviewer preference: A={pref['A']}, B={pref['B']}, tie={pref['tie']}",
        f"- Exact two-sided binomial test of raw A/B preference: p={p_position:.4f}",
        f"- focused_full win rate when placed A: {sum(focal_credit(x) for x in focal_by_pos['A'])/len(focal_by_pos['A']):.3f}",
        f"- focused_full win rate when placed B: {sum(focal_credit(x) for x in focal_by_pos['B'])/len(focal_by_pos['B']):.3f}",
        f"- Reviewer token use: {total_tokens:,}",
        "",
        "## Overall result",
        "",
        f"focused_full: {o['focused_full_wins']} wins, {o['losses']} losses, {o['ties']} ties; "
        f"tie-half win rate={o['win_rate_tie_half']:.3f}, 95% task×replicate cluster bootstrap CI "
        f"[{o['cluster_bootstrap_ci_low']:.3f}, {o['cluster_bootstrap_ci_high']:.3f}].",
        "",
        "| dimension | mean score delta (focused_full - comparator) |",
        "| --- | ---: |",
    ]
    for dim in DIMENSIONS:
        lines.append(f"| {dim} | {o[f'mean_delta_{dim}']:+.3f} |")

    def add_table(title: str, rows: list[dict], labels: list[str]) -> None:
        lines.extend(["", f"## {title}", "", "| group | N | W/L/T | win rate | 95% cluster CI | overall delta |", "| --- | ---: | ---: | ---: | ---: | ---: |"])
        for row in rows:
            label = " / ".join(str(row[x]) for x in labels)
            lines.append(
                f"| {label} | {row['n']} | {row['focused_full_wins']}/{row['losses']}/{row['ties']} | "
                f"{row['win_rate_tie_half']:.3f} | [{row['cluster_bootstrap_ci_low']:.3f}, {row['cluster_bootstrap_ci_high']:.3f}] | "
                f"{row['mean_delta_overall']:+.3f} |"
            )

    add_table("By comparison", by_comparison, ["private_comparison"])
    add_table("By task", by_task, ["task"])
    add_table("By replicate", by_replicate, ["replicate_id"])
    lines.extend([
        "", "## Interpretation boundary", "",
        "This is one complete balanced blind-review run from one LLM reviewer. It is a valid descriptive result for this reviewer, but it is not yet multi-reviewer evidence and must not be presented as human evaluation. The original unbalanced v1 review is excluded from all statistics.",
    ])
    (out_dir / "FULL_REVIEW_RESULTS_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_dir / 'FULL_REVIEW_RESULTS_SUMMARY.md'}")
    print(f"Wrote decoded and grouped CSV/JSONL tables to {out_dir}")
    print(f"Summary: W/L/T={o['focused_full_wins']}/{o['losses']}/{o['ties']}, win_rate={o['win_rate_tie_half']:.3f}")


if __name__ == "__main__":
    main()
