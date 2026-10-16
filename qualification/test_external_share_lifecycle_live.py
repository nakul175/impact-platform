"""Positive live journey for FR-ACC-006 / APL-353 external share lifecycle."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from test_administration import action, expect
from test_forms import temporary_grants
from test_permission_safe_derivatives_live import fresh_evidence


def _derivative(live):
    evidence = fresh_evidence(live)
    derivative_id, revision_id = str(uuid4()), str(uuid4())
    expect(
        live.request(
            live.path("derivatives", derivative_id) + "/revisions",
            method="POST",
            body={
                "revision_id": revision_id,
                "kind": "Analysis",
                "disclosure_mode": "PRIVATE",
                "sources": [
                    {
                        "object_id": evidence["object_id"],
                        "revision_id": evidence["revision_id"],
                        "object_type": "Evidence",
                        "capability": "evidence.manage",
                    }
                ],
            },
        ),
        200,
    )
    return derivative_id, revision_id


def _share(live, derivative_id, revision_id):
    return expect(
        live.request(
            live.path("external-shares"),
            method="POST",
            body={
                "derivative_id": derivative_id,
                "revision_id": revision_id,
                "audience_principal_id": live.fixture["actors"]["partner"]["principal_id"],
                "actions": ["read"],
                "reason": "Bounded synthetic recipient review",
                "expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            },
        ),
        200,
    )


def test_named_audience_revocation_expiry_and_source_revalidation(live):
    revoke = temporary_grants(live, "author", ["reports.write", "reports.share", "evidence.manage"])
    temporary_grants(live, "partner", ["evidence.manage"])
    derivative_id, revision_id = _derivative(live)
    share = _share(live, derivative_id, revision_id)
    path = live.path("external-shares", share["share_id"])

    expect(live.request(path, actor="reviewer"), 404)
    visible = expect(live.request(path, actor="partner"), 200)
    assert visible["actions"] == ["read"]
    assert visible["derivative"]["revision_id"] == revision_id

    expect(live.request(path + "/revocation", method="POST"), 200)
    expect(live.request(path, actor="partner"), 404)

    expired = _share(live, derivative_id, revision_id)
    with live.db() as c:
        c.execute(
            "UPDATE impact.external_share SET expires_at=now()-interval '1 second' WHERE tenant_id=%s AND share_id=%s",
            (live.fixture["tenant_a"], expired["share_id"]),
        )
    expect(live.request(live.path("external-shares", expired["share_id"]), actor="partner"), 404)

    revalidated = _share(live, derivative_id, revision_id)
    tenant = live.fixture["tenant_a"]
    principal = live.fixture["actors"]["partner"]["principal_id"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        grant = c.execute(
            "SELECT r.object_id,r.head_revision FROM impact.object_registry r "
            "JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
            "WHERE r.tenant_id=%s AND r.object_type='Grant' AND r.lifecycle_state='Active' "
            "AND v.payload->>'subject_id'=%s AND v.payload->>'capability'='evidence.manage' "
            "ORDER BY r.created_at DESC LIMIT 1",
            (tenant, principal),
        ).fetchone()
    expect(
        action(
            live,
            "grants",
            str(grant["object_id"]),
            "revoke",
            str(grant["head_revision"]),
            actor="admin",
        ),
        200,
    )
    expect(live.request(live.path("external-shares", revalidated["share_id"]), actor="partner"), 404)
    revoke()
