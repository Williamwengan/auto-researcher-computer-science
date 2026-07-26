#!/usr/bin/env python3
"""Build a stratified position-swapped control subset from a review pack."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.open(encoding="utf-8") if x.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-pack", required=True)
    parser.add_argument("--answer-key", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--seed", type=int, default=20260715)
    args = parser.parse_args()
    public = read_jsonl(ROOT / args.review_pack)
    keys = read_jsonl(ROOT / args.answer_key)
    pub_by_id = {x["item_id"]: x for x in public}
    groups = defaultdict(list)
    for key in keys:
        groups[(key["private_comparison"], key["task"])].append(key)
    rng = random.Random(args.seed)
    selected = []
    for group in sorted(groups):
        candidates = groups[group][:]
        rng.shuffle(candidates)
        # Two items per task for each of four comparison types: 24 total.
        chosen = []
        used_replicates = set()
        for item in candidates:
            if item["replicate_id"] not in used_replicates:
                chosen.append(item); used_replicates.add(item["replicate_id"])
            if len(chosen) == 2:
                break
        selected.extend(chosen)
    if len(selected) != 24:
        raise RuntimeError(f"Expected 24 stratified items, found {len(selected)}")

    swapped_public, swapped_keys = [], []
    for key in selected:
        original = pub_by_id[key["item_id"]]
        digest = hashlib.sha256((key["item_id"] + "||position_swap_v1").encode()).hexdigest()[:10]
        new_id = f"SWAP-{digest}"
        item = dict(original)
        item["item_id"] = new_id
        item["comparison"] = original["comparison"] + "_position_swap"
        item["candidate_a"], item["candidate_b"] = original["candidate_b"], original["candidate_a"]
        swapped_public.append(item)
        new_key = dict(key)
        new_key["item_id"] = new_id
        new_key["comparison"] = item["comparison"]
        new_key["source_item_id"] = key["item_id"]
        new_key["candidate_mapping"] = {
            "A": key["candidate_mapping"]["B"],
            "B": key["candidate_mapping"]["A"],
        }
        swapped_keys.append(new_key)
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    write_jsonl(out / "anonymous_review_items.jsonl", swapped_public)
    write_jsonl(out / "private_answer_key.jsonl", swapped_keys)
    summary = [
        "# Position-Swapped Control Pack", "", f"Items: {len(swapped_public)}",
        f"Seed: `{args.seed}`", "",
        "The subset contains two items per task for each private comparison type, using distinct replicates where possible. Candidate A/B positions are reversed relative to the main balanced pack.",
        "", "The private key contains `source_item_id` for paired position-effect analysis.",
    ]
    (out / "position_swap_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(f"Wrote {out / 'anonymous_review_items.jsonl'}")
    print(f"Wrote {out / 'private_answer_key.jsonl'}")
    print(f"Position-swapped items: {len(swapped_public)}")


if __name__ == "__main__":
    main()
