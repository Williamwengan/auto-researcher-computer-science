#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

TASK_SPEC="${TASK_SPEC:-focused_workflow/tasks/task_spec.yaml}"
PROMPT_TEMPLATE="${PROMPT_TEMPLATE:-focused_workflow/prompts/focused_ideation_prompt.md}"
RENDERED_PROMPT="${RENDERED_PROMPT:-focused_workflow/prompts/rendered_focused_ideation_prompt.md}"
RUN_DIR="${RUN_DIR:-outputs/focused_workflow_v0_2_$(date +%Y%m%d_%H%M%S)}"

echo "== Focused Workflow v0.2 =="
echo "Project root: $PROJECT_ROOT"
echo "Task spec:    $TASK_SPEC"
echo "Run dir:      $RUN_DIR"
echo

if [ ! -f "$TASK_SPEC" ]; then
  echo "Missing task spec: $TASK_SPEC" >&2
  exit 1
fi

if [ ! -f "$PROMPT_TEMPLATE" ]; then
  echo "Missing prompt template: $PROMPT_TEMPLATE" >&2
  exit 1
fi

if [ -f "$HOME/.estelle_api_env" ]; then
  # shellcheck disable=SC1090
  source "$HOME/.estelle_api_env"
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "Cannot find codex in PATH. Please source ~/.estelle_api_env or add the Codex binary directory to PATH." >&2
  exit 1
fi

if [ -z "${CODEX_HOME:-}" ]; then
  export CODEX_HOME="$HOME/.codex-estelle"
fi

if [ -z "${ESTELLE_API_KEY:-}" ]; then
  echo "ESTELLE_API_KEY is empty. Please run: source ~/.estelle_api_env" >&2
  exit 1
fi

echo "Step 1/6: Render prompt"
python - "$TASK_SPEC" "$PROMPT_TEMPLATE" "$RENDERED_PROMPT" <<'PY'
import sys
from pathlib import Path

task_path = Path(sys.argv[1])
prompt_path = Path(sys.argv[2])
output_path = Path(sys.argv[3])

task_yaml = task_path.read_text()
prompt_template = prompt_path.read_text()
rendered_prompt = prompt_template.replace("{{TASK_SPEC_YAML}}", task_yaml)

output_path.write_text(rendered_prompt)

print("Rendered prompt saved to:", output_path)
print("Prompt length:", len(rendered_prompt))
PY

mkdir -p "$RUN_DIR"
cp "$RENDERED_PROMPT" "$RUN_DIR/prompt.md"
cp "$TASK_SPEC" "$RUN_DIR/task_spec.yaml"

echo
echo "Step 2/6: Run Codex ideation"
(
  cd "$RUN_DIR"
  CODEX_HOME="$CODEX_HOME" codex exec \
    --skip-git-repo-check \
    --dangerously-bypass-approvals-and-sandbox \
    "Read prompt.md and execute it. Save all required outputs into the current working directory."
)

echo
echo "Step 3/6: Validate generated JSON files"
python focused_workflow/scripts/validate_outputs.py "$RUN_DIR"
python - "$RUN_DIR" <<'PY'
import json
import sys
from pathlib import Path

run_dir = Path(sys.argv[1])
required = [
    "baseline_cards.jsonl",
    "focused_ideas.json",
    "experiment_plan.json",
]

for name in required:
    path = run_dir / name
    if not path.exists():
        raise FileNotFoundError(f"Missing required output: {path}")

ideas = json.loads((run_dir / "focused_ideas.json").read_text())
plans = json.loads((run_dir / "experiment_plan.json").read_text())

if not isinstance(ideas, list):
    raise TypeError("focused_ideas.json must be a JSON list")
if not isinstance(plans, list):
    raise TypeError("experiment_plan.json must be a JSON list")

cards = []
for idx, line in enumerate((run_dir / "baseline_cards.jsonl").read_text().splitlines(), start=1):
    if not line.strip():
        continue
    try:
        cards.append(json.loads(line))
    except json.JSONDecodeError as exc:
        raise ValueError(f"baseline_cards.jsonl line {idx} is invalid JSON: {exc}") from exc

print("baseline_cards.jsonl OK items:", len(cards))
print("focused_ideas.json OK items:", len(ideas))
print("experiment_plan.json OK items:", len(plans))
PY

echo
echo "Step 4/6: Format ideas for Si et al. style review"
python focused_workflow/scripts/format_ideas_for_review.py "$RUN_DIR"

echo
echo "Step 5/6: Create manual review sheet"
python focused_workflow/scripts/make_si2025_review_sheet.py "$RUN_DIR"

echo
echo "Step 6/6: Done"
echo
echo "Outputs:"
echo "  $PROJECT_ROOT/$RUN_DIR"
echo
echo "Next manual review step:"
echo "  cp \"$PROJECT_ROOT/$RUN_DIR/si2025_manual_review_sheet.json\" \"$PROJECT_ROOT/$RUN_DIR/si2025_review_reviewer01.json\""
echo "  nano \"$PROJECT_ROOT/$RUN_DIR/si2025_review_reviewer01.json\""
echo
echo "After reviewer scores are filled:"
echo "  python focused_workflow/scripts/summarize_si2025_reviews.py \"$RUN_DIR\""
