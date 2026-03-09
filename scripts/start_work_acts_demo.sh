#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$ROOT_DIR/data"
RUN_DIR="$DATA_DIR/run"
LOG_DIR="$DATA_DIR/logs"
SQLITE_DIR="$DATA_DIR/sqlite"
SQLITE_DB_PATH="${SQLITE_DB_PATH:-$SQLITE_DIR/work_acts_demo.sqlite}"
SCHEMA_SQL="$ROOT_DIR/db/sqlite/work_acts_schema.sql"
SEED_SQL="$ROOT_DIR/db/sqlite/work_acts_seed_demo.sql"
PRINT_PORT="${PRINT_PORT:-4000}"
NOCO_PORT="${NOCO_PORT:-1233}"
NOCO_HOST="${NOCO_HOST:-127.0.0.1}"
NOCO_BASE_URL="http://${NOCO_HOST}:${NOCO_PORT}"
NC_TOOL_DIR="${NC_TOOL_DIR:-$DATA_DIR/nocodb-meta}"
NC_ADMIN_EMAIL="${NC_ADMIN_EMAIL:-admin@local.test}"
NC_ADMIN_PASS="${NC_ADMIN_PASS:-Admin123!}"
NC_AUTH_JWT_SECRET="${NC_AUTH_JWT_SECRET:-work-acts-demo-jwt-secret-2026}"
NOCO_BASE_TITLE="${NOCO_BASE_TITLE:-Work Acts Demo}"
NOCO_SOURCE_ALIAS="${NOCO_SOURCE_ALIAS:-Work Acts Demo DB}"
PRINT_BASE_URL="http://127.0.0.1:${PRINT_PORT}/"
RUN_DIR_PRINT_PID="$RUN_DIR/print_artifacts_server.pid"
RUN_DIR_NOCO_PID="$RUN_DIR/nocodb.pid"
PRINT_LOG="$LOG_DIR/print_artifacts_server.log"
NOCO_LOG="$LOG_DIR/nocodb.log"
BOOTSTRAP_JSON="$RUN_DIR/work_acts_demo_bootstrap.json"

require_cmd() { command -v "$1" >/dev/null 2>&1 || { echo "Missing command: $1" >&2; exit 1; }; }
pid_is_running() { [[ -f "$1" ]] && kill -0 "$(cat "$1")" 2>/dev/null; }
port_busy() { lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1; }

wait_for_url() {
  python3 - "$1" "$2" <<'PY'
import sys, time, urllib.request
url, needle = sys.argv[1], sys.argv[2]
for _ in range(60):
    try:
        with urllib.request.urlopen(url, timeout=2) as r:
            body = r.read(512).decode(errors='ignore')
            if r.status == 200 and (not needle or needle in body):
                sys.exit(0)
    except Exception:
        pass
    time.sleep(1)
sys.exit(1)
PY
}

stop_pidfile() {
  local pidfile="$1"
  if pid_is_running "$pidfile"; then
    kill "$(cat "$pidfile")" || true
    sleep 1
  fi
  rm -f "$pidfile"
}

mkdir -p "$RUN_DIR" "$LOG_DIR" "$SQLITE_DIR" "$NC_TOOL_DIR"

require_cmd python3
require_cmd sqlite3
require_cmd lsof
[[ -x "$ROOT_DIR/bin/nocodb" ]] || { echo "Missing executable: $ROOT_DIR/bin/nocodb" >&2; exit 1; }
[[ -f "$SCHEMA_SQL" ]] || { echo "Missing schema: $SCHEMA_SQL" >&2; exit 1; }
[[ -f "$SEED_SQL" ]] || { echo "Missing seed: $SEED_SQL" >&2; exit 1; }

stop_pidfile "$RUN_DIR_PRINT_PID"
stop_pidfile "$RUN_DIR_NOCO_PID"

if port_busy "$PRINT_PORT"; then
  echo "Port $PRINT_PORT is busy. Stop the current service or override PRINT_PORT." >&2
  exit 1
fi

if port_busy "$NOCO_PORT"; then
  echo "Port $NOCO_PORT is busy. Stop the current service or override NOCO_PORT." >&2
  exit 1
fi

echo "[1/6] Rebuilding demo SQLite database..."
rm -f "$SQLITE_DB_PATH" "$SQLITE_DB_PATH-shm" "$SQLITE_DB_PATH-wal"
sqlite3 "$SQLITE_DB_PATH" < "$SCHEMA_SQL" >/dev/null
sqlite3 "$SQLITE_DB_PATH" < "$SEED_SQL" >/dev/null
sqlite3 "$SQLITE_DB_PATH" <<SQL >/dev/null
DROP VIEW IF EXISTS v_nocodb_print_links;
CREATE VIEW v_nocodb_print_links AS
SELECT
  wa.id AS act_id,
  wa.act_number,
  wa.status,
  wa.act_date,
  cp.full_name AS counterparty_name,
  r.id AS revision_id,
  r.revision_no,
  r.revision_kind,
  da.id AS html_artifact_id,
  da.storage_path AS html_storage_path,
  CASE WHEN da.storage_path IS NOT NULL THEN '${PRINT_BASE_URL}' || da.storage_path ELSE NULL END AS print_url,
  '${PRINT_BASE_URL}' AS print_center_url
FROM work_act wa
JOIN counterparty cp ON cp.id = wa.counterparty_id
LEFT JOIN work_act_revision r ON r.id = COALESCE(wa.signed_revision_id, wa.current_revision_id)
LEFT JOIN document_artifact da ON da.id = r.html_artifact_id
WHERE wa.deleted_at IS NULL;
SQL

echo "[2/6] Starting print artifacts server on :$PRINT_PORT..."
"$ROOT_DIR/scripts/start_print_artifacts_server.sh" "$PRINT_PORT" > "$PRINT_LOG" 2>&1 &
echo $! > "$RUN_DIR_PRINT_PID"
wait_for_url "http://127.0.0.1:${PRINT_PORT}/" "<html" || { echo "Print server failed. See $PRINT_LOG" >&2; exit 1; }

echo "[3/6] Starting NocoDB on :$NOCO_PORT..."
PORT="$NOCO_PORT" \
NC_TOOL_DIR="$NC_TOOL_DIR" \
NC_ADMIN_EMAIL="$NC_ADMIN_EMAIL" \
NC_ADMIN_PASS="$NC_ADMIN_PASS" \
NC_DISABLE_TELE=true \
NC_AUTH_JWT_SECRET="$NC_AUTH_JWT_SECRET" \
"$ROOT_DIR/bin/nocodb" > "$NOCO_LOG" 2>&1 &
echo $! > "$RUN_DIR_NOCO_PID"
wait_for_url "${NOCO_BASE_URL}/dashboard" "<!DOCTYPE html>" || { echo "NocoDB failed. See $NOCO_LOG" >&2; exit 1; }

echo "[4/6] Ensuring NocoDB base/source are configured..."
python3 - "$NOCO_BASE_URL" "$NC_ADMIN_EMAIL" "$NC_ADMIN_PASS" "$NOCO_BASE_TITLE" "$NOCO_SOURCE_ALIAS" "$SQLITE_DB_PATH" "$BOOTSTRAP_JSON" <<'PY'
import json, os, sys, time, urllib.error, urllib.request

base_url, email, password, base_title, source_alias, db_path, output_path = sys.argv[1:]

def req(method, path, body=None, token=None):
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode()
        headers['Content-Type'] = 'application/json'
    if token:
        headers['xc-auth'] = token
    request = urllib.request.Request(base_url + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            text = response.read().decode()
            return response.status, json.loads(text) if text else {}
    except urllib.error.HTTPError as error:
        text = error.read().decode()
        payload = json.loads(text) if text else {}
        return error.code, payload

def auth():
    status, payload = req('POST', '/api/v2/auth/user/signin', {'email': email, 'password': password})
    if status == 200 and payload.get('token'):
        return payload['token'], False
    if payload.get('msg') != 'Invalid credentials':
        raise SystemExit(f"Auth failed: {payload}")
    status, payload = req('POST', '/api/v2/auth/user/signup', {
        'email': email,
        'password': password,
        'firstname': 'Admin',
        'lastname': 'Local',
        'ignore_subscribe': 1,
    })
    if status == 200 and payload.get('token'):
        return payload['token'], True
    raise SystemExit(f"Signup failed: {payload}")

def ensure_base(token):
    status, payload = req('GET', '/api/v2/meta/bases', token=token)
    if status != 200:
        raise SystemExit(f"Base list failed: {payload}")
    for base in payload.get('list', []):
        if base.get('title') == base_title:
            return base['id'], False
    status, payload = req('POST', '/api/v2/meta/bases', {'title': base_title}, token=token)
    if status != 200 or not payload.get('id'):
        raise SystemExit(f"Base create failed: {payload}")
    return payload['id'], True

def ensure_source(token, base_id):
    status, payload = req('GET', f'/api/v2/meta/bases/{base_id}/sources', token=token)
    if status != 200:
        raise SystemExit(f"Source list failed: {payload}")
    sources = payload.get('list', [])
    for source in sources:
        if source.get('alias') == source_alias:
            return source['id'], False
    external_sources = [s for s in sources if not s.get('is_meta') and s.get('type') == 'sqlite3']
    if len(external_sources) == 1:
        source_id = external_sources[0]['id']
        req('PATCH', f'/api/v2/meta/bases/{base_id}/sources/{source_id}', {'alias': source_alias}, token=token)
        return source_id, False
    status, payload = req('POST', f'/api/v2/meta/bases/{base_id}/sources', {
        'alias': source_alias,
        'type': 'sqlite3',
        'config': {
            'client': 'sqlite3',
            'connection': {
                'client': 'sqlite3',
                'database': '',
                'connection': {'filename': os.path.abspath(db_path)},
                'useNullAsDefault': True,
            },
        },
        'inflection_column': 'none',
        'inflection_table': 'none',
        'is_schema_readonly': True,
        'is_data_readonly': False,
        'external': False,
    }, token=token)
    if status != 200:
        raise SystemExit(f"Source create failed: {payload}")
    for _ in range(40):
        time.sleep(1)
        status, payload = req('GET', f'/api/v2/meta/bases/{base_id}/sources', token=token)
        for source in payload.get('list', []):
            if source.get('alias') == source_alias:
                return source['id'], True
    raise SystemExit('Timed out waiting for SQLite source to appear')

def sync_source(token, base_id, source_id):
    status, payload = req('POST', f'/api/v2/meta/bases/{base_id}/meta-diff/{source_id}', token=token)
    if status != 200:
        raise SystemExit(f"Meta Sync failed: {payload}")
    for _ in range(60):
        status, payload = req('GET', f'/api/v2/meta/bases/{base_id}/{source_id}/tables', token=token)
        titles = {item.get('title') for item in payload.get('list', [])}
        if 'v_nocodb_print_links' in titles:
            return len(payload.get('list', []))
        time.sleep(1)
    raise SystemExit('Timed out waiting for v_nocodb_print_links after Meta Sync')

token, signed_up = auth()
base_id, created_base = ensure_base(token)
source_id, created_source = ensure_source(token, base_id)
table_count = sync_source(token, base_id, source_id)

with open(output_path, 'w', encoding='utf-8') as fh:
    json.dump({
        'baseId': base_id,
        'sourceId': source_id,
        'signedUp': signed_up,
        'createdBase': created_base,
        'createdSource': created_source,
        'tableCount': table_count,
    }, fh)
PY

echo "[5/6] Verifying print entrypoints..."
PRINT_URL="$(sqlite3 "$SQLITE_DB_PATH" "SELECT print_url FROM v_nocodb_print_links ORDER BY act_number LIMIT 1;")"
wait_for_url "$PRINT_URL" "Акт" || { echo "Print artifact did not open: $PRINT_URL" >&2; exit 1; }

echo "[6/6] Opening ready URLs..."
BASE_ID="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["baseId"])' "$BOOTSTRAP_JSON")"
DASHBOARD_URL="${NOCO_BASE_URL}/dashboard/#/nc/${BASE_ID}"
PRINT_CENTER_URL="http://127.0.0.1:${PRINT_PORT}/"

if [[ "${NO_OPEN:-0}" != "1" ]] && command -v open >/dev/null 2>&1; then
  open "$DASHBOARD_URL" || true
  open "$PRINT_CENTER_URL" || true
  open "$PRINT_URL" || true
fi

echo
echo "Work Acts demo is ready."
echo "NocoDB:        $DASHBOARD_URL"
echo "Login:         $NC_ADMIN_EMAIL / $NC_ADMIN_PASS"
echo "Print center:  $PRINT_CENTER_URL"
echo "Sample print:  $PRINT_URL"
echo "Logs:          $NOCO_LOG , $PRINT_LOG"