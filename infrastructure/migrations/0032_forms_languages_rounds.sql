BEGIN;
SET LOCAL ROLE impact_owner;
-- Web forms, continued (v0.27): language versions inside the Form revision, the language a
-- response was presented in, the assignment a response fulfils, corrections of returned responses
-- and the unit a collection assignment covers. Additive only: new nullable projection columns for
-- payload properties the v0.27 contracts introduce. Collection rounds are a registry kind of 0002
-- ('CollectionRound') kept in object_registry/object_revision without a projection, like
-- CollectionPlan; no grant, role or policy changes.
--
-- Form: the language of the field definitions. The translations themselves are the existing
-- translation_versions array (empty before v0.27).
ALTER TABLE impact.form_current ADD COLUMN default_language varchar(16);
-- Submission: the language presented to the respondent, the assignment the response fulfils, and
-- for a correction the Submitted revision it supersedes with the stated reason.
ALTER TABLE impact.submission_current ADD COLUMN language varchar(16);
ALTER TABLE impact.submission_current ADD COLUMN correction_of_revision uuid;
ALTER TABLE impact.submission_current ADD COLUMN correction_reason text;
ALTER TABLE impact.submission_current ADD CONSTRAINT submission_assignment_kind
 FOREIGN KEY(tenant_id,assignment_id,assignment_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;
-- Assignment: the unit (the unit key an observation's source key starts with) the assignee is
-- expected to report for, and the history a reassignment leaves in the new revision.
ALTER TABLE impact.assignment_current ADD COLUMN unit_key varchar(100);
ALTER TABLE impact.assignment_current ADD COLUMN previous_assignee_id uuid;
ALTER TABLE impact.assignment_current ADD COLUMN reason text;
ALTER TABLE impact.assignment_current ADD CONSTRAINT assignment_round_kind
 FOREIGN KEY(tenant_id,round_id,round_id_kind) REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE impact.assignment_current ADD CONSTRAINT assignment_assignee
 FOREIGN KEY(tenant_id,assignee_id) REFERENCES impact.tenant_principal(tenant_id,principal_id) DEFERRABLE INITIALLY DEFERRED;
COMMIT;
