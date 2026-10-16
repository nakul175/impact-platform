-- Permit the authenticated application to lock an extraction draft for one human review.
BEGIN;
SET LOCAL ROLE impact_owner;

-- SELECT FOR UPDATE needs an UPDATE privilege even though the review path never changes the
-- proposal. Grant one key column only and keep every draft immutable with a database trigger.
CREATE FUNCTION impact.refuse_ai_extraction_draft_update()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog, impact
AS $$
BEGIN
  RAISE EXCEPTION 'ai extraction drafts are immutable' USING ERRCODE='55000';
END
$$;
REVOKE ALL ON FUNCTION impact.refuse_ai_extraction_draft_update() FROM PUBLIC;

CREATE TRIGGER ai_extraction_draft_immutable
BEFORE UPDATE ON impact.ai_extraction_draft
FOR EACH ROW EXECUTE FUNCTION impact.refuse_ai_extraction_draft_update();

GRANT UPDATE(draft_id) ON impact.ai_extraction_draft TO impact_app;

COMMIT;
