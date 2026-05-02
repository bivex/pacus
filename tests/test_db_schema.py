#!/usr/bin/env python3
"""
SQL schema integrity tests for pacus work-acts + projects database.

Tests are grouped by what invariant or contract they verify:
  - Schema structure       (tables, columns, views exist)
  - Project constraints    (check constraints, uniqueness)
  - Project status FSM     (valid / invalid transitions)
  - Project history        (append-only)
  - work_act ↔ project     (tenant + counterparty referential integrity triggers)
  - work_act status FSM    (valid / invalid transitions, trigger guards)
  - Immutable revisions    (revision + artifact protection)
  - Append-only history    (work_act_status_history, audit_event)
  - Integration inbox      (import invariants)
  - Unique constraints     (act_number, project code, one current revision)
  - Views with seed data   (project_overview aggregates, project_work_acts order)
  - Seed smoke             (seed loads cleanly, data is internally consistent)

Run:
    python -m pytest tests/test_db_schema.py -v
    python tests/test_db_schema.py
"""

import os
import sqlite3
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WORK_ACTS_SCHEMA = os.path.join(BASE_DIR, "db/sqlite/work_acts_schema.sql")
PROJECTS_SCHEMA  = os.path.join(BASE_DIR, "db/sqlite/projects_schema.sql")
WORK_ACTS_SEED   = os.path.join(BASE_DIR, "db/sqlite/work_acts_seed_demo.sql")
PROJECTS_SEED    = os.path.join(BASE_DIR, "db/sqlite/projects_seed_demo.sql")


# ---------------------------------------------------------------------------
# DB factory
# ---------------------------------------------------------------------------

def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def make_db(seed: bool = False) -> sqlite3.Connection:
    """Fresh in-memory DB with both schemas (and optionally seed data) applied."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(_read(WORK_ACTS_SCHEMA))
    conn.executescript(_read(PROJECTS_SCHEMA))
    if seed:
        conn.executescript(_read(WORK_ACTS_SEED))
        conn.executescript(_read(PROJECTS_SEED))
    return conn


# ---------------------------------------------------------------------------
# Minimal-record helpers  (insert only what's required for a given test)
# ---------------------------------------------------------------------------

def ins_tenant(conn, id="t1"):
    conn.execute(
        "INSERT INTO tenant VALUES (?, ?, 'Tenant One', '2026-01-01T00:00:00Z')",
        (id, id.upper()),  # use id as code to keep uniqueness across tenants
    )


def ins_counterparty(conn, id="cp1", tenant_id="t1", inn="7700000001"):
    conn.execute(
        "INSERT INTO counterparty "
        "  (id, tenant_id, full_name, inn, is_active, created_at) "
        "VALUES (?, ?, 'CP One', ?, 1, '2026-01-01T00:00:00Z')",
        (id, tenant_id, inn),
    )


def ins_contract(conn, id="ct1", tenant_id="t1", counterparty_id="cp1"):
    conn.execute(
        "INSERT INTO contract VALUES "
        "  (?, ?, ?, ?, '2026-01-01', 'RUB', 'vat_20', '2026-01-01T00:00:00Z')",
        (id, tenant_id, counterparty_id, id.upper()),
    )


def ins_work_act(
    conn,
    id="wa1",
    tenant_id="t1",
    contract_id="ct1",
    counterparty_id="cp1",
    act_number="A-001",
    status="draft",
    project_id=None,
):
    conn.execute(
        "INSERT INTO work_act "
        "  (id, tenant_id, contract_id, counterparty_id, act_number, act_date, "
        "   period_from, period_to, status, total_amount_minor, "
        "   total_vat_amount_minor, grand_total_amount_minor, "
        "   created_by, created_at, updated_at, project_id) "
        "VALUES (?, ?, ?, ?, ?, '2026-03-01', '2026-03-01', '2026-03-31', ?, "
        "        0, 0, 0, 'user', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z', ?)",
        (id, tenant_id, contract_id, counterparty_id, act_number, status, project_id),
    )


def ins_project(
    conn,
    id="p1",
    tenant_id="t1",
    counterparty_id="cp1",
    code="PRJ-001",
    status="active",
):
    conn.execute(
        "INSERT INTO project "
        "  (id, tenant_id, counterparty_id, code, name, status, started_on, "
        "   created_by, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, 'Project One', ?, '2026-01-01', "
        "        'user', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')",
        (id, tenant_id, counterparty_id, code, status),
    )


def ins_artifact(conn, id="da1", tenant_id="t1"):
    # storage_path is UNIQUE so we embed the id to avoid conflicts
    conn.execute(
        "INSERT INTO document_artifact VALUES "
        "  (?, ?, 'html', ?, 'text/html', ?, 1000, 'renderer-1.0', '2026-01-01T00:00:00Z')",
        (id, tenant_id, f"acts/path/{id}.html", "0" * 64),
    )


def ins_revision(
    conn,
    id="rev1",
    act_id="wa1",
    revision_no=1,
    kind="draft",
    is_current=1,
    is_immutable=0,
    artifact_id=None,
):
    conn.execute(
        "INSERT INTO work_act_revision "
        "  (id, act_id, revision_no, revision_kind, snapshot_json, totals_json, "
        "   template_version, html_artifact_id, created_by, created_at, "
        "   is_current, is_immutable) "
        "VALUES (?, ?, ?, ?, '{}', '{}', 'tpl-1', ?, "
        "        'user', '2026-01-01T00:00:00Z', ?, ?)",
        (id, act_id, revision_no, kind, artifact_id, is_current, is_immutable),
    )


# ===========================================================================
# Test classes
# ===========================================================================


class TestSchemaStructure(unittest.TestCase):
    """All expected tables, columns, and views must be created by the migrations."""

    def setUp(self):
        self.db = make_db()

    def tearDown(self):
        self.db.close()

    def _tables(self):
        rows = self.db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        return {r[0] for r in rows}

    def _views(self):
        rows = self.db.execute(
            "SELECT name FROM sqlite_master WHERE type='view'"
        ).fetchall()
        return {r[0] for r in rows}

    def test_work_acts_core_tables_exist(self):
        expected = {
            "tenant", "counterparty", "contract",
            "work_act", "work_act_item", "work_act_revision",
            "work_act_status_history", "document_artifact",
            "audit_event", "integration_inbox_work_act",
        }
        self.assertTrue(expected.issubset(self._tables()))

    def test_project_tables_exist(self):
        self.assertIn("project", self._tables())
        self.assertIn("project_status_history", self._tables())

    def test_work_act_has_project_id_column(self):
        cols = {row[1] for row in self.db.execute("PRAGMA table_info(work_act)")}
        self.assertIn("project_id", cols)

    def test_project_views_exist(self):
        views = self._views()
        self.assertIn("v_nocodb_project_overview", views)
        self.assertIn("v_nocodb_project_work_acts", views)

    def test_work_acts_views_exist(self):
        for v in (
            "v_nocodb_work_act_overview",
            "v_nocodb_work_act_drafts",
            "v_nocodb_work_act_revisions_readonly",
            "v_nocodb_print_links",
            "v_nocodb_work_act_corrections",
            "v_nocodb_work_act_status_history_readonly",
            "v_nocodb_document_artifacts_readonly",
        ):
            self.assertIn(v, self._views(), msg=f"view {v!r} not found")


# ---------------------------------------------------------------------------


class TestProjectConstraints(unittest.TestCase):
    """CHECK constraints and uniqueness on the project table."""

    def setUp(self):
        self.db = make_db()
        ins_tenant(self.db)
        ins_counterparty(self.db)

    def tearDown(self):
        self.db.close()

    def test_project_code_unique_per_tenant(self):
        ins_project(self.db, id="p1", code="PRJ-001")
        with self.assertRaises(sqlite3.Error):
            ins_project(self.db, id="p2", code="PRJ-001")  # duplicate code, same tenant

    def test_project_code_can_repeat_across_tenants(self):
        ins_tenant(self.db, id="t2")
        ins_counterparty(self.db, id="cp2", tenant_id="t2", inn="7700000002")
        ins_project(self.db, id="p1", tenant_id="t1", counterparty_id="cp1", code="PRJ-001")
        ins_project(self.db, id="p2", tenant_id="t2", counterparty_id="cp2", code="PRJ-001")

    def test_project_invalid_status_rejected(self):
        with self.assertRaises(sqlite3.Error):
            self.db.execute(
                "INSERT INTO project "
                "  (id, tenant_id, counterparty_id, code, name, status, "
                "   started_on, created_by, created_at, updated_at) "
                "VALUES ('p1','t1','cp1','X','X','unknown','2026-01-01',"
                "        'user','2026-01-01T00:00:00Z','2026-01-01T00:00:00Z')"
            )

    def test_finished_on_before_started_on_rejected(self):
        with self.assertRaises(sqlite3.Error):
            self.db.execute(
                "INSERT INTO project "
                "  (id, tenant_id, counterparty_id, code, name, status, "
                "   started_on, finished_on, created_by, created_at, updated_at) "
                "VALUES ('p1','t1','cp1','X','X','active','2026-06-01','2026-01-01',"
                "        'user','2026-01-01T00:00:00Z','2026-01-01T00:00:00Z')"
            )

    def test_finished_on_equal_to_started_on_ok(self):
        self.db.execute(
            "INSERT INTO project "
            "  (id, tenant_id, counterparty_id, code, name, status, "
            "   started_on, finished_on, created_by, created_at, updated_at) "
            "VALUES ('p1','t1','cp1','X','X','active','2026-01-01','2026-01-01',"
            "        'user','2026-01-01T00:00:00Z','2026-01-01T00:00:00Z')"
        )

    def test_null_finished_on_ok(self):
        ins_project(self.db, id="p1")  # finished_on defaults to NULL

    def test_project_requires_existing_tenant(self):
        with self.assertRaises(sqlite3.Error):
            ins_project(self.db, id="p1", tenant_id="nonexistent")

    def test_project_requires_existing_counterparty(self):
        with self.assertRaises(sqlite3.Error):
            ins_project(self.db, id="p1", counterparty_id="nonexistent")


# ---------------------------------------------------------------------------


class TestProjectStatusTransitions(unittest.TestCase):
    """Status FSM for project: allowed paths and terminal states."""

    def setUp(self):
        self.db = make_db()
        ins_tenant(self.db)
        ins_counterparty(self.db)
        ins_project(self.db, id="p1", status="active")

    def tearDown(self):
        self.db.close()

    def _set(self, status):
        self.db.execute("UPDATE project SET status=? WHERE id='p1'", (status,))

    # --- valid transitions ---

    def test_active_to_on_hold(self):
        self._set("on_hold")

    def test_active_to_completed(self):
        self._set("completed")

    def test_active_to_cancelled(self):
        self._set("cancelled")

    def test_on_hold_to_active(self):
        self._set("on_hold")
        self._set("active")

    def test_on_hold_to_cancelled(self):
        self._set("on_hold")
        self._set("cancelled")

    def test_same_status_is_noop(self):
        self._set("active")  # active → active must not raise

    # --- invalid transitions ---

    def test_completed_is_terminal_no_active(self):
        self._set("completed")
        with self.assertRaises(sqlite3.Error):
            self._set("active")

    def test_completed_is_terminal_no_on_hold(self):
        self._set("completed")
        with self.assertRaises(sqlite3.Error):
            self._set("on_hold")

    def test_cancelled_is_terminal_no_active(self):
        self._set("cancelled")
        with self.assertRaises(sqlite3.Error):
            self._set("active")

    def test_on_hold_cannot_jump_to_completed(self):
        self._set("on_hold")
        with self.assertRaises(sqlite3.Error):
            self._set("completed")

    def test_active_cannot_jump_back_from_nothing(self):
        # only to verify the guard itself fires; 'draft' is not a valid status
        with self.assertRaises(sqlite3.Error):
            self._set("draft")


# ---------------------------------------------------------------------------


class TestProjectStatusHistoryAppendOnly(unittest.TestCase):
    """project_status_history rows must never be updated or deleted."""

    def setUp(self):
        self.db = make_db()
        ins_tenant(self.db)
        ins_counterparty(self.db)
        ins_project(self.db, id="p1")
        self.db.execute(
            "INSERT INTO project_status_history VALUES "
            "  ('psh1','p1',NULL,'active','user','2026-01-01T00:00:00Z',NULL)"
        )

    def tearDown(self):
        self.db.close()

    def test_update_rejected(self):
        with self.assertRaises(sqlite3.Error):
            self.db.execute(
                "UPDATE project_status_history SET reason='x' WHERE id='psh1'"
            )

    def test_delete_rejected(self):
        with self.assertRaises(sqlite3.Error):
            self.db.execute("DELETE FROM project_status_history WHERE id='psh1'")

    def test_insert_new_row_ok(self):
        self.db.execute(
            "INSERT INTO project_status_history VALUES "
            "  ('psh2','p1','active','on_hold','user','2026-01-02T00:00:00Z','paused')"
        )


# ---------------------------------------------------------------------------


class TestWorkActProjectIntegrity(unittest.TestCase):
    """
    work_act.project_id triggers:
    - the project must belong to the same tenant as the act
    - the project must belong to the same counterparty as the act
    Both on INSERT and on UPDATE OF project_id.
    """

    def setUp(self):
        self.db = make_db()
        ins_tenant(self.db, id="t1")
        ins_tenant(self.db, id="t2")
        ins_counterparty(self.db, id="cp1", tenant_id="t1", inn="7700000001")
        ins_counterparty(self.db, id="cp2", tenant_id="t1", inn="7700000002")
        ins_contract(self.db, id="ct1", tenant_id="t1", counterparty_id="cp1")
        ins_contract(self.db, id="ct2", tenant_id="t1", counterparty_id="cp2")
        ins_project(self.db, id="p_for_cp1", tenant_id="t1", counterparty_id="cp1")

    def tearDown(self):
        self.db.close()

    def test_correct_assignment_on_insert(self):
        ins_work_act(
            self.db, id="wa1", tenant_id="t1",
            contract_id="ct1", counterparty_id="cp1",
            project_id="p_for_cp1",
        )

    def test_counterparty_mismatch_on_insert_rejected(self):
        # act is for cp2, but project is for cp1
        with self.assertRaises(sqlite3.Error):
            ins_work_act(
                self.db, id="wa2", tenant_id="t1",
                contract_id="ct2", counterparty_id="cp2",
                project_id="p_for_cp1",
            )

    def test_counterparty_mismatch_on_update_rejected(self):
        ins_work_act(
            self.db, id="wa3", tenant_id="t1",
            contract_id="ct2", counterparty_id="cp2",
            project_id=None,
        )
        with self.assertRaises(sqlite3.Error):
            self.db.execute(
                "UPDATE work_act SET project_id='p_for_cp1' WHERE id='wa3'"
            )

    def test_null_project_id_always_ok_on_insert(self):
        ins_work_act(
            self.db, id="wa4", tenant_id="t1",
            contract_id="ct2", counterparty_id="cp2",
            project_id=None,
        )

    def test_null_project_id_always_ok_on_update(self):
        ins_work_act(
            self.db, id="wa5", tenant_id="t1",
            contract_id="ct1", counterparty_id="cp1",
            project_id="p_for_cp1",
        )
        self.db.execute("UPDATE work_act SET project_id=NULL WHERE id='wa5'")

    def test_correct_assignment_on_update(self):
        ins_work_act(
            self.db, id="wa6", tenant_id="t1",
            contract_id="ct1", counterparty_id="cp1",
            project_id=None,
        )
        self.db.execute(
            "UPDATE work_act SET project_id='p_for_cp1' WHERE id='wa6'"
        )


# ---------------------------------------------------------------------------


class TestWorkActStatusTransitions(unittest.TestCase):
    """work_act status FSM and trigger guards."""

    def setUp(self):
        self.db = make_db()
        ins_tenant(self.db)
        ins_counterparty(self.db)
        ins_contract(self.db)
        ins_work_act(self.db, id="wa1", status="draft")

    def tearDown(self):
        self.db.close()

    def _set(self, status, **extra):
        sets = ["status=?"]
        vals = [status]
        for k, v in extra.items():
            sets.append(f"{k}=?")
            vals.append(v)
        vals.append("wa1")
        self.db.execute(
            f"UPDATE work_act SET {', '.join(sets)} WHERE id=?", vals
        )

    # --- valid transitions ---

    def test_draft_to_generated(self):
        self._set("generated")

    def test_generated_to_sent(self):
        self._set("generated")
        self._set("sent")

    def test_sent_to_signed_with_revision_id(self):
        ins_artifact(self.db)
        ins_revision(self.db, id="rev1", act_id="wa1", is_immutable=1)
        self._set("generated")
        self._set("sent")
        self._set("signed", signed_revision_id="rev1")

    def test_signed_to_corrected(self):
        ins_artifact(self.db)
        ins_revision(self.db, id="rev1", act_id="wa1", is_immutable=1)
        self._set("generated")
        self._set("sent")
        self._set("signed", signed_revision_id="rev1")
        self._set("corrected")

    def test_draft_to_cancelled(self):
        self._set("cancelled")

    def test_generated_to_cancelled(self):
        self._set("generated")
        self._set("cancelled")

    def test_sent_to_cancelled(self):
        self._set("generated")
        self._set("sent")
        self._set("cancelled")

    # --- invalid transitions ---

    def test_draft_cannot_go_to_signed_directly(self):
        with self.assertRaises(sqlite3.Error):
            self._set("signed")

    def test_draft_cannot_go_to_sent_directly(self):
        with self.assertRaises(sqlite3.Error):
            self._set("sent")

    def test_sent_cannot_go_back_to_draft(self):
        self._set("generated")
        self._set("sent")
        with self.assertRaises(sqlite3.Error):
            self._set("draft")

    def test_cancelled_is_terminal(self):
        self._set("cancelled")
        with self.assertRaises(sqlite3.Error):
            self._set("draft")

    # --- trigger guards ---

    def test_signed_requires_signed_revision_id(self):
        self._set("generated")
        self._set("sent")
        with self.assertRaises(sqlite3.Error):
            self._set("signed")  # signed_revision_id is NULL → trigger fires

    def test_signed_revision_id_is_immutable_once_set(self):
        ins_artifact(self.db, id="da1")
        ins_artifact(self.db, id="da2")
        ins_revision(
            self.db, id="rev1", act_id="wa1", revision_no=1,
            is_immutable=1, is_current=1, artifact_id="da1",
        )
        ins_revision(
            self.db, id="rev2", act_id="wa1", revision_no=2,
            is_immutable=1, is_current=0, artifact_id="da2",
        )
        self._set("generated")
        self._set("sent")
        self._set("signed", signed_revision_id="rev1")
        with self.assertRaises(sqlite3.Error):
            self.db.execute(
                "UPDATE work_act SET signed_revision_id='rev2' WHERE id='wa1'"
            )


# ---------------------------------------------------------------------------


class TestImmutableRevisions(unittest.TestCase):
    """Immutable revisions and the artifacts they reference cannot be changed."""

    def setUp(self):
        self.db = make_db()
        ins_tenant(self.db)
        ins_counterparty(self.db)
        ins_contract(self.db)
        ins_work_act(self.db)
        ins_artifact(self.db)

    def tearDown(self):
        self.db.close()

    def test_mutable_revision_can_be_updated(self):
        ins_revision(self.db, id="rev1", is_immutable=0)
        self.db.execute("UPDATE work_act_revision SET comment='edited' WHERE id='rev1'")

    def test_mutable_revision_can_be_deleted(self):
        ins_revision(self.db, id="rev1", is_immutable=0, is_current=0)
        self.db.execute("DELETE FROM work_act_revision WHERE id='rev1'")

    def test_immutable_revision_cannot_be_updated(self):
        ins_revision(self.db, id="rev1", is_immutable=1)
        with self.assertRaises(sqlite3.Error):
            self.db.execute(
                "UPDATE work_act_revision SET comment='edited' WHERE id='rev1'"
            )

    def test_immutable_revision_cannot_be_deleted(self):
        ins_revision(self.db, id="rev1", is_immutable=1)
        with self.assertRaises(sqlite3.Error):
            self.db.execute("DELETE FROM work_act_revision WHERE id='rev1'")

    def test_artifact_linked_to_immutable_revision_cannot_be_updated(self):
        ins_revision(self.db, id="rev1", is_immutable=1, artifact_id="da1")
        with self.assertRaises(sqlite3.Error):
            self.db.execute(
                "UPDATE document_artifact SET size_bytes=9999 WHERE id='da1'"
            )

    def test_artifact_linked_to_immutable_revision_cannot_be_deleted(self):
        ins_revision(self.db, id="rev1", is_immutable=1, artifact_id="da1")
        with self.assertRaises(sqlite3.Error):
            self.db.execute("DELETE FROM document_artifact WHERE id='da1'")

    def test_artifact_linked_only_to_mutable_revision_can_be_updated(self):
        ins_revision(self.db, id="rev1", is_immutable=0, artifact_id="da1")
        self.db.execute(
            "UPDATE document_artifact SET size_bytes=9999 WHERE id='da1'"
        )


# ---------------------------------------------------------------------------


class TestAppendOnlyHistory(unittest.TestCase):
    """work_act_status_history and audit_event are append-only ledgers."""

    def setUp(self):
        self.db = make_db()
        ins_tenant(self.db)
        ins_counterparty(self.db)
        ins_contract(self.db)
        ins_work_act(self.db)
        self.db.execute(
            "INSERT INTO work_act_status_history VALUES "
            "  ('wsh1','wa1',NULL,'draft','user','2026-01-01T00:00:00Z',NULL)"
        )
        self.db.execute(
            "INSERT INTO audit_event VALUES "
            "  ('ae1','t1','work_act','wa1','create','{}','user','2026-01-01T00:00:00Z')"
        )

    def tearDown(self):
        self.db.close()

    def test_status_history_update_rejected(self):
        with self.assertRaises(sqlite3.Error):
            self.db.execute(
                "UPDATE work_act_status_history SET reason='x' WHERE id='wsh1'"
            )

    def test_status_history_delete_rejected(self):
        with self.assertRaises(sqlite3.Error):
            self.db.execute("DELETE FROM work_act_status_history WHERE id='wsh1'")

    def test_status_history_insert_ok(self):
        self.db.execute(
            "INSERT INTO work_act_status_history VALUES "
            "  ('wsh2','wa1','draft','generated','user','2026-01-02T00:00:00Z',NULL)"
        )

    def test_audit_event_update_rejected(self):
        with self.assertRaises(sqlite3.Error):
            self.db.execute("UPDATE audit_event SET action='x' WHERE id='ae1'")

    def test_audit_event_delete_rejected(self):
        with self.assertRaises(sqlite3.Error):
            self.db.execute("DELETE FROM audit_event WHERE id='ae1'")

    def test_audit_event_insert_ok(self):
        self.db.execute(
            "INSERT INTO audit_event VALUES "
            "  ('ae2','t1','work_act','wa1','update','{}','user','2026-01-02T00:00:00Z')"
        )


# ---------------------------------------------------------------------------


class TestIntegrationInbox(unittest.TestCase):
    """Invariants on integration_inbox_work_act."""

    def setUp(self):
        self.db = make_db()
        ins_tenant(self.db)
        ins_counterparty(self.db)
        ins_contract(self.db)

    def tearDown(self):
        self.db.close()

    def _ins_inbox(self, id="ib1", import_status="new", imported_act_id=None):
        self.db.execute(
            "INSERT INTO integration_inbox_work_act "
            "  (id, tenant_id, source_system, external_document_id, external_version, "
            "   idempotency_key, counterparty_inn, contract_number, contract_date, "
            "   act_number, act_date, period_from, period_to, payload_json, "
            "   payload_hash_sha256, import_status, import_attempts, "
            "   imported_act_id, received_at) "
            "VALUES (?, 't1', 'erp', 'doc-001', '1', ?, '7700000001', "
            "        'C-001', '2026-01-01', 'A-001', '2026-03-01', "
            "        '2026-03-01', '2026-03-31', '{}', ?, ?, 0, ?, "
            "        '2026-01-01T00:00:00Z')",
            (id, f"erp:doc-001:{id}", "0" * 64, import_status, imported_act_id),
        )

    def test_set_imported_without_act_id_rejected(self):
        self._ins_inbox(id="ib1", import_status="new")
        with self.assertRaises(sqlite3.Error):
            self.db.execute(
                "UPDATE integration_inbox_work_act "
                "SET import_status='imported' WHERE id='ib1'"
            )

    def test_set_imported_with_act_id_ok(self):
        ins_work_act(self.db, id="wa1")
        self._ins_inbox(id="ib1", import_status="new")
        self.db.execute(
            "UPDATE integration_inbox_work_act "
            "SET import_status='imported', imported_act_id='wa1' WHERE id='ib1'"
        )

    def test_idempotency_key_must_be_unique(self):
        self._ins_inbox(id="ib1")
        with self.assertRaises(sqlite3.Error):
            # different id, same idempotency key
            self.db.execute(
                "INSERT INTO integration_inbox_work_act "
                "  (id, tenant_id, source_system, external_document_id, "
                "   external_version, idempotency_key, counterparty_inn, "
                "   contract_number, contract_date, act_number, act_date, "
                "   period_from, period_to, payload_json, payload_hash_sha256, "
                "   import_status, import_attempts, received_at) "
                "VALUES ('ib2','t1','erp','doc-002','1','erp:doc-001:ib1',"
                "        '7700000001','C-001','2026-01-01','A-002','2026-03-01',"
                "        '2026-03-01','2026-03-31','{}',?,'new',0,'2026-01-01T00:00:00Z')",
                ("0" * 64,),
            )

    def test_period_from_after_period_to_rejected(self):
        with self.assertRaises(sqlite3.Error):
            self.db.execute(
                "INSERT INTO integration_inbox_work_act "
                "  (id, tenant_id, source_system, external_document_id, "
                "   external_version, idempotency_key, counterparty_inn, "
                "   contract_number, contract_date, act_number, act_date, "
                "   period_from, period_to, payload_json, payload_hash_sha256, "
                "   import_status, import_attempts, received_at) "
                "VALUES ('ib_bad','t1','erp','x','1','key-x','7700000001',"
                "        'C-001','2026-01-01','A-X','2026-03-01',"
                "        '2026-04-01','2026-03-01','{}',?,'new',0,'2026-01-01T00:00:00Z')",
                ("0" * 64,),
            )

    def test_invalid_import_status_rejected(self):
        with self.assertRaises(sqlite3.Error):
            self._ins_inbox(id="ib1", import_status="unknown_status")


# ---------------------------------------------------------------------------


class TestUniqueConstraints(unittest.TestCase):

    def setUp(self):
        self.db = make_db()
        ins_tenant(self.db)
        ins_counterparty(self.db)
        ins_contract(self.db)

    def tearDown(self):
        self.db.close()

    def test_work_act_number_unique_per_tenant(self):
        ins_work_act(self.db, id="wa1", act_number="A-001")
        with self.assertRaises(sqlite3.Error):
            ins_work_act(self.db, id="wa2", act_number="A-001")

    def test_work_act_same_number_ok_across_tenants(self):
        ins_tenant(self.db, id="t2")
        ins_counterparty(self.db, id="cp2", tenant_id="t2", inn="7700000002")
        ins_contract(self.db, id="ct2", tenant_id="t2", counterparty_id="cp2")
        ins_work_act(self.db, id="wa1", act_number="A-001")
        ins_work_act(
            self.db, id="wa2", tenant_id="t2",
            contract_id="ct2", counterparty_id="cp2",
            act_number="A-001",
        )

    def test_contract_unique_per_tenant_number_and_date(self):
        with self.assertRaises(sqlite3.Error):
            # setUp inserts contract with id='ct1', number='CT1' (id.upper())
            # try to insert a duplicate: same tenant, number, date
            self.db.execute(
                "INSERT INTO contract VALUES "
                "  ('ct2','t1','cp1','CT1','2026-01-01','RUB','vat_20','2026-01-02T00:00:00Z')"
            )

    def test_only_one_current_revision_per_act(self):
        ins_work_act(self.db, id="wa1")
        ins_revision(self.db, id="rev1", act_id="wa1", revision_no=1, is_current=1)
        with self.assertRaises(sqlite3.Error):
            ins_revision(self.db, id="rev2", act_id="wa1", revision_no=2, is_current=1)

    def test_multiple_non_current_revisions_ok(self):
        ins_work_act(self.db, id="wa1")
        ins_revision(self.db, id="rev1", act_id="wa1", revision_no=1, is_current=0)
        ins_revision(self.db, id="rev2", act_id="wa1", revision_no=2, is_current=0)

    def test_project_code_unique_per_tenant(self):
        ins_project(self.db, id="p1", code="PRJ-001")
        with self.assertRaises(sqlite3.Error):
            ins_project(self.db, id="p2", code="PRJ-001")


# ---------------------------------------------------------------------------


class TestProjectOverviewView(unittest.TestCase):
    """v_nocodb_project_overview — aggregates, totals, and empty-project edge case."""

    def setUp(self):
        self.db = make_db(seed=True)

    def tearDown(self):
        self.db.close()

    def test_both_demo_projects_present(self):
        codes = {
            r[0]
            for r in self.db.execute(
                "SELECT code FROM v_nocodb_project_overview"
            ).fetchall()
        }
        self.assertIn("ALFA-DEV-2026", codes)
        self.assertIn("BETA-SUP-2026", codes)

    def test_alfa_dev_act_count(self):
        # wa_draft_mar + wa_cancelled_apr
        row = self.db.execute(
            "SELECT act_count FROM v_nocodb_project_overview WHERE code='ALFA-DEV-2026'"
        ).fetchone()
        self.assertEqual(row[0], 2)

    def test_beta_support_act_count(self):
        # wa_sent_feb + wa_original_jan + wa_correction_jan
        row = self.db.execute(
            "SELECT act_count FROM v_nocodb_project_overview WHERE code='BETA-SUP-2026'"
        ).fetchone()
        self.assertEqual(row[0], 3)

    def test_beta_support_signed_count_and_total(self):
        # only wa_correction_jan has status='signed'
        row = self.db.execute(
            "SELECT signed_act_count, signed_total_minor "
            "FROM v_nocodb_project_overview WHERE code='BETA-SUP-2026'"
        ).fetchone()
        signed_count, signed_total = row
        self.assertEqual(signed_count, 1)
        self.assertEqual(signed_total, 1_440_000)

    def test_project_with_no_acts_shows_zero_aggregates(self):
        self.db.execute(
            "INSERT INTO project "
            "  (id, tenant_id, counterparty_id, code, name, status, "
            "   started_on, created_by, created_at, updated_at) "
            "VALUES ('proj_empty','tenant_demo','cp_alfa','EMPTY','Empty','active',"
            "        '2026-01-01','user','2026-01-01T00:00:00Z','2026-01-01T00:00:00Z')"
        )
        row = self.db.execute(
            "SELECT act_count, signed_total_minor, all_acts_total_minor "
            "FROM v_nocodb_project_overview WHERE id='proj_empty'"
        ).fetchone()
        self.assertEqual(row, (0, 0, 0))

    def test_counterparty_name_joined_correctly(self):
        row = self.db.execute(
            "SELECT counterparty_name FROM v_nocodb_project_overview "
            "WHERE code='ALFA-DEV-2026'"
        ).fetchone()
        self.assertEqual(row[0], "ООО Альфа Инжиниринг")


# ---------------------------------------------------------------------------


class TestProjectWorkActsView(unittest.TestCase):
    """v_nocodb_project_work_acts — chronological history for printing."""

    def setUp(self):
        self.db = make_db(seed=True)

    def tearDown(self):
        self.db.close()

    def test_beta_acts_end_with_february_act(self):
        # Seed order: two Jan acts (period_from 2026-01-01), then Feb act
        rows = self.db.execute(
            "SELECT act_number FROM v_nocodb_project_work_acts "
            "WHERE project_code='BETA-SUP-2026'"
        ).fetchall()
        numbers = [r[0] for r in rows]
        self.assertEqual(numbers[-1], "A-2026-002")

    def test_only_acts_with_project_appear(self):
        total = self.db.execute(
            "SELECT COUNT(*) FROM v_nocodb_project_work_acts"
        ).fetchone()[0]
        # Seed assigns all 5 work_acts to projects
        self.assertEqual(total, 5)

    def test_print_url_has_correct_prefix(self):
        urls = self.db.execute(
            "SELECT print_url FROM v_nocodb_project_work_acts "
            "WHERE print_url IS NOT NULL LIMIT 1"
        ).fetchall()
        self.assertTrue(len(urls) > 0)
        self.assertTrue(urls[0][0].startswith("http://localhost:4000/"))

    def test_deleted_acts_are_excluded(self):
        self.db.execute(
            "UPDATE work_act SET deleted_at='2026-03-20T00:00:00Z' "
            "WHERE id='wa_draft_mar'"
        )
        act_ids = {
            r[0]
            for r in self.db.execute(
                "SELECT act_id FROM v_nocodb_project_work_acts "
                "WHERE project_code='ALFA-DEV-2026'"
            ).fetchall()
        }
        self.assertNotIn("wa_draft_mar", act_ids)
        # the other alfa act must still be there
        self.assertIn("wa_cancelled_apr", act_ids)

    def test_contract_number_joined_correctly(self):
        row = self.db.execute(
            "SELECT contract_number FROM v_nocodb_project_work_acts "
            "WHERE act_id='wa_draft_mar'"
        ).fetchone()
        self.assertEqual(row[0], "DEV-2026-01")


# ---------------------------------------------------------------------------


class TestSeedSmoke(unittest.TestCase):
    """Seed loads without errors and the resulting data is internally consistent."""

    def setUp(self):
        self.db = make_db(seed=True)

    def tearDown(self):
        self.db.close()

    def test_two_demo_projects_loaded(self):
        count = self.db.execute("SELECT COUNT(*) FROM project").fetchone()[0]
        self.assertEqual(count, 2)

    def test_three_project_status_history_entries(self):
        count = self.db.execute(
            "SELECT COUNT(*) FROM project_status_history"
        ).fetchone()[0]
        self.assertEqual(count, 3)  # 1 for alfa, 2 for beta

    def test_all_seed_acts_assigned_to_a_project(self):
        unassigned = self.db.execute(
            "SELECT COUNT(*) FROM work_act "
            "WHERE project_id IS NULL AND deleted_at IS NULL"
        ).fetchone()[0]
        self.assertEqual(unassigned, 0)

    def test_no_act_assigned_to_wrong_counterparty_project(self):
        mismatches = self.db.execute(
            "SELECT COUNT(*) FROM work_act wa "
            "JOIN project p ON p.id = wa.project_id "
            "WHERE wa.counterparty_id != p.counterparty_id"
        ).fetchone()[0]
        self.assertEqual(mismatches, 0)

    def test_no_act_assigned_to_wrong_tenant_project(self):
        mismatches = self.db.execute(
            "SELECT COUNT(*) FROM work_act wa "
            "JOIN project p ON p.id = wa.project_id "
            "WHERE wa.tenant_id != p.tenant_id"
        ).fetchone()[0]
        self.assertEqual(mismatches, 0)

    def test_five_work_acts_seeded(self):
        count = self.db.execute("SELECT COUNT(*) FROM work_act").fetchone()[0]
        self.assertEqual(count, 5)

    def test_project_overview_total_matches_act_sum(self):
        """Sum of grand_total in overview must equal sum of acts directly."""
        direct = self.db.execute(
            "SELECT SUM(grand_total_amount_minor) FROM work_act "
            "WHERE project_id='proj_beta_support' AND deleted_at IS NULL"
        ).fetchone()[0]
        via_view = self.db.execute(
            "SELECT all_acts_total_minor FROM v_nocodb_project_overview "
            "WHERE id='proj_beta_support'"
        ).fetchone()[0]
        self.assertEqual(direct, via_view)


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
