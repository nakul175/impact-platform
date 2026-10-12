"""FR-CAL-006 contracts for governed hierarchical aggregation."""

from copy import deepcopy

from .measurement_contracts import closed, text_field

VERSION = "1.61.0"
UUID = {"type": "string", "format": "uuid"}
NUMBER = {"type": "string", "pattern": r"^-?(0|[1-9][0-9]{0,25})(\.[0-9]{1,12})?$"}
ROOT = "aggregation-hierarchies"
COMPUTE = "hierarchical-aggregation/compute"
IMPLEMENTED = [
    ("get", ROOT),
    ("post", ROOT),
    ("get", ROOT + "/{object_id}"),
    ("patch", ROOT + "/{object_id}"),
    ("post", ROOT + "/{object_id}/actions/submit"),
    ("post", COMPUTE),
]


def _replace(value, old, new):
    if isinstance(value, dict):
        return {key: _replace(item, old, new) for key, item in value.items()}
    if isinstance(value, list):
        return [_replace(item, old, new) for item in value]
    return value.replace(old, new) if isinstance(value, str) else value


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    edge = closed(
        {
            "parent": text_field(80),
            "child": text_field(80),
            "contribution": {"enum": ["VALUE", "UNIQUE_SOURCE"]},
            "combination_rule": {"enum": ["SUM", "UNIQUE_UNION", "WEIGHTED"]},
            "attribution_scope": text_field(200),
            "weight": {"oneOf": [NUMBER, {"type": "null"}]},
        },
        ["parent", "child", "contribution", "combination_rule", "attribution_scope", "weight"],
    )
    data = closed(
        {
            "title": text_field(200),
            "unit": text_field(64),
            "root_node": text_field(80),
            "edges": {"type": "array", "minItems": 1, "maxItems": 5000, "items": edge},
        },
        ["title", "unit", "root_node", "edges"],
    )
    schemas["AggregationHierarchyData"] = data
    schemas["AggregationHierarchyDraftData"] = deepcopy(data)
    for suffix in ("", "List", "Create", "Patch"):
        schemas["AggregationHierarchy" + suffix] = _replace(
            deepcopy(schemas["IndicatorDefinition" + suffix]), "IndicatorDefinition", "AggregationHierarchy"
        )
    schemas["HierarchyLeafContribution"] = closed(
        {"node": text_field(80), "source_revision": deepcopy(UUID), "value": NUMBER},
        ["node", "source_revision", "value"],
    )
    schemas["HierarchicalAggregationComputeRequest"] = closed(
        {
            "operation_id": deepcopy(UUID),
            "hierarchy_revision": deepcopy(UUID),
            "contributions": {
                "type": "array",
                "minItems": 1,
                "maxItems": 10000,
                "items": {"$ref": "#/components/schemas/HierarchyLeafContribution"},
            },
        },
        ["operation_id", "hierarchy_revision", "contributions"],
    )
    schemas["HierarchicalAggregationResult"] = closed(
        {
            "result_id": deepcopy(UUID),
            "hierarchy_revision": deepcopy(UUID),
            "root_node": text_field(80),
            "value": NUMBER,
            "maximum_depth": {"type": "integer", "minimum": 1, "maximum": 100},
            "source_revisions": {
                "type": "array",
                "minItems": 1,
                "maxItems": 10000,
                "uniqueItems": True,
                "items": deepcopy(UUID),
            },
        },
        ["result_id", "hierarchy_revision", "root_node", "value", "maximum_depth", "source_revisions"],
    )
    prefix = "/v1/tenants/{tenant_id}/"
    for item in (False, True):
        suffix = "/{object_id}" if item else ""
        template = _replace(
            deepcopy(paths[prefix + "indicator-definitions" + suffix]),
            "IndicatorDefinition",
            "AggregationHierarchy",
        )
        for method in ("get", "patch") if item else ("get", "post"):
            verb = (
                "get"
                if item and method == "get"
                else "list"
                if method == "get"
                else "patch"
                if item
                else "create"
            )
            template[method].update(
                operationId=verb + "_aggregation_hierarchies",
                **{"x-capability": "calculated-results.read", "x-contract-version": VERSION},
            )
        paths[prefix + ROOT + suffix] = template
    submit = _replace(
        deepcopy(paths[prefix + "indicator-definitions/{object_id}/actions/submit"]),
        "IndicatorDefinition",
        "AggregationHierarchy",
    )
    submit["post"].update(
        operationId="submit_aggregation_hierarchy",
        **{"x-capability": "calculated-results.read", "x-contract-version": VERSION},
    )
    paths[prefix + ROOT + "/{object_id}/actions/submit"] = submit
    compute = deepcopy(paths[prefix + "recalculations"])
    op = compute["post"]
    op.update(
        operationId="compute_hierarchical_aggregation",
        summary="Compute and record a governed aggregation hierarchy",
        **{"x-capability": "calculated-results.read", "x-contract-version": VERSION},
    )
    op["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/HierarchicalAggregationComputeRequest"
    }
    op["responses"].pop("202", None)
    op["responses"]["200"] = {
        "description": "Recorded hierarchical aggregate",
        "content": {
            "application/json": {"schema": {"$ref": "#/components/schemas/HierarchicalAggregationResult"}}
        },
    }
    paths[prefix + COMPUTE] = compute
    ids = (
        {paths[prefix + ROOT][m]["operationId"] for m in ("get", "post")}
        | {paths[prefix + ROOT + "/{object_id}"][m]["operationId"] for m in ("get", "patch")}
        | {"submit_aggregation_hierarchy", "compute_hierarchical_aggregation"}
    )
    policy["operations"] = [row for row in policy["operations"] if row["operation_id"] not in ids]
    for method, path in IMPLEMENTED:
        full = prefix + path
        policy["operations"].append(
            {
                "operation_id": paths[full][method]["operationId"],
                "method": method.upper(),
                "path": full,
                "capability": "calculated-results.read",
                "role_templates": ["MEL_ADMIN", "PROGRAMME_MANAGER", "ANALYST", "DATA_STEWARD"],
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": method != "get",
                "state_guard": "Acyclic explicit edges; unique unions deduplicate exact sources; additive duplicates and unreconciled weights are refused.",
            }
        )
