#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def make_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:20]
    return f"{prefix}_{digest}"


def as_int(value, field: str) -> int:
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{field} must be an integer")
    return int(value)


def money_minor(item: dict, field: str) -> int:
    if field in item:
        return as_int(item[field], field)
    major_field = field.removesuffix("_minor")
    if major_field in item:
        return int(round(float(item[major_field]) * 100))
    raise ValueError(f"{field} is required")


def quantity_milli(item: dict) -> int:
    if "quantity_milli" in item:
        return as_int(item["quantity_milli"], "quantity_milli")
    if "quantity" in item:
        return int(round(float(item["quantity"]) * 1000))
    raise ValueError("quantity_milli or quantity is required")


def vat_basis_points(item: dict) -> int:
    if "vat_rate_basis_points" in item:
        return as_int(item["vat_rate_basis_points"], "vat_rate_basis_points")
    if "vat_rate_percent" in item:
        return int(round(float(item["vat_rate_percent"]) * 100))
    return 0


def round_div(value: int, divisor: int) -> int:
    return (value + divisor // 2) // divisor


def normalize_items(payload: dict) -> list[dict]:
    raw_items = payload.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise ValueError("payload.items must contain at least one line")
    items = []
    for idx, raw in enumerate(raw_items, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"items[{idx}] must be an object")
        description = str(raw.get("description", "")).strip()
        if not description:
            raise ValueError(f"items[{idx}] description is required")
        qty = quantity_milli(raw)
        price = money_minor(raw, "price_minor")
        vat_bp = vat_basis_points(raw)
        if qty <= 0 or price < 0 or vat_bp < 0:
            raise ValueError(f"items[{idx}] has invalid numeric values")
        amount = raw.get("amount_minor")
        amount_minor = (
            as_int(amount, f"items[{idx}].amount_minor")
            if amount is not None
            else round_div(qty * price, 1000)
        )
        vat_amount = raw.get("vat_amount_minor")
        vat_amount_minor = (
            as_int(vat_amount, f"items[{idx}].vat_amount_minor")
            if vat_amount is not None
            else round_div(amount_minor * vat_bp, 10000)
        )
        items.append(
            {
                "line_no": idx,
                "description": description,
                "unit_code": raw.get("unit_code"),
                "quantity_milli": qty,
                "price_minor": price,
                "amount_minor": amount_minor,
                "vat_rate_basis_points": vat_bp,
                "vat_amount_minor": vat_amount_minor,
                "sort_order": idx,
            }
        )
    return items


def find_one(
    conn: sqlite3.Connection, sql: str, params: tuple, error: str
) -> sqlite3.Row:
    rows = conn.execute(sql, params).fetchall()
    if len(rows) != 1:
        raise ValueError(error)
    return rows[0]


def upsert_draft(
    conn: sqlite3.Connection, inbox: sqlite3.Row, items: list[dict], now: str
) -> tuple[str, str]:
    actor = f"integration:{inbox['source_system']}"
    counterparty = find_one(
        conn,
        "SELECT id FROM counterparty WHERE tenant_id = ? AND inn = ? AND is_active = 1",
        (inbox["tenant_id"], inbox["counterparty_inn"]),
        f"counterparty with INN {inbox['counterparty_inn']} not found or ambiguous",
    )
    contract = find_one(
        conn,
        "SELECT id FROM contract WHERE tenant_id = ? AND counterparty_id = ? AND contract_number = ? AND contract_date = ?",
        (
            inbox["tenant_id"],
            counterparty["id"],
            inbox["contract_number"],
            inbox["contract_date"],
        ),
        f"contract {inbox['contract_number']} / {inbox['contract_date']} not found or ambiguous",
    )
    total_amount = sum(item["amount_minor"] for item in items)
    total_vat = sum(item["vat_amount_minor"] for item in items)
    grand_total = total_amount + total_vat
    existing = conn.execute(
        "SELECT id, status FROM work_act WHERE tenant_id = ? AND source_system = ? AND external_document_id = ? AND deleted_at IS NULL",
        (inbox["tenant_id"], inbox["source_system"], inbox["external_document_id"]),
    ).fetchone()
    if existing and existing["status"] != "draft":
        raise ValueError(
            f"existing act {existing['id']} is not draft (status={existing['status']})"
        )
    act_id = (
        existing["id"]
        if existing
        else make_id(
            "waimp",
            inbox["tenant_id"],
            inbox["source_system"],
            inbox["external_document_id"],
        )
    )
    if existing:
        action = "import_update"
        conn.execute(
            """
            UPDATE work_act
               SET contract_id = ?, counterparty_id = ?, external_version = ?, imported_at = ?,
                   act_number = ?, act_date = ?, period_from = ?, period_to = ?,
                   total_amount_minor = ?, total_vat_amount_minor = ?, grand_total_amount_minor = ?, updated_at = ?
             WHERE id = ?
            """,
            (
                contract["id"],
                counterparty["id"],
                inbox["external_version"],
                now,
                inbox["act_number"],
                inbox["act_date"],
                inbox["period_from"],
                inbox["period_to"],
                total_amount,
                total_vat,
                grand_total,
                now,
                act_id,
            ),
        )
        conn.execute("DELETE FROM work_act_item WHERE act_id = ?", (act_id,))
    else:
        action = "import_create"
        conn.execute(
            """
            INSERT INTO work_act (
              id, tenant_id, contract_id, source_act_id, counterparty_id,
              source_system, external_document_id, external_version, imported_at,
              act_number, act_date, period_from, period_to, status,
              current_revision_id, signed_revision_id,
              total_amount_minor, total_vat_amount_minor, grand_total_amount_minor,
              created_by, created_at, updated_at, deleted_at
            ) VALUES (?, ?, ?, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'draft', NULL, NULL, ?, ?, ?, ?, ?, ?, NULL)
            """,
            (
                act_id,
                inbox["tenant_id"],
                contract["id"],
                counterparty["id"],
                inbox["source_system"],
                inbox["external_document_id"],
                inbox["external_version"],
                now,
                inbox["act_number"],
                inbox["act_date"],
                inbox["period_from"],
                inbox["period_to"],
                total_amount,
                total_vat,
                grand_total,
                actor,
                now,
                now,
            ),
        )
        conn.execute(
            "INSERT INTO work_act_status_history (id, act_id, from_status, to_status, changed_by, changed_at, reason) VALUES (?, ?, NULL, 'draft', ?, ?, ?)",
            (
                make_id("wshimp", act_id, "draft"),
                act_id,
                actor,
                now,
                f"Imported from inbox {inbox['id']}",
            ),
        )
    conn.executemany(
        "INSERT INTO work_act_item (id, act_id, line_no, description, unit_code, quantity_milli, price_minor, amount_minor, vat_rate_basis_points, vat_amount_minor, sort_order) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (
                make_id("waiimp", act_id, str(item["line_no"])),
                act_id,
                item["line_no"],
                item["description"],
                item["unit_code"],
                item["quantity_milli"],
                item["price_minor"],
                item["amount_minor"],
                item["vat_rate_basis_points"],
                item["vat_amount_minor"],
                item["sort_order"],
            )
            for item in items
        ],
    )
    audit_payload = json.dumps(
        {
            "inbox_id": inbox["id"],
            "source_system": inbox["source_system"],
            "external_document_id": inbox["external_document_id"],
            "external_version": inbox["external_version"],
            "item_count": len(items),
            "grand_total_amount_minor": grand_total,
        },
        ensure_ascii=False,
    )
    conn.execute(
        "INSERT INTO audit_event (id, tenant_id, entity_type, entity_id, action, payload_json, actor_id, occurred_at) VALUES (?, ?, 'work_act', ?, ?, json(?), ?, ?)",
        (
            make_id("aeimp", inbox["id"], action),
            inbox["tenant_id"],
            act_id,
            action,
            audit_payload,
            actor,
            now,
        ),
    )
    return act_id, action


def process_row(conn: sqlite3.Connection, inbox: sqlite3.Row) -> tuple[str, str]:
    now = utc_now()
    try:
        payload = json.loads(inbox["payload_json"])
        items = normalize_items(payload)
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            "UPDATE integration_inbox_work_act SET import_status = 'processing', import_attempts = import_attempts + 1, locked_at = ?, processed_at = NULL, last_error = NULL WHERE id = ?",
            (now, inbox["id"]),
        )
        act_id, action = upsert_draft(conn, inbox, items, now)
        conn.execute(
            "UPDATE integration_inbox_work_act SET import_status = 'imported', imported_act_id = ?, locked_at = NULL, processed_at = ?, last_error = NULL WHERE id = ?",
            (act_id, now, inbox["id"]),
        )
        conn.commit()
        return inbox["id"], f"{action}:{act_id}"
    except Exception as exc:
        if conn.in_transaction:
            conn.rollback()
        now = utc_now()
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            "UPDATE integration_inbox_work_act SET import_status = 'error', import_attempts = import_attempts + 1, locked_at = NULL, processed_at = ?, last_error = ? WHERE id = ?",
            (now, str(exc), inbox["id"]),
        )
        conn.commit()
        return inbox["id"], f"error:{exc}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import work acts from integration_inbox_work_act into draft work_act rows."
    )
    parser.add_argument(
        "--db",
        default="data/sqlite/work_acts_demo.sqlite",
        help="Path to SQLite database",
    )
    parser.add_argument(
        "--limit", type=int, default=100, help="Maximum inbox rows to process"
    )
    parser.add_argument(
        "--retry-errors",
        action="store_true",
        help="Also retry inbox rows in error status",
    )
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 5000")
        statuses = ["new"] + (["error"] if args.retry_errors else [])
        placeholders = ",".join("?" for _ in statuses)
        rows = conn.execute(
            f"SELECT * FROM integration_inbox_work_act WHERE import_status IN ({placeholders}) ORDER BY received_at, id LIMIT ?",
            (*statuses, args.limit),
        ).fetchall()
        results = [process_row(conn, row) for row in rows]
        imported = sum(1 for _, result in results if not result.startswith("error:"))
        failed = len(results) - imported
        print(
            json.dumps(
                {
                    "processed": len(results),
                    "imported": imported,
                    "failed": failed,
                    "results": results,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
