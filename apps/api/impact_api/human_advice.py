"""Internal peer advice draft: scoped participants, immutable consent and accountable notes.

The transaction-local principal is resolved by application authentication. Its SQL
policies guard missing or mis-scoped context; a writable GUC is not authentication
against a compromised database login. No provider or external adapter is used.
"""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from jsonschema import Draft202012Validator, FormatChecker
from psycopg.types.json import Jsonb

from .administration import Administration
from .domain import DomainError
from .human_advice_contracts import (
    PUBLIC_DECISION_FIELDS,
    PUBLIC_FIELDS,
    ROUTE,
    operation,
    stored_schema,
    validate_body,
)
from .store import audit, authorize, context, hash_data, load, visible_sql, write

KIND = "HumanAdviceCase"
READ_CAP = "ai.enablement.read"
TERMINAL = {"Closed", "Cancelled"}
REQUESTER_ACTIONS = {"assign", "respond", "close", "cancel"}
ADVISER_ACTIONS = {"declare-scope", "request-input", "advise"}
STORED_VALIDATOR = Draft202012Validator(stored_schema(), format_checker=FormatChecker())


def selector(value):
    # psycopg returns UUID objects for server-owned projection selectors.
    # Closed request schemas still accept only UUID strings on transport.
    if isinstance(value, UUID):
        return str(value)
    try:
        return str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        raise DomainError("VALIDATION_FAILED", reason="HUMAN_ADVICE_INVALID") from None


def unavailable():
    raise DomainError("RESOURCE_UNAVAILABLE", 404)


def denied(reason):
    raise DomainError("POLICY_DENIED", 403, reason=reason)


def role(payload, principal):
    if str(principal) == payload["requester_principal_id"]:
        return "REQUESTER"
    if str(principal) == payload["adviser_principal_id"]:
        return "ADVISER"
    unavailable()


def brief_digest(problem, nonce):
    """The private nonce prevents invitation hashes from confirming guessed briefs."""
    return hash_data({"problem": problem, "nonce": str(nonce)})


def initial_payload(data, participants, authenticated_at, brief_nonce=None):
    if participants["requester_natural_id"] == participants["adviser_natural_id"]:
        denied("INDEPENDENCE_REQUIRED")
    result = {
        **{key: deepcopy(value) for key, value in data.items() if key != "problem"},
        **deepcopy(participants),
        "state": "Open",
        "case_schema_version": "internal-peer-advice-v1",
        "requester_auth_time": authenticated_at,
        "problem_sha256": brief_digest(data["problem"], brief_nonce or uuid4()).hex(),
        "declaration": None,
        "assignment": None,
        "notes": [],
        "advice": None,
        "closure": None,
        "cancellation": None,
    }
    for key in ("context_plan_id", "context_plan_revision", "adviser_membership_id"):
        result[key] = selector(result[key])
    return result


def public_payload(payload):
    """Participants receive case content, never the server's private alias/auth proofs."""
    result = {key: deepcopy(payload[key]) for key in PUBLIC_FIELDS}
    for key, fields in PUBLIC_DECISION_FIELDS.items():
        if result[key] is not None:
            result[key] = {field: result[key][field] for field in fields}
    return result


def transition(payload, state, action, data, principal, revision_id, recorded_at, authenticated_at=None):
    """Pure material transitions; capability, membership and freshness are checked outside."""
    who = role(payload, principal)
    if action not in REQUESTER_ACTIONS | ADVISER_ACTIONS:
        unavailable()
    if (action in REQUESTER_ACTIONS) != (who == "REQUESTER"):
        unavailable()
    if state in TERMINAL:
        raise DomainError("STATE_TRANSITION_DENIED", 409, reason="HUMAN_ADVICE_TERMINAL")
    result = deepcopy(payload)

    def finish(next_state):
        result["state"] = next_state
        return result, next_state

    if action == "cancel":
        result["cancellation"] = {**data, "cancelled_by": str(principal), "cancelled_at": recorded_at}
        return finish("Cancelled")
    if action == "declare-scope":
        if state != "Open":
            raise DomainError("STATE_TRANSITION_DENIED", 409)
        if data["conflict"] == "DECLARED" and data["scope_accepted"]:
            denied("CONFLICT_CANNOT_ACCEPT_SCOPE")
        result["declaration"] = {
            **data,
            "declared_by": str(principal),
            "declared_at": recorded_at,
            "authenticated_at": authenticated_at or recorded_at,
        }
        return finish("Open")
    if action == "assign":
        if state != "Open" or not payload["declaration"]:
            raise DomainError("STATE_TRANSITION_DENIED", 409, reason="SCOPE_DECLARATION_REQUIRED")
        declaration = payload["declaration"]
        if declaration["conflict"] != "NONE":
            denied("DECLARED_CONFLICT")
        if not declaration["scope_accepted"]:
            denied("SCOPE_NOT_ACCEPTED")
        if selector(data["declaration_revision_id"]) != str(revision_id):
            raise DomainError("CONFLICT_VERSION", 409, reason="SCOPE_DECLARATION_CHANGED")
        if data["sharing_confirmed"] is not True:
            denied("SHARING_CONSENT_REQUIRED")
        result["assignment"] = {
            **data,
            "declaration_revision_id": selector(data["declaration_revision_id"]),
            "assigned_by": str(principal),
            "assigned_at": recorded_at,
            "authenticated_at": authenticated_at or recorded_at,
        }
        return finish("Assigned")
    if action in {"request-input", "respond"}:
        expected = {"Assigned", "AdviceDraft"} if action == "request-input" else {"AwaitingInput"}
        if state not in expected:
            raise DomainError("STATE_TRANSITION_DENIED", 409)
        if len(result["notes"]) >= 50:
            raise DomainError("LIMIT_EXCEEDED", 429, reason="HUMAN_ADVICE_NOTE_LIMIT")
        result["notes"].append(
            {
                "note_id": str(uuid4()),
                "kind": "QUESTION" if action == "request-input" else "RESPONSE",
                "text": data["question" if action == "request-input" else "response"],
                "author_id": str(principal),
                "recorded_at": recorded_at,
            }
        )
        # A new question invalidates previous draft advice as the closure target.
        result["advice"] = None
        return finish("AwaitingInput" if action == "request-input" else "Assigned")
    if action == "advise":
        if state not in {"Assigned", "AdviceDraft"}:
            raise DomainError("STATE_TRANSITION_DENIED", 409)
        result["advice"] = {
            "text": data["advice"],
            "actions": [{**item, "action_id": str(uuid4())} for item in data["actions"]],
            "advised_by": str(principal),
            "advised_at": recorded_at,
        }
        return finish("AdviceDraft")
    if state != "AdviceDraft" or not payload["advice"]:
        raise DomainError("STATE_TRANSITION_DENIED", 409, reason="FINAL_ADVICE_REQUIRED")
    if selector(data["advice_revision_id"]) != str(revision_id):
        raise DomainError("CONFLICT_VERSION", 409, reason="ADVICE_CHANGED")
    acknowledged = [selector(item) for item in data["acknowledged_action_ids"]]
    required = {item["action_id"] for item in payload["advice"]["actions"]}
    if len(acknowledged) != len(set(acknowledged)) or set(acknowledged) != required:
        denied("ACTION_ACKNOWLEDGEMENT_REQUIRED")
    result["closure"] = {
        **data,
        "advice_revision_id": selector(data["advice_revision_id"]),
        "acknowledged_action_ids": acknowledged,
        "closed_by": str(principal),
        "closed_at": recorded_at,
    }
    return finish("Closed")


def fingerprint_value(value):
    """Canonicalise database metadata without serialising Python UUID/datetime objects."""
    if isinstance(value, dict):
        return {key: fingerprint_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [fingerprint_value(item) for item in value]
    if isinstance(value, (UUID, datetime)):
        return str(value)
    return value


class HumanAdviceCases:
    def __init__(self, service):
        self.service = service

    def actor_context(self, c, identity, tenant, writing=False):
        ctx = context(c, identity, tenant, write=writing)
        c.execute("SELECT set_config('impact.human_advice_principal',%s,true)", (ctx.principal_id,))
        return ctx

    def member(self, c, ctx, membership_id):
        row = c.execute(
            "SELECT m.object_id AS membership_id,m.identity_id,m.expires_at,h.head_revision,"
            "p.principal_id,impact.human_advice_auth_cutoff(p.principal_id) AS auth_not_before,"
            "impact.member_natural_identity(m.tenant_id,p.principal_id) AS natural_id "
            "FROM impact.membership_current m JOIN impact.object_registry h "
            "ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id "
            "JOIN impact.tenant_principal p ON p.tenant_id=m.tenant_id AND p.identity_id=m.identity_id "
            "WHERE m.tenant_id=%s AND m.object_id=%s AND h.lifecycle_state='Active' "
            "AND (m.status IS NULL OR m.status='Active') AND p.active "
            "AND (m.expires_at IS NULL OR m.expires_at>now())",
            (ctx.tenant_id, selector(membership_id)),
        ).fetchone()
        if not row or not row["natural_id"]:
            unavailable()
        return row

    def projection(self, c, ctx, object_id):
        row = c.execute(
            "SELECT * FROM impact.human_advice_case_current WHERE tenant_id=%s AND object_id=%s",
            (ctx.tenant_id, selector(object_id)),
        ).fetchone()
        if not row:
            unavailable()
        return row

    def require_available_anchor(self, c, ctx, plan_id, revision_id):
        """Consent to an exact plan pin ends when that retained revision is unavailable."""
        row = c.execute(
            "SELECT revision_id FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s "
            "AND revision_id=%s AND object_type='AIAdoptionPlan' AND restriction_state='AVAILABLE'",
            (ctx.tenant_id, selector(plan_id), selector(revision_id)),
        ).fetchone()
        if not row:
            unavailable()

    def resolve(self, c, ctx, object_id, requested_operation, writing=False):
        projection = self.projection(c, ctx, object_id)
        actor = "requester" if str(projection["requester_principal_id"]) == ctx.principal_id else "adviser"
        if str(projection[actor + "_principal_id"]) != ctx.principal_id:
            unavailable()
        member = self.member(c, ctx, projection[actor + "_membership_id"])
        if (
            str(member["principal_id"]) != ctx.principal_id
            or str(member["membership_id"]) != ctx.membership_id
            or str(member["natural_id"]) != str(projection[actor + "_natural_id"])
            or str(member["natural_id"]) != ctx.identity.natural_identity_id
        ):
            unavailable()
        if actor == "adviser" and projection["case_state"] in TERMINAL:
            unavailable()
        anchor = str(projection["context_plan_id"])
        authorize(c, ctx, requested_operation, anchor, hidden=True)
        authorize(c, ctx, "get_ai_adoption_plan", anchor, hidden=True)
        plan = load(c, ctx, anchor, "AIAdoptionPlan", READ_CAP)
        self.require_available_anchor(c, ctx, anchor, projection["context_plan_revision"])
        case = load(c, ctx, selector(object_id), KIND, lock=writing)
        if not STORED_VALIDATOR.is_valid(case["payload"]):
            raise DomainError("RESOURCE_UNAVAILABLE", 503, reason="HUMAN_ADVICE_UNREADABLE")
        return projection, case, plan, member

    def current_participants(self, c, ctx, payload):
        proof = []
        for who in ("requester", "adviser"):
            member = self.member(c, ctx, payload[who + "_membership_id"])
            if (
                str(member["principal_id"]) != payload[who + "_principal_id"]
                or str(member["natural_id"]) != payload[who + "_natural_id"]
            ):
                raise DomainError("CONFLICT_VERSION", 409, reason="CASE_PARTICIPANT_CHANGED")
            proof.append(str(member["natural_id"]))
            if not all(
                self.member_scope(c, ctx, member, cap, payload["context_plan_id"])
                for cap in (READ_CAP, "ai.enablement.manage")
            ):
                unavailable()
            consent = (
                (payload["assignment"] or {}).get("authenticated_at", payload["requester_auth_time"])
                if who == "requester"
                else (payload["declaration"] or {}).get("authenticated_at")
            )
            if (
                consent
                and member["auth_not_before"]
                and datetime.fromisoformat(consent) <= member["auth_not_before"]
            ):
                raise DomainError("CONFLICT_VERSION", 409, reason="CASE_CONSENT_CHANGED")
        if proof[0] == proof[1]:
            denied("INDEPENDENCE_REQUIRED")

    def member_scope(self, c, ctx, member, capability, anchor):
        """Resolve current counterpart grants without inventing an authenticated identity."""
        return bool(
            c.execute(
                "SELECT EXISTS(SELECT 1 FROM ("
                "SELECT g.capability,g.scope_id,s.scope_type FROM impact.grant_current g "
                "JOIN impact.object_registry h ON h.tenant_id=g.tenant_id AND h.object_id=g.object_id "
                "JOIN impact.scope_definition s ON s.tenant_id=g.tenant_id AND s.scope_id=g.scope_id "
                "WHERE g.tenant_id=%s AND g.subject_id=%s AND g.purpose IS NULL AND h.lifecycle_state='Active' "
                "AND g.starts_at<=now() AND (g.expires_at IS NULL OR g.expires_at>now()) "
                "UNION ALL SELECT e.capability,e.scope_id,s.scope_type FROM impact.group_entitlement e "
                "JOIN impact.object_registry h ON h.tenant_id=e.tenant_id AND h.object_id=e.group_id "
                "JOIN impact.scope_definition s ON s.tenant_id=e.tenant_id AND s.scope_id=e.scope_id "
                "WHERE e.tenant_id=%s AND e.membership_id=%s AND e.expires_at>now() AND h.lifecycle_state='Active'"
                ") g WHERE g.capability=%s AND (g.scope_type='TENANT' OR EXISTS(SELECT 1 FROM impact.scope_member sm "
                "WHERE sm.tenant_id=%s AND sm.scope_id=g.scope_id AND sm.object_id=%s))) AS allowed",
                (
                    ctx.tenant_id,
                    member["principal_id"],
                    ctx.tenant_id,
                    member["membership_id"],
                    capability,
                    ctx.tenant_id,
                    anchor,
                ),
            ).fetchone()["allowed"]
        )

    def result(self, c, ctx, case, plan):
        payload = deepcopy(case["payload"])
        who = role(payload, ctx.principal_id)
        problem = None
        if who == "REQUESTER" or case["lifecycle_state"] in {"Assigned", "AwaitingInput", "AdviceDraft"}:
            brief = c.execute(
                "SELECT problem,problem_sha256,brief_nonce FROM impact.human_advice_private_brief WHERE tenant_id=%s AND object_id=%s",
                (ctx.tenant_id, case["object_id"]),
            ).fetchone()
            if (
                not brief
                or bytes(brief["problem_sha256"]).hex() != payload["problem_sha256"]
                or brief_digest(brief["problem"], brief["brief_nonce"]) != bytes(brief["problem_sha256"])
            ):
                unavailable()
            problem = brief["problem"]
        return {
            "object_id": str(case["object_id"]),
            "revision_id": str(case["head_revision"]),
            "business_state": case["lifecycle_state"],
            "context_current": str(plan["head_revision"]) == payload["context_plan_revision"],
            "problem": problem,
            "data": public_payload(payload),
        }

    def get(self, identity, tenant, object_id, revision_id=None):
        name = "get_human_advice_revision" if revision_id is not None else "get_human_advice_case"
        with self.service.db.transaction(tenant) as c:
            ctx = self.actor_context(c, identity, tenant)
            _, case, plan, _ = self.resolve(c, ctx, object_id, name)
            if revision_id is not None:
                old = c.execute(
                    "SELECT revision_id,payload FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s "
                    "AND revision_id=%s AND object_type=%s AND restriction_state='AVAILABLE'",
                    (tenant, selector(object_id), selector(revision_id), KIND),
                ).fetchone()
                if not old:
                    unavailable()
                if not STORED_VALIDATOR.is_valid(old["payload"]):
                    raise DomainError("RESOURCE_UNAVAILABLE", 503, reason="HUMAN_ADVICE_UNREADABLE")
                case = {
                    **case,
                    "head_revision": old["revision_id"],
                    "payload": old["payload"],
                    "lifecycle_state": old["payload"]["state"],
                }
                # Current access is checked before reading history. A historical
                # state never reactivates an adviser whose case is now terminal.
            return self.result(c, ctx, case, plan)

    def bound(self, c, ctx, route, projection=None):
        member = self.member(c, ctx, ctx.membership_id)
        if projection is None:
            predicate, args = visible_sql(ctx, READ_CAP)
            rows = c.execute(
                "SELECT p.object_id,p.revision_id,p.case_state,p.context_plan_revision,r.head_revision "
                "FROM impact.human_advice_case_current p JOIN impact.object_registry r "
                "ON r.tenant_id=p.tenant_id AND r.object_id=p.context_plan_id "
                "WHERE p.tenant_id=%s AND " + predicate + " ORDER BY p.object_id",
                [ctx.tenant_id, *args],
            ).fetchall()
            visibility = fingerprint_value([dict(row) for row in rows])
        else:
            visibility = fingerprint_value(dict(projection))
        return hash_data(
            [
                self.service.cursor_binding(ctx, route),
                str(member["head_revision"]),
                str(member["expires_at"]),
                visibility,
            ]
        ).hex()

    def key(self, bound, cursor, number=False):
        key = self.service.cursor_key(bound, cursor)
        if key is not None and (not isinstance(key, list) or len(key) != 1):
            raise DomainError("INVALID_CURSOR", 400)
        if key is None:
            return None
        if number:
            if type(key[0]) is not int or key[0] < 1:
                raise DomainError("INVALID_CURSOR", 400)
            return key[0]
        try:
            return str(UUID(key[0]))
        except (ValueError, TypeError, AttributeError):
            raise DomainError("INVALID_CURSOR", 400) from None

    def directory_authority(self, c, ctx, anchor):
        """Reuse directory gates, then prove the caller's current administrative role."""
        try:
            authorize(c, ctx, "list_membership_directory", hidden=True)
            # The existing helper uses only ctx; keeping the exact check avoids
            # treating an ordinary scoped AI grant as tenant directory authority.
            Administration.require_tenant_admin_scope(self, ctx, "memberships.read")
            authorize(c, ctx, "list_human_advice_eligible_peers", anchor, hidden=True)
            authorize(c, ctx, "get_ai_adoption_plan", anchor, hidden=True)
        except DomainError:
            unavailable()
        current_role = c.execute(
            "SELECT EXISTS(SELECT 1 FROM impact.tenant_custody "
            "WHERE tenant_id=%s AND owner_membership_id=%s) OR EXISTS("
            "SELECT 1 FROM impact.member_role_assignment a JOIN impact.object_revision v "
            "ON v.tenant_id=a.tenant_id AND v.revision_id=a.role_revision "
            "JOIN impact.object_registry h ON h.tenant_id=v.tenant_id AND h.object_id=v.object_id "
            "JOIN impact.grant_current g ON g.tenant_id=a.tenant_id AND g.object_id=ANY(a.grant_ids) "
            "JOIN impact.object_registry gh ON gh.tenant_id=g.tenant_id AND gh.object_id=g.object_id "
            "JOIN impact.scope_definition s ON s.tenant_id=g.tenant_id AND s.scope_id=g.scope_id "
            "WHERE a.tenant_id=%s AND a.membership_id=%s AND a.expires_at>now() "
            "AND h.lifecycle_state='Active' AND v.restriction_state='AVAILABLE' "
            "AND v.payload->>'managed_by'='impact-access-v1' AND v.payload->>'name'='TENANT_ADMIN' "
            "AND g.subject_id=%s AND g.capability='memberships.read' AND g.purpose IS NULL "
            "AND g.starts_at<=now() AND (g.expires_at IS NULL OR g.expires_at>now()) "
            "AND gh.lifecycle_state='Active' AND s.scope_type='TENANT') AS allowed",
            (ctx.tenant_id, ctx.membership_id, ctx.tenant_id, ctx.membership_id, ctx.principal_id),
        ).fetchone()
        if not current_role or not current_role["allowed"]:
            unavailable()

    def peer_candidates(self, c, ctx, anchor):
        """A permission-gated roster, filtered before any paging or public projection."""
        rows = c.execute(
            "SELECT m.object_id AS membership_id,h.head_revision,m.expires_at,"
            "COALESCE(profile.display_name,'Member '||left(m.identity_id::text,8)) AS display_name "
            "FROM impact.membership_current m JOIN impact.object_registry h "
            "ON h.tenant_id=m.tenant_id AND h.object_id=m.object_id "
            "JOIN impact.object_revision v ON v.tenant_id=h.tenant_id AND v.revision_id=h.head_revision "
            "JOIN impact.tenant_principal p ON p.tenant_id=m.tenant_id AND p.identity_id=m.identity_id "
            "LEFT JOIN impact.member_profile profile ON profile.tenant_id=m.tenant_id "
            "AND profile.membership_id=m.object_id WHERE m.tenant_id=%s AND p.active "
            "AND p.principal_id<>%s::uuid AND h.lifecycle_state='Active' "
            "AND h.classification<>'RESTRICTED' AND v.restriction_state='AVAILABLE' "
            "AND (m.status IS NULL OR m.status='Active') AND (m.expires_at IS NULL OR m.expires_at>now()) "
            "AND impact.member_natural_identity(m.tenant_id,p.principal_id) IS NOT NULL "
            "AND impact.member_natural_identity(m.tenant_id,p.principal_id)<>%s::uuid "
            "AND NOT EXISTS(SELECT 1 FROM (VALUES('ai.enablement.read'),('ai.enablement.manage')) wanted(cap) "
            "WHERE NOT EXISTS(SELECT 1 FROM ("
            "SELECT g.capability,g.scope_id,s.scope_type FROM impact.grant_current g "
            "JOIN impact.object_registry gh ON gh.tenant_id=g.tenant_id AND gh.object_id=g.object_id "
            "JOIN impact.scope_definition s ON s.tenant_id=g.tenant_id AND s.scope_id=g.scope_id "
            "WHERE g.tenant_id=m.tenant_id AND g.subject_id=p.principal_id AND g.purpose IS NULL "
            "AND gh.lifecycle_state='Active' AND g.starts_at<=now() "
            "AND (g.expires_at IS NULL OR g.expires_at>now()) "
            "UNION ALL SELECT e.capability,e.scope_id,s.scope_type FROM impact.group_entitlement e "
            "JOIN impact.object_registry eh ON eh.tenant_id=e.tenant_id AND eh.object_id=e.group_id "
            "JOIN impact.scope_definition s ON s.tenant_id=e.tenant_id AND s.scope_id=e.scope_id "
            "WHERE e.tenant_id=m.tenant_id AND e.membership_id=m.object_id "
            "AND e.expires_at>now() AND eh.lifecycle_state='Active') g "
            "WHERE g.capability=wanted.cap AND (g.scope_type='TENANT' OR EXISTS("
            "SELECT 1 FROM impact.scope_member sm WHERE sm.tenant_id=m.tenant_id "
            "AND sm.scope_id=g.scope_id AND sm.object_id=%s::uuid)))) "
            "ORDER BY m.object_id LIMIT 5001",
            (ctx.tenant_id, ctx.principal_id, ctx.identity.natural_identity_id, anchor),
        ).fetchall()
        if len(rows) > 5000:
            raise DomainError("LIMIT_EXCEEDED", 422, reason="HUMAN_ADVICE_PEER_INPUT_LIMIT")
        return rows

    def eligible_peers(self, identity, tenant, context_plan_id, limit=50, cursor=None):
        if type(limit) is not int or not 1 <= limit <= 50:
            raise DomainError("VALIDATION_FAILED", reason="HUMAN_ADVICE_INVALID")
        anchor = selector(context_plan_id)
        with self.service.db.transaction(tenant) as c:
            ctx = self.actor_context(c, identity, tenant)
            self.directory_authority(c, ctx, anchor)
            plan = load(c, ctx, anchor, "AIAdoptionPlan", READ_CAP)
            member = self.member(c, ctx, ctx.membership_id)
            if str(member["natural_id"]) != ctx.identity.natural_identity_id:
                unavailable()
            rows = self.peer_candidates(c, ctx, anchor)
            bound = hash_data(
                [
                    self.service.cursor_binding(ctx, ROUTE + "/eligible-peers/" + anchor),
                    str(plan["head_revision"]),
                    str(member["head_revision"]),
                    str(member["expires_at"]),
                    fingerprint_value([dict(row) for row in rows]),
                ]
            ).hex()
            after = self.key(bound, cursor)
            page = [row for row in rows if after is None or str(row["membership_id"]) > after][: limit + 1]
            return {
                "items": [
                    {"membership_id": str(row["membership_id"]), "display_name": row["display_name"]}
                    for row in page[:limit]
                ],
                "next_cursor": self.service.next_cursor(bound, [str(page[limit - 1]["membership_id"])])
                if len(page) > limit
                else None,
            }

    def listing(self, identity, tenant, limit=50, cursor=None):
        if type(limit) is not int or not 1 <= limit <= 50:
            raise DomainError("VALIDATION_FAILED", reason="HUMAN_ADVICE_INVALID")
        with self.service.db.transaction(tenant) as c:
            ctx = self.actor_context(c, identity, tenant)
            if not any(g["capability"] == READ_CAP and g["purpose"] is None for g in ctx.grants):
                authorize(c, ctx, "list_human_advice_cases", hidden=True)
            bound = self.bound(c, ctx, ROUTE)
            after = self.key(bound, cursor)
            predicate, args = visible_sql(ctx, READ_CAP)
            rows = c.execute(
                "SELECT p.object_id FROM impact.human_advice_case_current p JOIN impact.object_registry r "
                "ON r.tenant_id=p.tenant_id AND r.object_id=p.context_plan_id WHERE p.tenant_id=%s AND "
                + predicate
                + (" AND p.object_id>%s::uuid" if after else "")
                + " ORDER BY p.object_id LIMIT %s",
                [tenant, *args, *([after] if after else []), limit + 1],
            ).fetchall()
            page = rows[:limit]
            items = []
            for item in page:
                _, case, plan, _ = self.resolve(c, ctx, item["object_id"], "list_human_advice_cases")
                items.append(self.result(c, ctx, case, plan))
            return {
                "items": items,
                "next_cursor": self.service.next_cursor(bound, [str(page[-1]["object_id"])])
                if len(rows) > limit
                else None,
            }

    def history(self, identity, tenant, object_id, limit=50, cursor=None):
        if type(limit) is not int or not 1 <= limit <= 50:
            raise DomainError("VALIDATION_FAILED", reason="HUMAN_ADVICE_INVALID")
        with self.service.db.transaction(tenant) as c:
            ctx = self.actor_context(c, identity, tenant)
            projection, case, plan, _ = self.resolve(c, ctx, object_id, "list_human_advice_revisions")
            bound = hash_data(
                [
                    self.bound(c, ctx, ROUTE + "/" + selector(object_id) + "/revisions", projection),
                    str(plan["head_revision"]),
                ]
            ).hex()
            after = self.key(bound, cursor, number=True)
            rows = c.execute(
                "SELECT revision_id,revision_number,created_at FROM impact.object_revision "
                "WHERE tenant_id=%s AND object_id=%s AND object_type=%s AND restriction_state='AVAILABLE'"
                + (" AND revision_number<%s" if after else "")
                + " ORDER BY revision_number DESC LIMIT %s",
                [tenant, case["object_id"], KIND, *([after] if after else []), limit + 1],
            ).fetchall()
            page = rows[:limit]
            return {
                "object_id": selector(object_id),
                "items": [
                    {
                        "revision_id": str(row["revision_id"]),
                        "revision_number": row["revision_number"],
                        "saved_at": row["created_at"].isoformat(),
                    }
                    for row in page
                ],
                "next_cursor": self.service.next_cursor(bound, [page[-1]["revision_number"]])
                if len(rows) > limit
                else None,
            }

    def save(self, identity, tenant, body, correlation, object_id=None, action=None):
        validate_body(body, action)
        if (object_id is None) != (action is None):
            unavailable()
        name = operation(action)
        fingerprint = hash_data([name, object_id, body])
        now = datetime.now(timezone.utc)
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = self.actor_context(c, identity, tenant, writing=True)
            previous = None
            if action is None:
                anchor = selector(body["data"]["context_plan_id"])
                authorize(c, ctx, name, anchor, hidden=True)
                authorize(c, ctx, "get_ai_adoption_plan", anchor, hidden=True)
                plan = load(c, ctx, anchor, "AIAdoptionPlan", READ_CAP)
                # Check before receipt lookup too: an old receipt never restores
                # a case whose exact consent anchor has been withdrawn.
                self.require_available_anchor(c, ctx, anchor, body["data"]["context_plan_revision"])
            else:
                _, previous, plan, _ = self.resolve(c, ctx, object_id, name, writing=True)
                who = role(previous["payload"], ctx.principal_id)
                if (action in REQUESTER_ACTIONS) != (who == "REQUESTER"):
                    unavailable()
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, ctx.principal_id, name, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= now:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                self.resolve(c, ctx, old["outcome"]["object_id"], name)
                return old["outcome"]
            if previous:
                if str(previous["head_revision"]) != selector(body["expected_revision"]):
                    raise DomainError("CONFLICT_VERSION", 409)
                if action != "cancel":
                    if str(plan["head_revision"]) != previous["payload"]["context_plan_revision"]:
                        raise DomainError("CONFLICT_VERSION", 409, reason="ADVICE_CONTEXT_CHANGED")
                    self.current_participants(c, ctx, previous["payload"])
                    if previous["revision_number"] >= 200 and action != "close":
                        raise DomainError("LIMIT_EXCEEDED", 429, reason="HUMAN_ADVICE_REVISION_LIMIT")
                payload, state = transition(
                    previous["payload"],
                    previous["lifecycle_state"],
                    action,
                    body["data"],
                    ctx.principal_id,
                    previous["head_revision"],
                    now.isoformat(),
                    ctx.identity.auth_time.isoformat(),
                )
                receipt = write(c, ctx, KIND, payload, state, previous)
                c.execute(
                    "UPDATE impact.human_advice_case_current SET revision_id=%s,case_state=%s WHERE tenant_id=%s AND object_id=%s",
                    (receipt["revision_id"], state, tenant, object_id),
                )
            else:
                data = body["data"]
                if str(plan["head_revision"]) != selector(data["context_plan_revision"]):
                    raise DomainError("CONFLICT_VERSION", 409, reason="ADVICE_CONTEXT_CHANGED")
                requester = self.member(c, ctx, ctx.membership_id)
                if (
                    str(requester["principal_id"]) != ctx.principal_id
                    or str(requester["natural_id"]) != ctx.identity.natural_identity_id
                ):
                    unavailable()
                adviser = self.member(c, ctx, data["adviser_membership_id"])
                participants = {}
                for who, member in (("requester", requester), ("adviser", adviser)):
                    participants.update(
                        {
                            who + "_principal_id": str(member["principal_id"]),
                            who + "_membership_id": str(member["membership_id"]),
                            who + "_natural_id": str(member["natural_id"]),
                        }
                    )
                brief_nonce = str(uuid4())
                payload = initial_payload(data, participants, ctx.identity.auth_time.isoformat(), brief_nonce)
                self.current_participants(c, ctx, payload)
                count = c.execute(
                    "SELECT count(*) AS n FROM impact.human_advice_case_current WHERE tenant_id=%s AND requester_principal_id=%s",
                    (tenant, ctx.principal_id),
                ).fetchone()["n"]
                if count >= 100:
                    raise DomainError("LIMIT_EXCEEDED", 429, reason="HUMAN_ADVICE_CASE_LIMIT")
                obj = str(uuid4())
                # The participant projection comes first, so registry/revision
                # participant RLS has no permissive creation exception. Deferred
                # tenant-qualified FKs validate the actual final head at commit.
                c.execute(
                    "INSERT INTO impact.human_advice_case_current(tenant_id,object_id,revision_id,context_plan_id,context_plan_revision,requester_principal_id,requester_membership_id,requester_natural_id,adviser_principal_id,adviser_membership_id,adviser_natural_id,case_state) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'Open')",
                    (
                        tenant,
                        obj,
                        str(uuid4()),
                        data["context_plan_id"],
                        data["context_plan_revision"],
                        *[
                            participants[key]
                            for key in (
                                "requester_principal_id",
                                "requester_membership_id",
                                "requester_natural_id",
                                "adviser_principal_id",
                                "adviser_membership_id",
                                "adviser_natural_id",
                            )
                        ],
                    ),
                )
                receipt = write(c, ctx, KIND, payload, "Open", object_id=obj)
                c.execute(
                    "UPDATE impact.human_advice_case_current SET revision_id=%s WHERE tenant_id=%s AND object_id=%s",
                    (receipt["revision_id"], tenant, obj),
                )
                c.execute(
                    "INSERT INTO impact.human_advice_private_brief(tenant_id,object_id,problem,problem_sha256,brief_nonce) VALUES(%s,%s,%s,%s,%s)",
                    (tenant, obj, data["problem"], brief_digest(data["problem"], brief_nonce), brief_nonce),
                )
            receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
            audit(c, ctx, name, receipt, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    name,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(receipt),
                    now + timedelta(days=7),
                ),
            )
            return receipt
