#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


DIMENSIONS = [
    "novelty",
    "feasibility",
    "expected_effectiveness",
    "experimental_rigor",
    "baseline_grounding",
    "mechanism_specificity",
    "implementation_readiness",
    "overall",
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def safe_float(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def load_reviews(paths: list[Path]) -> list[tuple[str, list[dict]]]:
    reviews = []
    for path in paths:
        data = load_json(path)
        if not isinstance(data, list):
            raise TypeError(f"{path} must contain a JSON list")
        reviews.append((path.stem, data))
    return reviews


def summarize(answer_key: dict, reviews: list[tuple[str, list[dict]]]) -> dict:
    key_by_pair = {item["pair_id"]: item for item in answer_key["pairs"]}
    pair_votes = defaultdict(list)
    dim_deltas = defaultdict(list)
    reviewer_rows = []

    for reviewer, items in reviews:
        after_wins = 0
        before_wins = 0
        ties = 0
        invalid = 0
        completed = 0
        for item in items:
            pair_id = item.get("pair_id")
            key = key_by_pair.get(pair_id)
            if not key:
                invalid += 1
                continue
            pref = item.get("preferred")
            if isinstance(pref, str):
                pref = pref.strip().upper()
            if pref not in {"A", "B", "TIE"}:
                if isinstance(pref, str) and pref.lower() == "tie":
                    pref = "TIE"
                else:
                    invalid += 1
                    continue
            completed += 1
            if pref == "TIE":
                outcome = "tie"
                ties += 1
            else:
                label = key.get(pref)
                outcome = label
                if label == "after":
                    after_wins += 1
                elif label == "before":
                    before_wins += 1
            pair_votes[pair_id].append(outcome)

            scores = item.get("scores", {}) or {}
            for dim in DIMENSIONS:
                a = safe_float((scores.get("A", {}) or {}).get(dim))
                b = safe_float((scores.get("B", {}) or {}).get(dim))
                if a is None or b is None:
                    continue
                after_score = a if key.get("A") == "after" else b
                before_score = a if key.get("A") == "before" else b
                dim_deltas[dim].append(after_score - before_score)

        total = after_wins + before_wins + ties
        reviewer_rows.append(
            {
                "reviewer": reviewer,
                "completed": completed,
                "invalid": invalid,
                "after_wins": after_wins,
                "before_wins": before_wins,
                "ties": ties,
                "after_win_rate": round((after_wins + 0.5 * ties) / total, 3) if total else None,
            }
        )

    pair_rows = []
    agreements = []
    for pair in answer_key["pairs"]:
        votes = pair_votes.get(pair["pair_id"], [])
        counts = Counter(votes)
        total = sum(counts.values())
        majority = counts.most_common(1)[0][0] if total else None
        agreement = counts[majority] / total if total and majority else None
        if agreement is not None:
            agreements.append(agreement)
        pair_rows.append(
            {
                "pair_id": pair["pair_id"],
                "idea_title": pair["idea_title"],
                "votes": dict(counts),
                "majority": majority,
                "agreement": round(agreement, 3) if agreement is not None else None,
            }
        )

    dimension_summary = {}
    for dim, values in dim_deltas.items():
        if not values:
            continue
        dimension_summary[dim] = {
            "mean_after_minus_before": round(sum(values) / len(values), 3),
            "n": len(values),
            "positive_count": sum(1 for v in values if v > 0),
            "negative_count": sum(1 for v in values if v < 0),
            "tie_count": sum(1 for v in values if v == 0),
        }

    total_after = sum(row["after_wins"] for row in reviewer_rows)
    total_before = sum(row["before_wins"] for row in reviewer_rows)
    total_ties = sum(row["ties"] for row in reviewer_rows)
    total_votes = total_after + total_before + total_ties

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "domain": answer_key.get("domain"),
        "reviewers": len(reviewer_rows),
        "total_votes": total_votes,
        "after_wins": total_after,
        "before_wins": total_before,
        "ties": total_ties,
        "after_win_rate_with_ties_half": round((total_after + 0.5 * total_ties) / total_votes, 3)
        if total_votes
        else None,
        "mean_pair_agreement": round(sum(agreements) / len(agreements), 3) if agreements else None,
        "reviewer_rows": reviewer_rows,
        "pair_rows": pair_rows,
        "dimension_summary": dimension_summary,
    }


def write_report(path: Path, summary: dict) -> None:
    lines = [
        "# v0.6 匿名 A/B 盲评统计报告",
        "",
        f"- Domain: {summary.get('domain')}",
        f"- Reviewers: {summary.get('reviewers')}",
        f"- Total votes: {summary.get('total_votes')}",
        f"- After wins: {summary.get('after_wins')}",
        f"- Before wins: {summary.get('before_wins')}",
        f"- Ties: {summary.get('ties')}",
        f"- After win rate with ties half: {summary.get('after_win_rate_with_ties_half')}",
        f"- Mean pair agreement: {summary.get('mean_pair_agreement')}",
        "",
        "## Reviewer Summary",
        "",
        "| Reviewer | Completed | Invalid | After Wins | Before Wins | Ties | After Win Rate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["reviewer_rows"]:
        lines.append(
            f"| {row['reviewer']} | {row['completed']} | {row['invalid']} | "
            f"{row['after_wins']} | {row['before_wins']} | {row['ties']} | {row['after_win_rate']} |"
        )
    lines.extend(
        [
            "",
            "## Pair Summary",
            "",
            "| Pair | Idea | Majority | Agreement | Votes |",
            "|---|---|---|---:|---|",
        ]
    )
    for row in summary["pair_rows"]:
        lines.append(
            f"| {row['pair_id']} | {row['idea_title']} | {row['majority']} | "
            f"{row['agreement']} | {json.dumps(row['votes'], ensure_ascii=False)} |"
        )
    lines.extend(
        [
            "",
            "## Dimension Delta",
            "",
            "`mean_after_minus_before > 0` means after-repair is rated higher.",
            "",
            "| Dimension | Mean After-Before | N | Positive | Negative | Tie |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for dim, row in summary["dimension_summary"].items():
        lines.append(
            f"| {dim} | {row['mean_after_minus_before']} | {row['n']} | "
            f"{row['positive_count']} | {row['negative_count']} | {row['tie_count']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize blinded A/B review results.")
    parser.add_argument("--answer-key", required=True, type=Path)
    parser.add_argument("--reviews", required=True, nargs="+", type=Path)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    answer_key = load_json(args.answer_key)
    reviews = load_reviews(args.reviews)
    summary = summarize(answer_key, reviews)
    output_dir = args.output_dir or args.answer_key.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "blind_ab_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_report(output_dir / "blind_ab_summary_CN.md", summary)
    print("Blind A/B summary complete")
    print("Output:", output_dir / "blind_ab_summary_CN.md")


if __name__ == "__main__":
    main()
