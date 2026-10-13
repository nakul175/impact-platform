"""FR-CAL-007 contracts for governed dimension crosswalks and previews."""

from copy import deepcopy

from .measurement_contracts import closed, text_field

VERSION = "1.62.0"
UUID = {"type": "string", "format": "uuid"}
NUMBER = {"type": "string", "pattern": r"^-?(0|[1-9][0-9]{0,25})(\.[0-9]{1,12})?$"}
ROOT = "dimension-crosswalks"
PREVIEW = ROOT + "/{object_id}/preview"
IMPLEMENTED = [
    ("get", ROOT),
    ("post", ROOT),
    ("get", ROOT + "/{object_id}"),
    ("patch", ROOT + "/{object_id}"),
    ("post", ROOT + "/{object_id}/actions/submit"),
    ("post", PREVIEW),
]


def _replace(value, old, new):
    if isinstance(value, dict):
        return {k: _replace(v, old, new) for k, v in value.items()}
    if isinstance(value, list):
        return [_replace(v, old, new) for v in value]
    return value.replace(old, new) if isinstance(value, str) else value


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    mapping = closed(
        {
            "source_category": text_field(32),
            "target_category": text_field(32),
            "weight": {"oneOf": [NUMBER, {"type": "null"}]},
            "suppressed": {"type": "boolean"},
        },
        ["source_category", "target_category", "weight", "suppressed"],
    )
    data = closed(
        {
            "title": text_field(200),
            "source_definition_revision": deepcopy(UUID),
            "source_dimension_code": text_field(64),
            "target_definition_revision": deepcopy(UUID),
            "target_dimension_code": text_field(64),
            "mapping_type": {"enum": ["EXACT", "MANY_TO_ONE", "PROPORTIONAL"]},
            "information_loss": {"enum": ["NONE", "POOLING", "ESTIMATED"]},
            "estimation_method": {"type": ["string", "null"], "maxLength": 1000},
            "mappings": {"type": "array", "minItems": 1, "maxItems": 500, "items": mapping},
        },
        [
            "title",
            "source_definition_revision",
            "source_dimension_code",
            "target_definition_revision",
            "target_dimension_code",
            "mapping_type",
            "information_loss",
            "estimation_method",
            "mappings",
        ],
    )
    schemas["DimensionCrosswalkData"] = data
    schemas["DimensionCrosswalkDraftData"] = deepcopy(data)
    for suffix in ("", "List", "Create", "Patch"):
        schemas["DimensionCrosswalk" + suffix] = _replace(
            deepcopy(schemas["IndicatorDefinition" + suffix]), "IndicatorDefinition", "DimensionCrosswalk"
        )
    schemas["DimensionCrosswalkPreviewInput"] = closed(
        {"source_category": text_field(32), "value": NUMBER}, ["source_category", "value"]
    )
    schemas["DimensionCrosswalkPreviewRequest"] = closed(
        {
            "crosswalk_revision": deepcopy(UUID),
            "inputs": {
                "type": "array",
                "minItems": 1,
                "maxItems": 500,
                "items": {"$ref": "#/components/schemas/DimensionCrosswalkPreviewInput"},
            },
        },
        ["crosswalk_revision", "inputs"],
    )
    schemas["DimensionCrosswalkPreviewValue"] = closed(
        {"target_category": text_field(32), "value": NUMBER}, ["target_category", "value"]
    )
    schemas["DimensionCrosswalkPreview"] = closed(
        {
            "crosswalk_revision": deepcopy(UUID),
            "mapping_type": {"enum": ["EXACT", "MANY_TO_ONE", "PROPORTIONAL"]},
            "information_loss": {"enum": ["NONE", "POOLING", "ESTIMATED"]},
            "mapped": {
                "type": "array",
                "maxItems": 500,
                "items": {"$ref": "#/components/schemas/DimensionCrosswalkPreviewValue"},
            },
            "unmapped_source_categories": {
                "type": "array",
                "maxItems": 500,
                "uniqueItems": True,
                "items": text_field(32),
            },
            "suppressed_source_categories": {
                "type": "array",
                "maxItems": 500,
                "uniqueItems": True,
                "items": text_field(32),
            },
        },
        [
            "crosswalk_revision",
            "mapping_type",
            "information_loss",
            "mapped",
            "unmapped_source_categories",
            "suppressed_source_categories",
        ],
    )
    prefix = "/v1/tenants/{tenant_id}/"
    for item in (False, True):
        suffix = "/{object_id}" if item else ""
        template = _replace(
            deepcopy(paths[prefix + "indicator-definitions" + suffix]),
            "IndicatorDefinition",
            "DimensionCrosswalk",
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
                operationId=verb + "_dimension_crosswalks",
                **{"x-capability": "calculated-results.read", "x-contract-version": VERSION},
            )
        paths[prefix + ROOT + suffix] = template
    submit = _replace(
        deepcopy(paths[prefix + "indicator-definitions/{object_id}/actions/submit"]),
        "IndicatorDefinition",
        "DimensionCrosswalk",
    )
    submit["post"].update(
        operationId="submit_dimension_crosswalk",
        **{"x-capability": "calculated-results.read", "x-contract-version": VERSION},
    )
    paths[prefix + ROOT + "/{object_id}/actions/submit"] = submit
    preview = deepcopy(paths[prefix + "recalculations"])
    preview["parameters"] = deepcopy(paths[prefix + "indicator-definitions/{object_id}"]["parameters"])
    op = preview["post"]
    op.update(
        operationId="preview_dimension_crosswalk",
        summary="Preview mapped, unmapped and suppressed dimension contributions",
        **{"x-capability": "calculated-results.read", "x-contract-version": VERSION},
    )
    op["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/DimensionCrosswalkPreviewRequest"
    }
    op["responses"].pop("202", None)
    op["responses"]["200"] = {
        "description": "Crosswalk preview with explicit gaps",
        "content": {
            "application/json": {"schema": {"$ref": "#/components/schemas/DimensionCrosswalkPreview"}}
        },
    }
    paths[prefix + PREVIEW] = preview
    ids = (
        {paths[prefix + ROOT][m]["operationId"] for m in ("get", "post")}
        | {paths[prefix + ROOT + "/{object_id}"][m]["operationId"] for m in ("get", "patch")}
        | {"submit_dimension_crosswalk", "preview_dimension_crosswalk"}
    )
    policy["operations"] = [r for r in policy["operations"] if r["operation_id"] not in ids]
    for method, path in IMPLEMENTED:
        full = prefix + path
        policy["operations"].append(
            {
                "operation_id": paths[full][method]["operationId"],
                "method": method.upper(),
                "path": full,
                "capability": "calculated-results.read",
                "role_templates": ["DATA_STEWARD", "MEL_ADMIN", "ANALYST"],
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": method != "get",
                "state_guard": "Exact approved definition revisions and category codes; broad-to-narrow splits require explicit proportional estimation; unknown never silently remaps.",
            }
        )
