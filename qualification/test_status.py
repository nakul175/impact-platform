"""User-visible degradation status, GET /v1/status (release 0.27, VF-AVL-002), through live HTTP:
every signed-in identity reads the closed notice catalogue (never a reason code, login, tenant or
address); platform operators also read the detail (worker freshness, failed deliveries, storage,
the server's alert list, the on-call rota); an anonymous caller gets 401. A stale worker heartbeat
turns the delivery and export notices on for members and operators alike, and a fresh beat turns
them off again."""

import json

from impact_api.status import CATALOGUE, POLL_SECONDS
from test_administration import expect
from test_worker import make_worker

PATH = "/v1/status"
MEMBER_KEYS = {"generated_at", "state", "poll_seconds", "notices"}


def read(live, actor):
    body = expect(live.request(PATH, actor=actor), 200)
    assert set(body) in (MEMBER_KEYS, MEMBER_KEYS | {"detail"})
    assert body["state"] in {"OK", "DEGRADED"} and body["poll_seconds"] == POLL_SECONDS
    for notice in body["notices"]:
        assert notice["code"] in CATALOGUE and notice["message"] == CATALOGUE[notice["code"]][1]
        assert notice["severity"] == CATALOGUE[notice["code"]][0]
    assert (body["state"] == "DEGRADED") == bool(body["notices"])
    return body


def age_heartbeats(live, worker, seconds):
    with worker.transaction() as c:
        c.execute(
            "UPDATE impact.worker_heartbeat SET beat_at=statement_timestamp()-make_interval(secs=>%s)",
            (seconds,),
        )


def test_members_read_notices_only_and_operators_read_the_detail(live):
    worker = make_worker(live)
    worker.run_once()  # a fresh RUNNING heartbeat
    for actor in ["author", "partner", "other_tenant", "enumerator"]:
        body = read(live, actor)
        assert "detail" not in body
        assert "DELIVERY_DELAYED" not in {n["code"] for n in body["notices"]}
    expect(live.request(PATH, actor=None), 401)
    body = read(live, "admin")
    detail = body["detail"]
    assert detail["workers"]["running_fresh"] >= 1 and detail["workers"]["stale"] is False
    assert detail["workers"]["stale_after_seconds"] == 120
    assert detail["deliveries"]["dead"] is not None and detail["deliveries"]["held"] is not None
    assert detail["operations"] is None  # no ops-check file in the test configuration
    assert detail["on_call"] == {"status": "NOT_CONFIGURED"}
    assert "WORKER_STALE" not in detail["sources"]
    text = json.dumps(body)
    assert live.fixture["tenant_a"] not in text and "impact_app" not in text and "dsn" not in text.lower()


def test_a_stale_worker_turns_the_delivery_and_export_notices_on_for_everyone(live):
    worker = make_worker(live)
    worker.run_once()
    age_heartbeats(live, worker, 600)
    try:
        member = read(live, "author")
        assert member["state"] == "DEGRADED"
        assert [n["code"] for n in member["notices"]] == ["DELIVERY_DELAYED", "EXPORTS_DELAYED"]
        assert all(n["severity"] == "warning" for n in member["notices"])
        operator = read(live, "owner")
        assert operator["notices"] == member["notices"]
        assert (
            operator["detail"]["workers"]["stale"] is True
            and operator["detail"]["workers"]["running_fresh"] == 0
        )
        assert operator["detail"]["sources"] == ["WORKER_STALE"]
        # The notices are catalogue text: no code, login or figure from the detail leaks into them.
        for notice in member["notices"]:
            assert "WORKER" not in notice["message"] and "120" not in notice["message"]
    finally:
        worker.heartbeat("RUNNING")
    recovered = read(live, "author")
    assert recovered["state"] == "OK" and recovered["notices"] == []
