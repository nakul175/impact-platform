-- Reviewed additive0039 candidate; integrator registers exact bytes after review.
-- Older unavailable plan pins end every case/pointer read through the central helper.
-- Keep frozen0038 unchanged; no new tables, data changes or broader runtime privileges.
BEGIN;
SET LOCAL ROLE impact_owner;

CREATE OR REPLACE FUNCTION impact.human_advice_participant(target uuid,material boolean DEFAULT false) RETURNS boolean
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,impact AS $$
 SELECT EXISTS(
  SELECT 1 FROM impact.human_advice_case_current c
  JOIN impact.tenant_principal p ON p.tenant_id=c.tenant_id AND p.principal_id=impact.human_advice_principal()
  JOIN impact.auth_identity i ON i.identity_id=p.identity_id
  JOIN impact.membership_current m ON m.tenant_id=c.tenant_id AND m.identity_id=p.identity_id
  JOIN impact.object_registry h ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id
  JOIN impact.object_registry plan ON plan.tenant_id=c.tenant_id AND plan.object_id=c.context_plan_id
  JOIN impact.object_revision plan_head ON plan_head.tenant_id=plan.tenant_id
    AND plan_head.object_id=plan.object_id AND plan_head.revision_id=plan.head_revision
  JOIN impact.object_revision plan_anchor ON plan_anchor.tenant_id=c.tenant_id
    AND plan_anchor.object_id=c.context_plan_id AND plan_anchor.revision_id=c.context_plan_revision
    AND plan_anchor.object_type='AIAdoptionPlan'
  WHERE c.tenant_id=impact.current_tenant() AND c.object_id=target AND p.active
  AND plan.object_type='AIAdoptionPlan' AND plan.classification<>'RESTRICTED'
  AND plan_head.restriction_state='AVAILABLE' AND plan_anchor.restriction_state='AVAILABLE'
  AND impact.human_advice_read_scope(p.principal_id,m.object_id,c.context_plan_id)
  AND h.lifecycle_state='Active' AND (m.status IS NULL OR m.status='Active')
  AND (m.expires_at IS NULL OR m.expires_at>now())
  AND ((p.principal_id=c.requester_principal_id AND m.object_id=c.requester_membership_id AND i.natural_identity_id=c.requester_natural_id)
       OR (p.principal_id=c.adviser_principal_id AND m.object_id=c.adviser_membership_id AND i.natural_identity_id=c.adviser_natural_id
           AND c.case_state NOT IN ('Closed','Cancelled')
           AND (NOT material OR c.case_state IN ('Assigned','AwaitingInput','AdviceDraft'))))
 )
$$;
REVOKE ALL ON FUNCTION impact.human_advice_participant(uuid,boolean) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION impact.human_advice_participant(uuid,boolean) TO impact_app;

COMMIT;
