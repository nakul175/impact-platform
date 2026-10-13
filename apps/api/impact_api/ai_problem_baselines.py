"""Exact self-reported baselines bound to immutable diagnosis problem identities."""

from copy import deepcopy
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from uuid import UUID

from psycopg.types.json import Jsonb

from .domain import DomainError
from .ai_diagnosis_evidence import resolve_references
from .store import audit, authorize, context, hash_data, load, write

KIND = "AIProblemBaseline"
DIAGNOSIS_KIND = "AIDiagnosis"
ROUTE = "ai-enablement/problem-baselines"
READ_CAP = "ai.problem-baseline.read"
METRICS = ("time", "cost", "quality", "reach")
DATA_FIELDS = {
    "diagnosis_id",
    "diagnosis_revision",
    "problem_id",
    "title",
    "metrics",
    "supporting_evidence",
    "evidence_references",
}
MEASURE_FIELDS = {"value", "unit", "basis", "observed_from", "observed_to"}


def _invalid(reason="PROBLEM_BASELINE_INVALID", fields=None):
    raise DomainError("VALIDATION_FAILED", reason=reason, fields=fields)


def _uuid(value):
    if not isinstance(value, str):
        _invalid()
    try:
        canonical = str(UUID(value))
    except (ValueError, AttributeError):
        _invalid()
    if canonical != value:
        _invalid()
    return canonical


def _measure(value):
    if not isinstance(value, dict) or set(value) != MEASURE_FIELDS:
        _invalid()
    number = value["value"]
    if not isinstance(number, str) or len(number) > 40:
        _invalid()
    try:
        parsed = Decimal(number)
    except InvalidOperation:
        _invalid()
    if not parsed.is_finite() or parsed.as_tuple().exponent < -12 or len(parsed.as_tuple().digits) > 38:
        _invalid()
    if not isinstance(value["unit"], str) or not value["unit"].strip() or len(value["unit"]) > 80:
        _invalid()
    if not isinstance(value["basis"], str) or not value["basis"].strip() or len(value["basis"]) > 500:
        _invalid()
    try:
        start, end = date.fromisoformat(value["observed_from"]), date.fromisoformat(value["observed_to"])
    except (TypeError, ValueError):
        _invalid()
    if end < start:
        _invalid("PROBLEM_BASELINE_PERIOD_INVALID")


def validate_baseline(data, complete=False):
    if not isinstance(data, dict) or set(data) != DATA_FIELDS:
        _invalid()
    for field in ("diagnosis_id", "diagnosis_revision", "problem_id"):
        _uuid(data[field])
    if not isinstance(data["title"], str) or not data["title"].strip() or len(data["title"]) > 150:
        _invalid()
    if not isinstance(data["supporting_evidence"], str) or len(data["supporting_evidence"]) > 4000:
        _invalid()
    refs = data["evidence_references"]
    if not isinstance(refs, list) or len(refs) > 5:
        _invalid()
    pairs = []
    for ref in refs:
        if not isinstance(ref, dict) or set(ref) != {"object_id", "revision_id"}:
            _invalid()
        pairs.append((_uuid(ref["object_id"]), _uuid(ref["revision_id"])))
    if len(set(pairs)) != len(pairs):
        _invalid("PROBLEM_BASELINE_DUPLICATE_EVIDENCE")
    metrics = data["metrics"]
    if not isinstance(metrics, dict) or set(metrics) - set(METRICS):
        _invalid()
    for value in metrics.values():
        _measure(value)
    if complete and set(metrics) != set(METRICS):
        missing = [
            {"path": "metrics." + name, "message": name.title() + " baseline is required."}
            for name in METRICS
            if name not in metrics
        ]
        _invalid("PROBLEM_BASELINE_INCOMPLETE", missing)


def _data(payload):
    return {field: deepcopy(payload[field]) for field in DATA_FIELDS}


def _result(object_id, revision_id, payload):
    data = deepcopy(payload)
    state = data.pop("baseline_state")
    return {
        "object_id": str(object_id),
        "revision_id": str(revision_id),
        "business_state": state,
        "data": data,
    }


class AIProblemBaselines:
    def __init__(self, service, diagnoses):
        self.service, self.diagnoses = service, diagnoses

    def _source(self, c, identity, tenant, data, current_required):
        ctx = context(c, identity, tenant)
        authorize(c, ctx, "get_ai_diagnosis", hidden=True)
        current = load(c, ctx, data["diagnosis_id"], DIAGNOSIS_KIND, "ai.diagnosis.read")
        if current_required and str(current["head_revision"]) != data["diagnosis_revision"]:
            raise DomainError("CONFLICT_VERSION", 409, reason="DIAGNOSIS_SOURCE_CHANGED")
        payload = self.diagnoses.revision(c, tenant, data["diagnosis_id"], data["diagnosis_revision"])
        self.diagnoses.check_evidence(c, identity, tenant, payload)
        if payload.get("diagnosis_state") != "Completed":
            raise DomainError("STATE_TRANSITION_DENIED", 409, reason="DIAGNOSIS_NOT_COMPLETE")
        problems = {
            item["problem_id"]: item
            for item in payload["problems"]
            if item["problem_id"] in payload["priority_order"]
        }
        if data["problem_id"] not in problems:
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
        try:
            resolve_references(c, identity, tenant, data["evidence_references"])
        except DomainError as error:
            if error.code == "VALIDATION_FAILED":
                raise DomainError("RESOURCE_UNAVAILABLE", 404) from None
            raise
        return problems[data["problem_id"]]

    def visible_page(self, c, identity, tenant, rows, limit):
        page = []
        scanned = 0
        # Keep pagination opaque while advancing past sources the actor can no
        # longer see. The bounded scan avoids an unbounded authority oracle.
        for row in rows[:100]:
            scanned += 1
            try:
                self._source(c, identity, tenant, row["payload"], False)
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
            authorize(c, ctx, "get_ai_problem_baseline", hidden=True)
            current = load(c, ctx, object_id, KIND, READ_CAP)
            if revision_id is None:
                payload = current["payload"]
            else:
                authorize(c, ctx, "get_ai_problem_baseline_revision", hidden=True)
                payload = self.revision(c, tenant, object_id, revision_id)
            self._source(c, identity, tenant, payload, False)
            return _result(object_id, revision_id or current["head_revision"], payload)

    def listing(self, identity, tenant, limit=50, cursor=None):
        if type(limit) is not int or not 1 <= limit <= 100:
            _invalid()
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_ai_problem_baselines", hidden=True)
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
            visible, scanned = self.visible_page(c, identity, tenant, rows, limit)
            return {
                "items": [_result(row["object_id"], row["head_revision"], row["payload"]) for row in visible],
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
            authorize(c, ctx, "list_ai_problem_baseline_revisions", hidden=True)
            current = load(c, ctx, object_id, KIND, READ_CAP)
            self._source(c, identity, tenant, current["payload"], False)
            bound = self.service.cursor_binding(ctx, ROUTE + "/" + object_id + "/revisions")
            key = self.service.cursor_key(bound, cursor)
            if key is not None and (
                not isinstance(key, list) or len(key) != 1 or type(key[0]) is not int or key[0] < 1
            ):
                raise DomainError("INVALID_CURSOR", 400)
            query = (
                "SELECT revision_id,revision_number,created_at,payload,payload->>'title' AS title,"
                "payload->>'baseline_state' AS business_state FROM impact.object_revision "
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
        if action not in (None, "lock") or (action and not object_id):
            _invalid()
        required = {"operation_id"}
        if object_id is not None:
            required.add("expected_revision")
        if action is None:
            required.add("data")
        if not isinstance(body, dict) or set(body) != required:
            _invalid()
        _uuid(body["operation_id"])
        if object_id is not None:
            _uuid(object_id)
            _uuid(body["expected_revision"])
        operation = (
            "lock_ai_problem_baseline"
            if action
            else "update_ai_problem_baseline"
            if object_id
            else "create_ai_problem_baseline"
        )
        fingerprint = hash_data([operation, object_id, body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, operation, hidden=True)
            authorize(c, ctx, "get_ai_problem_baseline", hidden=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            now = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
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
                self._source(c, identity, tenant, replay_current["payload"], False)
                replay_payload = self.revision(
                    c, tenant, old["outcome"]["object_id"], old["outcome"]["revision_id"]
                )
                self._source(c, identity, tenant, replay_payload, False)
                return old["outcome"]
            previous = load(c, ctx, object_id, KIND, READ_CAP, lock=True) if object_id else None
            if previous and str(previous["head_revision"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if previous and previous["lifecycle_state"] == "Locked":
                raise DomainError("STATE_TRANSITION_DENIED", 409, reason="PROBLEM_BASELINE_LOCKED")
            if action is None:
                validate_baseline(body["data"])
                self._source(c, identity, tenant, body["data"], True)
                if previous is None:
                    count = c.execute(
                        "SELECT count(*) AS n FROM impact.object_registry WHERE tenant_id=%s AND object_type=%s",
                        (tenant, KIND),
                    ).fetchone()["n"]
                    if count >= 5000:
                        raise DomainError("LIMIT_EXCEEDED", 429, reason="PROBLEM_BASELINE_LIMIT")
                payload = {**deepcopy(body["data"]), "baseline_state": "Draft"}
                state = "Draft"
            else:
                payload = deepcopy(previous["payload"])
                validate_baseline(_data(payload), complete=True)
                self._source(c, identity, tenant, payload, True)
                state = "Locked"
                payload.update(
                    baseline_state=state,
                    locked_at=now.isoformat(),
                    locked_by=str(ctx.principal_id),
                )
            receipt = write(c, ctx, KIND, payload, state, previous=previous)
            if action == "lock":
                c.execute(
                    "INSERT INTO impact.problem_baseline_lock "
                    "(tenant_id,object_id,revision_id,diagnosis_id,diagnosis_revision,problem_id,"
                    "locked_by,locked_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        tenant,
                        receipt["object_id"],
                        receipt["revision_id"],
                        payload["diagnosis_id"],
                        payload["diagnosis_revision"],
                        payload["problem_id"],
                        ctx.principal_id,
                        now,
                    ),
                )
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
