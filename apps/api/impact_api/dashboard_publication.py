"""FR-ANA-008 pinned dashboard publication and recipient-safe sharing preview."""

from datetime import datetime, timedelta, timezone

from psycopg.types.json import Jsonb

from .dashboard_authoring import BINDINGS
from .domain import DomainError
from .independence import require_object_independence
from .store import audit, authorize, context, hash_data, load, write


def _recipient_can_read(c, tenant, principal_id, capability, object_id):
    return bool(
        c.execute(
            "SELECT 1 FROM impact.grant_current g "
            "JOIN impact.object_registry r ON r.tenant_id=g.tenant_id AND r.object_id=g.object_id "
            "JOIN impact.scope_definition s ON s.tenant_id=g.tenant_id AND s.scope_id=g.scope_id "
            "LEFT JOIN impact.grant_access_facet f ON f.tenant_id=g.tenant_id AND f.grant_id=g.object_id "
            "WHERE g.tenant_id=%s AND g.subject_id=%s AND g.capability=%s "
            "AND r.lifecycle_state='Active' AND g.starts_at<=statement_timestamp() "
            "AND (g.expires_at IS NULL OR g.expires_at>statement_timestamp()) "
            "AND (f.record_object_ids IS NULL OR %s::uuid=ANY(f.record_object_ids)) "
            "AND (s.scope_type='TENANT' OR EXISTS(SELECT 1 FROM impact.scope_member m "
            "WHERE m.tenant_id=g.tenant_id AND m.scope_id=g.scope_id AND m.object_id=%s)) LIMIT 1",
            (tenant, principal_id, capability, str(object_id), str(object_id)),
        ).fetchone()
    )


def _manifest(c, ctx, dashboard, recipient_id=None):
    widgets = []
    for widget in sorted(dashboard["payload"]["widgets"], key=lambda item: item["position"]):
        binding = widget["binding"]
        kind, capability = BINDINGS[binding["resource_type"]]
        available = False
        try:
            current = load(c, ctx, binding["object_id"], kind, capability)
            available = str(current["head_revision"]) == binding["revision_id"]
        except DomainError as error:
            if error.status != 404:
                raise
        if recipient_id:
            available = available and _recipient_can_read(
                c, ctx.tenant_id, recipient_id, capability, binding["object_id"]
            )
        registry = c.execute(
            "SELECT classification FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
            (ctx.tenant_id, binding["object_id"]),
        ).fetchone()
        widgets.append(
            {
                "widget_id": widget["widget_id"],
                "binding": binding,
                "classification": registry["classification"] if registry else None,
                "availability": "AVAILABLE" if available else "UNAVAILABLE",
            }
        )
    return widgets


class DashboardPublication:
    def __init__(self, service):
        self.service = service

    @staticmethod
    def _receipt(c, ctx, op, operation_id, fingerprint):
        old = c.execute(
            "SELECT payload_hash,outcome,expires_at FROM impact.operation_receipt "
            "WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
            (ctx.tenant_id, ctx.principal_id, op, operation_id),
        ).fetchone()
        if not old:
            return None
        if bytes(old["payload_hash"]) != fingerprint:
            raise DomainError("CONFLICT_OPERATION", 409)
        if old["expires_at"] <= datetime.now(timezone.utc):
            raise DomainError("IDEMPOTENCY_EXPIRED", 409)
        return old["outcome"]

    @staticmethod
    def _save_receipt(c, ctx, op, operation_id, fingerprint, outcome):
        c.execute(
            "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
            (
                ctx.tenant_id,
                ctx.principal_id,
                op,
                operation_id,
                fingerprint,
                Jsonb(outcome),
                datetime.now(timezone.utc) + timedelta(days=7),
            ),
        )

    def prepare_disclosure(self, identity, tenant, dashboard_id, body, correlation):
        op = "action_dashboard_disclosures_prepare"
        fingerprint = hash_data({"dashboard_id": str(dashboard_id), "body": body})
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, op, dashboard_id, hidden=True)
            old = self._receipt(c, ctx, op, body["operation_id"], fingerprint)
            if old:
                return old
            dashboard = load(c, ctx, dashboard_id, "Dashboard", "dashboards.read", lock=True)
            if str(dashboard["head_revision"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409, reason="DASHBOARD_REVISION_CHANGED")
            expected = {str(item["widget_id"]) for item in dashboard["payload"]["widgets"]}
            supplied = {str(item["widget_id"]) for item in body["data"]["widgets"]}
            if expected != supplied:
                raise DomainError("VALIDATION_FAILED", reason="DISCLOSURE_WIDGET_SET_MISMATCH")
            payload = {
                "dashboard_id": str(dashboard_id),
                "dashboard_revision": str(dashboard["head_revision"]),
                "widgets": body["data"]["widgets"],
                "status": "DRAFT",
                "reviewed_by": None,
                "reviewed_at": None,
            }
            receipt = write(c, ctx, "DashboardDisclosureArtifact", payload)
            receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
            audit(c, ctx, op, receipt, correlation)
            self._save_receipt(c, ctx, op, body["operation_id"], fingerprint, receipt)
            return receipt

    def review_disclosure(self, identity, tenant, dashboard_id, artifact_id, body, correlation):
        op = "action_dashboard_disclosures_review"
        fingerprint = hash_data(
            {"dashboard_id": str(dashboard_id), "artifact_id": str(artifact_id), "body": body}
        )
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, op, dashboard_id, hidden=True)
            old = self._receipt(c, ctx, op, body["operation_id"], fingerprint)
            if old:
                return old
            artifact = load(c, ctx, artifact_id, "DashboardDisclosureArtifact", lock=True)
            if artifact["payload"]["dashboard_id"] != str(dashboard_id):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            if str(artifact["head_revision"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409, reason="DISCLOSURE_REVISION_CHANGED")
            require_object_independence(c, ctx, artifact_id)
            if body["data"]["decision"] != "APPROVE":
                raise DomainError("VALIDATION_FAILED", reason="DISCLOSURE_APPROVAL_REQUIRED")
            payload = {
                **artifact["payload"],
                "status": "APPROVED",
                "reviewed_by": str(ctx.identity.natural_identity_id),
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
            }
            receipt = write(c, ctx, "DashboardDisclosureArtifact", payload, "Approved", previous=artifact)
            receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
            audit(c, ctx, op, receipt, correlation)
            self._save_receipt(c, ctx, op, body["operation_id"], fingerprint, receipt)
            return receipt

    def sharing_preview(self, identity, tenant, dashboard_id, recipient_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "preview_dashboards", dashboard_id, hidden=True)
            if not c.execute(
                "SELECT 1 FROM impact.tenant_principal WHERE tenant_id=%s AND principal_id=%s AND active",
                (tenant, recipient_id),
            ).fetchone():
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            dashboard = load(c, ctx, dashboard_id, "Dashboard", "dashboards.read")
            widgets = _manifest(c, ctx, dashboard, recipient_id)
            return {
                "dashboard_id": str(dashboard_id),
                "dashboard_revision": str(dashboard["head_revision"]),
                "recipient_id": str(recipient_id),
                "grants_created": False,
                "widgets": widgets,
                "unavailable_binding_count": sum(item["availability"] == "UNAVAILABLE" for item in widgets),
            }

    def publish(self, identity, tenant, dashboard_id, body, correlation):
        op = "action_dashboards_publish"
        fingerprint = hash_data({"dashboard_id": str(dashboard_id), "body": body})
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, "patch_dashboards", dashboard_id, hidden=True)
            old = c.execute(
                "SELECT payload_hash,outcome,expires_at FROM impact.operation_receipt "
                "WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, op, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= datetime.now(timezone.utc):
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                return old["outcome"]
            dashboard = load(c, ctx, dashboard_id, "Dashboard", "dashboards.read", lock=True)
            if str(dashboard["head_revision"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409, reason="DASHBOARD_REVISION_CHANGED")
            expires = datetime.fromisoformat(body["data"]["expires_at"].replace("Z", "+00:00"))
            if expires <= datetime.now(timezone.utc):
                raise DomainError("VALIDATION_FAILED", reason="PUBLICATION_EXPIRY_REQUIRED")
            manifest = _manifest(c, ctx, dashboard)
            if any(item["availability"] != "AVAILABLE" for item in manifest):
                raise DomainError("CONFLICT_VERSION", 409, reason="PUBLICATION_BINDING_REVALIDATION_REQUIRED")
            disclosure = None
            if body["data"]["audience"] == "PUBLIC":
                artifact_id = body["data"].get("disclosure_artifact_id")
                if not artifact_id:
                    raise DomainError("VALIDATION_FAILED", reason="PUBLIC_DISCLOSURE_REQUIRED")
                disclosure = load(c, ctx, artifact_id, "DashboardDisclosureArtifact", lock=True)
                if (
                    disclosure["payload"]["status"] != "APPROVED"
                    or disclosure["lifecycle_state"] != "Approved"
                    or disclosure["payload"]["dashboard_id"] != str(dashboard_id)
                    or disclosure["payload"]["dashboard_revision"] != str(dashboard["head_revision"])
                ):
                    raise DomainError("VALIDATION_FAILED", reason="PUBLIC_DISCLOSURE_NOT_APPROVED")
            payload = {
                "dashboard_id": str(dashboard_id),
                "dashboard_revision": str(dashboard["head_revision"]),
                "layout": [
                    {
                        "widget_id": item["widget_id"],
                        "position": item["position"],
                        "width": item["width"],
                    }
                    for item in dashboard["payload"]["widgets"]
                ],
                "binding_manifest": [
                    {
                        "widget_id": item["widget_id"],
                        "binding": item["binding"],
                        "classification": item["classification"],
                    }
                    for item in manifest
                ],
                "audience": body["data"]["audience"],
                "expires_at": expires.isoformat(),
                "owner_id": str(ctx.principal_id),
                "status": "ACTIVE",
                "suspension_reason": None,
                "disclosure_artifact_id": str(disclosure["object_id"]) if disclosure else None,
                "disclosure_artifact_revision": str(disclosure["head_revision"]) if disclosure else None,
            }
            receipt = write(c, ctx, "DashboardPublication", payload, state="Published")
            receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
            audit(c, ctx, op, receipt, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    op,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(receipt),
                    datetime.now(timezone.utc) + timedelta(days=7),
                ),
            )
            return receipt

    def status(self, identity, tenant, dashboard_id, publication_id, correlation):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "action_dashboard_publications_revalidate", dashboard_id, hidden=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            publication = load(c, ctx, publication_id, "DashboardPublication", lock=True)
            if publication["payload"]["dashboard_id"] != str(dashboard_id):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            status, reason = publication["payload"]["status"], None
            if datetime.fromisoformat(publication["payload"]["expires_at"]) <= datetime.now(timezone.utc):
                status, reason = "SUSPENDED", "EXPIRED"
            for item in publication["payload"]["binding_manifest"]:
                binding = item["binding"]
                registry = c.execute(
                    "SELECT head_revision,classification FROM impact.object_registry "
                    "WHERE tenant_id=%s AND object_id=%s",
                    (tenant, binding["object_id"]),
                ).fetchone()
                if (
                    not registry
                    or str(registry["head_revision"]) != binding["revision_id"]
                    or registry["classification"] != item["classification"]
                ):
                    status, reason = "SUSPENDED", "SOURCE_AUTHORITY_OR_SENSITIVITY_CHANGED"
                    break
            if status == "SUSPENDED" and publication["payload"]["status"] != "SUSPENDED":
                payload = {**publication["payload"], "status": "SUSPENDED", "suspension_reason": reason}
                receipt = write(c, ctx, "DashboardPublication", payload, "Suspended", previous=publication)
                receipt.update(correlation_id=correlation)
                audit(c, ctx, "action_dashboard_publications_suspend", receipt, correlation)
                publication = load(c, ctx, publication_id, "DashboardPublication")
            return {
                "publication_id": str(publication_id),
                "dashboard_id": str(dashboard_id),
                "dashboard_revision": publication["payload"]["dashboard_revision"],
                "audience": publication["payload"]["audience"],
                "expires_at": publication["payload"]["expires_at"],
                "status": status,
                "reason_code": reason,
            }

    def transfer_owner(self, identity, tenant, dashboard_id, publication_id, body, correlation):
        return self._change(
            identity, tenant, dashboard_id, publication_id, body, correlation, "TRANSFER_OWNER"
        )

    def revalidate(self, identity, tenant, dashboard_id, publication_id, body, correlation):
        return self._change(identity, tenant, dashboard_id, publication_id, body, correlation, "REVALIDATE")

    def resume(self, identity, tenant, dashboard_id, publication_id, body, correlation):
        return self._change(identity, tenant, dashboard_id, publication_id, body, correlation, "RESUME")

    def _change(self, identity, tenant, dashboard_id, publication_id, body, correlation, action):
        op = "action_dashboard_publications_" + action.lower()
        fingerprint = hash_data(
            {"dashboard_id": str(dashboard_id), "publication_id": str(publication_id), "body": body}
        )
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            authorize(c, ctx, op, dashboard_id, hidden=True)
            old = self._receipt(c, ctx, op, body["operation_id"], fingerprint)
            if old:
                return old
            publication = load(c, ctx, publication_id, "DashboardPublication", lock=True)
            if publication["payload"]["dashboard_id"] != str(dashboard_id):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            if str(publication["head_revision"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409, reason="PUBLICATION_REVISION_CHANGED")
            payload = dict(publication["payload"])
            state = publication["lifecycle_state"]
            if payload["owner_id"] != str(ctx.principal_id):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            if action == "TRANSFER_OWNER":
                target = body["data"]["owner_id"]
                if not c.execute(
                    "SELECT 1 FROM impact.tenant_principal WHERE tenant_id=%s AND principal_id=%s AND active",
                    (tenant, target),
                ).fetchone():
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
                if not _recipient_can_read(c, tenant, target, "dashboards.read", dashboard_id):
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
                payload["owner_id"] = target
            else:
                if datetime.fromisoformat(payload["expires_at"]) <= datetime.now(timezone.utc):
                    raise DomainError("CONFLICT_VERSION", 409, reason="PUBLICATION_EXPIRED")
                dashboard = load(c, ctx, dashboard_id, "Dashboard", "dashboards.read", lock=True)
                manifest = _manifest(c, ctx, dashboard)
                if any(item["availability"] != "AVAILABLE" for item in manifest):
                    raise DomainError(
                        "CONFLICT_VERSION", 409, reason="PUBLICATION_BINDING_REVALIDATION_REQUIRED"
                    )
                payload["dashboard_revision"] = str(dashboard["head_revision"])
                payload["binding_manifest"] = [
                    {
                        "widget_id": item["widget_id"],
                        "binding": item["binding"],
                        "classification": item["classification"],
                    }
                    for item in manifest
                ]
                if payload["audience"] == "PUBLIC":
                    disclosure = load(
                        c, ctx, payload["disclosure_artifact_id"], "DashboardDisclosureArtifact"
                    )
                    if disclosure["payload"]["status"] != "APPROVED" or disclosure["payload"][
                        "dashboard_revision"
                    ] != str(dashboard["head_revision"]):
                        raise DomainError(
                            "CONFLICT_VERSION", 409, reason="PUBLIC_DISCLOSURE_REVALIDATION_REQUIRED"
                        )
                    payload["disclosure_artifact_revision"] = str(disclosure["head_revision"])
                if action == "REVALIDATE":
                    payload["status"] = "SUSPENDED"
                    payload["suspension_reason"] = "REVALIDATED_AWAITING_RESUME"
                    state = "Suspended"
                else:
                    if (
                        publication["payload"]["status"] != "SUSPENDED"
                        or publication["payload"].get("suspension_reason") != "REVALIDATED_AWAITING_RESUME"
                    ):
                        raise DomainError("CONFLICT_VERSION", 409, reason="PUBLICATION_REVALIDATION_REQUIRED")
                    payload["status"] = "ACTIVE"
                    payload["suspension_reason"] = None
                    state = "Published"
            receipt = write(c, ctx, "DashboardPublication", payload, state, previous=publication)
            if action == "TRANSFER_OWNER":
                c.execute(
                    "UPDATE impact.object_registry SET owner_id=%s WHERE tenant_id=%s AND object_id=%s",
                    (payload["owner_id"], tenant, publication_id),
                )
            receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
            audit(c, ctx, op, receipt, correlation)
            self._save_receipt(c, ctx, op, body["operation_id"], fingerprint, receipt)
            return receipt

    def content(self, identity, tenant, dashboard_id, publication_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "read_dashboard_publication_content", dashboard_id, hidden=True)
            publication = load(c, ctx, publication_id, "DashboardPublication")
            if (
                publication["payload"]["dashboard_id"] != str(dashboard_id)
                or publication["payload"]["status"] != "ACTIVE"
            ):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            artifact_id = publication["payload"].get("disclosure_artifact_id")
            if not artifact_id:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            artifact = load(c, ctx, artifact_id, "DashboardDisclosureArtifact")
            if (
                str(artifact["head_revision"]) != publication["payload"]["disclosure_artifact_revision"]
                or artifact["payload"]["status"] != "APPROVED"
            ):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            if datetime.fromisoformat(publication["payload"]["expires_at"]) <= datetime.now(timezone.utc):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            for item in publication["payload"]["binding_manifest"]:
                binding = item["binding"]
                registry = c.execute(
                    "SELECT head_revision,classification FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
                    (tenant, binding["object_id"]),
                ).fetchone()
                if (
                    not registry
                    or str(registry["head_revision"]) != binding["revision_id"]
                    or registry["classification"] != item["classification"]
                ):
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
            return {
                "publication_id": str(publication_id),
                "dashboard_id": str(dashboard_id),
                "dashboard_revision": publication["payload"]["dashboard_revision"],
                "disclosure_artifact_id": str(artifact_id),
                "disclosure_artifact_revision": str(artifact["head_revision"]),
                "widgets": artifact["payload"]["widgets"],
            }
