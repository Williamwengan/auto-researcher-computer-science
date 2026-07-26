#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <run_dir>" >&2
  echo "Environment toggles:" >&2
  echo "  RUN_MULTI_JUDGE=1            Run multi_llm_judge.py" >&2
  echo "  MULTI_JUDGE_DRY_RUN=1        Render multi-judge prompts only" >&2
  echo "  RUN_REPAIR=1                 Run repair_low_quality_ideas.py" >&2
  echo "  REPAIR_DRY_RUN=1             Render repair prompt only" >&2
  echo "  REPAIR_MIN_SCORE=88          Repair threshold" >&2
  exit 1
fi

RUN_DIR="$1"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "== Idea Quality Pipeline v0.4 =="
echo "Run dir: $RUN_DIR"
echo

echo "Step 1/5: Validate outputs"
python focused_workflow/scripts/validate_outputs.py "$RUN_DIR"

echo
echo "Step 2/5: Format review-ready ideas"
python focused_workflow/scripts/format_ideas_for_review.py "$RUN_DIR"

echo
echo "Step 3/5: Rule-based quality scoring"
python focused_workflow/scripts/evaluate_idea_quality.py "$RUN_DIR" --overwrite

if [ "${RUN_MULTI_JUDGE:-0}" = "1" ]; then
  echo
  echo "Step 4/5: Multi-LLM judge"
  if [ "${MULTI_JUDGE_DRY_RUN:-1}" = "1" ]; then
    python focused_workflow/scripts/multi_llm_judge.py "$RUN_DIR" --dry-run
  else
    python focused_workflow/scripts/multi_llm_judge.py "$RUN_DIR"
  fi
else
  echo
  echo "Step 4/5: Multi-LLM judge skipped. Set RUN_MULTI_JUDGE=1 to enable."
fi

if [ "${RUN_REPAIR:-0}" = "1" ]; then
  echo
  echo "Step 5/5: Critic-repair"
  REPAIR_ARGS=("$RUN_DIR" --min-score "${REPAIR_MIN_SCORE:-88}")
  if [ "${REPAIR_DRY_RUN:-1}" = "1" ]; then
    REPAIR_ARGS+=(--dry-run)
  fi
  python focused_workflow/scripts/repair_low_quality_ideas.py "${REPAIR_ARGS[@]}"
else
  echo
  echo "Step 5/5: Critic-repair skipped. Set RUN_REPAIR=1 to enable."
fi

echo
echo "Done."
