import json
import sys
from pathlib import Path
from statistics import mean


SCORE_FIELDS = [
    "novelty_score",
    "feasibility_score",
    "expected_effectiveness_score",
    "excitement_score",
    "overall_score",
]


def main():
    if len(sys.argv) != 2:
        print("Usage: python focused_workflow/scripts/summarize_si2025_reviews.py <run_dir>")
        sys.exit(2)

    run_dir = Path(sys.argv[1])
    review_files = sorted(run_dir.glob("si2025_review_reviewer*.json"))

    if not review_files:
        raise FileNotFoundError("No reviewer files found: si2025_review_reviewer*.json")

    grouped = {}

    for review_file in review_files:
        reviews = json.loads(review_file.read_text())
        for row in reviews:
            title = row["title"]
            grouped.setdefault(title, {field: [] for field in SCORE_FIELDS})
            grouped[title].setdefault("review_files", []).append(review_file.name)

            for field in SCORE_FIELDS:
                value = row.get(field)
                if isinstance(value, (int, float)):
                    grouped[title][field].append(value)

    summary = []

    for title, scores in grouped.items():
        item = {
            "title": title,
            "num_reviews": len(scores["overall_score"]),
            "review_files": sorted(set(scores["review_files"])),
        }

        for field in SCORE_FIELDS:
            values = scores[field]
            item[field.replace("_score", "_mean")] = round(mean(values), 2) if values else None

        item["ranking_score"] = item["overall_mean"]
        summary.append(item)

    summary.sort(key=lambda x: x["ranking_score"], reverse=True)

    json_path = run_dir / "si2025_review_summary.json"
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    md_lines = [
        "# Si et al. 2025 Style Review Summary",
        "",
        "| Rank | Idea | Novelty | Feasibility | Effectiveness | Excitement | Overall | Reviews |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]

    for rank, item in enumerate(summary, start=1):
        md_lines.append(
            f"| {rank} | {item['title']} | "
            f"{item['novelty_mean']} | "
            f"{item['feasibility_mean']} | "
            f"{item['expected_effectiveness_mean']} | "
            f"{item['excitement_mean']} | "
            f"{item['overall_mean']} | "
            f"{item['num_reviews']} |"
        )

    md_lines.extend([
        "",
        "## Recommendation",
        "",
        f"Top ranked idea: **{summary[0]['title']}**",
        "",
        "Use the top-ranked idea as the main research contribution, and use the most feasible idea as the first implementation backbone.",
    ])

    md_path = run_dir / "si2025_review_summary.md"
    md_path.write_text("\n".join(md_lines))

    print("Saved:", json_path)
    print("Saved:", md_path)
    print()
    for rank, item in enumerate(summary, start=1):
        print(rank, item["title"], "overall =", item["overall_mean"])


if __name__ == "__main__":
    main()