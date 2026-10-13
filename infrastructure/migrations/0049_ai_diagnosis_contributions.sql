-- Governed, scoped contributions to one existing diagnosis.
BEGIN;
SET LOCAL ROLE impact_owner;

-- Registered for governed future/bootstrap upgrades only. Existing tenants are
-- not widened or auto-activated by this migration.
INSERT INTO impact.platform_access_profile(profile_hash,manifest,source_migration)
 VALUES('d58e9f971a4fb2c0d5aa4813cfeabd9edc612a6c61eae9dd2c83b9b1606c32ed',$profile_0049${"purpose_bound":["audit.export","privacy-cases.draft.create","privacy-cases.draft.edit","privacy-cases.read","privacy.approve","privacy.execute","privacy.export"],"roles":{"ANALYST":["ai.enablement.read","calculated-results.read","dashboards.read","decisions.read","evidence.download","evidence.read","framework.export","frameworks.read","imports.read","indicator-definitions.read","indicator-instances.read","notifications.acknowledge","notifications.read","observations.read","periods.read","programmes.read","publication.download","report-templates.read","report.export","reports.read","snapshots.read","targets.read","uploads.read","work-items.read","workflows.read"],"AUDIT_READER":["audit-events.read","notifications.read","uploads.read"],"AUTHOR":["ai.diagnosis.contribute","ai.enablement.read","assignments.read","calculated-results.read","collection-plan.submit","collection-plans.draft.create","collection-plans.draft.edit","collection-plans.read","collection-rounds.read","dashboards.read","decisions.read","disclosure.request","evidence.attach","evidence.download","evidence.draft.create","evidence.draft.edit","evidence.read","form.submit","forms.draft.create","forms.draft.edit","forms.read","framework.submit","frameworks.draft.create","frameworks.draft.edit","frameworks.read","geographies.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.draft.create","indicator-definitions.draft.edit","indicator-definitions.read","indicator-instances.draft.create","indicator-instances.draft.edit","indicator-instances.read","indicator.submit","lineage-manifests.read","measurement-changes.draft.create","measurement-changes.draft.edit","measurement-changes.read","measurement-changes.submit","measurement-members.read","notifications.acknowledge","notifications.read","observation.submit","observations.draft.create","observations.draft.edit","observations.read","period-closes.read","periods.read","programmes.read","publication.download","report-templates.read","report.export","report.submit","reporting-calendars.read","reports.draft.create","reports.draft.edit","reports.read","restatement-requests.read","snapshots.read","submission.correct","submission.submit","submissions.draft.create","submissions.draft.edit","submissions.read","target.submit","targets.draft.create","targets.draft.edit","targets.read","upload.create","upload.write","uploads.read","work-items.read","workflow-templates.read","workflows.read"],"DATA_STEWARD":["ai.enablement.read","assignments.read","calculated-results.read","dashboards.read","decisions.read","evidence.attach","evidence.download","evidence.draft.create","evidence.draft.edit","evidence.read","forms.read","frameworks.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.read","indicator-instances.read","notifications.read","observations.draft.create","observations.draft.edit","observations.read","periods.read","programmes.read","publication.download","report-templates.read","reports.read","snapshots.read","submissions.read","targets.read","upload.create","upload.write","uploads.read","work-items.read","workflows.read"],"ENUMERATOR":["assignments.read","collection-rounds.read","forms.read","notifications.read","submission.correct","submission.submit","submissions.draft.create","submissions.draft.edit","submissions.read","upload.create","upload.write","uploads.read"],"EXTERNAL":["calculated-results.read","dashboards.read","decisions.read","evidence.read","frameworks.read","indicator-definitions.read","indicator-instances.read","invitation.accept","notifications.acknowledge","notifications.read","observations.read","periods.read","programmes.read","publication.download","report-templates.read","reports.read","snapshots.read","targets.read","uploads.read","work-items.read","workflows.read"],"FINANCE":["ai.enablement.read","notifications.read","uploads.read"],"MEL_ADMIN":["ai.advisory.request","ai.diagnosis.contribute","ai.diagnosis.contributors.manage","ai.enablement.export","ai.enablement.manage","ai.enablement.read","assignments.draft.create","assignments.draft.edit","assignments.read","calculated-results.read","collection-plan.submit","collection-plans.draft.create","collection-plans.draft.edit","collection-plans.read","collection-rounds.draft.create","collection-rounds.draft.edit","collection-rounds.read","dashboards.read","decisions.read","disclosures.read","evidence.read","form.publish","form.submit","forms.draft.create","forms.draft.edit","forms.read","framework.export","framework.submit","frameworks.draft.create","frameworks.draft.edit","frameworks.read","geographies.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.draft.create","indicator-definitions.draft.edit","indicator-definitions.read","indicator-instances.draft.create","indicator-instances.draft.edit","indicator-instances.read","indicator.activate","indicator.calculate","indicator.submit","lineage-manifests.read","measurement-changes.draft.create","measurement-changes.draft.edit","measurement-changes.read","measurement-changes.submit","measurement-members.read","notifications.acknowledge","notifications.read","observations.read","period-closes.read","period.close","period.restate","periods.read","programme.activate","programmes.draft.create","programmes.draft.edit","programmes.read","publication.download","report-templates.read","report.export","report.publish","report.withdraw","reporting-calendars.read","reports.read","restatement-requests.read","snapshots.read","submissions.read","target.submit","targets.draft.create","targets.draft.edit","targets.read","uploads.read","work-items.read","workflow-templates.read","workflows.read"],"PRIVACY":["disclosure.request","disclosures.read","notifications.read","publication.download","report.withdraw","reports.read","retention-holds.read","retention-policies.draft.create","retention-policies.draft.edit","retention-policies.read","retention-policy.approve","retention.hold","retention.read","retention.release","uploads.read"],"PROGRAMME_MANAGER":["ai.advisory.request","ai.diagnosis.contribute","ai.diagnosis.contributors.manage","ai.enablement.export","ai.enablement.manage","ai.enablement.read","assignment.reassign","assignments.draft.create","assignments.draft.edit","assignments.read","calculated-results.read","collection-plan.submit","collection-plans.draft.create","collection-plans.draft.edit","collection-plans.read","collection-rounds.draft.create","collection-rounds.draft.edit","collection-rounds.read","dashboards.read","decisions.read","evidence.read","form.submit","forms.read","framework.export","frameworks.read","geographies.read","import.cancel","import.commit","import.preview","imports.draft.create","imports.draft.edit","imports.read","indicator-definitions.read","indicator-instances.read","indicator.activate","indicator.calculate","lineage-manifests.read","measurement-changes.draft.create","measurement-changes.draft.edit","measurement-changes.read","measurement-changes.submit","measurement-members.read","notifications.acknowledge","notifications.read","observation.submit","observations.read","period-closes.read","period.close","period.restate","periods.read","programme.activate","programmes.draft.create","programmes.draft.edit","programmes.read","publication.download","report-templates.read","report.export","reporting-calendars.read","reports.read","restatement-requests.read","snapshots.read","submissions.read","targets.read","uploads.read","work-items.read","workflow-templates.read","workflows.read"],"REVIEWER":["ai.diagnosis.contribute","ai.enablement.read","assignments.read","calculated-results.read","collection-plans.read","collection-rounds.read","dashboards.read","decisions.read","evidence.download","evidence.read","forms.read","frameworks.read","geographies.read","imports.read","indicator-definitions.read","indicator-instances.read","lineage-manifests.read","measurement-changes.read","measurement-members.read","notifications.acknowledge","notifications.read","observations.read","period-closes.read","periods.read","programmes.read","publication.download","report-templates.read","report.export","reporting-calendars.read","reports.read","restatement-requests.read","snapshots.read","submissions.read","targets.read","uploads.read","work-items.read","workflow-templates.read","workflow.approve","workflow.reject","workflow.return","workflows.read"],"TENANT_ADMIN":["access-denials.read","access-requests.read","access-scopes.create","access-scopes.read","ai.advisory.request","ai.diagnosis.contribute","ai.diagnosis.contributors.manage","ai.diagnosis.manage","ai.diagnosis.read","ai.enablement.export","ai.enablement.manage","ai.enablement.read","ai.policy.manage","ai.problem-baseline.manage","ai.problem-baseline.read","connections.read","grant.approve","grant.request","grant.revoke","grants.read","groups.approve","groups.manage","groups.read","groups.request","member-invitations.read","member.invite","membership.reactivate","membership.renew.approve","membership.renew.request","membership.revoke","membership.suspend","memberships.read","notifications.read","organisation-units.manage","organisation-units.read","ownership.transfer","reference-data.manage","retention-holds.read","retention-policies.draft.create","retention-policies.draft.edit","retention-policies.read","retention-policy.approve","retention.hold","retention.read","retention.release","role-templates.read","roles.manage","uploads.read"]},"version":"initial-access-v2"}$profile_0049$::jsonb,'0049_ai_diagnosis_contributions.sql');

CREATE TABLE impact.ai_diagnosis_contributor_assignment(
 tenant_id uuid NOT NULL,
 assignment_id uuid NOT NULL,
 diagnosis_id uuid NOT NULL,
 diagnosis_revision uuid NOT NULL,
 diagnosis_kind text GENERATED ALWAYS AS ('AIDiagnosis') STORED,
 member_invitation_id uuid NOT NULL,
 contribution_role text NOT NULL CHECK(contribution_role IN
  ('PROBLEM_OWNER','EVIDENCE_CONTRIBUTOR','PRIORITISATION_CONTRIBUTOR')),
 problem_ids uuid[] NOT NULL CHECK(cardinality(problem_ids) BETWEEN 1 AND 20),
 sections text[] NOT NULL CHECK(cardinality(sections) BETWEEN 1 AND 4),
 inviter_id uuid NOT NULL,
 created_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 PRIMARY KEY(tenant_id,assignment_id),
 UNIQUE(tenant_id,diagnosis_id,member_invitation_id),
 FOREIGN KEY(tenant_id,diagnosis_id,diagnosis_revision)
  REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,diagnosis_revision,diagnosis_kind)
  REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,member_invitation_id)
  REFERENCES impact.member_invitation(tenant_id,invitation_id),
 FOREIGN KEY(tenant_id,inviter_id)
  REFERENCES impact.tenant_principal(tenant_id,principal_id),
 CHECK(sections <@ ARRAY['PROBLEM_DESCRIPTION','AFFECTED_AREA','SUPPORTING_EVIDENCE','PRIORITY_ORDER']::text[])
);

CREATE TABLE impact.ai_diagnosis_contribution(
 tenant_id uuid NOT NULL,
 contribution_id uuid NOT NULL,
 assignment_id uuid NOT NULL,
 diagnosis_id uuid NOT NULL,
 base_revision uuid NOT NULL,
 diagnosis_kind text GENERATED ALWAYS AS ('AIDiagnosis') STORED,
 contributor_principal_id uuid NOT NULL,
 contributor_membership_id uuid NOT NULL,
 patch jsonb NOT NULL CHECK(jsonb_typeof(patch)='object'),
 submitted_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 PRIMARY KEY(tenant_id,contribution_id),
 FOREIGN KEY(tenant_id,assignment_id)
  REFERENCES impact.ai_diagnosis_contributor_assignment(tenant_id,assignment_id),
 FOREIGN KEY(tenant_id,diagnosis_id,base_revision)
  REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,base_revision,diagnosis_kind)
  REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,contributor_principal_id)
  REFERENCES impact.tenant_principal(tenant_id,principal_id),
 FOREIGN KEY(tenant_id,contributor_membership_id)
  REFERENCES impact.membership_current(tenant_id,object_id)
);

CREATE TABLE impact.ai_diagnosis_contribution_decision(
 tenant_id uuid NOT NULL,
 contribution_id uuid NOT NULL,
 decision text NOT NULL CHECK(decision IN ('ACCEPTED','REJECTED')),
 reason text,
 diagnosis_id uuid NOT NULL,
 diagnosis_before_revision uuid NOT NULL,
 diagnosis_after_revision uuid NOT NULL,
 diagnosis_kind text GENERATED ALWAYS AS ('AIDiagnosis') STORED,
 decided_by uuid NOT NULL,
 decided_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 PRIMARY KEY(tenant_id,contribution_id),
 FOREIGN KEY(tenant_id,contribution_id)
  REFERENCES impact.ai_diagnosis_contribution(tenant_id,contribution_id),
 FOREIGN KEY(tenant_id,diagnosis_id,diagnosis_before_revision)
  REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,diagnosis_id,diagnosis_after_revision)
  REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
 FOREIGN KEY(tenant_id,diagnosis_before_revision,diagnosis_kind)
  REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,diagnosis_after_revision,diagnosis_kind)
  REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
 FOREIGN KEY(tenant_id,decided_by)
  REFERENCES impact.tenant_principal(tenant_id,principal_id),
 CHECK((decision='REJECTED' AND reason IS NOT NULL AND length(btrim(reason)) BETWEEN 1 AND 1000)
    OR (decision='ACCEPTED' AND reason IS NULL))
);

ALTER TABLE impact.ai_diagnosis_contributor_assignment ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_diagnosis_contributor_assignment FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_diagnosis_contributor_assignment
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.ai_diagnosis_contribution ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_diagnosis_contribution FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_diagnosis_contribution
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
ALTER TABLE impact.ai_diagnosis_contribution_decision ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.ai_diagnosis_contribution_decision FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.ai_diagnosis_contribution_decision
 USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());

GRANT SELECT,INSERT ON impact.ai_diagnosis_contributor_assignment TO impact_app;
GRANT SELECT,INSERT ON impact.ai_diagnosis_contribution TO impact_app;
GRANT SELECT,INSERT ON impact.ai_diagnosis_contribution_decision TO impact_app;

CREATE FUNCTION impact.guard_ai_diagnosis_contribution_immutable() RETURNS trigger
 LANGUAGE plpgsql SET search_path=pg_catalog,impact AS $$
BEGIN
 IF TG_OP<>'INSERT' THEN
  RAISE EXCEPTION 'diagnosis collaboration records are immutable' USING ERRCODE='42501';
 END IF;
 RETURN NEW;
END;
$$;
REVOKE ALL ON FUNCTION impact.guard_ai_diagnosis_contribution_immutable() FROM PUBLIC;
CREATE TRIGGER ai_diagnosis_assignment_immutable BEFORE UPDATE OR DELETE
 ON impact.ai_diagnosis_contributor_assignment FOR EACH ROW
 EXECUTE FUNCTION impact.guard_ai_diagnosis_contribution_immutable();
CREATE TRIGGER ai_diagnosis_contribution_immutable BEFORE UPDATE OR DELETE
 ON impact.ai_diagnosis_contribution FOR EACH ROW
 EXECUTE FUNCTION impact.guard_ai_diagnosis_contribution_immutable();
CREATE TRIGGER ai_diagnosis_decision_immutable BEFORE UPDATE OR DELETE
 ON impact.ai_diagnosis_contribution_decision FOR EACH ROW
 EXECUTE FUNCTION impact.guard_ai_diagnosis_contribution_immutable();

COMMIT;
