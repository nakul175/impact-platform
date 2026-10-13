"""Solution-bound internal champion appointments and their pinned support guide."""

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from psycopg.types.json import Jsonb

from .ai_adoption_plans import KIND as PLAN_KIND, READ_CAP, _principal_can_manage_plan
from .domain import DomainError
from .store import audit, authorize, context, hash_data, load, write

KIND = "AIChampionAppointment"
GUIDE_ID = "internal-champion-guide"
GUIDE_VERSION = "internal-champion-guide-2026-10-12.1"
CREATE_OPERATION = "appoint_ai_internal_champion"
LIST_OPERATION = "list_ai_champion_appointments"
GUIDE_OPERATION = "get_ai_champion_guide"
GUIDE = {
    "guide_id": GUIDE_ID,
    "version": GUIDE_VERSION,
    "title": "Internal champion guide",
    "sections": [
        {
            "key": "protect-the-boundary",
            "title": "Protect the agreed use and data boundary",
            "body": "Keep the solution inside the recorded workflow, access and data boundary. Escalate proposed changes to the support owner before use changes.",
        },
        {
            "key": "support-colleagues",
            "title": "Support colleagues without becoming an approver",
            "body": "Help colleagues follow the documented workflow and training. Champion status does not grant approval, administration or access authority.",
        },
        {
            "key": "use-check-ins",
            "title": "Use scheduled check-ins",
            "body": "Bring adoption barriers, unsafe workarounds and unresolved questions to each recorded check-in with the accountable support owner.",
        },
    ],
}


def _invalid(reason="CHAMPION_APPOINTMENT_INVALID"):
    raise DomainError("VALIDATION_FAILED", reason=reason)


def _uuid(value):
    try:
        return str(UUID(value))
    except (TypeError, ValueError, AttributeError):
        _invalid()


def _member(c, tenant, membership_id):
    row = c.execute(
        "SELECT m.object_id AS membership_id,p.principal_id,"
        "impact.member_natural_identity(m.tenant_id,p.principal_id) AS natural_id "
        "FROM impact.membership_current m JOIN impact.object_registry h "
        "ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id "
        "JOIN impact.object_revision v ON v.tenant_id=h.tenant_id AND v.revision_id=h.head_revision "
        "JOIN impact.tenant_principal p ON p.tenant_id=m.tenant_id AND p.identity_id=m.identity_id "
        "WHERE m.tenant_id=%s AND m.object_id=%s AND p.active "
        "AND h.lifecycle_state='Active' AND h.classification<>'RESTRICTED' "
        "AND v.restriction_state='AVAILABLE' AND (m.status IS NULL OR m.status='Active') "
        "AND (m.expires_at IS NULL OR m.expires_at>now())",
        (tenant, membership_id),
    ).fetchone()
    if not row or not row["natural_id"]:
        raise DomainError("RESOURCE_UNAVAILABLE", 404)
    return row


def _can(c, tenant, principal_id, membership_id, capability, plan_id):
    return bool(
        c.execute(
            "SELECT 1 FROM (SELECT g.scope_id,s.scope_type,g.purpose FROM impact.grant_current g "
            "JOIN impact.object_registry h ON h.tenant_id=g.tenant_id AND h.object_id=g.object_id "
            "JOIN impact.scope_definition s ON s.tenant_id=g.tenant_id AND s.scope_id=g.scope_id "
            "WHERE g.tenant_id=%s AND g.subject_id=%s AND g.capability=%s "
            "AND h.lifecycle_state='Active' AND g.starts_at<=now() "
            "AND (g.expires_at IS NULL OR g.expires_at>now()) UNION ALL "
            "SELECT e.scope_id,s.scope_type,NULL FROM impact.group_entitlement e "
            "JOIN impact.object_registry h ON h.tenant_id=e.tenant_id AND h.object_id=e.group_id "
            "JOIN impact.scope_definition s ON s.tenant_id=e.tenant_id AND s.scope_id=e.scope_id "
            "WHERE e.tenant_id=%s AND e.membership_id=%s AND e.capability=%s "
            "AND e.expires_at>now() AND h.lifecycle_state='Active') q "
            "WHERE purpose IS NULL AND (scope_type='TENANT' OR EXISTS(SELECT 1 "
            "FROM impact.scope_member sm WHERE sm.tenant_id=%s AND sm.scope_id=q.scope_id "
            "AND sm.object_id=%s)) LIMIT 1",
            (
                tenant,
                principal_id,
                capability,
                tenant,
                membership_id,
                capability,
                tenant,
                plan_id,
            ),
        ).fetchone()
    )


def _deployment(plan):
    value = plan["payload"].get("training_deployment")
    if not value:
        raise DomainError("STATE_TRANSITION_DENIED", 409, reason="DEPLOYED_SOLUTION_REQUIRED")
    return value


def _owner(c, ctx):
    if not c.execute(
        "SELECT 1 FROM impact.tenant_custody WHERE tenant_id=%s AND owner_membership_id=%s",
        (ctx.tenant_id, ctx.membership_id),
    ).fetchone():
        raise DomainError("POLICY_DENIED", 403, reason="EXECUTIVE_OWNER_REQUIRED")


def _check_ins(value, now):
    if not isinstance(value, list) or not 1 <= len(value) <= 12:
        _invalid("CHAMPION_CHECK_INS_REQUIRED")
    parsed = []
    instants = set()
    for item in value:
        if not isinstance(item, dict) or set(item) != {"scheduled_at", "title"}:
            _invalid("CHAMPION_CHECK_IN_INVALID")
        title = item["title"]
        if not isinstance(title, str) or not title.strip() or len(title) > 150:
            _invalid("CHAMPION_CHECK_IN_INVALID")
        try:
            scheduled = datetime.fromisoformat(item["scheduled_at"].replace("Z", "+00:00"))
        except (AttributeError, TypeError, ValueError):
            _invalid("CHAMPION_CHECK_IN_INVALID")
        if scheduled.tzinfo is None:
            _invalid("CHAMPION_CHECK_IN_INVALID")
        scheduled = scheduled.astimezone(timezone.utc)
        if scheduled <= now or scheduled.isoformat() in instants:
            _invalid("CHAMPION_CHECK_IN_INVALID")
        instants.add(scheduled.isoformat())
        parsed.append(
            {
                "check_in_id": str(uuid4()),
                "scheduled_at": scheduled.isoformat(),
                "title": title.strip(),
            }
        )
    return parsed


def _result(receipt, payload):
    return {
        "object_id": str(receipt["object_id"]),
        "revision_id": str(receipt["revision_id"]),
        "business_state": "Completed",
        "appointment": payload,
    }


class AIChampionAppointments:
    def __init__(self, service):
        self.service = service

    def create(self, identity, tenant, plan_id, body, correlation):
        if not isinstance(body, dict) or set(body) != {
            "operation_id",
            "expected_plan_revision",
            "champion_membership_id",
            "support_owner_membership_id",
            "check_ins",
        }:
            _invalid()
        _uuid(body.get("operation_id"))
        _uuid(body.get("expected_plan_revision"))
        champion_membership = _uuid(body.get("champion_membership_id"))
        support_membership = _uuid(body.get("support_owner_membership_id"))
        now = datetime.now(timezone.utc)
        fingerprint = hash_data([CREATE_OPERATION, plan_id, body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, CREATE_OPERATION, plan_id, hidden=True)
            authorize(c, ctx, "get_ai_adoption_plan", plan_id, hidden=True)
            _owner(c, ctx)
            plan = load(c, ctx, plan_id, PLAN_KIND, READ_CAP, lock=True)
            deployment = _deployment(plan)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s "
                "AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, CREATE_OPERATION, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= now:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                saved = old["outcome"]["appointment"]
                champion = _member(c, tenant, saved["champion_membership_id"])
                support = _member(c, tenant, saved["support_owner_membership_id"])
                if not _can(
                    c,
                    tenant,
                    champion["principal_id"],
                    saved["champion_membership_id"],
                    READ_CAP,
                    plan_id,
                ) or not _principal_can_manage_plan(
                    c,
                    tenant,
                    support["principal_id"],
                    saved["support_owner_membership_id"],
                    plan_id,
                ):
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
                if saved["deployment_attestation_id"] != deployment["attestation_id"]:
                    raise DomainError("CONFLICT_VERSION", 409)
                visible = c.execute(
                    "SELECT 1 FROM impact.object_registry h JOIN impact.object_revision v "
                    "ON v.tenant_id=h.tenant_id AND v.revision_id=h.head_revision "
                    "WHERE h.tenant_id=%s AND h.object_id=%s AND h.object_type=%s "
                    "AND h.lifecycle_state='Completed' AND h.classification<>'RESTRICTED' "
                    "AND v.restriction_state='AVAILABLE' AND v.payload->>'deployment_attestation_id'=%s",
                    (
                        tenant,
                        old["outcome"]["object_id"],
                        KIND,
                        deployment["attestation_id"],
                    ),
                ).fetchone()
                if not visible:
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
                return old["outcome"]
            if str(plan["head_revision"]) != body["expected_plan_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            check_ins = _check_ins(body["check_ins"], now)
            champion = _member(c, tenant, champion_membership)
            support = _member(c, tenant, support_membership)
            if not _can(c, tenant, champion["principal_id"], champion_membership, READ_CAP, plan_id):
                raise DomainError("STATE_TRANSITION_DENIED", 409, reason="CHAMPION_GUIDE_ACCESS_REQUIRED")
            if not _principal_can_manage_plan(
                c, tenant, support["principal_id"], support_membership, plan_id
            ):
                raise DomainError("STATE_TRANSITION_DENIED", 409, reason="CHAMPION_SUPPORT_OWNER_REQUIRED")
            existing = c.execute(
                "SELECT 1 FROM impact.object_registry h JOIN impact.object_revision v "
                "ON v.tenant_id=h.tenant_id AND v.revision_id=h.head_revision "
                "WHERE h.tenant_id=%s AND h.object_type=%s AND h.lifecycle_state='Completed' "
                "AND h.classification<>'RESTRICTED' AND v.restriction_state='AVAILABLE' "
                "AND v.payload->>'plan_id'=%s "
                "AND v.payload->>'deployment_attestation_id'=%s "
                "AND v.payload->>'champion_membership_id'=%s LIMIT 1",
                (tenant, KIND, str(plan_id), deployment["attestation_id"], champion_membership),
            ).fetchone()
            if existing:
                raise DomainError("STATE_TRANSITION_DENIED", 409, reason="CHAMPION_ALREADY_APPOINTED")
            payload = {
                "plan_id": str(plan_id),
                "plan_revision": str(plan["head_revision"]),
                "deployment_attestation_id": deployment["attestation_id"],
                "solution_id": deployment["solution_id"],
                "role": "CHAMPION",
                "guide_id": GUIDE_ID,
                "guide_version": GUIDE_VERSION,
                "guide_hash": bytes(hash_data(GUIDE)).hex(),
                "champion_principal_id": str(champion["principal_id"]),
                "champion_membership_id": champion_membership,
                "support_owner_principal_id": str(support["principal_id"]),
                "support_owner_membership_id": support_membership,
                "check_ins": check_ins,
                "appointed_by": ctx.principal_id,
                "appointed_at": now.isoformat(),
                "confirmed_at": now.isoformat(),
            }
            receipt = write(c, ctx, KIND, payload, "Completed")
            outcome = _result(receipt, payload)
            audit(
                c,
                ctx,
                CREATE_OPERATION,
                {**receipt, "operation_id": body["operation_id"], "correlation_id": correlation},
                correlation,
            )
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    CREATE_OPERATION,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(outcome),
                    now + timedelta(days=7),
                ),
            )
            return outcome

    def listing(self, identity, tenant, plan_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, LIST_OPERATION, plan_id, hidden=True)
            plan = load(c, ctx, plan_id, PLAN_KIND, READ_CAP)
            deployment = _deployment(plan)
            manager = _principal_can_manage_plan(c, tenant, ctx.principal_id, ctx.membership_id, plan_id)
            rows = c.execute(
                "SELECT h.object_id,h.head_revision,v.payload FROM impact.object_registry h "
                "JOIN impact.object_revision v ON v.tenant_id=h.tenant_id AND v.revision_id=h.head_revision "
                "WHERE h.tenant_id=%s AND h.object_type=%s AND h.lifecycle_state='Completed' "
                "AND h.classification<>'RESTRICTED' AND v.restriction_state='AVAILABLE' "
                "AND v.payload->>'plan_id'=%s "
                "AND v.payload->>'deployment_attestation_id'=%s "
                "AND (%s OR v.payload->>'champion_principal_id'=%s OR v.payload->>'support_owner_principal_id'=%s) "
                "ORDER BY v.created_at,h.object_id LIMIT 101",
                (
                    tenant,
                    KIND,
                    str(plan_id),
                    deployment["attestation_id"],
                    manager,
                    ctx.principal_id,
                    ctx.principal_id,
                ),
            ).fetchall()
            if len(rows) > 100:
                raise DomainError("LIMIT_EXCEEDED", 422, reason="CHAMPION_APPOINTMENT_LIMIT")
            return {
                "items": [
                    _result({"object_id": r["object_id"], "revision_id": r["head_revision"]}, r["payload"])
                    for r in rows
                ]
            }

    def guide(self, identity, tenant, plan_id, solution_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, GUIDE_OPERATION, plan_id, hidden=True)
            plan = load(c, ctx, plan_id, PLAN_KIND, READ_CAP)
            deployment = _deployment(plan)
            if deployment["solution_id"] != solution_id:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            row = c.execute(
                "SELECT v.payload FROM impact.object_registry h JOIN impact.object_revision v "
                "ON v.tenant_id=h.tenant_id AND v.revision_id=h.head_revision "
                "WHERE h.tenant_id=%s AND h.object_type=%s AND h.lifecycle_state='Completed' "
                "AND h.classification<>'RESTRICTED' AND v.restriction_state='AVAILABLE' "
                "AND v.payload->>'plan_id'=%s "
                "AND v.payload->>'deployment_attestation_id'=%s "
                "AND v.payload->>'solution_id'=%s AND v.payload->>'champion_principal_id'=%s "
                "AND v.payload->>'champion_membership_id'=%s LIMIT 1",
                (
                    tenant,
                    KIND,
                    str(plan_id),
                    deployment["attestation_id"],
                    solution_id,
                    ctx.principal_id,
                    ctx.membership_id,
                ),
            ).fetchone()
            if not row:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            expected_hash = bytes(hash_data(GUIDE)).hex()
            if (
                row["payload"].get("guide_id") != GUIDE_ID
                or row["payload"].get("guide_version") != GUIDE_VERSION
                or row["payload"].get("guide_hash") != expected_hash
            ):
                raise DomainError("RESOURCE_UNAVAILABLE", 404, reason="CHAMPION_GUIDE_EDITION_UNAVAILABLE")
            return {
                **GUIDE,
                "plan_id": str(plan_id),
                "plan_revision": str(plan["head_revision"]),
                "solution_id": solution_id,
                "deployment_attestation_id": deployment["attestation_id"],
                "role": "CHAMPION",
            }
