"""Positive live journey for FR-ACC-005 / APL-352 permission-safe derivatives."""

from uuid import uuid4

from test_administration import action, expect
from test_forms import temporary_grants


def test_b_exact_source_manifest_rechecks_current_authority(live):
    revoke_write = temporary_grants(live, "author", ["reports.write"])
    evidence = expect(live.request(live.path("evidence", live.records["evidence_a"]["object_id"])), 200)
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
                "capability": "evidence.read",
            }
        ],
    }
    try:
        created = expect(
            live.request(
                live.path("derivatives", derivative_id) + "/revisions",
                method="POST",
                body=body,
            ),
            200,
        )
    finally:
        revoke_write()
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

    grant = live.records["grant:author:evidence.read"]
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
    expect(live.request(path), 404)


def test_a_mixed_source_derivative_cannot_claim_public_disclosure(live):
    revoke_write = temporary_grants(live, "author", ["reports.write"])
    evidence = live.records["evidence_a"]
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
                            "capability": "evidence.read",
                        }
                    ],
                },
            ),
            400,
        )
    finally:
        revoke_write()
