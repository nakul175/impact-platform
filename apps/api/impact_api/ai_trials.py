"""US-AS-01 immutable advisor-led trials over own governed evidence or synthetic sample data."""

from datetime import date, timedelta
from uuid import uuid4
from psycopg.types.json import Jsonb
from .ai_diagnosis_evidence import resolve_references
from .ai_solution_fit_scores import AISolutionFitScores
from .contracts import validate
from .domain import DomainError
from .store import audit, authorize, context, hash_data


class AITrials:
    def __init__(self, service):
        self.service = service

    @staticmethod
    def _result(row, today=None):
        today = today or date.today()
        status = "PLANNED" if today < row["starts_on"] else "ENDED" if today >= row["ends_on"] else "ACTIVE"
        return {
            "trial_id": str(row["trial_id"]),
            "opportunity_id": row["opportunity_id"],
            "solution_id": row["solution_id"],
            "catalogue_content_version": row["catalogue_content_version"],
            "starts_on": row["starts_on"].isoformat(),
            "ends_on": row["ends_on"].isoformat(),
            "duration_days": row["duration_days"],
            "data_mode": row["data_mode"],
            "evidence_reference": (
                {
                    "object_id": str(row["evidence_object_id"]),
                    "revision_id": str(row["evidence_revision_id"]),
                }
                if row["evidence_object_id"]
                else None
            ),
            "sample_id": row["sample_id"],
            "success_criteria": row["success_criteria"],
            "advisor_membership_id": str(row["advisor_membership_id"]),
            "status": status,
            "created_at": row["created_at"].isoformat(),
        }

    def create(self, identity, tenant, body, correlation):
        validate("AITrialCreate", body)
        catalogue_version = AISolutionFitScores._catalog_match(body["opportunity_id"], body["solution_id"])
        name = "create_ai_option_trial"
        fingerprint = hash_data([name, body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, name, hidden=True)
            now = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, name, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= now:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                if body["data_mode"] == "OWN_EVIDENCE":
                    resolve_references(c, identity, tenant, [body["evidence_reference"]])
                return old["outcome"]
            advisor = c.execute(
                "SELECT impact.member_natural_identity(%s,%s) AS natural_id FROM impact.membership_current m JOIN impact.object_registry h ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id WHERE m.tenant_id=%s AND m.object_id=%s AND h.lifecycle_state='Active' AND (m.status IS NULL OR m.status='Active') AND (m.expires_at IS NULL OR m.expires_at>now())",
                (tenant, ctx.principal_id, tenant, ctx.membership_id),
            ).fetchone()
            if not advisor or not advisor["natural_id"]:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            starts_on = date.fromisoformat(body["starts_on"])
            if starts_on < now.date():
                raise DomainError("VALIDATION_FAILED", 400, reason="TRIAL_START_IN_PAST")
            evidence = body.get("evidence_reference")
            if body["data_mode"] == "OWN_EVIDENCE":
                resolve_references(c, identity, tenant, [evidence])
            trial_id = str(uuid4())
            ends_on = starts_on + timedelta(days=body["duration_days"])
            c.execute(
                "INSERT INTO impact.ai_option_trial VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    tenant,
                    trial_id,
                    body["opportunity_id"],
                    body["solution_id"],
                    catalogue_version,
                    starts_on,
                    ends_on,
                    body["duration_days"],
                    body["data_mode"],
                    evidence["object_id"] if evidence else None,
                    evidence["revision_id"] if evidence else None,
                    body.get("sample_id"),
                    body["success_criteria"].strip(),
                    ctx.principal_id,
                    ctx.membership_id,
                    advisor["natural_id"],
                    now,
                ),
            )
            row = c.execute(
                "SELECT * FROM impact.ai_option_trial WHERE tenant_id=%s AND trial_id=%s",
                (tenant, trial_id),
            ).fetchone()
            result = self._result(row, now.date())
            audit(
                c,
                ctx,
                name,
                {"object_id": trial_id, "business_state": result["status"], "saved_at": now.isoformat()},
                correlation,
            )
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    name,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(result),
                    now + timedelta(days=7),
                ),
            )
            return result

    def list(self, identity, tenant, opportunity_id):
        if not isinstance(opportunity_id, str) or not opportunity_id.strip() or len(opportunity_id) > 120:
            raise DomainError("VALIDATION_FAILED", 400)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_ai_option_trials", hidden=True)
            today = c.execute("SELECT current_date AS today").fetchone()["today"]
            rows = c.execute(
                "SELECT * FROM impact.ai_option_trial WHERE tenant_id=%s AND opportunity_id=%s ORDER BY created_at DESC,trial_id DESC LIMIT 100",
                (tenant, opportunity_id),
            ).fetchall()
            items = []
            for row in rows:
                if row["data_mode"] == "OWN_EVIDENCE":
                    try:
                        resolve_references(
                            c,
                            identity,
                            tenant,
                            [
                                {
                                    "object_id": str(row["evidence_object_id"]),
                                    "revision_id": str(row["evidence_revision_id"]),
                                }
                            ],
                        )
                    except DomainError:
                        continue
                items.append(self._result(row, today))
            return {"items": items}
