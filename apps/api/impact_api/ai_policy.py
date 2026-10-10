"""Versioned tenant AI policy (FR-AI-001): explicit enablement per use case, checked before any AI spend.

AI runs only when three switches are on: the server switch (`ai_enabled` with a configured provider),
the tenant's policy in force, and the use case within it. A policy is changed only by a new version,
never in place: each version is the next immutable revision of the tenant's single AIConfiguration
object plus insert-only `ai_policy_version` / `ai_use_case_policy` rows (migration 0041), committed
with the audit event `ai_policy.changed`, its outbox intent and the operation receipt in one
transaction under the tenant write lock. The enforcement source is the checked relational rows.

`require()` is the gate the advisory request runs after the replay lookup and before any budget
reservation or provider call, inside the same transaction and tenant lock as the reservation.
"""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import re
from uuid import UUID

from psycopg.types.json import Jsonb

from .ai_enablement_contracts import (
    DATA_CLASSES,
    DESTINATIONS,
    LANGUAGE_PATTERN,
    MAX_BUDGET_UNITS,
    MAX_POLICY_VERSION,
    REVIEW_MODES,
    TOOL_PATTERN,
    USE_CASES,
)
from .domain import DomainError
from .store import audit, authorize, context, hash_data, write

KIND = "AIConfiguration"
ROUTE = "ai-enablement/policy"
AUDIT_ACTION = "ai_policy.changed"
OPERATION = "update_ai_policy"
# Only ADVISORY_DRAFT has a runtime in this build. The other use cases are reserved for later stories
# and can be recorded only as disabled (migration 0041 CHECK), so nothing is pre-approved for a feature
# whose data flows have not been designed and reviewed yet.
ACTIVE_USE_CASES = ("ADVISORY_DRAFT",)
RESERVED_USE_CASES = tuple(case for case in USE_CASES if case not in ACTIVE_USE_CASES)
DESTINATION_DETAILS = {"openai-us": {"provider": "OpenAI", "region": "United States"}}
# Allowed data classes are a ceiling: a request passes when its class is at or below the highest
# class the rule lists (PUBLIC < INTERNAL < CONFIDENTIAL < RESTRICTED). An advisory brief is at least
# INTERNAL, so an enabled ADVISORY_DRAFT rule whose ceiling is below INTERNAL could never run.
CLASS_RANK = {name: rank for rank, name in enumerate(DATA_CLASSES)}
MINIMUM_CLASS = {"ADVISORY_DRAFT": "INTERNAL"}
FIELDS = {
    "use_case",
    "enabled",
    "data_classes",
    "destinations",
    "purposes",
    "languages",
    "review_mode",
    "budget_units",
    "tools",
}
LANGUAGE = re.compile(LANGUAGE_PATTERN)
TOOL = re.compile(TOOL_PATTERN)
CONTROL = re.compile(r"[\x00-\x1f\x7f]")
NO_POLICY = {
    "version": 0,
    "policy_version_id": None,
    "object_id": None,
    "created_at": None,
    "created_by": None,
    "use_cases": {},
}


def _invalid(reason="AI_POLICY_INVALID", message=None):
    raise DomainError("VALIDATION_FAILED", message=message, reason=reason)


def _members(value, allowed, maximum):
    if (
        not isinstance(value, list)
        or len(value) > maximum
        or any(not isinstance(item, str) or item not in allowed for item in value)
        or len(set(value)) != len(value)
    ):
        _invalid()
    # Canonical order: the order of the closed list, so equal policies have equal payloads.
    return [item for item in allowed if item in value]


def _purposes(value):
    if not isinstance(value, list) or len(value) > 10:
        _invalid()
    for item in value:
        if (
            not isinstance(item, str)
            or not 1 <= len(item) <= 200
            or item != item.strip()
            or CONTROL.search(item)
        ):
            _invalid()
    if len({item.casefold() for item in value}) != len(value):
        _invalid()
    return list(value)


def _languages(value):
    if not isinstance(value, list) or len(value) > 20:
        _invalid()
    if any(not isinstance(item, str) or not LANGUAGE.fullmatch(item) for item in value):
        _invalid("AI_POLICY_INVALID", "Languages must be BCP 47 tags such as en, hi or pt-BR.")
    if len({item.lower() for item in value}) != len(value):
        _invalid()
    return list(value)


def validate_policy(data):
    """The closed policy body `{use_cases: [...]}`, normalised; raises VALIDATION_FAILED otherwise."""
    if (
        not isinstance(data, dict)
        or set(data) != {"use_cases"}
        or not isinstance(data["use_cases"], list)
        or len(data["use_cases"]) > len(USE_CASES)
    ):
        _invalid()
    rules, seen = [], set()
    for item in data["use_cases"]:
        if not isinstance(item, dict) or set(item) != FIELDS:
            _invalid()
        use_case = item["use_case"]
        if use_case not in USE_CASES or use_case in seen:
            _invalid()
        seen.add(use_case)
        if type(item["enabled"]) is not bool:
            _invalid()
        if not isinstance(item["tools"], list) or item["tools"]:
            # No tool catalogue exists: a policy may never grant a tool implicitly or explicitly yet.
            _invalid("AI_TOOLS_NOT_ALLOWED", "No AI tool can be enabled in this release; leave tools empty.")
        if item["review_mode"] not in REVIEW_MODES:
            _invalid()
        budget = item["budget_units"]
        if type(budget) is not int or not 0 <= budget <= MAX_BUDGET_UNITS:
            _invalid()
        rule = {
            "use_case": use_case,
            "enabled": item["enabled"],
            "data_classes": _members(item["data_classes"], DATA_CLASSES, len(DATA_CLASSES)),
            "destinations": _members(item["destinations"], DESTINATIONS, 10),
            "purposes": _purposes(item["purposes"]),
            "languages": _languages(item["languages"]),
            "review_mode": item["review_mode"],
            "budget_units": budget,
            "tools": [],
        }
        if rule["enabled"] and use_case not in ACTIVE_USE_CASES:
            _invalid(
                "AI_USE_CASE_RESERVED",
                "This AI use case is reserved for a later release and cannot be enabled yet.",
            )
        if rule["enabled"] and not all(
            rule[field] for field in ("data_classes", "destinations", "purposes", "languages")
        ):
            _invalid(
                "AI_POLICY_INCOMPLETE",
                "An enabled use case needs at least one data class, destination, purpose and language.",
            )
        minimum = MINIMUM_CLASS.get(use_case)
        if rule["enabled"] and minimum and ceiling(rule["data_classes"]) < CLASS_RANK[minimum]:
            _invalid(
                "AI_DATA_CLASS_TOO_LOW",
                "AI advisory drafts send an organisation brief, which is internal data. Allow at least "
                "internal data or turn the use case off.",
            )
        rules.append(rule)
    return sorted(rules, key=lambda rule: USE_CASES.index(rule["use_case"]))


def ceiling(data_classes):
    """The rank of the highest allowed data class, or -1 when none is allowed."""
    return max((CLASS_RANK[name] for name in data_classes if name in CLASS_RANK), default=-1)


def _rule(row):
    return {
        "use_case": row["use_case"],
        "enabled": row["enabled"],
        "data_classes": list(row["data_classes"]),
        "destinations": list(row["destinations"]),
        "purposes": list(row["purposes"]),
        "languages": list(row["languages"]),
        "review_mode": row["review_mode"],
        "budget_units": row["budget_units"],
        "tools": list(row["tools"]),
    }


def _rules(c, tenant, version_id):
    rows = c.execute(
        "SELECT use_case,enabled,data_classes,destinations,purposes,languages,review_mode,budget_units,tools "
        "FROM impact.ai_use_case_policy WHERE tenant_id=%s AND policy_version_id=%s",
        (tenant, version_id),
    ).fetchall()
    return {row["use_case"]: _rule(row) for row in rows}


def in_force(c, tenant):
    """The latest policy version of the tenant (version 0 and no use case when none was ever set).

    Read failures propagate: the caller's transaction rolls back and no AI runs (fail closed)."""
    row = c.execute(
        "SELECT policy_version_id,object_id,version_no,created_by,created_at FROM impact.ai_policy_version "
        "WHERE tenant_id=%s ORDER BY version_no DESC LIMIT 1",
        (tenant,),
    ).fetchone()
    if not row:
        return deepcopy(NO_POLICY)
    return {
        "version": row["version_no"],
        "policy_version_id": str(row["policy_version_id"]),
        "object_id": str(row["object_id"]),
        "created_at": row["created_at"],
        "created_by": str(row["created_by"]),
        "use_cases": _rules(c, tenant, row["policy_version_id"]),
    }


def enabled(policy, use_case):
    rule = policy["use_cases"].get(use_case)
    return bool(rule and rule["enabled"])


def _covers(languages, language):
    primary = language.split("-")[0].lower()
    return any(tag.split("-")[0].lower() == primary for tag in languages)


def require(policy, use_case, version, data_class, destination, language, tools=()):
    """Refuse an AI request the policy in force does not allow. Raises; returns the rule otherwise.

    Order: a request made against another policy version (409 AI_POLICY_CHANGED), a use case that is
    not enabled (503 AI_USE_CASE_DISABLED, the not-configured behaviour), then every rule of the use
    case (422 AI_POLICY_BLOCKED naming each unmet rule)."""
    if type(version) is not int or version != policy["version"]:
        raise DomainError(
            "CONFLICT_VERSION",
            409,
            message="Your organisation's AI policy changed. Reload the policy in force before requesting AI.",
            reason="AI_POLICY_CHANGED",
        )
    rule = policy["use_cases"].get(use_case)
    if not rule or not rule["enabled"]:
        raise DomainError(
            "SERVICE_UNAVAILABLE",
            503,
            message="Your organisation's AI policy does not enable this AI use.",
            reason="AI_USE_CASE_DISABLED",
        )
    problems = []
    if data_class not in CLASS_RANK or CLASS_RANK[data_class] > ceiling(rule["data_classes"]):
        problems.append(data_class.lower() + " data is above the highest allowed data class")
    if destination not in rule["destinations"]:
        problems.append("the configured AI provider is not an allowed destination")
    if not rule["purposes"]:
        problems.append("no approved purpose is recorded")
    if not _covers(rule["languages"], language):
        problems.append("the draft language (" + language + ") is not covered")
    if rule["review_mode"] not in REVIEW_MODES:
        problems.append("no supported review mode is recorded")
    if rule["budget_units"] < 1:
        problems.append("no budget is approved")
    if set(tools) - set(rule["tools"]):
        problems.append("tools are not allowed for this use case")
    if problems:
        raise DomainError(
            "VALIDATION_FAILED",
            422,
            message="This request is outside your organisation's AI policy: " + "; ".join(problems) + ".",
            reason="AI_POLICY_BLOCKED",
        )
    return rule


def _iso(value):
    return value.isoformat() if value else None


def _version_view(policy):
    return {
        "policy_version": policy["version"],
        "policy_version_id": policy["policy_version_id"],
        "created_at": _iso(policy["created_at"]),
        "created_by": policy["created_by"],
        "use_cases": [policy["use_cases"][case] for case in USE_CASES if case in policy["use_cases"]],
    }


def _request(body):
    if not isinstance(body, dict) or set(body) != {"operation_id", "expected_version", "data"}:
        _invalid()
    try:
        if not isinstance(body["operation_id"], str):
            raise ValueError
        UUID(body["operation_id"])
    except (ValueError, AttributeError):
        _invalid()
    expected = body["expected_version"]
    if type(expected) is not int or not 0 <= expected <= MAX_POLICY_VERSION:
        _invalid()


class AIPolicy:
    """GET/PUT .../ai-enablement/policy and GET .../policy/revisions."""

    def __init__(self, service, server_ready=lambda: False):
        self.service, self.server_ready = service, server_ready

    def get(self, identity, tenant):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "get_ai_policy", hidden=True)
            policy = in_force(c, tenant)
            server = bool(self.server_ready())
            return {
                **_version_view(policy),
                "server_enabled": server,
                "advisory_available": server and enabled(policy, "ADVISORY_DRAFT"),
                "destinations": [
                    {"id": key, **DESTINATION_DETAILS[key]}
                    for key in DESTINATIONS
                    if key in DESTINATION_DETAILS
                ],
                "reserved_use_cases": list(RESERVED_USE_CASES),
            }

    def revisions(self, identity, tenant, limit=50, cursor=None):
        if type(limit) is not int or not 1 <= limit <= 100:
            _invalid()
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_ai_policy_revisions", hidden=True)
            bound = self.service.cursor_binding(ctx, ROUTE + "/revisions")
            key = self.service.cursor_key(bound, cursor)
            if key is not None and (
                not isinstance(key, list) or len(key) != 1 or type(key[0]) is not int or key[0] < 1
            ):
                raise DomainError("INVALID_CURSOR", 400)
            query = (
                "SELECT policy_version_id,object_id,version_no,created_by,created_at "
                "FROM impact.ai_policy_version WHERE tenant_id=%s"
            )
            params = [tenant]
            if key is not None:
                query += " AND version_no<%s"
                params.append(key[0])
            query += " ORDER BY version_no DESC LIMIT %s"
            params.append(limit + 1)
            rows = c.execute(query, params).fetchall()
            page = rows[:limit]
            # One read for the rules of the whole page.
            rules = {}
            for rule in c.execute(
                "SELECT policy_version_id,use_case,enabled,data_classes,destinations,purposes,languages,"
                "review_mode,budget_units,tools FROM impact.ai_use_case_policy "
                "WHERE tenant_id=%s AND policy_version_id=ANY(%s::uuid[])",
                (tenant, [str(row["policy_version_id"]) for row in page]),
            ).fetchall():
                rules.setdefault(str(rule["policy_version_id"]), {})[rule["use_case"]] = _rule(rule)
            items = [
                _version_view(
                    {
                        "version": row["version_no"],
                        "policy_version_id": str(row["policy_version_id"]),
                        "created_at": row["created_at"],
                        "created_by": str(row["created_by"]),
                        "use_cases": rules.get(str(row["policy_version_id"]), {}),
                    }
                )
                for row in page
            ]
            return {
                "items": items,
                "next_cursor": self.service.next_cursor(bound, [page[-1]["version_no"]])
                if len(rows) > limit
                else None,
            }

    def save(self, identity, tenant, body, correlation):
        _request(body)
        rules = validate_policy(body["data"])
        fingerprint = hash_data([OPERATION, body])
        now = datetime.now(timezone.utc)
        with self.service.db.transaction(tenant) as c:
            # Tenant write lock before resolving authority (rule 17); serialises policy versions with
            # every AI reservation, which reads the policy under the same lock.
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "get_ai_policy", hidden=True)
            # TENANT_ADMIN only, authentication within 300 s plus the configured assurance (policy row).
            authorize(c, ctx, OPERATION)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s "
                "AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, OPERATION, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= now:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                return old["outcome"]
            current = in_force(c, tenant)
            if current["version"] != body["expected_version"]:
                raise DomainError(
                    "CONFLICT_VERSION",
                    409,
                    message="The AI policy changed since you opened it. Reload it and review the changes.",
                    reason="AI_POLICY_CHANGED",
                )
            previous = None
            if current["object_id"]:
                previous = c.execute(
                    "SELECT r.object_id,r.head_revision,v.revision_number FROM impact.object_registry r "
                    "JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.object_id=r.object_id "
                    "AND v.revision_id=r.head_revision "
                    "WHERE r.tenant_id=%s AND r.object_id=%s AND r.object_type=%s FOR UPDATE OF r",
                    (tenant, current["object_id"], KIND),
                ).fetchone()
                if not previous or str(previous["head_revision"]) != current["policy_version_id"]:
                    # The registry head and the version register must agree; never guess.
                    raise DomainError("SERVICE_UNAVAILABLE", 503, reason="AI_POLICY_UNREADABLE")
            version = current["version"] + 1
            receipt = write(
                c,
                ctx,
                KIND,
                {"policy_version": version, "use_cases": rules},
                "Active",
                previous=previous,
            )
            c.execute(
                "INSERT INTO impact.ai_policy_version(tenant_id,policy_version_id,object_id,version_no,created_by,created_at) "
                "VALUES(%s,%s,%s,%s,%s,%s)",
                (tenant, receipt["revision_id"], receipt["object_id"], version, ctx.principal_id, now),
            )
            for rule in rules:
                c.execute(
                    "INSERT INTO impact.ai_use_case_policy(tenant_id,policy_version_id,use_case,enabled,data_classes,"
                    "destinations,purposes,languages,review_mode,budget_units,tools) "
                    "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        tenant,
                        receipt["revision_id"],
                        rule["use_case"],
                        rule["enabled"],
                        rule["data_classes"],
                        rule["destinations"],
                        rule["purposes"],
                        rule["languages"],
                        rule["review_mode"],
                        rule["budget_units"],
                        rule["tools"],
                    ),
                )
            receipt.update(
                operation_id=body["operation_id"],
                correlation_id=correlation,
                policy_version=version,
                policy_version_id=receipt["revision_id"],
            )
            audit(c, ctx, AUDIT_ACTION, receipt, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    OPERATION,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(receipt),
                    now + timedelta(days=7),
                ),
            )
            return receipt
