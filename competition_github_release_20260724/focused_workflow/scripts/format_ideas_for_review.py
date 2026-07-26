import json
import sys
from pathlib import Path

import yaml


def as_list_text(value):
    if value is None:
        return "- Not specified"
    if isinstance(value, list):
        if not value:
            return "- Not specified"
        return "\n".join(f"- {item}" for item in value)
    if isinstance(value, str):
        return value.strip() or "- Not specified"
    return str(value)


def as_module_text(value):
    if not isinstance(value, dict) or not value:
        return "Not specified"

    lines = []
    for key in [
        "name",
        "input",
        "output",
        "algorithm_steps",
        "training_or_inference_objective",
        "why_baseline_cannot_do_this",
    ]:
        if key not in value:
            continue
        label = key.replace("_", " ")
        nested = value[key]
        if isinstance(nested, list):
            nested_text = as_list_text(nested)
            lines.append(f"**{label}:**\n\n{nested_text}")
        else:
            lines.append(f"**{label}:** {nested}")
    return "\n\n".join(lines) if lines else "Not specified"


def as_artifacts_text(value):
    if not isinstance(value, dict) or not value:
        return "Not specified"

    labels = [
        ("required_scripts", "Required scripts"),
        ("required_data_files", "Required data files"),
        ("expected_tables", "Expected tables"),
        ("expected_figures", "Expected figures"),
        ("success_threshold", "Success threshold"),
    ]
    lines = []
    for key, label in labels:
        if key not in value:
            continue
        nested = value[key]
        if isinstance(nested, list):
            lines.append(f"**{label}:**\n\n{as_list_text(nested)}")
        else:
            lines.append(f"**{label}:** {nested}")
    return "\n\n".join(lines) if lines else "Not specified"


def find_plan_for_idea(plans, title):
    for plan in plans:
        if plan.get("idea_title") == title:
            return plan
    return {}


def load_task_context(run_dir):
    task_path = run_dir / "task_spec.yaml"
    if not task_path.exists():
        return {
            "focus_area": "the specified research task",
            "research_goal": "Not specified",
            "input_type": "Not specified",
            "output_format": "Not specified",
            "required_outputs": [],
        }

    task = yaml.safe_load(task_path.read_text()) or {}
    output = task.get("output", {}) or {}
    input_spec = task.get("input", {}) or {}
    return {
        "focus_area": task.get("focus_area", "the specified research task"),
        "research_goal": task.get("research_goal", "Not specified"),
        "input_type": input_spec.get("type", "Not specified"),
        "output_format": output.get("format", "Not specified"),
        "required_outputs": output.get("required_fields", []),
    }


def render_idea(index, idea, plan, task_context):
    title = idea.get("title", f"Idea {index}")
    focus_area = task_context["focus_area"]
    research_goal = task_context["research_goal"]
    input_type = task_context["input_type"]
    output_format = task_context["output_format"]
    required_outputs = as_list_text(task_context["required_outputs"])

    content = f"""# Idea {index}: {title}

## 1. Title

{title}

## 2. Problem Statement

The target problem is to generate a focused research idea for:

{focus_area}

Research goal:

{research_goal}

Expected input type:

{input_type}

Expected output format:

{output_format}

Required output fields:

{required_outputs}

## 3. Motivation

{idea.get("why_it_may_work", "Not specified")}

## 4. Direct Baselines

{as_list_text(idea.get("direct_baselines"))}

## 5. Transfer Baselines

{as_list_text(idea.get("transfer_baselines"))}

## 6. Borrowed Components

{as_list_text(idea.get("borrowed_components"))}

## 7. Proposed Method

{idea.get("new_component", "Not specified")}

## 8. Datasets

{as_list_text(idea.get("datasets"))}

## 9. Evaluation Metrics

{as_list_text(idea.get("metrics"))}

## 10. Step-by-step Experiment Plan

{as_list_text(plan.get("implementation_steps") or idea.get("implementation_plan"))}

## 11. Data Preparation

{as_list_text(plan.get("data_preparation"))}

## 12. Baselines to Compare

{as_list_text(plan.get("baseline_to_compare"))}

## 13. Ablation Studies

{as_list_text(plan.get("ablation_studies") or idea.get("ablations"))}

## 14. Success Criteria

{as_list_text(plan.get("success_criteria"))}

## 15. Risks

{as_list_text(idea.get("risks"))}

## 16. Failure Cases / Failure Criteria

{as_list_text(plan.get("failure_cases") or idea.get("failure_criteria"))}

## 17. Expected Outputs

{as_list_text(idea.get("expected_outputs"))}

## 18. Minimal New Module

{as_module_text(idea.get("minimal_new_module"))}

## 19. MVP Artifacts

{as_artifacts_text(idea.get("mvp_artifacts"))}

## 20. Estimated Compute

{plan.get("estimated_compute", "Not specified")}

## 21. Estimated Timeline

{plan.get("estimated_timeline", "Not specified")}

## 22. Fallback Plan

If the full idea is too difficult to implement, start with the simplest baseline-grounded version:
reuse the strongest direct baseline, add only the proposed lightweight component, and evaluate it on the clearest metrics listed above. If the new component fails, keep the baseline reproduction, error analysis, and failure-case taxonomy as the fallback research output.

"""
    return content


def main():
    if len(sys.argv) != 2:
        print("Usage: python focused_workflow/scripts/format_ideas_for_review.py <run_dir>")
        sys.exit(2)

    run_dir = Path(sys.argv[1])
    ideas_path = run_dir / "focused_ideas.json"
    plans_path = run_dir / "experiment_plan.json"

    if not ideas_path.exists():
        raise FileNotFoundError(f"Missing {ideas_path}")
    if not plans_path.exists():
        raise FileNotFoundError(f"Missing {plans_path}")

    ideas = json.loads(ideas_path.read_text())
    plans = json.loads(plans_path.read_text())
    task_context = load_task_context(run_dir)

    output_dir = run_dir / "review_ready_ideas"
    output_dir.mkdir(exist_ok=True)

    for index, idea in enumerate(ideas, start=1):
        title = idea.get("title", f"Idea {index}")
        plan = find_plan_for_idea(plans, title)
        content = render_idea(index, idea, plan, task_context)
        output_path = output_dir / f"idea_{index:02d}.md"
        output_path.write_text(content)
        print("Saved:", output_path)

    print("Done.")
    print("Review-ready ideas:", output_dir)


if __name__ == "__main__":
    main()
