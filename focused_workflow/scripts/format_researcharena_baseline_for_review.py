import json
import sys
from pathlib import Path


def as_list_text(items):
    if not items:
        return "- Not specified"
    if isinstance(items, list):
        lines = []
        for item in items:
            if isinstance(item, dict):
                paper = item.get("paper", "Unknown paper")
                difference = item.get("difference", "")
                lines.append(f"- {paper}: {difference}")
            else:
                lines.append(f"- {item}")
        return "\n".join(lines)
    return str(items)


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python focused_workflow/scripts/format_researcharena_baseline_for_review.py "
            "<baseline_dir> <output_dir>"
        )
        sys.exit(2)

    baseline_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    output_dir.mkdir(parents=True, exist_ok=True)

    idea_path = baseline_dir / "idea.json"
    proposal_path = baseline_dir / "proposal.md"

    if not idea_path.exists():
        raise FileNotFoundError(f"Missing {idea_path}")
    if not proposal_path.exists():
        raise FileNotFoundError(f"Missing {proposal_path}")

    idea = json.loads(idea_path.read_text())
    proposal = proposal_path.read_text()

    title = idea.get("title", "ResearchArena Baseline Idea")

    content = f"""# ResearchArena Baseline: {title}

## 1. Title

{title}

## 2. Problem Statement

This is the original ResearchArena baseline idea generated from the same research direction:
object-level physical property prediction from single 2D indoor scene images.

The target properties include density, Young's modulus, Poisson's ratio, hardness, and friction coefficient.

## 3. Motivation

{idea.get("motivation", "Not specified")}

## 4. Direct Baselines / Related Work

{as_list_text(idea.get("related_work"))}

## 5. Proposed Method

{idea.get("proposed_approach", "Not specified")}

## 6. Hypothesis

{idea.get("hypothesis", "Not specified")}

## 7. Evaluation Metrics and Success Criteria

{as_list_text(idea.get("success_criteria"))}

## 8. Compute Feasibility

{idea.get("compute_feasibility", "Not specified")}

## 9. Expected Contribution

{idea.get("expected_contribution", "Not specified")}

## 10. Full Original Proposal

The following content is copied from the original ResearchArena `proposal.md`.

---

{proposal}
"""

    output_path = output_dir / "researcharena_propertyset.md"
    output_path.write_text(content)

    print("Saved:", output_path)


if __name__ == "__main__":
    main()
    