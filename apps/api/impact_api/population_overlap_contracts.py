"""FR-CAL-004 contracts for governed population-overlap calculation."""

from copy import deepcopy

from .measurement_contracts import closed, text_field

VERSION = "1.60.0"
UUID = {"type": "string", "format": "uuid"}
ROOT = "population-matching-scopes"
COMPUTE = "population-overlap/compute"
IMPLEMENTED = [
    ("get", ROOT),
    ("post", ROOT),
    ("get", ROOT + "/{object_id}"),
    ("patch", ROOT + "/{object_id}"),
    ("post", ROOT + "/{object_id}/actions/submit"),
    ("post", COMPUTE),
]


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    scope = closed(
        {
            "title": text_field(200),
            "entity_type": text_field(80),
            "population": text_field(2000),
            "project_id": deepcopy(UUID),
            "window_start": {"type": "string", "format": "date-time"},
            "window_end": {"type": "string", "format": "date-time"},
            "matching_method": {"const": "EXACT_STABLE_PSEUDONYM"},
        },
        ["title", "entity_type", "population", "project_id", "window_start", "window_end", "matching_method"],
    )
    schemas["PopulationMatchingScopeData"] = scope
    schemas["PopulationMatchingScopeDraftData"] = deepcopy(scope)
    for suffix in ("", "List", "Create", "Patch"):
        schemas["PopulationMatchingScope" + suffix] = deepcopy(schemas["IndicatorDefinition" + suffix])
        schemas["PopulationMatchingScope" + suffix] = _replace_ref(
            schemas["PopulationMatchingScope" + suffix], "IndicatorDefinition", "PopulationMatchingScope"
        )
    schemas["PopulationOverlapInput"] = closed(
        {
            "source_revision": deepcopy(UUID),
            "project_id": deepcopy(UUID),
            "input_mode": {"enum": ["IDENTITY_SET", "AGGREGATE_ONLY"]},
            "stable_pseudonyms": {
                "type": "array",
                "maxItems": 10000,
                "uniqueItems": True,
                "items": {"type": "string", "pattern": "^[A-Za-z0-9_-]{16,128}$"},
            },
            "aggregate_count": {"type": "integer", "minimum": 0, "maximum": 1000000000},
        },
        ["source_revision", "project_id", "input_mode"],
    )
    schemas["PopulationOverlapComputeRequest"] = closed(
        {
            "operation_id": deepcopy(UUID),
            "scope_revision": deepcopy(UUID),
            "inputs": {
                "type": "array",
                "minItems": 2,
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/PopulationOverlapInput"},
            },
        },
        ["operation_id", "scope_revision", "inputs"],
    )
    schemas["PopulationOverlapResult"] = closed(
        {
            "result_id": deepcopy(UUID),
            "scope_revision": deepcopy(UUID),
            "reach_kind": {"enum": ["UNIQUE", "GROSS"]},
            "reach": {"type": "integer", "minimum": 0},
            "matched_overlap": {"oneOf": [{"type": "integer", "minimum": 0}, {"const": "UNKNOWN"}]},
            "source_revisions": {"type": "array", "minItems": 2, "maxItems": 100, "items": deepcopy(UUID)},
        },
        ["result_id", "scope_revision", "reach_kind", "reach", "matched_overlap", "source_revisions"],
    )

    prefix = "/v1/tenants/{tenant_id}/"
    for item in (False, True):
        suffix = "/{object_id}" if item else ""
        template = deepcopy(paths[prefix + "indicator-definitions" + suffix])
        template = _replace_ref(template, "IndicatorDefinition", "PopulationMatchingScope")
        methods = ("get", "patch") if item else ("get", "post")
        for method in methods:
            op = template[method]
            verb = (
                "get"
                if item and method == "get"
                else "list"
                if method == "get"
                else "patch"
                if item
                else "create"
            )
            op.update(
                operationId=verb + "_population_matching_scopes",
                **{"x-capability": "calculated-results.read", "x-contract-version": VERSION},
            )
        paths[prefix + ROOT + suffix] = template
    submit = deepcopy(paths[prefix + "indicator-definitions/{object_id}/actions/submit"])
    submit = _replace_ref(submit, "IndicatorDefinition", "PopulationMatchingScope")
    submit["post"].update(
        operationId="submit_population_matching_scope",
        **{"x-capability": "calculated-results.read", "x-contract-version": VERSION},
    )
    paths[prefix + ROOT + "/{object_id}/actions/submit"] = submit

    compute = deepcopy(paths[prefix + "recalculations"])
    op = compute["post"]
    op.update(
        operationId="compute_population_overlap",
        summary="Compute and record governed population overlap",
        **{"x-capability": "calculated-results.read", "x-contract-version": VERSION},
    )
    op["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/PopulationOverlapComputeRequest"
    }
    op["responses"].pop("202", None)
    op["responses"]["200"] = {
        "description": "Recorded population reach result",
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PopulationOverlapResult"}}},
    }
    paths[prefix + COMPUTE] = compute

    ids = (
        {paths[prefix + ROOT][m]["operationId"] for m in ("get", "post")}
        | {paths[prefix + ROOT + "/{object_id}"][m]["operationId"] for m in ("get", "patch")}
        | {"submit_population_matching_scope", "compute_population_overlap"}
    )
    policy["operations"] = [row for row in policy["operations"] if row["operation_id"] not in ids]
    for method, path in IMPLEMENTED:
        full = prefix + path
        operation = paths[full][method]["operationId"]
        policy["operations"].append(
            {
                "operation_id": operation,
                "method": method.upper(),
                "path": full,
                "capability": "calculated-results.read",
                "role_templates": ["MEL_ADMIN", "PROGRAMME_MANAGER", "ANALYST", "DATA_STEWARD"],
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": method != "get",
                "state_guard": "Exact tenant/project scope and approved current scope revision; no name or fuzzy matching.",
            }
        )


def _replace_ref(value, old, new):
    if isinstance(value, dict):
        return {key: _replace_ref(item, old, new) for key, item in value.items()}
    if isinstance(value, list):
        return [_replace_ref(item, old, new) for item in value]
    return value.replace(old, new) if isinstance(value, str) else value
