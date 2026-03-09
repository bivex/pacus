#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB_PATH="${DB_PATH:-$ROOT_DIR/data/sqlite/work_acts_demo.sqlite}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Missing command: python3" >&2
  exit 1
fi

if ! command -v sqlite3 >/dev/null 2>&1; then
  echo "Missing command: sqlite3" >&2
  exit 1
fi

if [[ ! -f "$DB_PATH" ]]; then
  echo "SQLite database not found: $DB_PATH" >&2
  exit 1
fi

python3 "$ROOT_DIR/scripts/import_inbox_work_acts.py" --db "$DB_PATH" "$@"

echo
echo "Inbox summary:"
sqlite3 -header -column "$DB_PATH" <<'SQL'
SELECT import_status, COUNT(*) AS row_count
FROM integration_inbox_work_act
GROUP BY import_status
ORDER BY import_status;
SQL

echo
echo "Latest inbox rows:"
sqlite3 -header -column "$DB_PATH" <<'SQL'
SELECT id, source_system, external_document_id, external_version, import_status, imported_act_id, substr(coalesce(last_error, ''), 1, 80) AS last_error
FROM integration_inbox_work_act
ORDER BY received_at DESC, id DESC
LIMIT 10;
SQL