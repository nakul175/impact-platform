"""Positive live journey for FR-ACC-005 / APL-352 permission-safe derivatives."""

from types import SimpleNamespace
from uuid import uuid4

from impact_api.store import Context, write
from test_administration import action, expect
from test_forms import temporary_grants


def fresh_evidence(live, owner="reviewer"):
    """Create a test-owned source so revoking its grant cannot damage the shared fixture."""
    tenant = live.fixture["tenant_a"]
    actor = live.fixture["actors"][owner]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        source = c.execute(
            "SELECT r.lifecycle_state,v.payload FROM impact.object_registry r "
            "JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
            "WHERE r.tenant_id=%s AND r.object_id=%s",
            (tenant, live.records["evidence_a"]["object_id"]),
        ).fetchone()
        ctx = Context(
            tenant,
            actor["principal_id"],
            actor["membership_id"],
            SimpleNamespace(natural_identity_id=actor["natural_identity_id"]),
            0,
            0,
            [],
        )
        return write(c, ctx, "Evidence", source["payload"], source["lifecycle_state"])


def test_b_exact_source_manifest_rechecks_current_authority(live):
    revoke_write = temporary_grants(live, "author", ["reports.write"])
    temporary_grants(live, "author", ["evidence.manage"])
    evidence = fresh_evidence(live)
    derivative_id, derivative_revision = str(uuid4()), str(uuid4())
    body = {
        "revision_id": derivative_revision,
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
    }
    created = expect(
        live.request(
            live.path("derivatives", derivative_id) + "/revisions",
            method="POST",
            body=body,
        ),
        200,
    )
    assert created == {
        "derivative_id": derivative_id,
        "revision_id": derivative_revision,
        "kind": "Analysis",
        "disclosure_mode": "PRIVATE",
        "source_count": 1,
    }

    path = live.path("derivatives", derivative_id) + "/revisions/" + derivative_revision
    current = expect(live.request(path), 200)
    assert current["sources"] == [
        {
            "object_id": evidence["object_id"],
            "revision_id": evidence["revision_id"],
            "object_type": "Evidence",
        }
    ]

    cross_tenant = expect(
        live.request(
            live.path("derivatives", derivative_id, tenant=live.fixture["tenant_b"])
            + "/revisions/"
            + derivative_revision,
            actor="other_tenant",
        ),
        404,
    )
    assert cross_tenant["code"] == "RESOURCE_UNAVAILABLE"

    tenant = live.fixture["tenant_a"]
    principal = live.fixture["actors"]["author"]["principal_id"]
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
    expect(live.request(path), 404)
    restore_source = temporary_grants(live, "author", ["evidence.manage"])
    try:
        assert expect(live.request(path), 200) == current
    finally:
        restore_source()
    # The reports grant remains test-owned and is cleaned up normally. The source grant was
    # deliberately revoked through policy above.
    revoke_write()


def test_a_mixed_source_derivative_cannot_claim_public_disclosure(live):
    revoke_write = temporary_grants(live, "author", ["reports.write", "evidence.manage"])
    evidence = fresh_evidence(live)
    try:
        expect(
            live.request(
                live.path("derivatives", str(uuid4())) + "/revisions",
                method="POST",
                body={
                    "revision_id": str(uuid4()),
                    "kind": "Analysis",
                    "disclosure_mode": "APPROVED_AGGREGATE",
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
            400,
        )
    finally:
        revoke_write()


def test_c_external_member_cannot_create_derivative_manifest(live):
    evidence = fresh_evidence(live)
    denied = expect(
        live.request(
            live.path("derivatives", str(uuid4())) + "/revisions",
            actor="partner",
            method="POST",
            body={
                "revision_id": str(uuid4()),
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
        403,
    )
    assert denied["code"] == "POLICY_DENIED"
