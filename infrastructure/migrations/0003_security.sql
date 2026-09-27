BEGIN;

SET LOCAL ROLE impact_owner;

CREATE FUNCTION impact.current_tenant() RETURNS uuid LANGUAGE sql STABLE AS $$ SELECT nullif(current_setting('impact.tenant_id',true),'')::uuid $$;

REVOKE ALL ON FUNCTION impact.current_tenant() FROM PUBLIC;

GRANT EXECUTE ON FUNCTION impact.current_tenant() TO impact_app,impact_worker,impact_identity,impact_sensitive,impact_privacy,impact_observer;

ALTER TABLE impact.tenant_root ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.tenant_root FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.tenant_root USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.tenant_principal ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.tenant_principal FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.tenant_principal USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.object_registry ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.object_registry FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.object_registry USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.object_revision ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.object_revision FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.object_revision USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.tenant_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.tenant_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.tenant_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.membership_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.membership_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.membership_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.grant_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.grant_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.grant_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.organisation_unit_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.organisation_unit_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.organisation_unit_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.programme_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.programme_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.programme_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.framework_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.framework_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.framework_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.indicator_definition_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.indicator_definition_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.indicator_definition_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.indicator_instance_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.indicator_instance_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.indicator_instance_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.target_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.target_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.target_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.dimension_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.dimension_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.dimension_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.period_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.period_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.period_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p00 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p00 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p00 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p01 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p01 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p01 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p02 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p02 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p02 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p03 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p03 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p03 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p04 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p04 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p04 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p05 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p05 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p05 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p06 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p06 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p06 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p07 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p07 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p07 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p08 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p08 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p08 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p09 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p09 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p09 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p10 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p10 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p10 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p11 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p11 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p11 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p12 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p12 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p12 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p13 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p13 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p13 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p14 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p14 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p14 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p15 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p15 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p15 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p16 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p16 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p16 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p17 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p17 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p17 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p18 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p18 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p18 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p19 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p19 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p19 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p20 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p20 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p20 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p21 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p21 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p21 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p22 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p22 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p22 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p23 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p23 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p23 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p24 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p24 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p24 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p25 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p25 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p25 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p26 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p26 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p26 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p27 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p27 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p27 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p28 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p28 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p28 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p29 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p29 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p29 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p30 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p30 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p30 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.observation_p31 ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.observation_p31 FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.observation_p31 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.calculated_result_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.calculated_result_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.calculated_result_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.form_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.form_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.form_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.form_field_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.form_field_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.form_field_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.assignment_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.assignment_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.assignment_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.submission_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.submission_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.submission_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.participant_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.participant_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.participant_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.service_event_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.service_event_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.service_event_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.handling_record_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.handling_record_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.handling_record_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.dataset_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.dataset_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.dataset_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.import_job_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.import_job_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.import_job_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.quality_issue_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.quality_issue_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.quality_issue_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.evidence_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.evidence_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.evidence_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.workflow_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.workflow_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.workflow_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.decision_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.decision_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.decision_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.snapshot_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.snapshot_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.snapshot_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.report_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.report_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.report_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.disclosure_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.disclosure_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.disclosure_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.budget_line_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.budget_line_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.budget_line_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.connection_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.connection_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.connection_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.a_i_task_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.a_i_task_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.a_i_task_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.privacy_case_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.privacy_case_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.privacy_case_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.audit_event_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.audit_event_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.audit_event_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.evaluation_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.evaluation_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.evaluation_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.retention_policy_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.retention_policy_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.retention_policy_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.subscription_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.subscription_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.subscription_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.funding_agreement_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.funding_agreement_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.funding_agreement_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.finance_transaction_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.finance_transaction_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.finance_transaction_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.exchange_rate_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.exchange_rate_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.exchange_rate_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.allocation_rule_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.allocation_rule_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.allocation_rule_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.work_item_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.work_item_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.work_item_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.dashboard_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.dashboard_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.dashboard_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.report_template_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.report_template_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.report_template_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.notification_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.notification_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.notification_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.schedule_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.schedule_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.schedule_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.qualitative_extract_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.qualitative_extract_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.qualitative_extract_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.device_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.device_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.device_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.support_request_current ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.support_request_current FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.support_request_current USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.scope_definition ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.scope_definition FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.scope_definition USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.scope_member ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.scope_member FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.scope_member USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.operation_receipt ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.operation_receipt FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.operation_receipt USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.source_key_registry ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.source_key_registry FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.source_key_registry USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.source_revision_receipt ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.source_revision_receipt FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.source_revision_receipt USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.workflow_author ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.workflow_author FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.workflow_author USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.review_decision ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.review_decision FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.review_decision USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.lineage_edge ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.lineage_edge FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.lineage_edge USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.snapshot_member ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.snapshot_member FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.snapshot_member USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.file_blob ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.file_blob FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.file_blob USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.offline_grant ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.offline_grant FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.offline_grant USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.sync_receipt ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.sync_receipt FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.sync_receipt USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.service_identity ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.service_identity FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.service_identity USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.job ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.job FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.job USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.job_item ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.job_item FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.job_item USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.outbox_event ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.outbox_event FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.outbox_event USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.outbox_delivery ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.outbox_delivery FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.outbox_delivery USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.consumer_receipt ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.consumer_receipt FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.consumer_receipt USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.deletion_ledger ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.deletion_ledger FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.deletion_ledger USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.retention_hold ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.retention_hold FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.retention_hold USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.privacy_store_action ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.privacy_store_action FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.privacy_store_action USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.participant_private ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.participant_private FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.participant_private USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.webhook_delivery ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.webhook_delivery FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.webhook_delivery USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.audit_batch_root ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.audit_batch_root FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.audit_batch_root USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.application_session ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.application_session FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.application_session USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.member_invitation ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.member_invitation FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.member_invitation USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.upload_session ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.upload_session FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.upload_session USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

ALTER TABLE impact.upload_part ENABLE ROW LEVEL SECURITY; ALTER TABLE impact.upload_part FORCE ROW LEVEL SECURITY; CREATE POLICY tenant_fence ON impact.upload_part USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

GRANT SELECT,INSERT,UPDATE ON impact.tenant_root TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.tenant_principal TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.object_registry TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.object_revision TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.tenant_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.membership_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.grant_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.organisation_unit_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.programme_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.framework_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.indicator_definition_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.indicator_instance_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.target_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.dimension_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.period_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.observation_current TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.calculated_result_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.form_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.form_field_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.assignment_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.submission_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.participant_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.service_event_current TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.handling_record_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.dataset_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.import_job_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.quality_issue_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.evidence_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.workflow_current TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.decision_current TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.snapshot_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.report_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.disclosure_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.budget_line_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.connection_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.a_i_task_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.privacy_case_current TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.audit_event_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.evaluation_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.retention_policy_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.subscription_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.funding_agreement_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.finance_transaction_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.exchange_rate_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.allocation_rule_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.work_item_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.dashboard_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.report_template_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.notification_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.schedule_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.qualitative_extract_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.device_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.support_request_current TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.scope_definition TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.scope_member TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.operation_receipt TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.source_key_registry TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.source_revision_receipt TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.workflow_author TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.review_decision TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.lineage_edge TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.snapshot_member TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.file_blob TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.offline_grant TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.sync_receipt TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.service_identity TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.job TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.job_item TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.outbox_event TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.outbox_delivery TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.consumer_receipt TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.deletion_ledger TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.retention_hold TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.privacy_store_action TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.webhook_delivery TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.audit_batch_root TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.upload_session TO impact_app,impact_worker;

GRANT SELECT,INSERT ON impact.upload_part TO impact_app,impact_worker;

GRANT SELECT,INSERT,UPDATE ON impact.auth_identity TO impact_identity;

GRANT SELECT,INSERT,UPDATE ON impact.application_session,impact.member_invitation TO impact_identity;

GRANT SELECT,INSERT,UPDATE ON impact.participant_private TO impact_sensitive;

GRANT SELECT ON impact.tenant_root TO impact_observer;

GRANT SELECT ON impact.object_revision,impact.object_registry,impact.privacy_case_current,impact.privacy_store_action,impact.retention_hold,impact.deletion_ledger TO impact_privacy;

GRANT UPDATE(payload,restriction_state) ON impact.object_revision TO impact_privacy;

GRANT INSERT ON impact.deletion_ledger TO impact_privacy;

GRANT UPDATE(state) ON impact.privacy_store_action TO impact_privacy;

GRANT SELECT,DELETE ON impact.participant_private TO impact_privacy;

ALTER DEFAULT PRIVILEGES FOR ROLE impact_owner IN SCHEMA impact REVOKE ALL ON TABLES FROM PUBLIC;

ALTER DEFAULT PRIVILEGES FOR ROLE impact_owner IN SCHEMA impact REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

CREATE FUNCTION impact.guard_revision_removal() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE case_ref uuid;
BEGIN
 IF NOT pg_has_role(current_user,'impact_privacy','USAGE') THEN RAISE EXCEPTION 'immutable revision'; END IF;
 case_ref := nullif(current_setting('impact.privacy_case_id',true),'')::uuid;
 IF case_ref IS NULL OR NEW.tenant_id<>impact.current_tenant() THEN RAISE EXCEPTION 'privacy context required'; END IF;
 IF (to_jsonb(OLD)-'payload'-'restriction_state') IS DISTINCT FROM (to_jsonb(NEW)-'payload'-'restriction_state') THEN RAISE EXCEPTION 'immutable metadata'; END IF;
 IF NEW.payload IS NOT NULL OR NEW.restriction_state<>'REMOVED' THEN RAISE EXCEPTION 'removal only'; END IF;
 IF EXISTS(SELECT 1 FROM impact.retention_hold WHERE tenant_id=OLD.tenant_id AND object_id=OLD.object_id AND released_at IS NULL) THEN RAISE EXCEPTION 'active hold'; END IF;
 IF NOT EXISTS(SELECT 1 FROM impact.privacy_store_action WHERE tenant_id=OLD.tenant_id AND case_id=case_ref AND object_id=OLD.object_id AND store='DATABASE' AND action='DELETE' AND state='EXECUTING') THEN RAISE EXCEPTION 'approved executing plan required'; END IF;
 IF NOT EXISTS(SELECT 1 FROM impact.deletion_ledger WHERE tenant_id=OLD.tenant_id AND case_id=case_ref AND object_id=OLD.object_id) THEN RAISE EXCEPTION 'durable ledger prerequisite'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER revision_removal_guard BEFORE UPDATE ON impact.object_revision FOR EACH ROW EXECUTE FUNCTION impact.guard_revision_removal();


REVOKE ALL ON FUNCTION impact.guard_revision_removal() FROM PUBLIC;

COMMIT;