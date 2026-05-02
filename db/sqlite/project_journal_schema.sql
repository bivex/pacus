-- ===========================================
-- project_journal_schema.sql
-- Version: 1.0
-- Effective Date: 2026-05-01
-- Description: Schema for project journal (decisions, milestones, notes)
-- ===========================================

PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- ---------------------------------------------------------------------------
-- Table: project_journal
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS project_journal (
  id            TEXT PRIMARY KEY NOT NULL,
  project_id    TEXT NOT NULL REFERENCES project(id) ON DELETE RESTRICT,
  tenant_id     TEXT NOT NULL REFERENCES tenant(id)  ON DELETE RESTRICT,
  entry_date    TEXT NOT NULL,
   kind          TEXT NOT NULL CHECK (kind IN ('meeting', 'call', 'email', 'note', 'milestone', 'decision', 'result')),
  title         TEXT NOT NULL,
  body          TEXT,
  decision_made TEXT,
  outcome       TEXT,
  recorded_by   TEXT NOT NULL,
  recorded_at   TEXT NOT NULL
);

-- ---------------------------------------------------------------------------
-- Table: project_journal_act  (junction: journal entry ↔ work act)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS project_journal_act (
  journal_id TEXT NOT NULL REFERENCES project_journal(id) ON DELETE CASCADE,
  act_id     TEXT NOT NULL REFERENCES work_act(id)        ON DELETE RESTRICT,
  PRIMARY KEY (journal_id, act_id)
);

-- ---------------------------------------------------------------------------
-- Indexes
-- ---------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_project_journal_project_date ON project_journal (project_id, entry_date DESC);
CREATE INDEX IF NOT EXISTS idx_project_journal_act ON project_journal_act (act_id);

-- ---------------------------------------------------------------------------
-- Trigger: tenant isolation — journal entry must belong to the same tenant
-- as the project it references.
-- ---------------------------------------------------------------------------

CREATE TRIGGER IF NOT EXISTS trg_project_journal_tenant_match
BEFORE INSERT ON project_journal
FOR EACH ROW
BEGIN
  SELECT RAISE(ABORT, 'project_journal.tenant_id must match project.tenant_id')
  WHERE NEW.tenant_id != (SELECT tenant_id FROM project WHERE id = NEW.project_id);
END;

-- ---------------------------------------------------------------------------
-- Triggers: project_journal is append-only
-- ---------------------------------------------------------------------------

CREATE TRIGGER IF NOT EXISTS trg_project_journal_append_only_update
BEFORE UPDATE ON project_journal
FOR EACH ROW
BEGIN
  SELECT RAISE(ABORT, 'project_journal is append-only');
END;

CREATE TRIGGER IF NOT EXISTS trg_project_journal_append_only_delete
BEFORE DELETE ON project_journal
FOR EACH ROW
BEGIN
  SELECT RAISE(ABORT, 'project_journal is append-only');
END;

-- ---------------------------------------------------------------------------
-- Trigger: tenant isolation — linked work act must belong to the same tenant
-- as the journal entry.
-- ---------------------------------------------------------------------------

CREATE TRIGGER IF NOT EXISTS trg_project_journal_act_tenant_match
BEFORE INSERT ON project_journal_act
FOR EACH ROW
BEGIN
  SELECT RAISE(ABORT, 'project_journal_act: act and journal entry must share the same tenant')
  WHERE (SELECT tenant_id FROM work_act WHERE id = NEW.act_id)
     != (SELECT tenant_id FROM project_journal WHERE id = NEW.journal_id);
END;

COMMIT;
