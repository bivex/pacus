#!/usr/bin/env python3
"""Pacus — Flask Web UI for work acts management."""

import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask_babel import Babel, gettext as _

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).parent
DB_PATH = ROOT_DIR / "data/sqlite/work_acts_demo.sqlite"
ARTIFACTS_DIR = ROOT_DIR / "data/artifacts"
TENANT_ID = "tenant_demo"
SUPPORTED_LOCALES = ["ru", "en"]

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "pacus-dev-secret-2026")
app.config["ARTIFACTS_DIR"] = str(ARTIFACTS_DIR)
app.config["BABEL_DEFAULT_LOCALE"] = "ru"
app.config["BABEL_TRANSLATION_DIRECTORIES"] = str(ROOT_DIR / "translations")


def get_locale():
    return session.get("lang", "ru")


babel = Babel(app, locale_selector=get_locale)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ACT_STATUSES = ["draft", "generated", "sent", "signed", "cancelled", "corrected"]
PROJECT_STATUSES = ["active", "on_hold", "completed", "cancelled"]

ACT_TRANSITIONS = {
    "draft": ["generated", "cancelled"],
    "generated": ["sent", "cancelled"],
    "sent": ["signed", "cancelled"],
    "signed": ["corrected"],
    "cancelled": [],
    "corrected": [],
}

PROJECT_TRANSITIONS = {
    "active": ["on_hold", "completed", "cancelled"],
    "on_hold": ["active", "cancelled"],
    "completed": [],
    "cancelled": [],
}


def _status_labels():
    return {
        "draft": _("Черновик"),
        "generated": _("Сформирован"),
        "sent": _("Отправлен"),
        "signed": _("Подписан"),
        "cancelled": _("Отменён"),
        "corrected": _("Скорректирован"),
        "active": _("Активный"),
        "on_hold": _("Приостановлен"),
        "completed": _("Завершён"),
    }


def make_id(prefix, *parts):
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:20]
    return "{}_{}".format(prefix, digest)


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_db():
    if "db" not in g:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 5000")
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db:
        db.close()


def fmt_amount(minor):
    if minor is None:
        return "—"
    rubles = minor / 100
    integer = int(rubles)
    frac = round((rubles - integer) * 100)
    s = "{:,}".format(integer).replace(",", " ")
    return "{},{:02d}".format(s, frac)


def fmt_date(iso):
    if not iso:
        return "—"
    try:
        y, m, d = iso[:10].split("-")
        return "{}.{}.{}".format(d, m, y)
    except Exception:
        return iso


def fmt_dt(iso):
    if not iso:
        return "—"
    return "{} {}".format(fmt_date(iso[:10]), iso[11:16])


def parse_rubles(text):
    text = text.replace(",", ".").replace(" ", "").replace(" ", "").strip()
    val = float(text)
    return int(round(val * 100))


def parse_qty(text):
    text = text.replace(",", ".").strip()
    val = float(text)
    return int(round(val * 1000))


def recalculate_totals(act_id):
    db = get_db()
    row = db.execute(
        "SELECT COALESCE(SUM(amount_minor),0), COALESCE(SUM(vat_amount_minor),0) FROM work_act_item WHERE act_id = ?",
        (act_id,),
    ).fetchone()
    total, vat = row[0], row[1]
    db.execute(
        "UPDATE work_act SET total_amount_minor=?, total_vat_amount_minor=?, grand_total_amount_minor=?, updated_at=? WHERE id=?",
        (total, vat, total + vat, utc_now(), act_id),
    )


# ---------------------------------------------------------------------------
# Jinja2 filters
# ---------------------------------------------------------------------------
app.jinja_env.filters["rubles"] = lambda v: fmt_amount(v)
app.jinja_env.filters["fmt_date"] = fmt_date
app.jinja_env.filters["fmt_dt"] = fmt_dt


@app.context_processor
def inject_globals():
    return {
        "ACT_TRANSITIONS": ACT_TRANSITIONS,
        "PROJECT_TRANSITIONS": PROJECT_TRANSITIONS,
        "STATUS_LABELS": _status_labels(),
        "current_locale": get_locale(),
    }


# ---------------------------------------------------------------------------
# Language switch
# ---------------------------------------------------------------------------
@app.route("/lang/<locale>")
def set_language(locale):
    if locale in SUPPORTED_LOCALES:
        session["lang"] = locale
    return redirect(request.referrer or url_for("dashboard"))


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@app.route("/")
def dashboard():
    db = get_db()
    acts = db.execute(
        "SELECT * FROM v_nocodb_work_act_overview WHERE tenant_id = ? ORDER BY act_date DESC",
        (TENANT_ID,),
    ).fetchall()
    projects = db.execute(
        "SELECT * FROM v_nocodb_project_overview WHERE tenant_id = ? ORDER BY started_on DESC",
        (TENANT_ID,),
    ).fetchall()
    inbox_count = db.execute(
        "SELECT COUNT(*) FROM integration_inbox_work_act WHERE import_status = 'new'"
    ).fetchone()[0]
    return render_template(
        "dashboard.html", acts=acts, projects=projects, inbox_count=inbox_count
    )


# ---------------------------------------------------------------------------
# Acts
# ---------------------------------------------------------------------------
@app.route("/acts")
def acts_list():
    db = get_db()
    status_filter = request.args.get("status", "")
    if status_filter in ACT_STATUSES:
        rows = db.execute(
            "SELECT * FROM v_nocodb_work_act_overview WHERE tenant_id = ? AND status = ? ORDER BY act_date DESC",
            (TENANT_ID, status_filter),
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM v_nocodb_work_act_overview WHERE tenant_id = ? ORDER BY act_date DESC",
            (TENANT_ID,),
        ).fetchall()
    return render_template(
        "acts/list.html", acts=rows, current_filter=status_filter, statuses=ACT_STATUSES
    )


@app.route("/acts/new", methods=["GET", "POST"])
def act_new():
    db = get_db()
    counterparties = db.execute(
        "SELECT id, full_name, inn FROM counterparty WHERE tenant_id = ? AND is_active = 1 ORDER BY full_name",
        (TENANT_ID,),
    ).fetchall()

    if request.method == "GET":
        now = datetime.now()
        now_iso_date = now.strftime("%Y-%m-%d")
        now_iso_month_start = now.strftime("%Y-%m-01")
        return render_template(
            "acts/form.html",
            mode="create",
            counterparties=counterparties,
            now_iso_date=now_iso_date,
            now_iso_month_start=now_iso_month_start,
        )

    # POST — create act
    cp_id = request.form.get("counterparty_id")
    contract_id = request.form.get("contract_id")
    project_id = request.form.get("project_id") or None
    act_number = request.form.get("act_number", "").strip()
    act_date = request.form.get("act_date", "").strip()
    period_from = request.form.get("period_from", "").strip()
    period_to = request.form.get("period_to", "").strip()

    if not all([cp_id, contract_id, act_number, act_date, period_from, period_to]):
        flash(_("Заполните все обязательные поля"), "error")
        return render_template(
            "acts/form.html", mode="create", counterparties=counterparties
        ), 400

    now = utc_now()
    act_id = make_id("wa", TENANT_ID, act_number, act_date)

    items = []
    idx = 0
    while True:
        desc = request.form.get("item_desc_{}".format(idx))
        if desc is None:
            break
        if not desc.strip():
            idx += 1
            continue
        qty_text = request.form.get("item_qty_{}".format(idx), "0")
        price_text = request.form.get("item_price_{}".format(idx), "0")
        vat_bp = int(request.form.get("item_vat_{}".format(idx), "2000"))
        qty_milli = parse_qty(qty_text) if qty_text else 1000
        price_minor = parse_rubles(price_text) if price_text else 0
        amount = (qty_milli * price_minor + 500) // 1000
        vat_amount = (amount * vat_bp + 5000) // 10000
        items.append(
            {
                "id": make_id("wai", act_id, str(idx + 1)),
                "line_no": idx + 1,
                "description": desc.strip(),
                "unit_code": request.form.get("item_unit_{}".format(idx), "JOB"),
                "quantity_milli": qty_milli,
                "price_minor": price_minor,
                "amount_minor": amount,
                "vat_rate_basis_points": vat_bp,
                "vat_amount_minor": vat_amount,
                "sort_order": idx + 1,
            }
        )
        idx += 1

    if not items:
        flash(_("Добавьте хотя бы одну позицию"), "error")
        return render_template(
            "acts/form.html", mode="create", counterparties=counterparties
        ), 400

    total = sum(i["amount_minor"] for i in items)
    vat = sum(i["vat_amount_minor"] for i in items)

    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute(
            "INSERT INTO work_act (id,tenant_id,contract_id,counterparty_id,project_id,act_number,act_date,period_from,period_to,status,total_amount_minor,total_vat_amount_minor,grand_total_amount_minor,created_by,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                act_id,
                TENANT_ID,
                contract_id,
                cp_id,
                project_id,
                act_number,
                act_date,
                period_from,
                period_to,
                "draft",
                total,
                vat,
                total + vat,
                "web_user",
                now,
                now,
            ),
        )
        for it in items:
            db.execute(
                "INSERT INTO work_act_item (id,act_id,line_no,description,unit_code,quantity_milli,price_minor,amount_minor,vat_rate_basis_points,vat_amount_minor,sort_order) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (
                    it["id"],
                    act_id,
                    it["line_no"],
                    it["description"],
                    it["unit_code"],
                    it["quantity_milli"],
                    it["price_minor"],
                    it["amount_minor"],
                    it["vat_rate_basis_points"],
                    it["vat_amount_minor"],
                    it["sort_order"],
                ),
            )
        db.execute(
            "INSERT INTO work_act_status_history (id,act_id,from_status,to_status,changed_by,changed_at,reason) VALUES (?,?,?,?,?,?,?)",
            (
                make_id("wsh", act_id, "draft"),
                act_id,
                None,
                "draft",
                "web_user",
                now,
                _("Создан через веб-UI"),
            ),
        )
        db.commit()
        flash(_("Акт %(number)s создан", number=act_number), "success")
        return redirect(url_for("act_detail", act_id=act_id))
    except Exception as exc:
        if db.in_transaction:
            db.rollback()
        flash(_("Ошибка: %(error)s", error=exc), "error")
        return render_template(
            "acts/form.html", mode="create", counterparties=counterparties
        ), 400


@app.route("/acts/<act_id>")
def act_detail(act_id):
    db = get_db()
    act = db.execute(
        "SELECT wa.*, t.name AS tenant_name, cp.full_name AS counterparty_name, cp.inn AS counterparty_inn, ct.contract_number, ct.contract_date, p.code AS project_code, p.name AS project_name FROM work_act wa JOIN tenant t ON t.id=wa.tenant_id JOIN counterparty cp ON cp.id=wa.counterparty_id JOIN contract ct ON ct.id=wa.contract_id LEFT JOIN project p ON p.id=wa.project_id WHERE wa.id=? AND wa.deleted_at IS NULL",
        (act_id,),
    ).fetchone()
    if not act:
        abort(404)

    items = db.execute(
        "SELECT * FROM work_act_item WHERE act_id=? ORDER BY sort_order", (act_id,)
    ).fetchall()
    history = db.execute(
        "SELECT * FROM work_act_status_history WHERE act_id=? ORDER BY changed_at",
        (act_id,),
    ).fetchall()
    revisions = db.execute(
        "SELECT r.*, da.storage_path FROM work_act_revision r LEFT JOIN document_artifact da ON da.id=r.html_artifact_id WHERE r.act_id=? ORDER BY r.revision_no",
        (act_id,),
    ).fetchall()

    valid_transitions = ACT_TRANSITIONS.get(act["status"], [])
    return render_template(
        "acts/detail.html",
        act=act,
        items=items,
        history=history,
        revisions=revisions,
        valid_transitions=valid_transitions,
    )


@app.route("/acts/<act_id>/edit", methods=["GET", "POST"])
def act_edit(act_id):
    db = get_db()
    act = db.execute(
        "SELECT * FROM work_act WHERE id=? AND status='draft' AND deleted_at IS NULL",
        (act_id,),
    ).fetchone()
    if not act:
        flash(_("Редактирование доступно только для черновиков"), "error")
        return redirect(url_for("act_detail", act_id=act_id))

    counterparties = db.execute(
        "SELECT id, full_name FROM counterparty WHERE tenant_id = ? AND is_active = 1 ORDER BY full_name",
        (TENANT_ID,),
    ).fetchall()

    if request.method == "GET":
        items = db.execute(
            "SELECT * FROM work_act_item WHERE act_id=? ORDER BY sort_order", (act_id,)
        ).fetchall()
        return render_template(
            "acts/form.html",
            mode="edit",
            act=act,
            items=items,
            counterparties=counterparties,
        )

    # POST — update draft
    act_number = request.form.get("act_number", "").strip()
    act_date = request.form.get("act_date", "").strip()
    period_from = request.form.get("period_from", "").strip()
    period_to = request.form.get("period_to", "").strip()
    project_id = request.form.get("project_id") or None
    now = utc_now()

    items = []
    idx = 0
    while True:
        desc = request.form.get("item_desc_{}".format(idx))
        if desc is None:
            break
        if not desc.strip():
            idx += 1
            continue
        qty_text = request.form.get("item_qty_{}".format(idx), "0")
        price_text = request.form.get("item_price_{}".format(idx), "0")
        vat_bp = int(request.form.get("item_vat_{}".format(idx), "2000"))
        qty_milli = parse_qty(qty_text) if qty_text else 1000
        price_minor = parse_rubles(price_text) if price_text else 0
        amount = (qty_milli * price_minor + 500) // 1000
        vat_amount = (amount * vat_bp + 5000) // 10000
        items.append(
            {
                "id": make_id("wai", act_id, str(idx + 1)),
                "line_no": idx + 1,
                "description": desc.strip(),
                "unit_code": request.form.get("item_unit_{}".format(idx), "JOB"),
                "quantity_milli": qty_milli,
                "price_minor": price_minor,
                "amount_minor": amount,
                "vat_rate_basis_points": vat_bp,
                "vat_amount_minor": vat_amount,
                "sort_order": idx + 1,
            }
        )
        idx += 1

    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute(
            "UPDATE work_act SET act_number=?, act_date=?, period_from=?, period_to=?, project_id=?, updated_at=? WHERE id=?",
            (act_number, act_date, period_from, period_to, project_id, now, act_id),
        )
        db.execute("DELETE FROM work_act_item WHERE act_id=?", (act_id,))
        for it in items:
            db.execute(
                "INSERT INTO work_act_item (id,act_id,line_no,description,unit_code,quantity_milli,price_minor,amount_minor,vat_rate_basis_points,vat_amount_minor,sort_order) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (
                    it["id"],
                    act_id,
                    it["line_no"],
                    it["description"],
                    it["unit_code"],
                    it["quantity_milli"],
                    it["price_minor"],
                    it["amount_minor"],
                    it["vat_rate_basis_points"],
                    it["vat_amount_minor"],
                    it["sort_order"],
                ),
            )
        recalculate_totals(act_id)
        db.commit()
        flash(_("Акт обновлён"), "success")
        return redirect(url_for("act_detail", act_id=act_id))
    except Exception as exc:
        if db.in_transaction:
            db.rollback()
        flash(_("Ошибка: %(error)s", error=exc), "error")
        return render_template(
            "acts/form.html", mode="edit", act=act, counterparties=counterparties
        ), 400


@app.route("/acts/<act_id>/status", methods=["POST"])
def act_status_change(act_id):
    db = get_db()
    act = db.execute(
        "SELECT status FROM work_act WHERE id=? AND deleted_at IS NULL", (act_id,)
    ).fetchone()
    if not act:
        abort(404)

    to_status = request.form.get("to_status", "")
    reason = request.form.get("reason", "")
    now = utc_now()

    valid = ACT_TRANSITIONS.get(act["status"], [])
    if to_status not in valid:
        flash(
            _(
                "Недопустимый переход: %(src)s → %(dst)s",
                src=act["status"],
                dst=to_status,
            ),
            "error",
        )
        return redirect(url_for("act_detail", act_id=act_id))

    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute(
            "UPDATE work_act SET status=?, updated_at=? WHERE id=?",
            (to_status, now, act_id),
        )
        db.execute(
            "INSERT INTO work_act_status_history (id,act_id,from_status,to_status,changed_by,changed_at,reason) VALUES (?,?,?,?,?,?,?)",
            (
                make_id("wsh", act_id, to_status),
                act_id,
                act["status"],
                to_status,
                "web_user",
                now,
                reason,
            ),
        )
        db.commit()
        labels = _status_labels()
        flash(
            _("Статус изменён: %(status)s", status=labels.get(to_status, to_status)),
            "success",
        )
    except Exception as exc:
        if db.in_transaction:
            db.rollback()
        flash(_("Ошибка: %(error)s", error=exc), "error")
    return redirect(url_for("act_detail", act_id=act_id))


@app.route("/acts/<act_id>/preview")
def act_preview(act_id):
    db = get_db()
    act = db.execute(
        "SELECT wa.*, t.name AS tenant_name, cp.full_name AS counterparty_name, cp.inn AS counterparty_inn, cp.kpp AS counterparty_kpp, cp.legal_address AS counterparty_address, ct.contract_number, ct.contract_date FROM work_act wa JOIN tenant t ON t.id=wa.tenant_id JOIN counterparty cp ON cp.id=wa.counterparty_id JOIN contract ct ON ct.id=wa.contract_id WHERE wa.id=?",
        (act_id,),
    ).fetchone()
    if not act:
        abort(404)
    items = [
        dict(r)
        for r in db.execute(
            "SELECT * FROM work_act_item WHERE act_id=? ORDER BY sort_order", (act_id,)
        ).fetchall()
    ]
    revision = db.execute(
        "SELECT * FROM work_act_revision WHERE id=?", (act["current_revision_id"],)
    ).fetchone()
    act_dict = dict(act)
    return render_template(
        "acts/preview.html",
        act=act_dict,
        items=items,
        revision=dict(revision) if revision else None,
    )


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------
@app.route("/projects")
def projects_list():
    db = get_db()
    status_filter = request.args.get("status", "")
    if status_filter in PROJECT_STATUSES:
        rows = db.execute(
            "SELECT * FROM v_nocodb_project_overview WHERE tenant_id = ? AND status = ? ORDER BY started_on DESC",
            (TENANT_ID, status_filter),
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM v_nocodb_project_overview WHERE tenant_id = ? ORDER BY started_on DESC",
            (TENANT_ID,),
        ).fetchall()
    return render_template(
        "projects/list.html",
        projects=rows,
        current_filter=status_filter,
        statuses=PROJECT_STATUSES,
    )


@app.route("/projects/new", methods=["GET", "POST"])
def project_new():
    db = get_db()
    counterparties = db.execute(
        "SELECT id, full_name FROM counterparty WHERE tenant_id = ? AND is_active = 1 ORDER BY full_name",
        (TENANT_ID,),
    ).fetchall()

    if request.method == "GET":
        return render_template("projects/form.html", counterparties=counterparties)

    cp_id = request.form.get("counterparty_id")
    code = request.form.get("code", "").strip()
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip() or None
    started_on = request.form.get("started_on", "").strip()
    now = utc_now()
    proj_id = make_id("proj", TENANT_ID, code)

    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute(
            "INSERT INTO project (id,tenant_id,counterparty_id,code,name,description,status,started_on,created_by,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                proj_id,
                TENANT_ID,
                cp_id,
                code,
                name,
                description,
                "active",
                started_on,
                "web_user",
                now,
                now,
            ),
        )
        db.execute(
            "INSERT INTO project_status_history (id,project_id,from_status,to_status,changed_by,changed_at,reason) VALUES (?,?,?,?,?,?,?)",
            (
                make_id("psh", proj_id, "active"),
                proj_id,
                None,
                "active",
                "web_user",
                now,
                _("Создан через веб-UI"),
            ),
        )
        db.commit()
        flash(_("Проект %(code)s создан", code=code), "success")
        return redirect(url_for("project_detail", proj_id=proj_id))
    except Exception as exc:
        if db.in_transaction:
            db.rollback()
        flash(_("Ошибка: %(error)s", error=exc), "error")
        return render_template("projects/form.html", counterparties=counterparties), 400


@app.route("/projects/<proj_id>")
def project_detail(proj_id):
    db = get_db()
    project = db.execute("SELECT * FROM project WHERE id=?", (proj_id,)).fetchone()
    if not project:
        abort(404)
    project = dict(project)

    acts = db.execute(
        """SELECT wa.id, wa.act_number, wa.act_date, wa.status AS act_status,
                  wa.grand_total_amount_minor, wa.period_from, wa.period_to,
                  c.contract_number, c.contract_date,
                  cp.full_name AS counterparty_name
           FROM work_act wa
           JOIN contract c ON c.id = wa.contract_id
           JOIN counterparty cp ON cp.id = wa.counterparty_id
           WHERE wa.project_id = ? AND wa.deleted_at IS NULL
           ORDER BY wa.act_date""",
        (proj_id,),
    ).fetchall()

    journal = db.execute(
        "SELECT id, entry_date, kind, title, decision_made FROM project_journal "
        "WHERE project_id = ? ORDER BY entry_date DESC, recorded_at DESC",
        (proj_id,),
    ).fetchall()

    history = db.execute(
        "SELECT changed_at, from_status, to_status, reason "
        "FROM project_status_history WHERE project_id = ? ORDER BY changed_at DESC",
        (proj_id,),
    ).fetchall()

    valid_transitions = []
    if project["status"] in PROJECT_TRANSITIONS:
        valid_transitions = PROJECT_TRANSITIONS[project["status"]]

    # Signed totals from view — сумма только подписанных актов
    stats = db.execute(
        "SELECT signed_act_count, signed_total_minor "
        "FROM v_nocodb_project_overview WHERE id = ?",
        (proj_id,),
    ).fetchone()
    signed_count = stats["signed_act_count"] if stats else 0
    signed_total_minor = stats["signed_total_minor"] if stats else 0
    project["signed_act_count"] = signed_count
    project["signed_total_minor"] = signed_total_minor

    return render_template(
        "projects/detail.html",
        project=project,
        acts=acts,
        journal=journal,
        history=history,
        valid_transitions=valid_transitions,
    )


# ---------------------------------------------------------------------------
# Project edit (GET/POST)
# ---------------------------------------------------------------------------
@app.route("/projects/<proj_id>/status", methods=["POST"])
def project_change_status(proj_id):
    db = get_db()
    to_status = request.form.get("to_status")
    reason = request.form.get("reason", "").strip() or None
    finished_on = request.form.get("finished_on")

    project = db.execute(
        "SELECT id, status FROM project WHERE id=?", (proj_id,)
    ).fetchone()
    if not project:
        abort(404)

    valid = PROJECT_TRANSITIONS.get(project["status"], [])
    if to_status not in valid:
        flash(
            _(
                "Недопустимый переход: %(src)s → %(dst)s",
                src=project["status"],
                dst=to_status,
            ),
            "error",
        )
        return redirect(url_for("project_detail", proj_id=proj_id))

    try:
        db.execute("BEGIN IMMEDIATE")
        now = utc_now()
        db.execute(
            "UPDATE project SET status=?, updated_at=? WHERE id=?",
            (to_status, now, proj_id),
        )
        db.execute(
            "INSERT INTO project_status_history (id,project_id,from_status,to_status,changed_by,changed_at,reason) "
            "VALUES (?,?,?,?,?,?,?)",
            (
                make_id("psh", proj_id, to_status, now),
                proj_id,
                project["status"],
                to_status,
                "web_user",
                now,
                reason,
            ),
        )
        db.commit()
        flash(_("Статус проекта изменён"), "success")
    except Exception as exc:
        if db.in_transaction:
            db.rollback()
        flash(_("Ошибка: %(error)s", error=exc), "error")

    return redirect(url_for("project_detail", proj_id=proj_id))


# ---------------------------------------------------------------------------
# Project edit (GET/POST) — moved below detail to keep endpoints grouped
# ---------------------------------------------------------------------------


@app.route("/projects/<proj_id>/journal/new", methods=["GET", "POST"])
def journal_new(proj_id):
    db = get_db()
    proj = db.execute(
        "SELECT id, tenant_id, counterparty_id, code FROM project WHERE id=?",
        (proj_id,),
    ).fetchone()
    if not proj:
        abort(404)

    linked_acts = db.execute(
        "SELECT wa.id, wa.act_number FROM work_act wa WHERE wa.project_id=? AND wa.deleted_at IS NULL ORDER BY wa.act_date",
        (proj_id,),
    ).fetchall()

    if request.method == "GET":
        return render_template(
            "journal/form.html", project=proj, linked_acts=linked_acts
        )

    kind = request.form.get("kind")
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip() or None
    decision_made = request.form.get("decision_made", "").strip() or None
    outcome = request.form.get("outcome", "").strip() or None
    entry_date = request.form.get("entry_date", "").strip()
    now = utc_now()
    entry_id = make_id("pj", proj_id, title, entry_date)

    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute(
            "INSERT INTO project_journal (id,project_id,tenant_id,entry_date,kind,title,body,decision_made,outcome,recorded_by,recorded_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                entry_id,
                proj_id,
                TENANT_ID,
                entry_date,
                kind,
                title,
                body,
                decision_made,
                outcome,
                "web_user",
                now,
            ),
        )
        for act_id in request.form.getlist("linked_act_ids"):
            db.execute(
                "INSERT INTO project_journal_act (journal_id, act_id) VALUES (?,?)",
                (entry_id, act_id),
            )
        db.commit()
        flash(_("Запись журнала добавлена"), "success")
        return redirect(url_for("project_detail", proj_id=proj_id))
    except Exception as exc:
        if db.in_transaction:
            db.rollback()
        flash(_("Ошибка: %(error)s", error=exc), "error")
        return render_template(
            "journal/form.html", project=proj, linked_acts=linked_acts
        ), 400


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------
@app.route("/api/contracts")
def api_contracts():
    cp_id = request.args.get("counterparty_id")
    db = get_db()
    rows = db.execute(
        "SELECT id, contract_number, contract_date, vat_mode FROM contract WHERE tenant_id=? AND counterparty_id=? ORDER BY contract_date DESC",
        (TENANT_ID, cp_id),
    ).fetchall()
    return json.dumps([dict(r) for r in rows])


@app.route("/api/projects")
def api_projects():
    cp_id = request.args.get("counterparty_id")
    db = get_db()
    rows = db.execute(
        "SELECT id, code, name FROM project WHERE tenant_id=? AND counterparty_id=? AND status IN ('active','on_hold') ORDER BY code",
        (TENANT_ID, cp_id),
    ).fetchall()
    return json.dumps([dict(r) for r in rows])


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------
@app.route("/admin/regenerate", methods=["GET", "POST"])
def regenerate_artifacts():
    try:
        subprocess.run(
            [sys.executable, str(ROOT_DIR / "scripts/gen_artifacts.py")],
            check=True,
            capture_output=True,
            text=True,
        )
        flash(_("HTML-артефакты обновлены"), "success")
    except Exception as exc:
        flash(_("Ошибка регенерации: %(error)s", error=exc), "error")
    return redirect(request.referrer or url_for("dashboard"))


@app.route("/artifacts/<path:path>")
def serve_artifact(path):
    return send_from_directory(str(ARTIFACTS_DIR), path)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pacus Web UI")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    app.run(host="127.0.0.1", port=args.port, debug=args.debug)
