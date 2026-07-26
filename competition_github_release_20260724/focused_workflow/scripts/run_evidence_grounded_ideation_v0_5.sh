#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

TASK_SPEC=""
EVIDENCE_DIR=""
RUN_DIR=""
PROMPT_TEMPLATE="focused_workflow/prompts/evidence_grounded_ideation_prompt.md"
MODEL="${MODEL:-}"
RUN_CODEX=1
MAX_PAPERS=40
ABSTRACT_CHARS=900

usage() {
  cat >&2 <<'EOF'
Usage:
  bash focused_workflow/scripts/run_evidence_grounded_ideation_v0_5.sh \
    --task-spec <task.yaml> \
    --evidence-dir <paper_evidence_dir>

Options:
  --task-spec PATH       Required task specification YAML.
  --evidence-dir PATH    Required paper_evidence directory or its parent run directory.
  --run-dir PATH         Optional output directory. Default is timestamped under outputs/.
  --prompt-template PATH Optional prompt template.
  --model MODEL          Optional Codex model override, for example gpt-5.5.
  --max-papers N         Maximum paper records injected into prompt. Default: 40.
  --abstract-chars N     Maximum abstract characters per paper. Default: 900.
  --dry-run              Render prompt and copy inputs, but do not call Codex.

Examples:
  bash focused_workflow/scripts/run_evidence_grounded_ideation_v0_5.sh \
    --task-spec focused_workflow/tasks/benchmark_cv/05_iad_agent_workflow.yaml \
    --evidence-dir outputs/v05_paper_evidence_05_iad_agent_workflow_20260712_100802/paper_evidence
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --task-spec)
      TASK_SPEC="$2"
      shift 2
      ;;
    --evidence-dir)
      EVIDENCE_DIR="$2"
      shift 2
      ;;
    --run-dir)
      RUN_DIR="$2"
      shift 2
      ;;
    --prompt-template)
      PROMPT_TEMPLATE="$2"
      shift 2
      ;;
    --model)
      MODEL="$2"
      shift 2
      ;;
    --max-papers)
      MAX_PAPERS="$2"
      shift 2
      ;;
    --abstract-chars)
      ABSTRACT_CHARS="$2"
      shift 2
      ;;
    --dry-run)
      RUN_CODEX=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [ -z "$TASK_SPEC" ] || [ -z "$EVIDENCE_DIR" ]; then
  echo "ERROR: --task-spec and --evidence-dir are required." >&2
  usage
  exit 1
fi

if [ ! -f "$TASK_SPEC" ]; then
  echo "ERROR: task spec not found: $TASK_SPEC" >&2
  exit 1
fi

if [ ! -f "$PROMPT_TEMPLATE" ]; then
  echo "ERROR: prompt template not found: $PROMPT_TEMPLATE" >&2
  exit 1
fi

if [ -d "$EVIDENCE_DIR/paper_evidence" ]; then
  EVIDENCE_DIR="$EVIDENCE_DIR/paper_evidence"
fi

if [ ! -d "$EVIDENCE_DIR" ]; then
  echo "ERROR: evidence dir not found: $EVIDENCE_DIR" >&2
  exit 1
fi

for required in evidence_baseline_cards.jsonl papers.jsonl evidence_quality_summary.json; do
  if [ ! -f "$EVIDENCE_DIR/$required" ]; then
    echo "ERROR: missing evidence file: $EVIDENCE_DIR/$required" >&2
    exit 1
  fi
done

if [ -z "$RUN_DIR" ]; then
  task_name="$(basename "$TASK_SPEC" .yaml)"
  tag="$(date +%Y%m%d_%H%M%S)"
  RUN_DIR="outputs/v05_evidence_grounded_ideation_${task_name}_${tag}"
fi

if [ -e "$RUN_DIR" ]; then
  echo "ERROR: run directory already exists: $RUN_DIR" >&2
  echo "Use a new --run-dir to avoid overwriting previous results." >&2
  exit 1
fi

if [ -f "$HOME/.estelle_api_env" ]; then
  # shellcheck disable=SC1090
  source "$HOME/.estelle_api_env"
fi

if [ "$RUN_CODEX" = "1" ]; then
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
fi

mkdir -p "$RUN_DIR"

echo "== Evidence-Grounded Ideation v0.5 =="
echo "Project root:    $PROJECT_ROOT"
echo "Task spec:       $TASK_SPEC"
echo "Evidence dir:    $EVIDENCE_DIR"
echo "Run dir:         $RUN_DIR"
echo "Prompt template: $PROMPT_TEMPLATE"
echo "Run Codex:       $RUN_CODEX"
echo "Max papers:      $MAX_PAPERS"
echo "Abstract chars:  $ABSTRACT_CHARS"
echo

cp "$TASK_SPEC" "$RUN_DIR/task_spec.yaml"
cp "$EVIDENCE_DIR/evidence_baseline_cards.jsonl" "$RUN_DIR/evidence_baseline_cards.jsonl"
cp "$EVIDENCE_DIR/papers.jsonl" "$RUN_DIR/papers.jsonl"
cp "$EVIDENCE_DIR/evidence_quality_summary.json" "$RUN_DIR/evidence_quality_summary.json"
if [ -f "$EVIDENCE_DIR/evidence_context.md" ]; then
  cp "$EVIDENCE_DIR/evidence_context.md" "$RUN_DIR/evidence_context.md"
fi

echo "Step 1/7: Render evidence-grounded prompt"
python - "$TASK_SPEC" "$EVIDENCE_DIR/evidence_baseline_cards.jsonl" "$EVIDENCE_DIR/papers.jsonl" "$PROMPT_TEMPLATE" "$RUN_DIR/prompt.md" "$RUN_DIR/prompt_papers.jsonl" "$MAX_PAPERS" "$ABSTRACT_CHARS" <<'PY'
import json
import sys
from pathlib import Path

task_path = Path(sys.argv[1])
cards_path = Path(sys.argv[2])
papers_path = Path(sys.argv[3])
template_path = Path(sys.argv[4])
output_path = Path(sys.argv[5])
prompt_papers_path = Path(sys.argv[6])
max_papers = int(sys.argv[7])
abstract_chars = int(sys.argv[8])

cards = [json.loads(line) for line in cards_path.read_text(encoding="utf-8").splitlines() if line.strip()]
paper_rows = [json.loads(line) for line in papers_path.read_text(encoding="utf-8").splitlines() if line.strip()]
paper_by_id = {row.get("paper_id"): row for row in paper_rows}

referenced_ids = []
for card in cards:
    for paper in card.get("evidence_papers", []) or []:
        pid = paper.get("paper_id")
        if pid and pid not in referenced_ids:
            referenced_ids.append(pid)

selected = []
seen = set()
for pid in referenced_ids:
    paper = paper_by_id.get(pid)
    if paper and pid not in seen:
        selected.append(paper)
        seen.add(pid)

for paper in sorted(paper_rows, key=lambda x: x.get("relevance_score", 0), reverse=True):
    pid = paper.get("paper_id")
    if len(selected) >= max_papers:
        break
    if pid not in seen:
        selected.append(paper)
        seen.add(pid)

trimmed = []
for paper in selected[:max_papers]:
    row = {
        "paper_id": paper.get("paper_id", ""),
        "title": paper.get("title", ""),
        "year": paper.get("year"),
        "source": paper.get("source", ""),
        "url": paper.get("url", ""),
        "doi": paper.get("doi", ""),
        "baseline_tags": paper.get("baseline_tags", []),
        "task_relevance": paper.get("task_relevance", ""),
        "relevance_score": paper.get("relevance_score", 0),
        "matched_terms": paper.get("matched_terms", []),
        "abstract": (paper.get("abstract", "") or "")[:abstract_chars],
    }
    trimmed.append(row)

prompt_papers_path.write_text(
    "\n".join(json.dumps(row, ensure_ascii=False) for row in trimmed) + ("\n" if trimmed else ""),
    encoding="utf-8",
)

rendered = template_path.read_text(encoding="utf-8")
rendered = rendered.replace("{{TASK_SPEC_YAML}}", task_path.read_text(encoding="utf-8"))
rendered = rendered.replace("{{EVIDENCE_BASELINE_CARDS_JSONL}}", cards_path.read_text(encoding="utf-8"))
rendered = rendered.replace("{{PAPER_EVIDENCE_JSONL}}", prompt_papers_path.read_text(encoding="utf-8"))

output_path.write_text(rendered, encoding="utf-8")
print("Rendered prompt saved to:", output_path)
print("Prompt length:", len(rendered))
print("Prompt papers:", len(trimmed))
PY

if [ "$RUN_CODEX" = "0" ]; then
  echo
  echo "Dry run complete. Prompt rendered only:"
  echo "  $RUN_DIR/prompt.md"
  exit 0
fi

echo
echo "Step 2/6: Run Codex evidence-grounded ideation"
codex_args=(
  exec
  --skip-git-repo-check
  --dangerously-bypass-approvals-and-sandbox
)
if [ -n "$MODEL" ]; then
  codex_args+=(--model "$MODEL")
fi
(
  cd "$RUN_DIR"
  CODEX_HOME="$CODEX_HOME" codex "${codex_args[@]}" \
    "Read prompt.md and execute it. Save baseline_cards.jsonl, focused_ideas.json, and experiment_plan.json into the current working directory."
)

echo
echo "Step 3/7: Validate generated JSON files"
python focused_workflow/scripts/validate_outputs.py "$RUN_DIR"

echo
echo "Step 4/7: Validate evidence grounding"
python focused_workflow/scripts/validate_evidence_grounding.py "$RUN_DIR"

echo
echo "Step 5/7: Format ideas for review"
python focused_workflow/scripts/format_ideas_for_review.py "$RUN_DIR"

echo
echo "Step 6/7: Rule-based quality scoring"
python focused_workflow/scripts/evaluate_idea_quality.py "$RUN_DIR" --overwrite

echo
echo "Step 7/7: Create manual review sheet"
python focused_workflow/scripts/make_si2025_review_sheet.py "$RUN_DIR"

echo
echo "Done."
echo "Run dir:"
echo "  $PROJECT_ROOT/$RUN_DIR"
echo
echo "Key outputs:"
echo "  $RUN_DIR/focused_ideas.json"
echo "  $RUN_DIR/evidence_grounding_report_CN.md"
echo "  $RUN_DIR/idea_quality_scores.json"
echo "  $RUN_DIR/review_ready_ideas"
