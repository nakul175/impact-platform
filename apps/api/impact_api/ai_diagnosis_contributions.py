"""Scoped, immutable proposals merged into one existing diagnosis by a lead."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from psycopg.types.json import Jsonb

from .ai_diagnoses import KIND, validate_diagnosis
from .domain import DomainError
from .store import audit, authorize, context, hash_data, load, write

ROLES = {
    "PROBLEM_OWNER": {"PROBLEM_DESCRIPTION", "AFFECTED_AREA"},
    "EVIDENCE_CONTRIBUTOR": {"SUPPORTING_EVIDENCE"},
    "PRIORITISATION_CONTRIBUTOR": {"PRIORITY_ORDER"},
}
FIELD_SECTION = {
    "description": "PROBLEM_DESCRIPTION",
    "affected_area": "AFFECTED_AREA",
    "supporting_evidence": "SUPPORTING_EVIDENCE",
    "evidence_references": "SUPPORTING_EVIDENCE",
}


def _invalid(reason="DIAGNOSIS_CONTRIBUTION_INVALID"):
    raise DomainError("VALIDATION_FAILED", reason=reason)


def _uuid(value):
    if not isinstance(value, str):
        _invalid()
    try:
        canonical = str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        _invalid()
    if canonical != value:
        _invalid()
    return canonical


def _operation(c, ctx, operation, body, fingerprint, now):
    row = c.execute(
        "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s "
        "AND command_type=%s AND operation_id=%s",
        (ctx.tenant_id, ctx.principal_id, operation, body["operation_id"]),
    ).fetchone()
    if not row:
        return None
    if bytes(row["payload_hash"]) != fingerprint:
        raise DomainError("CONFLICT_OPERATION", 409)
    if row["expires_at"] <= now:
        raise DomainError("IDEMPOTENCY_EXPIRED", 409)
    return row["outcome"]


def _record_operation(c, ctx, operation, body, fingerprint, outcome, now):
    c.execute(
        "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
        (
            ctx.tenant_id,
            ctx.principal_id,
            operation,
            body["operation_id"],
            fingerprint,
            Jsonb(outcome),
            now + timedelta(days=7),
        ),
    )


def _delivery_state(invitation, delivery):
    now = datetime.now(timezone.utc)
    if invitation["revoked_at"]:
        return "REVOKED"
    if invitation["consumed_at"]:
        return "ACCEPTED"
    if invitation["expires_at"] <= now:
        return "EXPIRED"
    if delivery and delivery["state"] == "SENT":
        return "DELIVERED"
    if delivery and delivery["state"] == "DEAD":
        return "FAILED"
    return "QUEUED"


def _assignment_result(row):
    return {
        "assignment_id": str(row["assignment_id"]),
        "diagnosis_id": str(row["diagnosis_id"]),
        "diagnosis_revision": str(row["diagnosis_revision"]),
        "member_invitation_id": str(row["member_invitation_id"]),
        "contribution_role": row["contribution_role"],
        "problem_ids": [str(value) for value in row["problem_ids"]],
        "sections": list(row["sections"]),
        "delivery_state": _delivery_state(row, row.get("delivery")),
        "created_at": row["created_at"].isoformat(),
    }


def _contribution_result(row):
    return {
        "contribution_id": str(row["contribution_id"]),
        "assignment_id": str(row["assignment_id"]),
        "diagnosis_id": str(row["diagnosis_id"]),
        "base_revision": str(row["base_revision"]),
        "contribution_role": row["contribution_role"],
        "patch": row["patch"],
        "submitted_at": row["submitted_at"].isoformat(),
        "decision": row.get("decision") or "PENDING",
    }


class AIDiagnosisContributions:
    def __init__(self, service, diagnoses):
        self.service, self.diagnoses = service, diagnoses

    @staticmethod
    def _invitation_rows(c, tenant, diagnosis_id):
        return c.execute(
            "SELECT a.*,i.consumed_at,i.revoked_at,i.expires_at,"
            "(SELECT jsonb_build_object('state',d.state) FROM impact.outbox_delivery d "
            "JOIN impact.outbox_event e ON e.tenant_id=d.tenant_id AND e.event_id=d.event_id "
            "WHERE d.tenant_id=a.tenant_id AND d.reference_id=a.member_invitation_id "
            "ORDER BY e.occurred_at DESC LIMIT 1) AS delivery "
            "FROM impact.ai_diagnosis_contributor_assignment a "
            "JOIN impact.member_invitation i ON i.tenant_id=a.tenant_id "
            "AND i.invitation_id=a.member_invitation_id "
            "WHERE a.tenant_id=%s AND a.diagnosis_id=%s ORDER BY a.created_at,a.assignment_id",
            (tenant, diagnosis_id),
        ).fetchall()

    def list_invitations(self, identity, tenant, diagnosis_id):
        _uuid(diagnosis_id)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_ai_diagnosis_contributor_invitations", hidden=True)
            diagnosis = load(c, ctx, diagnosis_id, KIND, "ai.diagnosis.read")
            self.diagnoses.check_evidence(c, identity, tenant, diagnosis["payload"])
            return {
                "items": [_assignment_result(row) for row in self._invitation_rows(c, tenant, diagnosis_id)]
            }

    def list_contributions(self, identity, tenant, diagnosis_id):
        _uuid(diagnosis_id)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_ai_diagnosis_contributions", hidden=True)
            diagnosis = load(c, ctx, diagnosis_id, KIND, "ai.diagnosis.read")
            self.diagnoses.check_evidence(c, identity, tenant, diagnosis["payload"])
            rows = c.execute(
                "SELECT x.*,a.contribution_role,d.decision FROM impact.ai_diagnosis_contribution x "
                "JOIN impact.ai_diagnosis_contributor_assignment a ON a.tenant_id=x.tenant_id "
                "AND a.assignment_id=x.assignment_id LEFT JOIN impact.ai_diagnosis_contribution_decision d "
                "ON d.tenant_id=x.tenant_id AND d.contribution_id=x.contribution_id "
                "WHERE x.tenant_id=%s AND x.diagnosis_id=%s ORDER BY x.submitted_at,x.contribution_id",
                (tenant, diagnosis_id),
            ).fetchall()
            return {"items": [_contribution_result(row) for row in rows]}

    def create_invitation(self, identity, tenant, diagnosis_id, body, correlation):
        required = {
            "operation_id",
            "expected_diagnosis_revision",
            "member_invitation_id",
            "contribution_role",
            "problem_ids",
            "sections",
        }
        if not isinstance(body, dict) or set(body) != required:
            _invalid()
        for field in ("operation_id", "expected_diagnosis_revision", "member_invitation_id"):
            _uuid(body[field])
        role = body["contribution_role"]
        sections = body["sections"]
        problems = body["problem_ids"]
        if (
            role not in ROLES
            or not isinstance(sections, list)
            or not sections
            or len(set(sections)) != len(sections)
            or set(sections) - ROLES[role]
        ):
            _invalid("DIAGNOSIS_CONTRIBUTION_SCOPE_INVALID")
        if (
            not isinstance(problems, list)
            or not 1 <= len(problems) <= 20
            or len(set(problems)) != len(problems)
        ):
            _invalid()
        for value in problems:
            _uuid(value)
        operation = "create_ai_diagnosis_contributor_invitation"
        fingerprint = hash_data([operation, diagnosis_id, body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, operation, hidden=True)
            authorize(c, ctx, "get_ai_diagnosis", hidden=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            now = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            old = _operation(c, ctx, operation, body, fingerprint, now)
            if old:
                load(c, ctx, diagnosis_id, KIND, "ai.diagnosis.read", lock=True)
                return old
            diagnosis = load(c, ctx, diagnosis_id, KIND, "ai.diagnosis.read", lock=True)
            if str(diagnosis["head_revision"]) != body["expected_diagnosis_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if diagnosis["lifecycle_state"] != "Draft":
                raise DomainError("STATE_TRANSITION_DENIED", 409, reason="DIAGNOSIS_NOT_DRAFT")
            self.diagnoses.check_evidence(c, identity, tenant, diagnosis["payload"])
            valid_problems = {item["problem_id"] for item in diagnosis["payload"]["problems"]}
            if set(problems) - valid_problems:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            invitation = c.execute(
                "SELECT * FROM impact.member_invitation WHERE tenant_id=%s AND invitation_id=%s",
                (tenant, body["member_invitation_id"]),
            ).fetchone()
            if not invitation or invitation["revoked_at"] or invitation["expires_at"] <= now:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            assignment = str(uuid4())
            c.execute(
                "INSERT INTO impact.ai_diagnosis_contributor_assignment "
                "(tenant_id,assignment_id,diagnosis_id,diagnosis_revision,member_invitation_id,"
                "contribution_role,problem_ids,sections,inviter_id,created_at) "
                "VALUES(%s,%s,%s,%s,%s,%s,%s::uuid[],%s::text[],%s,%s)",
                (
                    tenant,
                    assignment,
                    diagnosis_id,
                    diagnosis["head_revision"],
                    body["member_invitation_id"],
                    role,
                    problems,
                    sections,
                    ctx.principal_id,
                    now,
                ),
            )
            result = _assignment_result(
                {
                    "assignment_id": assignment,
                    "diagnosis_id": diagnosis_id,
                    "diagnosis_revision": diagnosis["head_revision"],
                    "member_invitation_id": body["member_invitation_id"],
                    "contribution_role": role,
                    "problem_ids": problems,
                    "sections": sections,
                    "created_at": now,
                    **invitation,
                    "delivery": None,
                }
            )
            audit(
                c,
                ctx,
                operation,
                {
                    "object_id": diagnosis_id,
                    "revision_id": str(diagnosis["head_revision"]),
                    "business_state": "Draft",
                    "saved_at": now.isoformat(),
                },
                correlation,
            )
            _record_operation(c, ctx, operation, body, fingerprint, result, now)
            return result

    @staticmethod
    def _validate_patch(patch, assignment, diagnosis):
        if not isinstance(patch, dict) or set(patch) != {"problem_updates", "priority_order"}:
            _invalid()
        updates, order = patch["problem_updates"], patch["priority_order"]
        if not isinstance(updates, list) or len(updates) > 20:
            _invalid()
        allowed_problems = {str(value) for value in assignment["problem_ids"]}
        sections = set(assignment["sections"])
        seen = set()
        for update in updates:
            if not isinstance(update, dict) or set(update) != {"problem_id", "fields"}:
                _invalid()
            problem_id = _uuid(update["problem_id"])
            fields = update["fields"]
            if (
                problem_id not in allowed_problems
                or problem_id in seen
                or not isinstance(fields, dict)
                or not fields
            ):
                _invalid("DIAGNOSIS_CONTRIBUTION_SCOPE_INVALID")
            if set(fields) - set(FIELD_SECTION) or any(
                FIELD_SECTION[field] not in sections for field in fields
            ):
                _invalid("DIAGNOSIS_CONTRIBUTION_SCOPE_INVALID")
            seen.add(problem_id)
        if order is not None:
            if (
                "PRIORITY_ORDER" not in sections
                or not isinstance(order, list)
                or len(set(order)) != len(order)
            ):
                _invalid("DIAGNOSIS_CONTRIBUTION_SCOPE_INVALID")
            if set(order) != {item["problem_id"] for item in diagnosis["problems"]}:
                _invalid("DIAGNOSIS_CONTRIBUTION_SCOPE_INVALID")
        if not updates and order is None:
            _invalid()

    def submit(self, identity, tenant, diagnosis_id, body, correlation):
        required = {"operation_id", "assignment_id", "expected_diagnosis_revision", "patch"}
        if not isinstance(body, dict) or set(body) != required:
            _invalid()
        for field in ("operation_id", "assignment_id", "expected_diagnosis_revision"):
            _uuid(body[field])
        operation = "submit_ai_diagnosis_contribution"
        fingerprint = hash_data([operation, diagnosis_id, body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, operation, hidden=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            now = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            old = _operation(c, ctx, operation, body, fingerprint, now)
            if old:
                load(c, ctx, diagnosis_id, KIND, "ai.diagnosis.read", lock=True)
                return old
            diagnosis = load(c, ctx, diagnosis_id, KIND, "ai.diagnosis.read", lock=True)
            if str(diagnosis["head_revision"]) != body["expected_diagnosis_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if diagnosis["lifecycle_state"] != "Draft":
                raise DomainError("STATE_TRANSITION_DENIED", 409, reason="DIAGNOSIS_NOT_DRAFT")
            assignment = c.execute(
                "SELECT a.*,i.accepted_membership_id,i.consumed_at,i.revoked_at,i.expires_at "
                "FROM impact.ai_diagnosis_contributor_assignment a JOIN impact.member_invitation i "
                "ON i.tenant_id=a.tenant_id AND i.invitation_id=a.member_invitation_id "
                "WHERE a.tenant_id=%s AND a.assignment_id=%s AND a.diagnosis_id=%s",
                (tenant, body["assignment_id"], diagnosis_id),
            ).fetchone()
            if (
                not assignment
                or not assignment["consumed_at"]
                or assignment["revoked_at"]
                or str(assignment["accepted_membership_id"]) != ctx.membership_id
            ):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            self._validate_patch(body["patch"], assignment, diagnosis["payload"])
            proposed = deepcopy(diagnosis["payload"])
            self._apply_patch(proposed, body["patch"])
            validate_diagnosis({key: proposed[key] for key in ("title", "problems", "priority_order")})
            self.diagnoses.check_evidence(c, identity, tenant, proposed)
            contribution_id = str(uuid4())
            c.execute(
                "INSERT INTO impact.ai_diagnosis_contribution "
                "(tenant_id,contribution_id,assignment_id,diagnosis_id,base_revision,"
                "contributor_principal_id,contributor_membership_id,patch,submitted_at) "
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    tenant,
                    contribution_id,
                    body["assignment_id"],
                    diagnosis_id,
                    diagnosis["head_revision"],
                    ctx.principal_id,
                    ctx.membership_id,
                    Jsonb(body["patch"]),
                    now,
                ),
            )
            result = _contribution_result(
                {
                    "contribution_id": contribution_id,
                    "assignment_id": body["assignment_id"],
                    "diagnosis_id": diagnosis_id,
                    "base_revision": diagnosis["head_revision"],
                    "contribution_role": assignment["contribution_role"],
                    "patch": body["patch"],
                    "submitted_at": now,
                    "decision": None,
                }
            )
            audit(
                c,
                ctx,
                operation,
                {
                    "object_id": diagnosis_id,
                    "revision_id": str(diagnosis["head_revision"]),
                    "business_state": "Draft",
                    "saved_at": now.isoformat(),
                },
                correlation,
            )
            _record_operation(c, ctx, operation, body, fingerprint, result, now)
            return result

    @staticmethod
    def _apply_patch(payload, patch):
        by_id = {item["problem_id"]: item for item in payload["problems"]}
        for update in patch["problem_updates"]:
            by_id[update["problem_id"]].update(deepcopy(update["fields"]))
        if patch["priority_order"] is not None:
            payload["priority_order"] = list(patch["priority_order"])

    def decide(self, identity, tenant, diagnosis_id, contribution_id, body, correlation, decision):
        required = {"operation_id", "expected_diagnosis_revision"} | (
            {"reason"} if decision == "REJECTED" else set()
        )
        if not isinstance(body, dict) or set(body) != required:
            _invalid()
        for field in ("operation_id", "expected_diagnosis_revision"):
            _uuid(body[field])
        _uuid(contribution_id)
        if decision == "REJECTED" and (
            not isinstance(body["reason"], str) or not body["reason"].strip() or len(body["reason"]) > 1000
        ):
            _invalid()
        operation = ("accept" if decision == "ACCEPTED" else "reject") + "_ai_diagnosis_contribution"
        fingerprint = hash_data([operation, diagnosis_id, contribution_id, body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, operation, hidden=True)
            authorize(c, ctx, "get_ai_diagnosis", hidden=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            now = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            old = _operation(c, ctx, operation, body, fingerprint, now)
            if old:
                load(c, ctx, diagnosis_id, KIND, "ai.diagnosis.read", lock=True)
                return old
            diagnosis = load(c, ctx, diagnosis_id, KIND, "ai.diagnosis.read", lock=True)
            if str(diagnosis["head_revision"]) != body["expected_diagnosis_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if diagnosis["lifecycle_state"] != "Draft":
                raise DomainError("STATE_TRANSITION_DENIED", 409, reason="DIAGNOSIS_NOT_DRAFT")
            row = c.execute(
                "SELECT x.*,a.contribution_role,a.problem_ids,a.sections FROM impact.ai_diagnosis_contribution x "
                "JOIN impact.ai_diagnosis_contributor_assignment a ON a.tenant_id=x.tenant_id "
                "AND a.assignment_id=x.assignment_id LEFT JOIN impact.ai_diagnosis_contribution_decision d "
                "ON d.tenant_id=x.tenant_id AND d.contribution_id=x.contribution_id "
                "WHERE x.tenant_id=%s AND x.contribution_id=%s AND x.diagnosis_id=%s AND d.contribution_id IS NULL",
                (tenant, contribution_id, diagnosis_id),
            ).fetchone()
            if not row or str(row["base_revision"]) != body["expected_diagnosis_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            after = diagnosis["head_revision"]
            if decision == "ACCEPTED":
                self._validate_patch(row["patch"], row, diagnosis["payload"])
                payload = deepcopy(diagnosis["payload"])
                self._apply_patch(payload, row["patch"])
                validate_diagnosis({key: payload[key] for key in ("title", "problems", "priority_order")})
                self.diagnoses.check_evidence(c, identity, tenant, payload)
                receipt = write(c, ctx, KIND, payload, "Draft", diagnosis)
                after = receipt["revision_id"]
            c.execute(
                "INSERT INTO impact.ai_diagnosis_contribution_decision "
                "(tenant_id,contribution_id,decision,reason,diagnosis_id,diagnosis_before_revision,"
                "diagnosis_after_revision,decided_by,decided_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    tenant,
                    contribution_id,
                    decision,
                    body.get("reason"),
                    diagnosis_id,
                    diagnosis["head_revision"],
                    after,
                    ctx.principal_id,
                    now,
                ),
            )
            result = {
                "operation_id": body["operation_id"],
                "contribution_id": contribution_id,
                "decision": decision,
                "diagnosis_id": diagnosis_id,
                "diagnosis_revision": str(after),
                "saved_at": now.isoformat(),
            }
            audit(
                c,
                ctx,
                operation,
                {
                    "object_id": diagnosis_id,
                    "revision_id": str(after),
                    "business_state": "Draft",
                    "saved_at": now.isoformat(),
                },
                correlation,
            )
            _record_operation(c, ctx, operation, body, fingerprint, result, now)
            return result
