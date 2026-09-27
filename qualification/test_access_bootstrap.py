"""Initial authority review through live HTTP and actual database roles."""

import time
from uuid import uuid4
import psycopg
import pytest
from jsonschema import Draft202012Validator, FormatChecker
from test_administration import command, expect, expiry, signed, provision_identity
from test_tenant_lifecycle import active, action as tenant_action
from impact_api.bootstrap_contracts import DIRECTORY, RECEIPT

BASE = "/v1/platform/access-bootstraps"


def directory(live, actor="author"):
    result = expect(live.request(BASE, actor=actor), 200)
    Draft202012Validator(DIRECTORY, format_checker=FormatChecker()).validate(result)
    return result


def propose(live, tenant=None, status=200, **changes):
    tenant = tenant or active(live)
    body = command(
        {
            "second_identity_id": live.fixture["actors"]["reviewer"]["identity_id"],
            "profile_hash": directory(live)["profile_hash"],
            "role_names": ["PROGRAMME_MANAGER"],
            "expires_at": expiry(30),
            "reason": "Bounded initial access qualification",
            **changes,
        },
        tenant["revision_id"],
    )
    path = "/v1/platform/tenants/" + tenant["tenant_id"] + "/access-bootstrap"
    row = expect(live.request(path, method="POST", body=body), status)
    if status == 200:
        Draft202012Validator(RECEIPT, format_checker=FormatChecker()).validate(row)
    return row, tenant, path, body


def action(live, row, name, actor="reviewer", status=200, body=None):
    return expect(
        live.request(
            BASE + "/" + row["request_id"] + "/actions/" + name,
            actor=actor,
            method="POST",
            body=body or command({"reason": "Reviewed explicit authority"}, row["revision_id"]),
        ),
        status,
    )


def applied(live):
    row, tenant, _, _ = propose(live)
    row = action(live, row, "accept")
    return action(live, row, "approve", "admin"), tenant


def test_onboarding_to_first_programme_requires_two_reviews(live):
    row, tenant, _, _ = propose(live)

    def path(route):
        return live.path(route, tenant=tenant["tenant_id"])

    expect(live.request(path("programmes")), 403)
    action(live, row, "approve", "admin", status=409)
    accepted = action(live, row, "accept")
    expect(live.request(path("me/access"), actor="reviewer"), 404)
    approved = action(live, accepted, "approve", "admin")
    Draft202012Validator(RECEIPT, format_checker=FormatChecker()).validate(approved)
    for actor in ["author", "reviewer"]:
        expect(live.request(path("programmes"), actor=actor), 403)
        expect(live.request(path("membership-directory"), actor=actor), 200)
    expect(live.request(path("me/access"), actor="admin"), 404)
    roles = expect(live.request(path("role-templates"), actor="reviewer"), 200)["items"]
    assert {r["name"] for r in roles} == {"TENANT_ADMIN", "PROGRAMME_MANAGER"}
    role = next(r for r in roles if r["name"] == "PROGRAMME_MANAGER")
    members = expect(live.request(path("membership-directory"), actor="reviewer"), 200)["items"]
    member = next(m for m in members if m["object_id"] == approved["second_membership_id"])
    request = expect(
        live.request(
            path("access-requests"),
            actor="reviewer",
            method="POST",
            body=command(
                {
                    "membership_id": member["object_id"],
                    "expected_membership_revision": member["revision_id"],
                    "role_template_id": role["object_id"],
                    "scope_ids": [approved["scope_id"]],
                    "expires_at": expiry(20),
                    "reason": "First programme access",
                }
            ),
        ),
        200,
    )
    review_path = path("access-requests") + "/" + request["object_id"] + "/actions/approve"
    approval = command({"reason": "Reviewed business scope"}, request["revision_id"])
    expect(live.request(review_path, actor="reviewer", method="POST", body=approval), 403)
    expect(live.request(review_path, actor="author", method="POST", body=approval), 200)
    result = expect(
        live.request(
            path("programmes"),
            actor="reviewer",
            method="POST",
            body=command({"code": "FIRST", "title": "First reviewed programme"}),
        ),
        201,
    )
    assert result["business_state"] == "Draft"
    assert len(expect(live.request(path("programmes"), actor="reviewer"), 200)["items"]) == 1
    expect(live.request(path("programmes"), actor="author"), 403)
    with live.db() as c:
        authorities = c.execute(
            "SELECT capability,expires_at FROM impact.grant_authority WHERE tenant_id=%s",
            (tenant["tenant_id"],),
        ).fetchall()
        assert {r["capability"] for r in authorities} == set().union(
            *map(set, row["manifest"]["roles"].values())
        )
        assert len(authorities) == 2 * len({r["capability"] for r in authorities})


def test_request_is_owner_only_and_unknown_fields_are_closed(live):
    _, _, path, body = propose(live)
    for actor in ["admin", "reviewer", "owner", "other_tenant"]:
        expect(live.request(path, actor=actor, method="POST", body=body), 404)
    expect(live.request(path, method="POST", body={**body, "capabilities": ["*"]}), 422)


@pytest.mark.parametrize(
    "changes,status",
    [
        ({"expires_at": expiry(100)}, 422),
        ({"expires_at": expiry(-1)}, 422),
        ({"role_names": ["OWNER"]}, 422),
        ({"role_names": []}, 422),
        ({"role_names": ["AUTHOR", "AUTHOR"]}, 422),
        ({"profile_hash": "0" * 64}, 409),
        ({"second_identity_id": str(uuid4())}, 404),
    ],
)
def test_invalid_initial_authority_packages(live, changes, status):
    propose(live, status=status, **changes)


def test_same_natural_person_cannot_be_second_admin(live):
    identity, _ = provision_identity(live, live.fixture["actors"]["author"]["natural_identity_id"])
    propose(live, status=403, second_identity_id=identity)


def test_approval_independence_applies_across_identity_aliases(live):
    row, _, _, _ = propose(live, second_identity_id=live.fixture["actors"]["admin"]["identity_id"])
    row = action(live, row, "accept", "admin")
    action(live, row, "approve", "admin", status=403)
    action(live, row, "approve", "owner")


def test_private_inbox_nominee_binding_and_fresh_assurance(live):
    row, _, _, _ = propose(live)
    assert row["request_id"] in {r["request_id"] for r in directory(live, "reviewer")["items"]}
    assert row["request_id"] not in {r["request_id"] for r in directory(live, "other_tenant")["items"]}
    for actor in ["author", "admin", "other_tenant"]:
        action(live, row, "accept", actor, status=404)
    token = signed(live, live.fixture["actors"]["reviewer"]["identity_id"], auth_time=time.time() - 600)
    expect(
        live.request(
            BASE + "/" + row["request_id"] + "/actions/accept",
            actor=None,
            headers={"Authorization": "Bearer " + token},
            method="POST",
            body=command({"reason": "Stale assurance"}, row["revision_id"]),
        ),
        403,
    )


def test_idempotent_once_only_and_replay_cannot_restore_revoked_grants(live):
    row, tenant, path, body = propose(live)
    assert expect(live.request(path, method="POST", body=body), 200) == row
    expect(
        live.request(path, method="POST", body={**body, "data": {**body["data"], "reason": "Different"}}), 409
    )
    propose(live, tenant, status=409)
    row = action(live, row, "accept")
    approve = command({"reason": "Final review"}, row["revision_id"])
    result = action(live, row, "approve", "admin", body=approve)
    with live.db() as c:
        c.execute(
            "UPDATE impact.object_registry SET lifecycle_state='Revoked' WHERE tenant_id=%s AND object_type='Grant'",
            (tenant["tenant_id"],),
        )
    assert action(live, row, "approve", "admin", body=approve) == result
    propose(live, tenant, status=403)
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.tenant_access_bootstrap_applied WHERE tenant_id=%s",
                (tenant["tenant_id"],),
            ).fetchone()["n"]
            == 1
        )
        assert not c.execute(
            "SELECT 1 FROM impact.object_registry WHERE tenant_id=%s AND object_type='Grant' AND lifecycle_state='Active'",
            (tenant["tenant_id"],),
        ).fetchone()


@pytest.mark.parametrize(
    "drift,status",
    [
        ("tenant", 409),
        ("owner", 409),
        ("expired", 403),
        ("profile", 409),
        ("qualification", 403),
        ("owner_cutoff", 403),
        ("second_cutoff", 403),
    ],
)
def test_approval_rechecks_pinned_context_and_consent(live, drift, status):
    row, tenant, _, _ = propose(live)
    row = action(live, row, "accept")
    with live.db() as c:
        if drift == "tenant":
            c.execute(
                "UPDATE impact.tenant_onboarding SET revision_id=%s WHERE tenant_id=%s",
                (str(uuid4()), tenant["tenant_id"]),
            )
        elif drift == "owner":
            # Pin drift without touching immutable revision payloads.
            c.execute(
                "UPDATE impact.tenant_access_bootstrap SET owner_revision=%s WHERE request_id=%s",
                (str(uuid4()), row["request_id"]),
            )
        elif drift == "expired":
            c.execute(
                "UPDATE impact.tenant_access_bootstrap SET review_expires_at=now()-interval '1 second' WHERE request_id=%s",
                (row["request_id"],),
            )
        elif drift == "profile":
            c.execute(
                "UPDATE impact.tenant_access_bootstrap SET profile_hash=%s WHERE request_id=%s",
                ("0" * 64, row["request_id"]),
            )
        elif drift == "qualification":
            c.execute(
                "UPDATE impact.tenant_onboarding SET qualification_revision=%s WHERE tenant_id=%s",
                (str(uuid4()), tenant["tenant_id"]),
            )
        else:
            key = "owner_auth_time" if drift == "owner_cutoff" else "second_auth_time"
            # Set only this request's consent below an existing synthetic identity cutoff.
            person = row["owner_identity_id"] if drift == "owner_cutoff" else row["second_identity_id"]
            c.execute(
                "INSERT INTO impact.identity_security_state VALUES(%s,now()-interval '1 day') ON CONFLICT(identity_id) DO NOTHING",
                (person,),
            )
            c.execute(
                "UPDATE impact.tenant_access_bootstrap SET "
                + key
                + "=now()-interval '2 days' WHERE request_id=%s",
                (row["request_id"],),
            )
    action(live, row, "approve", "admin", status=status)
    with live.db() as c:
        assert not c.execute(
            "SELECT 1 FROM impact.grant_current WHERE tenant_id=%s", (tenant["tenant_id"],)
        ).fetchone()


def test_suspension_blocks_acceptance_and_cancellation_allows_fresh_proposal(live):
    row, tenant, _, _ = propose(live)
    tenant_action(live, tenant, "suspend", "admin")
    action(live, row, "accept", status=403)
    action(live, row, "cancel", "author", status=403)
    rejected = action(live, row, "reject", "admin")
    assert rejected["state"] == "Rejected"
    row, tenant, _, _ = propose(live)
    action(live, row, "cancel", "author")
    assert propose(live, tenant)[0]["state"] == "Requested"


def test_revoked_operator_cannot_replay_approval(live):
    row, _, _, _ = propose(live)
    row = action(live, row, "accept")
    body = command({"reason": "Approved"}, row["revision_id"])
    action(live, row, "approve", "admin", body=body)
    identity = live.fixture["actors"]["admin"]["identity_id"]
    try:
        with live.db() as c:
            c.execute("UPDATE impact.platform_operator SET active=false WHERE identity_id=%s", (identity,))
        action(live, row, "approve", "admin", status=404, body=body)
    finally:
        with live.db() as c:
            c.execute("UPDATE impact.platform_operator SET active=true WHERE identity_id=%s", (identity,))


def test_runtime_cannot_manufacture_delegation_or_reset_marker(live):
    for role, query in [
        ("impact_app", "SELECT * FROM impact.tenant_access_bootstrap"),
        ("impact_app", "SELECT impact.apply_initial_authority(gen_random_uuid())"),
        ("impact_platform", "DELETE FROM impact.tenant_access_bootstrap_applied"),
        ("impact_platform", "INSERT INTO impact.grant_authority VALUES(NULL,NULL,NULL,NULL,NULL,NULL)"),
        ("impact_platform", "SELECT impact.apply_initial_authority(gen_random_uuid())"),
    ]:
        with live.db() as c:
            c.execute("SET LOCAL ROLE " + role)
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                c.execute(query)


def test_unselected_capabilities_and_longer_grants_exceed_delegation_ceiling(live):
    row, tenant = applied(live)

    def path(route):
        return live.path(route, tenant=tenant["tenant_id"])

    for actor in ["author", "reviewer"]:
        expect(
            live.request(
                path("role-templates"),
                actor=actor,
                method="POST",
                body=command(
                    {
                        "name": "Outside reviewed ceiling",
                        "capabilities": ["observations.draft.create"],
                        "reason": "Must be refused",
                    }
                ),
            ),
            403,
        )
    role = next(
        r
        for r in expect(live.request(path("role-templates")), 200)["items"]
        if r["name"] == "PROGRAMME_MANAGER"
    )
    member = next(
        m
        for m in expect(live.request(path("membership-directory")), 200)["items"]
        if m["object_id"] == row["second_membership_id"]
    )
    expect(
        live.request(
            path("access-requests"),
            actor="reviewer",
            method="POST",
            body=command(
                {
                    "membership_id": member["object_id"],
                    "expected_membership_revision": member["revision_id"],
                    "role_template_id": role["object_id"],
                    "scope_ids": [row["scope_id"]],
                    "expires_at": expiry(40),
                    "reason": "Beyond reviewed expiry",
                }
            ),
        ),
        403,
    )


def test_failure_after_provisioning_rolls_back_all_access_and_receipt(live):
    row, tenant, _, _ = propose(live)
    row = action(live, row, "accept")
    body = command({"reason": "Atomic approval"}, row["revision_id"])
    with live.db() as c:
        c.execute(
            "CREATE FUNCTION impact.test_reject_bootstrap_event() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.action='initial-access-approve' THEN RAISE EXCEPTION 'qualification injected failure'; END IF; RETURN NEW; END $$"
        )
        c.execute(
            "CREATE TRIGGER test_reject_bootstrap_event BEFORE INSERT ON impact.platform_event FOR EACH ROW EXECUTE FUNCTION impact.test_reject_bootstrap_event()"
        )
    try:
        action(live, row, "approve", "admin", status=503, body=body)
        with live.db() as c:
            for table in [
                "grant_current",
                "grant_authority",
                "tenant_access_bootstrap_applied",
                "scope_definition",
                "member_role_assignment",
            ]:
                assert not c.execute(
                    "SELECT 1 FROM impact." + table + " WHERE tenant_id=%s", (tenant["tenant_id"],)
                ).fetchone()
            assert (
                c.execute(
                    "SELECT count(*) AS n FROM impact.membership_current WHERE tenant_id=%s",
                    (tenant["tenant_id"],),
                ).fetchone()["n"]
                == 1
            )
            assert not c.execute(
                "SELECT 1 FROM impact.platform_receipt WHERE operation_id=%s", (body["operation_id"],)
            ).fetchone()
    finally:
        with live.db() as c:
            c.execute("DROP TRIGGER test_reject_bootstrap_event ON impact.platform_event")
            c.execute("DROP FUNCTION impact.test_reject_bootstrap_event()")
    assert action(live, row, "approve", "admin", body=body)["state"] == "Applied"
