"""Shared checks for identity-bound control-plane workflows."""

from .domain import DomainError, unavailable


def registered_person(c, identity, issuer):
    row = c.execute(
        "SELECT i.*,p.display_name,p.email_mask,p.verified_email_hash,s.auth_not_before FROM impact.auth_identity i JOIN impact.identity_profile p USING(identity_id) LEFT JOIN impact.identity_security_state s USING(identity_id) WHERE identity_id=%s",
        (identity,),
    ).fetchone()
    if not row or row["issuer"] != issuer or not row["verified_email_hash"]:
        unavailable()
    return row


def current_owner(c, tenant):
    row = c.execute(
        "SELECT r.head_revision,p.principal_id,p.auth_not_before FROM impact.membership_current m JOIN impact.object_registry r ON r.tenant_id=m.tenant_id AND r.object_id=m.object_id JOIN impact.tenant_principal p ON p.tenant_id=m.tenant_id AND p.identity_id=m.identity_id JOIN impact.tenant_custody t ON t.tenant_id=m.tenant_id AND t.owner_membership_id=m.object_id WHERE m.tenant_id=%s AND m.object_id=%s AND m.identity_id=%s AND p.active AND r.lifecycle_state='Active' AND (m.expires_at IS NULL OR m.expires_at>now())",
        (tenant["tenant_id"], tenant["owner_membership_id"], tenant["owner_identity_id"]),
    ).fetchone()
    if not row:
        raise DomainError("POLICY_DENIED", 403, reason="OWNER_UNAVAILABLE")
    return row
