import json
import sys
from pathlib import Path


SCHEMA_DIR = Path("focused_workflow/schemas")


def load_json(path):
    return json.loads(path.read_text())


def load_schema(name):
    return load_json(SCHEMA_DIR / name)


def adapt_idea_schema_for_run(schema, run_dir):
    """Keep old generated runs valid while enforcing new fields for v0.3 runs."""
    task_path = run_dir / "task_spec.yaml"
    if task_path.exists() and "minimal_new_module" in task_path.read_text():
        return schema

    legacy_schema = json.loads(json.dumps(schema))
    for field in ["minimal_new_module", "mvp_artifacts"]:
        if field in legacy_schema.get("required", []):
            legacy_schema["required"].remove(field)
        if field in legacy_schema.get("dict_fields", []):
            legacy_schema["dict_fields"].remove(field)
        legacy_schema.get("nested_required", {}).pop(field, None)
        legacy_schema.get("nested_list_fields", {}).pop(field, None)
        legacy_schema.get("nested_string_fields", {}).pop(field, None)
    return legacy_schema


def validate_item(item, schema, label):
    errors = []

    for field in schema["required"]:
        if field not in item:
            errors.append(f"{label}: missing field `{field}`")
            continue

        value = item[field]

        if value is None:
            errors.append(f"{label}: field `{field}` is null")
        elif isinstance(value, str) and not value.strip():
            errors.append(f"{label}: field `{field}` is empty")
        elif isinstance(value, list) and len(value) == 0:
            errors.append(f"{label}: field `{field}` is an empty list")

    for field in schema.get("string_fields", []):
        if field in item and not isinstance(item[field], str):
            errors.append(f"{label}: field `{field}` should be string")

    for field in schema.get("list_fields", []):
        if field in item and not isinstance(item[field], list):
            errors.append(f"{label}: field `{field}` should be list")

    for field in schema.get("dict_fields", []):
        if field in item and not isinstance(item[field], dict):
            errors.append(f"{label}: field `{field}` should be object")

    for parent, fields in schema.get("nested_required", {}).items():
        value = item.get(parent)
        if value is None:
            continue
        if not isinstance(value, dict):
            continue
        for field in fields:
            if field not in value:
                errors.append(f"{label}: field `{parent}.{field}` is missing")
                continue
            nested_value = value[field]
            if nested_value is None:
                errors.append(f"{label}: field `{parent}.{field}` is null")
            elif isinstance(nested_value, str) and not nested_value.strip():
                errors.append(f"{label}: field `{parent}.{field}` is empty")
            elif isinstance(nested_value, list) and len(nested_value) == 0:
                errors.append(f"{label}: field `{parent}.{field}` is an empty list")

    for parent, fields in schema.get("nested_list_fields", {}).items():
        value = item.get(parent)
        if not isinstance(value, dict):
            continue
        for field in fields:
            if field in value and not isinstance(value[field], list):
                errors.append(f"{label}: field `{parent}.{field}` should be list")

    for parent, fields in schema.get("nested_string_fields", {}).items():
        value = item.get(parent)
        if not isinstance(value, dict):
            continue
        for field in fields:
            if field in value and not isinstance(value[field], str):
                errors.append(f"{label}: field `{parent}.{field}` should be string")

    return errors


def main():
    if len(sys.argv) != 2:
        print("Usage: python focused_workflow/scripts/validate_outputs.py <run_dir>")
        sys.exit(2)

    run_dir = Path(sys.argv[1])

    baseline_schema = load_schema("baseline_card.schema.json")
    idea_schema = adapt_idea_schema_for_run(load_schema("focused_idea.schema.json"), run_dir)
    plan_schema = load_schema("experiment_plan.schema.json")

    baseline_path = run_dir / "baseline_cards.jsonl"
    ideas_path = run_dir / "focused_ideas.json"
    plans_path = run_dir / "experiment_plan.json"

    errors = []

    if not baseline_path.exists():
        errors.append("missing baseline_cards.jsonl")
        baseline_cards = []
    else:
        baseline_cards = []
        for idx, line in enumerate(baseline_path.read_text().splitlines(), start=1):
            if not line.strip():
                continue
            try:
                card = json.loads(line)
                baseline_cards.append(card)
                errors.extend(validate_item(card, baseline_schema, f"baseline card line {idx}"))
            except json.JSONDecodeError as exc:
                errors.append(f"baseline_cards.jsonl line {idx}: invalid JSON: {exc}")

    if not ideas_path.exists():
        errors.append("missing focused_ideas.json")
        ideas = []
    else:
        ideas = load_json(ideas_path)
        if not isinstance(ideas, list):
            errors.append("focused_ideas.json should be a list")
            ideas = []
        for idx, idea in enumerate(ideas, start=1):
            errors.extend(validate_item(idea, idea_schema, f"idea item {idx}"))

    if not plans_path.exists():
        errors.append("missing experiment_plan.json")
        plans = []
    else:
        plans = load_json(plans_path)
        if not isinstance(plans, list):
            errors.append("experiment_plan.json should be a list")
            plans = []
        for idx, plan in enumerate(plans, start=1):
            errors.extend(validate_item(plan, plan_schema, f"experiment plan item {idx}"))

    idea_titles = {idea.get("title") for idea in ideas if isinstance(idea, dict)}
    plan_titles = {plan.get("idea_title") for plan in plans if isinstance(plan, dict)}

    for title in sorted(idea_titles - plan_titles):
        errors.append(f"idea has no matching experiment plan: {title}")

    for title in sorted(plan_titles - idea_titles):
        errors.append(f"experiment plan has no matching idea: {title}")

    print("Validation summary")
    print("------------------")
    print("baseline_cards:", len(baseline_cards))
    print("focused_ideas:", len(ideas))
    print("experiment_plans:", len(plans))

    if errors:
        print("\nFAILED")
        for err in errors:
            print("-", err)
        sys.exit(1)

    print("\nPASSED")


if __name__ == "__main__":
    main()
