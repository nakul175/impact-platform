"""Explicit, recipient-bound sponsor reports from self-reported realised values."""

import base64
import hashlib
import re
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, localcontext
from uuid import UUID

from psycopg.types.json import Jsonb

from .ai_value_case_versions import _revision as value_case_revision
from .domain import DomainError
from .store import audit, authorize, canonical, context, hash_data, load, write

KIND = "AISponsorValueReport"
VALUE_KIND = "AIValueCase"
OUTCOME_KIND = "AICurrentOutcomeObservation"
SELECTABLE = {
    "ROI_PERCENT",
    "NET_BENEFIT",
    "REALISED_BENEFIT",
    "REALISED_COST",
    "USAGE",
    "TIME",
    "COST",
    "QUALITY",
    "REACH",
}
RENDERER = "ai-sponsor-value-report-v1"


def _invalid(reason="SPONSOR_VALUE_REPORT_INVALID"):
    raise DomainError("VALIDATION_FAILED", reason=reason)


def _uuid(value):
    try:
        canonical_value = str(UUID(value))
    except (TypeError, ValueError, AttributeError):
        _invalid()
    if canonical_value != value:
        _invalid()
    return canonical_value


def _money(value):
    if not isinstance(value, str) or len(value) > 40:
        _invalid()
    try:
        number = Decimal(value)
    except InvalidOperation:
        _invalid()
    if (
        not number.is_finite()
        or number < 0
        or number.as_tuple().exponent < -12
        or len(number.as_tuple().digits) > 38
    ):
        _invalid()
    return number


class AISponsorValueReports:
    def __init__(self, service, outcome_observations):
        self.service, self.outcomes = service, outcome_observations

    def _source(self, c, identity, tenant, body):
        ctx = context(c, identity, tenant)
        value = load(c, ctx, body["value_case_object_id"], VALUE_KIND, "ai.value-case.read")
        if str(value["head_revision"]) != body["value_case_revision"]:
            raise DomainError("CONFLICT_VERSION", 409, reason="VALUE_CASE_CHANGED")
        value_payload = value_case_revision(
            c, tenant, body["value_case_object_id"], body["value_case_revision"]
        )
        if value["lifecycle_state"] != "Locked" or value_payload["version_state"] != "Locked":
            raise DomainError("STATE_TRANSITION_DENIED", 409, reason="LOCKED_VALUE_CASE_REQUIRED")
        observation = load(c, ctx, body["outcome_observation_id"], OUTCOME_KIND, "ai.enablement.read")
        if str(observation["head_revision"]) != body["outcome_observation_revision"]:
            raise DomainError("CONFLICT_VERSION", 409, reason="OUTCOME_OBSERVATION_CHANGED")
        outcome = observation["payload"]
        selectors = {
            name: outcome[name]
            for name in (
                "plan_id",
                "plan_revision",
                "deployment_attestation_id",
                "baseline_object_id",
                "baseline_revision",
                "opportunity_id",
            )
        }
        self.outcomes._resolve(c, identity, tenant, selectors)
        if value_payload["value_case"]["opportunity_id"] != outcome["opportunity_id"]:
            raise DomainError("STATE_TRANSITION_DENIED", 409, reason="VALUE_CASE_OPPORTUNITY_MISMATCH")
        return value_payload, outcome

    @staticmethod
    def _sponsor(c, tenant, membership_id, now):
        sponsor = c.execute(
            "SELECT m.object_id,m.identity_id,p.principal_id FROM impact.membership_current m JOIN impact.object_registry r ON r.tenant_id=m.tenant_id AND r.object_id=m.object_id JOIN impact.tenant_principal p ON p.tenant_id=m.tenant_id AND p.identity_id=m.identity_id WHERE m.tenant_id=%s AND m.object_id=%s AND m.external IS TRUE AND (m.status IS NULL OR m.status='Active') AND r.lifecycle_state='Active' AND p.active AND (m.expires_at IS NULL OR m.expires_at>%s)",
            (tenant, membership_id, now),
        ).fetchone()
        if not sponsor:
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
        return sponsor

    @staticmethod
    def _validate(body):
        required = {
            "operation_id",
            "sponsor_membership_id",
            "expires_at",
            "title",
            "value_case_object_id",
            "value_case_revision",
            "outcome_observation_id",
            "outcome_observation_revision",
            "realised",
            "selected_items",
        }
        if not isinstance(body, dict) or set(body) != required:
            _invalid()
        for name in (
            "operation_id",
            "sponsor_membership_id",
            "value_case_object_id",
            "value_case_revision",
            "outcome_observation_id",
            "outcome_observation_revision",
        ):
            _uuid(body[name])
        if not isinstance(body["title"], str) or not body["title"].strip() or len(body["title"]) > 150:
            _invalid()
        selected = body["selected_items"]
        if (
            not isinstance(selected, list)
            or not selected
            or len(selected) != len(set(selected))
            or set(selected) - SELECTABLE
        ):
            _invalid("SPONSOR_VALUE_SELECTION_INVALID")
        realised = body["realised"]
        if not isinstance(realised, dict) or set(realised) != {
            "currency",
            "observed_from",
            "observed_to",
            "realised_benefit",
            "realised_cost",
            "source_note",
        }:
            _invalid()
        if (
            not isinstance(realised["currency"], str)
            or re.fullmatch(r"[A-Za-z]{3}", realised["currency"]) is None
        ):
            _invalid()
        benefit, cost = _money(realised["realised_benefit"]), _money(realised["realised_cost"])
        if cost == 0:
            _invalid("REALISED_COST_ZERO")
        try:
            start, end = (
                date.fromisoformat(realised["observed_from"]),
                date.fromisoformat(realised["observed_to"]),
            )
        except (TypeError, ValueError):
            _invalid()
        if (
            end < start
            or end > date.today()
            or not isinstance(realised["source_note"], str)
            or not realised["source_note"].strip()
            or len(realised["source_note"]) > 2000
        ):
            _invalid()
        try:
            expiry = datetime.fromisoformat(body["expires_at"].replace("Z", "+00:00"))
        except (TypeError, ValueError):
            _invalid()
        if expiry.tzinfo is None:
            _invalid()
        return benefit, cost, expiry

    def create(self, identity, tenant, body, correlation):
        benefit, cost, expiry = self._validate(body)
        operation = "create_ai_sponsor_value_report"
        fingerprint = hash_data([operation, body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, operation, hidden=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            now = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, operation, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= now:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                existing = load(c, ctx, old["outcome"]["object_id"], KIND)
                self._sponsor(c, tenant, existing["payload"]["recipient_membership_id"], now)
                self._source(c, identity, tenant, existing["payload"])
                return old["outcome"]
            if expiry <= now or expiry > now + timedelta(days=90):
                _invalid("SPONSOR_VALUE_EXPIRY_INVALID")
            sponsor = self._sponsor(c, tenant, body["sponsor_membership_id"], now)
            value_case, outcome = self._source(c, identity, tenant, body)
            currency = body["realised"]["currency"].upper()
            if value_case["value_case"]["currency"] != currency:
                _invalid("REALISED_CURRENCY_MISMATCH")
            with localcontext() as decimal_context:
                decimal_context.prec = 50
                net = benefit - cost
                roi = (net * Decimal(100) / cost).quantize(Decimal("0.000001"))
            all_items = {
                "ROI_PERCENT": str(roi),
                "NET_BENEFIT": str(net),
                "REALISED_BENEFIT": str(benefit),
                "REALISED_COST": str(cost),
            }
            for name in ("usage", "time", "cost", "quality", "reach"):
                all_items[name.upper()] = deepcopy(outcome["metrics"][name])
            items = {key: all_items[key] for key in body["selected_items"]}
            payload = {
                "title": body["title"].strip(),
                "recipient_membership_id": body["sponsor_membership_id"],
                "recipient_identity_id": str(sponsor["identity_id"]),
                "recipient_principal_id": str(sponsor["principal_id"]),
                "value_case_object_id": body["value_case_object_id"],
                "value_case_revision": body["value_case_revision"],
                "outcome_observation_id": body["outcome_observation_id"],
                "outcome_observation_revision": body["outcome_observation_revision"],
                "selected_items": body["selected_items"],
                "items": items,
                "currency": currency,
                "observed_from": body["realised"]["observed_from"],
                "observed_to": body["realised"]["observed_to"],
                "reporting_basis": "SELF_REPORTED_REALISED",
                "source_note": body["realised"]["source_note"].strip(),
                "generated_at": now.isoformat(),
                "expires_at": expiry.isoformat(),
                "disclaimer": "Organisation-selected self-reported actual values; not official impact, causal proof or independent verification.",
            }
            artifact = canonical(
                {
                    key: deepcopy(payload[key])
                    for key in (
                        "title",
                        "selected_items",
                        "items",
                        "currency",
                        "observed_from",
                        "observed_to",
                        "reporting_basis",
                        "generated_at",
                        "expires_at",
                        "disclaimer",
                    )
                }
            )
            payload["manifest"] = {
                "renderer_version": RENDERER,
                "media_type": "application/json",
                "content_sha256": hashlib.sha256(artifact).hexdigest(),
                "size_bytes": len(artifact),
            }
            payload["content_base64"] = base64.b64encode(artifact).decode("ascii")
            saved = write(c, ctx, KIND, payload, "Published")
            receipt = {**saved, "operation_id": body["operation_id"], "correlation_id": correlation}
            audit(
                c,
                ctx,
                operation,
                {
                    **receipt,
                    "selected_items": body["selected_items"],
                    "recipient_membership_id": body["sponsor_membership_id"],
                },
                correlation,
            )
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

    def get(self, identity, tenant, object_id):
        _uuid(object_id)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "get_ai_sponsor_value_report", object_id, hidden=True)
            report = load(c, ctx, object_id, KIND)
            payload = report["payload"]
            now = datetime.now(timezone.utc)
            if (
                payload["recipient_membership_id"] != ctx.membership_id
                or payload["recipient_identity_id"] != str(ctx.identity.identity_id)
                or payload["recipient_principal_id"] != ctx.principal_id
                or datetime.fromisoformat(payload["expires_at"]) <= now
            ):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            return {
                "object_id": object_id,
                "revision_id": str(report["head_revision"]),
                "business_state": report["lifecycle_state"],
                **{
                    key: deepcopy(payload[key])
                    for key in (
                        "title",
                        "selected_items",
                        "items",
                        "currency",
                        "observed_from",
                        "observed_to",
                        "reporting_basis",
                        "generated_at",
                        "expires_at",
                        "disclaimer",
                        "manifest",
                        "content_base64",
                    )
                },
            }
