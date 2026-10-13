"""Manual, tenant-scoped diagnoses; completion never means independent approval."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from uuid import UUID

from psycopg.types.json import Jsonb

from .domain import DomainError
from .store import audit, authorize, context, hash_data, load, write
from .ai_diagnosis_evidence import resolve_problem_references, validate_references

KIND = "AIDiagnosis"
ROUTE = "ai-enablement/diagnoses"
READ_CAP = "ai.diagnosis.read"
MAX_PROBLEMS = 20
DATA_FIELDS = {"title", "problems", "priority_order"}
PROBLEM_FIELDS = {"problem_id", "description", "affected_area", "supporting_evidence"}
TEXT_LIMITS = {"description": 1000, "affected_area": 150, "supporting_evidence": 4000}


def _invalid(reason="DIAGNOSIS_INVALID", fields=None):
    raise DomainError("VALIDATION_FAILED", reason=reason, fields=fields)


def _uuid(value):
    if not isinstance(value, str):
        _invalid()
    try:
        canonical = str(UUID(value))
    except (ValueError, AttributeError):
        _invalid()
    # One spelling for identity, membership, request fingerprints and duplicate detection.
    if value != canonical:
        _invalid()
    return canonical


def validate_diagnosis(data, complete=False):
    """Bounded incomplete drafts; completion reports all missing visible problem fields."""
    if not isinstance(data, dict) or set(data) != DATA_FIELDS:
        _invalid()
    title = data["title"]
    if not isinstance(title, str) or not title.strip() or len(title) > 150:
        _invalid()
    problems, order = data["problems"], data["priority_order"]
    if not isinstance(problems, list) or len(problems) > MAX_PROBLEMS:
        _invalid()
    if not isinstance(order, list) or len(order) > MAX_PROBLEMS:
        _invalid()
    ids = []
    for problem in problems:
        if (
            not isinstance(problem, dict)
            or not PROBLEM_FIELDS <= set(problem)
            or set(problem) - PROBLEM_FIELDS - {"evidence_references"}
        ):
            _invalid()
        if "evidence_references" in problem:
            validate_references(problem["evidence_references"])
        ids.append(_uuid(problem["problem_id"]))
        for field, maximum in TEXT_LIMITS.items():
            value = problem[field]
            if not isinstance(value, str) or len(value) > maximum:
                _invalid()
    priorities = [_uuid(value) for value in order]
    if len(set(ids)) != len(ids) or len(set(priorities)) != len(priorities):
        _invalid("DIAGNOSIS_DUPLICATE_PROBLEM")
    if set(priorities) - set(ids):
        _invalid("DIAGNOSIS_UNKNOWN_PRIORITY")
    if not complete:
        return
    fields = []
    if not problems:
        fields.append({"path": "problems", "message": "Add at least one problem."})
    for problem in problems:
        missing = [field for field in TEXT_LIMITS if not problem[field].strip()]
        if problem["problem_id"] not in priorities:
            missing.append("priority")
        name = problem["description"].strip()[:150] or problem["problem_id"]
        for field in missing:
            fields.append(
                {
                    "path": "problems." + problem["problem_id"] + "." + field,
                    "message": "Problem " + name + ": " + field.replace("_", " ") + " is required.",
                }
            )
    if fields:
        _invalid("DIAGNOSIS_INCOMPLETE", fields)


def _data(payload):
    return {field: deepcopy(payload[field]) for field in DATA_FIELDS}


def _result(object_id, revision_id, payload):
    data = deepcopy(payload)
    state = data.pop("diagnosis_state")
    return {
        "object_id": str(object_id),
        "revision_id": str(revision_id),
        "business_state": state,
        "data": data,
    }


class AIDiagnoses:
    def __init__(self, service):
        self.service = service

    @staticmethod
    def check_evidence(c, identity, tenant, payload):
        try:
            resolve_problem_references(c, identity, tenant, payload["problems"])
        except DomainError as error:
            if error.code != "VALIDATION_FAILED":
                raise
            raise DomainError("RESOURCE_UNAVAILABLE", 404) from None

    def visible_page(self, c, identity, tenant, rows, limit):
        page = []
        scanned = 0
        # Scan a bounded source batch and fill the requested visible page.
        # Advance past hidden rows without returning their identifiers.
        for row in rows[:100]:
            scanned += 1
            try:
                self.check_evidence(c, identity, tenant, row["payload"])
            except DomainError as error:
                if error.status != 404:
                    raise
                continue
            page.append(row)
            if len(page) == limit:
                break
        return page, scanned

    @staticmethod
    def revision(c, tenant, object_id, revision_id):
        row = c.execute(
            "SELECT payload FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s "
            "AND revision_id=%s AND object_type=%s AND restriction_state='AVAILABLE'",
            (tenant, object_id, revision_id, KIND),
        ).fetchone()
        if not row:
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
        return row["payload"]

    def get(self, identity, tenant, object_id, revision_id=None):
        _uuid(object_id)
        if revision_id is not None:
            _uuid(revision_id)
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant)
            # None deliberately requires a TENANT grant, not an object-scoped grant.
            authorize(c, ctx, "get_ai_diagnosis", hidden=True)
            current = load(c, ctx, object_id, KIND, READ_CAP)
            self.check_evidence(c, identity, tenant, current["payload"])
            if revision_id is None:
                return _result(object_id, current["head_revision"], current["payload"])
            authorize(c, ctx, "get_ai_diagnosis_revision", hidden=True)
            payload = self.revision(c, tenant, object_id, revision_id)
            self.check_evidence(c, identity, tenant, payload)
            return _result(object_id, revision_id, payload)

    def listing(self, identity, tenant, limit=50, cursor=None):
        if type(limit) is not int or not 1 <= limit <= 100:
            _invalid()
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_ai_diagnoses", hidden=True)
            bound = self.service.cursor_binding(ctx, ROUTE)
            key = self.service.cursor_key(bound, cursor)
            if key is not None:
                if not isinstance(key, list) or len(key) != 1:
                    raise DomainError("INVALID_CURSOR", 400)
                try:
                    after = str(UUID(key[0]))
                except (TypeError, ValueError, AttributeError):
                    raise DomainError("INVALID_CURSOR", 400) from None
            query = (
                "SELECT r.object_id,r.head_revision,v.payload FROM impact.object_registry r "
                "JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.object_id=r.object_id "
                "AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_type=%s "
                "AND r.classification<>'RESTRICTED' AND v.restriction_state='AVAILABLE'"
            )
            params = [tenant, KIND]
            if key is not None:
                query += " AND r.object_id>%s::uuid"
                params.append(after)
            query += " ORDER BY r.object_id LIMIT %s"
            params.append(101)
            rows = c.execute(query, params).fetchall()
            page, scanned = self.visible_page(c, identity, tenant, rows, limit)
            return {
                "items": [_result(row["object_id"], row["head_revision"], row["payload"]) for row in page],
                "next_cursor": self.service.next_cursor(bound, [str(rows[scanned - 1]["object_id"])])
                if len(rows) > scanned
                else None,
            }

    def history(self, identity, tenant, object_id, limit=50, cursor=None):
        _uuid(object_id)
        if type(limit) is not int or not 1 <= limit <= 100:
            _invalid()
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_ai_diagnosis_revisions", hidden=True)
            current = load(c, ctx, object_id, KIND, READ_CAP)
            self.check_evidence(c, identity, tenant, current["payload"])
            bound = self.service.cursor_binding(ctx, ROUTE + "/" + object_id + "/revisions")
            key = self.service.cursor_key(bound, cursor)
            if key is not None and (
                not isinstance(key, list) or len(key) != 1 or type(key[0]) is not int or key[0] < 1
            ):
                raise DomainError("INVALID_CURSOR", 400)
            query = (
                "SELECT revision_id,revision_number,created_at,payload,payload->>'title' AS title,"
                "payload->>'diagnosis_state' AS business_state FROM impact.object_revision "
                "WHERE tenant_id=%s AND object_id=%s AND object_type=%s AND restriction_state='AVAILABLE'"
            )
            params = [tenant, object_id, KIND]
            if key is not None:
                query += " AND revision_number<%s"
                params.append(key[0])
            query += " ORDER BY revision_number DESC LIMIT %s"
            params.append(101)
            rows = c.execute(query, params).fetchall()
            page, scanned = self.visible_page(c, identity, tenant, rows, limit)
            return {
                "object_id": object_id,
                "items": [
                    {
                        "revision_id": str(row["revision_id"]),
                        "revision_number": row["revision_number"],
                        "saved_at": row["created_at"].isoformat(),
                        "business_state": row["business_state"],
                        "title": row["title"],
                    }
                    for row in page
                ],
                "next_cursor": self.service.next_cursor(bound, [rows[scanned - 1]["revision_number"]])
                if len(rows) > scanned
                else None,
            }

    def command(self, identity, tenant, body, correlation, object_id=None, action=None):
        if action not in (None, "complete", "revise") or (action and not object_id):
            _invalid()
        required = {"operation_id"}
        if object_id is not None:
            _uuid(object_id)
            required.add("expected_revision")
        if action is None:
            required.add("data")
        elif action == "revise":
            required.add("reason")
        if not isinstance(body, dict) or set(body) != required:
            _invalid()
        _uuid(body["operation_id"])
        if object_id is not None:
            _uuid(body["expected_revision"])
        operation = (
            action + "_ai_diagnosis"
            if action
            else "update_ai_diagnosis"
            if object_id is not None
            else "create_ai_diagnosis"
        )
        fingerprint = hash_data([operation, object_id, body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, operation, hidden=True)
            authorize(c, ctx, "get_ai_diagnosis", hidden=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            now = datetime.now(timezone.utc)
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s "
                "AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, operation, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= now:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                replay_current = load(c, ctx, old["outcome"]["object_id"], KIND, READ_CAP)
                self.check_evidence(c, identity, tenant, replay_current["payload"])
                replay_payload = self.revision(
                    c, tenant, old["outcome"]["object_id"], old["outcome"]["revision_id"]
                )
                self.check_evidence(c, identity, tenant, replay_payload)
                return old["outcome"]
            previous = load(c, ctx, object_id, KIND, READ_CAP, lock=True) if object_id else None
            if previous:
                self.check_evidence(c, identity, tenant, previous["payload"])
            if previous and str(previous["head_revision"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if action is None:
                if previous and previous["lifecycle_state"] != "Draft":
                    raise DomainError("STATE_TRANSITION_DENIED", 409)
                validate_diagnosis(body["data"])
                if previous is None:
                    count = c.execute(
                        "SELECT count(*) AS n FROM impact.object_registry WHERE tenant_id=%s AND object_type=%s",
                        (tenant, KIND),
                    ).fetchone()["n"]
                    if count >= 1000:
                        raise DomainError("LIMIT_EXCEEDED", 429, reason="DIAGNOSIS_LIMIT")
                payload = {**deepcopy(body["data"]), "diagnosis_state": "Draft"}
                if previous and "correction_reason" in previous["payload"]:
                    payload["correction_reason"] = previous["payload"]["correction_reason"]
                state = "Draft"
            else:
                required_state = "Draft" if action == "complete" else "Completed"
                if previous["lifecycle_state"] != required_state:
                    raise DomainError("STATE_TRANSITION_DENIED", 409)
                payload = deepcopy(previous["payload"])
                if action == "complete":
                    validate_diagnosis(_data(payload), complete=True)
                    state = "Completed"
                    payload.update(
                        diagnosis_state=state,
                        completed_at=now.isoformat(),
                        completed_by=str(ctx.principal_id),
                    )
                else:
                    reason = body["reason"]
                    if not isinstance(reason, str) or not reason.strip() or len(reason) > 1000:
                        _invalid()
                    state = "Draft"
                    payload.pop("completed_at", None)
                    payload.pop("completed_by", None)
                    payload.update(diagnosis_state=state, correction_reason=reason)
            self.check_evidence(c, identity, tenant, payload)
            receipt = write(c, ctx, KIND, payload, state, previous=previous)
            receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
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
                    now + timedelta(days=7),
                ),
            )
            return receipt
