#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

TASK_SPEC=""
OUTPUT_DIR=""
NO_NETWORK=1
STRICT=0
SOURCES="openalex"
PER_QUERY=3
MAX_BASELINES=12
SLEEP_SECONDS=0.4
PROXY_URL=""

usage() {
  cat >&2 <<'EOF'
Usage:
  bash focused_workflow/scripts/run_paper_evidence_v0_5.sh --task-spec <task.yaml> [options]

Options:
  --task-spec PATH       Required task specification YAML.
  --output-dir PATH      Optional output directory. Default is timestamped under outputs/.
  --network              Enable external paper retrieval APIs.
  --no-network           Disable network and only generate query plan + weak cards. Default.
  --strict               Fail if evidence is paperless or weak-only.
  --sources LIST         Comma-separated sources. Default: openalex.
  --per-query N          Results per source/query. Default: 3.
  --max-baselines N      Maximum baselines to query. Default: 12.
  --sleep N              Seconds to wait between API calls. Default: 0.4.
  --proxy URL            Optional HTTP/HTTPS proxy, e.g. http://127.0.0.1:7890.

Examples:
  bash focused_workflow/scripts/run_paper_evidence_v0_5.sh \
    --task-spec focused_workflow/tasks/benchmark_cv/05_iad_agent_workflow.yaml \
    --no-network

  bash focused_workflow/scripts/run_paper_evidence_v0_5.sh \
    --task-spec focused_workflow/tasks/benchmark_cv/05_iad_agent_workflow.yaml \
    --network --strict
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --task-spec)
      TASK_SPEC="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --network)
      NO_NETWORK=0
      shift
      ;;
    --no-network)
      NO_NETWORK=1
      shift
      ;;
    --strict)
      STRICT=1
      shift
      ;;
    --sources)
      SOURCES="$2"
      shift 2
      ;;
    --per-query)
      PER_QUERY="$2"
      shift 2
      ;;
    --max-baselines)
      MAX_BASELINES="$2"
      shift 2
      ;;
    --sleep)
      SLEEP_SECONDS="$2"
      shift 2
      ;;
    --proxy)
      PROXY_URL="$2"
      shift 2
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

if [ -z "$TASK_SPEC" ]; then
  echo "ERROR: --task-spec is required." >&2
  usage
  exit 1
fi

if [ ! -f "$TASK_SPEC" ]; then
  echo "ERROR: task spec not found: $TASK_SPEC" >&2
  exit 1
fi

if [ -z "$OUTPUT_DIR" ]; then
  task_name="$(basename "$TASK_SPEC" .yaml)"
  tag="$(date +%Y%m%d_%H%M%S)"
  OUTPUT_DIR="outputs/v05_paper_evidence_${task_name}_${tag}"
fi

if [ -e "$OUTPUT_DIR" ]; then
  echo "ERROR: output directory already exists: $OUTPUT_DIR" >&2
  echo "Use a new --output-dir to avoid overwriting previous results." >&2
  exit 1
fi

echo "== Paper Evidence Pipeline v0.5 =="
echo "Project root:  $PROJECT_ROOT"
echo "Task spec:     $TASK_SPEC"
echo "Output dir:    $OUTPUT_DIR"
echo "Network:       $([ "$NO_NETWORK" = "1" ] && echo disabled || echo enabled)"
echo "Sources:       $SOURCES"
echo "Per query:     $PER_QUERY"
echo "Max baselines: $MAX_BASELINES"
echo "Sleep:         $SLEEP_SECONDS"
echo "Proxy:         ${PROXY_URL:-none}"
echo

retrieve_args=(
  --task-spec "$TASK_SPEC"
  --output-dir "$OUTPUT_DIR"
  --sources "$SOURCES"
  --per-query "$PER_QUERY"
  --max-baselines "$MAX_BASELINES"
  --sleep "$SLEEP_SECONDS"
)

if [ "$NO_NETWORK" = "1" ]; then
  retrieve_args+=(--no-network)
fi

if [ -n "$PROXY_URL" ]; then
  retrieve_args+=(--proxy "$PROXY_URL")
fi

echo "Step 1/2: Retrieve paper evidence and build evidence cards"
python focused_workflow/scripts/retrieve_paper_evidence.py "${retrieve_args[@]}"

echo
echo "Step 2/2: Validate paper evidence"
validate_args=("$OUTPUT_DIR")
if [ "$STRICT" = "1" ]; then
  validate_args+=(--strict)
fi
python focused_workflow/scripts/validate_paper_evidence.py "${validate_args[@]}"

echo
echo "Done."
echo "Evidence context:"
echo "  $OUTPUT_DIR/paper_evidence/evidence_context.md"
echo "Chinese quality report:"
echo "  $OUTPUT_DIR/paper_evidence/evidence_quality_report_CN.md"
