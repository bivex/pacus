-- Recreate project_journal with expanded kind CHECK constraint
-- Keeps existing data; adds meeting/call/email to allowed kinds

BEGIN IMMEDIATE;

-- 1. Save journal data
CREATE TEMP TABLE tmp_journal AS SELECT * FROM project_journal;

-- 2. Drop dependent objects (triggers automatically dropped with table)
DROP TABLE IF EXISTS project_journal;

-- 3. Recreate journal with new CHECK
CREATE TABLE project_journal (
  id            TEXT PRIMARY KEY NOT NULL,
  project_id    TEXT NOT NULL REFERENCES project(id) ON DELETE RESTRICT,
  tenant_id     TEXT NOT NULL REFERENCES tenant(id)  ON DELETE RESTRICT,
  entry_date    TEXT NOT NULL,
  kind          TEXT NOT NULL CHECK (kind IN ('meeting','call','email','note','milestone','decision','result')),
  title         TEXT NOT NULL,
  body          TEXT,
  decision_made TEXT,
  outcome       TEXT,
  recorded_by   TEXT NOT NULL,
  recorded_at   TEXT NOT NULL
);

CREATE INDEX idx_project_journal_project_date ON project_journal(project_id, entry_date DESC);

-- Triggers on project_journal
CREATE TRIGGER trg_project_journal_tenant_match
BEFORE INSERT ON project_journal
FOR EACH ROW
BEGIN
  SELECT RAISE(ABORT,'project_journal.tenant_id must match project.tenant_id')
  WHERE NEW.tenant_id != (SELECT tenant_id FROM project WHERE id=NEW.project_id);
END;

CREATE TRIGGER trg_project_journal_append_only_update
BEFORE UPDATE ON project_journal
FOR EACH ROW
BEGIN
  SELECT RAISE(ABORT,'project_journal is append-only');
END;

CREATE TRIGGER trg_project_journal_append_only_delete
BEFORE DELETE ON project_journal
FOR EACH ROW
BEGIN
  SELECT RAISE(ABORT,'project_journal is append-only');
END;

-- 4. Restore data
INSERT INTO project_journal SELECT * FROM tmp_journal;

-- 5. Cleanup
DROP TABLE IF EXISTS tmp_journal;

COMMIT;
