"""Native PostgreSQL only: the worker as a real subprocess on its own provisioned login
(impact_worker_login -> impact_worker, IMPACT_REQUIRE_UNPRIVILEGED_DB). Races between two worker
processes, lease takeover while the first holder is still sending, SIGTERM, the login topology
refusal and 'no transaction open during the SMTP conversation' observed from pg_stat_activity."""

import json
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from psycopg.rows import dict_row

from impact_api.worker import Worker, empty_summary
from smtp_sink import SmtpSink
from test_worker import deliveries, invitation, settings

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Native PostgreSQL only: needs the provisioned worker login and real concurrent connections",
)


def wait_for(condition, timeout=30, interval=0.2):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = condition()
        if value:
            return value
        time.sleep(interval)
    raise AssertionError("Condition not met within " + str(timeout) + " s")


def start(live, name, **overrides):
    """One `python -m impact_api.worker` process: its configuration file, a few overrides, and no
    other IMPACT_* variable, connection string or libpq variable from the test environment."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("IMPACT_", "PG"))}
    env.update(
        PYTHONPATH=str(ROOT / "apps/api"),
        IMPACT_WORKER_CONFIG_FILE=str(live.local / "worker.json"),
        IMPACT_POLL_SECONDS="0.3",
        IMPACT_SYNTHETIC_SINK=str(live.local / (name + "-mail.jsonl")),
    )
    env.update({"IMPACT_" + key.upper(): str(value) for key, value in overrides.items()})
    log = live.local / (name + ".log")
    process = subprocess.Popen(
        [sys.executable, "-m", "impact_api.worker", "--worker-id", name],
        cwd=ROOT,
        env=env,
        stdout=open(log, "w"),
        stderr=subprocess.STDOUT,
    )
    process.log, process.sink, process.name = log, Path(env["IMPACT_SYNTHETIC_SINK"]), name
    return process


def stop(process, timeout=20):
    if process.poll() is None:
        process.send_signal(signal.SIGTERM)
    return process.wait(timeout=timeout)


def sink(process):
    return (
        [json.loads(line) for line in process.sink.read_text().splitlines()] if process.sink.exists() else []
    )


def heartbeat(live, worker_id):
    with live.db() as c:
        return c.execute("SELECT * FROM impact.worker_heartbeat WHERE worker_id=%s", (worker_id,)).fetchone()


def drain(live):
    """Deliver whatever earlier tests left due, so a test's own rows are the only due rows."""
    Worker(settings(live), worker_id="native-drain-" + uuid4().hex[:8]).run_once()


def test_native_worker_process_sends_over_smtp_with_no_transaction_open(live):
    drain(live)
    observed = []

    def during_data():
        with psycopg.connect(os.environ["IMPACT_FIXTURE_DSN"], row_factory=dict_row) as c:
            observed.append(
                c.execute(
                    "SELECT state,xact_start FROM pg_stat_activity WHERE usename='impact_worker_login'"
                ).fetchall()
            )

    with SmtpSink(on_data=during_data) as smtp:
        name = "native-smtp-" + uuid4().hex[:6]
        process = start(live, name, email_adapter="smtp", smtp_port=smtp.port, smtp_timeout=5)
        try:
            email, receipt = invitation(live)
            wait_for(lambda: deliveries(live, receipt["object_id"])[0]["state"] == "SENT")
            [message] = wait_for(lambda: smtp.for_recipient(email))
            running = wait_for(lambda: heartbeat(live, name))
            assert running["state"] == "RUNNING" and running["build"] == "0.16.0"
        finally:
            code = stop(process)
    assert code == 0
    assert observed and all(rows == [] for rows in observed), observed
    [row] = deliveries(live, receipt["object_id"])
    assert (row["attempts"], row["lease_generation"], row["lease_owner"]) == (1, 1, None)
    assert message["message"]["X-Impact-Delivery"] == str(row["event_id"])
    stopped = heartbeat(live, name)
    assert stopped["state"] == "STOPPED" and stopped["stopped_at"]
    assert "@example.test" not in process.log.read_text()


def test_native_two_worker_processes_never_deliver_the_same_row(live):
    drain(live)
    receipts = [invitation(live)[1] for _ in range(12)]
    events = {str(deliveries(live, r["object_id"])[0]["event_id"]) for r in receipts}
    workers = [
        start(live, "native-race-" + suffix + "-" + uuid4().hex[:6], batch_size=3, synthetic_delay=0.1)
        for suffix in ["a", "b"]
    ]
    try:
        wait_for(
            lambda: all(deliveries(live, r["object_id"])[0]["state"] == "SENT" for r in receipts), timeout=60
        )
    finally:
        codes = [stop(w) for w in workers]
    assert codes == [0, 0]
    sent = [m["event_id"] for w in workers for m in sink(w) if m["event_id"] in events]
    assert sorted(sent) == sorted(events)
    for receipt in receipts:
        [row] = deliveries(live, receipt["object_id"])
        assert (row["attempts"], row["lease_generation"]) == (1, 1)


def test_native_simultaneous_claims_are_disjoint(live):
    drain(live)
    receipts = [invitation(live)[1] for _ in range(8)]
    events = {str(deliveries(live, r["object_id"])[0]["event_id"]) for r in receipts}
    tenant = live.fixture["tenant_a"]
    barrier = threading.Barrier(2)
    claims = {}

    def claim(name):
        worker = Worker(settings(live, batch_size=100), worker_id=name)
        barrier.wait()
        claims[name] = {str(r["event_id"]) for r in worker.claim(tenant, empty_summary())}

    threads = [threading.Thread(target=claim, args=("native-claim-" + s,)) for s in ["a", "b"]]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(30)
    a, b = claims.values()
    assert not (a & b) and events <= (a | b)
    with live.db() as c:
        owners = c.execute(
            "SELECT lease_owner,lease_generation FROM impact.outbox_delivery WHERE event_id=ANY(%s::uuid[])",
            (list(events),),
        ).fetchall()
    assert {r["lease_generation"] for r in owners} == {1}
    assert len({r["lease_owner"] for r in owners}) >= 1


def test_native_lease_takeover_while_the_first_holder_is_sending(live):
    drain(live)
    email, receipt = invitation(live)
    [row] = deliveries(live, receipt["object_id"])
    slow = start(
        live,
        "native-slow-" + uuid4().hex[:6],
        lease_seconds=5,
        smtp_timeout=2,
        synthetic_delay=8,
        batch_size=1,
    )
    try:
        wait_for(lambda: deliveries(live, receipt["object_id"])[0]["state"] == "LEASED", timeout=20)
        time.sleep(5.5)
        rival = Worker(settings(live, lease_seconds=30), worker_id="native-rival-" + uuid4().hex[:6])
        summary = rival.run_once()
        assert summary["sent"] >= 1
        taken = deliveries(live, receipt["object_id"])[0]
        assert (taken["state"], taken["lease_generation"], taken["attempts"]) == ("SENT", 2, 2)
        # The first holder finishes its send afterwards; its outcome is refused by generation.
        wait_for(lambda: "lease generation superseded" in slow.log.read_text(), timeout=20)
    finally:
        assert stop(slow) == 0
    final = deliveries(live, receipt["object_id"])[0]
    assert (final["state"], final["lease_generation"], final["attempts"]) == ("SENT", 2, 2)
    # Email delivery is at least once: both holders handed the message to their adapter.
    assert [m["to"] for m in sink(slow) if m["event_id"] == str(row["event_id"])] == [email]
    assert (
        len(
            [
                line
                for line in Path(rival.s.synthetic_sink).read_text().splitlines()
                if str(row["event_id"]) in line
            ]
        )
        == 1
    )


def test_native_sigterm_finishes_the_current_send_and_releases_the_rest(live):
    drain(live)
    receipts = [invitation(live)[1] for _ in range(4)]
    events = [str(deliveries(live, r["object_id"])[0]["event_id"]) for r in receipts]
    name = "native-term-" + uuid4().hex[:6]
    process = start(live, name, batch_size=10, synthetic_delay=3, lease_seconds=60)
    wait_for(
        lambda: all(deliveries(live, r["object_id"])[0]["state"] == "LEASED" for r in receipts), timeout=20
    )
    time.sleep(0.5)
    started = time.monotonic()
    assert stop(process) == 0
    assert time.monotonic() - started < 10
    rows = {
        str(deliveries(live, r["object_id"])[0]["event_id"]): deliveries(live, r["object_id"])[0]
        for r in receipts
    }
    sent = [e for e in events if rows[e]["state"] == "SENT"]
    released = [e for e in events if rows[e]["state"] == "PENDING"]
    assert len(sent) == 1 and len(released) == 3
    for event in released:
        assert rows[event]["lease_owner"] is None and rows[event]["attempts"] == 0
    assert [m["event_id"] for m in sink(process)] == sent
    assert heartbeat(live, name)["state"] == "STOPPED"
    drain(live)
    assert all(deliveries(live, r["object_id"])[0]["state"] == "SENT" for r in receipts)


def test_native_worker_refuses_a_privileged_or_foreign_login(live):
    runs = {}
    for label, dsn in [
        ("superuser", os.environ["IMPACT_FIXTURE_DSN"]),
        ("app", os.environ["IMPACT_LOGIN_DSN_APP"]),
        ("worker", os.environ["IMPACT_LOGIN_DSN_WORKER"]),
    ]:
        once = subprocess.run(
            [sys.executable, "-m", "impact_api.worker", "--once", "--worker-id", "native-once-" + label],
            cwd=ROOT,
            env={
                **{k: v for k, v in os.environ.items() if not k.startswith(("IMPACT_", "PG"))},
                "PYTHONPATH": str(ROOT / "apps/api"),
                "IMPACT_WORKER_CONFIG_FILE": str(live.local / "worker.json"),
                "IMPACT_WORKER_DSN": dsn,
                "IMPACT_SYNTHETIC_SINK": str(live.local / "native-once-mail.jsonl"),
            },
            capture_output=True,
            text=True,
            timeout=60,
        )
        runs[label] = once
    assert runs["superuser"].returncode == 3 and "PRIVILEGED_WORKER_CONNECTION" in runs["superuser"].stderr
    assert runs["app"].returncode == 3 and "WORKER_LOGIN_TOPOLOGY" in runs["app"].stderr
    assert runs["worker"].returncode == 0, runs["worker"].stderr
    assert json.loads(runs["worker"].stdout.strip().splitlines()[-1])["tenants"] >= 2


def test_native_worker_login_holds_only_the_worker_role(live):
    dsn = os.environ["IMPACT_LOGIN_DSN_WORKER"]
    with psycopg.connect(dsn, row_factory=dict_row) as c:
        row = c.execute(
            "SELECT current_user AS login,rolsuper,rolbypassrls,rolinherit FROM pg_roles WHERE rolname=current_user"
        ).fetchone()
        assert (row["login"], row["rolsuper"], row["rolbypassrls"], row["rolinherit"]) == (
            "impact_worker_login",
            False,
            False,
            False,
        )
        # NOINHERIT: nothing is readable until the privilege role is assumed.
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            c.execute("SELECT 1 FROM impact.outbox_delivery LIMIT 1")
    for role in ["impact_app", "impact_identity", "impact_platform", "impact_owner"]:
        with psycopg.connect(dsn) as c:
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                c.execute("SET LOCAL ROLE " + role)
    with psycopg.connect(dsn, row_factory=dict_row) as c:
        c.execute("SET LOCAL ROLE impact_worker")
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        tenants = {
            str(r["tenant_id"]) for r in c.execute("SELECT DISTINCT tenant_id FROM impact.outbox_delivery")
        }
        assert tenants <= {live.fixture["tenant_a"]}
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.notification_current WHERE tenant_id=%s",
                (live.fixture["tenant_b"],),
            ).fetchone()["n"]
            == 0
        )
