"""Inspectable draft-only AI proposals confirmed through ordinary commands."""

from uuid import UUID, uuid4

from psycopg.types.json import Jsonb

from . import ai_policy
from .ai_safety import require_available
from .domain import DomainError
from .service import revision
from .store import authorize, context, hash_data, load

USE_CASE = "ACTION_PROPOSAL"
PURPOSE = "ACTION_PROPOSAL_GENERATION"
COMMAND = "CREATE_WORK_ITEM_DRAFT"


class AIActionProposals:
    def __init__(self, service, destination, configuration):
        self.service = service
        self.destination = destination
        self.configuration = configuration

    def create(self, identity, tenant, body):
        fingerprint = hash_data(["create_ai_action_proposal", body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "create_ai_action_proposal", hidden=True)
            replay = c.execute(
                "SELECT * FROM impact.ai_action_proposal WHERE tenant_id=%s AND generated_by=%s AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if replay:
                if bytes(replay["request_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return self._view(c, replay)
            if body["command_type"] != COMMAND:
                raise DomainError("VALIDATION_FAILED", reason="AI_PROTECTED_COMMAND_REFUSED")
            scope = revision(c, ctx, body["scope_revision_id"], "Programme", "programmes.read")
            if str(scope["object_id"]) != body["scope_object_id"]:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            head = load(c, ctx, body["scope_object_id"], "Programme", "programmes.read")
            if str(head["head_revision"]) != body["scope_revision_id"]:
                raise DomainError("CONFLICT_VERSION", 409, reason="ACTION_PROPOSAL_SCOPE_CHANGED")
            if body["after_values"].get("programme_id") != body["scope_object_id"]:
                raise DomainError("VALIDATION_FAILED", reason="ACTION_PROPOSAL_SCOPE_MISMATCH")
            sources = self._sources(c, ctx, body["affected_versions"])
            highest = max(
                [head["classification"], *(row["classification"] for row in sources)],
                key=["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"].index,
            )
            policy = ai_policy.in_force(c, tenant)
            ai_policy.require(
                policy,
                USE_CASE,
                body["policy_version"],
                highest,
                self.destination,
                body["language"],
                (),
                PURPOSE,
            )
            require_available(c, tenant, USE_CASE, self.destination, self.configuration)
            self.service.validate_data(c, ctx, "WorkItem", body["after_values"], ctx.principal_id)
            row = c.execute(
                "INSERT INTO impact.ai_action_proposal VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,statement_timestamp()) RETURNING *",
                (
                    tenant,
                    uuid4(),
                    COMMAND,
                    UUID(body["scope_object_id"]),
                    UUID(body["scope_revision_id"]),
                    Jsonb(None),
                    Jsonb(body["after_values"]),
                    Jsonb(body["consequences"]),
                    body["policy_version"],
                    uuid4(),
                    ctx.principal_id,
                    UUID(body["operation_id"]),
                    fingerprint,
                ),
            ).fetchone()
            for selector in body["affected_versions"]:
                c.execute(
                    "INSERT INTO impact.ai_action_proposal_source VALUES(%s,%s,%s,%s,%s)",
                    (
                        tenant,
                        row["proposal_id"],
                        selector["object_id"],
                        selector["revision_id"],
                        selector["object_type"],
                    ),
                )
            return self._view(c, row)

    def confirm(self, identity, tenant, proposal_id, body, correlation):
        fingerprint = hash_data(["confirm_ai_action_proposal", str(proposal_id), body])
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "confirm_ai_action_proposal", hidden=True)
            replay = c.execute(
                "SELECT * FROM impact.ai_action_confirmation WHERE tenant_id=%s AND confirmed_by=%s AND confirmation_operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if replay:
                if bytes(replay["confirmation_hash"]) != fingerprint or str(replay["proposal_id"]) != str(
                    proposal_id
                ):
                    raise DomainError("CONFLICT_OPERATION", 409)
                load(c, ctx, replay["outcome_object_id"], "WorkItem", "work-items.read")
                return self._confirmation_view(replay)

        def precondition(c, ctx):
            authorize(c, ctx, "confirm_ai_action_proposal", hidden=True)
            proposal = c.execute(
                "SELECT * FROM impact.ai_action_proposal WHERE tenant_id=%s AND proposal_id=%s FOR UPDATE",
                (tenant, proposal_id),
            ).fetchone()
            if not proposal:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            if c.execute(
                "SELECT 1 FROM impact.ai_action_confirmation WHERE tenant_id=%s AND proposal_id=%s",
                (tenant, proposal_id),
            ).fetchone():
                raise DomainError("CONFLICT_OPERATION", 409, reason="ACTION_PROPOSAL_ALREADY_CONFIRMED")
            head = load(c, ctx, proposal["scope_object_id"], "Programme", "programmes.read")
            if str(head["head_revision"]) != str(proposal["scope_revision_id"]):
                raise DomainError("CONFLICT_VERSION", 409, reason="ACTION_PROPOSAL_STALE")
            selectors = c.execute(
                "SELECT object_id,revision_id,object_type FROM impact.ai_action_proposal_source WHERE tenant_id=%s AND proposal_id=%s ORDER BY revision_id",
                (tenant, proposal_id),
            ).fetchall()
            sources = self._sources(c, ctx, selectors)
            highest = max(
                [head["classification"], *(row["classification"] for row in sources)],
                key=["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"].index,
            )
            policy = ai_policy.in_force(c, tenant)
            ai_policy.require(
                policy,
                USE_CASE,
                proposal["policy_version"],
                highest,
                self.destination,
                body["language"],
                (),
                PURPOSE,
            )
            require_available(c, tenant, USE_CASE, self.destination, self.configuration)

        def postcondition(c, ctx, receipt):
            c.execute(
                "INSERT INTO impact.ai_action_confirmation VALUES(%s,%s,%s,%s,%s,%s,%s,statement_timestamp())",
                (
                    tenant,
                    proposal_id,
                    UUID(body["operation_id"]),
                    fingerprint,
                    ctx.principal_id,
                    receipt["object_id"],
                    receipt["revision_id"],
                ),
            )

        proposal = self._proposal_for_execution(identity, tenant, proposal_id)
        outcome = self.service.command(
            identity,
            tenant,
            "work-items",
            {"operation_id": str(proposal["execution_operation_id"]), "data": proposal["after_values"]},
            correlation,
            precondition=precondition,
            postcondition=postcondition,
        )
        return {
            "proposal_id": str(proposal_id),
            "outcome_object_id": outcome["object_id"],
            "outcome_revision_id": outcome["revision_id"],
            "ordinary_command": "create_work_items",
            "protected_write": False,
        }

    def _proposal_for_execution(self, identity, tenant, proposal_id):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "confirm_ai_action_proposal", hidden=True)
            row = c.execute(
                "SELECT * FROM impact.ai_action_proposal WHERE tenant_id=%s AND proposal_id=%s",
                (tenant, proposal_id),
            ).fetchone()
            if not row:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            return row

    @staticmethod
    def _sources(c, ctx, selectors):
        seen, rows = set(), []
        mapping = {"Evidence": "evidence.read", "CalculatedResult": "calculated-results.read"}
        for selector in selectors:
            revision_id = str(selector["revision_id"])
            if revision_id in seen or selector["object_type"] not in mapping:
                raise DomainError("VALIDATION_FAILED", reason="ACTION_PROPOSAL_SOURCE_INVALID")
            seen.add(revision_id)
            row = revision(
                c,
                ctx,
                revision_id,
                selector["object_type"],
                mapping[selector["object_type"]],
            )
            if str(row["object_id"]) != str(selector["object_id"]):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            head = load(c, ctx, row["object_id"], selector["object_type"], mapping[selector["object_type"]])
            if str(head["head_revision"]) != revision_id:
                raise DomainError("CONFLICT_VERSION", 409, reason="ACTION_PROPOSAL_SOURCE_CHANGED")
            rows.append(row)
        return rows

    @staticmethod
    def _view(c, row):
        sources = c.execute(
            "SELECT object_id,revision_id,object_type FROM impact.ai_action_proposal_source WHERE tenant_id=%s AND proposal_id=%s ORDER BY revision_id",
            (row["tenant_id"], row["proposal_id"]),
        ).fetchall()
        return {
            "proposal_id": str(row["proposal_id"]),
            "command_type": row["command_type"],
            "scope_object_id": str(row["scope_object_id"]),
            "scope_revision_id": str(row["scope_revision_id"]),
            "before_values": row["before_values"],
            "after_values": row["after_values"],
            "affected_versions": [
                {key: str(item[key]) for key in ("object_id", "revision_id", "object_type")}
                for item in sources
            ],
            "policy_version": row["policy_version"],
            "consequences": row["consequences"],
            "confirmation_required": True,
            "domain_side_effects_created": False,
        }

    @staticmethod
    def _confirmation_view(row):
        return {
            "proposal_id": str(row["proposal_id"]),
            "outcome_object_id": str(row["outcome_object_id"]),
            "outcome_revision_id": str(row["outcome_revision_id"]),
            "ordinary_command": "create_work_items",
            "protected_write": False,
        }
