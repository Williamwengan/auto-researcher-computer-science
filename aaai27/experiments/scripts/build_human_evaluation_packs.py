#!/usr/bin/env python3
"""Build domain-specific, position-balanced human blind-review packets."""

from __future__ import annotations

import csv
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MAIN_ROOT = ROOT / "aaai27/experiments/results/derived/review_pack_main_v3_all_v2_balanced"
NOEV_ROOT = ROOT / "aaai27/experiments/results/derived/review_pack_ablation_no_evidence_v1"
OUT = ROOT / "aaai27/human_evaluation"
SEED = 20260718

DOMAIN_INFO = {
    "physical": ("物理属性预测", "physical_property_expert"),
    "indoor3d": ("室内单图 3D 场景生成", "indoor3d_expert"),
    "iad": ("工业异常检测 IAD + Agent", "iad_expert"),
}

DIMENSIONS = [
    "novelty", "excitement", "feasibility", "expected_effectiveness", "overall",
    "baseline_grounding", "experimental_rigor", "mechanism_specificity", "implementation_readiness",
]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.open(encoding="utf-8") if x.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def collect_sources() -> dict[str, list[dict]]:
    main_public = {x["item_id"]: x for x in read_jsonl(MAIN_ROOT / "anonymous_review_items.jsonl")}
    main_keys = read_jsonl(MAIN_ROOT / "private_answer_key.jsonl")
    noev_public = {x["item_id"]: x for x in read_jsonl(NOEV_ROOT / "anonymous_review_items.jsonl")}
    noev_keys = read_jsonl(NOEV_ROOT / "private_answer_key.jsonl")
    selected: dict[str, list[dict]] = defaultdict(list)

    primary = [x for x in main_keys if x["private_comparison"] == "primary_focused_full_vs_researcharena_portfolio"]
    repair = [x for x in main_keys if x["private_comparison"] == "repair_effect_full_vs_no_repair_idea"]
    consistency = [x for x in main_keys if x["private_comparison"] == "targeted_vs_generic_refine_idea"]
    rng = random.Random(SEED)
    for task in DOMAIN_INFO:
        # All five portfolio-level primary comparisons.
        for key in primary:
            if key["task"] == task:
                selected[task].append({"key": key, "public": main_public[key["item_id"]], "family": "baseline_portfolio"})
        # One paired idea per replicate for each repair comparison.
        for family, pool in (("repair_pair", repair), ("consistency_pair", consistency)):
            by_rep = defaultdict(list)
            for key in pool:
                if key["task"] == task:
                    by_rep[key["replicate_id"]].append(key)
            for replicate_id in sorted(by_rep):
                options = sorted(by_rep[replicate_id], key=lambda x: x["item_id"])
                key = rng.choice(options)
                selected[task].append({"key": key, "public": main_public[key["item_id"]], "family": family})
        # All five portfolio-level evidence ablations.
        for key in noev_keys:
            if key["task"] == task:
                selected[task].append({"key": key, "public": noev_public[key["item_id"]], "family": "evidence_portfolio"})
        if len(selected[task]) != 20:
            raise RuntimeError(f"{task}: expected 20 selected items, found {len(selected[task])}")
    return selected


def candidate_for_method(source: dict, method: str) -> dict:
    key, public = source["key"], source["public"]
    side = next(s for s in ("A", "B") if key["candidate_mapping"][s]["method"] == method)
    return public[f"candidate_{side.lower()}"]


def build_domain(task: str, sources: list[dict]) -> tuple[list[dict], list[dict]]:
    rng = random.Random(SEED + sum(map(ord, task)))
    focal_positions = ["A"] * 10 + ["B"] * 10
    rng.shuffle(focal_positions)
    public_rows, keys = [], []
    for source, focal_side in zip(sources, focal_positions):
        key = source["key"]
        full = candidate_for_method(source, "focused_full")
        other_side = next(s for s in ("A", "B") if key["candidate_mapping"][s]["method"] != "focused_full")
        other_method = key["candidate_mapping"][other_side]["method"]
        other = source["public"][f"candidate_{other_side.lower()}"]
        mapping = (
            {"A": (full, "focused_full"), "B": (other, other_method)}
            if focal_side == "A" else
            {"A": (other, other_method), "B": (full, "focused_full")}
        )
        digest = hashlib.sha256(f"human|{task}|{key['item_id']}".encode()).hexdigest()[:10]
        item_id = f"HUM-{digest}"
        public_rows.append({
            "item_id": item_id, "task": task, "family_public": "portfolio" if key["unit"] == "portfolio" else "single_idea",
            "candidate_a": mapping["A"][0]["text"], "candidate_b": mapping["B"][0]["text"],
        })
        keys.append({
            "item_id": item_id, "source_item_id": key["item_id"], "task": task,
            "private_comparison": key["private_comparison"], "family": source["family"],
            "replicate_id": key["replicate_id"],
            "candidate_mapping": {"A": mapping["A"][1], "B": mapping["B"][1]},
        })
    order = list(range(len(public_rows))); rng.shuffle(order)
    return [public_rows[i] for i in order], [keys[i] for i in order]


def write_packet(task: str, rows: list[dict], reviewer_code: str, label: str) -> None:
    task_dir = OUT / task
    task_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {label}：匿名科研 Idea A/B 评审包", "",
        f"评审者代码：`{reviewer_code}`", "", f"条目数：{len(rows)}", "",
        "请先完整阅读上一级目录的 `HUMAN_BLIND_REVIEW_INSTRUCTIONS_CN.md`。不要查看任何 private answer key，也不要使用大模型代评。",
    ]
    response_fields = ["reviewer_code", "item_id", "domain_familiarity_1_5"]
    for dim in DIMENSIONS:
        response_fields.extend([f"{dim}_A_1_5", f"{dim}_B_1_5"])
    response_fields.extend(["preference_A_B_tie", "confidence_1_5", "rationale_required", "concerns_optional", "minutes_spent"])
    responses = []
    for index, row in enumerate(rows, 1):
        lines.extend([
            "", f"## Item {index}: {row['item_id']}", "", f"类型：`{row['family_public']}`", "",
            "### Candidate A", "", row["candidate_a"], "", "### Candidate B", "", row["candidate_b"], "",
            "---",
        ])
        blank = {field: "" for field in response_fields}
        blank.update({"reviewer_code": reviewer_code, "item_id": row["item_id"]})
        responses.append(blank)
    (task_dir / "ANONYMOUS_REVIEW_PACKET.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_jsonl(task_dir / "public_human_items.jsonl", rows)
    with (task_dir / "RESPONSE_SHEET.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=response_fields); writer.writeheader(); writer.writerows(responses)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sources = collect_sources()
    all_keys = []
    for task, (label, reviewer_code) in DOMAIN_INFO.items():
        rows, keys = build_domain(task, sources[task])
        write_packet(task, rows, reviewer_code, label)
        all_keys.extend(keys)
    write_jsonl(OUT / "private_human_answer_key.jsonl", all_keys)
    print(f"Wrote human evaluation packs to {OUT}")
    for task in DOMAIN_INFO:
        print(f"{task}: 20 items")
    print(f"Private key rows: {len(all_keys)}")


if __name__ == "__main__":
    main()
