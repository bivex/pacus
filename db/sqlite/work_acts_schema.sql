PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS tenant (
  id TEXT PRIMARY KEY NOT NULL,
  code TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS counterparty (
  id TEXT PRIMARY KEY NOT NULL,
  tenant_id TEXT NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
  full_name TEXT NOT NULL,
  inn TEXT NOT NULL,
  kpp TEXT,
  legal_address TEXT,
  is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS contract (
  id TEXT PRIMARY KEY NOT NULL,
  tenant_id TEXT NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
  counterparty_id TEXT NOT NULL REFERENCES counterparty(id) ON DELETE RESTRICT,
  contract_number TEXT NOT NULL,
  contract_date TEXT NOT NULL,
  currency_code TEXT NOT NULL CHECK (length(currency_code) = 3),
  vat_mode TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE (tenant_id, contract_number, contract_date)
);

CREATE TABLE IF NOT EXISTS document_artifact (
  id TEXT PRIMARY KEY NOT NULL,
  tenant_id TEXT NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
  artifact_type TEXT NOT NULL CHECK (artifact_type IN ('html', 'pdf')),
  storage_path TEXT NOT NULL UNIQUE,
  content_type TEXT NOT NULL,
  checksum_sha256 TEXT NOT NULL CHECK (length(checksum_sha256) = 64),
  size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
  renderer_version TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS integration_inbox_work_act (
  id TEXT PRIMARY KEY NOT NULL,
  tenant_id TEXT NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
  source_system TEXT NOT NULL,
  external_document_id TEXT NOT NULL,
  external_version TEXT NOT NULL,
  idempotency_key TEXT NOT NULL UNIQUE,
  counterparty_inn TEXT NOT NULL,
  contract_number TEXT NOT NULL,
  contract_date TEXT NOT NULL,
  act_number TEXT NOT NULL,
  act_date TEXT NOT NULL,
  period_from TEXT NOT NULL,
  period_to TEXT NOT NULL,
  payload_json TEXT NOT NULL CHECK (json_valid(payload_json)),
  payload_hash_sha256 TEXT NOT NULL CHECK (length(payload_hash_sha256) = 64),
  import_status TEXT NOT NULL CHECK (import_status IN ('new', 'processing', 'imported', 'error')),
  import_attempts INTEGER NOT NULL DEFAULT 0 CHECK (import_attempts >= 0),
  imported_act_id TEXT REFERENCES work_act(id) ON DELETE SET NULL,
  last_error TEXT,
  received_at TEXT NOT NULL,
  locked_at TEXT,
  processed_at TEXT,
  CHECK (period_from <= period_to),
  UNIQUE (tenant_id, source_system, external_document_id, external_version)
);

CREATE TABLE IF NOT EXISTS work_act (
  id TEXT PRIMARY KEY NOT NULL,
  tenant_id TEXT NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
  contract_id TEXT NOT NULL REFERENCES contract(id) ON DELETE RESTRICT,
  source_act_id TEXT REFERENCES work_act(id) ON DELETE RESTRICT,
  counterparty_id TEXT NOT NULL REFERENCES counterparty(id) ON DELETE RESTRICT,
  source_system TEXT,
  external_document_id TEXT,
  external_version TEXT,
  imported_at TEXT,
  act_number TEXT NOT NULL,
  act_date TEXT NOT NULL,
  period_from TEXT NOT NULL,
  period_to TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('draft', 'generated', 'sent', 'signed', 'cancelled', 'corrected')),
  current_revision_id TEXT REFERENCES work_act_revision(id) ON DELETE RESTRICT,
  signed_revision_id TEXT REFERENCES work_act_revision(id) ON DELETE RESTRICT,
  total_amount_minor INTEGER NOT NULL DEFAULT 0 CHECK (total_amount_minor >= 0),
  total_vat_amount_minor INTEGER NOT NULL DEFAULT 0 CHECK (total_vat_amount_minor >= 0),
  grand_total_amount_minor INTEGER NOT NULL DEFAULT 0 CHECK (grand_total_amount_minor >= 0),
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  deleted_at TEXT,
  CHECK (period_from <= period_to),
  UNIQUE (tenant_id, act_number)
);

CREATE TABLE IF NOT EXISTS work_act_item (
  id TEXT PRIMARY KEY NOT NULL,
  act_id TEXT NOT NULL REFERENCES work_act(id) ON DELETE CASCADE,
  line_no INTEGER NOT NULL,
  description TEXT NOT NULL,
  unit_code TEXT,
  quantity_milli INTEGER NOT NULL CHECK (quantity_milli > 0),
  price_minor INTEGER NOT NULL CHECK (price_minor >= 0),
  amount_minor INTEGER NOT NULL CHECK (amount_minor >= 0),
  vat_rate_basis_points INTEGER NOT NULL CHECK (vat_rate_basis_points >= 0),
  vat_amount_minor INTEGER NOT NULL CHECK (vat_amount_minor >= 0),
  sort_order INTEGER NOT NULL,
  UNIQUE (act_id, line_no)
);

CREATE TABLE IF NOT EXISTS work_act_revision (
  id TEXT PRIMARY KEY NOT NULL,
  act_id TEXT NOT NULL REFERENCES work_act(id) ON DELETE RESTRICT,
  revision_no INTEGER NOT NULL CHECK (revision_no > 0),
  revision_kind TEXT NOT NULL CHECK (revision_kind IN ('draft', 'final', 'correction')),
  snapshot_json TEXT NOT NULL CHECK (json_valid(snapshot_json)),
  totals_json TEXT NOT NULL CHECK (json_valid(totals_json)),
  template_version TEXT NOT NULL,
  html_artifact_id TEXT REFERENCES document_artifact(id) ON DELETE RESTRICT,
  pdf_artifact_id TEXT REFERENCES document_artifact(id) ON DELETE RESTRICT,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  comment TEXT,
  is_current INTEGER NOT NULL DEFAULT 0 CHECK (is_current IN (0, 1)),
  is_immutable INTEGER NOT NULL DEFAULT 0 CHECK (is_immutable IN (0, 1)),
  UNIQUE (act_id, revision_no)
);

CREATE TABLE IF NOT EXISTS work_act_status_history (
  id TEXT PRIMARY KEY NOT NULL,
  act_id TEXT NOT NULL REFERENCES work_act(id) ON DELETE RESTRICT,
  from_status TEXT,
  to_status TEXT NOT NULL CHECK (to_status IN ('draft', 'generated', 'sent', 'signed', 'cancelled', 'corrected')),
  changed_by TEXT NOT NULL,
  changed_at TEXT NOT NULL,
  reason TEXT
);

CREATE TABLE IF NOT EXISTS audit_event (
  id TEXT PRIMARY KEY NOT NULL,
  tenant_id TEXT NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  action TEXT NOT NULL,
  payload_json TEXT NOT NULL CHECK (json_valid(payload_json)),
  actor_id TEXT NOT NULL,
  occurred_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_counterparty_tenant_name
  ON counterparty (tenant_id, full_name);

CREATE INDEX IF NOT EXISTS idx_contract_tenant_counterparty
  ON contract (tenant_id, counterparty_id, contract_date DESC);

CREATE INDEX IF NOT EXISTS idx_integration_inbox_status_received
  ON integration_inbox_work_act (import_status, received_at);

CREATE INDEX IF NOT EXISTS idx_integration_inbox_source_doc
  ON integration_inbox_work_act (tenant_id, source_system, external_document_id);

CREATE INDEX IF NOT EXISTS idx_work_act_tenant_counterparty_date
  ON work_act (tenant_id, counterparty_id, act_date DESC);

CREATE INDEX IF NOT EXISTS idx_work_act_tenant_status_date
  ON work_act (tenant_id, status, act_date DESC);

CREATE INDEX IF NOT EXISTS idx_work_act_tenant_source
  ON work_act (tenant_id, source_act_id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_work_act_external_doc
  ON work_act (tenant_id, source_system, external_document_id)
  WHERE source_system IS NOT NULL AND external_document_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_work_act_item_act_sort
  ON work_act_item (act_id, sort_order);

CREATE INDEX IF NOT EXISTS idx_work_act_revision_act_rev_desc
  ON work_act_revision (act_id, revision_no DESC);

CREATE UNIQUE INDEX IF NOT EXISTS uq_work_act_revision_current
  ON work_act_revision (act_id)
  WHERE is_current = 1;

CREATE INDEX IF NOT EXISTS idx_work_act_status_history_act_changed
  ON work_act_status_history (act_id, changed_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_event_entity
  ON audit_event (tenant_id, entity_type, entity_id, occurred_at DESC);

CREATE TRIGGER IF NOT EXISTS trg_work_act_status_transition
BEFORE UPDATE OF status ON work_act
FOR EACH ROW
WHEN NOT (
  (OLD.status = NEW.status) OR
  (OLD.status = 'draft' AND NEW.status IN ('generated', 'cancelled')) OR
  (OLD.status = 'generated' AND NEW.status IN ('sent', 'cancelled')) OR
  (OLD.status = 'sent' AND NEW.status IN ('signed', 'cancelled')) OR
  (OLD.status = 'signed' AND NEW.status IN ('corrected')) OR
  (OLD.status = 'cancelled' AND NEW.status = 'cancelled') OR
  (OLD.status = 'corrected' AND NEW.status = 'corrected')
)
BEGIN
  SELECT RAISE(ABORT, 'invalid status transition');
END;

CREATE TRIGGER IF NOT EXISTS trg_work_act_require_signed_revision
BEFORE UPDATE OF status ON work_act
FOR EACH ROW
WHEN NEW.status = 'signed' AND NEW.signed_revision_id IS NULL
BEGIN
  SELECT RAISE(ABORT, 'signed status requires signed_revision_id');
END;

CREATE TRIGGER IF NOT EXISTS trg_work_act_signed_revision_immutable
BEFORE UPDATE OF signed_revision_id ON work_act
FOR EACH ROW
WHEN OLD.signed_revision_id IS NOT NULL AND NEW.signed_revision_id <> OLD.signed_revision_id
BEGIN
  SELECT RAISE(ABORT, 'signed_revision_id is immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_work_act_revision_no_update_immutable
BEFORE UPDATE ON work_act_revision
FOR EACH ROW
WHEN OLD.is_immutable = 1
BEGIN
  SELECT RAISE(ABORT, 'immutable revision cannot be updated');
END;

CREATE TRIGGER IF NOT EXISTS trg_work_act_revision_no_delete_immutable
BEFORE DELETE ON work_act_revision
FOR EACH ROW
WHEN OLD.is_immutable = 1
BEGIN
  SELECT RAISE(ABORT, 'immutable revision cannot be deleted');
END;

CREATE TRIGGER IF NOT EXISTS trg_document_artifact_no_update_if_immutable
BEFORE UPDATE ON document_artifact
FOR EACH ROW
WHEN EXISTS (
  SELECT 1
  FROM work_act_revision r
  WHERE r.is_immutable = 1
    AND (r.html_artifact_id = OLD.id OR r.pdf_artifact_id = OLD.id)
)
BEGIN
  SELECT RAISE(ABORT, 'artifact linked to immutable revision cannot be updated');
END;

CREATE TRIGGER IF NOT EXISTS trg_document_artifact_no_delete_if_immutable
BEFORE DELETE ON document_artifact
FOR EACH ROW
WHEN EXISTS (
  SELECT 1
  FROM work_act_revision r
  WHERE r.is_immutable = 1
    AND (r.html_artifact_id = OLD.id OR r.pdf_artifact_id = OLD.id)
)
BEGIN
  SELECT RAISE(ABORT, 'artifact linked to immutable revision cannot be deleted');
END;

CREATE TRIGGER IF NOT EXISTS trg_status_history_append_only_update
BEFORE UPDATE ON work_act_status_history
FOR EACH ROW
BEGIN
  SELECT RAISE(ABORT, 'status history is append only');
END;

CREATE TRIGGER IF NOT EXISTS trg_status_history_append_only_delete
BEFORE DELETE ON work_act_status_history
FOR EACH ROW
BEGIN
  SELECT RAISE(ABORT, 'status history is append only');
END;

CREATE TRIGGER IF NOT EXISTS trg_audit_event_append_only_update
BEFORE UPDATE ON audit_event
FOR EACH ROW
BEGIN
  SELECT RAISE(ABORT, 'audit event is append only');
END;

CREATE TRIGGER IF NOT EXISTS trg_audit_event_append_only_delete
BEFORE DELETE ON audit_event
FOR EACH ROW
BEGIN
  SELECT RAISE(ABORT, 'audit event is append only');
END;

CREATE TRIGGER IF NOT EXISTS trg_integration_inbox_no_imported_without_act
BEFORE UPDATE OF import_status ON integration_inbox_work_act
FOR EACH ROW
WHEN NEW.import_status = 'imported' AND NEW.imported_act_id IS NULL
BEGIN
  SELECT RAISE(ABORT, 'imported inbox row requires imported_act_id');
END;

CREATE VIEW IF NOT EXISTS v_nocodb_work_act_overview AS
SELECT
  wa.id,
  wa.tenant_id,
  t.name AS tenant_name,
  wa.contract_id,
  c.contract_number,
  wa.counterparty_id,
  cp.full_name AS counterparty_name,
  wa.source_act_id,
  src.act_number AS source_act_number,
  wa.act_number,
  wa.act_date,
  wa.period_from,
  wa.period_to,
  wa.status,
  wa.total_amount_minor,
  wa.total_vat_amount_minor,
  wa.grand_total_amount_minor,
  wa.current_revision_id,
  cur.revision_no AS current_revision_no,
  wa.signed_revision_id,
  srev.revision_no AS signed_revision_no,
  wa.created_at,
  wa.updated_at
FROM work_act wa
JOIN tenant t ON t.id = wa.tenant_id
JOIN contract c ON c.id = wa.contract_id
JOIN counterparty cp ON cp.id = wa.counterparty_id
LEFT JOIN work_act src ON src.id = wa.source_act_id
LEFT JOIN work_act_revision cur ON cur.id = wa.current_revision_id
LEFT JOIN work_act_revision srev ON srev.id = wa.signed_revision_id
WHERE wa.deleted_at IS NULL;

CREATE VIEW IF NOT EXISTS v_nocodb_work_act_drafts AS
SELECT *
FROM work_act
WHERE status = 'draft' AND deleted_at IS NULL;

CREATE VIEW IF NOT EXISTS v_nocodb_work_act_revisions_readonly AS
SELECT
  r.id,
  r.act_id,
  wa.act_number,
  r.revision_no,
  r.revision_kind,
  r.template_version,
  r.html_artifact_id,
  r.pdf_artifact_id,
  r.created_by,
  r.created_at,
  r.comment,
  r.is_current,
  r.is_immutable
FROM work_act_revision r
JOIN work_act wa ON wa.id = r.act_id;

CREATE VIEW IF NOT EXISTS v_nocodb_document_artifacts_readonly AS
SELECT
  da.id,
  da.tenant_id,
  da.artifact_type,
  da.storage_path,
  da.content_type,
  da.checksum_sha256,
  da.size_bytes,
  da.renderer_version,
  da.created_at,
  r.act_id,
  wa.act_number,
  r.revision_no,
  r.is_immutable
FROM document_artifact da
LEFT JOIN work_act_revision r
  ON r.html_artifact_id = da.id OR r.pdf_artifact_id = da.id
LEFT JOIN work_act wa ON wa.id = r.act_id;

CREATE VIEW IF NOT EXISTS v_nocodb_work_act_status_history_readonly AS
SELECT
  h.id,
  h.act_id,
  wa.act_number,
  h.from_status,
  h.to_status,
  h.changed_by,
  h.changed_at,
  h.reason
FROM work_act_status_history h
JOIN work_act wa ON wa.id = h.act_id;

CREATE VIEW IF NOT EXISTS v_nocodb_work_act_corrections AS
SELECT
  src.id AS source_act_id,
  src.act_number AS source_act_number,
  child.id AS correction_act_id,
  child.act_number AS correction_act_number,
  child.status AS correction_status,
  child.act_date AS correction_act_date,
  child.grand_total_amount_minor AS correction_grand_total_amount_minor
FROM work_act src
JOIN work_act child ON child.source_act_id = src.id;

CREATE VIEW IF NOT EXISTS "Inbox All" AS
SELECT
  ib.id,
  ib.tenant_id,
  ib.source_system,
  ib.external_document_id,
  ib.external_version,
  ib.idempotency_key,
  ib.counterparty_inn,
  ib.contract_number,
  ib.contract_date,
  ib.act_number,
  ib.act_date,
  ib.period_from,
  ib.period_to,
  ib.import_status,
  ib.import_attempts,
  ib.imported_act_id,
  wa.status AS imported_act_status,
  ib.last_error,
  ib.received_at,
  ib.locked_at,
  ib.processed_at
FROM integration_inbox_work_act ib
LEFT JOIN work_act wa ON wa.id = ib.imported_act_id;

CREATE VIEW IF NOT EXISTS "Inbox" AS
SELECT *
FROM "Inbox All"
WHERE import_status = 'new';

CREATE VIEW IF NOT EXISTS "Imported" AS
SELECT *
FROM "Inbox All"
WHERE import_status = 'imported';

CREATE VIEW IF NOT EXISTS "Errors" AS
SELECT *
FROM "Inbox All"
WHERE import_status = 'error';

CREATE VIEW IF NOT EXISTS "Ready to Freeze" AS
SELECT
  wa.id AS act_id,
  wa.act_number,
  wa.act_date,
  wa.period_from,
  wa.period_to,
  wa.status,
  cp.full_name AS counterparty_name,
  ct.contract_number,
  ct.contract_date,
  wa.source_system,
  wa.external_document_id,
  wa.external_version,
  wa.imported_at,
  wa.total_amount_minor,
  wa.total_vat_amount_minor,
  wa.grand_total_amount_minor
FROM work_act wa
JOIN counterparty cp ON cp.id = wa.counterparty_id
JOIN contract ct ON ct.id = wa.contract_id
WHERE wa.deleted_at IS NULL
  AND wa.status = 'draft'
  AND wa.source_system IS NOT NULL
  AND wa.imported_at IS NOT NULL;

CREATE VIEW IF NOT EXISTS v_nocodb_print_links AS
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
  CASE
    WHEN da.storage_path IS NOT NULL THEN 'http://localhost:4000/' || da.storage_path
    ELSE NULL
  END AS print_url,
  'http://localhost:4000/' AS print_center_url
FROM work_act wa
JOIN counterparty cp ON cp.id = wa.counterparty_id
LEFT JOIN work_act_revision r ON r.id = COALESCE(wa.signed_revision_id, wa.current_revision_id)
LEFT JOIN document_artifact da ON da.id = r.html_artifact_id
WHERE wa.deleted_at IS NULL;

COMMIT;