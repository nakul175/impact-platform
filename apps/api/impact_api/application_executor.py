"""Application-role executor for governed jobs, separate from the outbox worker."""

import argparse
import logging
import os
import re
import signal
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime

import psycopg
from psycopg.rows import dict_row

from .auth import Identity
from .config import Settings
from .domain import DomainError
from .service import Service
from .store import audit, authorize, context, load
from .version import BUILD

LOG = logging.getLogger("impact.executor")
LOGIN_QUERY = (
    "SELECT current_user AS login,rolsuper,rolbypassrls,rolinherit,"
    "pg_has_role(current_user,'impact_owner','MEMBER') AS owns_schema,"
    "COALESCE((SELECT array_agg(r.rolname::text ORDER BY r.rolname) FROM pg_auth_members m "
    "JOIN pg_roles r ON r.oid=m.roleid WHERE m.member=l.oid),'{}') AS memberships "
    "FROM pg_roles l WHERE l.rolname=current_user"
)
ID = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
ERRORS = {
    "PREVIEW_STALE",
    "IMPORT_ATOMIC_REJECTED",
    "WARNINGS_NOT_ACCEPTED",
    "SOURCE_KEY_CONFLICT",
    "LEASE_EXPIRED",
    "AUTHORITY_CHANGED",
    "COMMIT_DEFECT",
    "IMPORT_NOTHING_TO_COMMIT",
    "DATABASE_UNAVAILABLE",
}


@dataclass(frozen=True)
class ExecutorSettings:
    dsn: str = field(repr=False)
    executor_id: str = "application-executor-1"
    require_unprivileged_db: bool = True
    poll_seconds: float = 5.0

    @classmethod
    def from_env(cls, env=os.environ):
        dsn = env.get("IMPACT_EXECUTOR_DSN", "")
        if not dsn:
            raise RuntimeError("IMPACT_EXECUTOR_DSN is required")
        executor_id = env.get("IMPACT_EXECUTOR_ID", "application-executor-1")
        if not ID.fullmatch(executor_id):
            raise RuntimeError("Invalid executor id")
        return cls(dsn, executor_id, env.get("IMPACT_REQUIRE_UNPRIVILEGED_DB", "1") == "1")


class ApplicationExecutor:
    def __init__(self, settings):
        self.s = settings
        # Governed write methods receive the tenant transaction explicitly. No API login is used.
        self.service = Service(Settings("executor", "", "", "", "", "", "", "", "", "", ""), None)
        self.stopping = False
        self.iterations = self.succeeded = self.failed = self.failures = 0

    @contextmanager
    def transaction(self, tenant=None, lock=False):
        with psycopg.connect(
            self.s.dsn, row_factory=dict_row, connect_timeout=5, prepare_threshold=None
        ) as c:
            login = c.execute(LOGIN_QUERY).fetchone()
            if self.s.require_unprivileged_db and (
                login["rolsuper"]
                or login["rolbypassrls"]
                or login["rolinherit"]
                or login["owns_schema"]
                or login["memberships"] != ["impact_app"]
                or login["login"] != "impact_executor_login"
            ):
                raise RuntimeError("EXECUTOR_LOGIN_TOPOLOGY")
            c.execute("SET LOCAL ROLE impact_app")
            c.execute("SET LOCAL statement_timeout='55s'")
            if tenant:
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
                if lock:
                    c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            yield c

    def heartbeat(self, state="RUNNING"):
        with self.transaction() as c:
            c.execute(
                "INSERT INTO impact.executor_heartbeat(executor_id,build,state,started_at,beat_at,"
                "stopped_at,iterations,succeeded,failed,failures) VALUES(%s,%s,%s,"
                "statement_timestamp(),statement_timestamp(),"
                "CASE WHEN %s='STOPPED' THEN statement_timestamp() END,%s,%s,%s,%s) "
                "ON CONFLICT(executor_id) DO UPDATE SET state=EXCLUDED.state,beat_at=EXCLUDED.beat_at,"
                "stopped_at=EXCLUDED.stopped_at,iterations=EXCLUDED.iterations,"
                "succeeded=EXCLUDED.succeeded,failed=EXCLUDED.failed,failures=EXCLUDED.failures",
                (
                    self.s.executor_id,
                    BUILD,
                    state,
                    state,
                    self.iterations,
                    self.succeeded,
                    self.failed,
                    self.failures,
                ),
            )

    def due_tenants(self):
        with self.transaction() as c:
            return [
                str(r["tenant_id"])
                for r in c.execute(
                    "SELECT tenant_id FROM impact.executor_due_tenants(statement_timestamp())"
                ).fetchall()
            ]

    def claim(self, tenant):
        with self.transaction(tenant, lock=True) as c:
            row = c.execute(
                "SELECT j.job_id,j.lease_generation FROM impact.job j JOIN impact.import_commit i "
                "ON i.tenant_id=j.tenant_id AND i.job_id=j.job_id "
                "JOIN impact.tenant_root t ON t.tenant_id=j.tenant_id "
                "WHERE j.tenant_id=%s AND t.lifecycle_state='Active' AND j.job_class='IMPORT_COMMIT' "
                "AND ((j.state='Queued' AND j.cancellation_requested_at IS NULL "
                "AND i.next_attempt_at<=statement_timestamp()) OR "
                "(j.state='Running' AND j.lease_expires_at<=statement_timestamp())) "
                "ORDER BY i.next_attempt_at,j.job_id FOR UPDATE OF j,i SKIP LOCKED LIMIT 1",
                (tenant,),
            ).fetchone()
            if not row:
                return None
            generation = row["lease_generation"] + 1
            c.execute(
                "UPDATE impact.job SET state='Running',lease_generation=%s,"
                "lease_expires_at=statement_timestamp()+interval '60 seconds' "
                "WHERE tenant_id=%s AND job_id=%s",
                (generation, tenant, row["job_id"]),
            )
            c.execute(
                "UPDATE impact.import_commit SET lease_owner=%s,attempts=attempts+1,"
                "last_attempt_at=statement_timestamp() WHERE tenant_id=%s AND job_id=%s",
                (self.s.executor_id, tenant, row["job_id"]),
            )
            return str(row["job_id"]), generation

    def fenced(self, c, tenant, job_id, generation):
        return c.execute(
            "SELECT j.*,i.import_id,i.lease_owner FROM impact.job j JOIN impact.import_commit i "
            "ON i.tenant_id=j.tenant_id AND i.job_id=j.job_id WHERE j.tenant_id=%s "
            "AND j.job_id=%s AND j.job_class='IMPORT_COMMIT' AND j.state='Running' "
            "AND j.lease_generation=%s AND j.lease_expires_at>statement_timestamp() "
            "AND i.lease_owner=%s FOR UPDATE OF j,i",
            (tenant, job_id, generation, self.s.executor_id),
        ).fetchone()

    def perform(self, tenant, job_id, generation):
        with self.transaction(tenant, lock=True) as c:
            job = self.fenced(c, tenant, job_id, generation)
            if not job or job["cancellation_requested_at"]:
                return False
            row = c.execute(
                "SELECT r.*,v.payload FROM impact.object_registry r JOIN impact.object_revision v "
                "ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
                "WHERE r.tenant_id=%s AND r.object_id=%s FOR UPDATE OF r",
                (tenant, job["import_id"]),
            ).fetchone()
            if not row or row["lifecycle_state"] != "Queued":
                raise DomainError("INVALID_STATE", 409, reason="PREVIEW_STALE")
            request = row["payload"].get("commit_request") or {}
            if request.get("job_id") != job_id or request.get("principal_id") != str(job["requester_id"]):
                raise DomainError("INVALID_STATE", 409, reason="PREVIEW_STALE")
            natural = c.execute(
                "SELECT impact.member_natural_identity(%s,%s) AS id",
                (tenant, request["principal_id"]),
            ).fetchone()["id"]
            if not natural:
                raise DomainError("POLICY_DENIED", 403, reason="AUTHORITY_CHANGED")
            identity = Identity(
                request["identity_id"],
                str(natural),
                "",
                datetime.fromisoformat(request["auth_time"].replace("Z", "+00:00")),
            )
            try:
                ctx = context(c, identity, tenant, write=True)
                if ctx.principal_id != request["principal_id"]:
                    raise DomainError("POLICY_DENIED", 403)
                authorize(c, ctx, "action_imports_commit", job["import_id"], hidden=True)
                if not any(
                    g["capability"] == "import.commit"
                    and g["scope_type"] == "TENANT"
                    and g["purpose"] is None
                    for g in ctx.grants
                ):
                    raise DomainError("POLICY_DENIED", 403)
                current = load(c, ctx, job["import_id"], "ImportJob", lock=True)
                receipt = self.service.imports.commit(
                    c,
                    ctx,
                    current,
                    {k: request[k] for k in ("preview_hash", "workflow_version", "accept_warnings")},
                    job_id,
                    executor=True,
                )
            except DomainError as exc:
                if exc.code not in {"POLICY_DENIED", "AUTH_REQUIRED", "RESOURCE_UNAVAILABLE"}:
                    raise
                raise DomainError("POLICY_DENIED", 403, reason="AUTHORITY_CHANGED") from None
            audit(c, ctx, "action_imports_commit", receipt, job_id)
            updated = c.execute(
                "UPDATE impact.job SET state='Succeeded',lease_expires_at=NULL,"
                "output_manifest=jsonb_build_object('import_id',%s::text,'revision_id',%s::text) "
                "WHERE tenant_id=%s AND job_id=%s AND state='Running' AND lease_generation=%s "
                "AND lease_expires_at>statement_timestamp() RETURNING job_id",
                (str(job["import_id"]), receipt["revision_id"], tenant, job_id, generation),
            ).fetchone()
            if not updated:
                raise DomainError("CONFLICT_VERSION", 409, reason="LEASE_EXPIRED")
            c.execute(
                "UPDATE impact.import_commit SET completed_at=statement_timestamp(),lease_owner=NULL "
                "WHERE tenant_id=%s AND job_id=%s AND lease_owner=%s",
                (tenant, job_id, self.s.executor_id),
            )
            return True

    def fail(self, tenant, job_id, generation, error_class):
        with self.transaction(tenant, lock=True) as c:
            if not self.fenced(c, tenant, job_id, generation):
                return False
            c.execute(
                "UPDATE impact.job SET state='Failed',lease_expires_at=NULL WHERE tenant_id=%s "
                "AND job_id=%s AND lease_generation=%s AND state='Running'",
                (tenant, job_id, generation),
            )
            c.execute(
                "UPDATE impact.import_commit SET last_error_class=%s,completed_at=statement_timestamp(),"
                "lease_owner=NULL WHERE tenant_id=%s AND job_id=%s AND lease_owner=%s",
                (error_class, tenant, job_id, self.s.executor_id),
            )
            return True

    def run_once(self):
        for tenant in self.due_tenants():
            if self.stopping:
                break
            claim = self.claim(tenant)
            if not claim:
                continue
            job_id, generation = claim
            try:
                if self.perform(tenant, job_id, generation):
                    self.succeeded += 1
            except DomainError as exc:
                error_class = next(
                    (candidate for candidate in (exc.reason, exc.code) if candidate in ERRORS),
                    "COMMIT_DEFECT",
                )
                self.failed += int(self.fail(tenant, job_id, generation, error_class))
            except psycopg.OperationalError:
                self.failures += 1
                LOG.warning("executor database unavailable")
            except Exception:
                self.failures += 1
                LOG.exception("executor job failed")
                self.failed += int(self.fail(tenant, job_id, generation, "COMMIT_DEFECT"))
        self.iterations += 1
        self.heartbeat("STOPPING" if self.stopping else "RUNNING")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--executor-id")
    args = parser.parse_args()
    settings = ExecutorSettings.from_env()
    if args.executor_id:
        settings = ExecutorSettings(settings.dsn, args.executor_id, settings.require_unprivileged_db)
    executor = ApplicationExecutor(settings)
    signal.signal(signal.SIGTERM, lambda *_: setattr(executor, "stopping", True))
    signal.signal(signal.SIGINT, lambda *_: setattr(executor, "stopping", True))
    executor.heartbeat()
    try:
        while not executor.stopping:
            executor.run_once()
            if args.once:
                break
            time.sleep(settings.poll_seconds)
    finally:
        executor.heartbeat("STOPPED")


if __name__ == "__main__":
    main()
