"""Frozen report packages, numeric reconciliation and controlled publication."""

import base64
import csv
import hashlib
import io
import re
from datetime import datetime, timedelta, timezone
from html import escape
from uuid import uuid4

from .domain import DomainError, unavailable
from .store import audit, authorize, context, hash_data, load, write


BINDING_TOKEN = re.compile(r"\{\{([A-Za-z][A-Za-z0-9_.-]{0,63})\}\}")
BARE_NUMBER = re.compile(r"(?<![\w{])-?\d+(?:\.\d+)?(?![\w}])")
REPORT_STYLE = (
    "body{font:16px system-ui;max-width:850px;margin:40px auto;padding:0 24px;color:#203c34}"
    "header{border-bottom:2px solid #203c34;margin-bottom:32px}section{margin:32px 0}"
    "table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:12px 16px;"
    "border-bottom:1px solid #ccd6cf}th{background:#f1f5ed}.bound-number{font-weight:700}"
    "footer{margin-top:48px;padding-top:16px;border-top:1px solid #ccd6cf;font-size:12px;"
    "color:#586d62}code{overflow-wrap:anywhere}"
)
REPORT_STYLE_HASH = base64.b64encode(hashlib.sha256(REPORT_STYLE.encode()).digest()).decode()
REPORT_CSP = (
    "default-src 'none'; style-src 'sha256-"
    + REPORT_STYLE_HASH
    + "'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
)


class Reporting:
    def __init__(self, service):
        self.service = service

    def reconcile(self, c, ctx, data, complete=False):
        from .service import revision

        if data.get("audience_class", "INTERNAL") != "INTERNAL":
            raise DomainError("POLICY_DENIED", 403, reason="INTERNAL_REPORTS_ONLY")
        required = ["template_version", "snapshot_id", "language", "audience_class", "sections"]
        if complete and any(data.get(field) in (None, "", []) for field in required):
            raise DomainError("VALIDATION_FAILED", reason="REPORT_PACKAGE_INCOMPLETE")
        if not data.get("snapshot_id") or not data.get("template_version"):
            return None
        snapshot = load(c, ctx, data["snapshot_id"], "Snapshot", "snapshots.read")
        if snapshot["lifecycle_state"] != "Locked":
            raise DomainError("INVALID_STATE", 409, reason="LOCKED_SNAPSHOT_REQUIRED")
        template = revision(
            c,
            ctx,
            data["template_version"],
            "ReportTemplate",
            "report-templates.read",
        )
        template_head = load(c, ctx, template["object_id"], "ReportTemplate", "report-templates.read")
        if (
            template_head["lifecycle_state"] not in {"Approved", "Active"}
            or str(template_head["head_revision"]) != data["template_version"]
        ):
            raise DomainError("INVALID_STATE", 409, reason="APPROVED_REPORT_TEMPLATE_REQUIRED")
        sections = data.get("sections", [])
        section_codes = [section["section_code"] for section in sections]
        if len(section_codes) != len(set(section_codes)):
            raise DomainError("VALIDATION_FAILED", reason="DUPLICATE_REPORT_SECTION")
        required_sections = {
            item["section_code"] for item in template["payload"].get("sections", []) if item.get("required")
        }
        if complete and not required_sections <= set(section_codes):
            raise DomainError("VALIDATION_FAILED", reason="REQUIRED_REPORT_SECTION_MISSING")
        snapshot_results = set(snapshot["payload"].get("result_versions", []))
        snapshot_evidence = set(snapshot["payload"].get("evidence_versions", []))
        bindings = []
        evidence = []
        for section in sections:
            codes = [binding["binding_code"] for binding in section["bindings"]]
            if len(codes) != len(set(codes)):
                raise DomainError("VALIDATION_FAILED", reason="DUPLICATE_NUMERIC_BINDING")
            template_section = next(
                (
                    item
                    for item in template["payload"].get("sections", [])
                    if item["section_code"] == section["section_code"]
                ),
                None,
            )
            if template_section and len(section["narrative"]) > template_section.get(
                "narrative_limit", 20000
            ):
                raise DomainError("VALIDATION_FAILED", reason="REPORT_NARRATIVE_LIMIT")
            if (
                complete
                and template_section
                and not set(template_section.get("required_binding_codes", [])) <= set(codes)
            ):
                raise DomainError("VALIDATION_FAILED", reason="REQUIRED_NUMERIC_BINDING_MISSING")
            for binding in section["bindings"]:
                if binding["result_revision"] not in snapshot_results:
                    raise DomainError("VALIDATION_FAILED", reason="RESULT_NOT_IN_SNAPSHOT")
                result = revision(
                    c,
                    ctx,
                    binding["result_revision"],
                    "CalculatedResult",
                    "calculated-results.read",
                )
                payload = result["payload"]
                if payload.get("mode") != "OFFICIAL":
                    raise DomainError("INVALID_STATE", 409, reason="OFFICIAL_RESULT_REQUIRED")
                if any(binding[key] != payload.get(key) for key in ["unit", "display_decimals"]):
                    raise DomainError("INCOMPATIBLE_MEASURE")
                bindings.append(
                    {
                        "section_code": section["section_code"],
                        "binding_code": binding["binding_code"],
                        "result_revision": binding["result_revision"],
                        "displayed_value": payload.get("displayed_value"),
                        "unit": payload.get("unit"),
                        "display_decimals": payload.get("display_decimals"),
                    }
                )
            for evidence_revision in section["evidence_revisions"]:
                if evidence_revision not in snapshot_evidence:
                    raise DomainError("VALIDATION_FAILED", reason="EVIDENCE_NOT_IN_SNAPSHOT")
                revision(c, ctx, evidence_revision, "Evidence", "evidence.read")
                evidence.append(evidence_revision)
            if complete:
                narrative = section["narrative"]
                for token in BINDING_TOKEN.findall(narrative):
                    if token not in codes:
                        raise DomainError("VALIDATION_FAILED", reason="UNKNOWN_NARRATIVE_BINDING")
                if BARE_NUMBER.search(BINDING_TOKEN.sub("", narrative)):
                    raise DomainError("VALIDATION_FAILED", reason="UNBOUND_NARRATIVE_NUMBER")
        digest_input = {
            "snapshot_revision": str(snapshot["head_revision"]),
            "template_revision": str(template["revision_id"]),
            "language": data.get("language"),
            "audience_class": data.get("audience_class"),
            "sections": sections,
            "bindings": bindings,
            "evidence": evidence,
        }
        return {
            "snapshot": snapshot,
            "template": template,
            "bindings": bindings,
            "digest": hash_data(digest_input),
        }

    def bind(self, c, ctx, report, approved):
        package = self.reconcile(c, ctx, report["payload"], complete=True)
        c.execute(
            "INSERT INTO impact.report_package_binding VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                ctx.tenant_id,
                report["object_id"],
                approved["revision_id"],
                package["snapshot"]["object_id"],
                package["snapshot"]["head_revision"],
                package["template"]["revision_id"],
                package["digest"],
                datetime.now(timezone.utc),
            ),
        )

    def _approved_package(self, c, ctx, report_id):
        from .service import revision

        report = load(c, ctx, report_id, "Report", "reports.read")
        if report["lifecycle_state"] != "Approved":
            raise DomainError("INVALID_STATE", 409, reason="APPROVED_REPORT_REQUIRED")
        binding = c.execute(
            "SELECT * FROM impact.report_package_binding "
            "WHERE tenant_id=%s AND report_id=%s AND report_revision=%s",
            (ctx.tenant_id, report_id, report["head_revision"]),
        ).fetchone()
        if not binding:
            raise DomainError("INVALID_STATE", 409, reason="FROZEN_REPORT_PACKAGE_REQUIRED")
        package = self.reconcile(c, ctx, report["payload"], complete=True)
        if package["digest"] != bytes(binding["reconciliation_digest"]):
            raise DomainError("CONFLICT_VERSION", 409, reason="REPORT_RECONCILIATION_CHANGED")
        values = {}
        for item in package["bindings"]:
            result = revision(
                c,
                ctx,
                item["result_revision"],
                "CalculatedResult",
                "calculated-results.read",
            )["payload"]
            values[(item["section_code"], item["binding_code"])] = result
        return report, binding, package, values

    @staticmethod
    def _narrative_html(text, section_code, values):
        chunks, start = [], 0
        for match in BINDING_TOKEN.finditer(text):
            chunks.append(escape(text[start : match.start()]))
            result = values[(section_code, match.group(1))]
            chunks.append(
                '<span class="bound-number" data-binding="%s">%s %s</span>'
                % (
                    escape(match.group(1)),
                    escape(str(result.get("displayed_value", "—"))),
                    escape(result.get("unit", "")),
                )
            )
            start = match.end()
        chunks.append(escape(text[start:]))
        return "".join(chunks)

    def _render_html(self, report, binding, package, values):
        title = package["template"]["payload"].get("title", "Impact report")
        chunks = [
            '<!doctype html><html lang="%s"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            "<title>%s</title><style>%s</style></head><body>"
            % (escape(report["payload"]["language"]), escape(title), REPORT_STYLE),
            "<header><p>CONTROLLED · APPROVED SNAPSHOT PACKAGE</p><h1>%s</h1></header>" % escape(title),
        ]
        for section in report["payload"]["sections"]:
            chunks.append("<section><h2>%s</h2>" % escape(section["heading"]))
            for paragraph in section["narrative"].splitlines() or [""]:
                chunks.append("<p>%s</p>" % self._narrative_html(paragraph, section["section_code"], values))
            if section["bindings"]:
                chunks.append(
                    '<table><caption>Bound official results</caption><thead><tr><th scope="col">Metric</th>'
                    '<th scope="col">Value and unit</th></tr></thead><tbody>'
                )
                for numeric in section["bindings"]:
                    result = values[(section["section_code"], numeric["binding_code"])]
                    chunks.append(
                        '<tr><th scope="row">%s</th><td>%s %s</td></tr>'
                        % (
                            escape(numeric["binding_code"]),
                            escape(str(result.get("displayed_value", "—"))),
                            escape(result.get("unit", "")),
                        )
                    )
                chunks.append("</tbody></table>")
            chunks.append("</section>")
        chunks.append(
            "<footer><p>Report <code>%s</code> · revision <code>%s</code></p>"
            "<p>Snapshot <code>%s</code> · locked %s</p><p>Reconciliation SHA-256 <code>%s</code></p></footer></body></html>"
            % (
                escape(str(report["object_id"])),
                escape(str(report["head_revision"])),
                escape(str(package["snapshot"]["object_id"])),
                escape(package["snapshot"]["payload"]["locked_at"]),
                bytes(binding["reconciliation_digest"]).hex(),
            )
        )
        return "".join(chunks).encode()

    @staticmethod
    def _csv_text(value):
        value = str(value)
        return "'" + value if value.startswith(("=", "+", "-", "@", "\t", "\r")) else value

    def _render_csv(self, report, package, values):
        output = io.StringIO(newline="")
        rows = csv.writer(output, lineterminator="\r\n")
        rows.writerow(
            [
                "section_code",
                "section_heading",
                "binding_code",
                "displayed_value",
                "unit",
                "result_revision",
                "report_revision",
                "snapshot_id",
            ]
        )
        for section in report["payload"]["sections"]:
            for numeric in section["bindings"]:
                result = values[(section["section_code"], numeric["binding_code"])]
                rows.writerow(
                    [
                        self._csv_text(section["section_code"]),
                        self._csv_text(section["heading"]),
                        self._csv_text(numeric["binding_code"]),
                        result.get("displayed_value", ""),
                        self._csv_text(result.get("unit", "")),
                        numeric["result_revision"],
                        str(report["head_revision"]),
                        str(package["snapshot"]["object_id"]),
                    ]
                )
        return output.getvalue().encode("utf-8")

    def export(self, identity, tenant, report_id, format="HTML"):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "export_report_package", report_id, hidden=True)
            report, binding, package, values = self._approved_package(c, ctx, report_id)
            body = (
                self._render_html(report, binding, package, values)
                if format == "HTML"
                else self._render_csv(report, package, values)
            )
            return body.decode("utf-8"), hashlib.sha256(body).hexdigest()

    def validate_disclosure(self, c, ctx, data):
        from .service import revision

        if data.get("public") is not False:
            raise DomainError("POLICY_DENIED", 403, reason="ANONYMOUS_PUBLICATION_NOT_IMPLEMENTED")
        report_revision = revision(c, ctx, data["artifact_version"], "Report", "reports.read")
        report = load(c, ctx, report_revision["object_id"], "Report", "reports.read")
        if (
            report["lifecycle_state"] != "Approved"
            or str(report["head_revision"]) != data["artifact_version"]
        ):
            raise DomainError("INVALID_STATE", 409, reason="APPROVED_REPORT_REQUIRED")
        if not c.execute(
            "SELECT 1 FROM impact.report_package_binding "
            "WHERE tenant_id=%s AND report_id=%s AND report_revision=%s",
            (ctx.tenant_id, report["object_id"], data["artifact_version"]),
        ).fetchone():
            raise DomainError("INVALID_STATE", 409, reason="FROZEN_REPORT_PACKAGE_REQUIRED")
        try:
            expires = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
        except (TypeError, ValueError):
            raise DomainError("VALIDATION_FAILED", reason="PUBLICATION_EXPIRY_INVALID") from None
        now = datetime.now(timezone.utc)
        if expires.tzinfo is None or expires <= now or expires > now + timedelta(days=90):
            raise DomainError("VALIDATION_FAILED", reason="PUBLICATION_EXPIRY_INVALID")
        recipients = data.get("recipients", [])
        identifiers = [item["membership_id"] for item in recipients]
        if not identifiers or len(identifiers) != len(set(identifiers)):
            raise DomainError("VALIDATION_FAILED", reason="PUBLICATION_RECIPIENTS_INVALID")
        for membership_id in identifiers:
            eligible = c.execute(
                "SELECT 1 FROM impact.membership_current m "
                "JOIN impact.object_registry r ON r.tenant_id=m.tenant_id AND r.object_id=m.object_id "
                "JOIN impact.tenant_principal p ON p.tenant_id=m.tenant_id AND p.identity_id=m.identity_id "
                "WHERE m.tenant_id=%s AND m.object_id=%s AND r.lifecycle_state='Active' "
                "AND (m.status IS NULL OR m.status='Active') "
                "AND (m.expires_at IS NULL OR m.expires_at>now()) AND p.active",
                (ctx.tenant_id, membership_id),
            ).fetchone()
            if not eligible:
                unavailable()
        return report

    def recipients(self, identity, tenant):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_publication_recipients")
            rows = c.execute(
                "SELECT m.object_id,m.external FROM impact.membership_current m "
                "JOIN impact.object_registry r ON r.tenant_id=m.tenant_id AND r.object_id=m.object_id "
                "JOIN impact.tenant_principal p ON p.tenant_id=m.tenant_id AND p.identity_id=m.identity_id "
                "WHERE m.tenant_id=%s AND r.lifecycle_state='Active' "
                "AND (m.status IS NULL OR m.status='Active') "
                "AND (m.expires_at IS NULL OR m.expires_at>now()) AND p.active "
                "ORDER BY m.external DESC,m.object_id LIMIT 501",
                (ctx.tenant_id,),
            ).fetchall()
            if len(rows) > 500:
                raise DomainError("LIMIT_EXCEEDED", 422, reason="PUBLICATION_RECIPIENT_LIMIT")
            return {
                "items": [
                    {
                        "membership_id": str(row["object_id"]),
                        "label": ("External" if row["external"] else "Workspace")
                        + " member "
                        + str(row["object_id"])[:8],
                        "external": bool(row["external"]),
                    }
                    for row in rows
                ]
            }

    def request_disclosure(self, c, ctx, data):
        from .service import revision

        payload = {key: value for key, value in data.items() if key != "workflow_version"}
        report = self.validate_disclosure(c, ctx, payload)
        template = revision(
            c,
            ctx,
            data["workflow_version"],
            "WorkflowTemplate",
            "workflow-templates.read",
        )
        template_head = load(c, ctx, template["object_id"], "WorkflowTemplate")
        if (
            template_head["lifecycle_state"] != "Active"
            or str(template_head["head_revision"]) != data["workflow_version"]
            or template["payload"].get("required_approvals") != 1
            or template["payload"].get("independent") is not True
        ):
            raise DomainError("INVALID_STATE", 409, reason="ACTIVE_WORKFLOW_REQUIRED")
        candidates = c.execute(
            "SELECT DISTINCT m.object_id FROM impact.membership_current m "
            "JOIN impact.object_registry mr ON mr.tenant_id=m.tenant_id AND mr.object_id=m.object_id "
            "JOIN impact.tenant_principal p ON p.tenant_id=m.tenant_id AND p.identity_id=m.identity_id "
            "JOIN impact.grant_current g ON g.tenant_id=p.tenant_id AND g.subject_id=p.principal_id "
            "JOIN impact.object_registry gr ON gr.tenant_id=g.tenant_id AND gr.object_id=g.object_id "
            "JOIN impact.scope_definition s ON s.tenant_id=g.tenant_id AND s.scope_id=g.scope_id "
            "WHERE m.tenant_id=%s AND mr.lifecycle_state='Active' "
            "AND (m.status IS NULL OR m.status='Active') AND (m.expires_at IS NULL OR m.expires_at>now()) "
            "AND p.active AND gr.lifecycle_state='Active' AND g.capability='report.publish' "
            "AND g.purpose IS NULL AND g.starts_at<=now() AND (g.expires_at IS NULL OR g.expires_at>now()) "
            "AND s.scope_type='TENANT' "
            "AND EXISTS(SELECT 1 FROM impact.grant_current wg "
            "JOIN impact.object_registry wgr ON wgr.tenant_id=wg.tenant_id AND wgr.object_id=wg.object_id "
            "JOIN impact.scope_definition ws ON ws.tenant_id=wg.tenant_id AND ws.scope_id=wg.scope_id "
            "WHERE wg.tenant_id=p.tenant_id AND wg.subject_id=p.principal_id "
            "AND wgr.lifecycle_state='Active' AND wg.capability='workflow.approve' AND wg.purpose IS NULL "
            "AND wg.starts_at<=now() AND (wg.expires_at IS NULL OR wg.expires_at>now()) "
            "AND ws.scope_type='TENANT') "
            "AND EXISTS(SELECT 1 FROM impact.grant_current dg "
            "JOIN impact.object_registry dgr ON dgr.tenant_id=dg.tenant_id AND dgr.object_id=dg.object_id "
            "JOIN impact.scope_definition ds ON ds.tenant_id=dg.tenant_id AND ds.scope_id=dg.scope_id "
            "WHERE dg.tenant_id=p.tenant_id AND dg.subject_id=p.principal_id "
            "AND dgr.lifecycle_state='Active' AND dg.capability='disclosures.read' AND dg.purpose IS NULL "
            "AND dg.starts_at<=now() AND (dg.expires_at IS NULL OR dg.expires_at>now()) "
            "AND ds.scope_type='TENANT') ORDER BY m.object_id LIMIT 101",
            (ctx.tenant_id,),
        ).fetchall()
        if not candidates or len(candidates) > 100:
            raise DomainError("INVALID_STATE", 409, reason="DISCLOSURE_REVIEWER_REQUIRED")
        disclosure = write(c, ctx, "Disclosure", payload, "Submitted")
        stage_id = str(uuid4())
        workflow = write(
            c,
            ctx,
            "Workflow",
            {
                "candidate_id": disclosure["object_id"],
                "candidate_revision": disclosure["revision_id"],
                "workflow_version": data["workflow_version"],
                "stages": [
                    {
                        "stage_id": stage_id,
                        "position": 0,
                        "required_approvals": 1,
                        "candidate_membership_ids": [str(item["object_id"]) for item in candidates],
                        "required_capability": "workflow.approve",
                        "independent": True,
                    }
                ],
            },
            "InReview",
            track_author=False,
        )
        c.execute(
            "INSERT INTO impact.workflow_author "
            "SELECT tenant_id,%s,natural_identity_id,%s FROM impact.object_natural_author "
            "WHERE tenant_id=%s AND object_id=%s",
            (
                workflow["object_id"],
                disclosure["revision_id"],
                ctx.tenant_id,
                disclosure["object_id"],
            ),
        )
        # The report reference is deliberately returned only through the reviewed candidate.
        assert str(report["head_revision"]) == payload["artifact_version"]
        return workflow

    def publish(self, c, ctx, report, data):
        if (
            report["lifecycle_state"] != "Approved"
            or str(report["head_revision"]) != data["approved_candidate_revision"]
        ):
            raise DomainError("CONFLICT_VERSION", 409, reason="APPROVED_REPORT_REVISION_REQUIRED")
        disclosure = load(c, ctx, data["disclosure_id"], "Disclosure", "disclosures.read", lock=True)
        if disclosure["lifecycle_state"] != "Approved" or disclosure["payload"].get(
            "artifact_version"
        ) != str(report["head_revision"]):
            raise DomainError("INVALID_STATE", 409, reason="APPROVED_DISCLOSURE_REQUIRED")
        self.validate_disclosure(c, ctx, disclosure["payload"])
        current, binding, package, values = self._approved_package(c, ctx, report["object_id"])
        bodies = {
            "HTML": (
                "text/html; charset=utf-8",
                self._render_html(current, binding, package, values),
            ),
            "CSV": (
                "text/csv; charset=utf-8",
                self._render_csv(current, package, values),
            ),
        }
        if any(len(body) > 5 * 1024 * 1024 for _, body in bodies.values()):
            raise DomainError("LIMIT_EXCEEDED", 422, reason="PUBLICATION_ARTIFACT_LIMIT")
        now = datetime.now(timezone.utc)
        published = write(
            c,
            ctx,
            "Disclosure",
            {**disclosure["payload"], "published_at": now.isoformat()},
            "Published",
            disclosure,
            track_author=False,
        )
        for format, (media_type, body) in bodies.items():
            c.execute(
                "INSERT INTO impact.report_publication_artifact "
                "(tenant_id,disclosure_id,disclosure_revision,report_id,report_revision,format,"
                "media_type,body,content_sha256,created_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    ctx.tenant_id,
                    disclosure["object_id"],
                    published["revision_id"],
                    report["object_id"],
                    report["head_revision"],
                    format,
                    media_type,
                    body,
                    hashlib.sha256(body).digest(),
                    now,
                ),
            )
        return published

    def withdraw(self, c, ctx, report, data, correlation):
        reason = data["reason"].strip()
        if not reason:
            raise DomainError("VALIDATION_FAILED", reason="WITHDRAWAL_REASON_REQUIRED")
        rows = c.execute(
            "SELECT r.*,v.payload,v.schema_version,v.author_id,v.revision_number,v.restriction_state "
            "FROM impact.disclosure_current d "
            "JOIN impact.object_registry r ON r.tenant_id=d.tenant_id AND r.object_id=d.object_id "
            "JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
            "WHERE d.tenant_id=%s AND d.artifact_version=%s AND r.lifecycle_state='Published' "
            "ORDER BY r.object_id LIMIT 101",
            (ctx.tenant_id, report["head_revision"]),
        ).fetchall()
        if not rows:
            raise DomainError("INVALID_STATE", 409, reason="ACTIVE_PUBLICATION_REQUIRED")
        if len(rows) > 100:
            raise DomainError("LIMIT_EXCEEDED", 422, reason="PUBLICATION_WITHDRAWAL_LIMIT")
        now = datetime.now(timezone.utc)
        receipts = []
        for disclosure in rows:
            receipts.append(
                write(
                    c,
                    ctx,
                    "Disclosure",
                    {
                        **disclosure["payload"],
                        "withdrawn_at": now.isoformat(),
                        "withdrawal_reason": reason,
                    },
                    "Withdrawn",
                    disclosure,
                    track_author=False,
                )
            )
        for receipt in receipts[1:]:
            audit(c, ctx, "publication.withdrawn", receipt, correlation)
        return receipts[0]

    def publication(self, identity, tenant, disclosure_id, format, correlation):
        operation = (
            "view_controlled_publication" if format == "HTML" else "download_controlled_publication_csv"
        )
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, operation, disclosure_id, hidden=True)
            disclosure = load(c, ctx, disclosure_id, "Disclosure")
            try:
                expires = datetime.fromisoformat(disclosure["payload"]["expires_at"].replace("Z", "+00:00"))
            except (KeyError, TypeError, ValueError):
                unavailable()
            recipient = next(
                (
                    item
                    for item in disclosure["payload"].get("recipients", [])
                    if item.get("membership_id") == ctx.membership_id
                ),
                None,
            )
            if (
                disclosure["lifecycle_state"] != "Published"
                or expires <= datetime.now(timezone.utc)
                or not recipient
                or (format == "CSV" and not recipient["allow_download"])
            ):
                unavailable()
            artifact = c.execute(
                "SELECT * FROM impact.report_publication_artifact "
                "WHERE tenant_id=%s AND disclosure_id=%s AND disclosure_revision=%s AND format=%s",
                (
                    ctx.tenant_id,
                    disclosure_id,
                    disclosure["head_revision"],
                    format,
                ),
            ).fetchone()
            if not artifact:
                unavailable()
            c.execute(
                "INSERT INTO impact.report_publication_access VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    ctx.tenant_id,
                    str(uuid4()),
                    disclosure_id,
                    ctx.principal_id,
                    ctx.membership_id,
                    format,
                    "VIEW" if format == "HTML" else "DOWNLOAD",
                    datetime.now(timezone.utc),
                    correlation,
                ),
            )
            return {
                "body": bytes(artifact["body"]),
                "media_type": artifact["media_type"],
                "digest": bytes(artifact["content_sha256"]).hex(),
                "filename": "impact-report-"
                + str(artifact["report_id"])[:8]
                + (".html" if format == "HTML" else ".csv"),
            }
