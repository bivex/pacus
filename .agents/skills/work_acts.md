# Skill: Жизненный цикл акта работ

## Когда применять

Создание акта, привязка к проекту, смена статуса, подписание, печать.

---

## 1. Создание акта

### Обязательные поля `work_act`

| Поле | Значение |
|---|---|
| `id` | UUID |
| `tenant_id` | из выбранного tenant |
| `contract_id` | договор с этим контрагентом |
| `counterparty_id` | должен совпадать с контрагентом договора |
| `act_number` | уникален в рамках tenant (`UNIQUE (tenant_id, act_number)`) |
| `act_date` | дата акта `YYYY-MM-DD` |
| `period_from`, `period_to` | период работ; `period_from <= period_to` |
| `status` | `'draft'` при создании |
| `created_by` | пользователь |
| `created_at`, `updated_at` | UTC ISO 8601 |

### Опциональные поля

- `project_id` — привязка к проекту (см. раздел 2)
- `source_act_id` — для корректировочных актов
- `source_system`, `external_document_id` — для интеграционных актов

### SQL-шаблон создания

```sql
INSERT INTO work_act (
  id, tenant_id, contract_id, counterparty_id,
  act_number, act_date, period_from, period_to,
  status, project_id,
  total_amount_minor, total_vat_amount_minor, grand_total_amount_minor,
  created_by, created_at, updated_at
) VALUES (
  :id, :tenant_id, :contract_id, :counterparty_id,
  :act_number, :act_date, :period_from, :period_to,
  'draft', :project_id,
  :total, :vat, :grand_total,
  :user, :now_utc, :now_utc
);
```

### Суммы

Все суммы хранятся в **минорных единицах** (копейки для RUB):
- `total_amount_minor` — сумма без НДС
- `total_vat_amount_minor` — сумма НДС
- `grand_total_amount_minor` — итого с НДС

Ставка НДС в `work_act_item.vat_rate_basis_points` (2000 = 20%).

---

## 2. Привязка акта к проекту

### Правила

- `project_id` — опционален (`NULL` допустим)
- Если указан: `work_act.tenant_id` **должен** совпадать с `project.tenant_id`
- Если указан: `work_act.counterparty_id` **должен** совпадать с `project.counterparty_id`

Оба инварианта контролируют триггеры:
`trg_work_act_project_tenant_match_*` и `trg_work_act_project_counterparty_match_*`

### Как правильно выбирать проект на UI

```sql
-- Показываем только проекты, доступные для этого акта
SELECT id, code, name, status
FROM project
WHERE tenant_id = :tenant_id
  AND counterparty_id = :counterparty_id
  AND status IN ('active', 'on_hold')   -- не показывать completed/cancelled
ORDER BY code;
```

Не надейся только на триггеры — фильтруй на уровне приложения.

### Привязка существующего акта к проекту

```sql
UPDATE work_act
SET project_id = :project_id,
    updated_at = :now_utc
WHERE id = :act_id;
```

Триггер `trg_work_act_project_counterparty_match_update` проверит совместимость.

---

## 3. Добавление позиций акта

```sql
INSERT INTO work_act_item (
  id, act_id, line_no, description, unit_code,
  quantity_milli, price_minor, amount_minor,
  vat_rate_basis_points, vat_amount_minor, sort_order
) VALUES (
  :id, :act_id, :line_no, :description, :unit_code,
  :quantity_milli,   -- 1 единица = 1000
  :price_minor,
  :amount_minor,     -- quantity_milli * price_minor / 1000
  :vat_rate_bps,     -- 2000 для 20%
  :vat_amount_minor,
  :sort_order
);
```

После вставки позиций пересчитай и обнови суммы в `work_act`.

---

## 4. Жизненный цикл статусов акта

### Разрешённые переходы

```
NULL
  ↓
draft ──→ generated ──→ sent ──→ signed ──→ corrected
  ↓            ↓          ↓
cancelled   cancelled  cancelled
```

БД блокирует недопустимые переходы триггером `trg_work_act_status_transition`.

### Переход в `generated` (сформирован HTML)

```sql
BEGIN;

UPDATE work_act
SET status = 'generated',
    current_revision_id = :revision_id,
    updated_at = :now_utc
WHERE id = :act_id;

INSERT INTO work_act_status_history (
  id, act_id, from_status, to_status, changed_by, changed_at, reason
) VALUES (:hid, :act_id, 'draft', 'generated', :user, :now_utc, :reason);

COMMIT;
```

### Переход в `signed` (подписан)

Обязательно: `signed_revision_id` должен быть заполнен.
БД проверяет триггером `trg_work_act_require_signed_revision`.

```sql
BEGIN;

UPDATE work_act
SET status = 'signed',
    signed_revision_id = :revision_id,
    updated_at = :now_utc
WHERE id = :act_id;

INSERT INTO work_act_status_history (
  id, act_id, from_status, to_status, changed_by, changed_at, reason
) VALUES (:hid, :act_id, 'sent', 'signed', :user, :now_utc, 'Получен подписанный экземпляр');

COMMIT;
```

> `signed_revision_id` нельзя изменить после установки — это иммутабельно.

---

## 5. Ревизии акта

Каждая версия документа — отдельная запись в `work_act_revision`.

### Создание ревизии

```sql
INSERT INTO work_act_revision (
  id, act_id, revision_no, revision_kind,
  snapshot_json, totals_json, template_version,
  html_artifact_id, pdf_artifact_id,
  created_by, created_at, comment,
  is_current, is_immutable
) VALUES (
  :id, :act_id, :revision_no, :kind,  -- kind: 'draft' | 'final' | 'correction'
  :snapshot_json, :totals_json, :template_version,
  :html_artifact_id, NULL,
  :user, :now_utc, :comment,
  1, 0   -- is_current=1, is_immutable=0 пока не подписан
);
```

### Заморозка ревизии (при подписании)

```sql
UPDATE work_act_revision
SET is_immutable = 1
WHERE id = :revision_id;
```

После установки `is_immutable = 1` ревизию нельзя изменить или удалить.
БД это блокирует триггерами `trg_work_act_revision_no_update_immutable` и `trg_work_act_revision_no_delete_immutable`.

### Только одна текущая ревизия

При создании новой текущей ревизии сначала снять флаг у старой:

```sql
UPDATE work_act_revision SET is_current = 0 WHERE act_id = :act_id AND is_current = 1;
INSERT INTO work_act_revision (..., is_current = 1) VALUES (...);
```

БД гарантирует уникальность через `uq_work_act_revision_current` (partial unique index).

---

## 6. Корректировочный акт

Создаётся как отдельный `work_act` с ссылкой на исходный:

```sql
INSERT INTO work_act (
  ...,
  source_act_id = :original_act_id,
  act_number = :original_act_number || '-К1',
  ...
);
```

Исходный акт переводится в статус `corrected`:

```sql
UPDATE work_act SET status = 'corrected' WHERE id = :original_act_id;
```

---

## 7. Печать акта

### Получить ссылку для печати

```sql
SELECT act_number, status, print_url, print_center_url
FROM v_nocodb_print_links
WHERE act_id = :act_id;
```

### История актов проекта для печати

```sql
SELECT act_number, period_from, period_to, act_status,
       grand_total_amount_minor, print_url
FROM v_nocodb_project_work_acts
WHERE project_id = :project_id
ORDER BY period_from, act_date;
```

---

## 8. Что обязано проверять приложение (БД не проверяет)

- Уникальность `act_number` предлагать пользователю, не надеяться только на constraint
- Не давать создавать акты к `completed`/`cancelled` проектам
- Пересчитывать суммы (`total_amount_minor`, `grand_total_amount_minor`) при изменении позиций
- При смене `counterparty_id` или `tenant_id` в уже привязанном акте —
  **проверить совместимость с проектом** (триггеры проверяют только смену `project_id`,
  но не смену `counterparty_id` при существующем `project_id`)
