BEGIN;
SET LOCAL ROLE impact_owner;
-- FR-AI-001 explicit AI enablement and policy. Additive: two insert-only, tenant-fenced policy
-- registers, a nullable policy pin on the insert-only advisory reservation, the singleton index of
-- the 0002 registry kind AIConfiguration (no projection; no type CHECK change) and the generated
-- access profile that adds ai.policy.manage to TENANT_ADMIN.

-- One AIConfiguration object per tenant; each policy version is its next immutable revision.
CREATE UNIQUE INDEX ai_configuration_one_per_tenant ON impact.object_registry(tenant_id)
 WHERE object_type='AIConfiguration';

CREATE TABLE impact.ai_policy_version(
 tenant_id uuid NOT NULL,
 policy_version_id uuid NOT NULL,
 object_id uuid NOT NULL,
 revision_kind text GENERATED ALWAYS AS ('AIConfiguration') STORED,
 version_no integer NOT NULL CHECK(version_no>=1),
 created_by uuid NOT NULL,
 created_at timestamptz NOT NULL,
 PRIMARY KEY(tenant_id,policy_version_id),
 UNIQUE(tenant_id,version_no),
 FOREIGN KEY(tenant_id,object_id,policy_version_id)
   REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,policy_version_id,revision_kind)
   REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,created_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
-- Closed enums. Reserved use cases may be recorded only as disabled, no tool can be granted and
-- the destination list holds only the reviewed provider-and-region labels; widening any of these
-- is a later, reviewed migration.
CREATE TABLE impact.ai_use_case_policy(
 tenant_id uuid NOT NULL,
 policy_version_id uuid NOT NULL,
 use_case varchar(32) NOT NULL CHECK(use_case IN ('ADVISORY_DRAFT','EXTRACTION','REPORT_DRAFT','CHAT')),
 enabled boolean NOT NULL,
 data_classes text[] NOT NULL
   CHECK(data_classes <@ ARRAY['PUBLIC','INTERNAL','CONFIDENTIAL','RESTRICTED']::text[]
     AND cardinality(data_classes)<=4),
 destinations text[] NOT NULL
   CHECK(destinations <@ ARRAY['openai-us']::text[] AND cardinality(destinations)<=10),
 purposes text[] NOT NULL
   CHECK(cardinality(purposes)<=10 AND array_position(purposes,NULL) IS NULL
     AND array_position(purposes,'') IS NULL AND char_length(array_to_string(purposes,''))<=2000),
 languages text[] NOT NULL
   CHECK(cardinality(languages)<=20 AND array_position(languages,NULL) IS NULL
     AND array_to_string(languages,',') ~ '^([A-Za-z]{2,3}(-[A-Za-z0-9]{2,8}){0,3}(,[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8}){0,3})*)?$'),
 review_mode varchar(32) NOT NULL CHECK(review_mode IN ('HUMAN_REVIEW')),
 budget_units integer NOT NULL CHECK(budget_units BETWEEN 0 AND 1000000),
 tools text[] NOT NULL DEFAULT '{}' CHECK(cardinality(tools)=0),
 PRIMARY KEY(tenant_id,policy_version_id,use_case),
 FOREIGN KEY(tenant_id,policy_version_id) REFERENCES impact.ai_policy_version(tenant_id,policy_version_id),
 CONSTRAINT ai_use_case_reserved CHECK(NOT enabled OR use_case='ADVISORY_DRAFT'),
 CONSTRAINT ai_use_case_complete CHECK(NOT enabled OR (cardinality(data_classes)>0
   AND cardinality(destinations)>0 AND cardinality(purposes)>0 AND cardinality(languages)>0))
);
CREATE FUNCTION impact.guard_ai_policy_insert_only() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
 BEGIN RAISE EXCEPTION 'AI policy versions are insert-only' USING ERRCODE='42501'; END $$;
REVOKE ALL ON FUNCTION impact.guard_ai_policy_insert_only() FROM PUBLIC;
CREATE TRIGGER ai_policy_version_immutable BEFORE UPDATE OR DELETE ON impact.ai_policy_version
 FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_policy_insert_only();
CREATE TRIGGER ai_use_case_policy_immutable BEFORE UPDATE OR DELETE ON impact.ai_use_case_policy
 FOR EACH ROW EXECUTE FUNCTION impact.guard_ai_policy_insert_only();
ALTER TABLE impact.ai_policy_version ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_policy_version FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_policy_version
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.ai_use_case_policy ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_use_case_policy FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_use_case_policy
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
GRANT SELECT,INSERT ON impact.ai_policy_version,impact.ai_use_case_policy TO impact_app;

-- Every new reservation records the policy version that allowed it. Rows reserved before this
-- migration keep NULL (the table is insert-only); NOT VALID applies the CHECK to new rows only.
ALTER TABLE impact.ai_advisory_request ADD COLUMN policy_version_id uuid;
ALTER TABLE impact.ai_advisory_request ADD CONSTRAINT ai_advisory_request_policy_version
 FOREIGN KEY(tenant_id,policy_version_id) REFERENCES impact.ai_policy_version(tenant_id,policy_version_id);
ALTER TABLE impact.ai_advisory_request ADD CONSTRAINT ai_advisory_request_policy_required
 CHECK(policy_version_id IS NOT NULL) NOT VALID;

-- The generated onboarding profile with ai.policy.manage for TENANT_ADMIN. Existing tenant ceilings
-- are unchanged; the reviewed access-upgrade path (0036) is the only way to widen them.
INSERT INTO impact.platform_access_profile(profile_hash,manifest,source_migration)
 VALUES('14997060d0b7d8a95c820674a5b1ad38c029eeed5d113e674a6ca04ec28ce133',$profile_0041${"purpose_bound":["audit.export","privacy-cases.draft.create","privacy-cases.draft.edit","privacy-cases.read","privacy.approve","privacy.execute","privacy.export"],"roles":{"ANALYST":["ai.enablement.read","calculated-results.read","dashboards.read","decisions.read","evidence.download","evidence.read","framework.export","frameworks.read","imports.read","indicator-definitions.read","indicator-instances.read","notifications.acknowledge","notifications.read","observations.read","periods.read","programmes.read","publication.download","report-templates.read","report.export","reports.read","snapshots.read","targets.read","uploads.read","work-items.read","workflows.read"],"AUDIT_READER":["audit-events.read","notifications.read","uploads.read"],"AUTHOR":["ai.enablement.read","assignments.read","calculated-results.read","collection-plan.submit","collection-plans.draft.create","collection-plans.draft.edit","collection-plans.read","collection-rounds.read","dashboards.read","decisions.read","disclosure.request","evidence.attach","evidence.download","evidence.draft.create","evidence.draft.edit","evidence.read","form.submit","forms.draft.create","forms.draft.edit","forms.read","framework.submit","frameworks.draft.create","frameworks.draft.edit","frameworks.read","geographies.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.draft.create","indicator-definitions.draft.edit","indicator-definitions.read","indicator-instances.draft.create","indicator-instances.draft.edit","indicator-instances.read","indicator.submit","lineage-manifests.read","measurement-changes.draft.create","measurement-changes.draft.edit","measurement-changes.read","measurement-changes.submit","measurement-members.read","notifications.acknowledge","notifications.read","observation.submit","observations.draft.create","observations.draft.edit","observations.read","period-closes.read","periods.read","programmes.read","publication.download","report-templates.read","report.export","report.submit","reporting-calendars.read","reports.draft.create","reports.draft.edit","reports.read","restatement-requests.read","snapshots.read","submission.correct","submission.submit","submissions.draft.create","submissions.draft.edit","submissions.read","target.submit","targets.draft.create","targets.draft.edit","targets.read","upload.create","upload.write","uploads.read","work-items.read","workflow-templates.read","workflows.read"],"DATA_STEWARD":["ai.enablement.read","assignments.read","calculated-results.read","dashboards.read","decisions.read","evidence.attach","evidence.download","evidence.draft.create","evidence.draft.edit","evidence.read","forms.read","frameworks.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.read","indicator-instances.read","notifications.read","observations.draft.create","observations.draft.edit","observations.read","periods.read","programmes.read","publication.download","report-templates.read","reports.read","snapshots.read","submissions.read","targets.read","upload.create","upload.write","uploads.read","work-items.read","workflows.read"],"ENUMERATOR":["assignments.read","collection-rounds.read","forms.read","notifications.read","submission.correct","submission.submit","submissions.draft.create","submissions.draft.edit","submissions.read","upload.create","upload.write","uploads.read"],"EXTERNAL":["calculated-results.read","dashboards.read","decisions.read","evidence.read","frameworks.read","indicator-definitions.read","indicator-instances.read","invitation.accept","notifications.acknowledge","notifications.read","observations.read","periods.read","programmes.read","publication.download","report-templates.read","reports.read","snapshots.read","targets.read","uploads.read","work-items.read","workflows.read"],"MEL_ADMIN":["ai.advisory.request","ai.enablement.export","ai.enablement.manage","ai.enablement.read","assignments.draft.create","assignments.draft.edit","assignments.read","calculated-results.read","collection-plan.submit","collection-plans.draft.create","collection-plans.draft.edit","collection-plans.read","collection-rounds.draft.create","collection-rounds.draft.edit","collection-rounds.read","dashboards.read","decisions.read","disclosures.read","evidence.read","form.publish","form.submit","forms.draft.create","forms.draft.edit","forms.read","framework.export","framework.submit","frameworks.draft.create","frameworks.draft.edit","frameworks.read","geographies.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.draft.create","indicator-definitions.draft.edit","indicator-definitions.read","indicator-instances.draft.create","indicator-instances.draft.edit","indicator-instances.read","indicator.activate","indicator.calculate","indicator.submit","lineage-manifests.read","measurement-changes.draft.create","measurement-changes.draft.edit","measurement-changes.read","measurement-changes.submit","measurement-members.read","notifications.acknowledge","notifications.read","observations.read","period-closes.read","period.close","period.restate","periods.read","programme.activate","programmes.draft.create","programmes.draft.edit","programmes.read","publication.download","report-templates.read","report.export","report.publish","report.withdraw","reporting-calendars.read","reports.read","restatement-requests.read","snapshots.read","submissions.read","target.submit","targets.draft.create","targets.draft.edit","targets.read","uploads.read","work-items.read","workflow-templates.read","workflows.read"],"PRIVACY":["disclosure.request","disclosures.read","notifications.read","publication.download","report.withdraw","reports.read","retention-holds.read","retention-policies.draft.create","retention-policies.draft.edit","retention-policies.read","retention-policy.approve","retention.hold","retention.read","retention.release","uploads.read"],"PROGRAMME_MANAGER":["ai.advisory.request","ai.enablement.export","ai.enablement.manage","ai.enablement.read","assignment.reassign","assignments.draft.create","assignments.draft.edit","assignments.read","calculated-results.read","collection-plan.submit","collection-plans.draft.create","collection-plans.draft.edit","collection-plans.read","collection-rounds.draft.create","collection-rounds.draft.edit","collection-rounds.read","dashboards.read","decisions.read","evidence.read","form.submit","forms.read","framework.export","frameworks.read","geographies.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.read","indicator-instances.read","indicator.activate","indicator.calculate","lineage-manifests.read","measurement-changes.draft.create","measurement-changes.draft.edit","measurement-changes.read","measurement-changes.submit","measurement-members.read","notifications.acknowledge","notifications.read","observation.submit","observations.read","period-closes.read","period.close","period.restate","periods.read","programme.activate","programmes.draft.create","programmes.draft.edit","programmes.read","publication.download","report-templates.read","report.export","reporting-calendars.read","reports.read","restatement-requests.read","snapshots.read","submissions.read","targets.read","uploads.read","work-items.read","workflow-templates.read","workflows.read"],"REVIEWER":["ai.enablement.read","assignments.read","calculated-results.read","collection-plans.read","collection-rounds.read","dashboards.read","decisions.read","evidence.download","evidence.read","forms.read","frameworks.read","geographies.read","imports.read","indicator-definitions.read","indicator-instances.read","lineage-manifests.read","measurement-changes.read","measurement-members.read","notifications.acknowledge","notifications.read","observations.read","period-closes.read","periods.read","programmes.read","publication.download","report-templates.read","report.export","reporting-calendars.read","reports.read","restatement-requests.read","snapshots.read","submissions.read","targets.read","uploads.read","work-items.read","workflow-templates.read","workflow.approve","workflow.reject","workflow.return","workflows.read"],"TENANT_ADMIN":["access-denials.read","access-requests.read","access-scopes.create","access-scopes.read","ai.advisory.request","ai.enablement.export","ai.enablement.manage","ai.enablement.read","ai.policy.manage","connections.read","grant.approve","grant.request","grant.revoke","grants.read","groups.approve","groups.manage","groups.read","groups.request","member-invitations.read","member.invite","membership.reactivate","membership.renew.approve","membership.renew.request","membership.revoke","membership.suspend","memberships.read","notifications.read","organisation-units.manage","organisation-units.read","ownership.transfer","reference-data.manage","retention-holds.read","retention-policies.draft.create","retention-policies.draft.edit","retention-policies.read","retention-policy.approve","retention.hold","retention.read","retention.release","role-templates.read","roles.manage","uploads.read"]},"version":"initial-access-v2"}$profile_0041$::jsonb,'0041_ai_policy.sql');
COMMIT;
