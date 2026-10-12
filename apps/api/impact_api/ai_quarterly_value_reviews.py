"""Quarterly value reviews with a pinned template and fully tracked agreed actions."""

from copy import deepcopy
from datetime import date, timedelta
from uuid import UUID

from psycopg.types.json import Jsonb

from .domain import DomainError
from .store import audit, authorize, context, hash_data, load, write

KIND = "AIQuarterlyValueReview"
OUTCOME_KIND = "AICurrentOutcomeObservation"
TEMPLATE = {
    "edition": "quarterly-value-review-2026-10-12.1",
    "title": "Quarterly value review",
    "sections": [
        {"key": "observed-change", "title": "What changed against the locked baseline?"},
        {"key": "problems", "title": "What problems or risks need early attention?"},
        {"key": "decisions", "title": "What was agreed?"},
        {"key": "actions", "title": "Which agreed actions will be tracked?"},
    ],
}


def _invalid(reason="QUARTERLY_VALUE_REVIEW_INVALID"):
    raise DomainError("VALIDATION_FAILED", reason=reason)


def _uuid(value):
    try:
        canonical = str(UUID(value))
    except (TypeError, ValueError, AttributeError):
        _invalid()
    if canonical != value:
        _invalid()
    return canonical


def _receipt(c, ctx, operation, body, fingerprint, now):
    row = c.execute(
        "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
        (ctx.tenant_id, ctx.principal_id, operation, body["operation_id"]),
    ).fetchone()
    if not row:
        return None
    if bytes(row["payload_hash"]) != fingerprint:
        raise DomainError("CONFLICT_OPERATION", 409)
    if row["expires_at"] <= now:
        raise DomainError("IDEMPOTENCY_EXPIRED", 409)
    return row["outcome"]


def _save_receipt(c, ctx, operation, body, fingerprint, outcome, now):
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


def _result(row):
    return {
        "object_id": str(row["object_id"]),
        "revision_id": str(row["head_revision"]),
        "business_state": row["lifecycle_state"],
        "review": deepcopy(row["payload"]),
    }


class AIQuarterlyValueReviews:
    def __init__(self, service, outcomes):
        self.service, self.outcomes = service, outcomes

    def _source(self, c, identity, tenant, observation_id, revision_id):
        ctx = context(c, identity, tenant)
        observation = load(c, ctx, observation_id, OUTCOME_KIND, "ai.enablement.read")
        if str(observation["head_revision"]) != revision_id:
            raise DomainError("CONFLICT_VERSION", 409, reason="OUTCOME_OBSERVATION_CHANGED")
        payload = observation["payload"]
        self.outcomes._resolve(
            c,
            identity,
            tenant,
            {
                key: payload[key]
                for key in (
                    "plan_id",
                    "plan_revision",
                    "deployment_attestation_id",
                    "baseline_object_id",
                    "baseline_revision",
                    "opportunity_id",
                )
            },
        )
        latest = c.execute(
            "SELECT h.object_id,h.head_revision FROM impact.object_registry h JOIN impact.object_revision v ON v.tenant_id=h.tenant_id AND v.revision_id=h.head_revision WHERE h.tenant_id=%s AND h.object_type=%s AND h.lifecycle_state='Recorded' AND v.restriction_state='AVAILABLE' AND v.payload->>'plan_id'=%s AND v.payload->>'baseline_object_id'=%s AND v.payload->>'opportunity_id'=%s ORDER BY v.payload->'metrics'->'usage'->>'observed_to' DESC,v.payload->>'recorded_at' DESC,h.object_id DESC LIMIT 1",
            (
                tenant,
                OUTCOME_KIND,
                payload["plan_id"],
                payload["baseline_object_id"],
                payload["opportunity_id"],
            ),
        ).fetchone()
        if (
            not latest
            or str(latest["object_id"]) != observation_id
            or str(latest["head_revision"]) != revision_id
        ):
            if latest:
                load(c, ctx, str(latest["object_id"]), OUTCOME_KIND, "ai.enablement.read")
            raise DomainError("CONFLICT_VERSION", 409, reason="NEWER_OUTCOME_OBSERVATION_AVAILABLE")
        return payload

    @staticmethod
    def _owner(c, tenant, membership_id):
        row = c.execute(
            "SELECT m.object_id,p.principal_id FROM impact.membership_current m JOIN impact.object_registry h ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id JOIN impact.tenant_principal p ON p.tenant_id=m.tenant_id AND p.identity_id=m.identity_id WHERE m.tenant_id=%s AND m.object_id=%s AND m.external IS FALSE AND h.lifecycle_state='Active' AND p.active AND (m.status IS NULL OR m.status='Active') AND (m.expires_at IS NULL OR m.expires_at>now()) AND impact.member_natural_identity(m.tenant_id,p.principal_id) IS NOT NULL",
            (tenant, membership_id),
        ).fetchone()
        if not row:
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
        return row

    def _load_current(self, c, ctx, identity, tenant, review_id, revision_id=None):
        row = load(c, ctx, review_id, KIND, "ai.enablement.read", lock=True)
        if revision_id is not None and str(row["head_revision"]) != revision_id:
            raise DomainError("CONFLICT_VERSION", 409)
        source = row["payload"]["source"]
        self._source(
            c,
            identity,
            tenant,
            source["outcome_observation_id"],
            source["outcome_observation_revision"],
        )
        if (
            row["payload"]["advisor_principal_id"] != str(ctx.principal_id)
            or row["payload"]["advisor_membership_id"] != str(ctx.membership_id)
            or row["payload"]["advisor_natural_identity_id"] != str(ctx.identity.natural_identity_id)
        ):
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
        return row

    def start(self, identity, tenant, body, correlation):
        required = {"operation_id", "outcome_observation_id", "outcome_observation_revision"}
        if not isinstance(body, dict) or set(body) != required:
            _invalid()
        for value in body.values():
            _uuid(value)
        operation = "start_ai_quarterly_value_review"
        fingerprint = hash_data([operation, body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, operation, hidden=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            now = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            old = _receipt(c, ctx, operation, body, fingerprint, now)
            if old:
                self._load_current(c, ctx, identity, tenant, old["object_id"])
                return old
            outcome = self._source(
                c,
                identity,
                tenant,
                body["outcome_observation_id"],
                body["outcome_observation_revision"],
            )
            windows = {
                (measure["observed_from"], measure["observed_to"]) for measure in outcome["metrics"].values()
            }
            if len(windows) != 1:
                _invalid("OUTCOME_OBSERVATION_WINDOW_MISMATCH")
            period_start, period_end = next(iter(windows))
            start_date, end_date = date.fromisoformat(period_start), date.fromisoformat(period_end)
            if end_date > date.today():
                _invalid("QUARTERLY_REVIEW_NOT_DUE")
            if not 80 <= (end_date - start_date).days + 1 <= 100:
                _invalid("QUARTERLY_REVIEW_PERIOD_REQUIRED")
            duplicate = c.execute(
                "SELECT 1 FROM impact.object_registry h JOIN impact.object_revision v ON v.tenant_id=h.tenant_id AND v.revision_id=h.head_revision WHERE h.tenant_id=%s AND h.object_type=%s AND h.lifecycle_state IN ('InProgress','Completed') AND v.payload->'source'->>'outcome_observation_id'=%s AND v.payload->'source'->>'outcome_observation_revision'=%s LIMIT 1",
                (tenant, KIND, body["outcome_observation_id"], body["outcome_observation_revision"]),
            ).fetchone()
            if duplicate:
                raise DomainError("CONFLICT_VERSION", 409, reason="QUARTERLY_REVIEW_ALREADY_STARTED")
            payload = {
                "template": deepcopy(TEMPLATE),
                "period_start": period_start,
                "period_end": period_end,
                "due_on": period_end,
                "source": {
                    "outcome_observation_id": body["outcome_observation_id"],
                    "outcome_observation_revision": body["outcome_observation_revision"],
                    **{
                        key: outcome[key]
                        for key in (
                            "plan_id",
                            "plan_revision",
                            "deployment_attestation_id",
                            "baseline_object_id",
                            "baseline_revision",
                            "opportunity_id",
                        )
                    },
                },
                "actions": [],
                "agreements": [],
                "started_at": now.isoformat(),
                "started_by": str(ctx.principal_id),
                "advisor_principal_id": str(ctx.principal_id),
                "advisor_membership_id": str(ctx.membership_id),
                "advisor_natural_identity_id": str(ctx.identity.natural_identity_id),
                "completed_at": None,
                "completed_by": None,
                "completion_summary": None,
            }
            saved = write(c, ctx, KIND, payload, "InProgress")
            c.execute(
                "UPDATE impact.object_registry SET classification='CONFIDENTIAL' WHERE tenant_id=%s AND object_id=%s",
                (tenant, saved["object_id"]),
            )
            result = {**saved, "review": payload}
            result.update(operation_id=body["operation_id"], correlation_id=correlation)
            audit(c, ctx, operation, result, correlation)
            _save_receipt(c, ctx, operation, body, fingerprint, result, now)
            return result

    def get(self, identity, tenant, review_id):
        _uuid(review_id)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "get_ai_quarterly_value_review", review_id, hidden=True)
            return _result(self._load_current(c, ctx, identity, tenant, review_id))

    def agreement(self, identity, tenant, review_id, body, correlation):
        if not isinstance(body, dict) or set(body) != {
            "operation_id",
            "expected_revision",
            "agreement_id",
            "text",
        }:
            _invalid()
        for key in ("operation_id", "expected_revision", "agreement_id"):
            _uuid(body[key])
        if not isinstance(body["text"], str) or not body["text"].strip() or len(body["text"]) > 2000:
            _invalid()
        operation = "record_ai_quarterly_review_agreement"
        fingerprint = hash_data([operation, review_id, body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, operation, review_id, hidden=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            now = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            old = _receipt(c, ctx, operation, body, fingerprint, now)
            if old:
                self._load_current(c, ctx, identity, tenant, review_id)
                return old
            previous = self._load_current(c, ctx, identity, tenant, review_id, body["expected_revision"])
            if previous["lifecycle_state"] != "InProgress":
                raise DomainError("STATE_TRANSITION_DENIED", 409)
            payload = deepcopy(previous["payload"])
            if len(payload["agreements"]) >= 50 or any(
                item["agreement_id"] == body["agreement_id"] for item in payload["agreements"]
            ):
                _invalid("QUARTERLY_REVIEW_AGREEMENT_INVALID")
            payload["agreements"].append(
                {
                    "agreement_id": body["agreement_id"],
                    "text": body["text"].strip(),
                    "agreed_at": now.isoformat(),
                    "agreed_by": str(ctx.principal_id),
                }
            )
            saved = write(c, ctx, KIND, payload, "InProgress", previous=previous)
            result = {**saved, "review": payload}
            result.update(operation_id=body["operation_id"], correlation_id=correlation)
            audit(c, ctx, operation, result, correlation)
            _save_receipt(c, ctx, operation, body, fingerprint, result, now)
            return result

    def action(self, identity, tenant, review_id, body, correlation, action_id=None):
        required = {"operation_id", "expected_revision"}
        if action_id is None:
            required |= {"action_id", "agreement_id", "title", "owner_membership_id", "due_on"}
        else:
            required |= {"status", "note"}
        if not isinstance(body, dict) or set(body) != required:
            _invalid()
        _uuid(review_id)
        _uuid(body["operation_id"])
        _uuid(body["expected_revision"])
        if action_id is None:
            _uuid(body["action_id"])
            _uuid(body["agreement_id"])
            _uuid(body["owner_membership_id"])
            if not isinstance(body["title"], str) or not body["title"].strip() or len(body["title"]) > 300:
                _invalid()
            try:
                due = date.fromisoformat(body["due_on"])
            except (TypeError, ValueError):
                _invalid()
            if due < date.today():
                _invalid("QUARTERLY_REVIEW_ACTION_DUE_DATE_INVALID")
            operation = "record_ai_quarterly_review_action"
        else:
            _uuid(action_id)
            if body["status"] not in {"OPEN", "IN_PROGRESS", "BLOCKED", "DONE"}:
                _invalid()
            if not isinstance(body["note"], str) or not body["note"].strip() or len(body["note"]) > 2000:
                _invalid()
            operation = "track_ai_quarterly_review_action"
        fingerprint = hash_data([operation, review_id, action_id, body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, operation, review_id, hidden=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            now = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            old = _receipt(c, ctx, operation, body, fingerprint, now)
            if old:
                current = self._load_current(c, ctx, identity, tenant, review_id)
                saved = next(
                    (
                        item
                        for item in current["payload"]["actions"]
                        if item["action_id"] == (body.get("action_id") or action_id)
                    ),
                    None,
                )
                if saved is None:
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
                self._owner(c, tenant, saved["owner_membership_id"])
                return old
            previous = self._load_current(c, ctx, identity, tenant, review_id, body["expected_revision"])
            if previous["lifecycle_state"] != "InProgress":
                raise DomainError("STATE_TRANSITION_DENIED", 409, reason="QUARTERLY_REVIEW_NOT_IN_PROGRESS")
            payload = deepcopy(previous["payload"])
            if action_id is None:
                if len(payload["actions"]) >= 50 or any(
                    item["action_id"] == body["action_id"] for item in payload["actions"]
                ):
                    _invalid("QUARTERLY_REVIEW_ACTION_INVALID")
                if not any(
                    item["agreement_id"] == body["agreement_id"] for item in payload["agreements"]
                ) or any(item["agreement_id"] == body["agreement_id"] for item in payload["actions"]):
                    _invalid("QUARTERLY_REVIEW_ACTION_AGREEMENT_INVALID")
                owner = self._owner(c, tenant, body["owner_membership_id"])
                payload["actions"].append(
                    {
                        "action_id": body["action_id"],
                        "agreement_id": body["agreement_id"],
                        "title": body["title"].strip(),
                        "owner_membership_id": body["owner_membership_id"],
                        "owner_principal_id": str(owner["principal_id"]),
                        "due_on": body["due_on"],
                        "status": "OPEN",
                        "created_at": now.isoformat(),
                        "created_by": str(ctx.principal_id),
                        "progress": [],
                    }
                )
            else:
                item = next((item for item in payload["actions"] if item["action_id"] == action_id), None)
                if item is None:
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
                self._owner(c, tenant, item["owner_membership_id"])
                if len(item["progress"]) >= 20:
                    raise DomainError("LIMIT_EXCEEDED", 422, reason="ACTION_PROGRESS_LIMIT")
                item["status"] = body["status"]
                item["progress"].append(
                    {
                        "status": body["status"],
                        "note": body["note"].strip(),
                        "recorded_at": now.isoformat(),
                        "recorded_by": str(ctx.principal_id),
                    }
                )
            saved = write(c, ctx, KIND, payload, "InProgress", previous=previous)
            result = {**saved, "review": payload}
            result.update(operation_id=body["operation_id"], correlation_id=correlation)
            audit(c, ctx, operation, result, correlation)
            _save_receipt(c, ctx, operation, body, fingerprint, result, now)
            return result

    def complete(self, identity, tenant, review_id, body, correlation):
        if not isinstance(body, dict) or set(body) != {
            "operation_id",
            "expected_revision",
            "summary",
        }:
            _invalid()
        _uuid(review_id)
        _uuid(body["operation_id"])
        _uuid(body["expected_revision"])
        if not isinstance(body["summary"], str) or not body["summary"].strip() or len(body["summary"]) > 4000:
            _invalid()
        operation = "complete_ai_quarterly_value_review"
        fingerprint = hash_data([operation, review_id, body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, operation, review_id, hidden=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            now = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            old = _receipt(c, ctx, operation, body, fingerprint, now)
            if old:
                current = self._load_current(c, ctx, identity, tenant, review_id)
                for item in current["payload"]["actions"]:
                    self._owner(c, tenant, item["owner_membership_id"])
                return old
            previous = self._load_current(c, ctx, identity, tenant, review_id, body["expected_revision"])
            if previous["lifecycle_state"] != "InProgress":
                raise DomainError("STATE_TRANSITION_DENIED", 409)
            actions = previous["payload"]["actions"]
            agreements = previous["payload"]["agreements"]
            linked = [item["agreement_id"] for item in actions]
            if (
                len(linked) != len(set(linked))
                or set(linked) != {item["agreement_id"] for item in agreements}
                or any(
                    not item["owner_membership_id"]
                    or item["status"] not in {"OPEN", "IN_PROGRESS", "BLOCKED", "DONE"}
                    for item in actions
                )
            ):
                raise DomainError("STATE_TRANSITION_DENIED", 409, reason="UNTRACKED_REVIEW_ACTIONS")
            for item in actions:
                self._owner(c, tenant, item["owner_membership_id"])
            payload = deepcopy(previous["payload"])
            payload.update(
                completed_at=now.isoformat(),
                completed_by=str(ctx.principal_id),
                completion_summary=body["summary"].strip(),
            )
            saved = write(c, ctx, KIND, payload, "Completed", previous=previous)
            result = {**saved, "review": payload}
            result.update(operation_id=body["operation_id"], correlation_id=correlation)
            audit(c, ctx, operation, result, correlation)
            _save_receipt(c, ctx, operation, body, fingerprint, result, now)
            return result
