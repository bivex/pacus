PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- Demo seed intended for a fresh or reusable local SQLite database.
-- IDs are deterministic so the file can be re-run with INSERT OR IGNORE.

INSERT OR IGNORE INTO tenant (id, code, name, created_at) VALUES
  ('tenant_demo', 'demo', 'Демо арендатор / Pacus Demo', '2026-03-08T09:00:00Z');

INSERT OR IGNORE INTO counterparty (id, tenant_id, full_name, inn, kpp, legal_address, is_active, created_at) VALUES
  ('cp_alfa', 'tenant_demo', 'ООО Альфа Инжиниринг', '7701234567', '770101001', 'Москва, ул. Летниковская, 10', 1, '2026-03-08T09:01:00Z'),
  ('cp_beta', 'tenant_demo', 'АО Бета Сервис', '7812345678', '781201001', 'Санкт-Петербург, Невский пр., 12', 1, '2026-03-08T09:02:00Z');

INSERT OR IGNORE INTO contract (id, tenant_id, counterparty_id, contract_number, contract_date, currency_code, vat_mode, created_at) VALUES
  ('ct_alfa_dev_2026', 'tenant_demo', 'cp_alfa', 'DEV-2026-01', '2026-01-15', 'RUB', 'vat_20', '2026-03-08T09:03:00Z'),
  ('ct_beta_support_2026', 'tenant_demo', 'cp_beta', 'SUP-2026-04', '2026-02-01', 'RUB', 'vat_20', '2026-03-08T09:04:00Z');

INSERT OR IGNORE INTO document_artifact (id, tenant_id, artifact_type, storage_path, content_type, checksum_sha256, size_bytes, renderer_version, created_at) VALUES
  ('da_draft_html', 'tenant_demo', 'html', 'acts/tenant_demo/2026/wa_draft_mar/rev-1/act.html', 'text/html', '1111111111111111111111111111111111111111111111111111111111111111', 24812, 'renderer-1.0.0', '2026-03-08T09:20:00Z'),
  ('da_sent_html', 'tenant_demo', 'html', 'acts/tenant_demo/2026/wa_sent_feb/rev-1/act.html', 'text/html', '2222222222222222222222222222222222222222222222222222222222222222', 25410, 'renderer-1.0.0', '2026-03-08T09:21:00Z'),
  ('da_orig_html', 'tenant_demo', 'html', 'acts/tenant_demo/2026/wa_original_jan/rev-1/act.html', 'text/html', '3333333333333333333333333333333333333333333333333333333333333333', 26100, 'renderer-1.0.0', '2026-03-08T09:22:00Z'),
  ('da_orig_pdf', 'tenant_demo', 'pdf', 'acts/tenant_demo/2026/wa_original_jan/rev-1/act.pdf', 'application/pdf', '4444444444444444444444444444444444444444444444444444444444444444', 84210, 'renderer-1.0.0', '2026-03-08T09:22:30Z'),
  ('da_corr_html', 'tenant_demo', 'html', 'acts/tenant_demo/2026/wa_correction_jan/rev-1/act.html', 'text/html', '5555555555555555555555555555555555555555555555555555555555555555', 23880, 'renderer-1.0.0', '2026-03-08T09:23:00Z'),
  ('da_corr_pdf', 'tenant_demo', 'pdf', 'acts/tenant_demo/2026/wa_correction_jan/rev-1/act.pdf', 'application/pdf', '6666666666666666666666666666666666666666666666666666666666666666', 79220, 'renderer-1.0.0', '2026-03-08T09:23:30Z'),
  ('da_cancelled_html', 'tenant_demo', 'html', 'acts/tenant_demo/2026/wa_cancelled_apr/rev-1/act.html', 'text/html', '7777777777777777777777777777777777777777777777777777777777777777', 19876, 'renderer-1.0.0', '2026-03-08T09:24:00Z');

INSERT OR IGNORE INTO work_act (id, tenant_id, contract_id, source_act_id, counterparty_id, source_system, external_document_id, external_version, imported_at, act_number, act_date, period_from, period_to, status, current_revision_id, signed_revision_id, total_amount_minor, total_vat_amount_minor, grand_total_amount_minor, created_by, created_at, updated_at, deleted_at) VALUES
  ('wa_draft_mar', 'tenant_demo', 'ct_alfa_dev_2026', NULL, 'cp_alfa', NULL, NULL, NULL, NULL, 'A-2026-003', '2026-03-10', '2026-03-01', '2026-03-10', 'draft', NULL, NULL, 18500000, 3700000, 22200000, 'user_demo_manager', '2026-03-08T09:10:00Z', '2026-03-08T09:10:00Z', NULL),
  ('wa_sent_feb', 'tenant_demo', 'ct_beta_support_2026', NULL, 'cp_beta', NULL, NULL, NULL, NULL, 'A-2026-002', '2026-02-28', '2026-02-01', '2026-02-28', 'sent', NULL, NULL, 9000000, 1800000, 10800000, 'user_demo_operator', '2026-03-08T09:11:00Z', '2026-03-08T09:11:00Z', NULL),
  ('wa_original_jan', 'tenant_demo', 'ct_beta_support_2026', NULL, 'cp_beta', NULL, NULL, NULL, NULL, 'A-2026-001', '2026-01-31', '2026-01-01', '2026-01-31', 'corrected', NULL, NULL, 15000000, 3000000, 18000000, 'user_demo_operator', '2026-03-08T09:12:00Z', '2026-03-08T09:12:00Z', NULL),
  ('wa_correction_jan', 'tenant_demo', 'ct_beta_support_2026', 'wa_original_jan', 'cp_beta', NULL, NULL, NULL, NULL, 'A-2026-001-К1', '2026-02-05', '2026-01-01', '2026-01-31', 'signed', NULL, NULL, 1200000, 240000, 1440000, 'user_demo_accountant', '2026-03-08T09:13:00Z', '2026-03-08T09:13:00Z', NULL),
  ('wa_cancelled_apr', 'tenant_demo', 'ct_alfa_dev_2026', NULL, 'cp_alfa', NULL, NULL, NULL, NULL, 'A-2026-004', '2026-04-03', '2026-04-01', '2026-04-03', 'cancelled', NULL, NULL, 4000000, 800000, 4800000, 'user_demo_manager', '2026-03-08T09:14:00Z', '2026-03-08T09:14:00Z', NULL);

INSERT OR IGNORE INTO work_act_item (id, act_id, line_no, description, unit_code, quantity_milli, price_minor, amount_minor, vat_rate_basis_points, vat_amount_minor, sort_order) VALUES
  ('wai_draft_1', 'wa_draft_mar', 1, 'Разработка backend модуля актов', 'JOB', 1000, 12000000, 12000000, 2000, 2400000, 1),
  ('wai_draft_2', 'wa_draft_mar', 2, 'Интеграция печатной HTML-формы', 'JOB', 1000, 6500000, 6500000, 2000, 1300000, 2),
  ('wai_sent_1', 'wa_sent_feb', 1, 'Техническая поддержка платформы за февраль', 'MONTH', 1000, 7000000, 7000000, 2000, 1400000, 1),
  ('wai_sent_2', 'wa_sent_feb', 2, 'Администрирование и мониторинг', 'MONTH', 1000, 2000000, 2000000, 2000, 400000, 2),
  ('wai_orig_1', 'wa_original_jan', 1, 'Комплексное сопровождение платформы за январь', 'MONTH', 1000, 15000000, 15000000, 2000, 3000000, 1),
  ('wai_corr_1', 'wa_correction_jan', 1, 'Корректировка по январскому акту', 'JOB', 1000, 1200000, 1200000, 2000, 240000, 1),
  ('wai_cancelled_1', 'wa_cancelled_apr', 1, 'Предварительный аудит интеграции', 'JOB', 1000, 4000000, 4000000, 2000, 800000, 1);

INSERT OR IGNORE INTO work_act_revision (id, act_id, revision_no, revision_kind, snapshot_json, totals_json, template_version, html_artifact_id, pdf_artifact_id, created_by, created_at, comment, is_current, is_immutable) VALUES
  ('rev_draft_1', 'wa_draft_mar', 1, 'draft', json_object('act_number', 'A-2026-003', 'status', 'draft', 'counterparty', 'ООО Альфа Инжиниринг', 'period_from', '2026-03-01', 'period_to', '2026-03-10'), json_object('total_amount_minor', 18500000, 'vat_amount_minor', 3700000, 'grand_total_minor', 22200000, 'currency', 'RUB'), 'tpl-2026.03', 'da_draft_html', NULL, 'user_demo_manager', '2026-03-08T09:20:10Z', 'Черновик для внутреннего согласования', 1, 0),
  ('rev_sent_1', 'wa_sent_feb', 1, 'final', json_object('act_number', 'A-2026-002', 'status', 'sent', 'counterparty', 'АО Бета Сервис', 'period_from', '2026-02-01', 'period_to', '2026-02-28'), json_object('total_amount_minor', 9000000, 'vat_amount_minor', 1800000, 'grand_total_minor', 10800000, 'currency', 'RUB'), 'tpl-2026.02', 'da_sent_html', NULL, 'user_demo_operator', '2026-03-08T09:21:10Z', 'Версия отправлена контрагенту', 1, 0),
  ('rev_orig_1', 'wa_original_jan', 1, 'final', json_object('act_number', 'A-2026-001', 'status', 'signed', 'counterparty', 'АО Бета Сервис', 'period_from', '2026-01-01', 'period_to', '2026-01-31'), json_object('total_amount_minor', 15000000, 'vat_amount_minor', 3000000, 'grand_total_minor', 18000000, 'currency', 'RUB'), 'tpl-2026.01', 'da_orig_html', 'da_orig_pdf', 'user_demo_operator', '2026-03-08T09:22:10Z', 'Исходный подписанный акт', 1, 1),
  ('rev_corr_1', 'wa_correction_jan', 1, 'correction', json_object('act_number', 'A-2026-001-К1', 'status', 'signed', 'counterparty', 'АО Бета Сервис', 'source_act_number', 'A-2026-001'), json_object('total_amount_minor', 1200000, 'vat_amount_minor', 240000, 'grand_total_minor', 1440000, 'currency', 'RUB'), 'tpl-2026.02-c1', 'da_corr_html', 'da_corr_pdf', 'user_demo_accountant', '2026-03-08T09:23:10Z', 'Корректировочный акт к январю', 1, 1),
  ('rev_cancelled_1', 'wa_cancelled_apr', 1, 'draft', json_object('act_number', 'A-2026-004', 'status', 'cancelled', 'counterparty', 'ООО Альфа Инжиниринг', 'period_from', '2026-04-01', 'period_to', '2026-04-03'), json_object('total_amount_minor', 4000000, 'vat_amount_minor', 800000, 'grand_total_minor', 4800000, 'currency', 'RUB'), 'tpl-2026.04', 'da_cancelled_html', NULL, 'user_demo_manager', '2026-03-08T09:24:10Z', 'Черновик был отменён', 1, 0);

UPDATE work_act SET current_revision_id = 'rev_draft_1', updated_at = '2026-03-08T09:20:20Z' WHERE id = 'wa_draft_mar';
UPDATE work_act SET current_revision_id = 'rev_sent_1', updated_at = '2026-03-08T09:21:20Z' WHERE id = 'wa_sent_feb';
UPDATE work_act SET current_revision_id = 'rev_orig_1', signed_revision_id = 'rev_orig_1', updated_at = '2026-03-08T09:22:20Z' WHERE id = 'wa_original_jan';
UPDATE work_act SET current_revision_id = 'rev_corr_1', signed_revision_id = 'rev_corr_1', updated_at = '2026-03-08T09:23:20Z' WHERE id = 'wa_correction_jan';
UPDATE work_act SET current_revision_id = 'rev_cancelled_1', updated_at = '2026-03-08T09:24:20Z' WHERE id = 'wa_cancelled_apr';

INSERT OR IGNORE INTO work_act_status_history (id, act_id, from_status, to_status, changed_by, changed_at, reason) VALUES
  ('wsh_draft_1', 'wa_draft_mar', NULL, 'draft', 'user_demo_manager', '2026-03-08T09:10:00Z', 'Создан новый черновик'),
  ('wsh_sent_1', 'wa_sent_feb', NULL, 'draft', 'user_demo_operator', '2026-02-28T17:00:00Z', 'Создан акт за февраль'),
  ('wsh_sent_2', 'wa_sent_feb', 'draft', 'generated', 'user_demo_operator', '2026-02-28T17:05:00Z', 'Сформирован HTML'),
  ('wsh_sent_3', 'wa_sent_feb', 'generated', 'sent', 'user_demo_operator', '2026-02-28T17:10:00Z', 'Отправлено клиенту по email'),
  ('wsh_orig_1', 'wa_original_jan', NULL, 'draft', 'user_demo_operator', '2026-01-31T12:00:00Z', 'Создан исходный акт'),
  ('wsh_orig_2', 'wa_original_jan', 'draft', 'generated', 'user_demo_operator', '2026-01-31T12:10:00Z', 'Подготовлен к отправке'),
  ('wsh_orig_3', 'wa_original_jan', 'generated', 'sent', 'user_demo_operator', '2026-01-31T12:15:00Z', 'Отправлен клиенту'),
  ('wsh_orig_4', 'wa_original_jan', 'sent', 'signed', 'user_demo_accountant', '2026-02-01T09:00:00Z', 'Получен подписанный экземпляр'),
  ('wsh_orig_5', 'wa_original_jan', 'signed', 'corrected', 'user_demo_accountant', '2026-02-05T10:00:00Z', 'Создан корректировочный акт'),
  ('wsh_corr_1', 'wa_correction_jan', NULL, 'draft', 'user_demo_accountant', '2026-02-05T09:00:00Z', 'Создан корректировочный акт'),
  ('wsh_corr_2', 'wa_correction_jan', 'draft', 'generated', 'user_demo_accountant', '2026-02-05T09:15:00Z', 'Сформирован HTML'),
  ('wsh_corr_3', 'wa_correction_jan', 'generated', 'sent', 'user_demo_accountant', '2026-02-05T09:20:00Z', 'Отправлен клиенту'),
  ('wsh_corr_4', 'wa_correction_jan', 'sent', 'signed', 'user_demo_accountant', '2026-02-05T12:00:00Z', 'Подписан обеими сторонами'),
  ('wsh_cancelled_1', 'wa_cancelled_apr', NULL, 'draft', 'user_demo_manager', '2026-04-03T11:00:00Z', 'Создан предварительный акт'),
  ('wsh_cancelled_2', 'wa_cancelled_apr', 'draft', 'cancelled', 'user_demo_manager', '2026-04-03T13:00:00Z', 'Работы перенесены, акт отменён');

INSERT OR IGNORE INTO audit_event (id, tenant_id, entity_type, entity_id, action, payload_json, actor_id, occurred_at) VALUES
  ('ae_draft_1', 'tenant_demo', 'work_act', 'wa_draft_mar', 'create', json_object('status', 'draft', 'act_number', 'A-2026-003'), 'user_demo_manager', '2026-03-08T09:10:05Z'),
  ('ae_sent_1', 'tenant_demo', 'work_act', 'wa_sent_feb', 'send', json_object('status', 'sent', 'revision_id', 'rev_sent_1'), 'user_demo_operator', '2026-02-28T17:10:05Z'),
  ('ae_orig_1', 'tenant_demo', 'work_act', 'wa_original_jan', 'sign', json_object('status', 'signed', 'revision_id', 'rev_orig_1'), 'user_demo_accountant', '2026-02-01T09:00:05Z'),
  ('ae_orig_2', 'tenant_demo', 'work_act', 'wa_original_jan', 'correct', json_object('status', 'corrected', 'correction_act_id', 'wa_correction_jan'), 'user_demo_accountant', '2026-02-05T10:00:05Z'),
  ('ae_corr_1', 'tenant_demo', 'work_act', 'wa_correction_jan', 'sign', json_object('status', 'signed', 'revision_id', 'rev_corr_1'), 'user_demo_accountant', '2026-02-05T12:00:05Z'),
  ('ae_cancelled_1', 'tenant_demo', 'work_act', 'wa_cancelled_apr', 'cancel', json_object('status', 'cancelled'), 'user_demo_manager', '2026-04-03T13:00:05Z');

INSERT OR IGNORE INTO integration_inbox_work_act (
  id,
  tenant_id,
  source_system,
  external_document_id,
  external_version,
  idempotency_key,
  counterparty_inn,
  contract_number,
  contract_date,
  act_number,
  act_date,
  period_from,
  period_to,
  payload_json,
  payload_hash_sha256,
  import_status,
  import_attempts,
  imported_act_id,
  last_error,
  received_at,
  locked_at,
  processed_at
) VALUES (
  'iwa_erp_demo_001',
  'tenant_demo',
  'erp_demo',
  'erp-act-2026-005',
  '1',
  'erp_demo:erp-act-2026-005:1',
  '7701234567',
  'DEV-2026-01',
  '2026-01-15',
  'A-2026-005',
  '2026-05-05',
  '2026-05-01',
  '2026-05-05',
  json_object(
    'currency_code', 'RUB',
    'items', json_array(
      json_object('description', 'Интеграционная загрузка акта за май', 'unit_code', 'JOB', 'quantity_milli', 1000, 'price_minor', 21000000, 'vat_rate_basis_points', 2000),
      json_object('description', 'Подготовка печатной формы и сверка', 'unit_code', 'JOB', 'quantity_milli', 1000, 'price_minor', 3500000, 'vat_rate_basis_points', 2000)
    )
  ),
  '8888888888888888888888888888888888888888888888888888888888888888',
  'new',
  0,
  NULL,
  NULL,
  '2026-03-08T10:00:00Z',
  NULL,
  NULL
);

COMMIT;