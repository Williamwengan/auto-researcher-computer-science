import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


REQUIRED_FIELDS = [
    "idea_file",
    "title",
    "novelty_score",
    "novelty_rationale",
    "feasibility_score",
    "feasibility_rationale",
    "expected_effectiveness_score",
    "expected_effectiveness_rationale",
    "excitement_score",
    "excitement_rationale",
    "overall_score",
    "overall_rationale",
]

SCORE_FIELDS = [
    "novelty_score",
    "feasibility_score",
    "expected_effectiveness_score",
    "excitement_score",
    "overall_score",
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def extract_title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped.lstrip("#").strip()
    return fallback


def build_idea_blocks(idea_files):
    blocks = []
    metadata = []

    for index, idea_path in enumerate(idea_files, start=1):
        text = idea_path.read_text()
        title = extract_title(text, f"Idea {index}")
        metadata.append({"idea_file": str(idea_path), "title": title})
        blocks.append(
            "\n".join(
                [
                    f"### Idea {index}",
                    "",
                    f"Idea file: {idea_path}",
                    f"Title: {title}",
                    "",
                    "```markdown",
                    text,
                    "```",
                ]
            )
        )

    return "\n\n".join(blocks), metadata


def render_prompt(run_dir: Path, output_file: str, review_dir: Path) -> Path:
    root = project_root()
    rubric_path = root / "focused_workflow/evaluation/si2025_review_rubric.yaml"
    template_path = root / "focused_workflow/prompts/si2025_llm_reviewer_prompt.md"

    if not rubric_path.exists():
        raise FileNotFoundError(f"Missing rubric file: {rubric_path}")
    if not template_path.exists():
        raise FileNotFoundError(f"Missing reviewer prompt template: {template_path}")
    if not review_dir.exists():
        raise FileNotFoundError(f"Missing review-ready ideas directory: {review_dir}")

    idea_files = sorted(review_dir.glob("idea_*.md"))
    if not idea_files:
        raise FileNotFoundError(f"No idea_*.md files found in {review_dir}")

    idea_blocks, metadata = build_idea_blocks(idea_files)

    prompt = template_path.read_text()
    prompt = prompt.replace("{{RUBRIC_YAML}}", rubric_path.read_text())
    prompt = prompt.replace("{{OUTPUT_FILE}}", output_file)
    prompt = prompt.replace("{{IDEA_BLOCKS}}", idea_blocks)

    prompt_path = run_dir / "si2025_llm_reviewer_prompt.rendered.md"
    prompt_path.write_text(prompt)

    metadata_path = run_dir / "si2025_llm_reviewer_ideas.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False))

    return prompt_path


def validate_review_file(path: Path, expected_count: int):
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise TypeError("LLM review output must be a JSON list")
    if len(data) != expected_count:
        raise ValueError(f"Expected {expected_count} reviews, got {len(data)}")

    errors = []
    for index, row in enumerate(data, start=1):
        if not isinstance(row, dict):
            errors.append(f"item {index}: should be an object")
            continue

        for field in REQUIRED_FIELDS:
            if field not in row:
                errors.append(f"item {index}: missing field `{field}`")
                continue
            value = row[field]
            if value is None:
                errors.append(f"item {index}: field `{field}` is null")
            elif isinstance(value, str) and not value.strip():
                errors.append(f"item {index}: field `{field}` is empty")

        for field in SCORE_FIELDS:
            value = row.get(field)
            if not isinstance(value, int):
                errors.append(f"item {index}: field `{field}` should be an integer")
            elif value < 1 or value > 10:
                errors.append(f"item {index}: field `{field}` should be between 1 and 10")

    if errors:
        raise ValueError("\n".join(errors))

    return data


def run_codex(run_dir: Path, prompt_path: Path, output_file: str):
    codex = shutil.which("codex")
    if not codex:
        raise FileNotFoundError("Cannot find `codex` in PATH. Run: source ~/.estelle_api_env")

    env = os.environ.copy()
    env.setdefault("CODEX_HOME", str(Path.home() / ".codex-estelle"))

    if not env.get("ESTELLE_API_KEY"):
        raise RuntimeError("ESTELLE_API_KEY is empty. Run: source ~/.estelle_api_env")

    prompt_name = prompt_path.name
    command = [
        codex,
        "exec",
        "--skip-git-repo-check",
        "--dangerously-bypass-approvals-and-sandbox",
        f"Read {prompt_name} and execute it. Save the required JSON file as {output_file}.",
    ]

    subprocess.run(command, cwd=run_dir, env=env, check=True)


def main():
    parser = argparse.ArgumentParser(
        description="Score review-ready ideas with an LLM reviewer using the adapted Si et al. 2025 rubric."
    )
    parser.add_argument("run_dir", help="Focused workflow output directory")
    parser.add_argument(
        "--review-dir",
        default=None,
        help="Directory containing idea_*.md files. Default: <run_dir>/review_ready_ideas",
    )
    parser.add_argument(
        "--output",
        default="si2025_review_llm_reviewer01.json",
        help="Output JSON filename inside run_dir",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only render the reviewer prompt; do not call Codex.",
    )
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    review_dir = Path(args.review_dir).resolve() if args.review_dir else run_dir / "review_ready_ideas"
    output_path = run_dir / args.output

    if not run_dir.exists():
        raise FileNotFoundError(f"Missing run_dir: {run_dir}")

    prompt_path = render_prompt(run_dir, args.output, review_dir)
    idea_count = len(sorted(review_dir.glob("idea_*.md")))

    print("Rendered LLM reviewer prompt:", prompt_path)
    print("Ideas to review:", idea_count)

    if args.dry_run:
        print("Dry run only. No API call was made.")
        return

    run_codex(run_dir, prompt_path, args.output)

    if not output_path.exists():
        raise FileNotFoundError(f"Codex did not create expected output: {output_path}")

    reviews = validate_review_file(output_path, idea_count)
    print("Saved:", output_path)
    for row in reviews:
        print(row["title"], "overall =", row["overall_score"])


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
