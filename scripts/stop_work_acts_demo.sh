#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$ROOT_DIR/data"
RUN_DIR="$DATA_DIR/run"
PRINT_PORT="${PRINT_PORT:-4000}"
NOCO_PORT="${NOCO_PORT:-1233}"
RUN_DIR_PRINT_PID="$RUN_DIR/print_artifacts_server.pid"
RUN_DIR_NOCO_PID="$RUN_DIR/nocodb.pid"

require_cmd() { command -v "$1" >/dev/null 2>&1 || { echo "Missing command: $1" >&2; exit 1; }; }
pid_is_running() { [[ -f "$1" ]] && kill -0 "$(cat "$1")" 2>/dev/null; }
port_busy() { lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1; }

stop_pidfile() {
  local label="$1"
  local pidfile="$2"
  if [[ ! -f "$pidfile" ]]; then
    echo "$label: pid file not found, skipping"
    return 0
  fi

  local pid
  pid="$(cat "$pidfile")"
  if ! kill -0 "$pid" 2>/dev/null; then
    echo "$label: pid $pid is not running, cleaning pid file"
    rm -f "$pidfile"
    return 0
  fi

  echo "$label: stopping pid $pid"
  kill "$pid" 2>/dev/null || true
  for _ in {1..10}; do
    if ! kill -0 "$pid" 2>/dev/null; then
      rm -f "$pidfile"
      echo "$label: stopped"
      return 0
    fi
    sleep 1
  done

  echo "$label: did not stop in time" >&2
  return 1
}

check_port_free() {
  local label="$1"
  local port="$2"
  if port_busy "$port"; then
    echo "$label: port $port is still busy" >&2
    lsof -nP -iTCP:"$port" -sTCP:LISTEN >&2 || true
    return 1
  fi
  echo "$label: port $port is free"
}

mkdir -p "$RUN_DIR"
require_cmd lsof

status=0

echo "[1/3] Stopping print server..."
stop_pidfile "Print server" "$RUN_DIR_PRINT_PID" || status=1

echo "[2/3] Stopping NocoDB..."
stop_pidfile "NocoDB" "$RUN_DIR_NOCO_PID" || status=1

echo "[3/3] Verifying ports are free..."
check_port_free "Print server" "$PRINT_PORT" || status=1
check_port_free "NocoDB" "$NOCO_PORT" || status=1

if [[ "$status" -ne 0 ]]; then
  echo "Demo stack stop finished with warnings." >&2
  exit 1
fi

echo "Work Acts demo stack stopped."