-- Update project_journal constraint to include meeting/call/email
-- This script recreates project_journal and project_journal_act with updated schema

BEGIN IMMEDIATE;

-- Save existing journal data
CREATE TEMP TABLE tmp_journal AS SELECT * FROM project_journal;

-- Save existing junction data
CREATE TEMP TABLE tmp_journal_act AS SELECT * FROM project_journal_act;

-- Drop old tables (cascades drop triggers automatically)
DROP TABLE IF EXISTS project_journal_act;
DROP TABLE IF EXISTS project_journal;

-- Recreate project_journal with updated CHECK constraint
-- (reading from schema file)
-- Inline the DDL to avoid file read issues
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

-- Indexes
CREATE INDEX IF NOT EXISTS idx_project_journal_project_date ON project_journal (project_id, entry_date DESC);

-- Triggers for tenant isolation on project_journal
CREATE TRIGGER IF NOT EXISTS trg_project_journal_tenant_match
BEFORE INSERT ON project_journal
FOR EACH ROW
BEGIN
  SELECT RAISE(ABORT, 'project_journal.tenant_id must match project.tenant_id')
  WHERE NEW.tenant_id != (SELECT tenant_id FROM project WHERE id = NEW.project_id);
END;

-- Triggers: append-only on project_journal
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

-- Recreate junction table (unchanged)
CREATE TABLE IF NOT EXISTS project_journal_act (
  journal_id TEXT NOT NULL REFERENCES project_journal(id) ON DELETE CASCADE,
  act_id     TEXT NOT NULL REFERENCES work_act(id)        ON DELETE RESTRICT,
  PRIMARY KEY (journal_id, act_id)
);

CREATE INDEX IF NOT EXISTS idx_project_journal_act ON project_journal_act (act_id);

-- Trigger: tenant isolation on junction (after table exists)
CREATE TRIGGER IF NOT EXISTS trg_project_journal_act_tenant_match
BEFORE INSERT ON project_journal_act
FOR EACH ROW
BEGIN
  SELECT RAISE(ABORT, 'project_journal_act: act and journal entry must share the same tenant')
  WHERE (SELECT tenant_id FROM work_act WHERE id = NEW.act_id)
     != (SELECT tenant_id FROM project_journal WHERE id = NEW.journal_id);
END;

-- Restore data
INSERT INTO project_journal SELECT * FROM tmp_journal;
INSERT INTO project_journal_act SELECT * FROM tmp_journal_act;

-- Cleanup
DROP TABLE IF EXISTS tmp_journal;
DROP TABLE IF EXISTS tmp_journal_act;

COMMIT;
