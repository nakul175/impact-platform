"""Worker runtime and outbox dispatcher (v0.16), with the worker invoked in-process one iteration
or one step at a time, with a test-only skew added to the database clock. On PGlite the worker connects through the fixture
connection and assumes impact_worker; under the native runner it uses the provisioned
impact_worker_login with IMPACT_REQUIRE_UNPRIVILEGED_DB. Real subprocesses, races and signals are
in test_native_worker.py."""
# ruff: noqa: F811

import json
import os
import random
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from jsonschema import Draft202012Validator, FormatChecker
from psycopg.pq import TransactionStatus
from psycopg.rows import dict_row

from impact_api.delivery import channel_code, invitation_token as derive_token
from impact_api.recovery_contracts import RECEIPT as CONTACT_RECEIPT
from impact_api.worker import (
    BACKOFF_BASE_SECONDS,
    ConfigurationError,
    DeliveryError,
    SmtpAdapter,
    SyntheticAdapter,
    Worker,
    WorkerSettings,
    empty_summary,
)
from impact_api.version import BUILD
from impact_api.worker_contracts import WORKERS
from smtp_sink import SmtpSink
from test_administration import action as admin_action, command, expect, invitation_token, invite
from test_changes import propose
from test_measurement import setup, get, submit, approve, observation, result  # noqa: F401
from test_recovery_contacts import BASE as CONTACTS, action as contact_action, listing, nominate

NATIVE = os.environ.get("IMPACT_NATIVE_TEST") == "1"
ROOT = Path(__file__).resolve().parents[1]


class Clock:
    """The worker's test-only skew: an offset added to the database clock, which the worker uses
    for every lease, due and expiry comparison. `now()` approximates the skewed database time."""

    def __init__(self):
        self.offset = timedelta(0)

    def __call__(self):
        return self.offset

    def now(self):
        return datetime.now(timezone.utc) + self.offset

    def advance(self, **delta):
        self.offset += timedelta(**delta)

    def at(self, instant):
        self.offset = instant - datetime.now(timezone.utc)


def worker_dsn():
    return os.environ["IMPACT_LOGIN_DSN_WORKER"] if NATIVE else os.environ["IMPACT_FIXTURE_DSN"]


def settings(live, **overrides):
    values = {
        "environment": "test",
        "worker_dsn": worker_dsn(),
        "public_origin": live.config["public_origin"],
        "invitation_secret": live.config["invitation_secret"],
        "delivery_secret": live.config["delivery_secret"],
        "email_adapter": "synthetic",
        "synthetic_sink": str(live.local / ("mail-" + uuid4().hex[:8] + ".jsonl")),
        "require_unprivileged_db": NATIVE,
        "batch_size": 100,
        "scan_seconds": 0,
    }
    values.update(overrides)
    s = WorkerSettings(**values)
    s.validate()
    return s


def make_worker(live, clock=None, adapter=None, probe=None, **overrides):
    s = settings(live, **overrides)
    return Worker(
        s, skew=clock or Clock(), adapter=adapter, probe=probe, worker_id="qual-" + uuid4().hex[:12]
    )


def deliveries(live, reference):
    with live.db() as c:
        return c.execute(
            "SELECT d.*,e.payload,e.event_type FROM impact.outbox_delivery d JOIN impact.outbox_event e "
            "USING(tenant_id,event_id) WHERE d.reference_id=%s ORDER BY e.occurred_at,d.event_id",
            (reference,),
        ).fetchall()


def sink_lines(s):
    path = Path(s.synthetic_sink)
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def invitation(live):
    email = "worker-" + uuid4().hex[:10] + "@example.test"
    _, receipt = invite(live, email)
    return email, receipt


def claimed(worker, tenant, event_id):
    rows = worker.claim(tenant, empty_summary())
    return next(row for row in rows if str(row["event_id"]) == str(event_id))


# -- intents ---------------------------------------------------------------------------------------


def test_invitation_intent_holds_no_token_or_address_and_is_sent_once(live):
    email, receipt = invitation(live)
    token = invitation_token(receipt)
    [row] = deliveries(live, receipt["object_id"])
    assert (row["channel"], row["template"], row["state"], row["attempts"]) == (
        "EMAIL",
        "MEMBER_INVITATION",
        "PENDING",
        0,
    )
    assert row["event_type"] == "delivery.requested"
    stored = json.dumps(row, default=str) + bytes(row["recipient_sealed"]).hex()
    for secret in [token, token.split(".")[-1], email, email.split("@")[0]]:
        assert secret not in stored and secret.encode().hex() not in stored
    assert bytes(row["recipient_sealed"]).find(email.encode()) == -1

    worker = make_worker(live)
    summary = worker.run_once()
    assert summary["sent"] >= 1
    [sent] = deliveries(live, receipt["object_id"])
    assert (sent["state"], sent["attempts"], sent["lease_owner"]) == ("SENT", 1, None)
    assert sent["sent_at"] and sent["completed_at"] and sent["last_error_class"] is None
    [message] = [m for m in sink_lines(worker.s) if m["event_id"] == str(row["event_id"])]
    assert message["to"] == email and token in message["body"]
    assert message["subject"] == "Your invitation to an Impact Platform workspace"
    # A second iteration finds nothing due: one message for one intent.
    worker.run_once()
    assert len([m for m in sink_lines(worker.s) if m["event_id"] == str(row["event_id"])]) == 1


def test_resent_or_revoked_invitation_is_superseded_not_sent(live):
    email, receipt = invitation(live)
    resent = expect(
        admin_action(live, "member-invitations", receipt["object_id"], "resend", receipt["revision_id"]), 200
    )
    first, second = deliveries(live, receipt["object_id"])
    assert first["reference_generation"] != second["reference_generation"]
    assert bytes(first["recipient_sealed"]) == bytes(second["recipient_sealed"])
    worker = make_worker(live)
    worker.run_once()
    first, second = deliveries(live, receipt["object_id"])
    assert (first["state"], first["last_error_class"], first["sent_at"]) == (
        "SUPERSEDED",
        "INVITATION_RESENT",
        None,
    )
    assert second["state"] == "SENT"
    [message] = [m for m in sink_lines(worker.s) if m["to"] == email]
    assert invitation_token(resent) in message["body"] and invitation_token(receipt) not in message["body"]

    _, other = invitation(live)
    expect(admin_action(live, "member-invitations", other["object_id"], "revoke", other["revision_id"]), 200)
    worker.run_once()
    [closed] = deliveries(live, other["object_id"])
    assert (closed["state"], closed["last_error_class"]) == ("SUPERSEDED", "INVITATION_CLOSED")


# -- leases, fencing, retries ----------------------------------------------------------------------


def test_lease_takeover_refuses_the_stale_holders_completion(live):
    _, receipt = invitation(live)
    [row] = deliveries(live, receipt["object_id"])
    tenant = live.fixture["tenant_a"]
    clock = Clock()
    first = make_worker(live, clock=clock, lease_seconds=30)
    second = make_worker(live, clock=clock, lease_seconds=30)
    held = claimed(first, tenant, row["event_id"])
    assert held["lease_generation"] == 1 and held["attempts"] == 1
    # While the lease is live nobody else can claim it.
    assert str(row["event_id"]) not in {str(r["event_id"]) for r in second.claim(tenant, empty_summary())}
    clock.advance(seconds=31)
    taken = claimed(second, tenant, row["event_id"])
    assert taken["lease_generation"] == 2 and taken["attempts"] == 2
    summary = empty_summary()
    second.process(tenant, taken, summary)
    assert summary["sent"] == 1
    # The first holder wakes up and reports success: refused by generation, nothing changes.
    late = empty_summary()
    assert first.record(tenant, held, late, "sent", None) is False
    assert late["stale_refused"] == 1
    assert first.record(tenant, held, late, "retry", "SYNTHETIC_FAILURE") is False
    [final] = deliveries(live, receipt["object_id"])
    assert (final["state"], final["lease_generation"], final["attempts"]) == ("SENT", 2, 2)
    assert len([m for m in sink_lines(second.s) if m["event_id"] == str(row["event_id"])]) == 1
    assert sink_lines(first.s) == []


def test_failures_back_off_with_jitter_then_become_dead(live):
    _, receipt = invitation(live)
    [row] = deliveries(live, receipt["object_id"])
    tenant = live.fixture["tenant_a"]
    clock = Clock()
    worker = make_worker(live, clock=clock, max_attempts=3, synthetic_failures=1000)
    for attempt in [1, 2]:
        held = claimed(worker, tenant, row["event_id"])
        started = clock.now()
        worker.process(tenant, held, empty_summary())
        [state] = deliveries(live, receipt["object_id"])
        assert (state["state"], state["attempts"], state["last_error_class"]) == (
            "PENDING",
            attempt,
            "SYNTHETIC_FAILURE",
        )
        delay = (state["next_attempt_at"] - started).total_seconds()
        base = BACKOFF_BASE_SECONDS * 2 ** (attempt - 1)
        assert base * 0.5 - 1 <= delay <= base + 1
        # Not due before its backoff has elapsed.
        assert str(row["event_id"]) not in {str(r["event_id"]) for r in worker.claim(tenant, empty_summary())}
        clock.advance(seconds=base + 1)
    held = claimed(worker, tenant, row["event_id"])
    summary = empty_summary()
    worker.process(tenant, held, summary)
    [dead] = deliveries(live, receipt["object_id"])
    assert (dead["state"], dead["attempts"], dead["sent_at"]) == ("DEAD", 3, None)
    assert dead["completed_at"] and dead["last_error_class"] == "SYNTHETIC_FAILURE"
    assert summary["dead"] == 1
    clock.advance(hours=2)
    assert str(row["event_id"]) not in {str(r["event_id"]) for r in worker.claim(tenant, empty_summary())}


def test_permanent_smtp_rejection_is_dead_at_once_and_transient_is_retried(live):
    _, permanent = invitation(live)
    _, transient = invitation(live)
    [p_row] = deliveries(live, permanent["object_id"])
    [t_row] = deliveries(live, transient["object_id"])
    tenant = live.fixture["tenant_a"]
    with SmtpSink(rejections=["550 5.1.1 Mailbox unavailable", "451 4.3.0 Try again later"]) as sink:
        worker = make_worker(live, email_adapter="smtp", smtp_port=sink.port, smtp_timeout=5)
        rows = {str(r["event_id"]): r for r in worker.claim(tenant, empty_summary())}
        worker.process(tenant, rows[str(p_row["event_id"])], empty_summary())
        worker.process(tenant, rows[str(t_row["event_id"])], empty_summary())
    [p_state] = deliveries(live, permanent["object_id"])
    [t_state] = deliveries(live, transient["object_id"])
    assert (p_state["state"], p_state["last_error_class"], p_state["attempts"]) == (
        "DEAD",
        "SMTP_PERMANENT_REJECTION",
        1,
    )
    assert (t_state["state"], t_state["last_error_class"]) == ("PENDING", "SMTP_TRANSIENT_REJECTION")
    assert sink.messages == []


def test_released_leases_on_stop_restore_the_attempt(live):
    receipts = [invitation(live)[1] for _ in range(3)]
    events = {str(deliveries(live, r["object_id"])[0]["event_id"]) for r in receipts}
    tenant = live.fixture["tenant_a"]
    worker = make_worker(live)

    class StopAfterFirst(SyntheticAdapter):
        def send(self, message):
            super().send(message)
            worker.stop_event.set()

    worker.adapter = StopAfterFirst(worker.s)
    summary = empty_summary()
    worker.dispatch(tenant, summary)
    assert summary["released"] >= 1
    states = {str(row["event_id"]): row for r in receipts for row in deliveries(live, r["object_id"])}
    finished = [e for e in events if states[e]["state"] == "SENT"]
    released = [e for e in events if states[e]["state"] == "PENDING"]
    assert len(finished) <= 1 and len(finished) + len(released) == 3
    for event in released:
        assert states[event]["lease_owner"] is None and states[event]["lease_expires_at"] is None
        assert states[event]["attempts"] == 0


# -- adapters and configuration --------------------------------------------------------------------


def test_smtp_delivery_to_a_local_sink_and_no_external_call_inside_a_transaction(live):
    email, receipt = invitation(live)
    probes = []

    def probe(worker):
        # The adapter runs only with no connection or an idle one: never inside a transaction.
        connection = worker.connection
        assert connection is None or connection.info.transaction_status == TransactionStatus.IDLE
        probes.append(connection)

    with SmtpSink() as sink:
        worker = make_worker(live, email_adapter="smtp", smtp_port=sink.port, probe=probe, smtp_timeout=5)
        worker.run_once()
    assert probes and all(p is None for p in probes)
    [message] = sink.for_recipient(email)
    assert message["from"] == worker.s.smtp_from
    parsed = message["message"]
    assert parsed["Subject"] == "Your invitation to an Impact Platform workspace"
    assert parsed["To"] == email and parsed["Auto-Submitted"] == "auto-generated"
    assert parsed.get_content_type() == "text/plain" and not parsed.is_multipart()
    assert invitation_token(receipt) in parsed.get_content()
    [row] = deliveries(live, receipt["object_id"])
    assert parsed["Message-ID"] == "<" + str(row["event_id"]) + "@127.0.0.1>"
    assert row["state"] == "SENT"

    # Negative: the probe itself fails if a transaction were open around the external call.
    with pytest.raises(AssertionError):
        with worker.transaction() as c:
            c.execute("SELECT 1")
            probe(worker)


def test_smtp_refuses_non_loopback_hosts_outside_staging(live):
    with pytest.raises(ConfigurationError) as refused:
        settings(live, email_adapter="smtp", smtp_host="192.0.2.10")
    assert refused.value.reason == "SMTP_HOST_REFUSED"
    unvalidated = WorkerSettings(
        environment="test",
        worker_dsn="unused",
        public_origin="http://127.0.0.1",
        email_adapter="smtp",
        smtp_host="192.0.2.10",
    )
    with pytest.raises(DeliveryError) as error:
        SmtpAdapter(unvalidated).send(None)
    assert error.value.error_class == "SMTP_HOST_REFUSED" and error.value.permanent
    for reason, overrides in [
        ("DELIVERY_SECRETS_REQUIRED", {"delivery_secret": "short"}),
        ("SMTP_AND_HTTPS_REQUIRED", {"environment": "production"}),
        ("LEASE_SHORTER_THAN_SMTP_TIMEOUT", {"lease_seconds": 10, "smtp_timeout": 20}),
    ]:
        with pytest.raises(ConfigurationError) as refused:
            settings(live, **overrides)
        assert refused.value.reason == reason


@pytest.mark.skipif(NATIVE, reason="PGlite only: the native login is unprivileged by provisioning")
def test_worker_refuses_a_privileged_connection_when_unprivileged_is_required(live):
    worker = make_worker(live, require_unprivileged_db=True)
    with pytest.raises(ConfigurationError) as refused:
        worker.run_once()
    assert refused.value.reason == "PRIVILEGED_WORKER_CONNECTION"
    make_worker(live, require_unprivileged_db=False).run_once()


# -- in-app notices --------------------------------------------------------------------------------


def stale_notices(live):
    with live.db() as c:
        return {
            str(r["object_id"])
            for r in c.execute(
                "SELECT object_id FROM impact.notification_current WHERE tenant_id=%s AND recipient_id=%s "
                "AND notice_class='CALCULATION_STALE'",
                (live.fixture["tenant_a"], live.fixture["actors"]["author"]["principal_id"]),
            )
        }


def stale_notice(live, setup):
    before = stale_notices(live)
    _, indicator, plan, period = setup()
    source = observation(live, indicator, plan["data"]["obligations"][0]["source_key"])
    approve(live, submit(live, "observations", source))
    source = get(live, "observations", source["object_id"])
    result(live, indicator, period)
    change = propose(live, source, "Observation", {"value": "31", "source_version": "2"})
    approve(live, submit(live, "measurement-changes", change))
    [created] = stale_notices(live) - before
    notice = get(live, "notifications", created)
    assert notice["data"]["notice_class"] == "CALCULATION_STALE" and notice["data"]["delivered_at"] is None
    return notice


def test_calculation_stale_notice_is_delivered_in_app_exactly_once(live, setup):
    notice = stale_notice(live, setup)
    [intent] = deliveries(live, notice["object_id"])
    assert (intent["channel"], intent["template"], intent["recipient_sealed"]) == (
        "IN_APP",
        "IN_APP_NOTICE",
        None,
    )
    tenant = live.fixture["tenant_a"]
    clock = Clock()
    first = make_worker(live, clock=clock, lease_seconds=30)
    second = make_worker(live, clock=clock, lease_seconds=30)
    stale_hold = claimed(first, tenant, intent["event_id"])
    clock.advance(seconds=31)
    second.process(tenant, claimed(second, tenant, intent["event_id"]), empty_summary())
    refused = empty_summary()
    first.deliver_in_app(tenant, stale_hold, refused)
    assert refused["stale_refused"] == 1 and refused["sent"] == 0

    # A redelivered intent (at-least-once dispatch) finds the effect already recorded.
    with live.db() as c:
        c.execute(
            "UPDATE impact.outbox_delivery SET state='PENDING',sent_at=NULL,completed_at=NULL,"
            "next_attempt_at=now() WHERE tenant_id=%s AND event_id=%s",
            (tenant, intent["event_id"]),
        )
    make_worker(live).run_once()
    with live.db() as c:
        rows = c.execute(
            "SELECT * FROM impact.notification_delivery WHERE tenant_id=%s AND notification_id=%s",
            (tenant, notice["object_id"]),
        ).fetchall()
        receipts = c.execute(
            "SELECT count(*) AS n FROM impact.consumer_receipt WHERE tenant_id=%s AND event_id=%s",
            (tenant, intent["event_id"]),
        ).fetchone()["n"]
    assert len(rows) == 1 and receipts == 1
    delivered = get(live, "notifications", notice["object_id"])
    assert delivered["data"]["delivered_at"] == rows[0]["delivered_at"].isoformat()
    # The notice is not delivered to, or visible by, anyone else.
    expect(live.request(live.path("notifications", notice["object_id"]), actor="reviewer"), 404)


def test_notice_for_an_inactive_recipient_is_superseded(live):
    tenant = live.fixture["tenant_a"]
    recipient = live.fixture["actors"]["revoked"]["principal_id"]
    notification = str(uuid4())
    with live.db() as c:
        from impact_api.delivery import enqueue
        from impact_api.store import write
        from types import SimpleNamespace

        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        ctx = SimpleNamespace(tenant_id=tenant, principal_id=live.fixture["actors"]["admin"]["principal_id"])
        event = enqueue(c, tenant, "IN_APP_NOTICE", notification)
        write(
            c,
            ctx,
            "Notification",
            {
                "event_id": event,
                "recipient_id": recipient,
                "channel": "IN_APP",
                "notice_class": "QUALIFICATION",
                "safe_reference": notification,
            },
            "Unread",
            object_id=notification,
            track_author=False,
        )
        active = c.execute(
            "SELECT active FROM impact.tenant_principal WHERE tenant_id=%s AND principal_id=%s",
            (tenant, recipient),
        ).fetchone()["active"]
    assert active is False
    make_worker(live).run_once()
    [row] = deliveries(live, notification)
    assert (row["state"], row["last_error_class"]) == ("SUPERSEDED", "RECIPIENT_INACTIVE")
    with live.db() as c:
        assert not c.execute(
            "SELECT 1 FROM impact.notification_delivery WHERE tenant_id=%s AND notification_id=%s",
            (tenant, notification),
        ).fetchone()


def test_authority_expiry_reminders_are_idempotent_per_threshold(live):
    """Isolated from the shared suite database: two ceilings of the reviewer with an expiry instant
    no other row has; every assertion is about that (principal, instant) group only, and the
    ceilings are removed afterwards."""
    tenant = live.fixture["tenant_a"]
    reviewer = live.fixture["actors"]["reviewer"]["principal_id"]
    expires = (datetime.now(timezone.utc) + timedelta(days=10, seconds=random.randrange(1, 80000))).replace(
        microsecond=0
    )
    authorities = [str(uuid4()) for _ in range(2)]
    with live.db() as c:
        scope = c.execute(
            "SELECT scope_id FROM impact.scope_definition WHERE tenant_id=%s AND scope_type='TENANT'",
            (tenant,),
        ).fetchone()["scope_id"]
        for authority in authorities:
            c.execute(
                "INSERT INTO impact.grant_authority VALUES(%s,%s,%s,%s,%s,%s)",
                (tenant, authority, reviewer, "qualification.reminder." + authority[:8], scope, expires),
            )

    def reminders():
        with live.db() as c:
            return c.execute(
                "SELECT a.threshold_days,a.notification_id,n.notice_class,n.recipient_id,r.created_by "
                "FROM impact.authority_reminder a JOIN impact.notification_current n "
                "ON n.tenant_id=a.tenant_id AND n.object_id=a.notification_id JOIN impact.object_registry r "
                "ON r.tenant_id=n.tenant_id AND r.object_id=n.object_id "
                "WHERE a.tenant_id=%s AND a.principal_id=%s AND a.expires_at=%s ORDER BY a.threshold_days DESC",
                (tenant, reviewer, expires),
            ).fetchall()

    try:
        clock = Clock()
        clock.advance(days=-5)
        make_worker(live, clock=clock).run_once()
        assert reminders() == []
        clock.advance(days=5)
        worker = make_worker(live, clock=clock)
        worker.run_once()
        worker.run_once()
        [fourteen] = reminders()
        assert (fourteen["threshold_days"], fourteen["notice_class"]) == (14, "AUTHORITY_EXPIRING_14D")
        assert str(fourteen["recipient_id"]) == reviewer
        with live.db() as c:
            author = c.execute(
                "SELECT principal_kind,identity_id FROM impact.tenant_principal WHERE tenant_id=%s AND principal_id=%s",
                (tenant, fourteen["created_by"]),
            ).fetchone()
        assert (author["principal_kind"], author["identity_id"]) == ("SERVICE", None)
        [intent] = deliveries(live, fourteen["notification_id"])
        assert intent["state"] == "SENT"
        clock.advance(days=8)
        make_worker(live, clock=clock).run_once()
        make_worker(live, clock=clock).run_once()
        rows = reminders()
        assert [(r["threshold_days"], r["notice_class"]) for r in rows] == [
            (14, "AUTHORITY_EXPIRING_14D"),
            (3, "AUTHORITY_EXPIRING_3D"),
        ]
        three = str(rows[1]["notification_id"])
        notice = expect(live.request(live.path("notifications", three), actor="reviewer"), 200)
        assert notice["data"]["notice_class"] == "AUTHORITY_EXPIRING_3D"
        expect(live.request(live.path("notifications", three), actor="author"), 404)
    finally:
        with live.db() as c:
            c.execute("DELETE FROM impact.grant_authority WHERE authority_id=ANY(%s::uuid[])", (authorities,))


# -- job cancellation ------------------------------------------------------------------------------


def test_queued_job_cancellation_is_honoured_and_a_running_job_is_not_cancelled(live):
    tenant = live.fixture["tenant_a"]
    author = live.fixture["actors"]["author"]["principal_id"]
    jobs = {name: str(uuid4()) for name in ["queued", "running", "untouched"]}
    with live.db() as c:
        scope = c.execute(
            "SELECT scope_id FROM impact.scope_definition WHERE tenant_id=%s AND scope_type='TENANT'",
            (tenant,),
        ).fetchone()["scope_id"]
        for name, state, cancelled in [
            ("queued", "Queued", True),
            ("running", "Running", True),
            ("untouched", "Queued", False),
        ]:
            c.execute(
                "INSERT INTO impact.job(tenant_id,job_id,job_class,requester_id,scope_id,state,input_manifest,"
                "cancellation_requested_at) VALUES(%s,%s,'qualification',%s,%s,%s,'{}',%s)",
                (tenant, jobs[name], author, scope, state, datetime.now(timezone.utc) if cancelled else None),
            )
    worker = make_worker(live)
    summary = worker.run_once()
    assert summary["cancelled"] >= 1 and summary["refused_cancellations"] >= 1
    worker.run_once()

    with live.db() as c:
        rows = {
            str(r["job_id"]): r
            for r in c.execute(
                "SELECT * FROM impact.job WHERE job_id=ANY(%s::uuid[])", (list(jobs.values()),)
            )
        }
        items = {
            str(r["job_id"]): r
            for r in c.execute(
                "SELECT * FROM impact.job_item WHERE job_id=ANY(%s::uuid[]) AND item_key='cancellation'",
                (list(jobs.values()),),
            )
        }
    assert rows[jobs["queued"]]["state"] == "Cancelled" and rows[jobs["queued"]]["lease_generation"] == 1
    assert rows[jobs["queued"]]["output_manifest"]["boundary"] == "BEFORE_START"
    assert items[jobs["queued"]]["outcome"] == "CANCELLED_BEFORE_START"
    assert rows[jobs["running"]]["state"] == "Running" and rows[jobs["running"]]["lease_generation"] == 0
    assert (items[jobs["running"]]["outcome"], items[jobs["running"]]["error_code"]) == (
        "NOT_CANCELLED_STARTED",
        "JOB_ALREADY_STARTED",
    )
    assert rows[jobs["untouched"]]["state"] == "Queued" and jobs["untouched"] not in items


# -- recovery-contact channel verification ---------------------------------------------------------


def contact_command(live, row, name, data, actor="partner", status=200):
    return expect(
        live.request(
            CONTACTS + "/" + row["contact_id"] + "/actions/" + name,
            actor=actor,
            method="POST",
            body=command({"reason": "Channel verification qualification", **data}, row["revision_id"]),
        ),
        status,
    )


def test_recovery_channel_verification_code_is_single_use_and_evidence_only(live):
    row, tenant, _, _ = nominate(live)
    assert row["channel_verification"]["state"] == "NONE"
    for actor in ["author", "admin", "other_tenant"]:
        contact_command(live, row, "channel-request", {"email": "partner@example.test"}, actor, 404)
    wrong = contact_command(live, row, "channel-request", {"email": "someone@example.test"}, status=403)
    assert wrong["reason_code"] == "CHANNEL_ADDRESS_MISMATCH"
    requested = contact_command(live, row, "channel-request", {"email": "Partner@Example.test"})
    Draft202012Validator(CONTACT_RECEIPT, format_checker=FormatChecker()).validate(requested)
    challenge = requested["channel_verification"]["challenge_id"]
    assert requested["channel_verification"]["state"] == "PENDING"
    [intent] = deliveries(live, challenge)
    assert (intent["template"], intent["channel"]) == ("RECOVERY_CHANNEL_VERIFICATION", "EMAIL")
    code = channel_code(live.config["delivery_secret"], challenge)
    with live.db() as c:
        stored = c.execute(
            "SELECT * FROM impact.recovery_channel_challenge WHERE challenge_id=%s", (challenge,)
        ).fetchone()
    raw = json.dumps(intent, default=str) + json.dumps(stored, default=str)
    assert code not in raw and "partner@example.test" not in raw
    assert bytes(stored["code_hash"]) != code.encode()

    worker = make_worker(live)
    worker.run_once()
    [message] = [m for m in sink_lines(worker.s) if m["event_id"] == str(intent["event_id"])]
    assert message["to"] == "partner@example.test" and code in message["body"]
    assert message["subject"] == "Impact Platform recovery contact verification code"

    wrong_code = "0" * 8 if code != "0" * 8 else "1" * 8
    refused = contact_command(
        live, requested, "channel-confirm", {"challenge_id": challenge, "code": wrong_code}, status=403
    )
    assert refused["reason_code"] == "CHANNEL_CODE_INVALID"
    with live.db() as c:
        assert (
            c.execute(
                "SELECT attempts FROM impact.recovery_channel_challenge WHERE challenge_id=%s", (challenge,)
            ).fetchone()["attempts"]
            == 1
        )
    contact_command(
        live, requested, "channel-confirm", {"challenge_id": challenge, "code": code}, "author", 404
    )
    confirmed = contact_command(live, requested, "channel-confirm", {"challenge_id": challenge, "code": code})
    assert confirmed["channel_verification"]["state"] == "VERIFIED"
    assert confirmed["channel_verification"]["verified_at"]
    # Evidence only: the contact's state, eligibility and access are unchanged.
    assert confirmed["state"] == row["state"] == "Nominated"
    assert confirmed["verification"] == row["verification"] | {
        "revision_id": confirmed["verification"]["revision_id"]
    }
    expect(live.request(live.path("me/access", tenant=tenant["tenant_id"]), actor="partner"), 404)
    reused = contact_command(
        live, confirmed, "channel-confirm", {"challenge_id": challenge, "code": code}, status=409
    )
    assert reused["reason_code"] == "CHANNEL_CODE_USED"


def test_recovery_channel_code_expires_and_locks_after_five_wrong_attempts(live):
    row, _, _, _ = nominate(live)
    requested = contact_command(live, row, "channel-request", {"email": "partner@example.test"})
    challenge = requested["channel_verification"]["challenge_id"]
    code = channel_code(live.config["delivery_secret"], challenge)
    with live.db() as c:
        c.execute(
            "UPDATE impact.recovery_channel_challenge SET created_at=now()-interval '20 minutes',"
            "expires_at=now()-interval '5 minutes' WHERE challenge_id=%s",
            (challenge,),
        )
    expired = contact_command(
        live, requested, "channel-confirm", {"challenge_id": challenge, "code": code}, status=403
    )
    assert expired["reason_code"] == "CHANNEL_CODE_EXPIRED"
    worker = make_worker(live)
    worker.run_once()
    [intent] = deliveries(live, challenge)
    assert (intent["state"], intent["last_error_class"]) == ("SUPERSEDED", "CHALLENGE_CLOSED")
    assert not [m for m in sink_lines(worker.s) if m["event_id"] == str(intent["event_id"])]
    closed = contact_command(
        live, requested, "channel-confirm", {"challenge_id": challenge, "code": code}, status=409
    )
    assert closed["reason_code"] == "CHANNEL_CHALLENGE_CLOSED"

    again = contact_command(live, requested, "channel-request", {"email": "partner@example.test"})
    challenge = again["channel_verification"]["challenge_id"]
    code = channel_code(live.config["delivery_secret"], challenge)
    wrong = "0" * 8 if code != "0" * 8 else "1" * 8
    reasons = [
        contact_command(
            live, again, "channel-confirm", {"challenge_id": challenge, "code": wrong}, status=403
        )["reason_code"]
        for _ in range(5)
    ]
    assert reasons == ["CHANNEL_CODE_INVALID"] * 4 + ["CHANNEL_CODE_ATTEMPTS_EXCEEDED"]
    locked = contact_command(
        live, again, "channel-confirm", {"challenge_id": challenge, "code": code}, status=409
    )
    assert locked["reason_code"] == "CHANNEL_CHALLENGE_CLOSED"
    current = next(
        item for item in listing(live, "partner")["items"] if item["contact_id"] == row["contact_id"]
    )
    assert current["channel_verification"]["state"] == "FAILED"
    assert current["channel_verification"]["attempts_remaining"] == 0


def test_channel_request_is_refused_for_a_closed_contact(live):
    row, _, _, _ = nominate(live)
    declined = contact_action(live, row, "decline")
    refused = contact_command(
        live, declined, "channel-request", {"email": "partner@example.test"}, status=409
    )
    assert refused["reason_code"] == "INVALID_RECOVERY_TRANSITION"
    bad = live.request(
        CONTACTS + "/" + row["contact_id"] + "/actions/channel-confirm",
        actor="partner",
        method="POST",
        body=command({"challenge_id": str(uuid4()), "code": "12ab", "reason": "x"}, declined["revision_id"]),
    )
    assert bad.status_code == 422


# -- isolation and operator signal -----------------------------------------------------------------


def test_worker_role_reads_only_the_tenant_in_context(live):
    tenant_a, tenant_b = live.fixture["tenant_a"], live.fixture["tenant_b"]
    with psycopg.connect(worker_dsn(), row_factory=dict_row, prepare_threshold=None) as c:
        c.execute("SET LOCAL ROLE impact_worker")
        assert c.execute("SELECT count(*) AS n FROM impact.outbox_delivery").fetchone()["n"] == 0
        tenants = c.execute("SELECT * FROM impact.worker_tenants(now())").fetchall()
        assert {str(r["tenant_id"]) for r in tenants} >= {tenant_a, tenant_b}
        assert set(tenants[0]) == {"tenant_id", "lifecycle_state", "due_deliveries"}
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_a,))
        seen = c.execute("SELECT DISTINCT tenant_id FROM impact.outbox_delivery").fetchall()
        assert {str(r["tenant_id"]) for r in seen} <= {tenant_a}
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.outbox_delivery WHERE tenant_id=%s", (tenant_b,)
            ).fetchone()["n"]
            == 0
        )
        assert (
            c.execute(
                "UPDATE impact.outbox_delivery SET attempts=attempts WHERE tenant_id=%s", (tenant_b,)
            ).rowcount
            == 0
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.recovery_channel_challenge WHERE tenant_id=%s", (tenant_b,)
            ).fetchone()["n"]
            == 0
        )
    for statement in [
        "SELECT * FROM impact.tenant_recovery_contact",
        "SELECT * FROM impact.auth_identity",
        "UPDATE impact.recovery_channel_challenge SET attempts=0",
        "SELECT impact.enqueue_recovery_channel_delivery(gen_random_uuid(),'\\x00'::bytea)",
    ]:
        with psycopg.connect(worker_dsn(), prepare_threshold=None) as c:
            c.execute("SET LOCAL ROLE impact_worker")
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                c.execute(statement)


def revoked_by_migration_0025():
    """(table, privileges) for every REVOKE of migration 0025; ALL means every table privilege."""
    source = (ROOT / "infrastructure/migrations/0025_worker_grants.sql").read_text()
    pairs = re.findall(r"^REVOKE ([A-Z,]+) ON impact\.([a-z0-9_]+) FROM impact_worker;$", source, re.M)
    full = ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"]
    return [(table, full if what == "ALL" else what.split(",")) for what, table in pairs]


def test_worker_role_holds_no_privilege_migration_0025_revoked(live):
    """Migration 0025 narrowed impact_worker to what worker.py touches; every revoked privilege is
    absent, at table and column level, and the privileges the worker uses are still there."""
    revoked = revoked_by_migration_0025()
    assert len(revoked) >= 60 and "SELECT" in dict(revoked)["tenant_root"]
    deferred = {"job", "job_item", "report_current", "report_template_current"}
    assert not deferred & {table for table, _ in revoked}
    with live.db() as c:
        for table, privileges in revoked:
            for privilege in privileges:
                held = c.execute(
                    "SELECT has_table_privilege('impact_worker',%s,%s) AS held",
                    ("impact." + table, privilege),
                ).fetchone()["held"]
                assert not held, (table, privilege)
        columns = c.execute(
            "SELECT count(*) AS n FROM information_schema.column_privileges WHERE grantee='impact_worker' "
            "AND table_schema='impact' AND table_name='tenant_root'"
        ).fetchone()["n"]
        assert columns == 0
        for table, privilege in [
            ("object_registry", "INSERT"),
            ("object_revision", "SELECT"),
            ("notification_current", "INSERT"),
            ("audit_event_current", "INSERT"),
            ("tenant_principal", "INSERT"),
            ("membership_current", "SELECT"),
            ("outbox_event", "INSERT"),
            ("outbox_delivery", "UPDATE"),
            ("consumer_receipt", "INSERT"),
            ("job", "UPDATE"),
            ("job_item", "INSERT"),
        ]:
            assert c.execute(
                "SELECT has_table_privilege('impact_worker',%s,%s) AS held", ("impact." + table, privilege)
            ).fetchone()["held"], (table, privilege)


def test_worker_job_and_report_privileges_after_migration_0026(live):
    """Migration 0026 finished the narrowing 0025 deferred: on the job tables the worker holds exactly
    what the REPORT_EXPORT job class and the cancellation pass use (0024), and nothing on the report
    and report-template projections."""
    expected = {
        "job": {"SELECT", "UPDATE"},
        "job_item": {"SELECT", "INSERT"},
        "report_current": set(),
        "report_template_current": set(),
        "report_export": {"SELECT", "UPDATE"},
        "report_export_artifact": {"SELECT", "INSERT"},
        "report_package_binding": {"SELECT"},
    }
    every = ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"]
    with live.db() as c:
        for table, privileges in expected.items():
            held = {
                privilege
                for privilege in every
                if c.execute(
                    "SELECT has_table_privilege('impact_worker',%s,%s) AS held",
                    ("impact." + table, privilege),
                ).fetchone()["held"]
            }
            assert held == privileges, (table, held)
        # The application keeps its own job grants (0003): it requests export jobs.
        for privilege in ["SELECT", "INSERT", "UPDATE"]:
            assert c.execute(
                "SELECT has_table_privilege('impact_app','impact.job',%s) AS held", (privilege,)
            ).fetchone()["held"], privilege


def test_worker_role_is_refused_on_revoked_tables(live):
    tenant = live.fixture["tenant_a"]
    for statement in [
        "SELECT * FROM impact.programme_current",
        "SELECT * FROM impact.observation_current",
        "SELECT tenant_id FROM impact.tenant_root",
        "UPDATE impact.tenant_root SET policy_epoch=policy_epoch",
        "UPDATE impact.object_registry SET updated_at=updated_at",
        "UPDATE impact.membership_current SET expires_at=expires_at",
        "SELECT * FROM impact.operation_receipt",
        "SELECT * FROM impact.grant_current",
        "SELECT * FROM impact.report_current",
        "SELECT * FROM impact.report_template_current",
        "UPDATE impact.job_item SET outcome=outcome",
    ]:
        with psycopg.connect(worker_dsn(), prepare_threshold=None) as c:
            c.execute("SET LOCAL ROLE impact_worker")
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                c.execute(statement)


def test_app_role_cannot_record_delivery_outcomes(live):
    with live.db() as c:
        c.execute("SET LOCAL ROLE impact_app")
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            c.execute("UPDATE impact.outbox_delivery SET state='SENT'")


def test_heartbeat_is_visible_to_platform_operators_only(live):
    worker = make_worker(live)
    worker.run_once()
    listing = expect(live.request("/v1/platform/workers", actor="admin"), 200)
    Draft202012Validator(WORKERS, format_checker=FormatChecker()).validate(listing)
    [mine] = [w for w in listing["items"] if w["worker_id"] == worker.worker_id]
    assert (mine["state"], mine["stale"], mine["build"]) == ("RUNNING", False, BUILD)
    assert mine["iterations"] == 1
    worker.heartbeat("STOPPED")
    listing = expect(live.request("/v1/platform/workers", actor="admin"), 200)
    [mine] = [w for w in listing["items"] if w["worker_id"] == worker.worker_id]
    assert mine["state"] == "STOPPED" and mine["stopped_at"]
    for actor in ["author", "partner", "other_tenant"]:
        expect(live.request("/v1/platform/workers", actor=actor), 404)
    expect(live.request("/v1/platform/workers", actor=None), 401)


def test_invitation_intent_needs_the_current_signing_secret(live):
    email, receipt = invitation(live)
    [row] = deliveries(live, receipt["object_id"])
    tenant = live.fixture["tenant_a"]
    worker = make_worker(live, invitation_secret="x" * 64)
    worker.process(tenant, claimed(worker, tenant, row["event_id"]), empty_summary())
    [state] = deliveries(live, receipt["object_id"])
    assert (state["state"], state["last_error_class"]) == ("DEAD", "SIGNING_KEY_MISMATCH")
    assert not [m for m in sink_lines(worker.s) if m["to"] == email]
    token = derive_token(
        live.config["invitation_secret"],
        live.fixture["tenant_a"],
        receipt["object_id"],
        row["reference_generation"],
    )
    assert token == invitation_token(receipt)


# -- review fixes (M1, L1, L2, L4, L5, L6, L7, L9) -------------------------------------------------


def test_a_batch_row_whose_lease_ran_out_is_skipped_not_sent_twice(live):
    _, taken = invitation(live)
    _, expired = invitation(live)
    [taken_row] = deliveries(live, taken["object_id"])
    [expired_row] = deliveries(live, expired["object_id"])
    tenant = live.fixture["tenant_a"]
    clock = Clock()
    first = make_worker(live, clock=clock, lease_seconds=30)
    second = make_worker(live, clock=clock, lease_seconds=30)
    batch = {str(r["event_id"]): r for r in first.claim(tenant, empty_summary())}
    clock.advance(seconds=31)
    # An expired, not yet taken-over lease: the first holder may not send it.
    lost = empty_summary()
    first.process(tenant, batch[str(expired_row["event_id"])], lost)
    assert lost["stale_refused"] == 1 and lost["sent"] == 0
    [waiting] = deliveries(live, expired["object_id"])
    assert (waiting["state"], waiting["lease_generation"], waiting["sent_at"]) == ("LEASED", 1, None)
    # A second worker takes the batch over while the first is still busy.
    rival = {str(r["event_id"]): r for r in second.claim(tenant, empty_summary())}
    first.process(tenant, batch[str(taken_row["event_id"])], lost)
    assert lost["stale_refused"] == 2 and sink_lines(first.s) == []
    for event in [taken_row["event_id"], expired_row["event_id"]]:
        second.process(tenant, rival[str(event)], empty_summary())
    for receipt in [taken, expired]:
        [done] = deliveries(live, receipt["object_id"])
        assert (done["state"], done["lease_generation"], done["attempts"]) == ("SENT", 2, 2)
    sent = [m["event_id"] for m in sink_lines(second.s)]
    assert sent.count(str(taken_row["event_id"])) == 1 and sent.count(str(expired_row["event_id"])) == 1


def test_a_held_row_is_never_sent_and_returns_to_pending_when_its_lease_ends(live):
    _, receipt = invitation(live)
    [row] = deliveries(live, receipt["object_id"])
    tenant = live.fixture["tenant_a"]
    clock = Clock()
    worker = make_worker(live, clock=clock, lease_seconds=30)
    held = claimed(worker, tenant, row["event_id"])
    with live.db() as c:
        # What quiesce_tenant does on suspension (tenant A itself stays Active here).
        c.execute(
            "UPDATE impact.outbox_delivery SET held_at=now() WHERE tenant_id=%s AND event_id=%s",
            (tenant, row["event_id"]),
        )
    summary = empty_summary()
    worker.process(tenant, held, summary)
    assert summary["stale_refused"] == 1 and sink_lines(worker.s) == []
    assert deliveries(live, receipt["object_id"])[0]["state"] == "LEASED"
    clock.advance(seconds=31)
    worker.run_once()
    [released] = deliveries(live, receipt["object_id"])
    assert (released["state"], released["lease_owner"], released["lease_expires_at"]) == (
        "PENDING",
        None,
        None,
    )
    assert released["held_at"] and released["sent_at"] is None
    clock.advance(hours=3)
    worker.run_once()
    assert deliveries(live, receipt["object_id"])[0]["state"] == "PENDING"
    assert not [m for m in sink_lines(worker.s) if m["event_id"] == str(row["event_id"])]


def test_unsent_events_counts_only_open_dispatchable_intents(live):
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        expected = c.execute(
            "SELECT count(*) AS n FROM impact.outbox_delivery WHERE tenant_id=%s AND channel IS NOT NULL "
            "AND state IN ('PENDING','LEASED')",
            (tenant,),
        ).fetchone()["n"]
        legacy = c.execute(
            "SELECT count(*) AS n FROM impact.outbox_delivery WHERE tenant_id=%s AND channel IS NULL",
            (tenant,),
        ).fetchone()["n"]
        c.execute("SET LOCAL ROLE impact_platform")
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        impact = c.execute("SELECT impact.tenant_work_impact(%s) AS i", (tenant,)).fetchone()["i"]
    assert legacy > 0
    assert impact["unsent_events"] == expected


def test_a_failing_tenant_or_template_does_not_stop_the_worker(live, monkeypatch):
    import impact_api.worker as module

    tenant_a = live.fixture["tenant_a"]
    worker = make_worker(live)
    original = worker.remind

    def remind(tenant, summary):
        if tenant == tenant_a:
            raise RuntimeError("qualification fault")
        return original(tenant, summary)

    worker.remind = remind
    summary = worker.run_once()
    assert summary["tenant_failures"] == 1 and summary["tenants"] >= 2
    listing = expect(live.request("/v1/platform/workers", actor="admin"), 200)
    [mine] = [w for w in listing["items"] if w["worker_id"] == worker.worker_id]
    assert mine["failures"] == 1

    _, receipt = invitation(live)

    def broken(*_args, **_kwargs):
        raise RuntimeError("renderer defect")

    monkeypatch.setattr(module, "render", broken)
    make_worker(live).run_once()
    [row] = deliveries(live, receipt["object_id"])
    assert (row["state"], row["last_error_class"]) == ("DEAD", "PREPARE_DEFECT")


def test_challenge_contact_must_belong_to_the_same_tenant(live):
    row, _, _, _ = nominate(live)
    with live.db() as c:
        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            c.execute(
                "INSERT INTO impact.recovery_channel_challenge(tenant_id,challenge_id,contact_id,contact_revision,"
                "requested_by,email_hash,code_hash,state,expires_at) VALUES(%s,gen_random_uuid(),%s,%s,%s,%s,%s,"
                "'PENDING',now()+interval '10 minutes')",
                (
                    live.fixture["tenant_a"],
                    row["contact_id"],
                    row["revision_id"],
                    row["nominee_identity_id"],
                    b"\0" * 32,
                    b"\0" * 32,
                ),
            )


@pytest.mark.parametrize(
    "sink_options,state,error_class",
    [
        ({"mail_rejections": ["550 5.7.1 Sender address rejected"]}, "PENDING", "SMTP_SENDER_REJECTED"),
        ({"mail_rejections": ["530 5.7.0 Authentication required"]}, "PENDING", "SMTP_SENDER_REJECTED"),
        ({"rejections": ["535 5.7.8 Authentication credentials invalid"]}, "PENDING", "SMTP_AUTHENTICATION"),
        ({"rcpt_rejections": ["550 5.1.1 No such user"]}, "DEAD", "RECIPIENT_REFUSED"),
    ],
)
def test_sender_and_authentication_rejections_are_retried_recipient_rejection_is_dead(
    live, sink_options, state, error_class
):
    _, receipt = invitation(live)
    [row] = deliveries(live, receipt["object_id"])
    tenant = live.fixture["tenant_a"]
    with SmtpSink(**sink_options) as sink:
        worker = make_worker(live, email_adapter="smtp", smtp_port=sink.port, smtp_timeout=5)
        worker.process(tenant, claimed(worker, tenant, row["event_id"]), empty_summary())
    [result] = deliveries(live, receipt["object_id"])
    assert (result["state"], result["last_error_class"]) == (state, error_class)
    assert sink.messages == []


def test_channel_requests_are_rate_limited_and_confirm_follows_the_tenant_state(live):
    row, tenant, _, _ = nominate(live)
    current = row
    for _ in range(3):
        current = contact_command(live, current, "channel-request", {"email": "partner@example.test"})
    limited = contact_command(live, current, "channel-request", {"email": "partner@example.test"}, status=429)
    assert limited["reason_code"] == "CHANNEL_REQUEST_LIMIT"
    challenge = current["channel_verification"]["challenge_id"]
    code = channel_code(live.config["delivery_secret"], challenge)
    with live.db() as c:
        c.execute(
            "UPDATE impact.tenant_root SET lifecycle_state='Closing' WHERE tenant_id=%s",
            (tenant["tenant_id"],),
        )
    closed = contact_command(
        live, current, "channel-confirm", {"challenge_id": challenge, "code": code}, status=403
    )
    assert closed["reason_code"] == "RECOVERY_TENANT_UNAVAILABLE"
    with live.db() as c:
        assert (
            c.execute(
                "SELECT state FROM impact.recovery_channel_challenge WHERE challenge_id=%s", (challenge,)
            ).fetchone()["state"]
            == "PENDING"
        )


def test_worker_settings_never_print_secrets_or_the_connection_string(live):
    s = settings(live, smtp_password="qualification-smtp-password")
    text = repr(s) + str(s)
    for secret in [s.worker_dsn, s.invitation_secret, s.delivery_secret, "qualification-smtp-password"]:
        assert secret not in text
