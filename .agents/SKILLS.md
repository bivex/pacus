# Pacus — Agent Skills Index

Этот файл — точка входа для агентов, работающих с системой **Pacus**
(SQLite + NocoDB, акты работ, проекты).

Читай нужный skill-файл перед тем как выполнять операции с данными.
Не обходи правила в этих файлах — они отражают реальные инварианты БД.

---

## Домен

```
tenant
  └── counterparty
        ├── contract
        │     └── work_act  ──> project (optional FK)
        │           └── work_act_item
        └── project
              └── work_act_status_history (append-only)
```

БД: `data/sqlite/work_acts_demo.sqlite`
Схема: `db/sqlite/work_acts_schema.sql` + `db/sqlite/projects_schema.sql`

---

## Доступные skills

| Файл | Что описывает |
|---|---|
| `skills/projects.md` | Жизненный цикл проекта: создание, статусы, завершение |
| `skills/work_acts.md` | Жизненный цикл акта: создание, привязка к проекту, статусы, печать |
| `skills/db_invariants.md` | Что делает БД сама, что делает приложение, известные ограничения |

---

## Обязательные правила для всех операций

1. **Каждое изменение статуса** (проект или акт) = одна транзакция:
   `UPDATE ... SET status` + `INSERT INTO ..._status_history`

2. **Всегда проверяй** `tenant_id` и `counterparty_id` перед привязкой акта к проекту —
   триггеры поймают несоответствие, но лучше не доводить до ошибки.

3. **Никогда не редактируй** `project_status_history`, `work_act_status_history`,
   `audit_event` — они append-only, БД это не разрешит.

4. **Для чтения** — используй вьюхи, не пиши JOIN вручную:
   - `v_nocodb_project_overview` — сводка по проектам
   - `v_nocodb_project_work_acts` — акты в хронологии проекта
   - `v_nocodb_work_act_overview` — обзор актов
   - `v_nocodb_print_links` — ссылки на печать
