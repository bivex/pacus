#!/usr/bin/env python3
"""
Generate HTML artifacts (project cards + act audit trails) from the SQLite DB.

Usage:
    python3 scripts/gen_artifacts.py
    python3 scripts/gen_artifacts.py --db data/sqlite/work_acts_demo.sqlite --out data/artifacts
"""

import sqlite3, os, sys, argparse
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_DB = Path(__file__).parent.parent / "data/sqlite/work_acts_demo.sqlite"
DEFAULT_OUT = Path(__file__).parent.parent / "data/artifacts"

# ---------------------------------------------------------------------------
# Shared HTML fragments
# ---------------------------------------------------------------------------
INLINE_CSS = """\
<style>
@page { size: A4; margin: 16mm 14mm 18mm; }
* { box-sizing: border-box; }
body { margin: 0; background: #f3f4f6; color: #111827; font: 14px/1.45 Inter, "Segoe UI", Arial, sans-serif; }
main { max-width: 860px; margin: 24px auto; background: #fff; padding: 18mm 16mm; box-shadow: 0 10px 30px rgba(0,0,0,.08); }
h1, h2, h3, p { margin: 0 0 10px; }
h1 { font-size: 24px; }
h2 { font-size: 16px; margin-top: 18px; }
table { width: 100%; border-collapse: collapse; margin: 12px 0 16px; }
th, td { border: 1px solid #d1d5db; padding: 8px 10px; vertical-align: top; }
th { background: #f9fafb; text-align: left; }
.topbar { display: flex; justify-content: space-between; gap: 12px; align-items: center; margin-bottom: 16px; }
.muted { color: #6b7280; }
.amount { text-align: right; white-space: nowrap; }
.right { text-align: right; }
.signature { height: 54px; border-bottom: 1px solid #9ca3af; margin-top: 24px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 20px; }
.no-print button, .no-print a, button { background: #111827; color: #fff; border: none; border-radius: 6px; padding: 8px 12px; text-decoration: none; cursor: pointer; }
.actions { display: flex; gap: 10px; }
/* Zebra striping for visual scanning (ISO 9241-12) */
tbody tr:nth-child(even) { background: #f9fafb; }
/* Keyboard focus indicators (ISO 9241-171) */
a:focus-visible, button:focus-visible { outline: 2px solid #005fcc; outline-offset: 2px; }
/* Status text labels (ISO 9241-171 - not colour alone) */
.status-label { font-size: 12px; padding: 2px 6px; border-radius: 3px; margin-left: 6px; }
.status-draft { background: #fef3c7; color: #92400e; }
.status-generated { background: #dbeafe; color: #1e40af; }
.status-sent { background: #fce7f3; color: #9a3412; }
.status-signed { background: #dcfce7; color: #166534; }
.status-cancelled { background: #fee2e2; color: #991b1b; }
.status-corrected { background: #f3e8ff; color: #5b21b6; }
@media print {
  body { background: #fff; }
  main { max-width: none; margin: 0; box-shadow: none; padding: 0; }
  .no-print { display: none !important; }
  thead { display: table-header-group; }
  tr, img { break-inside: avoid; }
  .status-label { background: transparent !important; color: #000 !important; border: 1px solid #000; }
}
</style>"""
CURRENCY_HEAD = "<script>const CURRENCY = '$'; // \u043c\u0435\u043d\u044f \u0437\u0430\u0439\u0442\u0430: $, \u20ac, \u20bd, \u00a3 ..."
CURRENCY_BODY = '<script>document.querySelectorAll(".sym").forEach(e=>e.textContent=CURRENCY);var _c={"$":"USD","\u20ac":"EUR","\u20bd":"RUB","\u00a3":"GBP"};document.querySelectorAll(".sym-code").forEach(e=>e.textContent=_c[CURRENCY]||CURRENCY);</script>'

CURRENCY_HEAD = "<script>const CURRENCY = '$'; // \u2190 \u043c\u0435\u043d\u044f\u0439 \u0437\u0434\u0435\u0441\u044c: $, \u20ac, \u20bd, \u00a3 ...</script>"
CURRENCY_BODY = '<script>document.querySelectorAll(".sym").forEach(e=>e.textContent=CURRENCY);var _c={"$":"USD","\u20ac":"EUR","\u20bd":"RUB","\u00a3":"GBP"};document.querySelectorAll(".sym-code").forEach(e=>e.textContent=_c[CURRENCY]||CURRENCY);</script>'

SYM = '<span class="sym"></span>'
SYMC = '<span class="sym-code"></span>'


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def rel(from_file: Path, to_file: Path) -> str:
    """Relative path from from_file's directory to to_file."""
    return os.path.relpath(to_file, from_file.parent).replace("\\", "/")


def act_html_path(out_dir: Path, tenant_id: str, act_id: str, act_date: str) -> Path:
    return out_dir / "acts" / tenant_id / act_date[:4] / act_id / "rev-1" / "act.html"


def act_audit_path(out_dir: Path, tenant_id: str, act_id: str, act_date: str) -> Path:
    return out_dir / "acts" / tenant_id / act_date[:4] / act_id / "audit" / "audit.html"


def project_card_path(out_dir: Path, tenant_id: str, proj_id: str) -> Path:
    return out_dir / "projects" / tenant_id / proj_id / "project-card.html"


def journal_entry_path(
    out_dir: Path, tenant_id: str, proj_id: str, entry_id: str
) -> Path:
    return out_dir / "projects" / tenant_id / proj_id / "journal" / f"{entry_id}.html"


def fmt_date(iso: Optional[str]) -> str:
    if not iso:
        return "—"
    try:
        y, m, d = iso[:10].split("-")
        return f"{d}.{m}.{y}"
    except Exception:
        return iso


def fmt_dt(iso: Optional[str]) -> str:
    if not iso:
        return "—"
    try:
        return f"{fmt_date(iso[:10])} {iso[11:16]}"
    except Exception:
        return iso


def fmt_amount(minor: Optional[int]) -> str:
    if minor is None:
        return "—"
    rubles = minor / 100
    integer = int(rubles)
    frac = round((rubles - integer) * 100)
    s = f"{integer:,}".replace(",", "\u202f")
    return f"{s},{frac:02d}"


def dash(v) -> str:
    return v if v else "—"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Project card
# ---------------------------------------------------------------------------
def render_project_card(
    proj: dict,
    history: list,
    acts: list,
    journal: list,
    journal_acts: dict,
    self_path: Path,
    out_dir: Path,
) -> str:
    code = proj["code"]
    name = proj["name"]
    status = proj["status"]
    cp_name = proj["counterparty_name"]
    tenant_name = proj["tenant_name"]
    started = fmt_date(proj["started_on"])
    ended = fmt_date(proj["finished_on"])
    desc = proj["description"] or ""
    created_by = proj["created_by"]
    created_at = fmt_date(proj["created_at"])

    index_href = rel(self_path, out_dir / "index.html")

    hist_rows = ""
    for h in history:
        from_s = (
            "<span class='muted'>—</span>" if not h["from_status"] else h["from_status"]
        )
        hist_rows += (
            f"<tr>"
            f"<td>{fmt_dt(h['changed_at'])}</td>"
            f"<td>{from_s}</td>"
            f"<td><strong>{h['to_status']}</strong></td>"
            f"<td>{dash(h['changed_by'])}</td>"
            f"<td>{dash(h['reason'])}</td>"
            f"</tr>\n"
        )

    act_rows = ""
    grand_total = 0
    for a in acts:
        amount = a["grand_total_amount_minor"] or 0
        grand_total += amount
        html_href = rel(
            self_path,
            act_html_path(out_dir, a["tenant_id"], a["act_id"], a["act_date"]),
        )
        audit_href = rel(
            self_path,
            act_audit_path(out_dir, a["tenant_id"], a["act_id"], a["act_date"]),
        )
        links = f'<a href="{html_href}">HTML</a> · <a href="{audit_href}">Аудит</a>'
        act_rows += (
            f"<tr>"
            f"<td>{a['act_number']}</td>"
            f"<td>{fmt_date(a['act_date'])}</td>"
            f"<td>{fmt_date(a['period_from'])} — {fmt_date(a['period_to'])}</td>"
            f"<td>{a['act_status']}</td>"
            f"<td class='amount'>{fmt_amount(amount)} {SYM}</td>"
            f"<td>{links}</td>"
            f"</tr>\n"
        )

    n_acts = len(acts)
    acts_label = "акт" if n_acts == 1 else "актов"

    KIND_LABEL = {
        "decision": "Решение",
        "result": "Результат",
        "note": "Заметка",
        "milestone": "Веха",
    }

    journal_rows = ""
    for entry in journal:
        linked = journal_acts.get(entry["id"], [])
        if linked:
            parts = []
            for a in linked:
                href = rel(
                    self_path,
                    act_html_path(
                        out_dir, proj["tenant_id"], a["act_id"], a["act_date"]
                    ),
                )
                parts.append(f'<a href="{href}">{a["act_number"]}</a>')
            act_links = ", ".join(parts)
        else:
            act_links = "—"

        detail_parts = []
        if entry.get("decision_made"):
            detail_parts.append(f"<em>Решение:</em> {entry['decision_made']}")
        if entry.get("outcome"):
            detail_parts.append(f"<em>Итог:</em> {entry['outcome']}")
        if entry.get("body"):
            detail_parts.append(entry["body"])
        detail_html = "<br>".join(detail_parts) if detail_parts else ""

        entry_href = rel(
            self_path,
            journal_entry_path(out_dir, proj["tenant_id"], proj["id"], entry["id"]),
        )
        title_cell = f'<a href="{entry_href}"><strong>{entry["title"]}</strong></a>'
        if detail_html:
            title_cell += f"<br><span class='muted'>{detail_html}</span>"

        journal_rows += (
            f"<tr>"
            f"<td>{fmt_date(entry['entry_date'])}</td>"
            f"<td>{KIND_LABEL.get(entry['kind'], entry['kind'])}</td>"
            f"<td>{title_cell}</td>"
            f"<td>{act_links}</td>"
            f"<td class='muted'>{dash(entry['recorded_by'])}</td>"
            f"</tr>\n"
        )

    return f"""\
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Проект {code}</title>
{INLINE_CSS}
{CURRENCY_HEAD}
</head>
<body>
<main>
  <div class="topbar no-print">
    <div>
      <h1>Проект {code} — {name}</h1>
      <p class="muted">Статус: <span class="status-label status-{status}">{status}</span> · {tenant_name} · {cp_name}</p>
    </div>
    <div class="actions"><a href="{index_href}" aria-label="Вернуться к списку проектов">К списку</a><button onclick="window.print()" aria-label="Печать страницы">Печать</button></div>
  </div>

  <h1>Проект {code}</h1>
  <p>{name}</p>

  <div class="grid">
    <div>
      <p><strong>Организация:</strong> {tenant_name}</p>
      <p><strong>Контрагент:</strong> {cp_name}</p>
      <p><strong>Статус:</strong> <span class="status-label status-{status}">{status}</span></p>
    </div>
    <div>
      <p><strong>Начало:</strong> {started}</p>
      <p><strong>Завершение:</strong> {ended}</p>
      <p><strong>Создан:</strong> {created_at} · {created_by}</p>
    </div>
  </div>
  {"<p class='muted'>" + desc + "</p>" if desc else ""}

  <h2>История статусов</h2>
  <table aria-label="История изменения статусов акта">
    <thead><tr><th scope="col">Дата и время</th><th scope="col">Из</th><th scope="col">В</th><th scope="col">Пользователь</th><th scope="col">Причина</th></tr></thead>
    <tbody>
{hist_rows}    </tbody>
  </table>

  <h2>Акты работ по проекту</h2>
  <table aria-label="Список актов работ по проекту">
    <thead><tr><th scope="col">Номер акта</th><th scope="col">Дата</th><th scope="col">Период</th><th scope="col">Статус</th><th scope="col">Итого</th><th scope="col">Ссылки</th></tr></thead>
    <tbody>
{act_rows}    </tbody>
    <tfoot>
      <tr>
        <th colspan="4" class="right">Итого по проекту ({n_acts} {acts_label})</th>
        <th class="amount">{fmt_amount(grand_total)} {SYM}</th>
        <th></th>
      </tr>
    </tfoot>
  </table>

  <h2>Журнал решений и событий</h2>
  <table aria-label="Журнал решений и событий проекта">
    <thead><tr><th scope="col">Дата</th><th scope="col">Тип</th><th scope="col">Событие / Решение</th><th scope="col">Акты</th><th scope="col">Записал</th></tr></thead>
    <tbody>
{journal_rows}    </tbody>
  </table>

  <p class="muted">Документ сформирован автоматически из БД · {tenant_name}<br>
  <a href="/contact.html" aria-label="Контактная информация">Контакты</a> ·
  <a href="/privacy.html" aria-label="Политика конфиденциальности">Приватность</a> ·
  <a href="/feedback.html" aria-label="Отправить отзыв">Обратная связь</a></p>
</main>
{CURRENCY_BODY}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Journal entry detail page
# ---------------------------------------------------------------------------
KIND_LABEL = {
    "decision": "Решение",
    "result": "Результат",
    "note": "Заметка",
    "milestone": "Веха",
}


def render_journal_entry(
    entry: dict, proj: dict, linked_acts: list, self_path: Path, out_dir: Path
) -> str:
    card_href = rel(
        self_path, project_card_path(out_dir, proj["tenant_id"], proj["id"])
    )
    index_href = rel(self_path, out_dir / "index.html")
    kind_label = KIND_LABEL.get(entry["kind"], entry["kind"])

    # Linked acts table
    act_rows = ""
    for a in linked_acts:
        html_href = rel(
            self_path,
            act_html_path(out_dir, proj["tenant_id"], a["act_id"], a["act_date"]),
        )
        audit_href = rel(
            self_path,
            act_audit_path(out_dir, proj["tenant_id"], a["act_id"], a["act_date"]),
        )
        act_rows += (
            f"<tr>"
            f"<td><a href='{html_href}'>{a['act_number']}</a></td>"
            f"<td>{fmt_date(a['act_date'])}</td>"
            f"<td>{a['act_status']}</td>"
            f"<td><a href='{audit_href}'>Аудит</a></td>"
            f"</tr>\n"
        )

    acts_section = ""
    if act_rows:
        acts_section = f"""\
  <h2>Связанные акты</h2>
  <table>
    <thead><tr><th scope="col">Акт</th><th scope="col">Дата</th><th scope="col">Статус</th><th scope="col">Аудит</th></tr></thead>
    <tbody>
{act_rows}    </tbody>
  </table>"""

    def field_row(label: str, value: Optional[str]) -> str:
        if not value:
            return ""
        return f"<tr><th style='width:28%'>{label}</th><td>{value}</td></tr>\n"

    detail_rows = (
        field_row("Тип записи", kind_label)
        + field_row("Дата события", fmt_date(entry["entry_date"]))
        + field_row(
            "Проект", f'<a href="{card_href}">{proj["code"]} — {proj["name"]}</a>'
        )
        + field_row("Записал", entry.get("recorded_by"))
        + field_row("Записано", fmt_dt(entry.get("recorded_at")))
    )

    body_section = ""
    if entry.get("body"):
        body_section = f"<h2>Описание</h2><p>{entry['body']}</p>"

    decision_section = ""
    if entry.get("decision_made"):
        decision_section = f"<h2>Принятое решение</h2><p>{entry['decision_made']}</p>"

    outcome_section = ""
    if entry.get("outcome"):
        outcome_section = f"<h2>Результат / Итог</h2><p>{entry['outcome']}</p>"

    return f"""\
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{kind_label}: {entry["title"]}</title>
{INLINE_CSS}
</head>
<body>
<main>
  <div class="topbar no-print">
    <div>
      <h1>{kind_label}: {entry["title"]}</h1>
      <p class="muted">{fmt_date(entry["entry_date"])} · Проект {proj["code"]}</p>
    </div>
    <div class="actions">
      <a href="{card_href}" aria-label="Вернуться к карточке проекта">К проекту</a>
      <a href="{index_href}" aria-label="Вернуться к списку проектов">К списку</a>
      <button onclick="window.print()" aria-label="Печать страницы">Печать</button>
    </div>
  </div>

  <h1>{entry["title"]}</h1>

  <table>
    <tbody>
{detail_rows}    </tbody>
  </table>

{body_section}
{decision_section}
{outcome_section}
{acts_section}

  <p class="muted">Запись журнала проекта · {proj["tenant_name"]}</p>
</main>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Act audit trail
# ---------------------------------------------------------------------------
def render_act_audit(
    act: dict,
    history: list,
    revisions: list,
    correction: Optional[dict],
    self_path: Path,
    out_dir: Path,
) -> str:
    act_number = act["act_number"]
    status = act["status"]
    cp_name = act["counterparty_name"]
    contract = act["contract_number"]
    proj_code = act["project_code"] or "—"
    proj_name = act["project_name"] or ""
    proj_id = act["project_id"]
    tenant_id = act["tenant_id"]
    tenant_name = act["tenant_name"]
    act_date = fmt_date(act["act_date"])
    period = f"{fmt_date(act['period_from'])} — {fmt_date(act['period_to'])}"

    index_href = rel(self_path, out_dir / "index.html")
    own_act_href = rel(
        self_path, act_html_path(out_dir, tenant_id, act["act_id"], act["act_date"])
    )

    hist_rows = ""
    for h in history:
        from_s = (
            "<span class='muted'>—</span>" if not h["from_status"] else h["from_status"]
        )
        hist_rows += (
            f"<tr>"
            f"<td>{fmt_dt(h['changed_at'])}</td>"
            f"<td>{from_s}</td>"
            f"<td><strong>{h['to_status']}</strong></td>"
            f"<td>{dash(h['changed_by'])}</td>"
            f"<td>{dash(h['reason'])}</td>"
            f"</tr>\n"
        )

    rev_rows = ""
    for r in revisions:
        immut = "<strong>да</strong>" if r["is_immutable"] else "нет"
        html_link = "—"
        if r["html_path"]:
            target = out_dir / r["html_path"]
            html_link = f'<a href="{rel(self_path, target)}">HTML</a>'
        rev_rows += (
            f"<tr>"
            f"<td>{r['revision_no']}</td>"
            f"<td>{r['revision_kind']}</td>"
            f"<td>{r['template_version'] or '—'}</td>"
            f"<td>{fmt_dt(r['created_at'])}</td>"
            f"<td>{dash(r['created_by'])}</td>"
            f"<td>{dash(r['comment'])}</td>"
            f"<td>{immut}</td>"
            f"<td>{html_link}</td>"
            f"</tr>\n"
        )

    related_rows = ""
    if correction:
        href = rel(
            self_path,
            act_html_path(
                out_dir, tenant_id, correction["act_id"], correction["act_date"]
            ),
        )
        related_rows += (
            f"<tr><td>Корректировочный акт</td><td>{correction['act_number']}</td>"
            f"<td>{correction['status']}</td><td><a href='{href}'>Открыть</a></td></tr>\n"
        )
    if proj_id:
        href = rel(self_path, project_card_path(out_dir, tenant_id, proj_id))
        related_rows += (
            f"<tr><td>Карточка проекта</td><td>{proj_code}</td>"
            f"<td>{proj_name}</td><td><a href='{href}'>Открыть</a></td></tr>\n"
        )

    related_section = ""
    if related_rows:
        related_section = f"""
  <h2>Связанные документы</h2>
  <table>
    <thead><tr><th>Тип</th><th>Номер / Код</th><th>Статус / Название</th><th>Ссылка</th></tr></thead>
    <tbody>
{related_rows}    </tbody>
  </table>"""

    proj_line = (
        f"<p><strong>Проект:</strong> {proj_code} — {proj_name}</p>" if proj_id else ""
    )

    return f"""\
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Аудит акта {act_number}</title>
{INLINE_CSS}
{CURRENCY_HEAD}
</head>
<body>
<main>
  <div class="topbar no-print">
    <div>
      <h1>Аудит акта {act_number}</h1>
      <p class="muted">Статус: <span class="status-label status-{status}">{status}</span> · {cp_name} · Проект: {proj_code}</p>
    </div>
    <div class="actions">
      <a href="{own_act_href}">Акт</a>
      <a href="{index_href}">К списку</a>
      <button onclick="window.print()">Печать</button>
    </div>
  </div>

  <h1>Аудит: Акт {act_number}</h1>

  <div class="grid">
    <div>
      <p><strong>Исполнитель:</strong> {tenant_name}</p>
      <p><strong>Заказчик:</strong> {cp_name}</p>
      <p><strong>Договор:</strong> {contract}</p>
      {proj_line}
    </div>
    <div>
      <p><strong>Дата акта:</strong> {act_date}</p>
      <p><strong>Период:</strong> {period}</p>
      <p><strong>Текущий статус:</strong> <span class="status-label status-{status}">{status}</span></p>
    </div>
  </div>

  <h2>Хронология статусов</h2>
  <table>
    <thead><tr><th>Дата и время</th><th>Из</th><th>В</th><th>Пользователь</th><th>Причина</th></tr></thead>
    <tbody>
{hist_rows}    </tbody>
  </table>

  <h2>Ревизии документа</h2>
  <table>
    <thead><tr><th>№</th><th>Вид</th><th>Шаблон</th><th>Создана</th><th>Создал</th><th>Комментарий</th><th>Иммут.</th><th>Артефакт</th></tr></thead>
    <tbody>
{rev_rows}    </tbody>
  </table>
{related_section}

  <p class="muted">Аудит-трейл сформирован автоматически из БД · {tenant_name}</p>
</main>
{CURRENCY_BODY}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Main: query DB and generate files
# ---------------------------------------------------------------------------
def generate(db_path: Path, out_dir: Path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # ---- Projects ----
    projects = conn.execute("""
        SELECT p.id, p.code, p.name, p.description, p.status,
               p.started_on, p.finished_on, p.tenant_id,
               p.created_by, p.created_at,
               t.name AS tenant_name,
               cp.full_name AS counterparty_name
        FROM project p
        JOIN tenant t ON t.id = p.tenant_id
        JOIN counterparty cp ON cp.id = p.counterparty_id
        ORDER BY p.tenant_id, p.code
    """).fetchall()

    for proj in projects:
        proj = dict(proj)

        history = conn.execute(
            """
            SELECT from_status, to_status, changed_by, changed_at, reason
            FROM project_status_history
            WHERE project_id = ?
            ORDER BY changed_at
        """,
            (proj["id"],),
        ).fetchall()

        acts = conn.execute(
            """
            SELECT wa.id AS act_id, wa.tenant_id, wa.act_number, wa.act_date,
                   wa.period_from, wa.period_to, wa.status AS act_status,
                   wa.grand_total_amount_minor,
                   da.storage_path AS html_path
            FROM work_act wa
            LEFT JOIN work_act_revision rev ON rev.id = wa.current_revision_id
            LEFT JOIN document_artifact da ON da.id = rev.html_artifact_id
            WHERE wa.project_id = ?
            ORDER BY wa.period_from, wa.act_date
        """,
            (proj["id"],),
        ).fetchall()

        journal = conn.execute(
            """
            SELECT id, entry_date, kind, title, body, decision_made, outcome,
                   recorded_by, recorded_at
            FROM project_journal
            WHERE project_id = ?
            ORDER BY entry_date ASC, recorded_at ASC
        """,
            (proj["id"],),
        ).fetchall()

        journal_acts = {}
        for entry in journal:
            linked = conn.execute(
                """
                SELECT wa.id AS act_id, wa.act_number, wa.act_date, wa.status AS act_status
                FROM project_journal_act ja
                JOIN work_act wa ON wa.id = ja.act_id
                WHERE ja.journal_id = ?
                ORDER BY wa.period_from, wa.act_date
            """,
                (entry["id"],),
            ).fetchall()
            journal_acts[entry["id"]] = [dict(a) for a in linked]
        journal = [dict(e) for e in journal]

        self_path = project_card_path(out_dir, proj["tenant_id"], proj["id"])
        html = render_project_card(
            proj,
            history,
            [dict(a) for a in acts],
            journal,
            journal_acts,
            self_path,
            out_dir,
        )
        write_file(self_path, html)
        print(f"  project  {self_path.relative_to(out_dir)}")

        for entry in journal:
            e_path = journal_entry_path(
                out_dir, proj["tenant_id"], proj["id"], entry["id"]
            )
            e_html = render_journal_entry(
                entry, proj, journal_acts.get(entry["id"], []), e_path, out_dir
            )
            write_file(e_path, e_html)
            print(f"  journal  {e_path.relative_to(out_dir)}")

    # ---- Act audit trails ----
    acts = conn.execute("""
        SELECT wa.id AS act_id, wa.tenant_id, wa.act_number, wa.act_date,
               wa.period_from, wa.period_to, wa.status,
               wa.source_act_id, wa.project_id,
               t.name AS tenant_name,
               cp.full_name AS counterparty_name,
               ct.contract_number,
               p.code AS project_code,
               p.name AS project_name
        FROM work_act wa
        JOIN tenant t ON t.id = wa.tenant_id
        JOIN counterparty cp ON cp.id = wa.counterparty_id
        JOIN contract ct ON ct.id = wa.contract_id
        LEFT JOIN project p ON p.id = wa.project_id
        ORDER BY wa.tenant_id, wa.act_date
    """).fetchall()

    corrections = {a["source_act_id"]: dict(a) for a in acts if a["source_act_id"]}

    for act in acts:
        act = dict(act)

        history = conn.execute(
            """
            SELECT from_status, to_status, changed_by, changed_at, reason
            FROM work_act_status_history
            WHERE act_id = ?
            ORDER BY changed_at
        """,
            (act["act_id"],),
        ).fetchall()

        revisions = conn.execute(
            """
            SELECT r.revision_no, r.revision_kind, r.template_version,
                   r.created_by, r.created_at, r.comment, r.is_immutable,
                   da.storage_path AS html_path
            FROM work_act_revision r
            LEFT JOIN document_artifact da ON da.id = r.html_artifact_id
            WHERE r.act_id = ?
            ORDER BY r.revision_no
        """,
            (act["act_id"],),
        ).fetchall()

        self_path = act_audit_path(
            out_dir, act["tenant_id"], act["act_id"], act["act_date"]
        )
        html = render_act_audit(
            act,
            history,
            [dict(r) for r in revisions],
            corrections.get(act["act_id"]),
            self_path,
            out_dir,
        )
        write_file(self_path, html)
        print(f"  audit    {self_path.relative_to(out_dir)}")

    # ---- index.html ----
    all_projects = conn.execute("""
        SELECT p.id, p.code, p.name, p.status, p.tenant_id, cp.full_name AS cp_name
        FROM project p JOIN counterparty cp ON cp.id = p.counterparty_id
        ORDER BY p.tenant_id, p.code
    """).fetchall()

    all_acts = conn.execute("""
        SELECT wa.id, wa.tenant_id, wa.act_number, wa.act_date, wa.status,
               da.storage_path AS html_path
        FROM work_act wa
        LEFT JOIN work_act_revision rev ON rev.id = wa.current_revision_id
        LEFT JOIN document_artifact da ON da.id = rev.html_artifact_id
        ORDER BY wa.tenant_id, wa.act_date
    """).fetchall()

    index_path = out_dir / "index.html"

    proj_rows = ""
    for p in all_projects:
        card_href = rel(index_path, project_card_path(out_dir, p["tenant_id"], p["id"]))
        proj_rows += (
            f"        <tr><td>{p['code']} — {p['name']}</td>"
            f"<td>{p['cp_name']}</td><td>{p['status']}</td>"
            f"<td><a href='{card_href}'>Карточка</a></td></tr>\n"
        )

    act_rows_idx = ""
    for a in all_acts:
        html_href = rel(
            index_path, act_html_path(out_dir, a["tenant_id"], a["id"], a["act_date"])
        )
        audit_href = rel(
            index_path, act_audit_path(out_dir, a["tenant_id"], a["id"], a["act_date"])
        )
        html_link = f"<a href='{html_href}'>HTML</a>" if a["html_path"] else "—"
        act_rows_idx += (
            f"        <tr><td>{a['act_number']}</td><td>{a['status']}</td>"
            f"<td>{html_link}</td><td><a href='{audit_href}'>Аудит</a></td></tr>\n"
        )

    index_html = f"""\
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Print Center — Work Acts Demo</title>
  {INLINE_CSS}
</head>
<body>
  <main>
    <div class="topbar no-print">
      <div>
        <h1>Print Center — Work Acts Demo</h1>
        <p class="muted">Открывай нужный HTML-артефакт и печатай через браузер.</p>
      </div>
      <div class="actions"><button onclick="window.print()">Печать этой страницы</button></div>
    </div>

    <h2>Карточки проектов</h2>
    <table>
      <thead><tr><th>Проект</th><th>Контрагент</th><th>Статус</th><th>Ссылка</th></tr></thead>
      <tbody>
{proj_rows}      </tbody>
    </table>

    <h2>Акты работ</h2>
    <table>
      <thead><tr><th>Акт</th><th>Статус</th><th>Печать</th><th>Аудит</th></tr></thead>
      <tbody>
{act_rows_idx}      </tbody>
    </table>

    <p class="muted">Базовый URL print server: <strong>http://localhost:4000</strong></p>
  </main>
</body>
</html>
"""
    write_file(index_path, index_html)
    print(f"  index    index.html")

    conn.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate HTML artifacts from SQLite DB"
    )
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to SQLite database")
    parser.add_argument(
        "--out", default=str(DEFAULT_OUT), help="Output directory (artifacts root)"
    )
    args = parser.parse_args()

    db_path = Path(args.db)
    out_dir = Path(args.out)

    if not db_path.exists():
        print(f"DB not found: {db_path}", file=sys.stderr)
        sys.exit(1)

    print(f"DB:  {db_path}")
    print(f"Out: {out_dir}")
    generate(db_path, out_dir)
    print("Done.")
