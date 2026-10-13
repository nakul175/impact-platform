"""Traceable, review-only extraction proposals from clean UTF-8 evidence files."""

import re
from uuid import UUID, uuid4

from psycopg.types.json import Jsonb

from . import ai_policy
from .ai_safety import require_available
from .domain import DomainError
from .store import authorize, context, hash_data, load

USE_CASE = "EXTRACTION"
PURPOSE = "PROPOSAL_LOGFRAME_EXTRACTION"
FIELDS = {
    "title": "title",
    "start date": "start_date",
    "end date": "end_date",
    "target": "target",
    "population": "population",
}
REQUIRED = ("end_date", "target", "population")
LINE = re.compile(r"^\s*([A-Za-z][A-Za-z ]{0,40})\s*:\s*(.*?)\s*$")
HEADING = re.compile(r"^\s*(?:#{1,6}\s+|section\s*:\s*)(.+?)\s*$", re.I)


def extract_text(raw):
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise DomainError("VALIDATION_FAILED", 422, reason="AI_EXTRACTION_UTF8_REQUIRED") from None
    if len(text) > 1_000_000:
        raise DomainError("LIMIT_EXCEEDED", 422, reason="AI_EXTRACTION_TEXT_LIMIT")
    section = None
    proposals = []
    for number, line in enumerate(text.splitlines(), 1):
        heading = HEADING.fullmatch(line)
        if heading:
            section = heading.group(1)[:200]
            continue
        match = LINE.fullmatch(line)
        key = FIELDS.get(match.group(1).strip().casefold()) if match else None
        value = match.group(2).strip() if match else ""
        if key and value:
            proposals.append(
                {
                    "proposal_id": str(uuid4()),
                    "field_key": key,
                    "proposed_value": value[:2000],
                    "classification": "EXTRACTED",
                    "location": {"line": number, "section": section},
                    "evidence_span": line[:2200],
                }
            )
    values = {}
    for proposal in proposals:
        values.setdefault(proposal["field_key"], set()).add(proposal["proposed_value"])
    for proposal in proposals:
        proposal["conflict"] = len(values[proposal["field_key"]]) > 1
    return proposals, [field for field in REQUIRED if field not in values]


class AIExtraction:
    def __init__(self, service, destination, configuration):
        self.service = service
        self.destination = destination
        self.configuration = configuration

    def create(self, identity, tenant, body, correlation):
        source_id = UUID(body["source_object_id"])
        source_revision = UUID(body["source_revision_id"])
        fingerprint = hash_data(["create_ai_extraction", None, body])
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "create_ai_extraction", hidden=True)
            old = c.execute(
                "SELECT * FROM impact.ai_extraction_draft WHERE tenant_id=%s AND requested_by=%s AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["request_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return self._stored(c, old)
        artifact = self.service.evidence.content(identity, tenant, source_id, source_revision, correlation)
        if artifact["media_type"] != "text/plain":
            raise DomainError("VALIDATION_FAILED", 422, reason="AI_EXTRACTION_PROFILE_NOT_QUALIFIED")
        proposals, missing = extract_text(artifact["body"])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "create_ai_extraction", hidden=True)
            old = c.execute(
                "SELECT * FROM impact.ai_extraction_draft WHERE tenant_id=%s AND requested_by=%s AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["request_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return self._stored(c, old)
            source = load(c, ctx, source_id, "Evidence", "evidence.read")
            if str(source["head_revision"]) != str(source_revision):
                raise DomainError("CONFLICT_VERSION", 409, reason="AI_EXTRACTION_SOURCE_CHANGED")
            policy = ai_policy.in_force(c, tenant)
            ai_policy.require(
                policy,
                USE_CASE,
                body["policy_version"],
                source["classification"],
                self.destination,
                body["language"],
                (),
                PURPOSE,
            )
            require_available(c, tenant, USE_CASE, self.destination, self.configuration)
            draft_id = str(uuid4())
            c.execute(
                "INSERT INTO impact.ai_extraction_draft VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,statement_timestamp())",
                (
                    tenant,
                    draft_id,
                    source_id,
                    source_revision,
                    artifact["digest"],
                    body["policy_version"],
                    body["language"],
                    ctx.principal_id,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(missing),
                ),
            )
            for proposal in proposals:
                c.execute(
                    "INSERT INTO impact.ai_extraction_field VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        tenant,
                        draft_id,
                        proposal["proposal_id"],
                        proposal["field_key"],
                        proposal["proposed_value"],
                        proposal["classification"],
                        Jsonb(proposal["location"]),
                        proposal["evidence_span"],
                        proposal["conflict"],
                    ),
                )
            return self._view(draft_id, source_id, source_revision, proposals, missing)

    def apply(self, identity, tenant, draft, body):
        selected = {str(UUID(value)) for value in body["selected_proposal_ids"]}
        additions = body["human_additions"]
        fingerprint = hash_data(["review_ai_extraction", str(draft), body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "review_ai_extraction", hidden=True)
            replay = c.execute(
                "SELECT * FROM impact.ai_extraction_review WHERE tenant_id=%s AND reviewed_by=%s AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if replay:
                if bytes(replay["request_hash"]) != fingerprint or str(replay["draft_id"]) != str(draft):
                    raise DomainError("CONFLICT_OPERATION", 409)
                return self._review_view(replay)
            row = c.execute(
                "SELECT * FROM impact.ai_extraction_draft WHERE tenant_id=%s AND draft_id=%s FOR UPDATE",
                (tenant, draft),
            ).fetchone()
            if not row:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            if c.execute(
                "SELECT 1 FROM impact.ai_extraction_review WHERE tenant_id=%s AND draft_id=%s",
                (tenant, draft),
            ).fetchone():
                raise DomainError("CONFLICT_OPERATION", 409, reason="AI_EXTRACTION_ALREADY_REVIEWED")
            source = load(c, ctx, row["source_object_id"], "Evidence", "evidence.read")
            if str(source["head_revision"]) != str(row["source_revision_id"]):
                raise DomainError("CONFLICT_VERSION", 409, reason="AI_EXTRACTION_SOURCE_CHANGED")
            policy = ai_policy.in_force(c, tenant)
            if policy["version"] != row["policy_version"]:
                raise DomainError("CONFLICT_VERSION", 409, reason="AI_POLICY_CHANGED")
            require_available(c, tenant, USE_CASE, self.destination, self.configuration)
            fields = c.execute(
                "SELECT * FROM impact.ai_extraction_field WHERE tenant_id=%s AND draft_id=%s ORDER BY field_key,proposal_id",
                (tenant, draft),
            ).fetchall()
            known = {str(item["proposal_id"]) for item in fields}
            if not selected <= known:
                raise DomainError("VALIDATION_FAILED", 400, reason="AI_EXTRACTION_SELECTION_INVALID")
            accepted = {}
            for item in fields:
                if str(item["proposal_id"]) in selected:
                    if item["field_key"] in accepted:
                        raise DomainError(
                            "VALIDATION_FAILED", 400, reason="AI_EXTRACTION_CONFLICT_UNRESOLVED"
                        )
                    accepted[item["field_key"]] = {
                        "value": item["proposed_value"],
                        "classification": item["classification"],
                        "proposal_id": str(item["proposal_id"]),
                    }
            for addition in additions:
                if addition["field_key"] in accepted:
                    raise DomainError("VALIDATION_FAILED", 400, reason="AI_EXTRACTION_FIELD_DUPLICATED")
                accepted[addition["field_key"]] = {
                    "value": addition["value"],
                    "classification": "HUMAN_ADDED",
                    "rationale": addition["rationale"],
                }
            unresolved = [field for field in REQUIRED if field not in accepted]
            state = "READY_FOR_DOMAIN_DRAFT" if not unresolved else "BLOCKED"
            c.execute(
                "INSERT INTO impact.ai_extraction_review VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,statement_timestamp())",
                (
                    tenant,
                    draft,
                    Jsonb(sorted(selected)),
                    Jsonb(additions),
                    Jsonb(unresolved),
                    Jsonb(accepted),
                    ctx.principal_id,
                    body["operation_id"],
                    fingerprint,
                ),
            )
            return {
                "draft_id": str(draft),
                "state": state,
                "accepted_fields": accepted,
                "unresolved_fields": unresolved,
                "domain_objects_changed": False,
            }

    @staticmethod
    def _stored(c, row):
        proposals = []
        for item in c.execute(
            "SELECT * FROM impact.ai_extraction_field WHERE tenant_id=%s AND draft_id=%s ORDER BY field_key,proposal_id",
            (row["tenant_id"], row["draft_id"]),
        ).fetchall():
            proposals.append(
                {
                    "proposal_id": str(item["proposal_id"]),
                    "field_key": item["field_key"],
                    "proposed_value": item["proposed_value"],
                    "classification": item["classification"],
                    "location": item["source_location"],
                    "evidence_span": item["evidence_span"],
                    "conflict": item["conflict"],
                }
            )
        return AIExtraction._view(
            row["draft_id"],
            row["source_object_id"],
            row["source_revision_id"],
            proposals,
            row["missing_fields"],
        )

    @staticmethod
    def _review_view(row):
        unresolved = row["unresolved_fields"]
        return {
            "draft_id": str(row["draft_id"]),
            "state": "READY_FOR_DOMAIN_DRAFT" if not unresolved else "BLOCKED",
            "accepted_fields": row["accepted_fields"],
            "unresolved_fields": unresolved,
            "domain_objects_changed": False,
        }

    @staticmethod
    def _view(draft_id, source_id, source_revision, proposals, missing):
        return {
            "draft_id": str(draft_id),
            "source_object_id": str(source_id),
            "source_revision_id": str(source_revision),
            "proposals": proposals,
            "missing_fields": missing,
            "activation_blocked": bool(missing or any(item["conflict"] for item in proposals)),
            "domain_objects_changed": False,
        }
