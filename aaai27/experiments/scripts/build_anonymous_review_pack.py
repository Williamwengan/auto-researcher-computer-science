#!/usr/bin/env python3
"""Build deterministic anonymous review packs from generation outputs.

The pack intentionally separates public blind-review items from a private
answer key. It does not call any model and does not modify generation outputs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]

DEFAULT_RUN_DIRS = {
    "physical": "aaai27/experiments/results/raw/smoke_physical_protocol_v3",
    "indoor3d": "aaai27/experiments/results/raw/smoke_indoor3d_protocol_v3_retry2",
    "iad": "aaai27/experiments/results/raw/smoke_iad_protocol_v3",
}

MAIN_REPLICATE_DIRS = {
    11: {
        "physical": "aaai27/experiments/results/raw/smoke_physical_protocol_v3",
        "indoor3d": "aaai27/experiments/results/raw/smoke_indoor3d_protocol_v3_retry2",
        "iad": "aaai27/experiments/results/raw/smoke_iad_protocol_v3",
    },
    23: {"all": "aaai27/experiments/results/raw/main_protocol_v3_s23"},
    37: {"all": "aaai27/experiments/results/raw/main_protocol_v3_s37"},
    53: {"all": "aaai27/experiments/results/raw/main_protocol_v3_s53"},
    71: {"all": "aaai27/experiments/results/raw/main_protocol_v3_s71"},
}

TASK_LABELS = {
    "physical": "Physical property prediction",
    "indoor3d": "Indoor single-image-to-3D scene generation",
    "iad": "Industrial anomaly detection agent workflow",
}

METHODS = [
    "direct_prompt",
    "researcharena",
    "focused_no_repair",
    "focused_generic_refine",
    "focused_full",
]

RUN_ID_BY_TASK_METHOD = {
    task: {method: f"{task}_{method}_s11" for method in METHODS} for task in DEFAULT_RUN_DIRS
}
RUN_ID_BY_TASK_METHOD["physical"] = {
    method: f"physical_{method}_s11" for method in METHODS
}
RUN_ID_BY_TASK_METHOD["indoor3d"] = {
    method: f"indoor3d_{method}_s11" for method in METHODS
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def stable_id(*parts: str) -> str:
    digest = hashlib.sha256("||".join(parts).encode("utf-8")).hexdigest()[:10]
    return digest


def as_list_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join(str(item) for item in value if str(item).strip())
    return str(value)


def render_idea(idea: dict) -> str:
    title = idea.get("title", "").strip()
    core = idea.get("description") or idea.get("proposed_mechanism") or ""
    motivation = idea.get("motivation") or idea.get("baseline_weakness") or ""
    mechanism_bits = [
        idea.get("proposed_approach"),
        idea.get("minimal_new_module"),
        idea.get("algorithmic_objective"),
    ]
    mechanism = "\n".join(str(x).strip() for x in mechanism_bits if str(x or "").strip())
    experiment_bits = [
        idea.get("experiment_outline"),
        as_list_text(idea.get("direct_baselines")),
        as_list_text(idea.get("required_data")),
        as_list_text(idea.get("required_scripts")),
        as_list_text(idea.get("metrics")),
        as_list_text(idea.get("ablations")),
        as_list_text(idea.get("negative_controls")),
        as_list_text(idea.get("success_thresholds")),
    ]
    experiment = "\n".join(str(x).strip() for x in experiment_bits if str(x or "").strip())
    risks = idea.get("risk_and_fallback", "")
    evidence = as_list_text(idea.get("evidence_paper_ids"))
    sections = [
        ("Title", title),
        ("Core proposal", core),
        ("Motivation or baseline weakness", motivation),
        ("Mechanism or approach", mechanism),
        ("Experiment and implementation plan", experiment),
        ("Evidence paper IDs", evidence),
        ("Risks, controls, or fallback", risks),
    ]
    return "\n\n".join(f"{name}:\n{text}" for name, text in sections if str(text).strip())


def render_portfolio(ideas: list[dict]) -> str:
    blocks = []
    for idx, idea in enumerate(ideas, 1):
        blocks.append(f"Idea {idx}\n{render_idea(idea)}")
    return "\n\n---\n\n".join(blocks)


def run_id(task: str, method: str, replicate_id: int) -> str:
    return f"{task}_{method}_s{replicate_id}"


def task_dir_for_replicate(replicate_id: int, task: str) -> Path:
    dirs = MAIN_REPLICATE_DIRS[replicate_id]
    rel_dir = dirs.get(task) or dirs["all"]
    return ROOT / rel_dir


def load_task_outputs(raw_root: Path) -> dict:
    data = {}
    for task, rel_dir in DEFAULT_RUN_DIRS.items():
        task_dir = raw_root / rel_dir if raw_root != ROOT else ROOT / rel_dir
        if not task_dir.exists():
            raise FileNotFoundError(f"Missing task run directory: {task_dir}")
        data[task] = {}
        for method, run_id in RUN_ID_BY_TASK_METHOD[task].items():
            run_dir = task_dir / run_id
            ideas_path = run_dir / "ideas.json"
            metadata_path = run_dir / "metadata.json"
            if not ideas_path.exists() or not metadata_path.exists():
                raise FileNotFoundError(f"Missing ideas/metadata for {run_id} in {run_dir}")
            ideas = read_json(ideas_path).get("ideas", [])
            metadata = read_json(metadata_path)
            if metadata.get("status") != "success":
                raise RuntimeError(f"{run_id} is not successful: {metadata.get('status')}")
            if len(ideas) != 3:
                raise RuntimeError(f"{run_id} expected 3 ideas, found {len(ideas)}")
            data[task][method] = {"run_id": run_id, "ideas": ideas, "metadata": metadata}
    return data


def load_replicate_outputs(replicate_ids: list[int]) -> dict:
    data = {}
    for replicate_id in replicate_ids:
        data[replicate_id] = {}
        for task in TASK_LABELS:
            task_dir = task_dir_for_replicate(replicate_id, task)
            if not task_dir.exists():
                raise FileNotFoundError(f"Missing task run directory: {task_dir}")
            data[replicate_id][task] = {}
            for method in METHODS:
                rid = run_id(task, method, replicate_id)
                run_dir = task_dir / rid
                ideas_path = run_dir / "ideas.json"
                metadata_path = run_dir / "metadata.json"
                if not ideas_path.exists() or not metadata_path.exists():
                    raise FileNotFoundError(f"Missing ideas/metadata for {rid} in {run_dir}")
                ideas = read_json(ideas_path).get("ideas", [])
                metadata = read_json(metadata_path)
                if metadata.get("status") != "success":
                    raise RuntimeError(f"{rid} is not successful: {metadata.get('status')}")
                if len(ideas) != 3:
                    raise RuntimeError(f"{rid} expected 3 ideas, found {len(ideas)}")
                data[replicate_id][task][method] = {"run_id": rid, "ideas": ideas, "metadata": metadata}
    return data


def make_candidate(task: str, method: str, unit: str, text: str, replicate_id: int, idea_id: str | None = None) -> dict:
    digest = stable_id(str(replicate_id), task, method, unit, idea_id or "portfolio", text)
    return {
        "anonymous_candidate_id": f"CAND-{digest}",
        "text": text,
        "char_count": len(text),
    }


def add_item(rows: list[dict], keys: list[dict], rng: random.Random, position_counts: dict, task: str, replicate_id: int, public_comparison: str,
             private_comparison: str, unit: str, left: dict, right: dict, left_meta: dict, right_meta: dict) -> None:
    # Balance the focal (left) method across A/B within each comparison type.
    # The previous implementation shuffled tuples that already contained the
    # labels "A" and "B", so the left method remained Candidate A even when
    # tuple order changed.  Assign labels only after deciding the order.
    counts = position_counts.setdefault(private_comparison, {"A": 0, "B": 0})
    if counts["A"] == counts["B"]:
        left_position = rng.choice(["A", "B"])
    else:
        left_position = "A" if counts["A"] < counts["B"] else "B"
    counts[left_position] += 1
    if left_position == "A":
        candidates = [("A", left, left_meta), ("B", right, right_meta)]
    else:
        candidates = [("A", right, right_meta), ("B", left, left_meta)]
    item_id = f"REV-{stable_id(str(replicate_id), task, private_comparison, unit, left_meta['method'], right_meta['method'])}"
    public_candidates = {}
    key_candidates = {}
    for position, candidate, meta in candidates:
        public_candidates[f"candidate_{position.lower()}"] = candidate
        key_candidates[position] = {
            "method": meta["method"],
            "run_id": meta["run_id"],
            "idea_id": meta.get("idea_id"),
            "title": meta.get("title"),
        }
    rows.append(
        {
            "item_id": item_id,
            "task": task,
            "task_label": TASK_LABELS[task],
            "replicate_id": replicate_id,
            "comparison": public_comparison,
            "unit": unit,
            "review_instruction": (
                "Blindly compare Candidate A and Candidate B. Do not infer method identity. "
                "Score novelty, excitement, feasibility, expected effectiveness, overall, "
                "baseline grounding, experimental rigor, mechanism specificity, and implementation readiness; "
                "then choose A, B, or tie with a short rationale."
            ),
            **public_candidates,
        }
    )
    keys.append(
        {
            "item_id": item_id,
            "task": task,
            "replicate_id": replicate_id,
            "comparison": public_comparison,
            "private_comparison": private_comparison,
            "unit": unit,
            "candidate_mapping": key_candidates,
        }
    )


def build_pack(data: dict, seed: int) -> tuple[list[dict], list[dict], list[dict]]:
    rng = random.Random(seed)
    rows: list[dict] = []
    keys: list[dict] = []
    length_rows: list[dict] = []
    position_counts: dict[str, dict[str, int]] = {}
    portfolio_comparisons = [
        ("portfolio_comparison_1", "primary_focused_full_vs_researcharena_portfolio", "focused_full", "researcharena"),
        ("portfolio_comparison_2", "focused_full_vs_direct_prompt_portfolio", "focused_full", "direct_prompt"),
    ]
    paired_comparisons = [
        ("paired_idea_comparison_1", "repair_effect_full_vs_no_repair_idea", "focused_full", "focused_no_repair"),
        ("paired_idea_comparison_2", "targeted_vs_generic_refine_idea", "focused_full", "focused_generic_refine"),
    ]
    if 11 not in data:
        data = {11: data}
    for replicate_id, replicate_data in data.items():
        for task, task_data in replicate_data.items():
            for public_comparison, private_comparison, left_method, right_method in portfolio_comparisons:
                left_text = render_portfolio(task_data[left_method]["ideas"])
                right_text = render_portfolio(task_data[right_method]["ideas"])
                left = make_candidate(task, left_method, "portfolio", left_text, replicate_id)
                right = make_candidate(task, right_method, "portfolio", right_text, replicate_id)
                add_item(
                    rows,
                    keys,
                    rng,
                    position_counts,
                    task,
                    replicate_id,
                    public_comparison,
                    private_comparison,
                    "portfolio",
                    left,
                    right,
                    {"method": left_method, "run_id": task_data[left_method]["run_id"]},
                    {"method": right_method, "run_id": task_data[right_method]["run_id"]},
                )
                length_rows.extend([
                    {"replicate_id": replicate_id, "task": task, "public_comparison": public_comparison, "private_comparison": private_comparison, "method": left_method, "unit": "portfolio", "char_count": len(left_text)},
                    {"replicate_id": replicate_id, "task": task, "public_comparison": public_comparison, "private_comparison": private_comparison, "method": right_method, "unit": "portfolio", "char_count": len(right_text)},
                ])
            for public_comparison, private_comparison, left_method, right_method in paired_comparisons:
                for idx in range(3):
                    left_idea = task_data[left_method]["ideas"][idx]
                    right_idea = task_data[right_method]["ideas"][idx]
                    idea_id = left_idea.get("idea_id") or f"idea_{idx + 1}"
                    unit = idea_id
                    left_text = render_idea(left_idea)
                    right_text = render_idea(right_idea)
                    left = make_candidate(task, left_method, unit, left_text, replicate_id, idea_id)
                    right = make_candidate(task, right_method, unit, right_text, replicate_id, idea_id)
                    add_item(
                        rows,
                        keys,
                        rng,
                        position_counts,
                        task,
                        replicate_id,
                        public_comparison,
                        private_comparison,
                        unit,
                        left,
                        right,
                        {
                            "method": left_method,
                            "run_id": task_data[left_method]["run_id"],
                            "idea_id": idea_id,
                            "title": left_idea.get("title"),
                        },
                        {
                            "method": right_method,
                            "run_id": task_data[right_method]["run_id"],
                            "idea_id": right_idea.get("idea_id") or f"idea_{idx + 1}",
                            "title": right_idea.get("title"),
                        },
                    )
                    length_rows.extend([
                        {"replicate_id": replicate_id, "task": task, "public_comparison": public_comparison, "private_comparison": private_comparison, "method": left_method, "unit": unit, "char_count": len(left_text)},
                        {"replicate_id": replicate_id, "task": task, "public_comparison": public_comparison, "private_comparison": private_comparison, "method": right_method, "unit": unit, "char_count": len(right_text)},
                    ])
    return rows, keys, length_rows


def write_markdown(path: Path, rows: list[dict], key_path: Path) -> None:
    lines = [
        "# AAAI-27 Anonymous Review Pack",
        "",
        "This public file contains blind review items only. Method labels are stored separately in the private answer key.",
        "",
        f"Review items: {len(rows)}",
        "",
        "Reviewer instruction: score each candidate on novelty, excitement, feasibility, expected effectiveness, overall, baseline grounding, experimental rigor, mechanism specificity, and implementation readiness. Then choose A, B, or tie and provide a short rationale.",
        "",
        f"Private answer key: `{key_path.name}`",
        "",
    ]
    for row in rows:
        lines.extend([
            f"## {row['item_id']}",
            "",
            f"- Task: {row['task_label']}",
            f"- Replicate: `{row['replicate_id']}`",
            f"- Comparison: `{row['comparison']}`",
            f"- Unit: `{row['unit']}`",
            "",
            "### Candidate A",
            "",
            row["candidate_a"]["text"],
            "",
            "### Candidate B",
            "",
            row["candidate_b"]["text"],
            "",
        ])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_summary(path: Path, rows: list[dict], length_rows: list[dict], seed: int) -> None:
    by_comparison = {}
    by_replicate = {}
    for row in rows:
        by_comparison[row["comparison"]] = by_comparison.get(row["comparison"], 0) + 1
        by_replicate[row["replicate_id"]] = by_replicate.get(row["replicate_id"], 0) + 1
    lines = [
        "# Anonymous Review Pack Summary",
        "",
        f"Randomization seed: `{seed}`",
        "",
        f"Total review items: {len(rows)}",
        "",
        "| comparison | items |",
        "| --- | ---: |",
    ]
    for comparison in sorted(by_comparison):
        lines.append(f"| {comparison} | {by_comparison[comparison]} |")
    lines.extend([
        "",
        "| replicate | items |",
        "| --- | ---: |",
    ])
    for replicate_id in sorted(by_replicate):
        lines.append(f"| {replicate_id} | {by_replicate[replicate_id]} |")
    lines.extend([
        "",
        "Design notes:",
        "",
        "- Portfolio items compare complete three-idea sets for methods that are not semantically paired idea-by-idea.",
        "- Idea-pair items compare refinement branches that share the same initial focused ideas.",
        "- Candidate text uses a common deterministic renderer and does not add new model-generated content.",
        "- Public comparison labels are anonymized; the private answer key and length stats must not be shown to reviewers.",
        "",
        f"Length rows: {len(length_rows)}",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="aaai27/experiments/results/derived/review_pack_seed11_v1")
    parser.add_argument("--randomization-seed", type=int, default=20260714)
    parser.add_argument(
        "--replicate-id",
        action="append",
        type=int,
        help="Include selected replicate_id values; repeat this flag as needed. Defaults to 11.",
    )
    parser.add_argument("--all-main-replicates", action="store_true", help="Include replicates 11, 23, 37, 53, and 71.")
    args = parser.parse_args()
    out_dir = ROOT / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    replicate_ids = sorted(MAIN_REPLICATE_DIRS) if args.all_main_replicates else (args.replicate_id or [11])
    data = load_replicate_outputs(replicate_ids)
    rows, keys, length_rows = build_pack(data, args.randomization_seed)
    write_jsonl(out_dir / "anonymous_review_items.jsonl", rows)
    write_jsonl(out_dir / "private_answer_key.jsonl", keys)
    with (out_dir / "candidate_length_stats.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["replicate_id", "task", "public_comparison", "private_comparison", "method", "unit", "char_count"])
        writer.writeheader()
        writer.writerows(length_rows)
    write_markdown(out_dir / "anonymous_review_pack.md", rows, out_dir / "private_answer_key.jsonl")
    write_summary(out_dir / "review_pack_summary.md", rows, length_rows, args.randomization_seed)
    print(f"Wrote {out_dir / 'anonymous_review_items.jsonl'}")
    print(f"Wrote {out_dir / 'private_answer_key.jsonl'}")
    print(f"Wrote {out_dir / 'anonymous_review_pack.md'}")
    print(f"Wrote {out_dir / 'review_pack_summary.md'}")
    print(f"Review items: {len(rows)}")


if __name__ == "__main__":
    main()
