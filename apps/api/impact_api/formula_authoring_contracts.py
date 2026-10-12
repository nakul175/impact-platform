"""FR-CAL-012 closed typed formula AST and preview contracts."""

from copy import deepcopy
from .measurement_contracts import closed, text_field

VERSION = "1.63.0"
UUID = {"type": "string", "format": "uuid"}
NUMBER = {"type": "string", "pattern": r"^-?(0|[1-9][0-9]{0,25})(\.[0-9]{1,12})?$"}
ROOT = "formula-definitions"
PREVIEW = ROOT + "/preview"
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
    node_ref = {"$ref": "#/components/schemas/FormulaNode"}
    schemas["FormulaNode"] = {
        "oneOf": [
            closed(
                {"kind": {"const": "LITERAL"}, "value": NUMBER, "unit": text_field(64)},
                ["kind", "value", "unit"],
            ),
            closed(
                {"kind": {"const": "REFERENCE"}, "definition_revision": deepcopy(UUID)},
                ["kind", "definition_revision"],
            ),
            closed(
                {
                    "kind": {"const": "FILTER"},
                    "definition_revision": deepcopy(UUID),
                    "dimension_code": text_field(64),
                    "category_code": text_field(32),
                },
                ["kind", "definition_revision", "dimension_code", "category_code"],
            ),
            closed(
                {
                    "kind": {"const": "CALL"},
                    "function": {
                        "enum": [
                            "ADD",
                            "SUB",
                            "MUL",
                            "DIV",
                            "COUNT",
                            "SUM",
                            "MIN",
                            "MAX",
                            "RATIO",
                            "ELIGIBLE_DISTINCT",
                        ]
                    },
                    "args": {"type": "array", "minItems": 1, "maxItems": 20, "items": node_ref},
                },
                ["kind", "function", "args"],
            ),
        ]
    }
    data = closed(
        {
            "title": text_field(200),
            "target_definition_id": deepcopy(UUID),
            "output_unit": text_field(64),
            "ast": node_ref,
        },
        ["title", "target_definition_id", "output_unit", "ast"],
    )
    schemas["FormulaDefinitionData"] = data
    schemas["FormulaDefinitionDraftData"] = deepcopy(data)
    for suffix in ("", "List", "Create", "Patch"):
        schemas["FormulaDefinition" + suffix] = _replace(
            deepcopy(schemas["IndicatorDefinition" + suffix]), "IndicatorDefinition", "FormulaDefinition"
        )
    dimensions = {
        "type": "object",
        "maxProperties": 5,
        "propertyNames": {"pattern": "^[A-Za-z][A-Za-z0-9_-]{0,63}$"},
        "additionalProperties": text_field(32),
    }
    schemas["FormulaSampleValue"] = closed(
        {
            "value": NUMBER,
            "eligible": {"type": "boolean"},
            "distinct_key": {"type": ["string", "null"], "maxLength": 200},
            "dimensions": dimensions,
        },
        ["value", "eligible", "distinct_key", "dimensions"],
    )
    schemas["FormulaSampleReference"] = closed(
        {
            "definition_revision": deepcopy(UUID),
            "values": {
                "type": "array",
                "maxItems": 1000,
                "items": {"$ref": "#/components/schemas/FormulaSampleValue"},
            },
        },
        ["definition_revision", "values"],
    )
    schemas["FormulaPreviewRequest"] = closed(
        {
            "data": {"$ref": "#/components/schemas/FormulaDefinitionDraftData"},
            "samples": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/FormulaSampleReference"},
            },
        },
        ["data", "samples"],
    )
    schemas["FormulaPreview"] = closed(
        {
            "output_unit": text_field(64),
            "value_state": {"enum": ["PRESENT", "MISSING", "UNDEFINED"]},
            "value": {"oneOf": [NUMBER, {"type": "null"}]},
            "referenced_definition_revisions": {
                "type": "array",
                "maxItems": 100,
                "uniqueItems": True,
                "items": deepcopy(UUID),
            },
        },
        ["output_unit", "value_state", "value", "referenced_definition_revisions"],
    )
    prefix = "/v1/tenants/{tenant_id}/"
    for item in (False, True):
        suffix = "/{object_id}" if item else ""
        template = _replace(
            deepcopy(paths[prefix + "indicator-definitions" + suffix]),
            "IndicatorDefinition",
            "FormulaDefinition",
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
                operationId=verb + "_formula_definitions",
                **{"x-capability": "calculated-results.read", "x-contract-version": VERSION},
            )
        paths[prefix + ROOT + suffix] = template
    submit = _replace(
        deepcopy(paths[prefix + "indicator-definitions/{object_id}/actions/submit"]),
        "IndicatorDefinition",
        "FormulaDefinition",
    )
    submit["post"].update(
        operationId="submit_formula_definition",
        **{"x-capability": "calculated-results.read", "x-contract-version": VERSION},
    )
    paths[prefix + ROOT + "/{object_id}/actions/submit"] = submit
    preview = deepcopy(paths[prefix + "recalculations"])
    op = preview["post"]
    op.update(
        operationId="preview_formula_definition",
        summary="Validate and preview a closed typed formula",
        **{"x-capability": "calculated-results.read", "x-contract-version": VERSION},
    )
    op["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/FormulaPreviewRequest"
    }
    op["responses"].pop("202", None)
    op["responses"]["200"] = {
        "description": "Permission, cycle and unit validated sample output",
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/FormulaPreview"}}},
    }
    paths[prefix + PREVIEW] = preview
    ids = (
        {paths[prefix + ROOT][m]["operationId"] for m in ("get", "post")}
        | {paths[prefix + ROOT + "/{object_id}"][m]["operationId"] for m in ("get", "patch")}
        | {"submit_formula_definition", "preview_formula_definition"}
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
                "role_templates": ["MEL_ADMIN", "PROGRAMME_MANAGER", "ANALYST"],
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": method != "get",
                "state_guard": "Closed AST and bounded catalogue only; exact readable approved references; cycles and incompatible units refused before review.",
            }
        )
