"""FR-CAL-004 deterministic reach over permitted stable pseudonyms."""

from datetime import datetime, timedelta, timezone

from psycopg.types.json import Jsonb

from .contracts import validate
from .domain import DomainError, aware, unavailable
from .store import authorize, context, hash_data, load, write


def _revision(c, ctx, revision_id, kind, capability):
    row = c.execute(
        "SELECT * FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
        (ctx.tenant_id, revision_id),
    ).fetchone()
    if not row or row["object_type"] != kind or row["restriction_state"] != "AVAILABLE":
        unavailable()
    load(c, ctx, row["object_id"], kind, capability)
    return row


class PopulationOverlap:
    def __init__(self, service):
        self.service = service

    def compute(self, identity, tenant, body, correlation):
        validate("PopulationOverlapComputeRequest", body)
        fingerprint = hash_data(["compute_population_overlap", body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "compute_population_overlap", hidden=True)
            now = datetime.now(timezone.utc)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type='compute_population_overlap' AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= now:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                outcome = old["outcome"]
                load(c, ctx, outcome["result_id"], "PopulationReachResult")
                _revision(
                    c, ctx, outcome["scope_revision"], "PopulationMatchingScope", "calculated-results.read"
                )
                for source_revision in outcome["source_revisions"]:
                    _revision(c, ctx, source_revision, "Observation", "observations.read")
                return outcome
            scope_revision = _revision(
                c, ctx, body["scope_revision"], "PopulationMatchingScope", "calculated-results.read"
            )
            scope = load(
                c, ctx, scope_revision["object_id"], "PopulationMatchingScope", "calculated-results.read"
            )
            if (
                scope["lifecycle_state"] != "Approved"
                or str(scope["head_revision"]) != body["scope_revision"]
            ):
                raise DomainError("INVALID_STATE", 409, reason="CURRENT_APPROVED_MATCHING_SCOPE_REQUIRED")
            window_start = aware(scope_revision["payload"]["window_start"])
            window_end = aware(scope_revision["payload"]["window_end"])
            if window_start >= window_end:
                raise DomainError("VALIDATION_FAILED", reason="INVALID_TIME_WINDOW")

            identity_sets, gross, sources = [], 0, []
            for item in body["inputs"]:
                if item["project_id"] != scope_revision["payload"]["project_id"]:
                    raise DomainError("INCOMPATIBLE_MEASURE", reason="CROSS_PROJECT_MATCHING_REFUSED")
                source = _revision(c, ctx, item["source_revision"], "Observation", "observations.read")
                if source["payload"].get("approval_state") != "APPROVED":
                    raise DomainError("INVALID_STATE", 409, reason="APPROVED_SOURCE_REQUIRED")
                indicator = load(
                    c,
                    ctx,
                    source["payload"]["indicator_id"],
                    "IndicatorInstance",
                    "indicator-instances.read",
                )
                if str(indicator["payload"]["programme_id"]) != item["project_id"]:
                    raise DomainError("INCOMPATIBLE_MEASURE", reason="SOURCE_PROJECT_MISMATCH")
                event_at = source["payload"].get("event_at")
                if not event_at or not (window_start <= aware(event_at) < window_end):
                    raise DomainError("INCOMPATIBLE_MEASURE", reason="SOURCE_OUTSIDE_TIME_WINDOW")
                sources.append(str(source["revision_id"]))
                if item["input_mode"] == "IDENTITY_SET":
                    if "aggregate_count" in item or not item.get("stable_pseudonyms"):
                        raise DomainError("VALIDATION_FAILED", reason="EXACT_PSEUDONYMS_REQUIRED")
                    values = set(item["stable_pseudonyms"])
                    identity_sets.append(values)
                    gross += len(values)
                else:
                    if "stable_pseudonyms" in item or "aggregate_count" not in item:
                        raise DomainError("VALIDATION_FAILED", reason="AGGREGATE_COUNT_REQUIRED")
                    gross += item["aggregate_count"]

            if len(identity_sets) == len(body["inputs"]):
                union = set().union(*identity_sets)
                reach_kind, reach, overlap = "UNIQUE", len(union), gross - len(union)
            else:
                reach_kind, reach, overlap = "GROSS", gross, "UNKNOWN"
            recorded = write(
                c,
                ctx,
                "PopulationReachResult",
                {
                    "scope_revision": body["scope_revision"],
                    "reach_kind": reach_kind,
                    "reach": reach,
                    "matched_overlap": overlap,
                    "source_revisions": sources,
                },
                "Recorded",
                track_author=False,
            )
            response = {
                "result_id": str(recorded["object_id"]),
                "scope_revision": body["scope_revision"],
                "reach_kind": reach_kind,
                "reach": reach,
                "matched_overlap": overlap,
                "source_revisions": sources,
            }
            validate("PopulationOverlapResult", response)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,'compute_population_overlap',%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(response),
                    now + timedelta(days=7),
                ),
            )
            return response
