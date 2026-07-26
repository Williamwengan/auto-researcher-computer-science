import json
import sys
from pathlib import Path


DIMENSIONS = [
    "novelty",
    "feasibility",
    "expected_effectiveness",
    "excitement",
    "overall",
]


def main():
    if len(sys.argv) != 2:
        print("Usage: python focused_workflow/scripts/make_si2025_review_sheet.py <run_dir>")
        sys.exit(2)

    run_dir = Path(sys.argv[1])
    review_dir = run_dir / "review_ready_ideas"

    if not review_dir.exists():
        raise FileNotFoundError(f"Missing review_ready_ideas directory: {review_dir}")

    ideas = sorted(review_dir.glob("idea_*.md"))

    rows = []
    for idea_path in ideas:
        text = idea_path.read_text()
        title = "Unknown"
        for line in text.splitlines():
            if line.startswith("# Idea"):
                title = line.strip("# ").strip()
                break

        row = {
            "idea_file": str(idea_path),
            "title": title,
        }

        for dim in DIMENSIONS:
            row[f"{dim}_score"] = None
            row[f"{dim}_rationale"] = ""

        rows.append(row)

    output_path = run_dir / "si2025_manual_review_sheet.json"
    output_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False))

    print("Saved:", output_path)
    print("Ideas:", len(rows))


if __name__ == "__main__":
    main()