"""Email readiness (v0.27) without a database: the SMTP adapter against an in-process TLS SMTP
server (STARTTLS with certificate verification, AUTH PLAIN and LOGIN, wrong password, failed
upgrade, 5xx rejection, stable Message-ID), the email rate limiter, the owner's mail check with its
redacted transcript, and the deployment wiring of the new settings."""

import base64
import json
import os
import re
import smtplib
import socket
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "deploy"
sys.path.insert(0, str(DEPLOY))

import mail_check  # noqa: E402
from impact_api.mail_rate import EmailRateLimiter  # noqa: E402
from impact_api.worker import ConfigurationError, DeliveryError, SmtpAdapter, WorkerSettings  # noqa: E402
from smtp_sink import DEFAULT_SERVER_NAME, SmtpSink, make_certificate, server_context  # noqa: E402

SECRET_A = "a" * 48
SECRET_B = "b" * 48
PASSWORD = "qualification-pass-word-7"
USER = "smtp-user@qualification.test"


@pytest.fixture(scope="module")
def certificate(tmp_path_factory):
    cert, key = make_certificate(tmp_path_factory.mktemp("tls"))
    return cert, key


@pytest.fixture
def tls_sink(certificate):
    def start(**options):
        return SmtpSink(tls_context=server_context(*certificate), credentials={USER: PASSWORD}, **options)

    return start


def settings(**overrides):
    values = {
        "environment": "staging",
        "worker_dsn": "postgresql://worker@db/impact",
        "public_origin": "https://impact.example.org",
        "invitation_secret": SECRET_A,
        "delivery_secret": SECRET_B,
        "email_adapter": "smtp",
        "smtp_host": DEFAULT_SERVER_NAME,
        "smtp_port": 25,
        "smtp_username": USER,
        "smtp_password": PASSWORD,
        "smtp_timeout": 5,
    }
    values.update(overrides)
    s = WorkerSettings(**values)
    s.validate()
    return s


@pytest.fixture
def resolve_to_loopback(monkeypatch):
    """The provider's host name resolves to the in-process server: the adapter keeps every rule of
    a non-loopback host (STARTTLS mandatory, certificate checked against that name)."""
    ports = {}

    def get_socket(self, host, port, timeout):
        return socket.create_connection(("127.0.0.1", ports.get(host, port)), timeout)

    monkeypatch.setattr(smtplib.SMTP, "_get_socket", get_socket)
    return ports


def message(event="11111111-2222-4333-8444-555555555555"):
    m = EmailMessage()
    m["From"] = "impact@impact.example.org"
    m["To"] = "person@example.test"
    m["Subject"] = "Qualification"
    m["Message-ID"] = "<" + event + "@impact.example.org>"
    m["X-Impact-Delivery"] = event
    m.set_content("hello")
    return m


# -- adapter: STARTTLS and AUTH against the TLS server ----------------------------------------------


@pytest.mark.parametrize("mechanisms", [("PLAIN",), ("LOGIN",), ("PLAIN", "LOGIN")])
def test_starttls_with_verification_then_auth_delivers(
    tls_sink, certificate, resolve_to_loopback, mechanisms
):
    with tls_sink(auth_mechanisms=mechanisms) as sink:
        resolve_to_loopback[DEFAULT_SERVER_NAME] = sink.port
        adapter = SmtpAdapter(settings(smtp_ca_file=str(certificate[0]), smtp_port=sink.port))
        adapter.send(message())
        adapter.send(message())
    assert len(sink.messages) == 2 and all(m["tls"] and m["authenticated_as"] == USER for m in sink.messages)
    assert sink.authenticated == [(USER, True), (USER, True)]
    # Credentials and mail only after the upgrade: nothing but the handshake verbs in clear.
    assert sink.commands_in_clear() == []
    assert [m["message"]["Message-ID"] for m in sink.messages] == [message()["Message-ID"]] * 2


def test_wrong_password_is_a_retried_authentication_failure_and_sends_nothing(
    tls_sink, certificate, resolve_to_loopback
):
    with tls_sink() as sink:
        resolve_to_loopback[DEFAULT_SERVER_NAME] = sink.port
        adapter = SmtpAdapter(
            settings(smtp_ca_file=str(certificate[0]), smtp_port=sink.port, smtp_password="wrong")
        )
        with pytest.raises(DeliveryError) as failed:
            adapter.send(message())
    assert (failed.value.error_class, failed.value.permanent) == ("SMTP_AUTHENTICATION", False)
    assert sink.messages == [] and sink.authenticated == []
    assert "MAIL" not in [verb for verb, _ in sink.commands]


def test_untrusted_certificate_is_a_tls_failure_and_never_falls_back_to_clear_text(
    tls_sink, resolve_to_loopback
):
    # The system store does not know the per-run certificate: verification fails.
    with tls_sink() as sink:
        resolve_to_loopback[DEFAULT_SERVER_NAME] = sink.port
        adapter = SmtpAdapter(settings(smtp_port=sink.port))
        with pytest.raises(DeliveryError) as failed:
            adapter.send(message())
    assert (failed.value.error_class, failed.value.permanent) == ("TLS_FAILURE", False)
    assert sink.tls_failures == 1 and sink.messages == [] and sink.commands_in_clear() == []


def test_certificate_for_another_name_is_refused(tmp_path, resolve_to_loopback):
    other_cert, other_key = make_certificate(tmp_path, names=("other.qualification.test",), ips=())
    with SmtpSink(tls_context=server_context(other_cert, other_key), credentials={USER: PASSWORD}) as sink:
        resolve_to_loopback[DEFAULT_SERVER_NAME] = sink.port
        adapter = SmtpAdapter(settings(smtp_ca_file=str(other_cert), smtp_port=sink.port))
        with pytest.raises(DeliveryError) as failed:
            adapter.send(message())
    assert failed.value.error_class == "TLS_FAILURE" and sink.commands_in_clear() == []


def test_starttls_advertised_but_not_offered_ends_the_conversation_in_clear(resolve_to_loopback):
    with SmtpSink(advertise_starttls_without_tls=True, credentials={USER: PASSWORD}) as sink:
        resolve_to_loopback[DEFAULT_SERVER_NAME] = sink.port
        adapter = SmtpAdapter(settings(smtp_port=sink.port))
        with pytest.raises(DeliveryError) as failed:
            adapter.send(message())
    assert failed.value.error_class in {"TLS_FAILURE", "SMTP_CONNECTION"} and not failed.value.permanent
    assert sink.commands_in_clear() == [] and sink.messages == []


def test_non_loopback_host_without_starttls_is_refused_before_any_credential(resolve_to_loopback):
    with SmtpSink(credentials={USER: PASSWORD}, plain_auth_allowed=True) as sink:
        resolve_to_loopback[DEFAULT_SERVER_NAME] = sink.port
        adapter = SmtpAdapter(settings(smtp_port=sink.port))
        with pytest.raises(DeliveryError) as failed:
            adapter.send(message())
    assert (failed.value.error_class, failed.value.permanent) == ("STARTTLS_UNAVAILABLE", False)
    assert sink.commands_in_clear() == [] and sink.authenticated == []


def test_permanent_rejection_over_tls_is_dead_and_transient_is_retried(
    tls_sink, certificate, resolve_to_loopback
):
    with tls_sink(rejections=["550 5.1.1 Mailbox unavailable", "451 4.3.0 Try again later"]) as sink:
        resolve_to_loopback[DEFAULT_SERVER_NAME] = sink.port
        adapter = SmtpAdapter(settings(smtp_ca_file=str(certificate[0]), smtp_port=sink.port))
        with pytest.raises(DeliveryError) as permanent:
            adapter.send(message())
        with pytest.raises(DeliveryError) as transient:
            adapter.send(message())
    assert (permanent.value.error_class, permanent.value.permanent) == ("SMTP_PERMANENT_REJECTION", True)
    assert (transient.value.error_class, transient.value.permanent) == ("SMTP_TRANSIENT_REJECTION", False)


def test_required_starttls_applies_to_a_loopback_relay_too(tls_sink, certificate):
    # A local relay that offers TLS: `required` upgrades and verifies against the IP SAN.
    with tls_sink() as sink:
        s = settings(
            environment="test",
            smtp_host="127.0.0.1",
            smtp_port=sink.port,
            smtp_starttls="required",
            smtp_ca_file=str(certificate[0]),
        )
        SmtpAdapter(s).send(message())
        assert sink.messages[0]["tls"] and sink.commands_in_clear() == []
    with SmtpSink(credentials={USER: PASSWORD}, plain_auth_allowed=True) as plain:
        s = settings(
            environment="test", smtp_host="127.0.0.1", smtp_port=plain.port, smtp_starttls="required"
        )
        with pytest.raises(DeliveryError) as failed:
            SmtpAdapter(s).send(message())
    assert failed.value.error_class == "STARTTLS_UNAVAILABLE" and plain.authenticated == []


def test_new_settings_are_validated_and_never_printed(tmp_path):
    for overrides, reason in [
        ({"smtp_starttls": "never"}, "INVALID_SMTP_STARTTLS"),
        ({"smtp_ca_file": str(tmp_path / "missing.pem")}, "SMTP_CA_FILE_UNREADABLE"),
        ({"smtp_password": ""}, "SMTP_CREDENTIALS_INCOMPLETE"),
        ({"email_rate_limit": -1}, "INVALID_EMAIL_RATE_LIMIT"),
        ({"email_rate_window_seconds": 0}, "INVALID_EMAIL_RATE_LIMIT"),
        ({"email_tenant_rate_limit": 2_000_000}, "INVALID_EMAIL_RATE_LIMIT"),
    ]:
        with pytest.raises(ConfigurationError) as refused:
            settings(**overrides)
        assert refused.value.reason == reason, overrides
    s = settings(email_rate_limit=100, email_tenant_rate_limit=10, email_rate_window_seconds=3600)
    assert PASSWORD not in repr(s) and "worker@db" not in repr(s)
    loaded = WorkerSettings.load(
        {
            "environment": "staging",
            "worker_dsn": "postgresql://worker@db/impact",
            "public_origin": "https://impact.example.org",
            "invitation_secret": SECRET_A,
            "delivery_secret": SECRET_B,
            "email_adapter": "smtp",
            "smtp_host": "smtp.example.org",
            "smtp_port": "587",
            "smtp_username": USER,
            "smtp_password": PASSWORD,
            "email_rate_limit": "300",
            "email_tenant_rate_limit": "50",
            "email_rate_window_seconds": "60",
            "smtp_starttls": "auto",
        }
    )
    assert (loaded.email_rate_limit, loaded.email_tenant_rate_limit, loaded.smtp_starttls) == (
        300,
        50,
        "auto",
    )


# -- rate limiter ------------------------------------------------------------------------------------


def test_rate_limiter_windows_global_and_per_tenant_and_never_below_zero():
    t0 = datetime(2026, 10, 2, 12, 0, tzinfo=timezone.utc)
    limiter = EmailRateLimiter(global_limit=5, tenant_limit=3, window_seconds=60)
    assert limiter.allowance("A", t0) == 3 and limiter.allowance("B", t0) == 3
    limiter.record("A", t0, 3)
    assert limiter.allowance("A", t0) == 0 and limiter.allowance("B", t0) == 2
    limiter.record("B", t0 + timedelta(seconds=10), 2)
    assert limiter.allowance("B", t0 + timedelta(seconds=10)) == 0
    assert limiter.allowance("C", t0 + timedelta(seconds=10)) == 0  # global window exhausted
    assert limiter.retry_after("C", t0 + timedelta(seconds=10)) == pytest.approx(50.0)
    # A's claims leave the window first: the tenant window frees 3, the global window frees 3.
    at = t0 + timedelta(seconds=61)
    assert limiter.allowance("A", at) == 3 and limiter.allowance("C", at) == 3
    assert limiter.allowance("B", at) == 1  # B's two claims are still inside the window
    limiter.record("A", at, 3)
    assert limiter.allowance("A", at) == 0 and limiter.deferred == 0
    limiter.defer(4)
    assert limiter.deferred == 4
    assert limiter.allowance("B", t0 + timedelta(seconds=69)) == 0  # global: 2 (B) + 3 (A) in window
    assert limiter.allowance("B", t0 + timedelta(seconds=71)) == 2  # B's claims left; 3 (A) remain


def test_rate_limiter_disabled_means_no_limit_and_rejects_bad_values():
    limiter = EmailRateLimiter()
    assert not limiter.enabled and limiter.allowance("A", datetime.now(timezone.utc)) is None
    limiter.record("A", datetime.now(timezone.utc), 10)
    assert (
        limiter.global_claims == type(limiter.global_claims)()
        and limiter.retry_after("A", datetime.now(timezone.utc)) == 0
    )
    only_tenant = EmailRateLimiter(tenant_limit=1)
    now = datetime.now(timezone.utc)
    only_tenant.record("A", now, 1)
    assert only_tenant.allowance("A", now) == 0 and only_tenant.allowance("B", now) == 1
    for bad in [dict(global_limit=-1), dict(window_seconds=0), dict(window_seconds=10**6)]:
        with pytest.raises(ValueError):
            EmailRateLimiter(**bad)


# -- the owner's mail check -------------------------------------------------------------------------


def environment(sink, certificate=None, **overrides):
    env = {
        "IMPACT_SMTP_HOST": DEFAULT_SERVER_NAME,
        "IMPACT_SMTP_PORT": str(sink.port),
        "IMPACT_SMTP_USERNAME": USER,
        "IMPACT_SMTP_PASSWORD": PASSWORD,
        "IMPACT_SMTP_FROM": "impact@impact.example.org",
        "IMPACT_PUBLIC_ORIGIN": "https://impact.example.org",
        "IMPACT_SMTP_TIMEOUT": "5",
    }
    if certificate:
        env["IMPACT_SMTP_CA_FILE"] = str(certificate[0])
    env.update(overrides)
    return env


def run_check(env, to="owner@example.org"):
    import io

    out = io.StringIO()
    code = mail_check.main(["--to", to], env=env, out=out)
    text = out.getvalue()
    return code, text, json.loads(text.strip().splitlines()[-1])


def assert_no_secret(text):
    for form in [PASSWORD, USER, base64.b64encode(PASSWORD.encode()).decode()]:
        assert form not in text
    assert base64.b64encode(("\0" + USER + "\0" + PASSWORD).encode()).decode() not in text


@pytest.mark.parametrize("mechanisms", [("PLAIN",), ("LOGIN",)])
def test_mail_check_sends_over_tls_and_prints_a_redacted_transcript(
    tls_sink, certificate, resolve_to_loopback, mechanisms
):
    with tls_sink(auth_mechanisms=mechanisms) as sink:
        resolve_to_loopback[DEFAULT_SERVER_NAME] = sink.port
        code, text, result = run_check(environment(sink, certificate))
    assert (
        code == 0 and result["ok"] and result["reason"] == "SENT" and result["tls"] and result["auth"] == "ok"
    )
    assert result["message_id"].endswith("@impact.example.org>")
    [sent] = sink.messages
    assert (
        sent["tls"]
        and sent["authenticated_as"] == USER
        and sent["message"]["Subject"] == "Impact Platform email check"
    )
    assert "STARTTLS" in text and "[redacted]" in text and "250" in text
    assert_no_secret(text)
    assert re.search(r"send: 'AUTH (PLAIN|LOGIN) \[redacted\]", text)


def test_mail_check_reports_a_wrong_password_without_revealing_it(tls_sink, certificate, resolve_to_loopback):
    with tls_sink() as sink:
        resolve_to_loopback[DEFAULT_SERVER_NAME] = sink.port
        code, text, result = run_check(
            environment(sink, certificate, IMPACT_SMTP_PASSWORD="not-the-password")
        )
    assert code == 1 and (result["ok"], result["reason"], result["tls"]) == (
        False,
        "SMTP_AUTHENTICATION",
        True,
    )
    assert "535" in text and "not-the-password" not in text
    assert base64.b64encode(("\0" + USER + "\0not-the-password").encode()).decode() not in text
    assert sink.messages == []


def test_mail_check_never_sends_in_clear_to_a_provider_and_refuses_bad_configuration(
    resolve_to_loopback, tls_sink
):
    with SmtpSink(credentials={USER: PASSWORD}, plain_auth_allowed=True) as plain:
        resolve_to_loopback[DEFAULT_SERVER_NAME] = plain.port
        code, text, result = run_check(environment(plain))
        assert code == 1 and result["reason"] == "STARTTLS_UNAVAILABLE" and plain.commands_in_clear() == []
    with tls_sink() as sink:
        resolve_to_loopback[DEFAULT_SERVER_NAME] = sink.port
        code, _, result = run_check(environment(sink))  # certificate not trusted: no CA file
        assert code == 1 and result["reason"] == "TLS_FAILURE" and sink.messages == []
        code, _, result = run_check(environment(sink, certificate=None, IMPACT_SMTP_PASSWORD=""))
        assert code == 2 and result["reason"] == "SMTP_CREDENTIALS_INCOMPLETE"
        code, _, result = run_check(environment(sink), to="not-an-address")
        assert code == 2 and result["reason"] == "INVALID_ADDRESS"
        code, _, result = run_check(environment(sink, IMPACT_SMTP_STARTTLS="never"))
        assert code == 2 and result["reason"] == "INVALID_SMTP_STARTTLS"
    # A closed port is a connection failure, reported as such.
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        free_port = probe.getsockname()[1]
    env = environment(sink, IMPACT_SMTP_HOST="127.0.0.1", IMPACT_SMTP_PORT=str(free_port))
    code, _, result = run_check(env)
    assert code == 1 and result["reason"] == "SMTP_CONNECTION"


def test_redaction_covers_login_exchanges_and_literal_forms():
    lines = [
        "send: 'ehlo host\\r\\n'",
        "reply: b'250-AUTH PLAIN LOGIN\\r\\n'",
        "send: 'AUTH LOGIN " + base64.b64encode(USER.encode()).decode() + "\\r\\n'",
        "reply: b'334 UGFzc3dvcmQ6\\r\\n'",
        "send: '" + base64.b64encode(PASSWORD.encode()).decode() + "\\r\\n'",
        "reply: b'235 2.7.0 Authentication successful\\r\\n'",
        "send: 'mail FROM:<impact@impact.example.org>\\r\\n'",
        "data: (250, b'OK " + PASSWORD + "')",
    ]
    redacted = mail_check.redact(lines, USER, PASSWORD)
    assert redacted[2] == "send: 'AUTH LOGIN [redacted]\\r\\n'" and redacted[4] == "send: [redacted]"
    assert redacted[6].startswith("send: 'mail FROM") and "[redacted]" in redacted[7]
    assert_no_secret("\n".join(redacted))


def test_mail_check_script_is_strict_and_refuses_bad_arguments(tmp_path):
    script = DEPLOY / "mail-check.sh"
    assert os.access(script, os.X_OK) and "set -euo pipefail" in script.read_text()
    for args in ["", "not-an-email", "a@example.org extra"]:
        result = subprocess.run(
            ["bash", "-c", "deploy/mail-check.sh " + args],
            cwd=ROOT,
            env={**os.environ, "IMPACT_HOME": str(tmp_path)},
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode != 0 and ("usage" in result.stderr or "not an e-mail" in result.stderr), args
    text = script.read_text()
    assert "mail_check.py:/app/deploy/mail_check.py:ro" in text and "admin-actions.log" in text
    assert "transcript" not in text.split("admin-actions.log")[0].split('log "mail check')[0][-80:]


def test_compose_and_update_pass_the_email_settings_to_the_worker():
    compose = (DEPLOY / "compose.yaml").read_text()
    worker = re.search(r"\n  worker:\n(.*?)(?=\n  [a-z-]+:\n)", compose, re.S).group(1)
    for line in [
        "IMPACT_SMTP_STARTTLS: ${SMTP_STARTTLS:-auto}",
        "IMPACT_SMTP_CA_FILE: ${SMTP_CA_FILE:-}",
        "IMPACT_EMAIL_RATE_LIMIT: ${EMAIL_RATE_LIMIT:-0}",
        "IMPACT_EMAIL_TENANT_RATE_LIMIT: ${EMAIL_TENANT_RATE_LIMIT:-0}",
        "IMPACT_EMAIL_RATE_WINDOW_SECONDS: ${EMAIL_RATE_WINDOW_SECONDS:-60}",
        "IMPACT_SMTP_PASSWORD: ${SMTP_PASSWORD:-}",
    ]:
        assert line in worker, line
    update = (DEPLOY / "update.sh").read_text()
    for key in [
        "SMTP_STARTTLS",
        "SMTP_CA_FILE",
        "EMAIL_RATE_LIMIT",
        "EMAIL_TENANT_RATE_LIMIT",
        "EMAIL_RATE_WINDOW_SECONDS",
    ]:
        assert key in update.split("for key in SMTP_HOST", 1)[1].split("; do", 1)[0], key
    # The password may live in secrets.env: every KEY=value line of it reaches compose.env, and
    # every value of secrets.env is scrubbed from the deployment log and status page.
    assert "grep -E '^[A-Z0-9_]+=' \"$SECRETS_FILE\"" in update
    assert "ssl.create_default_context(cafile=" in (ROOT / "apps/api/impact_api/worker.py").read_text()
