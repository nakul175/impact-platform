"""Operator re-queue of held or DEAD outbox deliveries (control plane, platform API 1.5.0).

Through live HTTP and the database roles: operator-only (others 404), fresh assurance, reason
required, revision-fenced (the row's lease generation), exact replay returns the original receipt,
platform_event + platform_receipt committed together, a Suspended tenant refused, and a re-queued or
released row delivered by the worker afterwards.
"""

import time
from uuid import uuid4

from jsonschema import Draft202012Validator, FormatChecker
from impact_api.requeue_contracts import DIRECTORY, RECEIPT
from impact_api.worker import empty_summary
from test_administration import command, expect
from test_tenant_lifecycle import action as tenant_action, active
from test_worker import deliveries, invitation, make_worker, sink_lines

BASE = "/v1/platform/deliveries"


def valid(schema, value):
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)
    return value


def attention(live, tenant=None, actor="admin"):
    path = BASE + ("?tenant_id=" + str(tenant) if tenant else "")
    return valid(DIRECTORY, expect(live.request(path, actor=actor), 200))


def listed(live, event_id, tenant=None):
    items = attention(live, tenant or live.fixture["tenant_a"])["items"]
    return next((i for i in items if i["event_id"] == str(event_id)), None)


def act(live, tenant, event_id, name, revision, actor="admin", status=200, body=None, **kwargs):
    path = "/v1/platform/tenants/" + str(tenant) + "/deliveries/" + str(event_id) + "/actions/" + name
    body = body or command({"reason": "Operator reviewed the failed delivery"}, revision)
    result = expect(live.request(path, actor=actor, method="POST", body=body, **kwargs), status)
    return valid(RECEIPT, result) if status == 200 else result


def dead_invitation(live):
    """A real invitation intent in tenant A that the worker gave up on (synthetic failure)."""
    _, receipt = invitation(live)
    [row] = deliveries(live, receipt["object_id"])
    worker = make_worker(live, max_attempts=1, synthetic_failures=1000)
    rows = {str(r["event_id"]): r for r in worker.claim(live.fixture["tenant_a"], empty_summary())}
    worker.process(live.fixture["tenant_a"], rows[str(row["event_id"])], empty_summary())
    [dead] = deliveries(live, receipt["object_id"])
    assert (dead["state"], dead["attempts"], dead["last_error_class"]) == ("DEAD", 1, "SYNTHETIC_FAILURE")
    return receipt, dead


def events(live, event_id):
    with live.db() as c:
        return c.execute(
            "SELECT action,reason,payload FROM impact.platform_event WHERE payload->>'event_id'=%s "
            "AND action LIKE 'delivery-%%' ORDER BY created_at",
            (str(event_id),),
        ).fetchall()


def test_operator_requeues_a_dead_delivery_once_and_the_worker_delivers_it(live):
    tenant = live.fixture["tenant_a"]
    receipt, dead = dead_invitation(live)
    item = listed(live, dead["event_id"])
    assert item and (item["state"], item["held"], item["permitted_actions"]) == ("DEAD", False, ["requeue"])
    assert item["revision"] == str(dead["lease_generation"]) and item["lifecycle_state"] == "Active"
    assert item["template"] == "MEMBER_INVITATION" and item["last_error_class"] == "SYNTHETIC_FAILURE"
    assert "recipient_sealed" not in item and "reference_id" not in item
    # Stale revision and the wrong action change nothing.
    stale = str(int(item["revision"]) + 1)
    assert act(live, tenant, dead["event_id"], "requeue", stale, status=409)["code"] == "CONFLICT_VERSION"
    wrong = act(live, tenant, dead["event_id"], "release", item["revision"], status=409)
    assert wrong["reason_code"] == "DELIVERY_NOT_HELD"
    assert (
        deliveries(live, receipt["object_id"])[0]["state"] == "DEAD" and events(live, dead["event_id"]) == []
    )

    body = command({"reason": "Mailbox restored; send the invitation again"}, item["revision"])
    done = act(live, tenant, dead["event_id"], "requeue", item["revision"], body=body)
    assert (done["state"], done["held"], done["attempts"], done["previous_state"]) == (
        "PENDING",
        False,
        0,
        "DEAD",
    )
    assert done["previous_attempts"] == 1 and done["previous_error_class"] == "SYNTHETIC_FAILURE"
    assert done["revision"] == str(dead["lease_generation"] + 1)
    [row] = deliveries(live, receipt["object_id"])
    assert (row["state"], row["attempts"], row["completed_at"], row["held_at"]) == ("PENDING", 0, None, None)
    # The exact retry returns the original receipt; the same identifier with another payload conflicts.
    assert act(live, tenant, dead["event_id"], "requeue", item["revision"], body=body) == done
    reused = dict(body, data={"reason": "Another reason"})
    assert (
        act(live, tenant, dead["event_id"], "requeue", item["revision"], body=reused, status=409)[
            "reason_code"
        ]
        == "OPERATION_REUSE"
    )
    [event] = events(live, dead["event_id"])
    assert event["action"] == "delivery-requeue" and event["reason"] == body["data"]["reason"]
    assert event["payload"] == done
    with live.db() as c:
        stored = c.execute(
            "SELECT response FROM impact.platform_receipt WHERE operation_id=%s", (body["operation_id"],)
        ).fetchone()
    assert stored["response"] == done
    assert listed(live, dead["event_id"]) is None

    worker = make_worker(live)
    worker.run_once()
    [sent] = deliveries(live, receipt["object_id"])
    assert sent["state"] == "SENT" and [
        m for m in sink_lines(worker.s) if m["event_id"] == str(sent["event_id"])
    ]
    again = act(live, tenant, dead["event_id"], "requeue", str(sent["lease_generation"]), status=409)
    assert again["reason_code"] == "DELIVERY_NOT_DEAD"


def test_only_a_fresh_platform_operator_with_a_reason_may_requeue(live):
    tenant = live.fixture["tenant_a"]
    _, dead = dead_invitation(live)
    revision = str(dead["lease_generation"])
    assert all(i["tenant_id"] == tenant for i in attention(live, tenant)["items"])
    assert listed(live, dead["event_id"]) in attention(live)["items"] or len(attention(live)["items"]) == 50
    for actor in ["author", "reviewer", "partner"]:
        expect(live.request(BASE, actor=actor), 404)
        act(live, tenant, dead["event_id"], "requeue", revision, actor=actor, status=404)
    stale = live.signed(live.fixture["actors"]["admin"]["identity_id"], auth_time=time.time() - 400)
    refused = act(
        live,
        tenant,
        dead["event_id"],
        "requeue",
        revision,
        status=403,
        headers={"Authorization": "Bearer " + stale},
    )
    assert refused["reason_code"] == "FRESH_MFA_REQUIRED"
    for body in [
        command({"reason": " "}, revision),
        command({}, revision),
        command({"reason": "x"}, "not-a-number"),
        {**command({"reason": "x"}, revision), "extra": True},
    ]:
        act(live, tenant, dead["event_id"], "requeue", revision, body=body, status=422)
    act(live, tenant, dead["event_id"], "resend", revision, status=404)
    act(live, tenant, uuid4(), "requeue", revision, status=404)
    act(live, live.fixture["tenant_b"], dead["event_id"], "requeue", revision, status=404)
    assert deliveries(live, dead["reference_id"])[0]["state"] == "DEAD"


def test_operator_releases_a_held_delivery_of_an_active_tenant(live):
    tenant = live.fixture["tenant_a"]
    _, receipt = invitation(live)
    [row] = deliveries(live, receipt["object_id"])
    with live.db() as c:
        # What quiesce_tenant does on suspension; tenant A itself stays Active here.
        c.execute(
            "UPDATE impact.outbox_delivery SET held_at=now() WHERE tenant_id=%s AND event_id=%s",
            (tenant, row["event_id"]),
        )
    worker = make_worker(live)
    worker.run_once()
    assert deliveries(live, receipt["object_id"])[0]["state"] == "PENDING"
    item = listed(live, row["event_id"])
    assert (item["state"], item["held"], item["permitted_actions"]) == ("PENDING", True, ["release"])
    wrong = act(live, tenant, row["event_id"], "requeue", item["revision"], status=409)
    assert wrong["reason_code"] == "DELIVERY_NOT_DEAD"
    released = act(live, tenant, row["event_id"], "release", item["revision"])
    assert (released["state"], released["held"], released["previous_state"]) == ("PENDING", False, "PENDING")
    assert [e["action"] for e in events(live, row["event_id"])] == ["delivery-release"]
    worker.run_once()
    assert deliveries(live, receipt["object_id"])[0]["state"] == "SENT"


def test_suspended_tenant_rows_are_listed_but_refused_until_reactivation(live):
    tenant = active(live)
    tenant_id, event_id = tenant["tenant_id"], str(uuid4())
    with live.db() as c:
        c.execute(
            "INSERT INTO impact.outbox_event VALUES(%s,%s,'delivery.requested',now(),'{}'::jsonb)",
            (tenant_id, event_id),
        )
        c.execute(
            "INSERT INTO impact.outbox_delivery(tenant_id,event_id,channel,template,reference_id,state,attempts,"
            "last_error_class,last_attempt_at,completed_at) VALUES(%s,%s,'IN_APP','IN_APP_NOTICE',%s,'DEAD',6,"
            "'SYNTHETIC_FAILURE',now(),now())",
            (tenant_id, event_id, str(uuid4())),
        )
    suspended = tenant_action(live, tenant, "suspend", actor="admin")
    item = listed(live, event_id, tenant_id)
    assert (item["state"], item["held"], item["lifecycle_state"], item["permitted_actions"]) == (
        "DEAD",
        True,
        "Suspended",
        [],
    )
    assert item["operating_name"] == tenant["operating_name"]
    refused = act(live, tenant_id, event_id, "requeue", item["revision"], status=403)
    assert refused["reason_code"] == "TENANT_NOT_ACTIVE" and events(live, event_id) == []
    tenant_action(live, suspended, "reactivate")
    assert listed(live, event_id, tenant_id)["permitted_actions"] == ["requeue"]
    done = act(live, tenant_id, event_id, "requeue", item["revision"])
    assert (done["state"], done["held"], done["attempts"]) == ("PENDING", False, 0)
    with live.db() as c:
        row = c.execute(
            "SELECT held_at,state,next_attempt_at<=now() AS due FROM impact.outbox_delivery "
            "WHERE tenant_id=%s AND event_id=%s",
            (tenant_id, event_id),
        ).fetchone()
    assert row["held_at"] is None and row["state"] == "PENDING" and row["due"]
