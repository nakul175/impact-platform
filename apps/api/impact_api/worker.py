"""Worker runtime and outbox dispatcher (v0.16): `python -m impact_api.worker`.

One process per worker login (`impact_worker_login` -> `impact_worker`). Each iteration:

1. `impact.worker_tenants(at)` names the Provisioning, Active and Suspended tenants with their
   lifecycle state and due delivery counts (identifiers only; migration 0018). Deliveries queued
   before a suspension carry held_at and are never claimed; the scans below run for Active only.
2. Per tenant, in its own transaction under the tenant advisory lock and a transaction-local
   tenant context, due `outbox_delivery` rows are claimed with `FOR UPDATE SKIP LOCKED`: the row
   becomes LEASED to this worker with `lease_generation + 1`, an expiry and one more attempt.
3. Per claimed row, a transaction renews the lease (fenced on owner and generation, only while
   the lease is still live and the row is not held; otherwise the row is skipped unsent), rechecks
   the intent (current invitation generation, pending challenge, active recipient) and builds the
   message; the connection is closed, then the channel adapter is called outside any transaction;
   a new transaction records the outcome. Every outcome update carries the lease owner and
   generation, so a holder whose lease was taken over is refused. Only a send that itself outlives
   a whole lease period mid-SMTP can be duplicated (email delivery is at least once).
   All lease and due comparisons use the database clock (statement_timestamp()).
4. IN_APP intents are transactional: the fenced SENT update, the `notification_delivery` row and
   the consumer receipt commit together, so the visible effect happens exactly once.
5. Per tenant scans: delegated-authority expiry reminders 14 and 3 days ahead (idempotent per
   principal, expiry instant and threshold) and cancellation of jobs that had not started.
6. A heartbeat row for operators (`GET /v1/platform/workers`).
7. Report exports (v0.23), the first job class the worker executes: per Active tenant with due
   REPORT_EXPORT jobs (`impact.worker_export_tenants(at)`, migration 0024), the jobs are claimed
   under the tenant lock with the same discipline as deliveries: Queued (not cancelled, due) or
   Running with an expired lease becomes Running with `lease_generation + 1`, the lease owner and
   one more attempt. Per job a transaction renews the lease (fenced) and reads the pinned, immutable
   package revisions; the connection is closed; the document is rendered outside any transaction;
   a fenced outcome transaction stores the artifact (Succeeded), requeues with backoff, or records
   Failed with an error class. A stale holder's outcome matches no row, so one job yields at most
   one artifact. A job with a cancellation request is never claimed.
8. Retention sweeps (v0.25 part B), job class RETENTION_SWEEP: during the per-tenant scan the
   definer `impact.worker_schedule_retention` queues one sweep per Active tenant when none is open
   and none completed within `retention_seconds`; the sweep is claimed like an export (lease
   generation + 1, database time) and executed in one transaction that renews the lease, applies
   the schedule of `impact_api.retention`, writes one insert-only `retention_proof` row per data
   class and records Succeeded, all fenced on the lease generation: a stale holder's sweep rolls
   back and leaves neither deletions nor proof.

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
from dataclasses import dataclass, field, fields
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

from . import keyring
from .delivery import (
    channel_code,
    code_secret,
    enqueue,
    invitation_token,
    invitation_url,
    render,
    unseal_recipient,
)
from .export_render import MEDIA_TYPES, RenderError, build_model, render as render_export
from .identity_profile import email_hash, normalize_email
from . import retention as retention_schedule
from .store import audit, write
from .version import BUILD

LOG = logging.getLogger("impact.worker")
BACKOFF_BASE_SECONDS = 30
BACKOFF_CAP_SECONDS = 3600
REMINDER_DAYS = (14, 3)
LOOPBACK = {"127.0.0.1", "::1", "localhost"}
PRE_START = ("Requested", "Validating", "Queued")
# SMTP replies that mean "authenticate first" or "authentication failed": configuration, not message.
AUTHENTICATION_CODES = {530, 534, 535, 538}
BOOLEAN = {"require_unprivileged_db"}
INTEGER = {
    "smtp_port",
    "synthetic_failures",
    "lease_seconds",
    "batch_size",
    "max_attempts",
    "scan_seconds",
    "retention_seconds",
}
FLOAT = {"smtp_timeout", "synthetic_delay", "poll_seconds"}
WORKER_QUERY = (
    "SELECT current_user AS login,rolsuper,rolbypassrls,"
    "pg_has_role(current_user,'impact_owner','MEMBER') AS owns_schema,"
    "pg_has_role(current_user,'impact_worker','MEMBER') AS worker,"
    "COALESCE((SELECT array_agg(g.rolname::text ORDER BY g.rolname) FROM pg_auth_members m "
    "JOIN pg_roles g ON g.oid=m.roleid WHERE m.member=l.oid),'{}') AS memberships "
    "FROM pg_roles l WHERE l.rolname=current_user"
)


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
    worker_dsn: str = field(repr=False)
    public_origin: str
    invitation_secret: str = field(default="", repr=False)
    delivery_secret: str = field(default="", repr=False)
    # Grace secrets after a rotation (v0.25 part A): comma- or space-separated, newest first.
    invitation_secret_previous: str = field(default="", repr=False)
    delivery_secret_previous: str = field(default="", repr=False)
    email_adapter: str = "synthetic"
    smtp_host: str = "127.0.0.1"
    smtp_port: int = 25
    smtp_username: str = ""
    smtp_password: str = field(default="", repr=False)
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
    # A tenant's next retention sweep is queued once its last one completed this long ago.
    retention_seconds: int = 86400

    @property
    def unprivileged_db_required(self):
        return self.environment in {"staging", "production"} or self.require_unprivileged_db

    @classmethod
    def load(cls, overrides=None):
        """IMPACT_WORKER_CONFIG_FILE (JSON), then IMPACT_<FIELD> environment variables, then
        overrides. The worker never reads the API configuration or its connection strings."""
        path = os.environ.get("IMPACT_WORKER_CONFIG_FILE")
        data = json.loads(Path(path).read_text()) if path else {}
        for entry in fields(cls):
            value = os.environ.get("IMPACT_" + entry.name.upper())
            if value is not None:
                data[entry.name] = value
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
        try:
            keyring.validate(self, families=("invitation", "delivery"))
        except keyring.KeyringError:
            raise ConfigurationError("INVALID_KEYRING") from None
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
        if not 60 <= self.retention_seconds <= 31 * 86400:
            raise ConfigurationError("INVALID_LIMITS")


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
            # Every recipient refused: the address itself is rejected, retrying cannot help.
            raise DeliveryError("RECIPIENT_REFUSED", permanent=True) from None
        except smtplib.SMTPSenderRefused:
            # MAIL FROM refused (5xx included): a relay, sender or authentication configuration
            # problem of ours, not of this message; retried with backoff until it is fixed.
            raise DeliveryError("SMTP_SENDER_REJECTED") from None
        except smtplib.SMTPAuthenticationError:
            raise DeliveryError("SMTP_AUTHENTICATION") from None
        except smtplib.SMTPResponseException as exc:
            if exc.smtp_code in AUTHENTICATION_CODES:
                raise DeliveryError("SMTP_AUTHENTICATION") from None
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
            "at": datetime.now(timezone.utc).isoformat(),
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


EXPORT_FENCE = (
    " WHERE j.tenant_id=%(tenant)s AND j.job_id=%(job)s AND j.state='Running'"
    " AND j.lease_generation=%(generation)s AND e.tenant_id=j.tenant_id AND e.job_id=j.job_id"
    " AND e.lease_owner=%(owner)s"
)
EXPORT_KEYS = [
    "exports_claimed",
    "exports_succeeded",
    "exports_retried",
    "exports_failed",
    "exports_cancelled",
]
RETENTION_FENCE = (
    " WHERE j.tenant_id=%(tenant)s AND j.job_id=%(job)s AND j.state='Running'"
    " AND j.lease_generation=%(generation)s AND s.tenant_id=j.tenant_id AND s.job_id=j.job_id"
    " AND s.lease_owner=%(owner)s"
)
RETENTION_KEYS = ["retention_scheduled", "retention_claimed", "retention_swept", "retention_failed"]


class StaleLease(Exception):
    """The fenced outcome of a sweep matched no row: roll the whole sweep back."""


def empty_summary():
    keys = ["tenants", "claimed", "sent", "retried", "dead", "superseded", "stale_refused", "released"]
    return dict.fromkeys(
        keys
        + ["reminders", "cancelled", "refused_cancellations", "tenant_failures"]
        + EXPORT_KEYS
        + RETENTION_KEYS,
        0,
    )


class Worker:
    """All lease, due and expiry comparisons use the database clock (`statement_timestamp()`),
    never the worker host's clock, so workers on skewed hosts agree on who holds a lease. `skew`
    is a test seam only: a callable returning a timedelta added to the database time (qualification
    moves time forward with it; the CLI never sets it)."""

    def __init__(self, s, skew=None, adapter=None, rng=None, worker_id=None, probe=None):
        self.s = s
        self.skew = skew or (lambda: timedelta(0))
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
        self.last_scan = None
        self.totals = {"iterations": 0, "sent": 0, "retried": 0, "dead": 0, "failures": 0}

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

    def now(self, c):
        """The database's statement time (plus the test-only skew)."""
        return c.execute("SELECT statement_timestamp()+%s::interval AS now", (self.skew(),)).fetchone()["now"]

    # -- iteration ------------------------------------------------------------------------------

    def run_once(self):
        summary = empty_summary()
        with self.transaction() as c:
            at = self.now(c)
            tenants = c.execute("SELECT * FROM impact.worker_tenants(%s)", (at,)).fetchall()
            exports = {
                str(row["tenant_id"]): row["due_exports"]
                for row in c.execute("SELECT * FROM impact.worker_export_tenants(%s)", (at,)).fetchall()
            }
        scan = self.last_scan is None or (at - self.last_scan).total_seconds() >= self.s.scan_seconds
        for row in tenants:
            if self.stopping:
                break
            summary["tenants"] += 1
            tenant = str(row["tenant_id"])
            try:
                if row["due_deliveries"]:
                    self.dispatch(tenant, summary)
                if exports.get(tenant) and row["lifecycle_state"] == "Active" and not self.stopping:
                    self.run_exports(tenant, summary)
                if scan and row["lifecycle_state"] == "Active" and not self.stopping:
                    self.remind(tenant, summary)
                    self.cancel_jobs(tenant, summary)
                    self.run_retention(tenant, summary)
            except ConfigurationError:
                raise
            except Exception as exc:  # one tenant's failure never stops the others
                summary["tenant_failures"] += 1
                LOG.warning("worker tenant pass failed class=%s", type(exc).__name__)
        if scan:
            self.last_scan = at
        self.totals["iterations"] += 1
        for key in ["sent", "retried", "dead"]:
            self.totals[key] += summary[key]
        self.totals["failures"] += summary["tenant_failures"]
        self.heartbeat("STOPPING" if self.stopping else "RUNNING")
        return summary

    def heartbeat(self, state):
        with self.transaction() as c:
            c.execute(
                "INSERT INTO impact.worker_heartbeat(worker_id,build,state,started_at,beat_at,stopped_at,"
                "iterations,sent,retried,dead,failures) VALUES(%(id)s,%(build)s,%(state)s,statement_timestamp(),"
                "statement_timestamp(),CASE WHEN %(stopped)s THEN statement_timestamp() END,"
                "%(iterations)s,%(sent)s,%(retried)s,%(dead)s,%(failures)s) "
                "ON CONFLICT(worker_id) DO UPDATE SET state=EXCLUDED.state,beat_at=EXCLUDED.beat_at,"
                "stopped_at=EXCLUDED.stopped_at,iterations=EXCLUDED.iterations,sent=EXCLUDED.sent,"
                "retried=EXCLUDED.retried,dead=EXCLUDED.dead,failures=EXCLUDED.failures",
                {
                    "id": self.worker_id,
                    "build": BUILD,
                    "state": state,
                    "stopped": state == "STOPPED",
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
        self.heartbeat("RUNNING")
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
        with self.transaction(tenant, lock=True) as c:
            at = self.now(c)
            # A held row (tenant suspended) whose lease ended goes back to PENDING and stays held:
            # never sent, never stuck LEASED; the suspension's no-replay rule is unchanged.
            c.execute(
                "UPDATE impact.outbox_delivery SET state='PENDING',lease_owner=NULL,lease_expires_at=NULL "
                "WHERE tenant_id=%(tenant)s AND channel IS NOT NULL AND held_at IS NOT NULL "
                "AND state='LEASED' AND lease_expires_at<=%(at)s",
                {"at": at, "tenant": tenant},
            )
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

    def fenced(self, c, tenant, row, assignments, values=None, condition=""):
        """Apply an outcome only if this worker still holds exactly this lease generation."""
        params = {
            "tenant": tenant,
            "event": str(row["event_id"]),
            "owner": self.worker_id,
            "generation": row["lease_generation"],
            **(values or {}),
        }
        statement = "UPDATE impact.outbox_delivery SET " + assignments + FENCE + condition
        return c.execute(statement, params).rowcount == 1

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

    def renew(self, c, tenant, row, at):
        """Immediately before building a message: extend the lease by a full lease period, but only
        if this worker still holds this generation, the lease has not yet expired and the row is not
        held by a suspension. A row of a batch whose lease ran out while earlier rows were being
        sent is skipped here (a second worker may already have taken it over), so the only send that
        can be duplicated is one that itself outlives a whole lease period mid-SMTP."""
        return self.fenced(
            c,
            tenant,
            row,
            "lease_expires_at=%(renewed)s",
            {"at": at, "renewed": at + timedelta(seconds=self.s.lease_seconds)},
            " AND lease_expires_at>%(at)s AND held_at IS NULL",
        )

    def process(self, tenant, row, summary):
        if row["channel"] == "IN_APP":
            self.deliver_in_app(tenant, row, summary)
            return
        try:
            with self.transaction(tenant, lock=True) as c:
                at = self.now(c)
                decision = self.prepare(c, tenant, row, at) if self.renew(c, tenant, row, at) else ("lost",)
        except ConfigurationError:
            raise
        except psycopg.Error as exc:
            LOG.warning("delivery %s prepare failed class=%s", row["event_id"], type(exc).__name__)
            decision = ("retry", "PREPARE_FAILED")
        except Exception as exc:  # a defect in rendering or unsealing is recorded, never a crash
            LOG.warning("delivery %s prepare defect class=%s", row["event_id"], type(exc).__name__)
            decision = ("dead", "PREPARE_DEFECT")
        if decision[0] == "lost":
            summary["stale_refused"] += 1
            LOG.warning(
                "delivery %s skipped: lease expired, taken over or held before sending", row["event_id"]
            )
            return
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
            at = self.now(c)
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

    def prepare(self, c, tenant, row, at):
        """Recheck the intent inside the tenant fence and build the message. Returns ("send",
        message), ("supersede", reason) or ("dead", reason)."""
        template, reference = row["template"], str(row["reference_id"])
        try:
            address = unseal_recipient(
                keyring.ring(self.s, "delivery"), tenant, template, reference, row["recipient_sealed"]
            )
        except (InvalidTag, ValueError, TypeError):
            return ("dead", "RECIPIENT_UNREADABLE")
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
            # The link is re-derived with whichever non-retired signing secret produced the stored
            # token hash (current or in grace after a rotation); a retired secret matches none.
            token = next(
                (
                    candidate
                    for candidate in (
                        invitation_token(secret, tenant, reference, row["reference_generation"])
                        for secret in keyring.ring(self.s, "invitation").secrets()
                    )
                    if bytes(invitation["token_hash"]) == hashlib.sha256(candidate.encode()).digest()
                ),
                None,
            )
            if token is None:
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
            secret = code_secret(keyring.ring(self.s, "delivery"), reference, challenge["code_hash"])
            if secret is None:
                return ("dead", "SIGNING_KEY_MISMATCH")
            code = channel_code(secret, reference)
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
        outcome, reason = "sent", None
        with self.transaction(tenant, lock=True) as c:
            at = self.now(c)
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
                    " AND held_at IS NULL",
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

    # -- report exports (job class REPORT_EXPORT) -----------------------------------------------

    def run_exports(self, tenant, summary):
        rows = self.claim_exports(tenant, summary)
        for index, row in enumerate(rows):
            if self.stopping:
                summary["released"] += self.release_exports(tenant, rows[index:])
                break
            self.process_export(tenant, row, summary)

    def claim_exports(self, tenant, summary):
        """Lease due export jobs of one tenant (at most four per batch: each renders a document).
        A Running job whose lease expired at the attempt limit becomes Failed LEASE_EXPIRED."""
        with self.transaction(tenant, lock=True) as c:
            at = self.now(c)
            expired = c.execute(
                "UPDATE impact.job j SET state='Failed',lease_expires_at=NULL,lease_generation=j.lease_generation+1,"
                "output_manifest=%(manifest)s FROM impact.report_export e WHERE j.tenant_id=%(tenant)s "
                "AND e.tenant_id=j.tenant_id AND e.job_id=j.job_id AND j.job_class='REPORT_EXPORT' "
                "AND j.state='Running' AND j.lease_expires_at<=%(at)s AND e.attempts>=%(max)s RETURNING j.job_id",
                {
                    "tenant": tenant,
                    "at": at,
                    "max": self.s.max_attempts,
                    "manifest": Jsonb({"error_class": "LEASE_EXPIRED", "completed_at": at.isoformat()}),
                },
            ).fetchall()
            for job in expired:
                c.execute(
                    "UPDATE impact.report_export SET lease_owner=NULL,completed_at=%s,"
                    "last_error_class='LEASE_EXPIRED' WHERE tenant_id=%s AND job_id=%s",
                    (at, tenant, job["job_id"]),
                )
                c.execute(
                    "INSERT INTO impact.job_item(tenant_id,job_id,item_key,outcome,error_code) "
                    "VALUES(%s,%s,'artifact','FAILED','LEASE_EXPIRED') ON CONFLICT DO NOTHING",
                    (tenant, job["job_id"]),
                )
            jobs = c.execute(
                "WITH due AS (SELECT j.job_id FROM impact.job j JOIN impact.report_export e "
                "ON e.tenant_id=j.tenant_id AND e.job_id=j.job_id WHERE j.tenant_id=%(tenant)s "
                "AND j.job_class='REPORT_EXPORT' AND ((j.state='Queued' AND j.cancellation_requested_at IS NULL "
                "AND e.next_attempt_at<=%(at)s) OR (j.state='Running' AND j.lease_expires_at<=%(at)s)) "
                "ORDER BY e.next_attempt_at,j.job_id LIMIT %(limit)s FOR UPDATE OF j SKIP LOCKED) "
                "UPDATE impact.job j SET state='Running',lease_generation=j.lease_generation+1,"
                "lease_expires_at=%(expires)s FROM due WHERE j.tenant_id=%(tenant)s AND j.job_id=due.job_id "
                "RETURNING j.job_id,j.lease_generation",
                {
                    "tenant": tenant,
                    "at": at,
                    "limit": min(self.s.batch_size, 4),
                    "expires": at + timedelta(seconds=self.s.lease_seconds),
                },
            ).fetchall()
            rows = []
            for job in jobs:
                export = c.execute(
                    "UPDATE impact.report_export SET lease_owner=%s,attempts=attempts+1,last_attempt_at=%s "
                    "WHERE tenant_id=%s AND job_id=%s RETURNING job_id,report_id,report_revision,format,"
                    "renderer_version,reconciliation_digest,attempts",
                    (self.worker_id, at, tenant, job["job_id"]),
                ).fetchone()
                rows.append({**export, "lease_generation": job["lease_generation"]})
        summary["exports_failed"] += len(expired)
        summary["exports_claimed"] += len(rows)
        return sorted(rows, key=lambda r: str(r["job_id"]))

    def fenced_export(self, c, tenant, row, assignments, values=None, condition=""):
        """Apply a job update only while this worker holds exactly this lease generation; returns
        the job's new state, or None when the lease was taken over (the outcome is refused)."""
        params = {
            "tenant": tenant,
            "job": str(row["job_id"]),
            "owner": self.worker_id,
            "generation": row["lease_generation"],
            **(values or {}),
        }
        statement = "UPDATE impact.job j SET " + assignments + " FROM impact.report_export e" + EXPORT_FENCE
        return c.execute(statement + condition + " RETURNING j.state", params).fetchone()

    def release_exports(self, tenant, rows):
        released = 0
        with self.transaction(tenant, lock=True) as c:
            for row in rows:
                if self.fenced_export(c, tenant, row, "state='Queued',lease_expires_at=NULL"):
                    c.execute(
                        "UPDATE impact.report_export SET lease_owner=NULL,attempts=attempts-1 "
                        "WHERE tenant_id=%s AND job_id=%s",
                        (tenant, row["job_id"]),
                    )
                    released += 1
        return released

    def export_model(self, c, tenant, row):
        """Read the pinned, immutable package: the frozen binding (digest unchanged since the
        request), the report, template and snapshot revisions and each bound OFFICIAL result of the
        snapshot. Restricted (privacy-removed) content is never reconstructed: the job fails."""
        binding = c.execute(
            "SELECT * FROM impact.report_package_binding WHERE tenant_id=%s AND report_id=%s "
            "AND report_revision=%s",
            (tenant, row["report_id"], row["report_revision"]),
        ).fetchone()
        if not binding or bytes(binding["reconciliation_digest"]) != bytes(row["reconciliation_digest"]):
            raise RenderError("PACKAGE_BINDING_CHANGED")

        def revision(revision_id, kind):
            found = c.execute(
                "SELECT object_type,payload,restriction_state FROM impact.object_revision "
                "WHERE tenant_id=%s AND revision_id=%s",
                (tenant, str(revision_id)),
            ).fetchone()
            if not found or found["object_type"] != kind:
                raise RenderError("PACKAGE_REVISION_MISSING")
            if found["restriction_state"] != "AVAILABLE":
                raise RenderError("PACKAGE_CONTENT_RESTRICTED")
            return found["payload"]

        report = revision(row["report_revision"], "Report")
        template = revision(binding["template_revision"], "ReportTemplate")
        snapshot = revision(binding["snapshot_revision"], "Snapshot")
        official = set(snapshot.get("result_versions", []))
        pinned_targets = set(snapshot.get("target_versions", []))
        values, targets = {}, {}
        for section in report["sections"]:
            for numeric in section["bindings"]:
                result = revision(numeric["result_revision"], "CalculatedResult")
                if result.get("mode") != "OFFICIAL" or numeric["result_revision"] not in official:
                    raise RenderError("RESULT_NOT_OFFICIAL")
                values[(section["section_code"], numeric["binding_code"])] = result
            # Chart targets (v0.27): only Target revisions the snapshot locked, read as revisions.
            for chart in section.get("charts") or []:
                for series in chart["series"]:
                    target_revision = series.get("target_revision")
                    if target_revision and target_revision not in targets:
                        if target_revision not in pinned_targets:
                            raise RenderError("RESULT_NOT_OFFICIAL")
                        targets[target_revision] = revision(target_revision, "Target")
        return build_model(
            row["report_id"],
            row["report_revision"],
            report,
            template,
            binding["snapshot_id"],
            snapshot,
            bytes(binding["reconciliation_digest"]).hex(),
            values,
            targets,
        )

    def process_export(self, tenant, row, summary):
        try:
            with self.transaction(tenant, lock=True) as c:
                at = self.now(c)
                renewed = self.fenced_export(
                    c,
                    tenant,
                    row,
                    "lease_expires_at=%(renewed)s",
                    {"at": at, "renewed": at + timedelta(seconds=self.s.lease_seconds)},
                    " AND j.lease_expires_at>%(at)s",
                )
                decision = ("render", self.export_model(c, tenant, row)) if renewed else ("lost",)
        except ConfigurationError:
            raise
        except RenderError as exc:
            decision = ("fail" if exc.permanent else "retry", exc.error_class)
        except psycopg.Error as exc:
            LOG.warning("export %s prepare failed class=%s", row["job_id"], type(exc).__name__)
            decision = ("retry", "PREPARE_FAILED")
        except Exception as exc:  # a defect reading the package is recorded, never a crash
            LOG.warning("export %s prepare defect class=%s", row["job_id"], type(exc).__name__)
            decision = ("fail", "PREPARE_DEFECT")
        if decision[0] == "lost":
            summary["stale_refused"] += 1
            LOG.warning("export %s skipped: lease expired or taken over before rendering", row["job_id"])
            return
        if decision[0] != "render":
            self.record_export(tenant, row, summary, *decision)
            return
        if self.probe:
            self.probe(self)
        try:
            body = render_export(row["format"], decision[1])
        except RenderError as exc:
            self.record_export(tenant, row, summary, "fail" if exc.permanent else "retry", exc.error_class)
            return
        self.record_export(tenant, row, summary, "succeeded", None, body)

    def record_export(self, tenant, row, summary, outcome, error_class, body=None):
        if outcome == "retry" and row["attempts"] >= self.s.max_attempts:
            outcome = "fail"
        with self.transaction(tenant, lock=True) as c:
            at = self.now(c)
            if outcome == "succeeded":
                manifest = {
                    "format": row["format"],
                    "media_type": MEDIA_TYPES[row["format"]],
                    "content_sha256": hashlib.sha256(body).hexdigest(),
                    "size_bytes": len(body),
                    "renderer_version": row["renderer_version"],
                    "completed_at": at.isoformat(),
                }
                assignments = "state='Succeeded',lease_expires_at=NULL,output_manifest=%(manifest)s"
            elif outcome == "retry":
                # A cancellation requested while this attempt ran is honoured between attempts.
                manifest = {"cancelled_at": at.isoformat(), "boundary": "BETWEEN_ATTEMPTS", "by": "worker"}
                assignments = (
                    "state=CASE WHEN j.cancellation_requested_at IS NULL THEN 'Queued' ELSE 'Cancelled' END,"
                    "lease_expires_at=NULL,output_manifest=CASE WHEN j.cancellation_requested_at IS NULL "
                    "THEN NULL ELSE %(manifest)s END"
                )
            else:
                manifest = {"error_class": error_class, "completed_at": at.isoformat()}
                assignments = "state='Failed',lease_expires_at=NULL,output_manifest=%(manifest)s"
            applied = self.fenced_export(c, tenant, row, assignments, {"manifest": Jsonb(manifest)})
            if applied:
                state = applied["state"]
                finished = state != "Queued"
                c.execute(
                    "UPDATE impact.report_export SET lease_owner=NULL,last_error_class=%s,"
                    "next_attempt_at=CASE WHEN %s THEN next_attempt_at ELSE %s END,"
                    "completed_at=CASE WHEN %s THEN %s::timestamptz END WHERE tenant_id=%s AND job_id=%s",
                    (
                        error_class,
                        finished,
                        at + self.backoff(row["attempts"]),
                        finished,
                        at,
                        tenant,
                        row["job_id"],
                    ),
                )
                if state == "Succeeded":
                    c.execute(
                        "INSERT INTO impact.report_export_artifact(tenant_id,job_id,report_id,report_revision,"
                        "format,renderer_version,media_type,body,content_sha256,lease_generation,created_at) "
                        "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (
                            tenant,
                            row["job_id"],
                            row["report_id"],
                            row["report_revision"],
                            row["format"],
                            row["renderer_version"],
                            MEDIA_TYPES[row["format"]],
                            body,
                            hashlib.sha256(body).digest(),
                            row["lease_generation"],
                            at,
                        ),
                    )
                if state in {"Succeeded", "Failed"}:
                    c.execute(
                        "INSERT INTO impact.job_item(tenant_id,job_id,item_key,outcome,error_code) "
                        "VALUES(%s,%s,'artifact',%s,%s) ON CONFLICT DO NOTHING",
                        (tenant, row["job_id"], "CREATED" if state == "Succeeded" else "FAILED", error_class),
                    )
        if not applied:
            summary["stale_refused"] += 1
            LOG.warning("export %s outcome refused: lease generation superseded", row["job_id"])
            return False
        summary[
            {
                "Succeeded": "exports_succeeded",
                "Queued": "exports_retried",
                "Failed": "exports_failed",
                "Cancelled": "exports_cancelled",
            }[applied["state"]]
        ] += 1
        LOG.info(
            "export %s format=%s outcome=%s class=%s attempt=%s",
            row["job_id"],
            row["format"],
            applied["state"],
            error_class,
            row["attempts"],
        )
        return True

    # -- retention sweeps (job class RETENTION_SWEEP) -------------------------------------------

    def run_retention(self, tenant, summary):
        for row in self.claim_retention(tenant, summary):
            if self.stopping:
                summary["released"] += self.release_retention(tenant, [row])
                break
            self.process_retention(tenant, row, summary)

    def claim_retention(self, tenant, summary, schedule=True):
        """Queue a sweep when one is due (definer, database clock), fail a sweep whose lease
        expired at the attempt limit, and lease at most one due sweep of the tenant."""
        with self.transaction(tenant, lock=True) as c:
            if schedule:
                principal = self.service_principal(c, tenant).principal_id
                if c.execute(
                    "SELECT impact.worker_schedule_retention(%s,%s) AS job",
                    (principal, self.s.retention_seconds),
                ).fetchone()["job"]:
                    summary["retention_scheduled"] += 1
            # Read after scheduling: a sweep queued just now is due at this instant.
            at = self.now(c)
            expired = c.execute(
                "UPDATE impact.job j SET state='Failed',lease_expires_at=NULL,lease_generation=j.lease_generation+1,"
                "output_manifest=%(manifest)s FROM impact.retention_sweep s WHERE j.tenant_id=%(tenant)s "
                "AND s.tenant_id=j.tenant_id AND s.job_id=j.job_id AND j.job_class='RETENTION_SWEEP' "
                "AND j.state='Running' AND j.lease_expires_at<=%(at)s AND s.attempts>=%(max)s RETURNING j.job_id",
                {
                    "tenant": tenant,
                    "at": at,
                    "max": self.s.max_attempts,
                    "manifest": Jsonb({"error_class": "LEASE_EXPIRED", "completed_at": at.isoformat()}),
                },
            ).fetchall()
            for job in expired:
                c.execute(
                    "UPDATE impact.retention_sweep SET lease_owner=NULL,completed_at=%s,"
                    "last_error_class='LEASE_EXPIRED' WHERE tenant_id=%s AND job_id=%s",
                    (at, tenant, job["job_id"]),
                )
            jobs = c.execute(
                "WITH due AS (SELECT j.job_id FROM impact.job j JOIN impact.retention_sweep s "
                "ON s.tenant_id=j.tenant_id AND s.job_id=j.job_id WHERE j.tenant_id=%(tenant)s "
                "AND j.job_class='RETENTION_SWEEP' AND ((j.state='Queued' AND j.cancellation_requested_at IS NULL "
                "AND s.next_attempt_at<=%(at)s) OR (j.state='Running' AND j.lease_expires_at<=%(at)s)) "
                "ORDER BY s.next_attempt_at,j.job_id LIMIT 1 FOR UPDATE OF j SKIP LOCKED) "
                "UPDATE impact.job j SET state='Running',lease_generation=j.lease_generation+1,"
                "lease_expires_at=%(expires)s FROM due WHERE j.tenant_id=%(tenant)s AND j.job_id=due.job_id "
                "RETURNING j.job_id,j.lease_generation",
                {"tenant": tenant, "at": at, "expires": at + timedelta(seconds=self.s.lease_seconds)},
            ).fetchall()
            rows = []
            for job in jobs:
                sweep = c.execute(
                    "UPDATE impact.retention_sweep SET lease_owner=%s,attempts=attempts+1,last_attempt_at=%s "
                    "WHERE tenant_id=%s AND job_id=%s RETURNING job_id,attempts",
                    (self.worker_id, at, tenant, job["job_id"]),
                ).fetchone()
                rows.append({**sweep, "lease_generation": job["lease_generation"]})
        summary["retention_failed"] += len(expired)
        summary["retention_claimed"] += len(rows)
        return rows

    def fenced_retention(self, c, tenant, row, assignments, values=None, condition=""):
        """Apply a job update only while this worker holds exactly this lease generation."""
        params = {
            "tenant": tenant,
            "job": str(row["job_id"]),
            "owner": self.worker_id,
            "generation": row["lease_generation"],
            **(values or {}),
        }
        statement = (
            "UPDATE impact.job j SET " + assignments + " FROM impact.retention_sweep s" + RETENTION_FENCE
        )
        return c.execute(statement + condition + " RETURNING j.state", params).fetchone()

    def release_retention(self, tenant, rows):
        released = 0
        with self.transaction(tenant, lock=True) as c:
            for row in rows:
                if self.fenced_retention(c, tenant, row, "state='Queued',lease_expires_at=NULL"):
                    c.execute(
                        "UPDATE impact.retention_sweep SET lease_owner=NULL,attempts=attempts-1 "
                        "WHERE tenant_id=%s AND job_id=%s",
                        (tenant, row["job_id"]),
                    )
                    released += 1
        return released

    def process_retention(self, tenant, row, summary):
        """One transaction: renew the lease (only while it is live), apply the schedule, write the
        proof rows and record Succeeded, every update fenced on this worker's lease generation. A
        refused fence rolls everything back: a stale holder deletes nothing and proves nothing."""
        manifest = {}
        try:
            with self.transaction(tenant, lock=True) as c:
                at = self.now(c)
                if not self.fenced_retention(
                    c,
                    tenant,
                    row,
                    "lease_expires_at=%(renewed)s",
                    {"at": at, "renewed": at + timedelta(seconds=self.s.lease_seconds)},
                    " AND j.lease_expires_at>%(at)s",
                ):
                    raise StaleLease()
                results = retention_schedule.apply(c, tenant)
                for data_class, (cutoff, items) in sorted(results.items()):
                    policy = retention_schedule.CLASSES[data_class]
                    digest = retention_schedule.digest(items)
                    c.execute(
                        "INSERT INTO impact.retention_proof(tenant_id,proof_id,job_id,lease_generation,data_class,"
                        "action,retention_days,cutoff,affected_count,items_sha256,executed_at,worker_id) "
                        "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,statement_timestamp(),%s)",
                        (
                            tenant,
                            str(uuid4()),
                            row["job_id"],
                            row["lease_generation"],
                            data_class,
                            policy["action"],
                            policy["retention_days"],
                            cutoff,
                            len(items),
                            digest,
                            self.worker_id,
                        ),
                    )
                    manifest[data_class] = {"affected": len(items), "items_sha256": digest.hex()}
                if not self.fenced_retention(
                    c,
                    tenant,
                    row,
                    "state='Succeeded',lease_expires_at=NULL,output_manifest=%(manifest)s",
                    {"manifest": Jsonb({"classes": manifest, "completed_at": at.isoformat()})},
                ):
                    raise StaleLease()
                c.execute(
                    "UPDATE impact.retention_sweep SET lease_owner=NULL,completed_at=statement_timestamp(),"
                    "last_error_class=NULL WHERE tenant_id=%s AND job_id=%s",
                    (tenant, row["job_id"]),
                )
                c.execute(
                    "INSERT INTO impact.job_item(tenant_id,job_id,item_key,outcome) "
                    "VALUES(%s,%s,'sweep','SUCCEEDED') ON CONFLICT DO NOTHING",
                    (tenant, row["job_id"]),
                )
        except ConfigurationError:
            raise
        except StaleLease:
            summary["stale_refused"] += 1
            LOG.warning("retention sweep %s refused: lease expired or taken over", row["job_id"])
            return False
        except psycopg.Error as exc:
            LOG.warning("retention sweep %s failed class=%s", row["job_id"], type(exc).__name__)
            self.record_retention_failure(tenant, row, summary, "SWEEP_FAILED")
            return False
        summary["retention_swept"] += 1
        LOG.info("retention sweep %s %s", row["job_id"], json.dumps(manifest, sort_keys=True))
        return True

    def record_retention_failure(self, tenant, row, summary, error_class):
        """Back off and queue again, or Failed with the error class at the attempt limit (fenced)."""
        with self.transaction(tenant, lock=True) as c:
            at = self.now(c)
            final = row["attempts"] >= self.s.max_attempts
            applied = self.fenced_retention(
                c,
                tenant,
                row,
                "state=%(state)s,lease_expires_at=NULL,output_manifest=%(manifest)s",
                {
                    "state": "Failed" if final else "Queued",
                    "manifest": (
                        Jsonb({"error_class": error_class, "completed_at": at.isoformat()}) if final else None
                    ),
                },
            )
            if not applied:
                summary["stale_refused"] += 1
                return
            c.execute(
                "UPDATE impact.retention_sweep SET lease_owner=NULL,last_error_class=%s,next_attempt_at=%s,"
                "completed_at=CASE WHEN %s THEN %s::timestamptz END WHERE tenant_id=%s AND job_id=%s",
                (error_class, at + self.backoff(row["attempts"]), final, at, tenant, row["job_id"]),
            )
            if final:
                summary["retention_failed"] += 1
                c.execute(
                    "INSERT INTO impact.job_item(tenant_id,job_id,item_key,outcome,error_code) "
                    "VALUES(%s,%s,'sweep','FAILED',%s) ON CONFLICT DO NOTHING",
                    (tenant, row["job_id"], error_class),
                )

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
        again within 3 days; one per (principal, expiry instant, threshold), recorded in
        authority_reminder and excluded in SQL, so the batch limit cannot starve later groups. A
        renewal moves the expiry and so re-arms both. The 14-day notice is not sent once inside the
        3-day window."""
        with self.transaction(tenant, lock=True) as c:
            at = self.now(c)
            rows = c.execute(
                "SELECT * FROM (SELECT a.principal_id,a.expires_at,min(m.object_id::text) AS membership_id,"
                "CASE WHEN a.expires_at-%(at)s<=make_interval(days=>%(short)s) THEN %(short)s ELSE %(long)s END "
                "AS threshold_days FROM impact.grant_authority a JOIN impact.tenant_principal p "
                "ON p.tenant_id=a.tenant_id AND p.principal_id=a.principal_id JOIN impact.membership_current m "
                "ON m.tenant_id=p.tenant_id AND m.identity_id=p.identity_id JOIN impact.object_registry r "
                "ON r.tenant_id=m.tenant_id AND r.object_id=m.object_id WHERE a.tenant_id=%(tenant)s AND p.active "
                "AND r.lifecycle_state='Active' AND a.expires_at>%(at)s "
                "AND a.expires_at<=%(at)s+make_interval(days=>%(long)s) GROUP BY a.principal_id,a.expires_at) g "
                "WHERE NOT EXISTS(SELECT 1 FROM impact.authority_reminder x WHERE x.tenant_id=%(tenant)s "
                "AND x.principal_id=g.principal_id AND x.expires_at=g.expires_at "
                "AND x.threshold_days=g.threshold_days) ORDER BY g.expires_at,g.principal_id LIMIT 200",
                {"tenant": tenant, "at": at, "short": REMINDER_DAYS[1], "long": REMINDER_DAYS[0]},
            ).fetchall()
            ctx = None
            for row in rows:
                days = row["threshold_days"]
                expires = row["expires_at"].astimezone(timezone.utc).isoformat()
                notification_id = str(
                    uuid5(
                        NAMESPACE_URL,
                        "impact-authority-reminder-v1:"
                        + ":".join([tenant, str(row["principal_id"]), expires, str(days)]),
                    )
                )
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
                c.execute(
                    "INSERT INTO impact.authority_reminder(tenant_id,principal_id,expires_at,threshold_days,"
                    "notification_id) VALUES(%s,%s,%s,%s,%s)",
                    (tenant, str(row["principal_id"]), row["expires_at"], days, notification_id),
                )
                audit(c, ctx, "notification.created", receipt, str(uuid4()))
                summary["reminders"] += 1

    def cancel_jobs(self, tenant, summary):
        """Honour a cancellation request for a job that has not started (Requested, Validating or
        Queued): Cancelled, lease generation advanced so no holder can complete it. A started job
        is left alone. Either outcome is recorded once as job_item 'cancellation'."""
        with self.transaction(tenant, lock=True) as c:
            at = self.now(c)
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
