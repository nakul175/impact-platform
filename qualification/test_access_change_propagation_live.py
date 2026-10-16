"""Positive live journey for FR-ACC-011 / APL-354 access-change propagation."""

from uuid import uuid4

from test_administration import action
from test_forms import temporary_grants
from test_live_application import expect
from test_permission_safe_derivatives_live import fresh_evidence


def _derivative(live, actor="author", source_capability="evidence.read"):
    evidence = fresh_evidence(live)
    derivative_id, revision_id = str(uuid4()), str(uuid4())
    created = expect(
        live.request(
            live.path("derivatives", derivative_id) + "/revisions",
            actor=actor,
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
                        "capability": source_capability,
                    }
                ],
            },
        ),
        200,
    )
    assert created["source_count"] == 1
    return derivative_id, revision_id


def _issue(live, derivative_id, revision_id, actor="author"):
    return expect(
        live.request(
            live.path("derivatives", derivative_id)
            + "/revisions/"
            + revision_id
            + "/presentation-leases",
            actor=actor,
            method="POST",
        ),
        200,
    )


def _revoke_temporary_grant_through_policy(live, capability):
    tenant = live.fixture["tenant_a"]
    principal = live.fixture["actors"]["author"]["principal_id"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        grant = c.execute(
            "SELECT r.object_id,r.head_revision FROM impact.object_registry r "
            "JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
            "WHERE r.tenant_id=%s AND r.object_type='Grant' AND r.lifecycle_state='Active' "
            "AND v.payload->>'subject_id'=%s AND v.payload->>'capability'=%s "
            "ORDER BY r.created_at DESC LIMIT 1",
            (tenant, principal, capability),
        ).fetchone()
    assert grant
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


def test_online_presentation_lease_is_bound_to_the_current_policy_epoch(live):
    revoke_write = temporary_grants(live, "author", ["reports.write", "evidence.read"])
    try:
        derivative_id, revision_id = _derivative(live)
        lease = _issue(live, derivative_id, revision_id)
        path = live.path("presentation-leases", lease["lease_id"])
        assert expect(live.request(path), 200) == {
            "lease_id": lease["lease_id"],
            "valid": True,
            "expires_at": lease["expires_at"],
        }
        assert lease["revalidate_after_seconds"] == 60

        temporary_grants(live, "author", ["forms.draft.create"])
        _revoke_temporary_grant_through_policy(live, "forms.draft.create")
        # An unrelated access-policy change advances the epoch. The still-readable
        # source cannot keep a presentation issued against the old epoch alive.
        expect(live.request(path), 404)
        source_path = live.path("derivatives", derivative_id) + "/revisions/" + revision_id
        expect(live.request(source_path), 200)
    finally:
        revoke_write()


def test_source_permission_loss_removes_the_derivative_and_its_live_presentation(live):
    revoke_write = temporary_grants(live, "author", ["reports.write"])
    temporary_grants(live, "author", ["evidence.manage"])
    derivative_id, revision_id = _derivative(live, source_capability="evidence.manage")
    lease = _issue(live, derivative_id, revision_id)
    path = live.path("presentation-leases", lease["lease_id"])
    expect(live.request(path), 200)

    _revoke_temporary_grant_through_policy(live, "evidence.manage")
    source_path = live.path("derivatives", derivative_id) + "/revisions/" + revision_id
    expect(live.request(source_path), 404)
    expect(live.request(path), 404)
    revoke_write()
