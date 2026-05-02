# Skill: Инварианты БД — что делает БД, что делает приложение

## Когда применять

Перед написанием любого SQL-кода против Pacus. Перед добавлением новых ограничений.
При отладке неожиданных ошибок.

---

## Что БД гарантирует сама

### Структурные ограничения (CHECK, UNIQUE, FK)

| Таблица | Ограничение | Что блокирует |
|---|---|---|
| `work_act` | `CHECK status IN (...)` | недопустимый статус акта |
| `work_act` | `UNIQUE (tenant_id, act_number)` | дубликат номера акта в рамках tenant |
| `work_act` | `CHECK (period_from <= period_to)` | некорректный период |
| `work_act_revision` | `uq_work_act_revision_current` | две «текущих» ревизии одного акта |
| `contract` | `UNIQUE (tenant_id, contract_number, contract_date)` | дубликат договора |
| `project` | `CHECK status IN (...)` | недопустимый статус проекта |
| `project` | `UNIQUE (tenant_id, code)` | дубликат кода проекта в рамках tenant |
| `project` | `CHECK (finished_on IS NULL OR finished_on >= started_on)` | дата окончания раньше начала |
| `integration_inbox_work_act` | `UNIQUE idempotency_key` | повторная обработка |
| `integration_inbox_work_act` | `CHECK (period_from <= period_to)` | некорректный период |
| `integration_inbox_work_act` | `CHECK import_status IN (...)` | недопустимый статус |

### Триггеры на work_act

| Триггер | Что блокирует |
|---|---|
| `trg_work_act_status_transition` | переходы статусов вне разрешённого FSM |
| `trg_work_act_require_signed_revision` | перевод в `signed` без `signed_revision_id` |
| `trg_work_act_signed_revision_immutable` | изменение `signed_revision_id` после установки |
| `trg_work_act_revision_no_update_immutable` | UPDATE иммутабельной ревизии |
| `trg_work_act_revision_no_delete_immutable` | DELETE иммутабельной ревизии |
| `trg_document_artifact_no_update_if_immutable` | UPDATE артефакта, связанного с иммутабельной ревизией |
| `trg_document_artifact_no_delete_if_immutable` | DELETE артефакта (избыточно: FK тоже блокирует) |
| `trg_status_history_append_only_update` | UPDATE записи в истории статусов акта |
| `trg_status_history_append_only_delete` | DELETE записи в истории статусов акта |
| `trg_audit_event_append_only_update` | UPDATE audit_event |
| `trg_audit_event_append_only_delete` | DELETE audit_event |
| `trg_work_act_no_counterparty_change_when_linked` | изменение `counterparty_id` при привязанном `project_id` |
| `trg_work_act_no_tenant_change_when_linked` | изменение `tenant_id` при привязанном `project_id` |
| `trg_integration_inbox_no_imported_without_act` | `import_status='imported'` без `imported_act_id` |

### Триггеры на project

| Триггер | Что блокирует |
|---|---|
| `trg_project_status_transition` | переходы статусов вне разрешённого FSM |
| `trg_project_status_history_append_only_update` | UPDATE истории статусов проекта |
| `trg_project_status_history_append_only_delete` | DELETE истории статусов проекта |
| `trg_work_act_project_tenant_match_insert` | привязка акта к проекту другого tenant (INSERT) |
| `trg_work_act_project_tenant_match_update` | то же при UPDATE |
| `trg_work_act_project_counterparty_match_insert` | привязка акта к проекту другого counterparty (INSERT) |
| `trg_work_act_project_counterparty_match_update` | то же при UPDATE |

---

## Что приложение обязано контролировать само

БД **не блокирует** следующее:

### 1. Привязка новых актов к завершённым проектам

```
project.status IN ('completed', 'cancelled')
→ БД позволит добавить work_act.project_id
→ Приложение обязано это запретить
```

**Проверка перед INSERT/UPDATE:**
```sql
SELECT status FROM project WHERE id = :project_id;
-- если 'completed' или 'cancelled' → отклонить операцию
```

### 2. Обязательность `finished_on` при завершении проекта

БД принимает `completed` без `finished_on`.
Приложение обязано требовать дату при переходе в `completed`.

### 3. Пересчёт сумм акта при изменении позиций

`work_act.total_amount_minor`, `total_vat_amount_minor`, `grand_total_amount_minor`
— приложение обязано пересчитывать из `work_act_item` и обновлять в `work_act`.

### 4. История статусов — ответственность приложения

БД не пишет историю автоматически. Каждая смена статуса (акта или проекта)
требует явного `INSERT INTO ..._status_history` от приложения.

---

## Вьюхи: всегда читай через них

| Вьюха | Назначение |
|---|---|
| `v_nocodb_project_overview` | агрегаты по проекту: акты, суммы, статус |
| `v_nocodb_project_work_acts` | хронология актов проекта с print_url |
| `v_nocodb_work_act_overview` | обзор актов с joined данными |
| `v_nocodb_work_act_drafts` | только черновики |
| `v_nocodb_work_act_revisions_readonly` | ревизии с номером акта |
| `v_nocodb_print_links` | print_url для каждого акта |
| `v_nocodb_work_act_corrections` | пары оригинал → корректировка |
| `v_nocodb_work_act_status_history_readonly` | история статусов с номером акта |
| `v_nocodb_document_artifacts_readonly` | артефакты с контекстом ревизии |
| `Inbox All` / `Inbox` / `Imported` / `Errors` | интеграционный inbox |
| `Ready to Freeze` | черновики из интеграции, готовые к заморозке |

---

## Тесты схемы

Любые изменения схемы требуют прогона:

```bash
python3 -m pytest tests/test_db_schema.py -v   # 88 тестов: каждый guard работает
python3 -m pytest tests/test_mutations.py -v   # 22 теста: каждый guard необходим
```

Если тест мутации стал красным — новый guard дублирует существующий или сам тест устарел.
Если тест схемы стал красным — нарушен инвариант.
