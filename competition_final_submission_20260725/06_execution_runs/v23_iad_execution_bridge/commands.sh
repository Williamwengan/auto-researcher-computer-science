#!/usr/bin/env bash
set -euo pipefail

# Optional full data-subset preparation. Requires explicit MVTec root.
# python iad_mvp/scripts/prepare_mvtec_subset.py \
#   --mvtec_root Datasets/01_IAD/mvtec_anomaly_detection/mvtec_anomaly_detection \
#   --categories bottle \
#   --output iad_mvp/data/mvtec_split.json

python iad_mvp/scripts/prepare_iad_reference_manifest.py
python iad_mvp/scripts/build_reference_bank.py
python iad_mvp/scripts/run_iad_baselines.py
python iad_mvp/scripts/score_reference_consistency.py
python iad_mvp/scripts/evaluate_iad_agent.py
python focused_workflow/scripts/build_v23_iad_execution_bridge.py
