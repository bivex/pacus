#!/usr/bin/env bash
set -euo pipefail

unset PYTHONHOME PYTHONPATH

PORT="${1:-4000}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACTS_DIR="$ROOT_DIR/data/artifacts"

echo "Serving print artifacts from: $ARTIFACTS_DIR"
echo "URL: http://127.0.0.1:${PORT}"

exec python3 -m http.server "$PORT" --directory "$ARTIFACTS_DIR"