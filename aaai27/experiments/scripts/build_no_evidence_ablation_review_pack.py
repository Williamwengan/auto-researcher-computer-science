#!/usr/bin/env python3
"""Build a balanced anonymous full-vs-no-evidence ablation review pack."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from pathlib import Path

from build_anonymous_review_pack import (
    MAIN_REPLICATE_DIRS,
    ROOT,
    TASK_LABELS,
    make_candidate,
    render_portfolio,
    task_dir_for_replicate,
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def short_task(task: str) -> str:
    return {"physical": "physical", "indoor3d": "indoor3d", "iad": "iad"}[task]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-evidence-root", default="aaai27/experiments/results/raw/ablation_no_evidence_v2")
    parser.add_argument("--output-dir", default="aaai27/experiments/results/derived/review_pack_ablation_no_evidence_v1")
    parser.add_argument("--seed", type=int, default=20260716)
    args = parser.parse_args()
    noev_root, out = ROOT / args.no_evidence_root, ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)
    public_rows, key_rows, length_rows = [], [], []

    for task in TASK_LABELS:
        # Five items per task: choose a deterministic random starting side and
        # alternate, giving a 2/3 split within every task and 7/8 overall.
        focal_on_a = rng.choice([True, False])
        for offset, replicate_id in enumerate(sorted(MAIN_REPLICATE_DIRS)):
            full_run_id = f"{short_task(task)}_focused_full_s{replicate_id}"
            full_dir = task_dir_for_replicate(replicate_id, task) / full_run_id
            noev_run_id = f"{short_task(task)}_focused_full_no_evidence_s{replicate_id}"
            noev_dir = noev_root / noev_run_id
            full_meta, noev_meta = read_json(full_dir / "metadata.json"), read_json(noev_dir / "metadata.json")
            if full_meta.get("status") != "success" or noev_meta.get("status") != "success":
                raise RuntimeError(f"Unsuccessful source: {full_run_id} or {noev_run_id}")
            full_ideas = read_json(full_dir / "ideas.json").get("ideas", [])
            noev_ideas = read_json(noev_dir / "ideas.json").get("ideas", [])
            if len(full_ideas) != 3 or len(noev_ideas) != 3:
                raise RuntimeError(f"Expected three ideas: {task} s{replicate_id}")
            full_text, noev_text = render_portfolio(full_ideas), render_portfolio(noev_ideas)
            full_candidate = make_candidate(task, "focused_full", "portfolio", full_text, replicate_id)
            noev_candidate = make_candidate(task, "focused_full_no_evidence", "portfolio", noev_text, replicate_id)
            put_focal_a = focal_on_a if offset % 2 == 0 else not focal_on_a
            ordered = (
                [("A", full_candidate, "focused_full", full_run_id), ("B", noev_candidate, "focused_full_no_evidence", noev_run_id)]
                if put_focal_a else
                [("A", noev_candidate, "focused_full_no_evidence", noev_run_id), ("B", full_candidate, "focused_full", full_run_id)]
            )
            digest = hashlib.sha256(f"{task}|{replicate_id}|full_vs_no_evidence".encode()).hexdigest()[:10]
            item_id = f"ABL-{digest}"
            candidates = {f"candidate_{side.lower()}": candidate for side, candidate, _, _ in ordered}
            public_rows.append({
                "item_id": item_id, "task": task, "task_label": TASK_LABELS[task],
                "replicate_id": replicate_id, "comparison": "ablation_comparison_1", "unit": "portfolio",
                "review_instruction": (
                    "Blindly compare Candidate A and Candidate B. Do not infer method identity. Score novelty, excitement, "
                    "feasibility, expected effectiveness, overall, baseline grounding, experimental rigor, mechanism "
                    "specificity, and implementation readiness; then choose A, B, or tie with a short rationale."
                ), **candidates,
            })
            key_rows.append({
                "item_id": item_id, "task": task, "replicate_id": replicate_id,
                "comparison": "ablation_comparison_1", "private_comparison": "focused_full_vs_no_evidence_portfolio",
                "unit": "portfolio", "candidate_mapping": {
                    side: {"method": method, "run_id": run_id, "idea_id": None, "title": None}
                    for side, _, method, run_id in ordered
                },
            })
            length_rows.extend([
                {"task": task, "replicate_id": replicate_id, "method": "focused_full", "char_count": len(full_text)},
                {"task": task, "replicate_id": replicate_id, "method": "focused_full_no_evidence", "char_count": len(noev_text)},
            ])

    write_jsonl(out / "anonymous_review_items.jsonl", public_rows)
    write_jsonl(out / "private_answer_key.jsonl", key_rows)
    with (out / "candidate_length_stats.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(length_rows[0])); writer.writeheader(); writer.writerows(length_rows)
    focal_positions = {side: sum(x["candidate_mapping"][side]["method"] == "focused_full" for x in key_rows) for side in ("A", "B")}
    summary = [
        "# No-Evidence Ablation Review Pack", "", f"Items: {len(public_rows)}", f"Randomization seed: `{args.seed}`",
        f"focused_full positions: A={focal_positions['A']}, B={focal_positions['B']}", "",
        "Each item compares complete three-idea portfolios from the same task and replicate ID. Source identity is stored only in the private answer key.",
    ]
    (out / "review_pack_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(f"Wrote {out / 'anonymous_review_items.jsonl'}")
    print(f"Wrote {out / 'private_answer_key.jsonl'}")
    print(f"Items: {len(public_rows)}; focused_full A/B={focal_positions['A']}/{focal_positions['B']}")


if __name__ == "__main__":
    main()
