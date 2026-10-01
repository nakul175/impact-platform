BEGIN;
SET LOCAL ROLE impact_owner;
-- Worker privileges and operator re-queue (quality hardening, October 2026).
-- Part 1 narrows impact_worker. Migration 0003 granted impact_worker the
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

-- Operator re-queue (control plane, platform API 1.5.0). impact_platform may not read or write the
-- tenant outbox; these two functions expose exactly the attention list (dispatchable rows that are
-- DEAD or held by a suspension, optionally of one tenant; no address, reference or payload) and one
-- fenced transition per row.
-- They read through the owner-only SELECT policies of 0018 and update under tenant_fence, so the
-- caller must have set impact.tenant_id. The lease generation is the row's revision: a re-queue or
-- a release advances it, so a worker that still believes it holds the row matches nothing (0018).
CREATE FUNCTION impact.operator_delivery_attention(requested_tenant uuid, max_rows integer)
 RETURNS TABLE(tenant_id uuid, lifecycle_state text, event_id uuid, channel text, template text,
  state text, held boolean, attempts integer, last_error_class text, last_attempt_at timestamptz,
  completed_at timestamptz, lease_generation bigint)
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT d.tenant_id,t.lifecycle_state,d.event_id,d.channel,d.template,d.state,d.held_at IS NOT NULL,
  d.attempts,d.last_error_class,d.last_attempt_at,d.completed_at,d.lease_generation
 FROM impact.outbox_delivery d JOIN impact.tenant_root t ON t.tenant_id=d.tenant_id
 WHERE d.channel IS NOT NULL AND (d.state='DEAD' OR (d.held_at IS NOT NULL AND d.state IN ('PENDING','LEASED')))
  AND (requested_tenant IS NULL OR d.tenant_id=requested_tenant)
 ORDER BY coalesce(d.last_attempt_at,d.next_attempt_at) DESC,d.tenant_id,d.event_id
 LIMIT least(greatest(max_rows,1),50)
$$;
REVOKE ALL ON FUNCTION impact.operator_delivery_attention(uuid,integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.operator_delivery_attention(uuid,integer) TO impact_platform;
-- 'requeue': a DEAD row becomes PENDING with a fresh attempt budget, due now, released from any
-- hold. 'release': a held PENDING row is released, due now. Anything else changes nothing and
-- answers a reason. The caller holds the tenant advisory lock and checks the tenant is Active.
CREATE FUNCTION impact.operator_requeue_delivery(requested_event uuid, mode text, expected_generation bigint)
 RETURNS TABLE(outcome text, state text, held boolean, attempts integer, lease_generation bigint,
  previous_state text, previous_attempts integer, previous_error_class text)
 LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
#variable_conflict use_column
DECLARE tenant uuid := impact.current_tenant(); r impact.outbox_delivery%ROWTYPE;
BEGIN
 IF tenant IS NULL OR mode NOT IN ('requeue','release') THEN
  RAISE EXCEPTION 'operator re-queue needs a tenant context and a known mode' USING ERRCODE='42501';
 END IF;
 SELECT * INTO r FROM impact.outbox_delivery d WHERE d.tenant_id=tenant AND d.event_id=requested_event
  AND d.channel IS NOT NULL FOR UPDATE;
 IF NOT FOUND THEN
  RETURN QUERY SELECT 'NOT_FOUND'::text,NULL::text,NULL::boolean,NULL::integer,NULL::bigint,NULL::text,NULL::integer,NULL::text;
  RETURN;
 END IF;
 IF r.lease_generation<>expected_generation THEN outcome := 'STALE';
 ELSIF mode='requeue' AND r.state<>'DEAD' THEN outcome := 'NOT_DEAD';
 ELSIF mode='release' AND r.held_at IS NULL THEN outcome := 'NOT_HELD';
 ELSIF mode='release' AND r.state<>'PENDING' THEN outcome := 'NOT_PENDING';
 ELSIF mode='requeue' THEN
  UPDATE impact.outbox_delivery d SET state='PENDING',attempts=0,completed_at=NULL,held_at=NULL,
   next_attempt_at=now(),lease_generation=d.lease_generation+1
   WHERE d.tenant_id=tenant AND d.event_id=requested_event;
  outcome := 'REQUEUED';
 ELSE
  UPDATE impact.outbox_delivery d SET held_at=NULL,next_attempt_at=now(),lease_generation=d.lease_generation+1
   WHERE d.tenant_id=tenant AND d.event_id=requested_event;
  outcome := 'RELEASED';
 END IF;
 RETURN QUERY SELECT outcome,d.state::text,d.held_at IS NOT NULL,d.attempts,d.lease_generation,
  r.state::text,r.attempts,r.last_error_class::text
  FROM impact.outbox_delivery d WHERE d.tenant_id=tenant AND d.event_id=requested_event;
END $$;
REVOKE ALL ON FUNCTION impact.operator_requeue_delivery(uuid,text,bigint) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.operator_requeue_delivery(uuid,text,bigint) TO impact_platform;
COMMIT;
