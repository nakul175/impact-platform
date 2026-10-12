"""Assigned natural-person review of immutable completed diagnosis revisions."""

from datetime import timedelta
from uuid import UUID, uuid4

from psycopg.types.json import Jsonb

from .ai_diagnoses import KIND
from .domain import DomainError
from .store import audit, authorize, context, hash_data, load


def invalid():
    raise DomainError("VALIDATION_FAILED", reason="DIAGNOSIS_REVIEW_INVALID")


def uid(value):
    try:
        result = str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        invalid()
    if result != value:
        invalid()
    return result


def operation(c, ctx, name, body, fingerprint, now):
    row = c.execute(
        "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
        (ctx.tenant_id, ctx.principal_id, name, body["operation_id"]),
    ).fetchone()
    if not row:
        return None
    if bytes(row["payload_hash"]) != fingerprint:
        raise DomainError("CONFLICT_OPERATION", 409)
    if row["expires_at"] <= now:
        raise DomainError("IDEMPOTENCY_EXPIRED", 409)
    return row["outcome"]


def save_operation(c, ctx, name, body, fingerprint, outcome, now):
    c.execute(
        "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
        (ctx.tenant_id, ctx.principal_id, name, body["operation_id"], fingerprint, Jsonb(outcome), now + timedelta(days=7)),
    )


class AIDiagnosisReviews:
    def __init__(self, service, diagnoses):
        self.service, self.diagnoses = service, diagnoses

    @staticmethod
    def advisor(c, tenant, membership):
        return c.execute(
            "SELECT m.object_id AS membership_id,p.principal_id,impact.member_natural_identity(m.tenant_id,p.principal_id) AS natural_id "
            "FROM impact.membership_current m JOIN impact.object_registry h ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id "
            "JOIN impact.tenant_principal p ON p.tenant_id=m.tenant_id AND p.identity_id=m.identity_id "
            "WHERE m.tenant_id=%s AND m.object_id=%s AND p.active AND h.lifecycle_state='Active' "
            "AND (m.status IS NULL OR m.status='Active') AND (m.expires_at IS NULL OR m.expires_at>now()) "
            "AND EXISTS(SELECT 1 FROM impact.grant_current g JOIN impact.object_registry gh ON gh.tenant_id=g.tenant_id AND gh.object_id=g.object_id "
            "JOIN impact.scope_definition s ON s.tenant_id=g.tenant_id AND s.scope_id=g.scope_id "
            "WHERE g.tenant_id=m.tenant_id AND g.subject_id=p.principal_id AND g.capability='ai.diagnosis.review' "
            "AND g.purpose IS NULL AND gh.lifecycle_state='Active' AND g.starts_at<=now() AND (g.expires_at IS NULL OR g.expires_at>now()) AND s.scope_type='TENANT')",
            (tenant, membership),
        ).fetchone()

    @staticmethod
    def rows(c, tenant, where, params):
        return c.execute(
            "SELECT r.*,o.head_revision,(SELECT jsonb_agg(jsonb_build_object('event_id',e.event_id,'kind',e.kind,'comment',e.comment,'actor_id',e.actor_principal_id,'recorded_at',e.recorded_at) ORDER BY e.recorded_at,e.event_id) FROM impact.ai_diagnosis_review_event e WHERE e.tenant_id=r.tenant_id AND e.review_id=r.review_id) AS events "
            "FROM impact.ai_diagnosis_review_request r JOIN impact.object_registry o ON o.tenant_id=r.tenant_id AND o.object_id=r.diagnosis_id "
            "WHERE r.tenant_id=%s AND " + where + " ORDER BY r.requested_at,r.review_id LIMIT 100",
            (tenant, *params),
        ).fetchall()

    @staticmethod
    def result(row):
        events = row.get("events") or []
        validated = any(item["kind"] == "VALIDATED" for item in events)
        status = "PREVIOUS_REVISION_VALIDATED" if validated and str(row["head_revision"]) != str(row["diagnosis_revision"]) else "VALIDATED" if validated else "IN_REVIEW" if events else "QUEUED"
        return {"review_id": str(row["review_id"]), "diagnosis_id": str(row["diagnosis_id"]), "diagnosis_revision": str(row["diagnosis_revision"]), "advisor_membership_id": str(row["advisor_membership_id"]), "requested_at": row["requested_at"].isoformat(), "status": status, "events": [{**item, "event_id": str(item["event_id"]), "actor_id": str(item["actor_id"]), "recorded_at": item["recorded_at"].isoformat() if hasattr(item["recorded_at"], "isoformat") else item["recorded_at"]} for item in events]}

    def request(self, identity, tenant, diagnosis_id, body, correlation):
        if not isinstance(body, dict) or set(body) != {"operation_id", "expected_diagnosis_revision", "advisor_membership_id"}:
            invalid()
        for key in body:
            uid(body[key])
        name = "request_ai_diagnosis_review"
        fingerprint = hash_data([name, diagnosis_id, body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, name, hidden=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            now = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            old = operation(c, ctx, name, body, fingerprint, now)
            if old:
                load(c, ctx, diagnosis_id, KIND, "ai.diagnosis.read", lock=True)
                return old
            diagnosis = load(c, ctx, diagnosis_id, KIND, "ai.diagnosis.read", lock=True)
            if str(diagnosis["head_revision"]) != body["expected_diagnosis_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if diagnosis["lifecycle_state"] != "Completed":
                raise DomainError("STATE_TRANSITION_DENIED", 409, reason="DIAGNOSIS_NOT_COMPLETED")
            self.diagnoses.check_evidence(c, identity, tenant, diagnosis["payload"])
            advisor = self.advisor(c, tenant, body["advisor_membership_id"])
            if not advisor or not advisor["natural_id"]:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            material = c.execute(
                "SELECT DISTINCT impact.member_natural_identity(%s,author_id) AS natural_id FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s "
                "UNION SELECT DISTINCT impact.member_natural_identity(%s,x.contributor_principal_id) FROM impact.ai_diagnosis_contribution x JOIN impact.ai_diagnosis_contribution_decision d ON d.tenant_id=x.tenant_id AND d.contribution_id=x.contribution_id WHERE x.tenant_id=%s AND x.diagnosis_id=%s AND d.decision='ACCEPTED'",
                (tenant, tenant, diagnosis_id, tenant, tenant, diagnosis_id),
            ).fetchall()
            if str(advisor["natural_id"]) in {str(row["natural_id"]) for row in material if row["natural_id"]}:
                raise DomainError("POLICY_DENIED", 403, reason="ADVISOR_INDEPENDENCE_REQUIRED")
            review_id = str(uuid4())
            c.execute(
                "INSERT INTO impact.ai_diagnosis_review_request(tenant_id,review_id,diagnosis_id,diagnosis_revision,requester_principal_id,requester_membership_id,advisor_principal_id,advisor_membership_id,advisor_natural_identity_id,requested_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (tenant, review_id, diagnosis_id, diagnosis["head_revision"], ctx.principal_id, ctx.membership_id, advisor["principal_id"], advisor["membership_id"], advisor["natural_id"], now),
            )
            row = self.rows(c, tenant, "r.review_id=%s", [review_id])[0]
            result = self.result(row)
            audit(c, ctx, name, {"object_id": diagnosis_id, "revision_id": str(diagnosis["head_revision"]), "business_state": "Completed", "saved_at": now.isoformat()}, correlation)
            save_operation(c, ctx, name, body, fingerprint, result, now)
            return result

    def list_for_diagnosis(self, identity, tenant, diagnosis_id):
        uid(diagnosis_id)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_ai_diagnosis_reviews", hidden=True)
            diagnosis = load(c, ctx, diagnosis_id, KIND, "ai.diagnosis.read")
            self.diagnoses.check_evidence(c, identity, tenant, diagnosis["payload"])
            return {"items": [self.result(row) for row in self.rows(c, tenant, "r.diagnosis_id=%s", [diagnosis_id])]}

    def queue(self, identity, tenant):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_ai_diagnosis_review_queue", hidden=True)
            rows = self.rows(c, tenant, "r.advisor_principal_id=%s", [ctx.principal_id])
            visible = []
            for row in rows:
                payload = self.diagnoses.revision(c, tenant, str(row["diagnosis_id"]), str(row["diagnosis_revision"]))
                self.diagnoses.check_evidence(c, identity, tenant, payload)
                visible.append(self.result(row))
            return {"items": visible}

    def get(self, identity, tenant, review_id):
        uid(review_id)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "get_ai_diagnosis_review", hidden=True)
            rows = self.rows(c, tenant, "r.review_id=%s AND r.advisor_principal_id=%s", [review_id, ctx.principal_id])
            if not rows:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            return self.result(rows[0])

    def act(self, identity, tenant, review_id, body, correlation, kind):
        required = {"operation_id", "expected_diagnosis_revision"} | ({"comment"} if kind == "COMMENTED" else set())
        if not isinstance(body, dict) or set(body) != required:
            invalid()
        uid(review_id); uid(body["operation_id"]); uid(body["expected_diagnosis_revision"])
        if kind == "COMMENTED" and (not isinstance(body["comment"], str) or not body["comment"].strip() or len(body["comment"]) > 4000):
            invalid()
        name = {"STARTED": "start_ai_diagnosis_review", "COMMENTED": "comment_ai_diagnosis_review", "VALIDATED": "validate_ai_diagnosis_review"}[kind]
        fingerprint = hash_data([name, review_id, body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, name, hidden=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            now = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            old = operation(c, ctx, name, body, fingerprint, now)
            rows = self.rows(c, tenant, "r.review_id=%s AND r.advisor_principal_id=%s", [review_id, ctx.principal_id])
            if not rows:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            row = rows[0]
            advisor = self.advisor(c, tenant, str(row["advisor_membership_id"]))
            if not advisor or str(advisor["principal_id"]) != str(ctx.principal_id) or str(advisor["natural_id"]) != str(row["advisor_natural_identity_id"]):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            if str(row["diagnosis_revision"]) != body["expected_diagnosis_revision"] or str(row["head_revision"]) != body["expected_diagnosis_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if old:
                return old
            existing = row.get("events") or []
            if any(item["kind"] == "VALIDATED" for item in existing):
                raise DomainError("STATE_TRANSITION_DENIED", 409)
            if kind == "VALIDATED" and not any(item["kind"] == "STARTED" for item in existing):
                raise DomainError("POLICY_DENIED", 403, reason="ADVISOR_REVIEW_REQUIRED")
            c.execute("INSERT INTO impact.ai_diagnosis_review_event VALUES(%s,%s,%s,%s,%s,%s,%s,%s)", (tenant, str(uuid4()), review_id, kind, body.get("comment"), ctx.principal_id, ctx.membership_id, row["advisor_natural_identity_id"], now))
            result = self.result(self.rows(c, tenant, "r.review_id=%s", [review_id])[0])
            audit(c, ctx, name, {"object_id": str(row["diagnosis_id"]), "revision_id": str(row["diagnosis_revision"]), "business_state": result["status"], "saved_at": now.isoformat()}, correlation)
            save_operation(c, ctx, name, body, fingerprint, result, now)
            return result
