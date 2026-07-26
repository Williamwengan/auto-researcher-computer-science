#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

TASK_DIR="${TASK_DIR:-focused_workflow/tasks/benchmark_cv}"
BENCHMARK_ROOT="${BENCHMARK_ROOT:-outputs/benchmark_cv_runs_$(date +%Y%m%d_%H%M%S)}"
DRY_RUN=0
ONLY_TASK=""

usage() {
  cat <<'EOF'
Usage:
  bash focused_workflow/scripts/run_benchmark_cv_tasks.sh [--dry-run] [--only TASK_FILE]

Options:
  --dry-run         Print planned commands without calling Codex.
  --only FILE      Run only one task file name, for example 02_open_vocabulary_segmentation.yaml.

Environment variables:
  TASK_DIR         Directory containing benchmark task YAML files.
  BENCHMARK_ROOT   Output root for all benchmark runs.

Examples:
  bash focused_workflow/scripts/run_benchmark_cv_tasks.sh --dry-run

  bash focused_workflow/scripts/run_benchmark_cv_tasks.sh \
    --only 02_open_vocabulary_segmentation.yaml
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --only)
      if [ "$#" -lt 2 ]; then
        echo "--only requires a task file name" >&2
        exit 2
      fi
      ONLY_TASK="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [ ! -d "$TASK_DIR" ]; then
  echo "Missing task directory: $TASK_DIR" >&2
  exit 1
fi

mapfile -t TASK_FILES < <(find "$TASK_DIR" -maxdepth 1 -type f -name '*.yaml' | sort)

if [ "${#TASK_FILES[@]}" -eq 0 ]; then
  echo "No task YAML files found in: $TASK_DIR" >&2
  exit 1
fi

if [ -n "$ONLY_TASK" ]; then
  FILTERED=()
  for task in "${TASK_FILES[@]}"; do
    if [ "$(basename "$task")" = "$ONLY_TASK" ]; then
      FILTERED+=("$task")
    fi
  done
  TASK_FILES=("${FILTERED[@]}")
  if [ "${#TASK_FILES[@]}" -eq 0 ]; then
    echo "Could not find task file named: $ONLY_TASK" >&2
    exit 1
  fi
fi

mkdir -p "$BENCHMARK_ROOT"

INDEX_MD="$BENCHMARK_ROOT/benchmark_runs_index.md"
INDEX_JSONL="$BENCHMARK_ROOT/benchmark_runs_index.jsonl"

cat > "$INDEX_MD" <<EOF
# Focused Workflow CV Benchmark Runs

Benchmark root:

\`\`\`text
$PROJECT_ROOT/$BENCHMARK_ROOT
\`\`\`

| # | Task | Status | Output Directory |
|---:|---|---|---|
EOF

: > "$INDEX_JSONL"

echo "== Focused Workflow CV Benchmark =="
echo "Project root:   $PROJECT_ROOT"
echo "Task dir:       $TASK_DIR"
echo "Benchmark root: $BENCHMARK_ROOT"
echo "Dry run:        $DRY_RUN"
echo "Tasks:          ${#TASK_FILES[@]}"
echo

for idx in "${!TASK_FILES[@]}"; do
  task_path="${TASK_FILES[$idx]}"
  task_name="$(basename "$task_path" .yaml)"
  run_dir="$BENCHMARK_ROOT/$task_name"
  status="planned"

  echo "[$((idx + 1))/${#TASK_FILES[@]}] $task_name"
  echo "  task: $task_path"
  echo "  run:  $run_dir"

  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  dry-run: skip Codex call"
  else
    status="running"
    TASK_SPEC="$task_path" RUN_DIR="$run_dir" bash focused_workflow/scripts/run_focused_workflow_v0_2.sh
    status="completed"
  fi

  printf '| %s | `%s` | %s | `%s` |\n' "$((idx + 1))" "$(basename "$task_path")" "$status" "$run_dir" >> "$INDEX_MD"
  python - "$idx" "$task_path" "$status" "$run_dir" >> "$INDEX_JSONL" <<'PY'
import json
import sys

idx, task_path, status, run_dir = sys.argv[1:5]
print(json.dumps({
    "index": int(idx) + 1,
    "task_path": task_path,
    "task_file": task_path.split("/")[-1],
    "status": status,
    "run_dir": run_dir,
}, ensure_ascii=False))
PY
  echo
done

echo "Benchmark index:"
echo "  $PROJECT_ROOT/$INDEX_MD"
echo "  $PROJECT_ROOT/$INDEX_JSONL"

if [ "$DRY_RUN" -eq 0 ]; then
  echo
  echo "You can summarize completed runs with:"
  echo "  python focused_workflow/scripts/summarize_benchmark_cv_runs.py \"$BENCHMARK_ROOT\""
fi
