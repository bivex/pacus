# Skill: Жизненный цикл проекта

## Когда применять

Создание проекта, смена статуса, завершение, отмена, чтение агрегатов.

---

## 1. Создание проекта

### Обязательные поля

| Поле | Откуда |
|---|---|
| `id` | UUID или детерминированный идентификатор |
| `tenant_id` | выбирается оператором |
| `counterparty_id` | выбирается оператором (должен принадлежать этому tenant) |
| `code` | короткий код, уникален внутри tenant |
| `name` | название |
| `status` | всегда `'active'` при создании |
| `started_on` | дата начала в формате `YYYY-MM-DD` |
| `created_by` | идентификатор пользователя |
| `created_at`, `updated_at` | UTC ISO 8601 |

### Опциональные поля

- `description` — описание проекта
- `finished_on` — оставить `NULL` при создании

### SQL-шаблон создания (одна транзакция)

```sql
BEGIN;

INSERT INTO project (
  id, tenant_id, counterparty_id, code, name, description,
  status, started_on, created_by, created_at, updated_at
) VALUES (
  :id, :tenant_id, :counterparty_id, :code, :name, :description,
  'active', :started_on, :created_by,
  :now_utc, :now_utc
);

INSERT INTO project_status_history (
  id, project_id, from_status, to_status,
  changed_by, changed_at, reason
) VALUES (
  :history_id, :id, NULL, 'active',
  :created_by, :now_utc, 'Проект открыт'
);

COMMIT;
```

### Инварианты БД

- `UNIQUE (tenant_id, code)` — код должен быть уникален в рамках tenant
- `CHECK (finished_on IS NULL OR finished_on >= started_on)` — даты не должны противоречить
- FK на `tenant_id` и `counterparty_id` — оба должны существовать

---

## 2. Смена статуса проекта

### Разрешённые переходы

```
active ──→ on_hold
active ──→ completed
active ──→ cancelled
on_hold ──→ active
on_hold ──→ cancelled
```

Статусы `completed` и `cancelled` **терминальные** — переходов из них нет.
БД это блокирует триггером `trg_project_status_transition`.

### SQL-шаблон смены статуса (одна транзакция)

```sql
BEGIN;

UPDATE project
SET status = :new_status,
    finished_on = :finished_on,   -- NULL если не completed/cancelled
    updated_at = :now_utc
WHERE id = :project_id;

INSERT INTO project_status_history (
  id, project_id, from_status, to_status,
  changed_by, changed_at, reason
) VALUES (
  :history_id, :project_id, :old_status, :new_status,
  :changed_by, :now_utc, :reason
);

COMMIT;
```

> **Важно:** всегда передавай `from_status` = текущий статус проекта *до* UPDATE.
> Читай его в той же транзакции (`SELECT status FROM project WHERE id = ...`).

### Когда заполнять `finished_on`

| Статус | `finished_on` |
|---|---|
| `active` | `NULL` |
| `on_hold` | `NULL` |
| `completed` | дата завершения (обязательно на уровне приложения) |
| `cancelled` | опционально |

БД не требует `finished_on` для `completed`, это правило приложения.

---

## 3. Завершение проекта (сценарий D)

```sql
BEGIN;

UPDATE project
SET status = 'completed',
    finished_on = :date,
    updated_at = :now_utc
WHERE id = :project_id;

INSERT INTO project_status_history (
  id, project_id, from_status, to_status,
  changed_by, changed_at, reason
) VALUES (
  :hid, :project_id, 'active', 'completed',
  :user, :now_utc, :reason
);

COMMIT;
```

---

## 4. Чтение данных проекта

### Сводка по проекту (dashboard)

```sql
SELECT *
FROM v_nocodb_project_overview
WHERE id = :project_id;
```

Возвращает: название, статус, контрагент, кол-во актов, суммы, диапазон периодов.

### Все проекты tenant по статусу

```sql
SELECT *
FROM v_nocodb_project_overview
WHERE tenant_id = :tenant_id
  AND status = 'active'
ORDER BY started_on DESC;
```

### История статусов проекта

```sql
SELECT from_status, to_status, changed_by, changed_at, reason
FROM project_status_history
WHERE project_id = :project_id
ORDER BY changed_at ASC;
```

---

## 5. Ограничения, которые обязано проверять приложение

БД **не проверяет** следующее — это зона ответственности приложения:

- Запрет привязывать новые акты к `completed`/`cancelled` проекту
- Обязательность `finished_on` при переходе в `completed`
- Корректность `reason` в истории статусов (любая строка проходит)
