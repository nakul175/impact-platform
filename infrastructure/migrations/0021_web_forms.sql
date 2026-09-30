BEGIN;
SET LOCAL ROLE impact_owner;
-- Web forms (v0.20). Form and Submission have been registry kinds with typed projections since
-- 0002; this migration adds the payload columns the implemented contract writes and one insert-only
-- register of published form versions. A register row is written only by the publish command, after
-- an independent approval of the exact revision; a later version is a new row naming the revision it
-- supersedes, so a published version is never re-pointed and each version is superseded at most once.
ALTER TABLE impact.form_current
 ADD COLUMN programme_id uuid,
 ADD COLUMN programme_id_kind text GENERATED ALWAYS AS ('Programme') STORED,
 ADD CONSTRAINT form_programme_fk FOREIGN KEY(tenant_id,programme_id,programme_id_kind)
  REFERENCES impact.object_registry(tenant_id,object_id,object_type) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE impact.submission_current
 ADD COLUMN observation_ids jsonb CHECK(observation_ids IS NULL OR jsonb_typeof(observation_ids)='array'),
 ADD COLUMN quarantine_reason varchar(64),
 ADD COLUMN unit_key varchar(100);

CREATE TABLE impact.form_publication(
  tenant_id uuid NOT NULL,
  form_id uuid NOT NULL,
  version_number integer NOT NULL CHECK(version_number>0),
  form_revision uuid NOT NULL,
  approved_revision uuid NOT NULL,
  supersedes_revision uuid,
  published_by uuid NOT NULL,
  published_at timestamptz NOT NULL,
  form_revision_kind text GENERATED ALWAYS AS ('Form') STORED,
  PRIMARY KEY(tenant_id,form_id,version_number),
  UNIQUE(tenant_id,form_revision),
  UNIQUE(tenant_id,form_id,form_revision),
  UNIQUE(tenant_id,supersedes_revision),
  CHECK((version_number=1)=(supersedes_revision IS NULL)),
  FOREIGN KEY(tenant_id,form_id,form_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,form_revision,form_revision_kind) REFERENCES impact.object_revision(tenant_id,revision_id,object_type),
  FOREIGN KEY(tenant_id,form_id,approved_revision) REFERENCES impact.object_revision(tenant_id,object_id,revision_id),
  FOREIGN KEY(tenant_id,form_id,supersedes_revision) REFERENCES impact.form_publication(tenant_id,form_id,form_revision),
  FOREIGN KEY(tenant_id,published_by) REFERENCES impact.tenant_principal(tenant_id,principal_id)
);
ALTER TABLE impact.form_publication ENABLE ROW LEVEL SECURITY;
ALTER TABLE impact.form_publication FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_fence ON impact.form_publication USING(tenant_id=impact.current_tenant()) WITH CHECK(tenant_id=impact.current_tenant());
-- Insert-only for the application; nothing for the control plane.
GRANT SELECT,INSERT ON impact.form_publication TO impact_app;
COMMIT;
