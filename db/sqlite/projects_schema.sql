-- ===========================================
-- projects_schema.sql
-- Version: 1.0
-- Effective Date: 2026-05-01
-- Description: Schema for project management system
-- Includes: project, project_status_history, project_journal,
--          project_journal_act, and related views
-- ===========================================

PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- ---------------------------------------------------------------------------
-- Table: project
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS project (
  id TEXT PRIMARY KEY NOT NULL,
  tenant_id TEXT NOT NULL REFERENCES tenant(id) ON DELETE RESTRICT,
  counterparty_id TEXT NOT NULL REFERENCES counterparty(id) ON DELETE RESTRICT,
  code TEXT NOT NULL,  -- short human code, unique per tenant
  name TEXT NOT NULL,
  description TEXT,    -- nullable: not every project needs a description
  status TEXT NOT NULL DEFAULT 'active'
    CHECK (status IN ('active', 'on_hold', 'completed', 'cancelled')),
  started_on TEXT NOT NULL,  -- ISO date YYYY-MM-DD
  finished_on TEXT,          -- nullable: open-ended projects allowed
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE (tenant_id, code),
  CHECK (finished_on IS NULL OR finished_on >= started_on)
);

-- ---------------------------------------------------------------------------
-- Table: project_status_history  (append-only, mirrors work_act_status_history)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS project_status_history (
  id TEXT PRIMARY KEY NOT NULL,
  project_id TEXT NOT NULL REFERENCES project(id) ON DELETE RESTRICT,
  from_status TEXT
    CHECK (from_status IS NULL OR from_status IN ('active', 'on_hold', 'completed', 'cancelled')),
  to_status TEXT NOT NULL
    CHECK (to_status IN ('active', 'on_hold', 'completed', 'cancelled')),
  changed_by TEXT NOT NULL,
  changed_at TEXT NOT NULL,
  reason TEXT
);

-- ---------------------------------------------------------------------------
-- Extend work_act with optional project linkage
-- ---------------------------------------------------------------------------

ALTER TABLE work_act ADD COLUMN project_id TEXT REFERENCES project(id) ON DELETE RESTRICT;

-- ---------------------------------------------------------------------------
-- Indexes
-- ---------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_project_tenant_status
  ON project (tenant_id, status);

CREATE INDEX IF NOT EXISTS idx_project_tenant_counterparty
  ON project (tenant_id, counterparty_id);

CREATE INDEX IF NOT EXISTS idx_project_status_history_project_changed
  ON project_status_history (project_id, changed_at DESC);

CREATE INDEX IF NOT EXISTS idx_work_act_project
  ON work_act (tenant_id, project_id)
  WHERE project_id IS NOT NULL;

-- ---------------------------------------------------------------------------
-- Trigger: project status transition guard
--
-- Allowed transitions:
--   active    → on_hold, completed, cancelled
--   on_hold   → active, cancelled
--   completed → (none — terminal)
--   cancelled → (none — terminal)
--   same status is always ok
-- ---------------------------------------------------------------------------

CREATE TRIGGER IF NOT EXISTS trg_project_status_transition
BEFORE UPDATE OF status ON project
FOR EACH ROW
WHEN NOT (
  (OLD.status = NEW.status) OR
  (OLD.status = 'active'    AND NEW.status IN ('on_hold', 'completed', 'cancelled')) OR
  (OLD.status = 'on_hold'   AND NEW.status IN ('active', 'cancelled'))
)
BEGIN
  SELECT RAISE(ABORT, 'invalid project status transition');
END;

-- ---------------------------------------------------------------------------
-- Triggers: project_status_history is append-only
-- ---------------------------------------------------------------------------

CREATE TRIGGER IF NOT EXISTS trg_project_status_history_append_only_update
BEFORE UPDATE ON project_status_history
FOR EACH ROW
BEGIN
  SELECT RAISE(ABORT, 'project status history is append only');
END;

CREATE TRIGGER IF NOT EXISTS trg_project_status_history_append_only_delete
BEFORE DELETE ON project_status_history
FOR EACH ROW
BEGIN
  SELECT RAISE(ABORT, 'project status history is append only');
END;

-- ---------------------------------------------------------------------------
-- Triggers: referential integrity — work_act.project_id must point to a
-- project that belongs to the same tenant AND same counterparty as the act.
-- SQLite does not support INSERT OR UPDATE in a single trigger definition,
-- so four triggers are required.
-- ---------------------------------------------------------------------------

CREATE TRIGGER IF NOT EXISTS trg_work_act_project_tenant_match_insert
BEFORE INSERT ON work_act
FOR EACH ROW
WHEN NEW.project_id IS NOT NULL
BEGIN
  SELECT RAISE(ABORT, 'work_act.project_id must belong to the same tenant as the act')
  WHERE NOT EXISTS (
    SELECT 1 FROM project p
    WHERE p.id = NEW.project_id
      AND p.tenant_id = NEW.tenant_id
  );
END;

CREATE TRIGGER IF NOT EXISTS trg_work_act_project_tenant_match_update
BEFORE UPDATE OF project_id ON work_act
FOR EACH ROW
WHEN NEW.project_id IS NOT NULL
BEGIN
  SELECT RAISE(ABORT, 'work_act.project_id must belong to the same tenant as the act')
  WHERE NOT EXISTS (
    SELECT 1 FROM project p
    WHERE p.id = NEW.project_id
      AND p.tenant_id = NEW.tenant_id
  );
END;

CREATE TRIGGER IF NOT EXISTS trg_work_act_project_counterparty_match_insert
BEFORE INSERT ON work_act
FOR EACH ROW
WHEN NEW.project_id IS NOT NULL
BEGIN
  SELECT RAISE(ABORT, 'work_act.project_id must belong to the same counterparty as the act')
  WHERE NOT EXISTS (
    SELECT 1 FROM project p
    WHERE p.id = NEW.project_id
      AND p.counterparty_id = NEW.counterparty_id
  );
END;

CREATE TRIGGER IF NOT EXISTS trg_work_act_project_counterparty_match_update
BEFORE UPDATE OF project_id ON work_act
FOR EACH ROW
WHEN NEW.project_id IS NOT NULL
BEGIN
  SELECT RAISE(ABORT, 'work_act.project_id must belong to the same counterparty as the act')
  WHERE NOT EXISTS (
    SELECT 1 FROM project p
    WHERE p.id = NEW.project_id
      AND p.counterparty_id = NEW.counterparty_id
  );
END;

-- ---------------------------------------------------------------------------
-- View: v_nocodb_project_overview
-- Aggregates act counts and totals per project for dashboard use.
-- ---------------------------------------------------------------------------

CREATE VIEW IF NOT EXISTS v_nocodb_project_overview AS
SELECT
  p.id,
  p.tenant_id,
  t.name AS tenant_name,
  p.counterparty_id,
  cp.full_name AS counterparty_name,
  p.code,
  p.name,
  p.description,
  p.status,
  p.started_on,
  p.finished_on,
  COUNT(wa.id)                                                    AS act_count,
  COUNT(CASE WHEN wa.status = 'signed'  THEN 1 END)              AS signed_act_count,
  COUNT(CASE WHEN wa.status = 'draft'   THEN 1 END)              AS draft_act_count,
  COALESCE(SUM(CASE WHEN wa.status = 'signed'
                    THEN wa.grand_total_amount_minor END), 0)     AS signed_total_minor,
  COALESCE(SUM(wa.grand_total_amount_minor), 0)                  AS all_acts_total_minor,
  MIN(wa.period_from)                                             AS earliest_period_from,
  MAX(wa.period_to)                                               AS latest_period_to,
  p.created_at,
  p.updated_at
FROM project p
JOIN tenant t       ON t.id  = p.tenant_id
JOIN counterparty cp ON cp.id = p.counterparty_id
LEFT JOIN work_act wa
  ON wa.project_id = p.id
 AND wa.deleted_at IS NULL
GROUP BY p.id;

-- ---------------------------------------------------------------------------
-- View: v_nocodb_project_work_acts
-- Chronological work history per project, intended for printing.
-- ---------------------------------------------------------------------------

CREATE VIEW IF NOT EXISTS v_nocodb_project_work_acts AS
SELECT
  p.id                            AS project_id,
  p.code                          AS project_code,
  p.name                          AS project_name,
  p.status                        AS project_status,
  wa.id                           AS act_id,
  wa.act_number,
  wa.act_date,
  wa.period_from,
  wa.period_to,
  wa.status                       AS act_status,
  cp.full_name                    AS counterparty_name,
  ct.contract_number,
  wa.grand_total_amount_minor,
  wa.created_at                   AS act_created_at,
  rev.revision_no                 AS current_revision_no,
  da.storage_path                 AS html_storage_path,
  CASE
    WHEN da.storage_path IS NOT NULL THEN 'http://localhost:4000/' || da.storage_path
    ELSE NULL
  END                             AS print_url
FROM project p
JOIN work_act wa        ON wa.project_id = p.id
                       AND wa.deleted_at IS NULL
JOIN counterparty cp    ON cp.id = wa.counterparty_id
JOIN contract ct        ON ct.id = wa.contract_id
LEFT JOIN work_act_revision rev ON rev.id = wa.current_revision_id
LEFT JOIN document_artifact da  ON da.id  = rev.html_artifact_id
ORDER BY wa.period_from ASC, wa.act_date ASC;

COMMIT;
