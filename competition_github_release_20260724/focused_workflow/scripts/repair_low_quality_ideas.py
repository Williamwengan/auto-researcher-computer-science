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
    return json.loads(path.read_text())


def select_repair_targets(scores: dict, min_score: float, max_penalty: float, repair_all: bool) -> list[dict]:
    targets = []
    for idx, row in enumerate(scores.get("scores", []), start=1):
        score = float(row.get("idea_quality_score", row.get("raw_quality_score", 0)))
        penalty = float(row.get("granularity_penalty", 0))
        reasons = row.get("granularity_penalty_reasons", [])
        dim_scores = row.get("dimension_scores", {})
        low_dims = {k: v for k, v in dim_scores.items() if isinstance(v, (int, float)) and v <= 7}
        should = repair_all or score < min_score or penalty > max_penalty or bool(reasons)
        if should:
            targets.append(
                {
                    "idea_index": idx,
                    "title": row.get("title", f"Idea {idx}"),
                    "idea_quality_score": score,
                    "granularity_penalty": penalty,
                    "penalty_reasons": reasons,
                    "low_dimension_scores": low_dims,
                    "repair_instruction": "Repair only the weaknesses listed here; keep task direction, baselines, and output schema stable.",
                }
            )
    return targets


def render_repair_prompt(run_dir: Path, repair_dir: Path, targets: list[dict]) -> Path:
    root = project_root()
    template = root / "focused_workflow/prompts/idea_critic_repair_prompt.md"
    if not template.exists():
        raise FileNotFoundError(f"Missing repair prompt template: {template}")

    required = {
        "task_spec": run_dir / "task_spec.yaml",
        "focused_ideas": run_dir / "focused_ideas.json",
        "experiment_plan": run_dir / "experiment_plan.json",
        "quality_scores": run_dir / "idea_quality_scores.json",
    }
    for name, path in required.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing {name}: {path}")

    prompt = template.read_text()
    prompt = prompt.replace("{{TASK_SPEC_YAML}}", required["task_spec"].read_text())
    prompt = prompt.replace("{{FOCUSED_IDEAS_JSON}}", required["focused_ideas"].read_text())
    prompt = prompt.replace("{{EXPERIMENT_PLAN_JSON}}", required["experiment_plan"].read_text())
    prompt = prompt.replace("{{IDEA_QUALITY_SCORES_JSON}}", required["quality_scores"].read_text())
    prompt = prompt.replace("{{REPAIR_TARGETS_JSON}}", json.dumps(targets, ensure_ascii=False, indent=2))

    repair_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = repair_dir / "idea_critic_repair_prompt.rendered.md"
    prompt_path.write_text(prompt, encoding="utf-8")
    (repair_dir / "repair_targets.json").write_text(json.dumps(targets, ensure_ascii=False, indent=2), encoding="utf-8")
    return prompt_path


def run_codex(repair_dir: Path, prompt_path: Path):
    codex = shutil.which("codex")
    if not codex:
        raise FileNotFoundError("Cannot find codex in PATH. Source ~/.estelle_api_env and add Codex binary to PATH.")
    env = os.environ.copy()
    env.setdefault("CODEX_HOME", str(Path.home() / ".codex-estelle"))
    if not env.get("ESTELLE_API_KEY"):
        raise RuntimeError("ESTELLE_API_KEY is empty. Run: source ~/.estelle_api_env")
    subprocess.run(
        [
            codex,
            "exec",
            "--skip-git-repo-check",
            "--dangerously-bypass-approvals-and-sandbox",
            f"Read {prompt_path.name} and execute it. Write focused_ideas_repaired.json and experiment_plan_repaired.json in the current directory.",
        ],
        cwd=repair_dir,
        env=env,
        check=True,
    )


def validate_repair_outputs(repair_dir: Path):
    ideas_path = repair_dir / "focused_ideas_repaired.json"
    plans_path = repair_dir / "experiment_plan_repaired.json"
    if not ideas_path.exists() or not plans_path.exists():
        raise FileNotFoundError("Repair did not create focused_ideas_repaired.json and experiment_plan_repaired.json")
    ideas = load_json(ideas_path)
    plans = load_json(plans_path)
    if not isinstance(ideas, list) or not isinstance(plans, list):
        raise TypeError("Repaired outputs must both be JSON lists")
    if len(ideas) != len(plans):
        raise ValueError("Repaired ideas and plans should have the same count")
    return ideas, plans


def write_summary(repair_dir: Path, run_dir: Path, targets: list[dict], dry_run: bool):
    lines = []
    lines.append("# Critic-Repair 运行摘要\n")
    lines.append(f"Original run: `{run_dir}`\n")
    lines.append(f"Repair dir: `{repair_dir}`\n")
    lines.append(f"Mode: `{'dry-run' if dry_run else 'executed'}`\n")
    lines.append("## Repair Targets\n")
    if not targets:
        lines.append("没有发现需要修复的 idea。\n")
    else:
        lines.append("| Idea | Score | Penalty | Reasons |")
        lines.append("|---|---:|---:|---|")
        for t in targets:
            lines.append(f"| {t['title']} | {t['idea_quality_score']} | {t['granularity_penalty']} | {', '.join(t.get('penalty_reasons') or [])} |")
    lines.append("\n## Next Step\n")
    if dry_run:
        lines.append("Dry-run 已生成 repair prompt。确认后可去掉 `--dry-run` 调用 LLM 生成 repaired JSON。")
    else:
        lines.append("请将 repaired JSON 放入一个新的 run 目录后重新运行 validate_outputs.py、format_ideas_for_review.py 和 evaluate_idea_quality.py，比较 before/after。")
    (repair_dir / "repair_summary_CN.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Critic-repair low-quality focused ideas without overwriting originals.")
    parser.add_argument("run_dir", help="Focused workflow output directory")
    parser.add_argument("--min-score", type=float, default=88.0, help="Repair ideas below this quality score")
    parser.add_argument("--max-penalty", type=float, default=0.0, help="Repair ideas with granularity penalty above this value")
    parser.add_argument("--all", action="store_true", help="Repair all ideas")
    parser.add_argument("--dry-run", action="store_true", help="Render repair prompt only; do not call LLM")
    parser.add_argument("--output-dir", default=None, help="Default: <run_dir>/repair_runs/repair_<timestamp>")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    if not run_dir.exists():
        raise FileNotFoundError(f"Missing run_dir: {run_dir}")
    scores_path = run_dir / "idea_quality_scores.json"
    if not scores_path.exists():
        raise FileNotFoundError(f"Missing idea_quality_scores.json: {scores_path}")

    scores = load_json(scores_path)
    targets = select_repair_targets(scores, args.min_score, args.max_penalty, args.all)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    repair_dir = Path(args.output_dir).resolve() if args.output_dir else run_dir / "repair_runs" / f"repair_{timestamp}"
    prompt_path = render_repair_prompt(run_dir, repair_dir, targets)
    write_summary(repair_dir, run_dir, targets, args.dry_run)

    print("Repair targets:", len(targets))
    print("Rendered prompt:", prompt_path)
    print("Repair dir:", repair_dir)

    if not targets:
        print("No repair targets selected. Use --all to force repair.")
        return
    if args.dry_run:
        print("Dry run only. No LLM call was made.")
        return

    run_codex(repair_dir, prompt_path)
    ideas, plans = validate_repair_outputs(repair_dir)
    print("Saved repaired ideas:", len(ideas))
    print("Saved repaired plans:", len(plans))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
