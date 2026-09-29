"""Worker runtime and outbox dispatcher (v0.16): `python -m impact_api.worker`.

One process per worker login (`impact_worker_login` -> `impact_worker`). Each iteration:

1. `impact.worker_tenants(at)` names the Provisioning, Active and Suspended tenants with their
   lifecycle state and due delivery counts (identifiers only; migration 0018). Deliveries queued
   before a suspension carry held_at and are never claimed; the scans below run for Active only.
2. Per tenant, in its own transaction under the tenant advisory lock and a transaction-local
   tenant context, due `outbox_delivery` rows are claimed with `FOR UPDATE SKIP LOCKED`: the row
   becomes LEASED to this worker with `lease_generation + 1`, an expiry and one more attempt.
3. Per claimed row, a read-only transaction rechecks the intent (current invitation generation,
   pending challenge, active recipient) and builds the message; the connection is closed, then the
   channel adapter is called outside any transaction; a new transaction records the outcome. Every
   outcome update carries the lease owner and generation, so a holder whose lease was taken over
   is refused (it may already have sent: email delivery is at least once).
4. IN_APP intents are transactional: the fenced SENT update, the `notification_delivery` row and
   the consumer receipt commit together, so the visible effect happens exactly once.
5. Per tenant scans: delegated-authority expiry reminders 14 and 3 days ahead (idempotent per
   principal, expiry instant and threshold) and cancellation of jobs that had not started.
6. A heartbeat row for operators (`GET /v1/platform/workers`).

Failures back off exponentially with jitter (BACKOFF_BASE_SECONDS doubling up to BACKOFF_CAP_SECONDS,
multiplied by a uniform factor in [0.5, 1.0)) and become DEAD after `max_attempts` claims or at once
on a permanent error class. Only an error class is recorded, never a message, address or secret.
SIGTERM/SIGINT finish the delivery in progress, release the leases claimed but not started and
mark the heartbeat STOPPED.
"""

import argparse
import hashlib
import ipaddress
import json
import logging
import os
import random
import re
import signal
import smtplib
import socket
import ssl
import sys
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, fields
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import formatdate
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlparse
from uuid import NAMESPACE_URL, uuid4, uuid5

import psycopg
from cryptography.exceptions import InvalidTag
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from .delivery import (
    channel_code,
    channel_code_hash,
    enqueue,
    invitation_token,
    invitation_url,
    render,
    unseal_recipient,
)
from .identity_profile import email_hash, normalize_email
from .store import audit, write

BUILD = "0.16.0"
LOG = logging.getLogger("impact.worker")
BACKOFF_BASE_SECONDS = 30
BACKOFF_CAP_SECONDS = 3600
REMINDER_DAYS = (14, 3)
LOOPBACK = {"127.0.0.1", "::1", "localhost"}
PRE_START = ("Requested", "Validating", "Queued")
BOOLEAN = {"require_unprivileged_db"}
INTEGER = {"smtp_port", "synthetic_failures", "lease_seconds", "batch_size", "max_attempts", "scan_seconds"}
FLOAT = {"smtp_timeout", "synthetic_delay", "poll_seconds"}
WORKER_QUERY = (
    "SELECT current_user AS login,rolsuper,rolbypassrls,"
    "pg_has_role(current_user,'impact_owner','MEMBER') AS owns_schema,"
    "pg_has_role(current_user,'impact_worker','MEMBER') AS worker,"
    "COALESCE((SELECT array_agg(g.rolname::text ORDER BY g.rolname) FROM pg_auth_members m "
    "JOIN pg_roles g ON g.oid=m.roleid WHERE m.member=l.oid),'{}') AS memberships "
    "FROM pg_roles l WHERE l.rolname=current_user"
)


def utcnow():
    return datetime.now(timezone.utc)


class ConfigurationError(RuntimeError):
    """The worker refuses to start or to open a transaction; `reason` is a code, never a login."""

    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


class DeliveryError(Exception):
    def __init__(self, error_class, permanent=False):
        super().__init__(error_class)
        self.error_class = error_class
        self.permanent = permanent


@dataclass(frozen=True)
class WorkerSettings:
    environment: str
    worker_dsn: str
    public_origin: str
    invitation_secret: str = ""
    delivery_secret: str = ""
    email_adapter: str = "synthetic"
    smtp_host: str = "127.0.0.1"
    smtp_port: int = 25
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = "impact-platform@localhost.localdomain"
    smtp_timeout: float = 20.0
    synthetic_sink: str = ""
    synthetic_failures: int = 0
    synthetic_delay: float = 0.0
    require_unprivileged_db: bool = False
    lease_seconds: int = 60
    poll_seconds: float = 5.0
    batch_size: int = 10
    max_attempts: int = 6
    scan_seconds: int = 60

    @property
    def unprivileged_db_required(self):
        return self.environment in {"staging", "production"} or self.require_unprivileged_db

    @classmethod
    def load(cls, overrides=None):
        """IMPACT_WORKER_CONFIG_FILE (JSON), then IMPACT_<FIELD> environment variables, then
        overrides. The worker never reads the API configuration or its connection strings."""
        path = os.environ.get("IMPACT_WORKER_CONFIG_FILE")
        data = json.loads(Path(path).read_text()) if path else {}
        for field in fields(cls):
            value = os.environ.get("IMPACT_" + field.name.upper())
            if value is not None:
                data[field.name] = value
        data.update(overrides or {})
        for name, value in list(data.items()):
            if name in BOOLEAN and isinstance(value, str):
                lowered = value.strip().lower()
                if lowered not in {"1", "true", "yes", "on", "0", "false", "no", "off", ""}:
                    raise ConfigurationError("INVALID_" + name.upper())
                data[name] = lowered in {"1", "true", "yes", "on"}
            elif name in INTEGER:
                data[name] = int(value)
            elif name in FLOAT:
                data[name] = float(value)
        s = cls(**{k: v for k, v in data.items() if k in {f.name for f in fields(cls)}})
        s.validate()
        return s

    def validate(self):
        production = self.environment in {"staging", "production"}
        if self.environment not in {"development", "test", "staging", "production"}:
            raise ConfigurationError("INVALID_ENVIRONMENT")
        if not self.worker_dsn:
            raise ConfigurationError("WORKER_DSN_REQUIRED")
        if len(self.invitation_secret) < 48 or len(self.delivery_secret) < 48:
            raise ConfigurationError("DELIVERY_SECRETS_REQUIRED")
        if self.invitation_secret == self.delivery_secret:
            raise ConfigurationError("DELIVERY_SECRETS_NOT_DISTINCT")
        if self.email_adapter not in {"smtp", "synthetic"}:
            raise ConfigurationError("INVALID_EMAIL_ADAPTER")
        if production and (self.email_adapter != "smtp" or not self.public_origin.startswith("https://")):
            raise ConfigurationError("SMTP_AND_HTTPS_REQUIRED")
        if self.email_adapter == "synthetic" and not self.synthetic_sink:
            raise ConfigurationError("SYNTHETIC_SINK_REQUIRED")
        if self.email_adapter == "smtp" and not production and self.smtp_host not in LOOPBACK:
            # No real email is ever sent from development or test.
            raise ConfigurationError("SMTP_HOST_REFUSED")
        normalize_email(self.smtp_from)
        if not (
            5 <= self.lease_seconds <= 3600 and 1 <= self.batch_size <= 100 and 1 <= self.max_attempts <= 20
        ):
            raise ConfigurationError("INVALID_LIMITS")
        if self.smtp_timeout >= self.lease_seconds:
            raise ConfigurationError("LEASE_SHORTER_THAN_SMTP_TIMEOUT")


def is_loopback(host):
    if host in LOOPBACK:
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


class SmtpAdapter:
    """stdlib smtplib. STARTTLS with certificate verification is mandatory for any non-loopback
    host, and a non-loopback host is refused outside staging/production."""

    name = "smtp"

    def __init__(self, s):
        self.s = s

    def send(self, message):
        s = self.s
        loopback = is_loopback(s.smtp_host)
        if not loopback and s.environment not in {"staging", "production"}:
            raise DeliveryError("SMTP_HOST_REFUSED", permanent=True)
        try:
            with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=s.smtp_timeout) as smtp:
                smtp.ehlo()
                if not loopback:
                    if not smtp.has_extn("starttls"):
                        raise DeliveryError("STARTTLS_UNAVAILABLE")
                    smtp.starttls(context=ssl.create_default_context())
                    smtp.ehlo()
                if s.smtp_username:
                    smtp.login(s.smtp_username, s.smtp_password)
                refused = smtp.send_message(message)
                if refused:
                    raise DeliveryError("RECIPIENT_REFUSED", permanent=True)
        except DeliveryError:
            raise
        except smtplib.SMTPRecipientsRefused:
            raise DeliveryError("RECIPIENT_REFUSED", permanent=True) from None
        except smtplib.SMTPAuthenticationError:
            raise DeliveryError("SMTP_AUTHENTICATION") from None
        except smtplib.SMTPResponseException as exc:
            if 500 <= exc.smtp_code < 600:
                raise DeliveryError("SMTP_PERMANENT_REJECTION", permanent=True) from None
            raise DeliveryError("SMTP_TRANSIENT_REJECTION") from None
        except ssl.SSLError:
            raise DeliveryError("TLS_FAILURE") from None
        except (smtplib.SMTPException, OSError):
            raise DeliveryError("SMTP_CONNECTION") from None


class SyntheticAdapter:
    """Test and development only: appends each message as one JSON line to a local sink file, and
    can be told to fail its first N sends or to take a fixed time per send."""

    name = "synthetic"

    def __init__(self, s):
        self.s = s
        self.failures_left = s.synthetic_failures
        self.sent = 0

    def send(self, message):
        if self.s.synthetic_delay:
            time.sleep(self.s.synthetic_delay)
        if self.failures_left > 0:
            self.failures_left -= 1
            raise DeliveryError("SYNTHETIC_FAILURE")
        sink = Path(self.s.synthetic_sink)
        sink.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "event_id": message["X-Impact-Delivery"],
            "from": message["From"],
            "to": message["To"],
            "subject": message["Subject"],
            "body": message.get_content(),
            "at": utcnow().isoformat(),
        }
        descriptor = os.open(sink, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        with os.fdopen(descriptor, "a") as handle:
            handle.write(json.dumps(record) + "\n")
        self.sent += 1


def make_adapter(s):
    return SmtpAdapter(s) if s.email_adapter == "smtp" else SyntheticAdapter(s)


FENCE = (
    " WHERE tenant_id=%(tenant)s AND event_id=%(event)s AND state='LEASED'"
    " AND lease_owner=%(owner)s AND lease_generation=%(generation)s"
)


def empty_summary():
    keys = ["tenants", "claimed", "sent", "retried", "dead", "superseded", "stale_refused", "released"]
    return dict.fromkeys(keys + ["reminders", "cancelled", "refused_cancellations"], 0)


class Worker:
    def __init__(self, s, clock=None, adapter=None, rng=None, worker_id=None, probe=None):
        self.s = s
        self.clock = clock or utcnow
        self.adapter = adapter or make_adapter(s)
        self.rng = rng or random.Random()
        self.worker_id = worker_id or re.sub(
            r"[^A-Za-z0-9._:-]",
            "-",
            socket.gethostname()[:60] + ":" + str(os.getpid()) + ":" + uuid4().hex[:8],
        )
        # Called just before every external call; tests use it to prove no transaction is open.
        self.probe = probe
        self.stop_event = threading.Event()
        self.connection = None
        self.started_at = self.clock()
        self.last_scan = None
        self.totals = {"iterations": 0, "sent": 0, "retried": 0, "dead": 0}

    # -- database -------------------------------------------------------------------------------

    @property
    def stopping(self):
        return self.stop_event.is_set()

    def check_login(self, c):
        """Under IMPACT_REQUIRE_UNPRIVILEGED_DB (always in staging/production) the worker's own
        login must be non-superuser, non-BYPASSRLS, not impact_owner and a member of impact_worker
        and nothing else; checked on every connection, as the API checks its logins."""
        if not self.s.unprivileged_db_required:
            return
        row = c.execute(WORKER_QUERY).fetchone()
        if row["rolsuper"] or row["rolbypassrls"] or row["owns_schema"]:
            LOG.error("worker login refused reason=PRIVILEGED_WORKER_CONNECTION login=%s", row["login"])
            raise ConfigurationError("PRIVILEGED_WORKER_CONNECTION")
        if not row["worker"] or list(row["memberships"]) != ["impact_worker"]:
            LOG.error("worker login refused reason=WORKER_LOGIN_TOPOLOGY login=%s", row["login"])
            raise ConfigurationError("WORKER_LOGIN_TOPOLOGY")

    @contextmanager
    def transaction(self, tenant=None, lock=False):
        """One connection per transaction, closed afterwards: nothing is held across an external
        call, and on the single-connection development database the API is never starved."""
        connection = psycopg.connect(
            self.s.worker_dsn,
            row_factory=dict_row,
            connect_timeout=5,
            prepare_threshold=None,
            autocommit=True,
        )
        self.connection = connection
        try:
            self.check_login(connection)
            with connection.transaction():
                connection.execute("SET LOCAL ROLE impact_worker")
                connection.execute("SET LOCAL statement_timeout='8s'")
                connection.execute("SET LOCAL lock_timeout='3s'")
                if tenant:
                    connection.execute("SELECT set_config('impact.tenant_id',%s,true)", (str(tenant),))
                    if lock:
                        connection.execute(
                            "SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (str(tenant),)
                        )
                yield connection
        finally:
            connection.close()
            self.connection = None

    # -- iteration ------------------------------------------------------------------------------

    def run_once(self):
        at = self.clock()
        summary = empty_summary()
        with self.transaction() as c:
            tenants = c.execute("SELECT * FROM impact.worker_tenants(%s)", (at,)).fetchall()
        scan = self.last_scan is None or (at - self.last_scan).total_seconds() >= self.s.scan_seconds
        for row in tenants:
            if self.stopping:
                break
            summary["tenants"] += 1
            tenant = str(row["tenant_id"])
            if row["due_deliveries"]:
                self.dispatch(tenant, summary)
            if scan and row["lifecycle_state"] == "Active" and not self.stopping:
                self.remind(tenant, summary)
                self.cancel_jobs(tenant, summary)
        if scan:
            self.last_scan = at
        self.totals["iterations"] += 1
        for key in ["sent", "retried", "dead"]:
            self.totals[key] += summary[key]
        self.heartbeat("STOPPING" if self.stopping else "RUNNING")
        return summary

    def heartbeat(self, state):
        at = self.clock()
        with self.transaction() as c:
            c.execute(
                "INSERT INTO impact.worker_heartbeat(worker_id,build,state,started_at,beat_at,stopped_at,iterations,sent,retried,dead) "
                "VALUES(%(id)s,%(build)s,%(state)s,%(started)s,%(at)s,%(stopped)s,%(iterations)s,%(sent)s,%(retried)s,%(dead)s) "
                "ON CONFLICT(worker_id) DO UPDATE SET state=EXCLUDED.state,beat_at=EXCLUDED.beat_at,"
                "stopped_at=EXCLUDED.stopped_at,iterations=EXCLUDED.iterations,sent=EXCLUDED.sent,"
                "retried=EXCLUDED.retried,dead=EXCLUDED.dead",
                {
                    "id": self.worker_id,
                    "build": BUILD,
                    "state": state,
                    "started": self.started_at,
                    "at": at,
                    "stopped": at if state == "STOPPED" else None,
                    **self.totals,
                },
            )

    def run_forever(self):
        def request_stop(signum, _frame):
            LOG.info("worker %s stopping on signal %s", self.worker_id, signum)
            self.stop_event.set()

        signal.signal(signal.SIGTERM, request_stop)
        signal.signal(signal.SIGINT, request_stop)
        LOG.info("worker %s started build=%s adapter=%s", self.worker_id, BUILD, self.adapter.name)
        while not self.stopping:
            try:
                summary = self.run_once()
                if any(summary[k] for k in summary if k != "tenants"):
                    LOG.info("worker iteration %s", json.dumps(summary, sort_keys=True))
            except ConfigurationError:
                raise
            except psycopg.Error as exc:
                LOG.warning("worker iteration failed class=%s", type(exc).__name__)
            self.stop_event.wait(self.s.poll_seconds)
        self.heartbeat("STOPPED")
        LOG.info("worker %s stopped", self.worker_id)

    # -- dispatch -------------------------------------------------------------------------------

    def dispatch(self, tenant, summary):
        rows = self.claim(tenant, summary)
        for index, row in enumerate(rows):
            if self.stopping:
                summary["released"] += self.release(tenant, rows[index:])
                break
            self.process(tenant, row, summary)

    def claim(self, tenant, summary):
        """Lease up to batch_size due rows of one tenant; returns them in event order."""
        at = self.clock()
        with self.transaction(tenant, lock=True) as c:
            # A holder that crashed on its last permitted attempt is not retried.
            expired = c.execute(
                "UPDATE impact.outbox_delivery SET state='DEAD',completed_at=%(at)s,lease_owner=NULL,"
                "lease_expires_at=NULL,lease_generation=lease_generation+1,last_error_class='LEASE_EXPIRED' "
                "WHERE tenant_id=%(tenant)s AND channel IS NOT NULL AND held_at IS NULL AND state='LEASED' "
                "AND lease_expires_at<=%(at)s AND attempts>=%(max)s",
                {"at": at, "tenant": tenant, "max": self.s.max_attempts},
            ).rowcount
            rows = c.execute(
                "WITH due AS (SELECT event_id FROM impact.outbox_delivery WHERE tenant_id=%(tenant)s "
                "AND channel IS NOT NULL AND held_at IS NULL AND ((state='PENDING' AND next_attempt_at<=%(at)s) "
                "OR (state='LEASED' AND lease_expires_at<=%(at)s)) ORDER BY next_attempt_at,event_id "
                "LIMIT %(limit)s FOR UPDATE SKIP LOCKED) "
                "UPDATE impact.outbox_delivery d SET state='LEASED',lease_owner=%(owner)s,"
                "lease_generation=d.lease_generation+1,lease_expires_at=%(expires)s,attempts=d.attempts+1,"
                "last_attempt_at=%(at)s FROM due WHERE d.tenant_id=%(tenant)s AND d.event_id=due.event_id "
                "RETURNING d.event_id,d.channel,d.template,d.reference_id,d.reference_generation,"
                "d.recipient_sealed,d.lease_generation,d.attempts",
                {
                    "tenant": tenant,
                    "at": at,
                    "limit": self.s.batch_size,
                    "owner": self.worker_id,
                    "expires": at + timedelta(seconds=self.s.lease_seconds),
                },
            ).fetchall()
        summary["dead"] += expired
        summary["claimed"] += len(rows)
        return sorted(rows, key=lambda r: str(r["event_id"]))

    def fenced(self, c, tenant, row, assignments, values=None):
        """Apply an outcome only if this worker still holds exactly this lease generation."""
        params = {
            "tenant": tenant,
            "event": str(row["event_id"]),
            "owner": self.worker_id,
            "generation": row["lease_generation"],
            **(values or {}),
        }
        return c.execute("UPDATE impact.outbox_delivery SET " + assignments + FENCE, params).rowcount == 1

    def release(self, tenant, rows):
        released = 0
        with self.transaction(tenant, lock=True) as c:
            for row in rows:
                released += self.fenced(
                    c,
                    tenant,
                    row,
                    "state='PENDING',lease_owner=NULL,lease_expires_at=NULL,attempts=attempts-1",
                )
        return released

    def process(self, tenant, row, summary):
        if row["channel"] == "IN_APP":
            self.deliver_in_app(tenant, row, summary)
            return
        try:
            with self.transaction(tenant) as c:
                decision = self.prepare(c, tenant, row)
        except psycopg.Error as exc:
            LOG.warning("delivery %s prepare failed class=%s", row["event_id"], type(exc).__name__)
            decision = ("retry", "PREPARE_FAILED")
        if decision[0] != "send":
            self.record(tenant, row, summary, *decision)
            return
        message = decision[1]
        if self.probe:
            self.probe(self)
        try:
            self.adapter.send(message)
        except DeliveryError as exc:
            self.record(tenant, row, summary, "dead" if exc.permanent else "retry", exc.error_class)
            return
        except Exception as exc:  # an adapter defect is a failed attempt, never a crash
            LOG.warning("delivery %s adapter failure class=%s", row["event_id"], type(exc).__name__)
            self.record(tenant, row, summary, "retry", "ADAPTER_FAILURE")
            return
        self.record(tenant, row, summary, "sent", None)

    def backoff(self, attempts):
        delay = min(BACKOFF_CAP_SECONDS, BACKOFF_BASE_SECONDS * 2 ** max(0, attempts - 1))
        return timedelta(seconds=delay * self.rng.uniform(0.5, 1.0))

    def record(self, tenant, row, summary, outcome, error_class):
        at = self.clock()
        if outcome == "retry" and row["attempts"] >= self.s.max_attempts:
            outcome = "dead"
        assignments = {
            "sent": "state='SENT',sent_at=%(at)s,completed_at=%(at)s,lease_owner=NULL,lease_expires_at=NULL,"
            "last_error_class=NULL",
            "retry": "state='PENDING',next_attempt_at=%(next)s,lease_owner=NULL,lease_expires_at=NULL,"
            "last_error_class=%(error)s",
            "dead": "state='DEAD',completed_at=%(at)s,lease_owner=NULL,lease_expires_at=NULL,"
            "last_error_class=%(error)s",
            "supersede": "state='SUPERSEDED',completed_at=%(at)s,lease_owner=NULL,lease_expires_at=NULL,"
            "last_error_class=%(error)s",
        }[outcome]
        with self.transaction(tenant, lock=True) as c:
            applied = self.fenced(
                c,
                tenant,
                row,
                assignments,
                {"at": at, "next": at + self.backoff(row["attempts"]), "error": error_class},
            )
        if not applied:
            summary["stale_refused"] += 1
            LOG.warning("delivery %s outcome refused: lease generation superseded", row["event_id"])
            return False
        summary[{"sent": "sent", "retry": "retried", "dead": "dead", "supersede": "superseded"}[outcome]] += 1
        LOG.info(
            "delivery %s template=%s outcome=%s class=%s attempt=%s",
            row["event_id"],
            row["template"],
            outcome,
            error_class,
            row["attempts"],
        )
        return True

    def prepare(self, c, tenant, row):
        """Recheck the intent inside the tenant fence and build the message. Returns ("send",
        message), ("supersede", reason) or ("dead", reason). Reads only."""
        template, reference = row["template"], str(row["reference_id"])
        try:
            address = unseal_recipient(
                self.s.delivery_secret, tenant, template, reference, row["recipient_sealed"]
            )
        except (InvalidTag, ValueError):
            return ("dead", "RECIPIENT_UNREADABLE")
        at = self.clock()
        if template == "MEMBER_INVITATION":
            invitation = c.execute(
                "SELECT * FROM impact.member_invitation WHERE tenant_id=%s AND invitation_id=%s",
                (tenant, reference),
            ).fetchone()
            if not invitation or invitation["consumed_at"] or invitation["revoked_at"]:
                return ("supersede", "INVITATION_CLOSED")
            if invitation["expires_at"] <= at:
                return ("supersede", "INVITATION_EXPIRED")
            if str(invitation["generation"]) != row["reference_generation"]:
                return ("supersede", "INVITATION_RESENT")
            if bytes(invitation["intended_email_hash"]) != email_hash(address):
                return ("supersede", "RECIPIENT_CHANGED")
            token = invitation_token(self.s.invitation_secret, tenant, reference, row["reference_generation"])
            if bytes(invitation["token_hash"]) != hashlib.sha256(token.encode()).digest():
                return ("dead", "SIGNING_KEY_MISMATCH")
            subject, body = render(
                template,
                url=invitation_url(self.s.public_origin, tenant, token),
                expires_at=invitation["expires_at"].astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M"),
            )
        elif template == "RECOVERY_CHANNEL_VERIFICATION":
            challenge = c.execute(
                "SELECT * FROM impact.recovery_channel_challenge WHERE tenant_id=%s AND challenge_id=%s",
                (tenant, reference),
            ).fetchone()
            if not challenge or challenge["state"] != "PENDING":
                return ("supersede", "CHALLENGE_CLOSED")
            if challenge["expires_at"] <= at:
                return ("supersede", "CHALLENGE_EXPIRED")
            if bytes(challenge["email_hash"]) != email_hash(address):
                return ("supersede", "RECIPIENT_CHANGED")
            code = channel_code(self.s.delivery_secret, reference)
            if bytes(challenge["code_hash"]) != channel_code_hash(self.s.delivery_secret, reference, code):
                return ("dead", "SIGNING_KEY_MISMATCH")
            subject, body = render(
                template,
                code=code,
                expires_at=challenge["expires_at"].astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M"),
            )
        else:
            return ("dead", "UNKNOWN_TEMPLATE")
        message = EmailMessage()
        message["From"] = self.s.smtp_from
        message["To"] = address
        message["Subject"] = subject
        message["Date"] = formatdate(usegmt=True)
        # Stable across attempts, so a receiving system can discard a duplicate of a retried send.
        message["Message-ID"] = (
            "<" + str(row["event_id"]) + "@" + (urlparse(self.s.public_origin).hostname or "impact") + ">"
        )
        message["Auto-Submitted"] = "auto-generated"
        message["X-Impact-Delivery"] = str(row["event_id"])
        message.set_content(body)
        return ("send", message)

    def deliver_in_app(self, tenant, row, summary):
        """The in-app channel's effect is a database row, so it commits with the fenced outcome."""
        at = self.clock()
        outcome, reason = "sent", None
        with self.transaction(tenant, lock=True) as c:
            notice = c.execute(
                "SELECT n.recipient_id,p.active FROM impact.notification_current n "
                "LEFT JOIN impact.tenant_principal p ON p.tenant_id=n.tenant_id AND p.principal_id=n.recipient_id "
                "WHERE n.tenant_id=%s AND n.object_id=%s",
                (tenant, str(row["reference_id"])),
            ).fetchone()
            if not notice:
                outcome, reason = "supersede", "NOTICE_MISSING"
            elif not notice["active"]:
                outcome, reason = "supersede", "RECIPIENT_INACTIVE"
            if outcome == "sent":
                applied = self.fenced(
                    c,
                    tenant,
                    row,
                    "state='SENT',sent_at=%(at)s,completed_at=%(at)s,lease_owner=NULL,lease_expires_at=NULL,"
                    "last_error_class=NULL",
                    {"at": at},
                )
                if applied:
                    c.execute(
                        "INSERT INTO impact.notification_delivery VALUES(%s,%s,'IN_APP',%s,%s) ON CONFLICT DO NOTHING",
                        (tenant, str(row["reference_id"]), str(row["event_id"]), at),
                    )
                    c.execute(
                        "INSERT INTO impact.consumer_receipt VALUES(%s,'worker.in_app',%s,%s) ON CONFLICT DO NOTHING",
                        (tenant, str(row["event_id"]), at),
                    )
                    summary["sent"] += 1
                else:
                    summary["stale_refused"] += 1
                    LOG.warning("delivery %s outcome refused: lease generation superseded", row["event_id"])
                return
        self.record(tenant, row, summary, outcome, reason)

    # -- scheduled scans ------------------------------------------------------------------------

    def service_principal(self, c, tenant):
        """The tenant's worker principal: SERVICE kind, no identity, membership or grant. It is
        the recorded author of what the worker writes, so nothing is attributed to a person."""
        principal = str(uuid5(NAMESPACE_URL, "impact-worker-principal-v1:" + tenant))
        c.execute(
            "INSERT INTO impact.tenant_principal(tenant_id,principal_id,identity_id,principal_kind,active) "
            "VALUES(%s,%s,NULL,'SERVICE',true) ON CONFLICT DO NOTHING",
            (tenant, principal),
        )
        return SimpleNamespace(tenant_id=tenant, principal_id=principal, identity=None)

    def remind(self, tenant, summary):
        """In-app reminders to an administrator whose delegation ceilings expire within 14 days,
        again within 3 days; one per (principal, expiry instant, threshold). A renewal moves the
        expiry and so re-arms both. The 14-day notice is not sent once inside the 3-day window."""
        at = self.clock()
        with self.transaction(tenant, lock=True) as c:
            rows = c.execute(
                "SELECT a.principal_id,a.expires_at,count(*) AS ceilings,min(m.object_id::text) AS membership_id "
                "FROM impact.grant_authority a JOIN impact.tenant_principal p ON p.tenant_id=a.tenant_id "
                "AND p.principal_id=a.principal_id JOIN impact.membership_current m ON m.tenant_id=p.tenant_id "
                "AND m.identity_id=p.identity_id JOIN impact.object_registry r ON r.tenant_id=m.tenant_id "
                "AND r.object_id=m.object_id WHERE a.tenant_id=%s AND p.active AND r.lifecycle_state='Active' "
                "AND a.expires_at>%s AND a.expires_at<=%s GROUP BY a.principal_id,a.expires_at "
                "ORDER BY a.principal_id,a.expires_at LIMIT 200",
                (tenant, at, at + timedelta(days=REMINDER_DAYS[0])),
            ).fetchall()
            ctx = None
            for row in rows:
                days = (
                    REMINDER_DAYS[1]
                    if row["expires_at"] - at <= timedelta(days=REMINDER_DAYS[1])
                    else REMINDER_DAYS[0]
                )
                notification_id = str(
                    uuid5(
                        NAMESPACE_URL,
                        "impact-authority-reminder-v1:"
                        + ":".join(
                            [tenant, str(row["principal_id"]), row["expires_at"].isoformat(), str(days)]
                        ),
                    )
                )
                if c.execute(
                    "SELECT 1 FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
                    (tenant, notification_id),
                ).fetchone():
                    continue
                ctx = ctx or self.service_principal(c, tenant)
                event_id = enqueue(c, tenant, "IN_APP_NOTICE", notification_id)
                receipt = write(
                    c,
                    ctx,
                    "Notification",
                    {
                        "event_id": event_id,
                        "recipient_id": str(row["principal_id"]),
                        "channel": "IN_APP",
                        "notice_class": "AUTHORITY_EXPIRING_" + str(days) + "D",
                        "safe_reference": row["membership_id"],
                    },
                    "Unread",
                    object_id=notification_id,
                    track_author=False,
                )
                audit(c, ctx, "notification.created", receipt, str(uuid4()))
                summary["reminders"] += 1

    def cancel_jobs(self, tenant, summary):
        """Honour a cancellation request for a job that has not started (Requested, Validating or
        Queued): Cancelled, lease generation advanced so no holder can complete it. A started job
        is left alone. Either outcome is recorded once as job_item 'cancellation'."""
        at = self.clock()
        with self.transaction(tenant, lock=True) as c:
            jobs = c.execute(
                "SELECT job_id,state,lease_generation FROM impact.job j WHERE tenant_id=%s "
                "AND cancellation_requested_at IS NOT NULL "
                "AND state NOT IN ('Succeeded','SucceededWithIssues','Failed','Cancelled') "
                "AND NOT EXISTS(SELECT 1 FROM impact.job_item i WHERE i.tenant_id=j.tenant_id "
                "AND i.job_id=j.job_id AND i.item_key='cancellation') ORDER BY job_id LIMIT 50 FOR UPDATE SKIP LOCKED",
                (tenant,),
            ).fetchall()
            for job in jobs:
                if job["state"] in PRE_START:
                    updated = c.execute(
                        "UPDATE impact.job SET state='Cancelled',lease_generation=lease_generation+1,"
                        "lease_expires_at=NULL,output_manifest=%s WHERE tenant_id=%s AND job_id=%s "
                        "AND lease_generation=%s AND state=%s",
                        (
                            Jsonb(
                                {"cancelled_at": at.isoformat(), "boundary": "BEFORE_START", "by": "worker"}
                            ),
                            tenant,
                            job["job_id"],
                            job["lease_generation"],
                            job["state"],
                        ),
                    ).rowcount
                    if updated:
                        c.execute(
                            "INSERT INTO impact.job_item(tenant_id,job_id,item_key,outcome) "
                            "VALUES(%s,%s,'cancellation','CANCELLED_BEFORE_START')",
                            (tenant, job["job_id"]),
                        )
                        summary["cancelled"] += 1
                else:
                    c.execute(
                        "INSERT INTO impact.job_item(tenant_id,job_id,item_key,outcome,error_code) "
                        "VALUES(%s,%s,'cancellation','NOT_CANCELLED_STARTED','JOB_ALREADY_STARTED') "
                        "ON CONFLICT DO NOTHING",
                        (tenant, job["job_id"]),
                    )
                    summary["refused_cancellations"] += 1


def main(argv=None):
    parser = argparse.ArgumentParser(description="Impact Platform worker (outbox dispatcher)")
    parser.add_argument("--once", action="store_true", help="Run one iteration and exit")
    parser.add_argument("--worker-id", help="Stable identifier for the heartbeat row")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    try:
        s = WorkerSettings.load()
        worker = Worker(s, worker_id=args.worker_id)
        if args.once:
            print(json.dumps(worker.run_once(), sort_keys=True))
            worker.heartbeat("STOPPED")
        else:
            worker.run_forever()
    except ConfigurationError as exc:
        LOG.error("worker refused to run reason=%s", exc.reason)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
