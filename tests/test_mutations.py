#!/usr/bin/env python3
"""
Mutation tests for the pacus SQLite schema.

Each test removes ONE guard (trigger, CHECK, or UNIQUE constraint) from the
schema, then verifies:

  (a) Original schema BLOCKS the bad operation  — probe raises sqlite3.Error
  (b) Mutated schema ALLOWS the bad operation   — probe succeeds

GREEN = the guard is real, effective, and necessary.
RED   = the guard was never enforced, or the mutation didn't remove it
        — a gap in schema correctness.

Run:
    python -m pytest tests/test_mutations.py -v
    python tests/test_mutations.py
"""

import os
import re
import sqlite3
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK_ACTS_SCHEMA = os.path.join(BASE_DIR, "db/sqlite/work_acts_schema.sql")
PROJECTS_SCHEMA  = os.path.join(BASE_DIR, "db/sqlite/projects_schema.sql")


# ── SQL text mutation helpers ─────────────────────────────────────────────────

def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _remove_trigger(sql, name):
    """Remove a CREATE TRIGGER…END; block by trigger name."""
    pattern = rf"CREATE TRIGGER IF NOT EXISTS\s+{re.escape(name)}\b.*?END;"
    result = re.sub(pattern, f"-- MUTATED: removed {name}", sql, flags=re.DOTALL)
    if result == sql:
        raise ValueError(f"Trigger {name!r} not found in SQL")
    return result


def _remove_unique_index(sql, name):
    """Remove a CREATE UNIQUE INDEX…; block by index name."""
    pattern = rf"CREATE UNIQUE INDEX IF NOT EXISTS\s+{re.escape(name)}\b.*?;"
    result = re.sub(pattern, f"-- MUTATED: removed {name}", sql, flags=re.DOTALL)
    if result == sql:
        raise ValueError(f"Unique index {name!r} not found in SQL")
    return result


# ── DB factory ────────────────────────────────────────────────────────────────

_WA_SQL = _read(WORK_ACTS_SCHEMA)
_PR_SQL = _read(PROJECTS_SCHEMA)


def _build(wa_sql, pr_sql):
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(wa_sql)
    conn.executescript(pr_sql)
    return conn


def _original():
    return _build(_WA_SQL, _PR_SQL)


# ── Minimal data helpers ──────────────────────────────────────────────────────

def _base(c):
    c.execute("INSERT INTO tenant VALUES ('t1','T1','Tenant','2026-01-01T00:00:00Z')")
    c.execute(
        "INSERT INTO counterparty (id,tenant_id,full_name,inn,is_active,created_at) "
        "VALUES ('cp1','t1','CP One','7700000001',1,'2026-01-01T00:00:00Z')"
    )
    c.execute(
        "INSERT INTO contract VALUES "
        "('ct1','t1','cp1','C-001','2026-01-01','RUB','vat_20','2026-01-01T00:00:00Z')"
    )


def _act(c, id="wa1", status="draft"):
    c.execute(
        "INSERT INTO work_act "
        " (id,tenant_id,contract_id,counterparty_id,act_number,act_date,"
        "  period_from,period_to,status,total_amount_minor,total_vat_amount_minor,"
        "  grand_total_amount_minor,created_by,created_at,updated_at) "
        "VALUES (?,'t1','ct1','cp1','A-001','2026-03-01',"
        "        '2026-03-01','2026-03-31',?,0,0,0,'user',"
        "        '2026-01-01T00:00:00Z','2026-01-01T00:00:00Z')",
        (id, status),
    )


def _artifact(c, id="da1"):
    c.execute(
        "INSERT INTO document_artifact VALUES "
        " (?,'t1','html',?,'text/html',?,1000,'r-1.0','2026-01-01T00:00:00Z')",
        (id, f"acts/{id}.html", "0" * 64),
    )


def _revision(c, id="rev1", act_id="wa1", no=1,
               is_immutable=1, is_current=1, artifact_id=None):
    c.execute(
        "INSERT INTO work_act_revision "
        " (id,act_id,revision_no,revision_kind,snapshot_json,totals_json,"
        "  template_version,html_artifact_id,created_by,created_at,"
        "  is_current,is_immutable) "
        "VALUES (?,?,?,'draft','{}','{}','tpl-1',?,'user',"
        "        '2026-01-01T00:00:00Z',?,?)",
        (id, act_id, no, artifact_id, is_current, is_immutable),
    )


def _project(c, id="p1", cp="cp1", status="active"):
    c.execute(
        "INSERT INTO project "
        " (id,tenant_id,counterparty_id,code,name,status,started_on,"
        "  created_by,created_at,updated_at) "
        "VALUES (?,'t1',?,?,?,?,'2026-01-01','user',"
        "        '2026-01-01T00:00:00Z','2026-01-01T00:00:00Z')",
        (id, cp, id.upper(), f"Proj {id}", status),
    )


def _add_second_counterparty(c):
    """Add cp2 (same tenant t1) with its own contract ct2."""
    c.execute(
        "INSERT INTO counterparty (id,tenant_id,full_name,inn,is_active,created_at) "
        "VALUES ('cp2','t1','CP Two','7700000002',1,'2026-01-01T00:00:00Z')"
    )
    c.execute(
        "INSERT INTO contract VALUES "
        "('ct2','t1','cp2','C-002','2026-01-01','RUB','vat_20','2026-01-01T00:00:00Z')"
    )


# ── Mutation descriptor ───────────────────────────────────────────────────────

class _Mut:
    __slots__ = ("name", "description", "mutate", "setup", "probe")

    def __init__(self, name, description, mutate, setup, probe):
        self.name        = name
        self.description = description
        self.mutate      = mutate   # (wa_sql, pr_sql) → (wa_sql', pr_sql')
        self.setup       = setup    # conn → (side-effects only)
        self.probe       = probe    # conn → (should succeed on mutant, fail on original)


# ── Mutation catalogue ────────────────────────────────────────────────────────

MUTATIONS = [

    # ── work_act CHECK constraints ────────────────────────────────────────────

    _Mut(
        name="work_act_status_check",
        description="Remove CHECK constraint on work_act.status",
        mutate=lambda wa, pr: (
            wa.replace(
                " CHECK (status IN ('draft', 'generated', 'sent', "
                "'signed', 'cancelled', 'corrected'))",
                "",
            ),
            pr,
        ),
        setup=_base,
        probe=lambda c: c.execute(
            "INSERT INTO work_act "
            " (id,tenant_id,contract_id,counterparty_id,act_number,act_date,"
            "  period_from,period_to,status,total_amount_minor,"
            "  total_vat_amount_minor,grand_total_amount_minor,"
            "  created_by,created_at,updated_at) "
            "VALUES ('wa1','t1','ct1','cp1','A-001','2026-03-01',"
            "        '2026-03-01','2026-03-31','BOGUS',0,0,0,'user',"
            "        '2026-01-01T00:00:00Z','2026-01-01T00:00:00Z')"
        ),
    ),

    _Mut(
        name="work_act_unique_act_number",
        description="Remove UNIQUE(tenant_id, act_number) — allows duplicate act numbers",
        mutate=lambda wa, pr: (
            wa.replace(",\n  UNIQUE (tenant_id, act_number)", ""),
            pr,
        ),
        setup=lambda c: (_base(c), _act(c, id="wa1")),
        probe=lambda c: c.execute(
            "INSERT INTO work_act "
            " (id,tenant_id,contract_id,counterparty_id,act_number,act_date,"
            "  period_from,period_to,status,total_amount_minor,"
            "  total_vat_amount_minor,grand_total_amount_minor,"
            "  created_by,created_at,updated_at) "
            "VALUES ('wa2','t1','ct1','cp1','A-001','2026-03-01',"
            "        '2026-03-01','2026-03-31','draft',0,0,0,'user',"
            "        '2026-01-01T00:00:00Z','2026-01-01T00:00:00Z')"
        ),
    ),

    # ── work_act_revision ─────────────────────────────────────────────────────

    _Mut(
        name="uq_work_act_revision_current",
        description="Remove partial UNIQUE index — allows two 'current' revisions per act",
        mutate=lambda wa, pr: (
            _remove_unique_index(wa, "uq_work_act_revision_current"),
            pr,
        ),
        setup=lambda c: (
            _base(c),
            _act(c),
            _revision(c, id="rev1", no=1, is_current=1, is_immutable=0),
        ),
        probe=lambda c: c.execute(
            "INSERT INTO work_act_revision "
            " (id,act_id,revision_no,revision_kind,snapshot_json,totals_json,"
            "  template_version,created_by,created_at,is_current,is_immutable) "
            "VALUES ('rev2','wa1',2,'draft','{}','{}','tpl-1','user',"
            "        '2026-01-01T00:00:00Z',1,0)"
        ),
    ),

    # ── work_act FSM triggers ─────────────────────────────────────────────────

    _Mut(
        name="trg_work_act_status_transition",
        description="Remove FSM trigger — allows draft→sent (invalid) direct jump",
        mutate=lambda wa, pr: (
            _remove_trigger(wa, "trg_work_act_status_transition"),
            pr,
        ),
        setup=lambda c: (_base(c), _act(c, status="draft")),
        # draft→sent skips the required generated step; also avoids triggering
        # trg_work_act_require_signed_revision (which only fires on 'signed')
        probe=lambda c: c.execute(
            "UPDATE work_act SET status='sent' WHERE id='wa1'"
        ),
    ),

    _Mut(
        name="trg_work_act_require_signed_revision",
        description="Remove trigger requiring signed_revision_id when signing",
        mutate=lambda wa, pr: (
            _remove_trigger(wa, "trg_work_act_require_signed_revision"),
            pr,
        ),
        setup=lambda c: (_base(c), _act(c, status="sent")),
        probe=lambda c: c.execute(
            "UPDATE work_act SET status='signed' WHERE id='wa1'"
        ),
    ),

    _Mut(
        name="trg_work_act_signed_revision_immutable",
        description="Remove trigger that locks signed_revision_id once set",
        mutate=lambda wa, pr: (
            _remove_trigger(wa, "trg_work_act_signed_revision_immutable"),
            pr,
        ),
        setup=lambda c: (
            _base(c),
            _act(c, status="sent"),
            _artifact(c, "da1"),
            _artifact(c, "da2"),
            _revision(c, "rev1", no=1, is_immutable=1, is_current=1, artifact_id="da1"),
            _revision(c, "rev2", no=2, is_immutable=1, is_current=0, artifact_id="da2"),
            c.execute("UPDATE work_act SET signed_revision_id='rev1' WHERE id='wa1'"),
        ),
        probe=lambda c: c.execute(
            "UPDATE work_act SET signed_revision_id='rev2' WHERE id='wa1'"
        ),
    ),

    # ── Immutability triggers ─────────────────────────────────────────────────

    _Mut(
        name="trg_work_act_revision_no_update_immutable",
        description="Remove trigger preventing UPDATE on immutable revisions",
        mutate=lambda wa, pr: (
            _remove_trigger(wa, "trg_work_act_revision_no_update_immutable"),
            pr,
        ),
        setup=lambda c: (_base(c), _act(c), _revision(c, is_immutable=1)),
        probe=lambda c: c.execute(
            "UPDATE work_act_revision SET comment='tampered' WHERE id='rev1'"
        ),
    ),

    _Mut(
        name="trg_work_act_revision_no_delete_immutable",
        description="Remove trigger preventing DELETE on immutable revisions",
        mutate=lambda wa, pr: (
            _remove_trigger(wa, "trg_work_act_revision_no_delete_immutable"),
            pr,
        ),
        setup=lambda c: (
            _base(c),
            _act(c),
            _revision(c, is_immutable=1, is_current=0),  # is_current=0: no FK from work_act
        ),
        probe=lambda c: c.execute("DELETE FROM work_act_revision WHERE id='rev1'"),
    ),

    _Mut(
        name="trg_document_artifact_no_update_if_immutable",
        description="Remove trigger preventing UPDATE on artifacts bound to immutable revisions",
        mutate=lambda wa, pr: (
            _remove_trigger(wa, "trg_document_artifact_no_update_if_immutable"),
            pr,
        ),
        setup=lambda c: (
            _base(c),
            _act(c),
            _artifact(c),
            _revision(c, is_immutable=1, artifact_id="da1"),
        ),
        probe=lambda c: c.execute(
            "UPDATE document_artifact SET size_bytes=9999 WHERE id='da1'"
        ),
    ),

    # NOTE: trg_document_artifact_no_delete_if_immutable is intentionally omitted.
    # The artifact FK (html_artifact_id / pdf_artifact_id REFERENCES document_artifact
    # ON DELETE RESTRICT) already blocks deletion of any referenced artifact regardless
    # of the trigger. The trigger is defense-in-depth; it cannot be independently
    # proven necessary via mutation because the FK fires first on the mutant too.

    # ── Append-only triggers ──────────────────────────────────────────────────

    _Mut(
        name="trg_status_history_append_only_update",
        description="Remove append-only guard on work_act_status_history UPDATE",
        mutate=lambda wa, pr: (
            _remove_trigger(wa, "trg_status_history_append_only_update"),
            pr,
        ),
        setup=lambda c: (
            _base(c),
            _act(c),
            c.execute(
                "INSERT INTO work_act_status_history VALUES "
                "('wsh1','wa1',NULL,'draft','user','2026-01-01T00:00:00Z',NULL)"
            ),
        ),
        probe=lambda c: c.execute(
            "UPDATE work_act_status_history SET reason='tampered' WHERE id='wsh1'"
        ),
    ),

    _Mut(
        name="trg_status_history_append_only_delete",
        description="Remove append-only guard on work_act_status_history DELETE",
        mutate=lambda wa, pr: (
            _remove_trigger(wa, "trg_status_history_append_only_delete"),
            pr,
        ),
        setup=lambda c: (
            _base(c),
            _act(c),
            c.execute(
                "INSERT INTO work_act_status_history VALUES "
                "('wsh1','wa1',NULL,'draft','user','2026-01-01T00:00:00Z',NULL)"
            ),
        ),
        probe=lambda c: c.execute(
            "DELETE FROM work_act_status_history WHERE id='wsh1'"
        ),
    ),

    _Mut(
        name="trg_audit_event_append_only_update",
        description="Remove append-only guard on audit_event UPDATE",
        mutate=lambda wa, pr: (
            _remove_trigger(wa, "trg_audit_event_append_only_update"),
            pr,
        ),
        setup=lambda c: (
            _base(c),
            c.execute(
                "INSERT INTO audit_event VALUES "
                "('ae1','t1','work_act','wa1','create','{}','user','2026-01-01T00:00:00Z')"
            ),
        ),
        probe=lambda c: c.execute(
            "UPDATE audit_event SET action='tampered' WHERE id='ae1'"
        ),
    ),

    _Mut(
        name="trg_audit_event_append_only_delete",
        description="Remove append-only guard on audit_event DELETE",
        mutate=lambda wa, pr: (
            _remove_trigger(wa, "trg_audit_event_append_only_delete"),
            pr,
        ),
        setup=lambda c: (
            _base(c),
            c.execute(
                "INSERT INTO audit_event VALUES "
                "('ae1','t1','work_act','wa1','create','{}','user','2026-01-01T00:00:00Z')"
            ),
        ),
        probe=lambda c: c.execute("DELETE FROM audit_event WHERE id='ae1'"),
    ),

    # ── Integration inbox ─────────────────────────────────────────────────────

    _Mut(
        name="trg_integration_inbox_no_imported_without_act",
        description="Remove trigger requiring imported_act_id when status='imported'",
        mutate=lambda wa, pr: (
            _remove_trigger(wa, "trg_integration_inbox_no_imported_without_act"),
            pr,
        ),
        setup=lambda c: (
            _base(c),
            c.execute(
                "INSERT INTO integration_inbox_work_act "
                " (id,tenant_id,source_system,external_document_id,external_version,"
                "  idempotency_key,counterparty_inn,contract_number,contract_date,"
                "  act_number,act_date,period_from,period_to,payload_json,"
                "  payload_hash_sha256,import_status,import_attempts,received_at) "
                "VALUES ('ib1','t1','erp','doc-1','1','key-1','7700000001','C-001',"
                "        '2026-01-01','A-001','2026-03-01','2026-03-01','2026-03-31',"
                "        '{}',?,'new',0,'2026-01-01T00:00:00Z')",
                ("0" * 64,),
            ),
        ),
        probe=lambda c: c.execute(
            "UPDATE integration_inbox_work_act "
            "SET import_status='imported' WHERE id='ib1'"
        ),
    ),

    # ── project CHECK constraints ─────────────────────────────────────────────

    _Mut(
        name="project_status_check",
        description="Remove CHECK constraint on project.status",
        mutate=lambda wa, pr: (
            wa,
            re.sub(
                r"  status TEXT NOT NULL DEFAULT 'active'\s*\n"
                r"\s*CHECK \(status IN \('active', 'on_hold', 'completed', 'cancelled'\)\),",
                "  status TEXT NOT NULL DEFAULT 'active',",
                pr,
            ),
        ),
        setup=_base,
        probe=lambda c: c.execute(
            "INSERT INTO project "
            " (id,tenant_id,counterparty_id,code,name,status,started_on,"
            "  created_by,created_at,updated_at) "
            "VALUES ('p1','t1','cp1','X','X','BOGUS','2026-01-01',"
            "        'user','2026-01-01T00:00:00Z','2026-01-01T00:00:00Z')"
        ),
    ),

    _Mut(
        name="project_finished_on_check",
        description="Remove CHECK (finished_on >= started_on) from project",
        mutate=lambda wa, pr: (
            wa,
            pr.replace(
                ",\n  CHECK (finished_on IS NULL OR finished_on >= started_on)",
                "",
            ),
        ),
        setup=_base,
        probe=lambda c: c.execute(
            "INSERT INTO project "
            " (id,tenant_id,counterparty_id,code,name,status,"
            "  started_on,finished_on,created_by,created_at,updated_at) "
            "VALUES ('p1','t1','cp1','X','X','active',"
            "        '2026-12-31','2026-01-01','user',"
            "        '2026-01-01T00:00:00Z','2026-01-01T00:00:00Z')"
        ),
    ),

    _Mut(
        name="project_unique_code",
        description="Remove UNIQUE(tenant_id, code) — allows duplicate project codes per tenant",
        mutate=lambda wa, pr: (
            wa,
            pr.replace("  UNIQUE (tenant_id, code),\n", ""),
        ),
        setup=lambda c: (_base(c), _project(c, id="p1")),
        probe=lambda c: c.execute(
            "INSERT INTO project "
            " (id,tenant_id,counterparty_id,code,name,status,started_on,"
            "  created_by,created_at,updated_at) "
            "VALUES ('p2','t1','cp1','P1','Duplicate','active','2026-01-01',"
            "        'user','2026-01-01T00:00:00Z','2026-01-01T00:00:00Z')"
        ),
    ),

    # ── project FSM trigger ───────────────────────────────────────────────────

    _Mut(
        name="trg_project_status_transition",
        description="Remove project FSM trigger — allows completed→active reverse",
        mutate=lambda wa, pr: (
            wa,
            _remove_trigger(pr, "trg_project_status_transition"),
        ),
        setup=lambda c: (_base(c), _project(c, status="completed")),
        probe=lambda c: c.execute(
            "UPDATE project SET status='active' WHERE id='p1'"
        ),
    ),

    # ── project_status_history append-only ────────────────────────────────────

    _Mut(
        name="trg_project_status_history_append_only_update",
        description="Remove append-only guard on project_status_history UPDATE",
        mutate=lambda wa, pr: (
            wa,
            _remove_trigger(pr, "trg_project_status_history_append_only_update"),
        ),
        setup=lambda c: (
            _base(c),
            _project(c),
            c.execute(
                "INSERT INTO project_status_history VALUES "
                "('psh1','p1',NULL,'active','user','2026-01-01T00:00:00Z',NULL)"
            ),
        ),
        probe=lambda c: c.execute(
            "UPDATE project_status_history SET reason='tampered' WHERE id='psh1'"
        ),
    ),

    _Mut(
        name="trg_project_status_history_append_only_delete",
        description="Remove append-only guard on project_status_history DELETE",
        mutate=lambda wa, pr: (
            wa,
            _remove_trigger(pr, "trg_project_status_history_append_only_delete"),
        ),
        setup=lambda c: (
            _base(c),
            _project(c),
            c.execute(
                "INSERT INTO project_status_history VALUES "
                "('psh1','p1',NULL,'active','user','2026-01-01T00:00:00Z',NULL)"
            ),
        ),
        probe=lambda c: c.execute(
            "DELETE FROM project_status_history WHERE id='psh1'"
        ),
    ),

    # ── work_act ↔ project referential integrity triggers ────────────────────

    _Mut(
        name="trg_work_act_project_counterparty_match_insert",
        description=(
            "Remove counterparty-match trigger on INSERT — "
            "allows assigning act to a project of a different counterparty"
        ),
        mutate=lambda wa, pr: (
            wa,
            _remove_trigger(pr, "trg_work_act_project_counterparty_match_insert"),
        ),
        setup=lambda c: (
            _base(c),
            _add_second_counterparty(c),
            _project(c, id="p1", cp="cp1"),  # project for cp1
        ),
        probe=lambda c: c.execute(
            # act for cp2, project for cp1 — counterparty mismatch
            "INSERT INTO work_act "
            " (id,tenant_id,contract_id,counterparty_id,act_number,act_date,"
            "  period_from,period_to,status,total_amount_minor,"
            "  total_vat_amount_minor,grand_total_amount_minor,"
            "  created_by,created_at,updated_at,project_id) "
            "VALUES ('wa1','t1','ct2','cp2','A-001','2026-03-01',"
            "        '2026-03-01','2026-03-31','draft',0,0,0,'user',"
            "        '2026-01-01T00:00:00Z','2026-01-01T00:00:00Z','p1')"
        ),
    ),

    _Mut(
        name="trg_work_act_project_counterparty_match_update",
        description=(
            "Remove counterparty-match trigger on UPDATE — "
            "allows reassigning act to a project of a different counterparty"
        ),
        mutate=lambda wa, pr: (
            wa,
            _remove_trigger(pr, "trg_work_act_project_counterparty_match_update"),
        ),
        setup=lambda c: (
            _base(c),
            _add_second_counterparty(c),
            _project(c, id="p1", cp="cp1"),     # project for cp1
            _act(c, id="wa1"),                   # default act is for cp1
            # insert a second act for cp2, unassigned
            c.execute(
                "INSERT INTO work_act "
                " (id,tenant_id,contract_id,counterparty_id,act_number,act_date,"
                "  period_from,period_to,status,total_amount_minor,"
                "  total_vat_amount_minor,grand_total_amount_minor,"
                "  created_by,created_at,updated_at) "
                "VALUES ('wa2','t1','ct2','cp2','A-002','2026-03-01',"
                "        '2026-03-01','2026-03-31','draft',0,0,0,'user',"
                "        '2026-01-01T00:00:00Z','2026-01-01T00:00:00Z')"
            ),
        ),
        probe=lambda c: c.execute(
            "UPDATE work_act SET project_id='p1' WHERE id='wa2'"  # cp2 act → cp1 project
        ),
    ),

]


# ── Test runner ───────────────────────────────────────────────────────────────

class TestMutations(unittest.TestCase):
    """
    One test_* method per schema mutation.
    Each test has two assertions:
      1. Probe FAILS on original schema     (guard is present)
      2. Probe SUCCEEDS on mutated schema   (guard was removed)
    """
    pass


def _add_test(mut: _Mut) -> None:
    def test_method(self: unittest.TestCase) -> None:
        # ── 1. Guard must be active on original schema ──────────────────────
        orig = _original()
        try:
            mut.setup(orig)
            try:
                mut.probe(orig)
                self.fail(
                    f"[{mut.name}] probe should have raised on the original schema "
                    f"— the guard may be missing or the probe is incorrect"
                )
            except sqlite3.Error:
                pass  # expected: guard blocked the operation
        finally:
            orig.close()

        # ── 2. Guard must be absent on mutated schema ────────────────────────
        wa_mut, pr_mut = mut.mutate(_WA_SQL, _PR_SQL)
        mutant = _build(wa_mut, pr_mut)
        try:
            mut.setup(mutant)
            try:
                mut.probe(mutant)
            except sqlite3.Error as exc:
                self.fail(
                    f"[{mut.name}] probe should have succeeded on the mutated schema "
                    f"(guard was supposed to be removed) but got: {exc}"
                )
        finally:
            mutant.close()

    test_method.__name__ = f"test_{mut.name}"
    test_method.__doc__  = mut.description
    setattr(TestMutations, test_method.__name__, test_method)


for _m in MUTATIONS:
    _add_test(_m)


if __name__ == "__main__":
    unittest.main(verbosity=2)
