#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8902}"

python 03_demo_video/demo_assets/start_demo_server.py \
  --host "${HOST}" \
  --port "${PORT}" \
  --strict-port
