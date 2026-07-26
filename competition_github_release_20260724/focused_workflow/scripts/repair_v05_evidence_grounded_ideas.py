#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def select_targets(scores: dict, repair_all: bool) -> list[dict]:
    targets = []
    for idx, row in enumerate(scores.get("scores", []), start=1):
        penalty_reasons = row.get("granularity_penalty_reasons", []) or []
        dim_scores = row.get("dimension_scores", {}) or {}
        low_dims = {k: v for k, v in dim_scores.items() if isinstance(v, (int, float)) and v <= 7}
        should_repair = repair_all or bool(penalty_reasons) or bool(low_dims)
        if not should_repair:
            continue
        targets.append(
            {
                "idea_index": idx,
                "title": row.get("title", f"idea_{idx}"),
                "idea_quality_score": row.get("idea_quality_score"),
                "granularity_penalty": row.get("granularity_penalty"),
                "penalty_reasons": penalty_reasons,
                "low_dimension_scores": low_dims,
                "required_repairs": [
                    "Add explicit algorithmic objective or scoring function if missing.",
                    "Add quantitative success and failure thresholds.",
                    "Add hard negative controls distinct from ablations.",
                    "Preserve and verify evidence_paper_ids.",
                ],
            }
        )
    return targets


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def render_prompt(run_dir: Path, repair_dir: Path, targets: list[dict]) -> Path:
    root = project_root()
    template = root / "focused_workflow/prompts/v05_evidence_critic_repair_prompt.md"
    prompt = read_text(template)

    replacements = {
        "{{TASK_SPEC_YAML}}": read_text(run_dir / "task_spec.yaml"),
        "{{EVIDENCE_BASELINE_CARDS_JSONL}}": read_text(run_dir / "evidence_baseline_cards.jsonl"),
        "{{PAPER_EVIDENCE_JSONL}}": read_text(run_dir / "prompt_papers.jsonl")
        if (run_dir / "prompt_papers.jsonl").exists()
        else read_text(run_dir / "papers.jsonl"),
        "{{FOCUSED_IDEAS_JSON}}": read_text(run_dir / "focused_ideas.json"),
        "{{EXPERIMENT_PLAN_JSON}}": read_text(run_dir / "experiment_plan.json"),
        "{{IDEA_QUALITY_SCORES_JSON}}": read_text(run_dir / "idea_quality_scores.json"),
        "{{REPAIR_TARGETS_JSON}}": json.dumps(targets, ensure_ascii=False, indent=2),
    }
    for old, new in replacements.items():
        prompt = prompt.replace(old, new)

    repair_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = repair_dir / "v05_evidence_critic_repair_prompt.rendered.md"
    prompt_path.write_text(prompt, encoding="utf-8")
    (repair_dir / "repair_targets.json").write_text(
        json.dumps(targets, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return prompt_path


def run_codex(repair_dir: Path, prompt_path: Path, model: str | None) -> None:
    codex = shutil.which("codex")
    if not codex:
        raise FileNotFoundError("Cannot find codex in PATH. Source ~/.estelle_api_env and add Codex binary to PATH.")
    env = os.environ.copy()
    env.setdefault("CODEX_HOME", str(Path.home() / ".codex-estelle"))
    if not env.get("ESTELLE_API_KEY"):
        raise RuntimeError("ESTELLE_API_KEY is empty. Run: source ~/.estelle_api_env")

    cmd = [
        codex,
        "exec",
        "--skip-git-repo-check",
        "--dangerously-bypass-approvals-and-sandbox",
    ]
    if model:
        cmd.extend(["--model", model])
    cmd.append(
        f"Read {prompt_path.name} and execute it. "
        "Write focused_ideas_repaired.json and experiment_plan_repaired.json in the current working directory."
    )
    subprocess.run(cmd, cwd=repair_dir, env=env, check=True)


def validate_repair_json(repair_dir: Path) -> None:
    ideas_path = repair_dir / "focused_ideas_repaired.json"
    plans_path = repair_dir / "experiment_plan_repaired.json"
    if not ideas_path.exists() or not plans_path.exists():
        raise FileNotFoundError("Missing focused_ideas_repaired.json or experiment_plan_repaired.json")
    ideas = load_json(ideas_path)
    plans = load_json(plans_path)
    if not isinstance(ideas, list):
        raise TypeError("focused_ideas_repaired.json must be a JSON list")
    if not isinstance(plans, list):
        raise TypeError("experiment_plan_repaired.json must be a JSON list")
    if len(ideas) != len(plans):
        raise ValueError("Repaired ideas and plans must have the same count")


def copy_for_repaired_run(run_dir: Path, repair_dir: Path) -> Path:
    repaired_run = repair_dir / "repaired_run"
    repaired_run.mkdir(parents=True, exist_ok=True)
    copy_names = [
        "task_spec.yaml",
        "baseline_cards.jsonl",
        "evidence_baseline_cards.jsonl",
        "papers.jsonl",
        "prompt_papers.jsonl",
        "evidence_context.md",
        "evidence_quality_summary.json",
    ]
    for name in copy_names:
        src = run_dir / name
        if src.exists():
            shutil.copy2(src, repaired_run / name)
    shutil.copy2(repair_dir / "focused_ideas_repaired.json", repaired_run / "focused_ideas.json")
    shutil.copy2(repair_dir / "experiment_plan_repaired.json", repaired_run / "experiment_plan.json")
    return repaired_run


def run_postprocess(repaired_run: Path) -> None:
    root = project_root()
    commands = [
        ["python", "focused_workflow/scripts/normalize_v05_ideation_outputs.py", str(repaired_run)],
        ["python", "focused_workflow/scripts/validate_outputs.py", str(repaired_run)],
        ["python", "focused_workflow/scripts/validate_evidence_grounding.py", str(repaired_run)],
        ["python", "focused_workflow/scripts/format_ideas_for_review.py", str(repaired_run)],
        ["python", "focused_workflow/scripts/evaluate_idea_quality.py", str(repaired_run), "--overwrite"],
        ["python", "focused_workflow/scripts/make_si2025_review_sheet.py", str(repaired_run)],
    ]
    for cmd in commands:
        subprocess.run(cmd, cwd=root, check=True)


def write_summary(repair_dir: Path, run_dir: Path, repaired_run: Path | None, targets: list[dict], dry_run: bool) -> None:
    lines = [
        "# v0.5 Evidence-Grounded Targeted Repair Summary",
        "",
        f"- Original run: `{run_dir}`",
        f"- Repair dir: `{repair_dir}`",
        f"- Repaired run: `{repaired_run}`" if repaired_run else "- Repaired run: not generated",
        f"- Mode: `{'dry-run' if dry_run else 'executed'}`",
        f"- Repair targets: {len(targets)}",
        "",
        "## Targets",
        "",
        "| Idea | Score | Penalty | Reasons |",
        "|---|---:|---:|---|",
    ]
    for target in targets:
        lines.append(
            f"| {target['title']} | {target.get('idea_quality_score')} | "
            f"{target.get('granularity_penalty')} | {', '.join(target.get('penalty_reasons') or [])} |"
        )
    lines.extend(
        [
            "",
            "## Required Post-Repair Checks",
            "",
            "- `validate_outputs.py` must pass.",
            "- `validate_evidence_grounding.py` must pass.",
            "- `idea_quality_scores.json` should improve or penalties should decrease.",
            "- Evidence IDs must not be invented.",
        ]
    )
    (repair_dir / "repair_summary_CN.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run v0.5 evidence-grounded targeted repair.")
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--all", action="store_true", help="Repair all ideas")
    parser.add_argument("--dry-run", action="store_true", help="Only render prompt")
    parser.add_argument("--no-postprocess", action="store_true", help="Do not create repaired_run or run validation/scoring")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    if not run_dir.exists():
        raise FileNotFoundError(run_dir)
    scores = load_json(run_dir / "idea_quality_scores.json")
    targets = select_targets(scores, args.all)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    repair_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else run_dir / "repair_runs" / f"v05_targeted_repair_{timestamp}"
    )

    prompt_path = render_prompt(run_dir, repair_dir, targets)
    repaired_run = None
    if targets and not args.dry_run:
        run_codex(repair_dir, prompt_path, args.model)
        validate_repair_json(repair_dir)
        if not args.no_postprocess:
            repaired_run = copy_for_repaired_run(run_dir, repair_dir)
            run_postprocess(repaired_run)

    write_summary(repair_dir, run_dir, repaired_run, targets, args.dry_run)
    print("v0.5 targeted repair prepared")
    print("Run dir:", run_dir)
    print("Repair dir:", repair_dir)
    print("Targets:", len(targets))
    if repaired_run:
        print("Repaired run:", repaired_run)
    if args.dry_run:
        print("Dry run only:", prompt_path)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
