-- ===========================================
-- projects_seed_demo.sql
-- Version: 1.0
-- Effective Date: 2026-05-01
-- Description: Demo seed data for project management system
-- ===========================================

PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- Demo seed for the projects extension.
-- Apply after work_acts_seed_demo.sql.
-- IDs are deterministic so the file can be re-run with INSERT OR IGNORE.

-- ---------------------------------------------------------------------------
-- Projects
-- ---------------------------------------------------------------------------

INSERT OR IGNORE INTO project (id, tenant_id, counterparty_id, code, name, description, status, started_on, finished_on, created_by, created_at, updated_at) VALUES
  ('proj_alfa_dev',
   'tenant_demo',
   'cp_alfa',
   'ALFA-DEV-2026',
   'Разработка платформы актов',
   'Проект по разработке backend-модуля и интеграции печатных форм',
   'active',
   '2026-01-01',
   NULL,
   'user_demo_manager',
   '2026-03-08T09:05:00Z',
   '2026-03-08T09:05:00Z'),
  ('proj_beta_support',
   'tenant_demo',
   'cp_beta',
   'BETA-SUP-2026',
   'Техническая поддержка платформы',
   'Сопровождение и мониторинг платформы в 2026 году',
   'completed',
   '2026-01-01',
   '2026-03-01',
   'user_demo_operator',
   '2026-03-08T09:06:00Z',
   '2026-03-08T09:06:00Z');

-- ---------------------------------------------------------------------------
-- Project status history
-- ---------------------------------------------------------------------------

INSERT OR IGNORE INTO project_status_history (id, project_id, from_status, to_status, changed_by, changed_at, reason) VALUES
  -- proj_alfa_dev: initial open
  ('psh_alfa_dev_1',
   'proj_alfa_dev',
   NULL,
   'active',
   'user_demo_manager',
   '2026-03-08T09:05:00Z',
   'Проект открыт'),
  -- proj_beta_support: initial open
  ('psh_beta_sup_1',
   'proj_beta_support',
   NULL,
   'active',
   'user_demo_operator',
   '2026-03-08T09:06:00Z',
   'Проект открыт'),
  -- proj_beta_support: completed
  ('psh_beta_sup_2',
   'proj_beta_support',
   'active',
   'completed',
   'user_demo_operator',
   '2026-03-08T09:06:30Z',
   'Все акты закрыты, поддержка завершена');

-- ---------------------------------------------------------------------------
-- Assign work_acts to projects
-- ---------------------------------------------------------------------------

UPDATE work_act SET project_id = 'proj_alfa_dev',    updated_at = '2026-03-08T09:07:00Z'
WHERE id = 'wa_draft_mar';

UPDATE work_act SET project_id = 'proj_alfa_dev',    updated_at = '2026-03-08T09:07:01Z'
WHERE id = 'wa_cancelled_apr';

UPDATE work_act SET project_id = 'proj_beta_support', updated_at = '2026-03-08T09:07:02Z'
WHERE id = 'wa_sent_feb';

UPDATE work_act SET project_id = 'proj_beta_support', updated_at = '2026-03-08T09:07:03Z'
WHERE id = 'wa_original_jan';

UPDATE work_act SET project_id = 'proj_beta_support', updated_at = '2026-03-08T09:07:04Z'
WHERE id = 'wa_correction_jan';

-- ---------------------------------------------------------------------------
-- Audit events for project creation
-- ---------------------------------------------------------------------------

INSERT OR IGNORE INTO audit_event (id, tenant_id, entity_type, entity_id, action, payload_json, actor_id, occurred_at) VALUES
  ('ae_proj_alfa_dev_create',
   'tenant_demo',
   'project',
   'proj_alfa_dev',
   'create',
   json_object(
     'code',       'ALFA-DEV-2026',
     'name',       'Разработка платформы актов',
     'status',     'active',
     'started_on', '2026-01-01'
   ),
   'user_demo_manager',
   '2026-03-08T09:05:05Z'),
  ('ae_proj_beta_support_create',
   'tenant_demo',
   'project',
   'proj_beta_support',
   'create',
   json_object(
     'code',       'BETA-SUP-2026',
     'name',       'Техническая поддержка платформы',
     'status',     'active',
     'started_on', '2026-01-01'
   ),
   'user_demo_operator',
   '2026-03-08T09:06:05Z'),
  ('ae_proj_beta_support_complete',
   'tenant_demo',
   'project',
   'proj_beta_support',
   'status_change',
   json_object(
     'from_status', 'active',
     'to_status',   'completed',
     'reason',      'Все акты закрыты, поддержка завершена'
   ),
   'user_demo_operator',
   '2026-03-08T09:06:35Z');

COMMIT;
