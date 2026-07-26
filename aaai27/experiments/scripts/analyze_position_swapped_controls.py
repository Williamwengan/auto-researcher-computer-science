#!/usr/bin/env python3
"""Analyze paired original and A/B-swapped blind-review judgments."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.open(encoding="utf-8") if x.strip()]


def decode(result: dict, key: dict) -> dict:
    mapping = key["candidate_mapping"]
    focal_pos = next(s for s in ("A", "B") if mapping[s]["method"] == "focused_full")
    pref = result["review"]["preference"]
    if pref == "tie":
        winner = "tie"
    else:
        winner = "focused_full" if mapping[pref]["method"] == "focused_full" else "comparator"
    scores = result["review"]["scores"]["overall"]
    other_pos = "B" if focal_pos == "A" else "A"
    return {
        "preference": pref,
        "winner": winner,
        "focal_position": focal_pos,
        "overall_delta": scores[focal_pos] - scores[other_pos],
    }


def credit(winner: str) -> float:
    return {"focused_full": 1.0, "comparator": 0.0, "tie": 0.5}[winner]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--main-answer-key", required=True)
    parser.add_argument("--swap-answer-key", required=True)
    parser.add_argument("--reviewer", action="append", nargs=3, metavar=("NAME", "MAIN_RESULTS", "SWAP_RESULTS"), required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    main_keys = {x["item_id"]: x for x in read_jsonl(ROOT / args.main_answer_key)}
    swap_keys = {x["item_id"]: x for x in read_jsonl(ROOT / args.swap_answer_key)}
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    pair_rows, summaries = [], []

    for name, main_path, swap_path in args.reviewer:
        main_results = {x["item_id"]: x for x in read_jsonl(ROOT / main_path)}
        swap_results = {x["item_id"]: x for x in read_jsonl(ROOT / swap_path)}
        if len(swap_results) != 24:
            raise ValueError(f"{name}: expected 24 swapped results, found {len(swap_results)}")
        rows = []
        for swap_id, swap_key in swap_keys.items():
            source_id = swap_key["source_item_id"]
            if source_id not in main_results or swap_id not in swap_results:
                raise ValueError(f"{name}: missing paired result for {source_id}/{swap_id}")
            original = decode(main_results[source_id], main_keys[source_id])
            swapped = decode(swap_results[swap_id], swap_key)
            expected_flipped_pref = "tie" if original["preference"] == "tie" else ("B" if original["preference"] == "A" else "A")
            row = {
                "reviewer": name, "source_item_id": source_id, "swap_item_id": swap_id,
                "task": main_keys[source_id]["task"],
                "private_comparison": main_keys[source_id]["private_comparison"],
                "replicate_id": main_keys[source_id]["replicate_id"],
                "original_focal_position": original["focal_position"],
                "swapped_focal_position": swapped["focal_position"],
                "original_preference": original["preference"], "swapped_preference": swapped["preference"],
                "original_winner": original["winner"], "swapped_winner": swapped["winner"],
                "content_winner_stable": original["winner"] == swapped["winner"],
                "raw_preference_flipped_as_expected": swapped["preference"] == expected_flipped_pref,
                "original_overall_delta": original["overall_delta"],
                "swapped_overall_delta": swapped["overall_delta"],
            }
            rows.append(row); pair_rows.append(row)
        judgments = [(r["original_winner"], r["original_focal_position"]) for r in rows] + [(r["swapped_winner"], r["swapped_focal_position"]) for r in rows]
        original_rate = sum(credit(r["original_winner"]) for r in rows) / len(rows)
        swapped_rate = sum(credit(r["swapped_winner"]) for r in rows) / len(rows)
        pooled_rate = sum(credit(w) for w, _ in judgments) / len(judgments)
        by_pos = {}
        for pos in ("A", "B"):
            selected = [w for w, p in judgments if p == pos]
            by_pos[pos] = sum(credit(w) for w in selected) / len(selected)
        counts = Counter(w for w, _ in judgments)
        summaries.append({
            "reviewer": name, "pairs": len(rows),
            "stable_content_winner_pairs": sum(r["content_winner_stable"] for r in rows),
            "content_winner_stability": sum(r["content_winner_stable"] for r in rows) / len(rows),
            "expected_raw_preference_flip_pairs": sum(r["raw_preference_flipped_as_expected"] for r in rows),
            "expected_raw_preference_flip_rate": sum(r["raw_preference_flipped_as_expected"] for r in rows) / len(rows),
            "original_win_rate": original_rate, "swapped_win_rate": swapped_rate,
            "position_adjusted_pooled_win_rate": pooled_rate,
            "focal_win_rate_position_A": by_pos["A"], "focal_win_rate_position_B": by_pos["B"],
            "pooled_wins": counts["focused_full"], "pooled_losses": counts["comparator"], "pooled_ties": counts["tie"],
        })

    with (out / "position_swap_pair_results.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(pair_rows[0])); writer.writeheader(); writer.writerows(pair_rows)
    with (out / "position_swap_summary.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summaries[0])); writer.writeheader(); writer.writerows(summaries)
    lines = [
        "# Paired Position-Swapped Control Analysis", "",
        "Each selected content pair is judged once in its original A/B assignment and once after exact A/B reversal.", "",
        "| reviewer | stable content winner | expected A/B flip | original win rate | swapped win rate | adjusted pooled W/L/T | adjusted win rate | focal@A | focal@B |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for x in summaries:
        lines.append(
            f"| {x['reviewer']} | {x['stable_content_winner_pairs']}/{x['pairs']} ({x['content_winner_stability']:.3f}) | "
            f"{x['expected_raw_preference_flip_pairs']}/{x['pairs']} ({x['expected_raw_preference_flip_rate']:.3f}) | "
            f"{x['original_win_rate']:.3f} | {x['swapped_win_rate']:.3f} | "
            f"{x['pooled_wins']}/{x['pooled_losses']}/{x['pooled_ties']} | {x['position_adjusted_pooled_win_rate']:.3f} | "
            f"{x['focal_win_rate_position_A']:.3f} | {x['focal_win_rate_position_B']:.3f} |"
        )
    lines.extend(["", "Interpretation: `stable content winner` is the strictest paired robustness measure. The adjusted pooled rate gives each selected item equal exposure in A and B positions; it does not convert LLM judgments into human evaluation."])
    (out / "POSITION_SWAPPED_CONTROL_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out / 'POSITION_SWAPPED_CONTROL_REPORT.md'}")
    for x in summaries:
        print(f"{x['reviewer']}: stability={x['content_winner_stability']:.3f}, adjusted_win_rate={x['position_adjusted_pooled_win_rate']:.3f}")


if __name__ == "__main__":
    main()
