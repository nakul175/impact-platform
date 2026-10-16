"""Positive live journey for FR-ACC-006 / APL-353 external share lifecycle."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from test_administration import action, expect
from test_forms import temporary_grants


def _derivative(live):
    evidence = expect(live.request(live.path("evidence", live.records["evidence_a"]["object_id"])), 200)
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
                        "capability": "evidence.read",
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
    revoke = temporary_grants(live, "author", ["reports.write", "reports.share"])
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
    grant = live.records["grant:partner:evidence.read"]
    with live.db() as c:
        current_grant_revision = str(
            c.execute(
                "SELECT head_revision FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
                (live.fixture["tenant_a"], grant["object_id"]),
            ).fetchone()["head_revision"]
        )
    expect(
        action(
            live,
            "grants",
            grant["object_id"],
            "revoke",
            current_grant_revision,
            actor="admin",
        ),
        200,
    )
    expect(live.request(live.path("external-shares", revalidated["share_id"]), actor="partner"), 404)
    revoke()
