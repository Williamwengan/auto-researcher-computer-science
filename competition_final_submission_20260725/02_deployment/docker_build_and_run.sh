#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

IMAGE_NAME="${IMAGE_NAME:-ai4s-research-agent:competition}"
PORT="${PORT:-8902}"

echo "[1/2] Building Docker image: ${IMAGE_NAME}"
docker build -t "${IMAGE_NAME}" .

echo "[2/2] Running demo server on port ${PORT}"
docker run --rm -p "${PORT}:8902" "${IMAGE_NAME}"
