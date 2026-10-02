"""Native-only non-functional qualification (QA 2026-10, v0.26 remainder): the three database
behaviours no earlier gate exercised.

- Connection pooler: with `scripts/run.py test --native --pooler pgbouncer` the API and the worker
  reach PostgreSQL through a PgBouncer in TRANSACTION pooling mode with three server connections per
  login. The cases here prove the multiplexing happened (admin console counters), that the
  transaction-local tenant context, the transaction-scoped advisory lock, operation receipts and
  signed cursors behave exactly as they do on direct connections, and that the pooled worker login
  delivers. They skip without the pooler.
- Database restart: with IMPACT_DB_STOP_COMMAND and IMPACT_DB_START_COMMAND naming shell commands
  that stop and start the suite's own cluster (the runner never does this itself, and CI's service
  container cannot be restarted from the job), the suite's API process answers 503
  DATABASE_UNAVAILABLE while the server is down, recovers without being restarted, replays receipts
  intact, commits a refused write exactly once on retry, and a worker subprocess keeps its heartbeat.
- Lock order across objects: three writers of one tenant, released together, touching the same
  period from different objects (close review approval, the creation of one more source and a
  restatement request) never deadlock and always land on the documented outcomes, whatever order
  the tenant advisory lock admits them in. By construction the tenant advisory lock serialises
  them, so this is evidence that the order is kept, not a test of row-lock ordering under
  concurrent writers (there are none once the tenant lock is held; see the module docstring of
  test_native_concurrency.py).

Every case uses fresh objects, so the rest of the suite stays order-independent.
"""

import json
import os
import re
import shlex
import subprocess
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import httpx
import psycopg
import pytest
from psycopg.rows import dict_row

from test_live_application import cmd, draft, expect
from test_measurement import get, measurement_builder
from test_native_concurrency import deadlocks, race, receipts, revisions, sender
from test_native_worker import heartbeat, start, stop, wait_for
from test_period_governance import complete_period, request_close

NATIVE = os.environ.get("IMPACT_NATIVE_TEST") == "1"
POOLER = os.environ.get("IMPACT_DB_POOLER")
POOLER_ADMIN_DSN = os.environ.get("IMPACT_POOLER_ADMIN_DSN")
POOL_SIZE = int(os.environ.get("IMPACT_POOLER_POOL_SIZE", "3"))
STOP_COMMAND = os.environ.get("IMPACT_DB_STOP_COMMAND")
START_COMMAND = os.environ.get("IMPACT_DB_START_COMMAND")
RACE_FILE = "lock-order-races.json"
# Four releases of the three-writer race: two unbiased, then one per forced order (a 50 ms head
# start for the other two writers) so that both admissible orders are asserted in every run.
RACE_MODES = ["race", "race", "close_first", "source_first"]
RACE_HEAD_START_SECONDS = 0.1

pytestmark = pytest.mark.skipif(
    not NATIVE,
    reason="native PostgreSQL only: the PGlite development database serialises every transaction behind "
    "one process lock and serves one socket connection, so a pooler, a server restart and simultaneous "
    "writers cannot be exercised there (run scripts/run.py test --native)",
)
needs_pooler = pytest.mark.skipif(
    not (POOLER and POOLER_ADMIN_DSN),
    reason="run with scripts/run.py test --native --pooler pgbouncer: the API is connected directly, "
    "so there is no transaction-mode pooler to qualify",
)
needs_restart_commands = pytest.mark.skipif(
    not (STOP_COMMAND and START_COMMAND),
    reason="set IMPACT_DB_STOP_COMMAND and IMPACT_DB_START_COMMAND to commands that stop and start the "
    "suite's own PostgreSQL cluster (for example pg_ctl on a private initdb cluster); the runner never "
    "restarts a server it does not own and CI's service container cannot be restarted from the job",
)


# -- helpers ---------------------------------------------------------------------------------------


def api_log_since(live, offset):
    log = live.local / "api.log"
    with log.open("rb") as handle:
        handle.seek(offset)
        return handle.read().decode(errors="replace")


def log_offset(live):
    log = live.local / "api.log"
    return log.stat().st_size if log.exists() else 0


def pooler_rows(statement):
    """One admin-console statement (simple query protocol: no parameters, text results)."""
    with psycopg.connect(
        POOLER_ADMIN_DSN, autocommit=True, prepare_threshold=None, row_factory=dict_row
    ) as c:
        return c.execute(statement).fetchall()


def pool_counters():
    pools = {
        r["user"]: r
        for r in pooler_rows("SHOW POOLS")
        if r["database"] != "pgbouncer" and r["user"] in {"impact_app_login", "impact_identity_login"}
    }
    stats = {r["database"]: r for r in pooler_rows("SHOW STATS")}
    return pools, stats


def envelope(response, reason):
    assert response.status_code == 503, response.text
    body = response.json()
    assert body["code"] == "SERVICE_UNAVAILABLE" and body["retryable"] is True, body
    assert body.get("reason_code") == reason, body
    assert "Traceback" not in response.text and "psycopg" not in response.text
    return body


def run_command(command, timeout=90):
    completed = subprocess.run(shlex.split(command), capture_output=True, text=True, timeout=timeout)
    assert completed.returncode == 0, (command, completed.stdout[-800:], completed.stderr[-800:])
    return completed


def database_up(live):
    try:
        with live.db() as c:
            c.execute("SELECT 1").fetchone()
        return True
    except psycopg.OperationalError:
        return False


# -- connection pooler -----------------------------------------------------------------------------


@needs_pooler
def test_native_pooler_transaction_mode_is_in_front_of_the_api(live):
    """The pooler is really in transaction mode and the API's own connections go through it: the
    suite configuration names the pooler's port, the console lists the pooled logins, and every
    later request of this module is served through at most POOL_SIZE server connections per login."""
    config = {r["key"]: r["value"] for r in pooler_rows("SHOW CONFIG")}
    assert config["pool_mode"] == "transaction"
    assert int(config["default_pool_size"]) == POOL_SIZE
    assert str(config["listen_port"]) in live.config["app_dsn"]
    assert str(config["listen_port"]) in live.config["identity_dsn"]
    assert str(config["listen_port"]) in live.config["platform_dsn"]
    expect(live.request(live.path("programmes") + "?limit=5"), 200)
    pools, _ = pool_counters()
    assert "impact_app_login" in pools, pools
    for user, row in pools.items():
        servers = sum(int(row[k]) for k in ["sv_active", "sv_idle", "sv_used", "sv_tested", "sv_login"])
        assert servers <= POOL_SIZE, (user, row)


@needs_pooler
def test_native_pooler_many_clients_share_few_server_connections_with_tenant_context_kept(live):
    """Thirty-two concurrent clients, each on its own TCP connection, mix tenant A writes with
    tenant A and tenant B reads. Every response is the expected one, tenant B never sees tenant A's
    rows (the RLS fence is transaction-local set_config, which must not leak between the
    transactions a server connection serves one after another), the console shows more
    transactions than server connections ever existed, and no pool exceeded its size."""
    tenant_b = live.fixture["tenant_b"]
    _, stats_before = pool_counters()
    before = int(stats_before[list(stats_before)[0]]["total_xact_count"])
    titles = ["Pooled write " + str(uuid.uuid4()) for _ in range(16)]
    calls = []
    for title in titles:
        calls.append(
            sender(live, live.token("author"), "POST", live.path("programmes"), cmd({"title": title}))
        )
        calls.append(sender(live, live.token("author"), "GET", live.path("programmes") + "?limit=100"))
        calls.append(
            sender(
                live,
                live.token("other_tenant"),
                "GET",
                live.path("programmes", tenant=tenant_b) + "?limit=100",
            )
        )
    results = race(*calls, timeout=120)
    writes, reads_a, reads_b = results[0::3], results[1::3], results[2::3]
    assert [r["status"] for r in writes] == [201] * len(titles), writes
    assert all(r["status"] == 200 for r in reads_a + reads_b), results
    assert {r["body"]["business_state"] for r in writes} == {"Draft"}
    seen_b = {item["data"].get("title") for r in reads_b for item in r["body"]["items"]}
    assert not (seen_b & set(titles)), "tenant B read tenant A's programme through a pooled connection"
    with live.db() as c:
        assert c.execute(
            "SELECT count(*) AS n FROM impact.programme_current WHERE tenant_id=%s AND title=ANY(%s)",
            (live.fixture["tenant_a"], titles),
        ).fetchone()["n"] == len(titles)
    pools, stats_after = pool_counters()
    after = int(stats_after[list(stats_after)[0]]["total_xact_count"])
    assert after - before >= len(calls), (before, after)
    for user, row in pools.items():
        servers = sum(int(row[k]) for k in ["sv_active", "sv_idle", "sv_used", "sv_tested", "sv_login"])
        assert servers <= POOL_SIZE, (user, row)
    # Assignments: pgbouncer 1.21+ counts every hand-over of a server connection to a client.
    row = stats_after[list(stats_after)[0]]
    if "total_server_assignment_count" in row:
        assert int(row["total_server_assignment_count"]) >= len(calls)


@needs_pooler
def test_native_pooler_keeps_receipts_cursors_and_the_transaction_scoped_tenant_lock(live):
    """Through the pooler: an exact retry replays the one receipt (same operation, same payload), a
    different payload on the same identifier is refused, a signed listing cursor minted in one
    transaction is honoured in a later one (served by whichever server connection is free), and a
    write queues behind the tenant advisory lock held by a direct connection — the lock is
    transaction-scoped, so it is seen by every server connection and released with the holder."""
    tenant = live.fixture["tenant_a"]
    token = live.token("author")
    body = cmd({"title": "Pooled receipt " + str(uuid.uuid4()), "code": "POOL"})
    path = live.path("programmes")
    first = sender(live, token, "POST", path, body)()
    again = sender(live, token, "POST", path, body)()
    assert first["status"] == 201 and again["body"] == first["body"]
    assert receipts(live, tenant, body["operation_id"]) == 1
    assert revisions(live, tenant, first["body"]["object_id"]) == 1
    changed = sender(live, token, "POST", path, {**body, "data": {**body["data"], "title": "Changed"}})()
    assert changed["status"] == 409 and changed["body"]["code"] == "CONFLICT_OPERATION"
    page = expect(live.request(path + "?limit=2"), 200)
    assert page.get("next_cursor"), "the suite holds more than two programmes"
    following = expect(live.request(path + "?limit=2&cursor=" + page["next_cursor"]), 200)
    assert following["items"] and following["items"][0]["object_id"] != page["items"][0]["object_id"]
    queued = cmd({"title": "Pooled write behind the tenant lock " + str(uuid.uuid4())})
    with ThreadPoolExecutor(max_workers=2) as pool:
        with live.db() as holder:
            holder.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            write = pool.submit(sender(live, token, "POST", path, queued))
            time.sleep(0.8)
            assert not write.done(), "the pooled write must wait for the tenant advisory lock"
            read = sender(live, token, "GET", path + "?limit=3")()
            assert read["status"] == 200 and read["seconds"] < 2.5
            holder.rollback()
        result = write.result(timeout=15)
    assert result["status"] == 201 and receipts(live, tenant, queued["operation_id"]) == 1


@needs_pooler
def test_native_pooler_worker_process_delivers_through_the_pooler(live):
    """The worker's provisioned login is pooled too: a worker subprocess passes its login check
    (current_user and role membership are per server connection, which the pooler keeps per
    login), heartbeats, and delivers one intent exactly once."""
    from test_worker import deliveries, invitation

    process = start(live, "pooled-worker-" + uuid.uuid4().hex[:6], poll_seconds="0.3")
    try:
        wait_for(
            lambda: heartbeat(live, process.name) and heartbeat(live, process.name)["state"] == "RUNNING"
        )
        _, receipt = invitation(live)
        wait_for(lambda: deliveries(live, receipt["object_id"])[0]["state"] == "SENT", timeout=60)
        [row] = deliveries(live, receipt["object_id"])
        assert row["attempts"] == 1 and row["sent_at"]
        assert process.poll() is None
    finally:
        stop(process)
    log = process.log.read_text()
    assert "WORKER_LOGIN_TOPOLOGY" not in log and "PRIVILEGED_WORKER_CONNECTION" not in log, log[-1500:]


# -- database restart ------------------------------------------------------------------------------


@needs_restart_commands
def test_native_database_restart_api_and_worker_recover_without_restart_and_receipts_hold(live):
    """Stop the cluster between requests, then start it again. While it is down: readiness and
    every request answer 503 DATABASE_UNAVAILABLE with the envelope and liveness stays 200; nothing
    is logged as a traceback. After the start: the same API process (never restarted) is ready
    again, objects written before the stop are still there with their receipts, the write refused
    during the outage commits exactly once when retried with the same operation identifier (and
    its exact replay returns the same receipt), and the worker subprocess started before the stop
    is still alive, logged the refused iterations and beats again."""
    tenant = live.fixture["tenant_a"]
    offset = log_offset(live)
    worker = start(live, "restart-worker-" + uuid.uuid4().hex[:6], poll_seconds="0.3")
    beat_before = None
    worker_alive = False
    downtime = None
    try:
        wait_for(lambda: heartbeat(live, worker.name) and heartbeat(live, worker.name)["state"] == "RUNNING")
        before_body = cmd(draft(live))
        kept = expect(live.request(live.path("observations"), method="POST", body=before_body), 201)
        refused_body = cmd(draft(live))
        beat_before = heartbeat(live, worker.name)["beat_at"]
        expect(live.client.get("/health/ready"), 200)

        run_command(STOP_COMMAND)
        assert not database_up(live)
        downtime_started = time.monotonic()
        # Directly connected, a stopped server refuses at once; behind a transaction pooler the
        # TCP connect succeeds and each attempt waits its connect_timeout (5 s) for a server, so the
        # first refusal can take readiness's three connections' worth. A long client timeout
        # measures that instead of hiding it.
        probe = httpx.Client(base_url=str(live.client.base_url), trust_env=False, timeout=90)
        headers = {"Authorization": "Bearer " + live.token("author")}
        t = time.monotonic()
        envelope(probe.get("/health/ready"), "DATABASE_UNAVAILABLE")
        seconds_to_first_503 = round(time.monotonic() - t, 1)
        expect(probe.get("/health/live"), 200)
        t = time.monotonic()
        envelope(probe.get(live.path("observations") + "?limit=3", headers=headers), "DATABASE_UNAVAILABLE")
        seconds_to_read_503 = round(time.monotonic() - t, 1)
        envelope(
            probe.get(live.path("observations", kept["object_id"]), headers=headers), "DATABASE_UNAVAILABLE"
        )
        envelope(
            probe.post(live.path("observations"), json=refused_body, headers=headers), "DATABASE_UNAVAILABLE"
        )
        # Long enough for the worker to attempt at least a few iterations against the stopped server.
        time.sleep(2)
        assert worker.poll() is None, "the worker process must survive the outage"

        run_command(START_COMMAND)
        wait_for(lambda: database_up(live), timeout=60)
        downtime = round(time.monotonic() - downtime_started, 1)
        # Behind a pooler the server connections it lost are retried on its own schedule
        # (server_login_retry), so readiness may stay 503 for a moment after the server is back.
        t = time.monotonic()
        wait_for(lambda: probe.get("/health/ready").status_code == 200, timeout=90, interval=0.5)
        seconds_to_ready = round(time.monotonic() - t, 1)
        # Behind a pooler, readiness answering 200 does not mean every pooled server connection is
        # alive: idle ones that died with the server are handed out unchecked until the pooler's
        # server_check_delay, and their first use fails once with a retryable 503. Directly
        # connected, the first read succeeds at once.
        t = time.monotonic()
        attempts = {"n": 0}

        def read_back():
            attempts["n"] += 1
            return probe.get(live.path("observations", kept["object_id"]), headers=headers).status_code == 200

        wait_for(read_back, timeout=30, interval=0.5)
        read_attempts_after_ready = attempts["n"]
        seconds_to_read_after_ready = round(time.monotonic() - t, 1)
        if not POOLER:
            assert read_attempts_after_ready == 1
        probe.close()
    finally:
        if not database_up(live):
            run_command(START_COMMAND)
            wait_for(lambda: database_up(live), timeout=60)
        worker_alive = worker.poll() is None
        if beat_before is not None and worker_alive:
            wait_for(
                lambda: (
                    heartbeat(live, worker.name) and heartbeat(live, worker.name)["beat_at"] > beat_before
                ),
                timeout=30,
            )
        stop(worker)
    assert worker_alive
    # Persistence and receipts: the earlier write and its receipt survived the restart.
    assert (
        expect(live.request(live.path("observations", kept["object_id"])), 200)["revision_id"]
        == kept["revision_id"]
    )
    assert expect(live.request(live.path("observations"), method="POST", body=before_body), 201) == kept
    assert receipts(live, tenant, before_body["operation_id"]) == 1
    # The write refused during the outage never committed; its retry commits exactly once.
    assert receipts(live, tenant, refused_body["operation_id"]) == 0
    created = expect(live.request(live.path("observations"), method="POST", body=refused_body), 201)
    replay = expect(live.request(live.path("observations"), method="POST", body=refused_body), 201)
    assert replay == created and receipts(live, tenant, refused_body["operation_id"]) == 1
    assert revisions(live, tenant, created["object_id"]) == 1
    # The worker saw the outage and recovered; the heartbeat row is RUNNING again after the start
    # and STOPPED only because the test stopped it.
    # Directly connected, a stopped server refuses the connection (OperationalError); behind
    # PgBouncer the client connects and the pooler answers the startup with an error of its own
    # (SQLSTATE 08P01, ProtocolViolation). Both are psycopg.Error, which the worker loop catches.
    worker_log = worker.log.read_text()
    refused_classes = sorted(set(re.findall(r"worker iteration failed class=(\w+)", worker_log)))
    assert refused_classes and set(refused_classes) <= {"OperationalError", "ProtocolViolation"}, worker_log[
        -2000:
    ]
    assert "Traceback" not in worker_log, worker_log[-2000:]
    final = heartbeat(live, worker.name)
    assert final["state"] == "STOPPED" and final["beat_at"] > beat_before
    appended = api_log_since(live, offset)
    assert "Traceback" not in appended and "unexpected failure" not in appended, appended[-3000:]
    (live.local / "database-restart.json").write_text(
        json.dumps(
            {
                "topology": POOLER or "direct",
                "downtime_seconds": downtime,
                "seconds_to_first_503_readiness": seconds_to_first_503,
                "seconds_to_read_503": seconds_to_read_503,
                "seconds_to_ready_after_start": seconds_to_ready,
                "read_attempts_after_ready": read_attempts_after_ready,
                "seconds_to_read_after_ready": seconds_to_read_after_ready,
                "worker_survived": worker_alive,
                "worker_refused_classes": refused_classes,
            },
            indent=2,
        )
        + "\n"
    )


# -- lock order across objects ---------------------------------------------------------------------


def new_source(indicator):
    """A create command for one more MANUAL source of the indicator: after the close preview it
    makes the preview stale (an unplanned value is a close blocker), before the lock it is a draft
    outside the snapshot."""
    return cmd(
        {
            "source_namespace": "MANUAL",
            "source_key": "late-" + str(uuid.uuid4()),
            "indicator_id": indicator["object_id"],
            "event_at": "2026-08-15T12:00:00Z",
            "captured_at": "2026-08-15T13:00:00Z",
            "capture_zone": "UTC",
            "value_state": "PRESENT",
            "value": "10",
            "source_version": "1",
            "dimension_values": {},
        }
    )


def approval(workflow, reason):
    return cmd(
        {"candidate_revision": workflow["data"]["candidate_revision"], "reason": reason},
        workflow["revision_id"],
    )


def restatement(live, programme, period, rows):
    template = get(live, "workflow-templates")["items"][0]
    return cmd(
        {
            "workflow_version": template["revision_id"],
            "programme_id": programme["object_id"],
            "reason": "Raced restatement request.",
            "source_ids": [rows[0]["object_id"]],
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        },
        period["revision_id"],
    )


def snapshot_bindings(live, tenant, programme, period):
    with live.db() as c:
        return c.execute(
            "SELECT snapshot_version,snapshot_id FROM impact.period_snapshot_binding WHERE tenant_id=%s AND programme_id=%s AND period_id=%s ORDER BY snapshot_version",
            (tenant, programme["object_id"], period["object_id"]),
        ).fetchall()


def programme_period_state(live, tenant, programme, period):
    """The governed programme-period state (Open when no row exists yet); the calendar Period
    object itself stays Open through a close."""
    with live.db() as c:
        row = c.execute(
            "SELECT lifecycle_state FROM impact.programme_period_state WHERE tenant_id=%s AND programme_id=%s AND period_id=%s",
            (tenant, programme["object_id"], period["object_id"]),
        ).fetchone()
    return row["lifecycle_state"] if row else "Open"


def snapshot_member_revisions(live, tenant, snapshot_id):
    with live.db() as c:
        rows = c.execute(
            "SELECT * FROM impact.official_result_snapshot WHERE tenant_id=%s AND snapshot_id=%s",
            (tenant, snapshot_id),
        ).fetchall()
    return rows


@pytest.mark.parametrize("repetition,mode", list(enumerate(RACE_MODES)))
def test_native_close_new_source_and_restatement_released_together_never_deadlock(live, repetition, mode):
    """Three writers of one tenant released together against one programme period, each entering
    the write path through a different object: the independent approval of the period-close review
    (workflow -> close job -> period state, snapshot, official results), the creation of one more
    source observation of a closing indicator (a new object whose existence makes the close
    preview stale), and a restatement request on the period. The tenant advisory lock admits them
    one at a time, so the pair that matters has two orders: close first locks the period once and
    the new source lands afterwards as a draft outside the snapshot; new source first makes the
    preview stale, so the close review is refused PERIOD_CLOSE_PREVIEW_STALE and the period stays
    Open. The restatement needs a locked snapshot (LOCKED_SNAPSHOT_REQUIRED while Open) and may
    open one against the fresh lock otherwise. Nothing deadlocks: the database's deadlock counter
    is unchanged and no 40P01, database-failure or unexpected-failure line reaches the API log.
    Two unbiased releases, then one per forced order (a head start for the other writers); each
    repetition's mode and observed order are recorded in <local>/lock-order-races.json."""
    tenant = live.fixture["tenant_a"]
    programme, indicator, _, period, rows, _ = complete_period(live, measurement_builder(live))
    close_workflow = request_close(live, programme, period)
    period = get(live, "periods", period["object_id"])
    bodies = {
        "close": approval(close_workflow, "Independent close review (raced)."),
        "source": new_source(indicator),
        "restate": restatement(live, programme, period, rows),
    }
    paths = {
        "close": live.path("workflows", close_workflow["object_id"]) + "/actions/approve",
        "source": live.path("observations"),
        "restate": live.path("periods", period["object_id"]) + "/actions/restate",
    }
    actors = {"close": "reviewer", "source": "author", "restate": "author"}
    for actor in set(actors.values()):
        live.token(actor)
    offset = log_offset(live)
    deadlocks_before = deadlocks(live)
    names = ["close", "source", "restate"]
    head_start = {
        "race": None,
        "close_first": (0, RACE_HEAD_START_SECONDS, RACE_HEAD_START_SECONDS),
        "source_first": (RACE_HEAD_START_SECONDS, 0, RACE_HEAD_START_SECONDS),
    }[mode]
    results = dict(
        zip(
            names,
            race(
                *[sender(live, live.token(actors[n]), "POST", paths[n], bodies[n]) for n in names],
                delays=head_start,
            ),
        )
    )
    close_r, source_r, restate_r = results["close"], results["source"], results["restate"]
    assert deadlocks(live) == deadlocks_before
    appended = api_log_since(live, offset)
    assert "40P01" not in appended and "database failure" not in appended, appended[-3000:]
    assert "unexpected failure" not in appended, appended[-3000:]
    for name, r in results.items():
        assert r["status"] in {200, 201, 409}, (name, r)
        if r["status"] == 409:
            assert r["body"]["code"] in {"INVALID_STATE", "CONFLICT_VERSION"}, (name, r)
    assert source_r["status"] == 201 and source_r["body"]["business_state"] == "Draft", source_r
    assert receipts(live, tenant, bodies["source"]["operation_id"]) == 1
    bindings = snapshot_bindings(live, tenant, programme, period)
    assert len(bindings) <= 1, bindings
    state_after = programme_period_state(live, tenant, programme, period)
    period_after = get(live, "periods", period["object_id"])
    assert period_after["lifecycle_state"] == "Open", "the calendar period object stays Open through a lock"
    source_after = get(live, "observations", source_r["body"]["object_id"])
    assert source_after["lifecycle_state"] == "Draft"
    if close_r["status"] == 200:
        # The close was admitted first: the period is locked exactly once, the new source is a
        # draft outside the snapshot, and the restatement either opened against the fresh lock or
        # was refused.
        order = "close_first"
        assert close_r["body"]["business_state"] == "Approved"
        assert [b["snapshot_version"] for b in bindings] == [1]
        members = snapshot_member_revisions(live, tenant, bindings[0]["snapshot_id"])
        assert members, "the locked snapshot holds the official results"
        assert source_after["revision_id"] not in json.dumps(members, default=str)
        # A restatement request is itself reviewed: admitted after the lock it opens a workflow
        # (InReview) and the state stays Locked until an independent approval; admitted before the
        # close it was refused for the open period and may be requested again now.
        assert state_after == "Locked", state_after
        if restate_r["status"] == 200:
            assert restate_r["body"]["business_state"] == "InReview", restate_r
            assert receipts(live, tenant, bodies["restate"]["operation_id"]) == 1
        else:
            assert restate_r["body"]["reason_code"] == "LOCKED_SNAPSHOT_REQUIRED", restate_r
            assert receipts(live, tenant, bodies["restate"]["operation_id"]) == 0
        assert receipts(live, tenant, bodies["close"]["operation_id"]) == 1
    else:
        # The new source was admitted first: the preview is stale, so the close review is refused
        # and the period stays open with no snapshot; a restatement needs a locked snapshot.
        order = "source_first"
        assert close_r["body"]["reason_code"] == "PERIOD_CLOSE_PREVIEW_STALE", close_r
        assert bindings == [] and state_after == "Open"
        assert restate_r["status"] == 409 and restate_r["body"]["reason_code"] == "LOCKED_SNAPSHOT_REQUIRED"
        assert receipts(live, tenant, bodies["close"]["operation_id"]) == 0
        assert receipts(live, tenant, bodies["restate"]["operation_id"]) == 0
        assert get(live, "workflows", close_workflow["object_id"])["lifecycle_state"] == "InReview"
    # Stable afterwards: the exact retry of every command replays its receipt or is refused the
    # same way, and nothing moves — except a restatement refused before a close that then
    # happened, which is a fresh request against the now-locked period (one receipt either way).
    retries = {}
    for name in names:
        again = sender(live, live.token(actors[name]), "POST", paths[name], bodies[name])()
        retries[name] = again["status"]
        if results[name]["status"] in {200, 201}:
            assert again["body"] == results[name]["body"], (name, again)
        elif name == "restate" and order == "close_first":
            assert again["status"] in {200, 409}, again
            assert receipts(live, tenant, bodies["restate"]["operation_id"]) == (again["status"] == 200)
        else:
            assert again["status"] == 409, (name, again)
    assert snapshot_bindings(live, tenant, programme, period) == bindings
    assert programme_period_state(live, tenant, programme, period) == state_after
    if mode != "race":
        assert order == mode, (mode, order)
    recorded = live.local / RACE_FILE
    data = json.loads(recorded.read_text()) if recorded.exists() else {}
    data[str(repetition)] = {
        "mode": mode,
        "order": order,
        "statuses": {n: results[n]["status"] for n in names},
        "reason_codes": {
            n: results[n]["body"].get("reason_code") or results[n]["body"].get("code") for n in names
        },
        "seconds": {n: results[n]["seconds"] for n in names},
        "programme_period_state_after": state_after,
        "retry_statuses": retries,
    }
    recorded.write_text(json.dumps(data, indent=2) + "\n")


def test_native_opposite_order_writers_on_two_objects_serialise_on_the_tenant_lock(live):
    """Two writers that each touch two of the same objects in opposite order (A then B, B then A)
    cannot interleave: a patch of programme P followed by a patch of indicator definition D on one
    thread, and D then P on another, repeated with fresh revisions, always complete with 200 and
    the expected-revision check never trips, because each command holds the tenant advisory lock
    for its whole transaction. Twenty rounds, no deadlock, no 40P01."""
    from test_measurement import create
    from test_measurement_unit import definition

    tenant = live.fixture["tenant_a"]
    programme = create(live, "programmes", {"title": "Lock order P " + str(uuid.uuid4()), "code": "LOP"})
    saved = create(live, "indicator-definitions", definition(code="LOD"))
    token = live.token("author")
    heads = {"P": programme["revision_id"], "D": saved["revision_id"]}
    lock = threading.Lock()
    deadlocks_before = deadlocks(live)
    offset = log_offset(live)
    statuses = []

    def patch(kind, label):
        path = (
            live.path("programmes", programme["object_id"])
            if kind == "P"
            else live.path("indicator-definitions", saved["object_id"])
        )
        for _ in range(20):
            with lock:
                head = heads[kind]
            body = cmd({"title": label} if kind == "P" else {"name": label}, head)
            with httpx.Client(base_url=str(live.client.base_url), trust_env=False, timeout=30) as client:
                response = client.request(
                    "PATCH", path, json=body, headers={"Authorization": "Bearer " + token}
                )
            statuses.append((kind, response.status_code, response.json().get("code")))
            if response.status_code == 200:
                with lock:
                    heads[kind] = response.json()["revision_id"]
                return response.json()
            assert response.status_code == 409 and response.json()["code"] == "CONFLICT_VERSION", (
                response.text
            )
        raise AssertionError("twenty stale retries on " + kind)

    def writer(order, number):
        for round_number in range(10):
            label = f"Lock order {order} {number} round {round_number}"
            for kind in order:
                patch(kind, label)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(writer, "PD", 1), pool.submit(writer, "DP", 2)]
        for future in futures:
            future.result(timeout=240)
    assert deadlocks(live) == deadlocks_before
    appended = api_log_since(live, offset)
    assert "40P01" not in appended and "database failure" not in appended, appended[-3000:]
    successes = [s for s in statuses if s[1] == 200]
    assert len(successes) == 40, statuses
    assert revisions(live, tenant, programme["object_id"]) == 21
    assert revisions(live, tenant, saved["object_id"]) == 21
