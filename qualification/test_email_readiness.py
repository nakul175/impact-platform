"""Email readiness (v0.27) with the worker on the database: an invitation delivered through
STARTTLS with certificate verification and AUTH to an in-process TLS SMTP server (a wrong password
first, retried, then the same Message-ID over the working credentials), and the email send rate
limit applied at claim time, so a deferred intent keeps its attempts and in-app notices are never
held back."""
# ruff: noqa: F811

from uuid import uuid4

import pytest

from impact_api.worker import empty_summary
from smtp_sink import SmtpSink, make_certificate, server_context
from test_measurement import setup  # noqa: F401
from test_worker import Clock, claimed, deliveries, invitation, make_worker, stale_notice

USER = "smtp-user@qualification.test"
PASSWORD = "qualification-pass-word-7"


@pytest.fixture(scope="module")
def certificate(tmp_path_factory):
    return make_certificate(tmp_path_factory.mktemp("worker-tls"))


def tls_worker(live, sink, certificate, clock=None, **overrides):
    return make_worker(
        live,
        clock=clock,
        email_adapter="smtp",
        smtp_host="127.0.0.1",
        smtp_port=sink.port,
        smtp_starttls="required",
        smtp_ca_file=str(certificate[0]),
        smtp_username=USER,
        smtp_password=PASSWORD,
        smtp_timeout=5,
        **overrides,
    )


def test_invitation_is_delivered_over_starttls_with_auth_after_a_retried_wrong_password(live, certificate):
    email, receipt = invitation(live)
    [row] = deliveries(live, receipt["object_id"])
    tenant = live.fixture["tenant_a"]
    clock = Clock()
    rejections = ["535 5.7.8 Authentication credentials invalid"]
    # One mechanism only: smtplib falls through to the next advertised mechanism after a 535, so
    # with PLAIN and LOGIN both offered the scripted refusal would be followed by a working LOGIN.
    with SmtpSink(
        tls_context=server_context(*certificate),
        credentials={USER: PASSWORD},
        auth_rejections=rejections,
        auth_mechanisms=("PLAIN",),
    ) as sink:
        worker = tls_worker(live, sink, certificate, clock=clock)
        # Only this row is processed (other due rows of the tenant stay leased), so the scripted
        # authentication refusal is consumed by this delivery's first attempt.
        worker.process(tenant, claimed(worker, tenant, row["event_id"]), empty_summary())
        [first] = deliveries(live, receipt["object_id"])
        assert (first["state"], first["last_error_class"], first["attempts"]) == (
            "PENDING",
            "SMTP_AUTHENTICATION",
            1,
        )
        assert sink.for_recipient(email) == [] and sink.commands_in_clear() == []
        clock.advance(seconds=45)  # past the first backoff (at most 30 s)
        worker.process(tenant, claimed(worker, tenant, row["event_id"]), empty_summary())
        [sent] = deliveries(live, receipt["object_id"])
        assert (sent["state"], sent["last_error_class"], sent["attempts"]) == ("SENT", None, 2)
        [message] = sink.for_recipient(email)
    assert message["tls"] and message["authenticated_as"] == USER
    assert message["message"]["Message-ID"] == "<" + str(row["event_id"]) + "@127.0.0.1>"
    assert (USER, True) in sink.authenticated and sink.commands_in_clear() == []


def claimed_by_channel(worker, tenant):
    rows = worker.claim(tenant, empty_summary())
    return rows, [r for r in rows if r["channel"] == "EMAIL"], [r for r in rows if r["channel"] == "IN_APP"]


def test_email_rate_limit_defers_claims_without_spending_attempts_and_spares_in_app(live, setup, certificate):
    tenant = live.fixture["tenant_a"]
    receipts = [invitation(live)[1] for _ in range(3)]
    mine = {str(deliveries(live, r["object_id"])[0]["event_id"]) for r in receipts}
    notice = stale_notice(live, setup)
    [in_app] = deliveries(live, notice["object_id"])
    clock = Clock()
    with SmtpSink(tls_context=server_context(*certificate), credentials={USER: PASSWORD}) as sink:
        worker = tls_worker(
            live, sink, certificate, clock=clock, email_rate_limit=2, email_rate_window_seconds=60
        )
        rows, emails, in_apps = claimed_by_channel(worker, tenant)
        assert len(emails) == 2 and str(in_app["event_id"]) in {str(r["event_id"]) for r in in_apps}
        assert worker.email_limiter.deferred >= 1
        waiting = mine - {str(r["event_id"]) for r in emails}
        assert len(waiting) >= 1
        for event in waiting:
            state = next(
                d for r in receipts for d in deliveries(live, r["object_id"]) if str(d["event_id"]) == event
            )
            assert (state["state"], state["attempts"], state["last_error_class"]) == ("PENDING", 0, None)
        worker.release(tenant, rows)
        # The window is exhausted: no email is claimed, in-app rows still are.
        rows, emails, in_apps = claimed_by_channel(worker, tenant)
        assert emails == [] and len(in_apps) >= 1
        worker.release(tenant, rows)
        clock.advance(seconds=61)
        rows, emails, _ = claimed_by_channel(worker, tenant)
        assert len(emails) == 2
        worker.release(tenant, rows)
        # A per-tenant limit alone: one email per window for this tenant, the rest deferred.
        per_tenant = tls_worker(live, sink, certificate, clock=clock, email_tenant_rate_limit=1)
        rows, emails, _ = claimed_by_channel(per_tenant, tenant)
        assert len(emails) == 1
        per_tenant.release(tenant, rows)
        rows, emails, _ = claimed_by_channel(per_tenant, tenant)
        assert emails == []
        per_tenant.release(tenant, rows)
        for receipt in receipts:
            [state] = deliveries(live, receipt["object_id"])
            assert (state["state"], state["attempts"], state["last_error_class"]) == ("PENDING", 0, None)
        # Without a limit every intent goes out, over TLS, with its attempts untouched by the waiting.
        unlimited = tls_worker(live, sink, certificate, clock=clock)
        unlimited.run_once()
        for receipt in receipts:
            [state] = deliveries(live, receipt["object_id"])
            assert (state["state"], state["attempts"]) == ("SENT", 1)
        assert all(m["tls"] for m in sink.messages) and sink.commands_in_clear() == []
    [delivered] = deliveries(live, notice["object_id"])
    assert delivered["state"] == "SENT"


def test_rate_limited_worker_settings_load_from_the_environment(live, monkeypatch, certificate):
    monkeypatch.setenv("IMPACT_EMAIL_RATE_LIMIT", "7")
    monkeypatch.setenv("IMPACT_EMAIL_TENANT_RATE_LIMIT", "3")
    monkeypatch.setenv("IMPACT_SMTP_STARTTLS", "required")
    with SmtpSink() as sink:
        worker = tls_worker(live, sink, certificate)
    limiter = worker.email_limiter
    assert (limiter.global_limit, limiter.tenant_limit) == (0, 0)  # overrides, not the environment
    from impact_api.worker import WorkerSettings

    loaded = WorkerSettings.load(
        {
            "environment": "test",
            "worker_dsn": worker.s.worker_dsn,
            "public_origin": live.config["public_origin"],
            "invitation_secret": live.config["invitation_secret"],
            "delivery_secret": live.config["delivery_secret"],
            "email_adapter": "synthetic",
            "synthetic_sink": str(live.local / ("mail-" + uuid4().hex[:8] + ".jsonl")),
        }
    )
    assert (loaded.email_rate_limit, loaded.email_tenant_rate_limit, loaded.smtp_starttls) == (
        7,
        3,
        "required",
    )
