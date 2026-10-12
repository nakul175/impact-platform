"""Versioned value cases with an immutable locked baseline revision."""

from copy import deepcopy
from datetime import timedelta
from uuid import UUID

from psycopg.types.json import Jsonb

from .ai_value_case import calculate_value_case
from .ai_diagnosis_evidence import resolve_references
from .domain import DomainError
from .store import audit, authorize, context, hash_data, load, write

KIND = "AIValueCase"
READ_CAP = "ai.value-case.read"


def _invalid(reason="AI_VALUE_CASE_VERSION_INVALID"):
    raise DomainError("VALIDATION_FAILED", reason=reason)


def _uuid(value):
    try:
        canonical = str(UUID(value))
    except (TypeError, ValueError, AttributeError):
        _invalid()
    if canonical != value:
        _invalid()
    return canonical


def _revision(c, tenant, object_id, revision_id):
    row = c.execute(
        "SELECT payload FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s "
        "AND revision_id=%s AND object_type=%s AND restriction_state='AVAILABLE'",
        (tenant, object_id, revision_id, KIND),
    ).fetchone()
    if not row:
        raise DomainError("RESOURCE_UNAVAILABLE", 404)
    return row["payload"]


def _result(object_id, revision_id, payload):
    state = payload["version_state"]
    return {
        "object_id": str(object_id),
        "revision_id": str(revision_id),
        "business_state": state,
        "baseline_revision": str(revision_id) if state == "Locked" else payload["locked_baseline_revision"],
        "approved_at": payload["approved_at"],
        "approved_by": payload["approved_by"],
        "trial_result_reference": deepcopy(payload.get("trial_result_reference")),
        "value_case": deepcopy(payload["value_case"]),
    }


class AIValueCaseVersions:
    def __init__(self, service):
        self.service = service

    def get(self, identity, tenant, object_id, revision_id=None):
        _uuid(object_id)
        if revision_id is not None:
            _uuid(revision_id)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(
                c,
                ctx,
                "get_ai_value_case_revision" if revision_id is not None else "get_ai_value_case_version",
                hidden=True,
            )
            current = load(c, ctx, object_id, KIND, READ_CAP)
            selected = revision_id or str(current["head_revision"])
            payload = current["payload"] if revision_id is None else _revision(c, tenant, object_id, selected)
            return _result(object_id, selected, payload)

    def command(
        self, identity, tenant, body, correlation, object_id=None, action=None, trial_result_reference=None
    ):
        if action not in (None, "approve", "lock", "revise") or (action and not object_id):
            _invalid()
        required = {"operation_id"}
        if object_id is not None:
            required.add("expected_revision")
        if action in (None, "revise"):
            required.add("value_case")
        if not isinstance(body, dict) or set(body) != required:
            _invalid()
        _uuid(body["operation_id"])
        if object_id is not None:
            _uuid(object_id)
            _uuid(body["expected_revision"])
        operation = {
            None: "create_ai_value_case_version",
            "approve": "approve_ai_value_case",
            "lock": "lock_ai_value_case_baseline",
            "revise": "revise_ai_value_case",
        }[action]
        fingerprint = hash_data([operation, object_id, body, trial_result_reference])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, operation, hidden=True)
            authorize(c, ctx, "get_ai_value_case_version", hidden=True)
            if trial_result_reference and trial_result_reference.get("evidence_reference"):
                resolve_references(c, identity, tenant, [trial_result_reference["evidence_reference"]])
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            observed = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s "
                "AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, operation, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= observed:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                load(c, ctx, old["outcome"]["object_id"], KIND, READ_CAP)
                _revision(c, tenant, old["outcome"]["object_id"], old["outcome"]["revision_id"])
                return old["outcome"]
            previous = load(c, ctx, object_id, KIND, READ_CAP, lock=True) if object_id else None
            inherited_trial_reference = (
                previous["payload"].get("trial_result_reference") if previous else None
            )
            if inherited_trial_reference and inherited_trial_reference.get("evidence_reference"):
                resolve_references(c, identity, tenant, [inherited_trial_reference["evidence_reference"]])
            if previous and str(previous["head_revision"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if action is None:
                result = calculate_value_case(body["value_case"])
                payload = {
                    "version_state": "Draft",
                    "locked_baseline_revision": None,
                    "draft_author_natural_id": str(ctx.identity.natural_identity_id),
                    "approved_at": None,
                    "approved_by": None,
                    "trial_result_reference": deepcopy(trial_result_reference),
                    "value_case": result,
                }
                state = "Draft"
            elif action == "approve":
                if previous["payload"]["version_state"] != "Draft":
                    raise DomainError("STATE_TRANSITION_DENIED", 409, reason="VALUE_CASE_NOT_DRAFT")
                if previous["payload"].get("draft_author_natural_id") == str(
                    ctx.identity.natural_identity_id
                ):
                    raise DomainError("INDEPENDENCE_REQUIRED", 409, reason="VALUE_CASE_SELF_APPROVAL")
                payload = deepcopy(previous["payload"])
                payload.update(
                    version_state="Approved",
                    approved_at=observed.isoformat(),
                    approved_by=str(ctx.principal_id),
                )
                state = "Approved"
            elif action == "lock":
                if previous["payload"]["version_state"] != "Approved":
                    raise DomainError("STATE_TRANSITION_DENIED", 409, reason="VALUE_CASE_NOT_APPROVED")
                payload = deepcopy(previous["payload"])
                payload["version_state"] = "Locked"
                state = "Locked"
            else:
                if previous["payload"]["version_state"] != "Locked":
                    raise DomainError("STATE_TRANSITION_DENIED", 409, reason="VALUE_CASE_NOT_LOCKED")
                result = calculate_value_case(body["value_case"])
                if result["opportunity_id"] != previous["payload"]["value_case"]["opportunity_id"]:
                    raise DomainError("STATE_TRANSITION_DENIED", 409, reason="VALUE_CASE_OPPORTUNITY_CHANGED")
                payload = {
                    "version_state": "Draft",
                    "locked_baseline_revision": str(previous["head_revision"]),
                    "draft_author_natural_id": str(ctx.identity.natural_identity_id),
                    "approved_at": None,
                    "approved_by": None,
                    "trial_result_reference": deepcopy(
                        trial_result_reference
                        if trial_result_reference is not None
                        else previous["payload"].get("trial_result_reference")
                    ),
                    "value_case": result,
                }
                state = "Draft"
            receipt = write(
                c,
                ctx,
                KIND,
                payload,
                state,
                previous=previous,
                track_author=action not in ("approve", "lock"),
            )
            receipt.update(
                operation_id=body["operation_id"],
                correlation_id=correlation,
                baseline_revision=str(receipt["revision_id"])
                if state == "Locked"
                else payload["locked_baseline_revision"],
                approved_at=payload["approved_at"],
                approved_by=payload["approved_by"],
            )
            audit(c, ctx, operation, receipt, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    operation,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(receipt),
                    observed + timedelta(days=7),
                ),
            )
            return receipt
