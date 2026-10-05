"""Three-party ceiling widening through real HTTP and actual database role fences."""

import time
import json
import os
import base64
from copy import deepcopy
from types import SimpleNamespace
from uuid import uuid4

import psycopg
import pytest
from jsonschema import Draft202012Validator, FormatChecker
from psycopg.types.json import Jsonb

from impact_api.access_upgrade_contracts import DIRECTORY, PREVIEW, RECEIPT
from impact_api.access_bootstrap import PROFILE, PROFILE_HASH
from test_access_upgrade_unit import migration_profile_seeds
from impact_api.auth import Identity
from impact_api.store import Context, load, write, hash_data
from impact_api.tenant_lifecycle import now
from impact_api.config import Settings
from impact_api.service import Service
from test_access_bootstrap import applied as bootstrapped
from test_administration import command, expect, provision_identity, request_as
from test_authority_renewal import propose as propose_renewal, snapshot


def valid(schema, value):
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)
    return value


def base(tenant):
    return "/v1/platform/tenants/" + tenant["tenant_id"]


def preview(live, tenant, actor="author", status=200):
    response = expect(live.request(base(tenant) + "/access-upgrade-preview", actor=actor), status)
    return valid(PREVIEW, response) if status == 200 else response


def propose(live, tenant=None, status=200, revision=None, **changes):
    tenant = tenant or bootstrapped(live)[1]
    current = preview(live, tenant)
    request = command(
        {
            "second_identity_id": current["second_identity_id"],
            "authority_hash": current["authority_hash"],
            "profile_hash": current["profile_hash"],
            "reason": "Review the additional platform capabilities",
            **changes,
        },
        revision or current["tenant_revision"],
    )
    path = base(tenant) + "/access-upgrade"
    row = expect(live.request(path, method="POST", body=request), status)
    return (valid(RECEIPT, row) if status == 200 else row), tenant, request


def action(live, row, name, actor="reviewer", status=200, body=None):
    path = base(row) + "/access-upgrades/" + row["request_id"] + "/actions/" + name
    response = expect(
        live.request(
            path,
            actor=actor,
            method="POST",
            body=body or command({"reason": "Explicit independent review"}, row["revision_id"]),
        ),
        status,
    )
    return valid(RECEIPT, response) if status == 200 else response


def listing(live, actor="author", tenant=None):
    path = base(tenant) + "/access-upgrades" if tenant else "/v1/platform/access-upgrades"
    return valid(DIRECTORY, expect(live.request(path, actor=actor), 200))


def test_owner_second_admin_operator_review_adds_only_new_authority_and_keeps_expiry(live):
    row, tenant, request = propose(live)
    assert row["state"] == "Requested" and row["new_capabilities"]
    before = snapshot(live, tenant["tenant_id"])
    assert preview(live, tenant)["reason_unavailable"] == "ACCESS_UPGRADE_PENDING"
    action(live, row, "approve", "admin", status=409)
    accepted = action(live, row, "accept")
    assert accepted["accepted_at"] and not accepted["applied_at"]
    assert snapshot(live, tenant["tenant_id"]) == before
    approved = action(live, accepted, "approve", "admin")
    assert (
        approved["state"] == "Applied"
        and approved["approved_by"] == live.fixture["actors"]["admin"]["identity_id"]
    )
    after = snapshot(live, tenant["tenant_id"])
    assert set(before["authority"]) < set(after["authority"])
    assert all(after["authority"][key] == value for key, value in before["authority"].items())
    assert set(after["authority"].values()) == set(before["authority"].values())
    assert after["memberships"] == before["memberships"] and after["marker"] == before["marker"]
    assert all(after["grants"][key] == value for key, value in before["grants"].items())
    assert after["policy_epoch"] == before["policy_epoch"] + 1
    assert preview(live, tenant)["reason_unavailable"] == "ACCESS_PROFILE_ALREADY_HELD"
    assert expect(live.request(base(tenant) + "/access-upgrade", method="POST", body=request), 200) == row
    with live.db() as c:
        marker = c.execute(
            "SELECT authorities_added FROM impact.tenant_access_upgrade_applied WHERE tenant_id=%s AND request_id=%s",
            (tenant["tenant_id"], row["request_id"]),
        ).fetchone()
        assert marker["authorities_added"] == len(after["authority"]) - len(before["authority"])
        events = c.execute(
            "SELECT action FROM impact.platform_event WHERE tenant_id=%s AND action LIKE 'access-upgrade-%%' ORDER BY created_at",
            (tenant["tenant_id"],),
        ).fetchall()
        assert [r["action"] for r in events] == [
            "access-upgrade-request",
            "access-upgrade-accept",
            "access-upgrade-approve",
        ]


def test_private_global_inbox_makes_named_second_review_reachable_and_hides_others(live):
    row, tenant, _ = propose(live)
    for actor in ["author", "reviewer", "admin"]:
        assert row["request_id"] in {item["request_id"] for item in listing(live, actor)["items"]}
        assert row["request_id"] in {item["request_id"] for item in listing(live, actor, tenant)["items"]}
    for actor in ["other_tenant", "partner", "enumerator"]:
        assert row["request_id"] not in {item["request_id"] for item in listing(live, actor)["items"]}
        preview(live, tenant, actor, 404)
        expect(live.request(base(tenant) + "/access-upgrades", actor=actor), 404)
        action(live, row, "accept", actor, status=404)
    for actor in ["admin", "reviewer", "other_tenant"]:
        expect(
            live.request(
                base(tenant) + "/access-upgrade",
                actor=actor,
                method="POST",
                body=command(
                    {
                        "second_identity_id": row["second_identity_id"],
                        "authority_hash": row["authority_hash"],
                        "profile_hash": row["profile_hash"],
                        "reason": "Cannot request as somebody else",
                    },
                    tenant["revision_id"],
                ),
            ),
            404,
        )


def test_a_historical_second_nomination_stops_exposing_rows_after_membership_ends(live):
    row, tenant, _ = propose(live)
    assert row["request_id"] in {item["request_id"] for item in listing(live, "reviewer")["items"]}
    with live.db() as c:
        c.execute(
            "UPDATE impact.object_registry SET lifecycle_state='Removed' WHERE tenant_id=%s AND object_id=%s",
            (tenant["tenant_id"], row["current_manifest"]["principals"][1]["membership_id"]),
        )
    assert row["request_id"] not in {item["request_id"] for item in listing(live, "reviewer")["items"]}
    preview(live, tenant, "reviewer", 404)
    expect(live.request(base(tenant) + "/access-upgrades", actor="reviewer"), 404)


def maintenance_context(live, c, tenant_id):
    """Owner-run synthetic fixture adaptation; it is never a runtime permission shortcut."""
    c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_id,))
    actor = live.fixture["actors"]["author"]
    person = Identity(actor["identity_id"], actor["natural_identity_id"], actor["identity_id"], now())
    principal = c.execute(
        "SELECT principal_id FROM impact.tenant_principal WHERE tenant_id=%s AND identity_id=%s",
        (tenant_id, actor["identity_id"]),
    ).fetchone()["principal_id"]
    return Context(tenant_id, str(principal), "", person, 0, 0, [])


def test_managed_role_omissions_and_revoked_access_before_proposal_are_preserved(live):
    _, tenant = bootstrapped(live)
    tenant_id = tenant["tenant_id"]
    with live.db() as c:
        ctx = maintenance_context(live, c, tenant_id)
        role_id = c.execute(
            "SELECT r.object_id FROM impact.object_registry r JOIN impact.object_revision v "
            "ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.tenant_id=%s "
            "AND r.object_type='RoleTemplate' AND v.payload->>'name'='TENANT_ADMIN'",
            (tenant_id,),
        ).fetchone()["object_id"]
        previous = load(c, ctx, str(role_id), "RoleTemplate")
        omitted = "ai.enablement.read"
        payload = {
            **previous["payload"],
            "capabilities": [cap for cap in previous["payload"]["capabilities"] if cap != omitted],
        }
        write(c, ctx, "RoleTemplate", payload, "Active", previous, track_author=False)
        c.execute(
            "UPDATE impact.object_registry r SET lifecycle_state='Revoked' FROM impact.grant_current g "
            "WHERE g.tenant_id=r.tenant_id AND g.object_id=r.object_id AND g.tenant_id=%s AND g.capability=%s",
            (tenant_id, omitted),
        )
    expect(live.request(live.path("ai-enablement/catalog", tenant=tenant_id), actor="reviewer"), 404)
    row, _, _ = propose(live, tenant)
    assert action(live, action(live, row, "accept"), "approve", "admin")["state"] == "Applied"
    expect(live.request(live.path("ai-enablement/catalog", tenant=tenant_id), actor="reviewer"), 404)
    with live.db() as c:
        ctx = maintenance_context(live, c, tenant_id)
        assert omitted not in load(c, ctx, str(role_id), "RoleTemplate")["payload"]["capabilities"]


def test_explicit_synthetic_pre_ai_profile_fixture_receives_new_ai_access_after_three_party_review(live):
    """The fixture models a historical profile, without changing old migrations or real tenants."""
    access, tenant = bootstrapped(live)
    tenant_id = tenant["tenant_id"]
    old = deepcopy(access["manifest"])
    old["version"] = "synthetic-pre-ai-profile"
    for name, caps in old["roles"].items():
        old["roles"][name] = [cap for cap in caps if not cap.startswith("ai.")]
    with live.db() as c:
        ctx = maintenance_context(live, c, tenant_id)
        c.execute(
            "UPDATE impact.tenant_access_bootstrap SET manifest=%s WHERE tenant_id=%s AND request_id=%s",
            (Jsonb(old), tenant_id, access["request_id"]),
        )
        c.execute(
            "DELETE FROM impact.grant_authority WHERE tenant_id=%s AND capability LIKE 'ai.%%'", (tenant_id,)
        )
        c.execute(
            "UPDATE impact.object_registry r SET lifecycle_state='Revoked' FROM impact.grant_current g "
            "WHERE g.tenant_id=r.tenant_id AND g.object_id=r.object_id AND g.tenant_id=%s AND g.capability LIKE 'ai.%%'",
            (tenant_id,),
        )
        roles = c.execute(
            "SELECT r.object_id FROM impact.object_registry r JOIN impact.object_revision v "
            "ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.tenant_id=%s "
            "AND r.object_type='RoleTemplate' AND v.payload->>'managed_by'='impact-access-v1'",
            (tenant_id,),
        ).fetchall()
        for item in roles:
            previous = load(c, ctx, str(item["object_id"]), "RoleTemplate")
            payload = {
                **previous["payload"],
                "capabilities": [
                    cap for cap in previous["payload"]["capabilities"] if not cap.startswith("ai.")
                ],
            }
            write(c, ctx, "RoleTemplate", payload, "Active", previous, track_author=False)
    expect(live.request(live.path("ai-enablement/catalog", tenant=tenant_id), actor="reviewer"), 404)
    row, _, _ = propose(live, tenant)
    assert {"ai.enablement.read", "ai.enablement.manage", "ai.advisory.request"} <= set(
        row["new_capabilities"]
    )
    before = snapshot(live, tenant_id)
    assert action(live, action(live, row, "accept"), "approve", "admin")["state"] == "Applied"
    after = snapshot(live, tenant_id)
    assert all(after["authority"][key] == value for key, value in before["authority"].items())
    expect(live.request(live.path("ai-enablement/catalog", tenant=tenant_id), actor="reviewer"), 200)


def test_registered_profile_is_exact_and_platform_role_cannot_write_registry(live):
    seeds = migration_profile_seeds()
    with live.db() as c:
        rows = c.execute(
            "SELECT profile_hash,manifest,source_migration FROM impact.platform_access_profile "
            "WHERE profile_hash=ANY(%s::varchar[]) ORDER BY source_migration",
            ([seed["profile_hash"] for seed in seeds],),
        ).fetchall()
        assert len(rows) == len(seeds)
        actual = {row["profile_hash"]: row for row in rows}
        assert all(actual[seed["profile_hash"]] == seed for seed in seeds)
        row = actual[PROFILE_HASH]
        assert row["manifest"] == PROFILE

    for action_sql in [
        "INSERT INTO impact.platform_access_profile DEFAULT VALUES",
        "UPDATE impact.platform_access_profile SET manifest='{}'",
        "DELETE FROM impact.platform_access_profile",
    ]:
        with live.db() as c:
            c.execute("SET LOCAL ROLE impact_platform")
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                c.execute(action_sql)


def test_custom_role_name_collision_is_reported_without_rewriting_custom_access(live):
    _, tenant = bootstrapped(live)
    role = expect(
        live.request(
            live.path("role-templates", tenant=tenant["tenant_id"]),
            method="POST",
            body=command(
                {
                    "name": "analyst",
                    "capabilities": ["roles.manage"],
                    "reason": "Synthetic custom role collision",
                }
            ),
        ),
        200,
    )
    described = preview(live, tenant)
    assert not described["upgradable"] and described["reason_unavailable"] == "ACCESS_PROFILE_ROLE_CONFLICT"
    assert propose(live, tenant, status=403)[0]["reason_code"] == "ACCESS_PROFILE_ROLE_CONFLICT"
    with live.db() as c:
        ctx = maintenance_context(live, c, tenant["tenant_id"])
        assert load(c, ctx, role["object_id"], "RoleTemplate")["payload"]["capabilities"] == ["roles.manage"]


@pytest.mark.parametrize("native", [False, True])
@pytest.mark.parametrize("restriction", ["role_bundle", "purpose_bound"])
def test_direct_platform_cannot_reset_baseline_to_a_registered_but_narrower_profile(
    live, native, restriction
):
    dsn = os.environ.get("IMPACT_LOGIN_DSN_PLATFORM") if native else None
    if native and not dsn:
        pytest.skip("Native provisioned platform login required; SET ROLE has separate bounded evidence")
    row, tenant, _ = propose(live)
    narrower = deepcopy(row["target_manifest"])
    if restriction == "role_bundle":
        narrower["roles"]["TENANT_ADMIN"].remove("roles.manage")
        narrower["roles"]["AUTHOR"].append("roles.manage")
    else:
        narrower["purpose_bound"].remove("audit.export")
        narrower["roles"]["TENANT_ADMIN"].append("audit.export")
    narrow_hash = hash_data(narrower).hex()
    with live.db() as c:
        # An additional immutable registry entry models a future migration;
        # neither existing profiles nor applied records are rewritten.
        c.execute(
            "INSERT INTO impact.platform_access_profile(profile_hash,manifest,source_migration) VALUES(%s,%s,'synthetic-registry-qualification') ON CONFLICT DO NOTHING",
            (narrow_hash, Jsonb(narrower)),
        )
        c.execute("ALTER TABLE impact.tenant_access_upgrade DISABLE TRIGGER access_upgrade_guard")
        c.execute(
            "UPDATE impact.tenant_access_upgrade SET state='Accepted',accepted_at=now(),second_auth_time=now(),profile_hash=%s,target_manifest=%s WHERE tenant_id=%s AND request_id=%s",
            (narrow_hash, Jsonb(narrower), tenant["tenant_id"], row["request_id"]),
        )
        c.execute("ALTER TABLE impact.tenant_access_upgrade ENABLE TRIGGER access_upgrade_guard")
    before = snapshot(live, tenant["tenant_id"])
    connection = psycopg.connect(dsn, prepare_threshold=None) if native else live.db()
    with connection as c:
        # Provisioned native logins are deliberately NOINHERIT: activate the
        # same bounded runtime role used by Database.transaction().
        c.execute("SET LOCAL ROLE impact_platform")
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant["tenant_id"],))
        with pytest.raises(psycopg.errors.InsufficientPrivilege, match="profile not monotonic"):
            c.execute(
                "SELECT impact.apply_access_upgrade(%s,%s,%s,now())",
                (tenant["tenant_id"], row["request_id"], live.fixture["actors"]["admin"]["identity_id"]),
            )
    assert snapshot(live, tenant["tenant_id"]) == before


@pytest.mark.parametrize("native", [False, True])
def test_direct_platform_proposal_cannot_apply_a_forged_unregistered_target(live, native):
    dsn = os.environ.get("IMPACT_LOGIN_DSN_PLATFORM") if native else None
    if native and not dsn:
        pytest.skip("Native provisioned platform login is required; PGlite SET ROLE is separate evidence")
    row, tenant, _ = propose(live)
    # The owner-run fixture records a forged review for the database boundary
    # check. The HTTP API rejects this shape; no consent rule is weakened.
    forged = deepcopy(row["target_manifest"])
    forged["roles"]["TENANT_ADMIN"].append("unregistered.security-bypass")
    with live.db() as c:
        c.execute("ALTER TABLE impact.tenant_access_upgrade DISABLE TRIGGER access_upgrade_guard")
        c.execute(
            "UPDATE impact.tenant_access_upgrade SET state='Accepted',accepted_at=now(),second_auth_time=now(),target_manifest=%s WHERE tenant_id=%s AND request_id=%s",
            (Jsonb(forged), tenant["tenant_id"], row["request_id"]),
        )
        c.execute("ALTER TABLE impact.tenant_access_upgrade ENABLE TRIGGER access_upgrade_guard")
    before = snapshot(live, tenant["tenant_id"])
    connection = psycopg.connect(dsn, prepare_threshold=None) if native else live.db()
    with connection as c:
        c.execute("SET LOCAL ROLE impact_platform")
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant["tenant_id"],))
        with pytest.raises(psycopg.errors.InsufficientPrivilege, match="access upgrade denied"):
            c.execute(
                "SELECT impact.apply_access_upgrade(%s,%s,%s,now())",
                (tenant["tenant_id"], row["request_id"], live.fixture["actors"]["admin"]["identity_id"]),
            )
    assert snapshot(live, tenant["tenant_id"]) == before


@pytest.mark.parametrize("kind", ["top", "nested", "duplicate"])
def test_closed_dtos_duplicate_json_and_server_owned_fields_fail_closed(live, kind):
    _, tenant, body = propose(live)
    if kind == "duplicate":
        import json

        raw = json.dumps(body).replace('"reason":', '"reason":"First reason","reason":')
        response = live.client.post(
            base(tenant) + "/access-upgrade",
            content=raw,
            headers={"Authorization": "Bearer " + live.token("author"), "Content-Type": "application/json"},
        )
    else:
        modified = deepcopy(body)
        (modified if kind == "top" else modified["data"])["approved_by"] = live.fixture["actors"]["admin"][
            "identity_id"
        ]
        response = live.request(base(tenant) + "/access-upgrade", method="POST", body=modified)
    expect(response, 400 if kind == "duplicate" else 422)


def test_exact_retry_reuse_stale_and_current_authority_are_checked_before_receipts(live):
    row, tenant, body = propose(live)
    assert expect(live.request(base(tenant) + "/access-upgrade", method="POST", body=body), 200) == row
    assert (
        expect(
            live.request(
                base(tenant) + "/access-upgrade",
                method="POST",
                body={**body, "data": {**body["data"], "reason": "Another payload"}},
            ),
            409,
        )["reason_code"]
        == "OPERATION_REUSE"
    )
    assert propose(live, tenant, status=409, revision=str(uuid4()))[0]["code"] == "CONFLICT_VERSION"
    consent = command({"reason": "Exact second administrator consent"}, row["revision_id"])
    accepted = action(live, row, "accept", body=consent)
    assert action(live, row, "accept", body=consent) == accepted
    stale_token = live.signed(row["second_identity_id"], auth_time=time.time() - 600)
    expect(
        request_as(
            live,
            row["second_identity_id"],
            base(row) + "/access-upgrades/" + row["request_id"] + "/actions/accept",
            "POST",
            consent,
            token=stale_token,
        ),
        403,
    )
    with live.db() as c:
        c.execute(
            "UPDATE impact.object_registry SET lifecycle_state='Removed' WHERE tenant_id=%s AND object_id=%s",
            (tenant["tenant_id"], row["current_manifest"]["principals"][1]["membership_id"]),
        )
    assert action(live, row, "accept", status=403, body=consent)["reason_code"] == "SECOND_ADMIN_UNAVAILABLE"


def test_operator_aliases_of_either_administrator_cannot_approve(live):
    row, _, _ = propose(live)
    row = action(live, row, "accept")
    for actor in ["author", "reviewer"]:
        alias, _ = provision_identity(live, live.fixture["actors"][actor]["natural_identity_id"])
        with live.db() as c:
            c.execute(
                "INSERT INTO impact.platform_operator(identity_id,active,expires_at,authority_reference) VALUES(%s,true,now()+interval '1 day','Synthetic alias qualification')",
                (alias,),
            )
        response = expect(
            request_as(
                live,
                alias,
                base(row) + "/access-upgrades/" + row["request_id"] + "/actions/approve",
                "POST",
                command({"reason": "A second login does not create independence"}, row["revision_id"]),
            ),
            403,
        )
        assert response["reason_code"] == "INDEPENDENCE_REQUIRED"
    assert action(live, row, "approve", "admin")["state"] == "Applied"


@pytest.mark.parametrize("drift", ["ceiling", "grant", "membership", "role"])
def test_any_pinned_authority_change_invalidates_second_consent_and_approval(live, drift):
    row, tenant, _ = propose(live)
    accepted = action(live, row, "accept")
    with live.db() as c:
        if drift == "ceiling":
            c.execute(
                "DELETE FROM impact.grant_authority WHERE tenant_id=%s AND authority_id=%s",
                (tenant["tenant_id"], row["current_manifest"]["authority_ids"][0]),
            )
        elif drift == "grant":
            c.execute(
                "UPDATE impact.object_registry SET lifecycle_state='Revoked' WHERE tenant_id=%s AND object_id=%s",
                (tenant["tenant_id"], row["current_manifest"]["grant_revisions"][0]["object_id"]),
            )
        elif drift == "membership":
            c.execute(
                "UPDATE impact.object_registry SET lifecycle_state='Removed' WHERE tenant_id=%s AND object_id=%s",
                (
                    tenant["tenant_id"],
                    row["current_manifest"]["principals"][0]["membership_id"],
                ),
            )
        else:
            c.execute(
                "UPDATE impact.object_registry SET lifecycle_state='Retired' WHERE tenant_id=%s AND object_id=%s",
                (tenant["tenant_id"], row["current_manifest"]["managed_roles"][0]["object_id"]),
            )
    before = snapshot(live, tenant["tenant_id"])
    refused = action(live, accepted, "approve", "admin", status=409 if drift != "membership" else 403)
    assert refused["reason_code"] in {"AUTHORITY_CHANGED", "OWNER_UNAVAILABLE"}
    assert snapshot(live, tenant["tenant_id"]) == before


def test_removed_old_ceiling_and_revoked_grant_are_never_restored(live):
    _, tenant = bootstrapped(live)
    current = preview(live, tenant)
    principal = current["current_manifest"]["principals"][1]
    with live.db() as c:
        old = c.execute(
            "SELECT capability FROM impact.grant_authority WHERE tenant_id=%s AND principal_id=%s ORDER BY capability LIMIT 1",
            (tenant["tenant_id"], principal["principal_id"]),
        ).fetchone()["capability"]
        c.execute(
            "DELETE FROM impact.grant_authority WHERE tenant_id=%s AND principal_id=%s AND capability=%s",
            (tenant["tenant_id"], principal["principal_id"], old),
        )
        grant = c.execute(
            "SELECT object_id FROM impact.grant_current WHERE tenant_id=%s AND subject_id=%s AND capability=%s",
            (tenant["tenant_id"], principal["principal_id"], old),
        ).fetchone()
        if grant:
            c.execute(
                "UPDATE impact.object_registry SET lifecycle_state='Revoked' WHERE tenant_id=%s AND object_id=%s",
                (tenant["tenant_id"], grant["object_id"]),
            )
    row, _, _ = propose(live, tenant)
    assert old not in row["new_capabilities"]
    assert action(live, action(live, row, "accept"), "approve", "admin")["state"] == "Applied"
    with live.db() as c:
        assert not c.execute(
            "SELECT 1 FROM impact.grant_authority WHERE tenant_id=%s AND principal_id=%s AND capability=%s",
            (tenant["tenant_id"], principal["principal_id"], old),
        ).fetchone()
        if grant:
            assert (
                c.execute(
                    "SELECT lifecycle_state FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
                    (tenant["tenant_id"], grant["object_id"]),
                ).fetchone()["lifecycle_state"]
                == "Revoked"
            )


def test_mutual_renewal_upgrade_exclusion_and_expired_request_can_be_closed(live):
    row, tenant, _ = propose(live)
    assert propose_renewal(live, tenant, status=409)[0]["reason_code"] == "ACCESS_UPGRADE_PENDING"
    assert action(live, row, "cancel", "author")["state"] == "Cancelled"
    renewal, _, _, _ = propose_renewal(live, tenant)
    assert propose(live, tenant, status=409)[0]["reason_code"] == "RENEWAL_PENDING"
    from test_authority_renewal import action as renewal_action

    renewal_action(live, renewal, "cancel", "author")
    row, _, _ = propose(live, tenant)
    # Database-owned fixture clock adjustment keeps immutable request contents intact.
    with live.db() as c:
        c.execute("ALTER TABLE impact.tenant_access_upgrade DISABLE TRIGGER access_upgrade_guard")
        c.execute(
            "UPDATE impact.tenant_access_upgrade SET review_expires_at=created_at+interval '1 microsecond' WHERE tenant_id=%s AND request_id=%s",
            (tenant["tenant_id"], row["request_id"]),
        )
        c.execute("ALTER TABLE impact.tenant_access_upgrade ENABLE TRIGGER access_upgrade_guard")
    assert action(live, row, "accept", status=403)["reason_code"] == "ACCESS_UPGRADE_EXPIRED"
    assert action(live, row, "reject", "admin")["state"] == "Rejected"


@pytest.mark.parametrize(
    "role,query",
    [
        ("impact_app", "SELECT * FROM impact.tenant_access_upgrade"),
        ("impact_identity", "SELECT * FROM impact.tenant_access_upgrade"),
        ("impact_worker", "SELECT * FROM impact.tenant_access_upgrade"),
        ("impact_app", "SELECT impact.apply_access_upgrade(NULL,NULL,NULL,NULL)"),
        ("impact_identity", "SELECT * FROM impact.access_upgrade_refs(NULL,NULL)"),
        ("impact_platform", "INSERT INTO impact.grant_authority DEFAULT VALUES"),
        ("impact_platform", "UPDATE impact.grant_authority SET expires_at=now()"),
        ("impact_platform", "INSERT INTO impact.tenant_access_upgrade_applied DEFAULT VALUES"),
        ("impact_platform", "DELETE FROM impact.tenant_access_upgrade"),
    ],
)
def test_runtime_roles_cannot_bypass_reviewed_ceiling_applicator(live, role, query):
    with live.db() as c:
        c.execute("SET LOCAL ROLE " + role)
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            c.execute(query)


def test_forced_tenant_fence_hides_other_tenants_and_applied_record_is_immutable(live):
    row, tenant, _ = propose(live)
    approved = action(live, action(live, row, "accept"), "approve", "admin")
    with live.db() as c:
        c.execute("SET LOCAL ROLE impact_platform")
        assert not c.execute("SELECT * FROM impact.tenant_access_upgrade").fetchall()
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_b"],))
        assert not c.execute(
            "SELECT * FROM impact.tenant_access_upgrade WHERE tenant_id=%s", (tenant["tenant_id"],)
        ).fetchall()
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant["tenant_id"],))
        assert (
            c.execute(
                "SELECT state FROM impact.tenant_access_upgrade WHERE request_id=%s", (row["request_id"],)
            ).fetchone()["state"]
            == "Applied"
        )
        with pytest.raises(psycopg.errors.InsufficientPrivilege, match="access upgrade final"):
            c.execute(
                "UPDATE impact.tenant_access_upgrade SET revision_id=%s WHERE request_id=%s",
                (str(uuid4()), approved["request_id"]),
            )


def test_failure_after_ceiling_insert_rolls_back_everything_then_exact_retry_commits_once(live):
    row, tenant, _ = propose(live)
    row = action(live, row, "accept")
    body = command({"reason": "Atomic upgrade failure and retry"}, row["revision_id"])
    before = snapshot(live, tenant["tenant_id"])
    with live.db() as c:
        c.execute(
            "CREATE FUNCTION impact.test_reject_upgrade_event() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.action='access-upgrade-approve' THEN RAISE EXCEPTION 'qualification injected failure'; END IF; RETURN NEW; END $$"
        )
        c.execute(
            "CREATE TRIGGER test_reject_upgrade_event BEFORE INSERT ON impact.platform_event FOR EACH ROW EXECUTE FUNCTION impact.test_reject_upgrade_event()"
        )
    try:
        action(live, row, "approve", "admin", status=503, body=body)
        assert snapshot(live, tenant["tenant_id"]) == before
        with live.db() as c:
            assert not c.execute(
                "SELECT 1 FROM impact.platform_receipt WHERE operation_id=%s", (body["operation_id"],)
            ).fetchone()
            assert not c.execute(
                "SELECT 1 FROM impact.tenant_access_upgrade_applied WHERE tenant_id=%s AND request_id=%s",
                (tenant["tenant_id"], row["request_id"]),
            ).fetchone()
    finally:
        with live.db() as c:
            c.execute("DROP TRIGGER test_reject_upgrade_event ON impact.platform_event")
            c.execute("DROP FUNCTION impact.test_reject_upgrade_event()")
    approved = action(live, row, "approve", "admin", body=body)
    assert action(live, row, "approve", "admin", body=body) == approved
    assert len(snapshot(live, tenant["tenant_id"])["authority"]) > len(before["authority"])


def test_signed_cursors_bind_identity_route_tenant_visibility_and_expiry(live):
    row, tenant, _ = propose(live)
    other = bootstrapped(live)[1]
    action(live, row, "cancel", "author")
    # Synthetic cancelled-request history exercises real bounded pagination.
    with live.db() as c:
        for _ in range(51):
            request_id = str(uuid4())
            c.execute(
                "INSERT INTO impact.tenant_access_upgrade(tenant_id,request_id,revision_id,state,bootstrap_request_id,"
                "owner_identity_id,second_identity_id,tenant_revision,owner_revision,current_manifest,authority_hash,"
                "profile_hash,target_manifest,new_capabilities,review_expires_at,owner_auth_time,reason) "
                "SELECT tenant_id,%s,%s,'Requested',bootstrap_request_id,owner_identity_id,second_identity_id,"
                "tenant_revision,owner_revision,current_manifest,authority_hash,profile_hash,target_manifest,"
                "new_capabilities,review_expires_at,owner_auth_time,'Synthetic cancelled request history' "
                "FROM impact.tenant_access_upgrade WHERE tenant_id=%s AND request_id=%s",
                (request_id, str(uuid4()), tenant["tenant_id"], row["request_id"]),
            )
            c.execute(
                "UPDATE impact.tenant_access_upgrade SET state='Cancelled' WHERE tenant_id=%s AND request_id=%s",
                (tenant["tenant_id"], request_id),
            )
    first = listing(live, tenant=tenant)
    token = first["next_cursor"]
    assert len(first["items"]) == 50 and token and "." in token
    second = valid(
        DIRECTORY, expect(live.request(base(tenant) + "/access-upgrades", params={"cursor": token}), 200)
    )
    assert len(second["items"]) == 2 and second["next_cursor"] is None
    assert not (
        {item["request_id"] for item in first["items"]} & {item["request_id"] for item in second["items"]}
    )
    for path, actor, value in [
        (base(tenant) + "/access-upgrades", "author", token[:-1] + ("0" if token[-1] != "0" else "1")),
        (base(tenant) + "/access-upgrades", "reviewer", token),
        (base(other) + "/access-upgrades", "author", token),
        ("/v1/platform/access-upgrades", "author", token),
        (base(tenant) + "/access-upgrades", "author", str(uuid4())),
    ]:
        assert (
            expect(live.request(path, actor=actor, params={"cursor": value}), 400)["code"] == "INVALID_CURSOR"
        )
    encoded = token.split(".")[0]
    payload = json.loads(base64.urlsafe_b64decode(encoded + "=" * ((-len(encoded)) % 4)))
    payload["expires"] = int(time.time()) - 1
    expired = Service.cursor(SimpleNamespace(s=Settings(**live.config)), payload)
    assert (
        expect(live.request(base(tenant) + "/access-upgrades", params={"cursor": expired}), 400)["code"]
        == "INVALID_CURSOR"
    )
    with live.db() as c:
        c.execute(
            "UPDATE impact.tenant_principal SET subject_epoch=subject_epoch+1 WHERE tenant_id=%s AND identity_id=%s",
            (tenant["tenant_id"], row["owner_identity_id"]),
        )
    assert (
        expect(live.request(base(tenant) + "/access-upgrades", params={"cursor": token}), 400)["code"]
        == "INVALID_CURSOR"
    )


def test_native_registry_and_review_tables_remain_outside_app_identity_worker_logins(live):
    if not os.environ.get("IMPACT_LOGIN_DSN_PLATFORM"):
        pytest.skip("Provisioned native logins required; no native role evidence is inferred from PGlite")
    for name in ["APP", "IDENTITY", "WORKER"]:
        with psycopg.connect(os.environ["IMPACT_LOGIN_DSN_" + name], prepare_threshold=None) as c:
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                c.execute("SELECT * FROM impact.platform_access_profile")
        with psycopg.connect(os.environ["IMPACT_LOGIN_DSN_" + name], prepare_threshold=None) as c:
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                c.execute("SELECT * FROM impact.tenant_access_upgrade")
    for sql in [
        "INSERT INTO impact.platform_access_profile DEFAULT VALUES",
        "UPDATE impact.platform_access_profile SET source_migration='forged'",
        "INSERT INTO impact.grant_authority DEFAULT VALUES",
    ]:
        with psycopg.connect(os.environ["IMPACT_LOGIN_DSN_PLATFORM"], prepare_threshold=None) as c:
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                c.execute(sql)
