#!/usr/bin/env bash
set -euo pipefail

unset PYTHONHOME PYTHONPATH

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${1:-5000}"

cd "$ROOT_DIR"

echo "Starting Pacus web UI..."
echo "URL: http://127.0.0.1:${PORT}"

exec python3 app.py --port "$PORT"
