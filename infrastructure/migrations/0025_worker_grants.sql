BEGIN;
SET LOCAL ROLE impact_owner;
-- Narrow impact_worker (quality hardening, October 2026). Migration 0003 granted impact_worker the
-- same SELECT/INSERT/UPDATE as impact_app on nearly every domain table. The worker of build 0.20.0
-- (impact_api/worker.py with store.write/audit and delivery.enqueue) touches only:
--   object_registry, object_revision, notification_current, audit_event_current: reminder notices
--     and their audit events (INSERT; SELECT for the reminder scan and the audit revision number)
--   tenant_principal      SELECT, INSERT (the SERVICE principal, ON CONFLICT DO NOTHING; recipients)
--   membership_current    SELECT (reminder recipients hold an active membership)
--   outbox_event          SELECT, INSERT;  outbox_delivery  SELECT, INSERT, UPDATE
--   consumer_receipt      SELECT, INSERT (worker.in_app)
--   job, job_item         cancellation of not-started jobs
--   from 0018: notification_delivery, recovery_channel_challenge, member_invitation,
--     grant_authority, worker_heartbeat, authority_reminder and EXECUTE on worker_tenants.
-- Tenant discovery goes through the SECURITY DEFINER impact.worker_tenants, so tenant_root is not
-- needed. Everything else is revoked below, one explicit statement per table: no dynamic
-- revoke-all-then-grant, which would undo explicit grants of other migrations.
-- Deliberately not touched, left for a follow-up once report exports (0024) have settled the
-- worker's export-job privileges: job, job_item, report_current, report_template_current.
-- Foreign-key checks run as the table owner and no row-level policy reads another table, so the
-- kept privileges cover every statement the worker issues. Nothing here depends on 0022-0024.
REVOKE ALL ON impact.a_i_task_current FROM impact_worker;
REVOKE ALL ON impact.allocation_rule_current FROM impact_worker;
REVOKE ALL ON impact.assignment_current FROM impact_worker;
REVOKE ALL ON impact.audit_batch_root FROM impact_worker;
REVOKE ALL ON impact.budget_line_current FROM impact_worker;
REVOKE ALL ON impact.calculated_result_current FROM impact_worker;
REVOKE ALL ON impact.connection_current FROM impact_worker;
REVOKE ALL ON impact.dashboard_current FROM impact_worker;
REVOKE ALL ON impact.dataset_current FROM impact_worker;
REVOKE ALL ON impact.decision_current FROM impact_worker;
REVOKE ALL ON impact.deletion_ledger FROM impact_worker;
REVOKE ALL ON impact.device_current FROM impact_worker;
REVOKE ALL ON impact.dimension_current FROM impact_worker;
REVOKE ALL ON impact.disclosure_current FROM impact_worker;
REVOKE ALL ON impact.evaluation_current FROM impact_worker;
REVOKE ALL ON impact.evidence_current FROM impact_worker;
REVOKE ALL ON impact.exchange_rate_current FROM impact_worker;
REVOKE ALL ON impact.file_blob FROM impact_worker;
REVOKE ALL ON impact.finance_transaction_current FROM impact_worker;
REVOKE ALL ON impact.form_current FROM impact_worker;
REVOKE ALL ON impact.form_field_current FROM impact_worker;
REVOKE ALL ON impact.framework_current FROM impact_worker;
REVOKE ALL ON impact.funding_agreement_current FROM impact_worker;
REVOKE ALL ON impact.grant_current FROM impact_worker;
REVOKE ALL ON impact.handling_record_current FROM impact_worker;
REVOKE ALL ON impact.import_job_current FROM impact_worker;
REVOKE ALL ON impact.indicator_definition_current FROM impact_worker;
REVOKE ALL ON impact.indicator_instance_current FROM impact_worker;
REVOKE ALL ON impact.lineage_edge FROM impact_worker;
REVOKE INSERT,UPDATE ON impact.membership_current FROM impact_worker;
REVOKE UPDATE ON impact.notification_current FROM impact_worker;
REVOKE UPDATE ON impact.object_registry FROM impact_worker;
REVOKE ALL ON impact.observation_current FROM impact_worker;
REVOKE ALL ON impact.offline_grant FROM impact_worker;
REVOKE ALL ON impact.operation_receipt FROM impact_worker;
REVOKE ALL ON impact.organisation_unit_current FROM impact_worker;
REVOKE ALL ON impact.participant_current FROM impact_worker;
REVOKE ALL ON impact.period_current FROM impact_worker;
REVOKE ALL ON impact.privacy_case_current FROM impact_worker;
REVOKE ALL ON impact.privacy_store_action FROM impact_worker;
REVOKE ALL ON impact.programme_current FROM impact_worker;
REVOKE ALL ON impact.qualitative_extract_current FROM impact_worker;
REVOKE ALL ON impact.quality_issue_current FROM impact_worker;
REVOKE ALL ON impact.retention_hold FROM impact_worker;
REVOKE ALL ON impact.retention_policy_current FROM impact_worker;
REVOKE ALL ON impact.review_decision FROM impact_worker;
REVOKE ALL ON impact.schedule_current FROM impact_worker;
REVOKE ALL ON impact.scope_definition FROM impact_worker;
REVOKE ALL ON impact.scope_member FROM impact_worker;
REVOKE ALL ON impact.service_event_current FROM impact_worker;
REVOKE ALL ON impact.service_identity FROM impact_worker;
REVOKE ALL ON impact.snapshot_current FROM impact_worker;
REVOKE ALL ON impact.snapshot_member FROM impact_worker;
REVOKE ALL ON impact.source_key_registry FROM impact_worker;
REVOKE ALL ON impact.source_revision_receipt FROM impact_worker;
REVOKE ALL ON impact.submission_current FROM impact_worker;
REVOKE ALL ON impact.subscription_current FROM impact_worker;
REVOKE ALL ON impact.support_request_current FROM impact_worker;
REVOKE ALL ON impact.sync_receipt FROM impact_worker;
REVOKE ALL ON impact.target_current FROM impact_worker;
REVOKE ALL ON impact.tenant_current FROM impact_worker;
REVOKE UPDATE ON impact.tenant_principal FROM impact_worker;
REVOKE ALL ON impact.tenant_root FROM impact_worker;
REVOKE ALL ON impact.tenant_schedule_hold FROM impact_worker;
REVOKE ALL ON impact.upload_part FROM impact_worker;
REVOKE ALL ON impact.upload_session FROM impact_worker;
REVOKE ALL ON impact.webhook_delivery FROM impact_worker;
REVOKE ALL ON impact.work_item_current FROM impact_worker;
REVOKE ALL ON impact.workflow_author FROM impact_worker;
REVOKE ALL ON impact.workflow_current FROM impact_worker;
COMMIT;
