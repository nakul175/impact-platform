"""Natural-person independence checks shared by approval paths."""

from .domain import DomainError


def _person(ctx):
    person = getattr(ctx.identity, "natural_identity_id", None)
    if not person:
        raise DomainError("POLICY_DENIED", 403, reason="INDEPENDENCE_REQUIRED")
    return str(person)


def require_object_independence(c, ctx, object_id, error=None):
    """Reject every verified alias of every material author; roles and groups do not matter."""
    person = _person(ctx)
    authors = c.execute(
        "SELECT natural_identity_id FROM impact.object_natural_author WHERE tenant_id=%s AND object_id=%s",
        (ctx.tenant_id, str(object_id)),
    ).fetchall()
    if not authors or person in {str(row["natural_identity_id"]) for row in authors}:
        raise error or DomainError("POLICY_DENIED", 403, reason="INDEPENDENCE_REQUIRED")


def require_workflow_independence(c, ctx, workflow_id, candidate_revision):
    """Use the immutable candidate author snapshot; an unknown/service identity cannot approve."""
    person = _person(ctx)
    authors = c.execute(
        "SELECT natural_identity_id FROM impact.workflow_author WHERE tenant_id=%s AND workflow_id=%s AND candidate_revision=%s",
        (ctx.tenant_id, str(workflow_id), str(candidate_revision)),
    ).fetchall()
    if not authors or person in {str(row["natural_identity_id"]) for row in authors}:
        raise DomainError("POLICY_DENIED", 403, reason="INDEPENDENCE_REQUIRED")
