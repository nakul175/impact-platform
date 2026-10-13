"""US-DX-01a native-only tenant fences, history guards and real edit/authority races.

Actual execution receipts are separate; this source makes no test-pass claim.

Requires the existing provisioned login harness. A PGlite run skips these checks;
the skip is not passing evidence. No new runtime grants or waiver identities.
"""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import os
import time

import psycopg
import pytest

from test_ai_diagnosis_live import action, action_body, diagnosis, domain_counts, get, save
from test_live_application import cmd, expect
from test_native_concurrency import count, outcomes, race, sender
from test_native_roles import denied

pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Native PostgreSQL login-role fences and simultaneous transactions cannot be qualified on PGlite",
)


def login(name):
    dsn = os.environ.get("IMPACT_LOGIN_DSN_" + name)
    assert dsn, "Native harness must provision the " + name + " login"
    return psycopg.connect(dsn, autocommit=True, prepare_threshold=None)


def test_native_diagnosis_shared_registry_and_revision_have_forced_tenant_fences(live):
    row = save(live)
    tenant_a, tenant_b = live.fixture["tenant_a"], live.fixture["tenant_b"]
    with login("APP") as c:
        for table in ("object_registry", "object_revision"):
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                assert c.execute(
                    "SELECT relrowsecurity,relforcerowsecurity FROM pg_class WHERE oid=%s::regclass",
                    ("impact." + table,),
                ).fetchone() == (True, True)
                assert (
                    c.execute(
                        "SELECT tenant_id FROM impact." + table + " WHERE object_id=%s",
                        (row["object_id"],),
                    ).fetchall()
                    == []
                )
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_b,))
                assert (
                    c.execute(
                        "SELECT tenant_id FROM impact." + table + " WHERE object_id=%s",
                        (row["object_id"],),
                    ).fetchall()
                    == []
                )
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_a,))
                seen = c.execute(
                    "SELECT tenant_id FROM impact." + table + " WHERE object_id=%s",
                    (row["object_id"],),
                ).fetchall()
                assert seen and {str(item[0]) for item in seen} == {tenant_a}


def test_native_application_cannot_rewrite_or_delete_a_saved_diagnosis_revision(live):
    row = save(live)
    tenant = live.fixture["tenant_a"]
    original = get(live, row)
    with login("APP") as c:
        for statement in (
            "UPDATE impact.object_revision SET payload='{}'::jsonb WHERE tenant_id=%s AND revision_id=%s",
            "DELETE FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
        ):
            denied(
                c,
                statement,
                (tenant, row["revision_id"]),
                role="impact_app",
                tenant=tenant,
            )
    assert get(live, row) == original


def test_native_platform_restrictive_kind_list_does_not_gain_diagnosis_access(live):
    row = save(live)
    tenant = live.fixture["tenant_a"]
    with login("PLATFORM") as c:
        for table in ("object_registry", "object_revision"):
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_platform")
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
                assert (
                    c.execute(
                        "SELECT tenant_id FROM impact." + table + " WHERE object_id=%s",
                        (row["object_id"],),
                    ).fetchall()
                    == []
                )


def test_native_two_diagnosis_edits_publish_one_authoritative_head_and_one_conflict(
    live,
):
    row = save(live)
    original = get(live, row)
    first = {key: deepcopy(original["data"][key]) for key in ("title", "problems", "priority_order")}
    second = deepcopy(first)
    first["title"] = "Synthetic concurrent edit A"
    second["title"] = "Synthetic concurrent edit B"
    first_body, second_body = (
        cmd(first, row["revision_id"]),
        cmd(second, row["revision_id"]),
    )
    token = live.token("admin")
    path = live.path("ai-enablement/diagnoses", row["object_id"])
    results = race(
        sender(live, token, "PUT", path, first_body),
        sender(live, token, "PUT", path, second_body),
    )
    assert outcomes(results) == [200, 409]
    winners = [item for item in results if item["status"] == 200]
    losers = [item for item in results if item["status"] == 409]
    assert losers[0]["body"]["code"] == "CONFLICT_VERSION"
    current = get(live, row)
    assert current["revision_id"] == winners[0]["body"]["revision_id"]
    assert current["data"]["title"] in {first["title"], second["title"]}
    tenant = live.fixture["tenant_a"]
    assert (
        count(
            live,
            "SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s",
            tenant,
            row["object_id"],
        )
        == 2
    )
    assert (
        count(
            live,
            "SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s AND operation_id=ANY(%s::uuid[])",
            tenant,
            [first_body["operation_id"], second_body["operation_id"]],
        )
        == 1
    )
    assert (
        count(
            live,
            "SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s AND object_reference=%s",
            tenant,
            row["object_id"],
        )
        == 2
    )


@pytest.mark.parametrize("capability", ["ai.diagnosis.read", "ai.diagnosis.manage"])
@pytest.mark.parametrize(
    "command", ["create", "edit", "replay", "complete", "revise", "complete_replay", "revise_replay"]
)
def test_native_queued_diagnosis_write_rechecks_current_grant_before_mutation_or_replay(
    live, capability, command
):
    """Withdraw only a synthetic current grant while the real API waits for the
    tenant lock. This is not a governed revocation workflow or historical edit.
    Observe an actual native advisory-lock wait before changing authority; a
    sleep alone would not prove that a request was queued under earlier grants.
    """
    creation = cmd(diagnosis())
    row = save(live, body=creation)
    if command in {"revise", "revise_replay"}:
        row = action(live, row, "complete")
    original = get(live, row)
    tenant = live.fixture["tenant_a"]
    principal = live.fixture["actors"]["admin"]["principal_id"]
    path = live.path("ai-enablement/diagnoses")
    method, expected = "POST", 201
    body = creation if command == "replay" else cmd(diagnosis())
    if command == "edit":
        path += "/" + row["object_id"]
        method, expected = "PUT", 200
        data = {key: deepcopy(original["data"][key]) for key in ("title", "problems", "priority_order")}
        data["title"] = "Synthetic queued edit under withdrawn authority"
        body = cmd(data, row["revision_id"])
    elif command in {"complete", "revise", "complete_replay", "revise_replay"}:
        name = command.removesuffix("_replay")
        path += "/" + row["object_id"] + "/actions/" + name
        expected = 200
        body = action_body(
            row, **({"reason": "Synthetic queued reasoned correction"} if name == "revise" else {})
        )
        if command.endswith("_replay"):
            row = action(live, row, name, body)
            original = get(live, row)
    token = live.token("admin")
    before = domain_counts(live)
    grants = []
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            with live.db() as holder:
                holder.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
                holder.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
                grants = holder.execute(
                    "SELECT object_id,purpose FROM impact.grant_current "
                    "WHERE tenant_id=%s AND subject_id=%s AND capability=%s AND purpose IS NULL",
                    (tenant, principal, capability),
                ).fetchall()
                assert grants, "The existing synthetic grant must actually authorize this capability"
                queued = pool.submit(sender(live, token, method, path, body))
                deadline = time.monotonic() + 1.5
                waiting = False
                while time.monotonic() < deadline and not queued.done():
                    holder.execute("SELECT pg_stat_clear_snapshot()")
                    waiting = holder.execute(
                        "SELECT EXISTS(SELECT 1 FROM pg_stat_activity "
                        "WHERE usename='impact_app_login' AND wait_event_type='Lock' "
                        "AND wait_event='advisory') AS waiting"
                    ).fetchone()["waiting"]
                    if waiting:
                        break
                    time.sleep(0.01)
                assert waiting and not queued.done(), "The real request must wait before authority changes"
                holder.execute(
                    "UPDATE impact.grant_current SET purpose='QUALIFICATION' "
                    "WHERE tenant_id=%s AND object_id=ANY(%s::uuid[])",
                    (tenant, [str(grant["object_id"]) for grant in grants]),
                )
                holder.commit()  # Publish authority loss before releasing the queued write.
            result = queued.result(timeout=10)
        assert result["status"] == 404 and result["body"]["code"] == "RESOURCE_UNAVAILABLE", result
        assert domain_counts(live) == before  # Including unchanged exact-replay receipt/history.
    finally:
        if grants:
            with live.db() as c:
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
                c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
                for grant in grants:
                    c.execute(
                        "UPDATE impact.grant_current SET purpose=%s WHERE tenant_id=%s AND object_id=%s",
                        (grant["purpose"], tenant, grant["object_id"]),
                    )
    assert get(live, row) == original
    # Once the exact fixture grant is restored, the same operation succeeds or
    # returns its original receipt. No replacement operation or new history is
    # used to hide an unauthorised side effect from the queued attempt.
    response = live.request(path, actor="admin", method=method, body=body)
    assert response.status_code == expected, response.text
    if command in {"replay", "complete_replay", "revise_replay"}:
        assert response.json() == row and domain_counts(live) == before


@pytest.mark.parametrize(
    "command,conflicting",
    [
        ("create", False),
        ("edit", False),
        ("complete", False),
        ("revise", False),
        ("create", True),
        ("edit", True),
        ("revise", True),
    ],
)
def test_native_simultaneous_diagnosis_operation_writes_once_and_binds_exact_payload(
    live, command, conflicting
):
    path = live.path("ai-enablement/diagnoses")
    method, success, prior_revisions = "POST", 201, 0
    original = None
    first = cmd(diagnosis())
    if command != "create":
        row = save(live)
        if command == "revise":
            row = action(live, row, "complete")
            prior_revisions = 2
        else:
            prior_revisions = 1
        original = get(live, row)
        path += "/" + row["object_id"]
        success = 200
        if command == "edit":
            method = "PUT"
            first = cmd(diagnosis(), row["revision_id"])
        else:
            path += "/actions/" + command
            first = action_body(
                row, **({"reason": "Synthetic competing correction A"} if command == "revise" else {})
            )
    second = deepcopy(first)
    if conflicting:
        if command == "revise":
            second["reason"] = "Synthetic competing correction B"
        else:
            second["data"]["title"] = "Synthetic competing payload B"
    before = domain_counts(live)
    token = live.token("admin")
    results = race(
        sender(live, token, method, path, first),
        sender(live, token, method, path, second),
    )
    assert outcomes(results) == ([success, 409] if conflicting else [success, success]), results
    winner = next(i for i, result in enumerate(results) if result["status"] == success)
    receipt = results[winner]["body"]
    if conflicting:
        assert results[1 - winner]["body"]["code"] == "CONFLICT_OPERATION"
    else:
        assert results[0]["body"] == results[1]["body"]
    current = get(live, receipt)
    assert current["revision_id"] == receipt["revision_id"]
    winner_body = (first, second)[winner]
    if command == "revise":
        assert current["business_state"] == "Draft"
        assert current["data"]["correction_reason"] == winner_body["reason"]
    elif command == "complete":
        assert current["business_state"] == "Completed"
    else:
        assert current["data"]["title"] == winner_body["data"]["title"]
    tenant = live.fixture["tenant_a"]
    assert (
        count(
            live,
            "SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s",
            tenant,
            receipt["object_id"],
        )
        == prior_revisions + 1
    )
    assert (
        count(
            live,
            "SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s AND object_reference=%s",
            tenant,
            receipt["object_id"],
        )
        == prior_revisions + 1
    )
    assert (
        count(
            live,
            "SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s AND operation_id=%s",
            tenant,
            first["operation_id"],
        )
        == 1
    )
    after = domain_counts(live)
    assert after["outbox_event"] == before["outbox_event"] + 1
    assert after["object_revision"] == before["object_revision"] + 2  # Diagnosis and its audit.
    assert after["operation_receipt"] == before["operation_receipt"] + 1
    if original:
        assert (
            expect(
                live.request(
                    live.path("ai-enablement/diagnoses", receipt["object_id"])
                    + "/revisions/"
                    + original["revision_id"],
                    actor="admin",
                ),
                200,
            )
            == original
        )
    assert expect(live.request(path, actor="admin", method=method, body=winner_body), success) == receipt
    if conflicting:
        refused = expect(
            live.request(path, actor="admin", method=method, body=(first, second)[1 - winner]), 409
        )
        assert refused["code"] == "CONFLICT_OPERATION"
    assert domain_counts(live) == after
