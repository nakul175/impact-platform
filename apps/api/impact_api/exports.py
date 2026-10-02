"""Report exports (v0.23): request, cancellation, status and mediated download of PDF, XLSX and
DOCX renderings of an approved, frozen report package.

A request is a business command on the report: in the same transaction as its receipt, audit and
outbox event it writes one `impact.job` row (job_class REPORT_EXPORT, state Queued, the pinned
package in input_manifest) and one `impact.report_export` row; it never renders. The worker
(`worker.py`, REPORT_EXPORT job class) claims the job under a generation-fenced lease, renders it
outside any transaction (`export_render.py`) and stores the immutable artifact in its fenced outcome
transaction. A download is mediated: authorised, recipient-checked for a publication, and logged in
`report_export_access`; the bytes are never re-pointed.
"""

import hashlib
from uuid import uuid4

from psycopg.types.json import Jsonb

from .domain import DomainError, unavailable
from .export_render import EXTENSIONS, RENDERER_VERSION
from .store import authorize, context, load

JOB_CLASS = "REPORT_EXPORT"
TERMINAL = ("Succeeded", "SucceededWithIssues", "Failed", "Cancelled")
# Export jobs not yet finished that one tenant may hold at once (VF-PER-005: explicit limits).
OPEN_EXPORT_LIMIT = 20


class Exports:
    def __init__(self, service):
        self.service = service

    # -- commands (inside Service.command's transaction, after authorisation) --------------------

    def request(self, c, ctx, report, data):
        format = data["format"]
        # The same checks as the HTML and CSV export: an approved report with a frozen package whose
        # reconciliation is unchanged; every bound result readable by the requester.
        current, binding, _, _ = self.service.reporting._approved_package(c, ctx, report["object_id"])
        duplicate = c.execute(
            "SELECT j.job_id FROM impact.report_export e JOIN impact.job j ON j.tenant_id=e.tenant_id "
            "AND j.job_id=e.job_id WHERE e.tenant_id=%s AND e.report_id=%s AND e.report_revision=%s "
            "AND e.format=%s AND e.renderer_version=%s AND j.state NOT IN ('Failed','Cancelled') LIMIT 1",
            (ctx.tenant_id, current["object_id"], current["head_revision"], format, RENDERER_VERSION),
        ).fetchone()
        if duplicate:
            raise DomainError("INVALID_STATE", 409, reason="EXPORT_ALREADY_REQUESTED")
        open_jobs = c.execute(
            "SELECT count(*) AS n FROM impact.job WHERE tenant_id=%s AND job_class=%s "
            "AND state NOT IN ('Succeeded','SucceededWithIssues','Failed','Cancelled')",
            (ctx.tenant_id, JOB_CLASS),
        ).fetchone()["n"]
        if open_jobs >= OPEN_EXPORT_LIMIT:
            raise DomainError("LIMIT_EXCEEDED", 429, reason="EXPORT_QUEUE_LIMIT")
        scope = next(
            g["scope_id"]
            for g in ctx.grants
            if g["capability"] == "report.export" and g["scope_type"] == "TENANT" and g["purpose"] is None
        )
        job_id = str(uuid4())
        digest = bytes(binding["reconciliation_digest"])
        manifest = {
            "report_id": str(current["object_id"]),
            "report_revision": str(current["head_revision"]),
            "format": format,
            "renderer_version": RENDERER_VERSION,
            "snapshot_id": str(binding["snapshot_id"]),
            "snapshot_revision": str(binding["snapshot_revision"]),
            "template_revision": str(binding["template_revision"]),
            "reconciliation_sha256": digest.hex(),
        }
        row = c.execute(
            "INSERT INTO impact.job(tenant_id,job_id,job_class,requester_id,scope_id,state,input_manifest) "
            "VALUES(%s,%s,%s,%s,%s,'Queued',%s) RETURNING now() AS at",
            (ctx.tenant_id, job_id, JOB_CLASS, ctx.principal_id, scope, Jsonb(manifest)),
        ).fetchone()
        # Database time, as the worker compares due times with the database clock.
        c.execute(
            "INSERT INTO impact.report_export(tenant_id,job_id,report_id,report_revision,format,"
            "renderer_version,reconciliation_digest,requested_by,requested_at,next_attempt_at) "
            "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,now(),now())",
            (
                ctx.tenant_id,
                job_id,
                current["object_id"],
                current["head_revision"],
                format,
                RENDERER_VERSION,
                digest,
                ctx.principal_id,
            ),
        )
        return self.receipt(current, "Queued", job_id, row["at"])

    def cancel(self, c, ctx, report, data):
        job = c.execute(
            "SELECT j.* FROM impact.job j JOIN impact.report_export e ON e.tenant_id=j.tenant_id "
            "AND e.job_id=j.job_id WHERE j.tenant_id=%s AND j.job_id=%s AND e.report_id=%s FOR UPDATE OF j",
            (ctx.tenant_id, data["job_id"], report["object_id"]),
        ).fetchone()
        if not job:
            unavailable()
        if job["state"] in TERMINAL:
            raise DomainError("INVALID_STATE", 409, reason="EXPORT_ALREADY_FINISHED")
        # Only a request is recorded: the worker cancels a job that has not started (and never
        # claims one with a cancellation request); a started job is not cancelled (job_item
        # 'cancellation' NOT_CANCELLED_STARTED).
        row = c.execute(
            "UPDATE impact.job SET cancellation_requested_at=COALESCE(cancellation_requested_at,now()) "
            "WHERE tenant_id=%s AND job_id=%s RETURNING now() AS at",
            (ctx.tenant_id, data["job_id"]),
        ).fetchone()
        return self.receipt(report, "CancellationRequested", data["job_id"], row["at"])

    @staticmethod
    def receipt(report, state, job_id, at):
        return {
            "operation_id": "",
            "object_id": str(report["object_id"]),
            "revision_id": str(report["head_revision"]),
            "business_state": state,
            "saved_at": at.isoformat(),
            "correlation_id": "",
            "job_id": str(job_id),
        }

    # -- disclosure pinning ----------------------------------------------------------------------

    def resolve(self, c, ctx, report, formats):
        """Pin each named format to the succeeded artifact of this report revision (the current
        rendering version first, then the newest)."""
        pinned = []
        for format in formats:
            artifact = c.execute(
                "SELECT a.job_id,a.content_sha256 FROM impact.report_export_artifact a "
                "WHERE a.tenant_id=%s AND a.report_id=%s AND a.report_revision=%s AND a.format=%s "
                "ORDER BY (a.renderer_version=%s) DESC,a.created_at DESC,a.job_id LIMIT 1",
                (ctx.tenant_id, report["object_id"], report["head_revision"], format, RENDERER_VERSION),
            ).fetchone()
            if not artifact:
                raise DomainError("INVALID_STATE", 409, reason="EXPORT_ARTIFACT_REQUIRED")
            pinned.append(
                {
                    "format": format,
                    "job_id": str(artifact["job_id"]),
                    "content_sha256": bytes(artifact["content_sha256"]).hex(),
                }
            )
        return pinned

    def verify(self, c, ctx, report, payload):
        """A stored disclosure's pinned artifacts still exist for exactly the disclosed revision."""
        pinned = payload.get("export_artifacts") or []
        if sorted(item["format"] for item in pinned) != sorted(payload.get("export_formats") or []):
            raise DomainError("INVALID_STATE", 409, reason="EXPORT_ARTIFACT_REQUIRED")
        for item in pinned:
            artifact = c.execute(
                "SELECT content_sha256 FROM impact.report_export_artifact WHERE tenant_id=%s AND job_id=%s "
                "AND report_id=%s AND report_revision=%s AND format=%s",
                (ctx.tenant_id, item["job_id"], report["object_id"], report["head_revision"], item["format"]),
            ).fetchone()
            if not artifact or bytes(artifact["content_sha256"]).hex() != item["content_sha256"]:
                raise DomainError("INVALID_STATE", 409, reason="EXPORT_ARTIFACT_REQUIRED")
        return pinned

    def bind(self, c, ctx, disclosure_id, disclosure_revision, payload, at):
        for item in payload.get("export_artifacts") or []:
            c.execute(
                "INSERT INTO impact.report_publication_export(tenant_id,disclosure_id,disclosure_revision,"
                "format,job_id,content_sha256,created_at) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                (
                    ctx.tenant_id,
                    disclosure_id,
                    disclosure_revision,
                    item["format"],
                    item["job_id"],
                    bytes.fromhex(item["content_sha256"]),
                    at,
                ),
            )

    # -- reads -----------------------------------------------------------------------------------

    def listing(self, identity, tenant, report_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_report_exports", report_id, hidden=True)
            load(c, ctx, report_id, "Report", "reports.read")
            rows = c.execute(
                "SELECT e.*,j.state,j.cancellation_requested_at,a.media_type,a.content_sha256,"
                "octet_length(a.body) AS size_bytes,i.outcome AS cancellation_outcome "
                "FROM impact.report_export e JOIN impact.job j ON j.tenant_id=e.tenant_id AND j.job_id=e.job_id "
                "LEFT JOIN impact.report_export_artifact a ON a.tenant_id=e.tenant_id AND a.job_id=e.job_id "
                "LEFT JOIN impact.job_item i ON i.tenant_id=e.tenant_id AND i.job_id=e.job_id "
                "AND i.item_key='cancellation' WHERE e.tenant_id=%s AND e.report_id=%s "
                "ORDER BY e.requested_at DESC,e.job_id LIMIT 100",
                (tenant, report_id),
            ).fetchall()
            return {"items": [self.item(row) for row in rows]}

    @staticmethod
    def item(row):
        return {
            "job_id": str(row["job_id"]),
            "report_id": str(row["report_id"]),
            "report_revision": str(row["report_revision"]),
            "format": row["format"],
            "renderer_version": row["renderer_version"],
            "state": row["state"],
            "attempts": row["attempts"],
            "last_error_class": row["last_error_class"],
            "cancellation_requested": row["cancellation_requested_at"] is not None,
            "cancellation_outcome": row["cancellation_outcome"],
            "requested_at": row["requested_at"].isoformat(),
            "completed_at": row["completed_at"].isoformat() if row["completed_at"] else None,
            "media_type": row["media_type"],
            "content_sha256": bytes(row["content_sha256"]).hex() if row["content_sha256"] else None,
            "size_bytes": row["size_bytes"],
        }

    @staticmethod
    def log(c, ctx, job_id, disclosure_id, format, correlation):
        c.execute(
            "INSERT INTO impact.report_export_access(tenant_id,access_id,job_id,disclosure_id,principal_id,"
            "membership_id,format,access_mode,accessed_at,correlation_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,now(),%s)",
            (
                ctx.tenant_id,
                str(uuid4()),
                job_id,
                disclosure_id,
                ctx.principal_id,
                ctx.membership_id,
                format,
                "RECIPIENT_DOWNLOAD" if disclosure_id else "INTERNAL_DOWNLOAD",
                correlation,
            ),
        )

    @staticmethod
    def artifact(row):
        body = bytes(row["body"])
        digest = hashlib.sha256(body).digest()
        if digest != bytes(row["content_sha256"]):
            # Stored bytes that no longer match their recorded digest are never served.
            raise DomainError("SERVICE_UNAVAILABLE", 503, reason="EXPORT_ARTIFACT_INTEGRITY")
        return {
            "body": body,
            "media_type": row["media_type"],
            "digest": digest.hex(),
            "filename": "impact-report-"
            + str(row["report_id"])[:8]
            + "-"
            + str(row["report_revision"])[:8]
            + EXTENSIONS[row["format"]],
        }

    def download(self, identity, tenant, report_id, job_id, correlation):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "download_report_export", report_id, hidden=True)
            load(c, ctx, report_id, "Report", "reports.read")
            row = c.execute(
                "SELECT * FROM impact.report_export_artifact WHERE tenant_id=%s AND job_id=%s AND report_id=%s",
                (tenant, job_id, report_id),
            ).fetchone()
            if not row:
                unavailable()
            artifact = self.artifact(row)
            self.log(c, ctx, job_id, None, row["format"], correlation)
            return artifact

    def publication(self, identity, tenant, disclosure_id, format, correlation):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "download_controlled_publication_" + format.lower(), disclosure_id, hidden=True)
            disclosure = self.service.reporting.recipient_disclosure(c, ctx, disclosure_id, download=True)
            row = c.execute(
                "SELECT a.* FROM impact.report_publication_export p JOIN impact.report_export_artifact a "
                "ON a.tenant_id=p.tenant_id AND a.job_id=p.job_id WHERE p.tenant_id=%s AND p.disclosure_id=%s "
                "AND p.disclosure_revision=%s AND p.format=%s AND a.content_sha256=p.content_sha256",
                (tenant, disclosure_id, disclosure["head_revision"], format),
            ).fetchone()
            if not row:
                unavailable()
            artifact = self.artifact(row)
            self.log(c, ctx, row["job_id"], disclosure_id, format, correlation)
            return artifact
