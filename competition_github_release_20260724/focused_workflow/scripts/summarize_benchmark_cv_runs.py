import argparse
import json
import subprocess
import sys
from pathlib import Path


REQUIRED_OUTPUTS = [
    "baseline_cards.jsonl",
    "focused_ideas.json",
    "experiment_plan.json",
    "prompt.md",
    "task_spec.yaml",
]


def load_json(path: Path):
    return json.loads(path.read_text())


def count_jsonl(path: Path):
    if not path.exists():
        return 0
    count = 0
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        json.loads(line)
        count += 1
    return count


def run_validator(project_root: Path, run_dir: Path):
    validator = project_root / "focused_workflow/scripts/validate_outputs.py"
    if not validator.exists():
        return False, "missing validate_outputs.py"

    result = subprocess.run(
        [sys.executable, str(validator), str(run_dir)],
        cwd=project_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.returncode == 0, result.stdout.strip()


def summarize_run(project_root: Path, run_dir: Path):
    item = {
        "run_dir": str(run_dir),
        "task_name": run_dir.name,
        "exists": run_dir.exists(),
        "complete_files": False,
        "baseline_cards": 0,
        "focused_ideas": 0,
        "experiment_plans": 0,
        "review_ready_ideas": 0,
        "manual_review_sheet": False,
        "schema_validation_passed": False,
        "schema_validation_output": "",
        "errors": [],
    }

    if not run_dir.exists():
        item["errors"].append("run directory does not exist")
        return item

    missing = [name for name in REQUIRED_OUTPUTS if not (run_dir / name).exists()]
    if missing:
        item["errors"].append("missing files: " + ", ".join(missing))
    else:
        item["complete_files"] = True

    try:
        item["baseline_cards"] = count_jsonl(run_dir / "baseline_cards.jsonl")
    except Exception as exc:
        item["errors"].append(f"baseline_cards.jsonl parse error: {exc}")

    try:
        ideas_path = run_dir / "focused_ideas.json"
        if ideas_path.exists():
            ideas = load_json(ideas_path)
            item["focused_ideas"] = len(ideas) if isinstance(ideas, list) else 0
    except Exception as exc:
        item["errors"].append(f"focused_ideas.json parse error: {exc}")

    try:
        plans_path = run_dir / "experiment_plan.json"
        if plans_path.exists():
            plans = load_json(plans_path)
            item["experiment_plans"] = len(plans) if isinstance(plans, list) else 0
    except Exception as exc:
        item["errors"].append(f"experiment_plan.json parse error: {exc}")

    review_dir = run_dir / "review_ready_ideas"
    if review_dir.exists():
        item["review_ready_ideas"] = len(list(review_dir.glob("idea_*.md")))

    item["manual_review_sheet"] = (run_dir / "si2025_manual_review_sheet.json").exists()

    if item["complete_files"]:
        passed, output = run_validator(project_root, run_dir)
        item["schema_validation_passed"] = passed
        item["schema_validation_output"] = output
        if not passed:
            item["errors"].append("schema validation failed")

    return item


def main():
    parser = argparse.ArgumentParser(description="Summarize Focused Workflow CV benchmark runs.")
    parser.add_argument("benchmark_root", help="Benchmark root created by run_benchmark_cv_tasks.sh")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    benchmark_root = Path(args.benchmark_root).resolve()

    if not benchmark_root.exists():
        raise FileNotFoundError(f"Missing benchmark root: {benchmark_root}")

    run_dirs = sorted([path for path in benchmark_root.iterdir() if path.is_dir()])
    summaries = [summarize_run(project_root, run_dir) for run_dir in run_dirs]

    json_path = benchmark_root / "benchmark_summary.json"
    json_path.write_text(json.dumps(summaries, indent=2, ensure_ascii=False))

    md_lines = [
        "# Focused Workflow CV Benchmark Summary",
        "",
        f"Benchmark root: `{benchmark_root}`",
        "",
        "| Task | Files | Schema | Baselines | Ideas | Plans | Review MD | Review Sheet | Errors |",
        "|---|---|---|---:|---:|---:|---:|---|---|",
    ]

    for item in summaries:
        files = "OK" if item["complete_files"] else "MISS"
        schema = "PASS" if item["schema_validation_passed"] else "FAIL"
        sheet = "YES" if item["manual_review_sheet"] else "NO"
        errors = "; ".join(item["errors"]) if item["errors"] else ""
        md_lines.append(
            f"| `{item['task_name']}` | {files} | {schema} | "
            f"{item['baseline_cards']} | {item['focused_ideas']} | {item['experiment_plans']} | "
            f"{item['review_ready_ideas']} | {sheet} | {errors} |"
        )

    md_path = benchmark_root / "benchmark_summary.md"
    md_path.write_text("\n".join(md_lines))

    print("Saved:", json_path)
    print("Saved:", md_path)
    print()
    for item in summaries:
        status = "PASS" if item["schema_validation_passed"] else "FAIL"
        print(item["task_name"], status, f"ideas={item['focused_ideas']}", f"baselines={item['baseline_cards']}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
