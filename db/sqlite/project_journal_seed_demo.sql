PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- ---------------------------------------------------------------------------
-- Demo seed for project journal.
-- Apply after projects_seed_demo.sql and work_acts_seed_demo.sql.
-- IDs are deterministic so the file can be re-run with INSERT OR IGNORE.
-- ---------------------------------------------------------------------------

-- ---------------------------------------------------------------------------
-- project_journal — proj_alfa_dev (tenant_demo, cp_alfa)
-- ---------------------------------------------------------------------------

INSERT OR IGNORE INTO project_journal
  (id, project_id, tenant_id, entry_date, kind, title, body, decision_made, outcome, recorded_by, recorded_at)
VALUES
  ('pj_alfa_1', 'proj_alfa_dev', 'tenant_demo', '2026-01-10', 'decision',
   'Принято решение о структуре модуля',
   NULL,
   'Разрабатывать backend на SQLite + Python, печатные формы через HTML-шаблоны',
   NULL,
   'user_demo_manager', '2026-01-10T10:00:00Z'),

  ('pj_alfa_2', 'proj_alfa_dev', 'tenant_demo', '2026-03-10', 'result',
   'Черновик акта за март сформирован',
   NULL, NULL,
   'Акт A-2026-003 передан на внутреннее согласование',
   'user_demo_manager', '2026-03-10T12:00:00Z'),

  ('pj_alfa_3', 'proj_alfa_dev', 'tenant_demo', '2026-04-03', 'decision',
   'Апрельский акт аннулирован до подписания',
   NULL,
   'Акт отозван: объём работ перенесён на май, пересогласование после уточнения ТЗ',
   NULL,
   'user_demo_manager', '2026-04-03T14:00:00Z'),

  ('pj_alfa_4', 'proj_alfa_dev', 'tenant_demo', '2026-03-21', 'milestone',
   'Контрольная точка Q1 пройдена',
   NULL, NULL,
   'Модуль интеграции готов, HTML-артефакты генерируются автоматически из БД',
   'user_demo_manager', '2026-03-21T09:00:00Z');

-- ---------------------------------------------------------------------------
-- project_journal — proj_beta_support (tenant_demo, cp_beta)
-- ---------------------------------------------------------------------------

INSERT OR IGNORE INTO project_journal
  (id, project_id, tenant_id, entry_date, kind, title, body, decision_made, outcome, recorded_by, recorded_at)
VALUES
  ('pj_beta_1', 'proj_beta_support', 'tenant_demo', '2026-01-05', 'decision',
   'Формат ежемесячной отчётности согласован',
   NULL,
   'Акты оформляются ежемесячно; корректировки — отдельным актом по требованию контрагента',
   NULL,
   'user_demo_operator', '2026-01-05T11:00:00Z'),

  ('pj_beta_2', 'proj_beta_support', 'tenant_demo', '2026-02-01', 'result',
   'Январские акты подписаны',
   NULL, NULL,
   'Базовый акт подписан 01.02.2026; корректировочный — 05.02.2026. Закрыт январь.',
   'user_demo_accountant', '2026-02-05T13:00:00Z'),

  ('pj_beta_3', 'proj_beta_support', 'tenant_demo', '2026-02-28', 'result',
   'Февральский акт отправлен контрагенту',
   NULL, NULL,
   'Акт A-2026-002 отправлен, ожидается подписание',
   'user_demo_operator', '2026-02-28T18:00:00Z'),

  ('pj_beta_4', 'proj_beta_support', 'tenant_demo', '2026-03-01', 'milestone',
   'Проект завершён',
   NULL, NULL,
   'Все обязательства выполнены. Поддержка прекращена по соглашению сторон.',
   'user_demo_operator', '2026-03-01T17:00:00Z');

-- ---------------------------------------------------------------------------
-- project_journal_act — junction rows
-- ---------------------------------------------------------------------------

INSERT OR IGNORE INTO project_journal_act (journal_id, act_id) VALUES
  ('pj_alfa_2', 'wa_draft_mar'),
  ('pj_alfa_3', 'wa_cancelled_apr'),
  ('pj_beta_2', 'wa_original_jan'),
  ('pj_beta_2', 'wa_correction_jan'),
  ('pj_beta_3', 'wa_sent_feb'),
  ('pj_beta_4', 'wa_original_jan'),
  ('pj_beta_4', 'wa_correction_jan'),
  ('pj_beta_4', 'wa_sent_feb');

COMMIT;
