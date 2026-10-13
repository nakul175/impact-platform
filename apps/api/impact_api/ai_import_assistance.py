"""Non-destructive import mapping and deterministic cleaning proposals."""

import json
import re
from datetime import datetime, timedelta, timezone
from uuid import NAMESPACE_URL, uuid5

from psycopg.types.json import Jsonb

from . import ai_policy
from .ai_safety import require_available
from .domain import DomainError
from .imports import parse
from .store import audit, authorize, context, hash_data, load

USE_CASE = "IMPORT_CLEANING"
PURPOSE = "IMPORT_MAPPING_ASSISTANCE"
SAMPLE_LIMIT = 5


def normal(value):
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def proposal_id(batch, revision, kind, key):
    return str(uuid5(NAMESPACE_URL, f"imprana:{batch}:{revision}:{kind}:{key}"))


class AIImportAssistance:
    def __init__(self, service, destination, configuration):
        self.service = service
        self.destination = destination
        self.configuration = configuration

    def _source(self, c, ctx, batch, revision):
        row = load(c, ctx, batch, "ImportJob", "imports.read")
        if str(row["head_revision"]) != str(revision) or row["lifecycle_state"] not in {
            "Draft",
            "Previewed",
        }:
            raise DomainError("CONFLICT_VERSION", 409, reason="IMPORT_DRAFT_CHANGED")
        return row

    def _policy(self, c, tenant, body, classification):
        policy = ai_policy.in_force(c, tenant)
        ai_policy.require(
            policy,
            USE_CASE,
            body["policy_version"],
            classification,
            self.destination,
            body["language"],
            (),
            PURPOSE,
        )
        require_available(c, tenant, USE_CASE, self.destination, self.configuration)

    def _proposals(self, c, ctx, row):
        payload = row["payload"]
        sheet = parse(payload)
        if not sheet.rows:
            raise DomainError("VALIDATION_FAILED", 422, reason="IMPORT_EMPTY")
        headers = sheet.rows[0]
        if len(set(headers)) != len(headers):
            raise DomainError("VALIDATION_FAILED", 422, reason="HEADER_DUPLICATE")
        indicators = c.execute(
            "SELECT i.object_id,r.classification,d.payload FROM impact.indicator_instance_current i "
            "JOIN impact.object_registry r ON r.tenant_id=i.tenant_id AND r.object_id=i.object_id "
            "JOIN impact.object_revision cur ON cur.tenant_id=r.tenant_id "
            "AND cur.revision_id=r.head_revision "
            "JOIN impact.object_revision d ON d.tenant_id=i.tenant_id AND d.revision_id=i.definition_version "
            "WHERE i.tenant_id=%s AND i.programme_id=%s AND r.lifecycle_state='Active' "
            "AND r.classification<>'RESTRICTED' AND cur.restriction_state='AVAILABLE' "
            "AND d.restriction_state='AVAILABLE' ORDER BY i.object_id",
            (ctx.tenant_id, payload["programme_id"]),
        ).fetchall()
        suggestions = []
        for header_index, header in enumerate(headers):
            key = normal(header)
            matches = [
                item
                for item in indicators
                if key
                and key
                in {
                    normal(item["payload"].get("code", "")),
                    normal(item["payload"].get("name", "")),
                }
                and item["payload"].get("measurement_type") not in {"RATIO", "PERCENTAGE"}
            ]
            for item in matches:
                definition = item["payload"]
                suggestions.append(
                    {
                        "proposal_id": proposal_id(
                            row["object_id"], row["head_revision"], "MAP", header + str(item["object_id"])
                        ),
                        "kind": "MAP_COLUMN",
                        "source_column": header,
                        "destination": {
                            "indicator_id": str(item["object_id"]),
                            "value_role": "VALUE",
                            "unit": definition["unit"],
                        },
                        "confidence": "EXACT" if len(matches) == 1 else "AMBIGUOUS",
                        "selected": False,
                        "affected_samples": [
                            {
                                "row_number": number + 2,
                                "before": values[header_index],
                                "after": values[header_index],
                            }
                            for number, values in enumerate(sheet.rows[1 : SAMPLE_LIMIT + 1])
                            if header_index < len(values)
                        ],
                    }
                )
        mapping = payload.get("mapping") or {}
        date_column = mapping.get("event_at_column")
        if date_column in headers:
            index = headers.index(date_column)
            samples = [
                row[index] for row in sheet.rows[1 : SAMPLE_LIMIT + 1] if index < len(row) and row[index]
            ]
            formats = []
            if samples and all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) for value in samples):
                formats = [("YYYY-MM-DD", "EXACT")]
            elif samples and all(re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", value) for value in samples):
                formats = [("DD/MM/YYYY", "AMBIGUOUS"), ("MM/DD/YYYY", "AMBIGUOUS")]
            for pattern, confidence in formats:
                suggestions.append(
                    {
                        "proposal_id": proposal_id(row["object_id"], row["head_revision"], "DATE", pattern),
                        "kind": "SET_DATE_PATTERN",
                        "source_column": date_column,
                        "destination": {"date_pattern": pattern},
                        "confidence": confidence,
                        "selected": False,
                        "affected_samples": [
                            {"row_number": number + 2, "before": value, "after": value}
                            for number, value in enumerate(samples)
                        ],
                    }
                )
        classification = max(
            [row["classification"], *(item["classification"] for item in indicators)],
            key=ai_policy.CLASS_RANK.get,
        )
        return suggestions[:200], classification

    def propose(self, identity, tenant, batch, revision, body):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "create_ai_import_proposals", batch, hidden=True)
            authorize(c, ctx, "list_indicator_instances", hidden=True)
            row = self._source(c, ctx, batch, revision)
            items, classification = self._proposals(c, ctx, row)
            self._policy(c, tenant, body, classification)
            return {
                "batch_id": str(batch),
                "batch_revision_id": str(revision),
                "raw_sha256": row["payload"].get("content_sha256"),
                "current_mapping": row["payload"].get("mapping"),
                "proposals": items,
                "destructive_actions_available": False,
            }

    def apply(self, identity, tenant, batch, revision, body, correlation):
        fingerprint = hash_data(["apply_ai_import_proposals", str(batch), body])
        now = datetime.now(timezone.utc)
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "apply_ai_import_proposals", batch, hidden=True)
            authorize(c, ctx, "patch_imports", batch, hidden=True)
            authorize(c, ctx, "list_indicator_instances", hidden=True)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s "
                "AND command_type='apply_ai_import_proposals' AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= now:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                load(c, ctx, old["outcome"]["object_id"], "ImportJob")
                return old["outcome"]
            row = self._source(c, ctx, batch, revision)
            proposal_items, classification = self._proposals(c, ctx, row)
            self._policy(c, tenant, body, classification)
            proposals = {item["proposal_id"]: item for item in proposal_items}
            selected = body["selected_proposal_ids"]
            if any(item not in proposals for item in selected):
                raise DomainError("VALIDATION_FAILED", 400, reason="IMPORT_PROPOSAL_SELECTION_INVALID")
            patch = {}
            before = json.loads(json.dumps(row["payload"].get("mapping") or {}))
            mapping = json.loads(json.dumps(before))
            mapping.setdefault("columns", [])
            for identifier in selected:
                item = proposals[identifier]
                if item["kind"] == "MAP_COLUMN":
                    binding = {"column": item["source_column"], **item["destination"]}
                    mapping["columns"] = [
                        existing for existing in mapping["columns"] if existing["column"] != binding["column"]
                    ] + [binding]
                elif item["kind"] == "SET_DATE_PATTERN":
                    patch["date_pattern"] = item["destination"]["date_pattern"]
            patch["mapping"] = mapping
            receipt = self.service.imports.save(c, ctx, row, patch)
            receipt.update(
                operation_id=body["operation_id"],
                correlation_id=correlation,
                raw_sha256=row["payload"].get("content_sha256"),
                mapping_diff={"before": before, "after": mapping},
                applied_proposal_ids=selected,
                raw_rows_changed=False,
                identities_merged=False,
                approved_actuals_changed=False,
            )
            audit(c, ctx, "apply_ai_import_proposals", receipt, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,'apply_ai_import_proposals',%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(receipt),
                    now + timedelta(days=7),
                ),
            )
            return receipt
