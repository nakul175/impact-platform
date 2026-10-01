"""Operator-only operations summary, GET /v1/platform/metrics (platform API 1.6.0), through live
HTTP: counts of workers, DEAD/held/unsent deliveries and unfinished jobs over the tenants under
control-plane custody, and this process's request counters; never a tenant identifier; anyone who
is not a platform operator gets 404, an anonymous caller 401."""

import json
from uuid import uuid4

from jsonschema import Draft202012Validator, FormatChecker
from impact_api.metrics_contracts import METRICS
from impact_api.version import BUILD, SCHEMA
from test_administration import expect
from test_tenant_lifecycle import active
from test_worker import make_worker

PATH = "/v1/platform/metrics"


def metrics(live, actor="admin"):
    body = expect(live.request(PATH, actor=actor), 200)
    Draft202012Validator(METRICS, format_checker=FormatChecker()).validate(body)
    return body


def delivery(live, tenant_id, state):
    event_id = str(uuid4())
    with live.db() as c:
        c.execute(
            "INSERT INTO impact.outbox_event VALUES(%s,%s,'delivery.requested',now(),'{}'::jsonb)",
            (tenant_id, event_id),
        )
        c.execute(
            "INSERT INTO impact.outbox_delivery(tenant_id,event_id,channel,template,reference_id,state,attempts,"
            "last_error_class,last_attempt_at,completed_at,next_attempt_at) VALUES(%s,%s,'IN_APP','IN_APP_NOTICE',"
            "%s,%s,%s,%s,now(),%s,now()+interval '1 day')",
            (
                tenant_id,
                event_id,
                str(uuid4()),
                state,
                6 if state == "DEAD" else 0,
                "SYNTHETIC_FAILURE" if state == "DEAD" else None,
                None if state == "PENDING" else "2026-10-01T00:00:00Z",
            ),
        )
    return event_id


def test_operators_read_counts_and_no_tenant_data(live):
    make_worker(live).run_once()
    before = metrics(live)
    tenant = active(live)
    delivery(live, tenant["tenant_id"], "DEAD")
    delivery(live, tenant["tenant_id"], "PENDING")
    after = metrics(live)
    assert (after["build"], after["schema_version"], after["schema_expected"]) == (BUILD, SCHEMA, SCHEMA)
    assert after["workers"]["running_fresh"] >= 1 and after["workers"]["newest_beat_age_seconds"] is not None
    assert after["deliveries"]["dead"] >= min(before["deliveries"]["dead"] + 1, 50)
    assert after["deliveries"]["unsent"] >= before["deliveries"]["unsent"] + 1
    assert after["tenants"]["counted"] == before["tenants"]["counted"] + 1
    assert after["tenants"]["by_lifecycle"].get("Active", 0) >= 1
    # The previous call is counted: a platform request answered 200.
    assert after["requests"]["total"] > before["requests"]["total"]
    assert after["requests"]["by_family"]["platform"]["2xx"] >= 1
    assert after["requests"]["latency_seconds"]["buckets"][-1]["count"] == after["requests"]["total"]
    text = json.dumps(after)
    assert tenant["tenant_id"] not in text and live.fixture["tenant_a"] not in text
    assert after["operations"] is None  # no ops-check file in the test configuration


def test_metrics_are_for_platform_operators_only(live):
    for actor in ["author", "partner", "other_tenant", "reviewer"]:
        expect(live.request(PATH, actor=actor), 404)
    expect(live.request(PATH, actor=None), 401)
    assert metrics(live, "owner")["workers"]["stale_after_seconds"] == 120
