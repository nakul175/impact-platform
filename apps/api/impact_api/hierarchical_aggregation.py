"""FR-CAL-006 deterministic DAG validation and parent evaluation."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from psycopg.types.json import Jsonb

from .contracts import validate
from .domain import DomainError, decimal_value, stored, unavailable
from .store import authorize, context, hash_data, load, write


def validate_hierarchy(data):
    parents, children, rules = {}, set(), {}
    for edge in data["edges"]:
        if edge["parent"] == edge["child"]:
            raise DomainError("VALIDATION_FAILED", reason="CYCLIC_AGGREGATION")
        parents.setdefault(edge["child"], set()).add(edge["parent"])
        children.add(edge["child"])
        prior = rules.setdefault(edge["parent"], edge["combination_rule"])
        if prior != edge["combination_rule"]:
            raise DomainError("VALIDATION_FAILED", reason="MIXED_PARENT_RULES")
        if edge["combination_rule"] == "WEIGHTED":
            if edge.get("weight") is None:
                raise DomainError("VALIDATION_FAILED", reason="EXPLICIT_WEIGHT_REQUIRED")
        elif edge.get("weight") is not None:
            raise DomainError("VALIDATION_FAILED", reason="UNEXPECTED_WEIGHT")
    graph = {}
    for edge in data["edges"]:
        graph.setdefault(edge["parent"], []).append(edge["child"])
    seen, active = set(), set()

    def visit(node, depth=1):
        if depth > 100:
            raise DomainError("VALIDATION_FAILED", reason="HIERARCHY_DEPTH_EXCEEDED")
        if node in active:
            raise DomainError("VALIDATION_FAILED", reason="CYCLIC_AGGREGATION")
        if node in seen:
            return
        active.add(node)
        for child in graph.get(node, []):
            visit(child, depth + 1)
        active.remove(node)
        seen.add(node)

    visit(data["root_node"])
    if set(graph) | children != seen:
        raise DomainError("VALIDATION_FAILED", reason="DISCONNECTED_AGGREGATION")
    for parent, rule in rules.items():
        if rule == "WEIGHTED":
            weights = [decimal_value(e["weight"]) for e in data["edges"] if e["parent"] == parent]
            if any(weight < 0 for weight in weights) or sum(weights, Decimal(0)) != Decimal(1):
                raise DomainError("VALIDATION_FAILED", reason="WEIGHTS_NOT_RECONCILED")


def _revision(c, ctx, revision_id, kind, capability):
    row = c.execute(
        "SELECT * FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
        (ctx.tenant_id, revision_id),
    ).fetchone()
    if not row or row["object_type"] != kind or row["restriction_state"] != "AVAILABLE":
        unavailable()
    load(c, ctx, row["object_id"], kind, capability)
    return row


class HierarchicalAggregation:
    def __init__(self, service):
        self.service = service

    def compute(self, identity, tenant, body, correlation):
        validate("HierarchicalAggregationComputeRequest", body)
        fingerprint = hash_data(["compute_hierarchical_aggregation", body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "compute_hierarchical_aggregation", hidden=True)
            now = datetime.now(timezone.utc)
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,1))", (body["operation_id"],))
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type='compute_hierarchical_aggregation' AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                if old["expires_at"] <= now:
                    raise DomainError("IDEMPOTENCY_EXPIRED", 409)
                outcome = old["outcome"]
                load(c, ctx, outcome["result_id"], "HierarchicalAggregationResult")
                _revision(
                    c, ctx, outcome["hierarchy_revision"], "AggregationHierarchy", "calculated-results.read"
                )
                for source in outcome["source_revisions"]:
                    _revision(c, ctx, source, "CalculatedResult", "calculated-results.read")
                return outcome
            hierarchy_revision = _revision(
                c, ctx, body["hierarchy_revision"], "AggregationHierarchy", "calculated-results.read"
            )
            hierarchy = load(
                c, ctx, hierarchy_revision["object_id"], "AggregationHierarchy", "calculated-results.read"
            )
            if (
                hierarchy["lifecycle_state"] != "Approved"
                or str(hierarchy["head_revision"]) != body["hierarchy_revision"]
            ):
                raise DomainError("INVALID_STATE", 409, reason="CURRENT_APPROVED_HIERARCHY_REQUIRED")
            data = hierarchy_revision["payload"]
            validate_hierarchy(data)
            leaf_values = {}
            for item in body["contributions"]:
                source = _revision(
                    c, ctx, item["source_revision"], "CalculatedResult", "calculated-results.read"
                )
                if source["payload"].get("value_state") != "PRESENT":
                    raise DomainError("INCOMPATIBLE_MEASURE", reason="PRESENT_SOURCE_VALUE_REQUIRED")
                if source["payload"].get("unit") != data["unit"]:
                    raise DomainError("INCOMPATIBLE_MEASURE", reason="SOURCE_UNIT_MISMATCH")
                if decimal_value(source["payload"].get("value")) != decimal_value(item["value"]):
                    raise DomainError("INCOMPATIBLE_MEASURE", reason="SOURCE_VALUE_MISMATCH")
                key = (item["node"], str(source["revision_id"]))
                if key in leaf_values:
                    raise DomainError("VALIDATION_FAILED", reason="DUPLICATE_LEAF_CONTRIBUTION")
                leaf_values[key] = decimal_value(item["value"])
            edges_by_parent = {}
            for edge in data["edges"]:
                edges_by_parent.setdefault(edge["parent"], []).append(edge)

            def evaluate(node, depth=1):
                edges = edges_by_parent.get(node)
                if not edges:
                    rows = {source: value for (leaf, source), value in leaf_values.items() if leaf == node}
                    if not rows:
                        raise DomainError("VALIDATION_FAILED", reason="MISSING_LEAF_CONTRIBUTION")
                    return rows, depth
                accumulated, maximum = {}, depth
                for edge in edges:
                    values, child_depth = evaluate(edge["child"], depth + 1)
                    maximum = max(maximum, child_depth)
                    for source, value in values.items():
                        adjusted = (
                            value * decimal_value(edge["weight"])
                            if edge["combination_rule"] == "WEIGHTED"
                            else value
                        )
                        if source in accumulated and edge["combination_rule"] == "SUM":
                            raise DomainError("INCOMPATIBLE_MEASURE", reason="AMBIGUOUS_ADDITIVE_DUPLICATION")
                        if (
                            source in accumulated
                            and edge["combination_rule"] == "UNIQUE_UNION"
                            and accumulated[source] != adjusted
                        ):
                            raise DomainError("INCOMPATIBLE_MEASURE", reason="INCONSISTENT_UNIQUE_SOURCE")
                        accumulated[source] = (
                            accumulated.get(source, Decimal(0)) + adjusted
                            if edge["combination_rule"] == "WEIGHTED"
                            else adjusted
                        )
                return accumulated, maximum

            values, maximum_depth = evaluate(data["root_node"])
            if maximum_depth > 100:
                raise DomainError("VALIDATION_FAILED", reason="HIERARCHY_DEPTH_EXCEEDED")
            sources = sorted(values)
            total = stored(sum(values.values(), Decimal(0)))
            recorded = write(
                c,
                ctx,
                "HierarchicalAggregationResult",
                {
                    "hierarchy_revision": body["hierarchy_revision"],
                    "root_node": data["root_node"],
                    "value": total,
                    "maximum_depth": maximum_depth,
                    "source_revisions": sources,
                },
                "Recorded",
                track_author=False,
            )
            response = {
                "result_id": str(recorded["object_id"]),
                "hierarchy_revision": body["hierarchy_revision"],
                "root_node": data["root_node"],
                "value": total,
                "maximum_depth": maximum_depth,
                "source_revisions": sources,
            }
            validate("HierarchicalAggregationResult", response)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,'compute_hierarchical_aggregation',%s,%s,'SUCCEEDED',%s,%s)",
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
