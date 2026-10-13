"""FR-CAL-002 contracts for semantic compatibility and approved conversion preview."""

from copy import deepcopy

from .measurement_contracts import closed, text_field

UUID = {"type": "string", "format": "uuid"}
NUMBER = {"type": "string", "pattern": r"^-?(0|[1-9][0-9]{0,25})(\.[0-9]{1,12})?$"}
ROOT = "calculation-compatibility/preview"
IMPLEMENTED = [("post", ROOT)]
VERSION = "1.49.0"


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    schemas["CalculationCompatibilityInput"] = closed(
        {
            "definition_revision": UUID,
            "value": NUMBER,
            "conversion_version": {"type": ["string", "null"], "maxLength": 120},
        },
        ["definition_revision", "value"],
    )
    schemas["CalculationCompatibilityPreviewRequest"] = closed(
        {
            "target_definition_revision": UUID,
            "inputs": {
                "type": "array",
                "minItems": 2,
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/CalculationCompatibilityInput"},
            },
        },
        ["target_definition_revision", "inputs"],
    )
    schemas["ApprovedUnitConversion"] = closed(
        {
            "version": text_field(120),
            "approval_state": {"const": "APPROVED"},
            "source_unit": text_field(64),
            "target_unit": text_field(64),
            "direction": {"const": "SOURCE_TO_TARGET"},
            "factor": NUMBER,
            "precision": {"type": "integer", "minimum": 0, "maximum": 12},
            "rounding_rule": {"const": "HALF_UP"},
            "catalogue_version": text_field(120),
        },
        [
            "version",
            "approval_state",
            "source_unit",
            "target_unit",
            "direction",
            "factor",
            "precision",
            "rounding_rule",
            "catalogue_version",
        ],
    )
    schemas["CalculationCompatibilityNormalizedInput"] = closed(
        {
            "definition_revision": UUID,
            "original_value": NUMBER,
            "original_unit": text_field(64),
            "converted_value": NUMBER,
            "target_unit": text_field(64),
            "conversion": {
                "oneOf": [
                    {"$ref": "#/components/schemas/ApprovedUnitConversion"},
                    {"type": "null"},
                ]
            },
        },
        [
            "definition_revision",
            "original_value",
            "original_unit",
            "converted_value",
            "target_unit",
            "conversion",
        ],
    )
    schemas["CalculationCompatibilitySignature"] = closed(
        {
            "measurement_type": text_field(64),
            "population": {"type": "string", "maxLength": 2000},
            "inclusion": {"type": "string", "maxLength": 2000},
            "exclusion": {"type": "string", "maxLength": 2000},
            "method": {"type": "string", "maxLength": 2000},
            "time_semantic": text_field(64),
            "dimensions": {
                "type": "array",
                "maxItems": 5,
                "items": closed(
                    {
                        "code": text_field(64),
                        "version": text_field(64),
                        "multiselect": {"type": "boolean"},
                        "exhaustive": {"type": "boolean"},
                        "categories": {
                            "type": "array",
                            "maxItems": 50,
                            "items": text_field(32),
                        },
                    },
                    ["code", "version", "multiselect", "exhaustive", "categories"],
                ),
            },
        },
        [
            "measurement_type",
            "population",
            "inclusion",
            "exclusion",
            "method",
            "time_semantic",
            "dimensions",
        ],
    )
    schemas["CalculationCompatibilityPreview"] = closed(
        {
            "compatible": {"const": True},
            "target_definition_revision": UUID,
            "compatibility": {"$ref": "#/components/schemas/CalculationCompatibilitySignature"},
            "inputs": {
                "type": "array",
                "minItems": 2,
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/CalculationCompatibilityNormalizedInput"},
            },
            "combined_value": NUMBER,
            "unit": text_field(64),
        },
        [
            "compatible",
            "target_definition_revision",
            "compatibility",
            "inputs",
            "combined_value",
            "unit",
        ],
    )

    template = deepcopy(paths["/v1/tenants/{tenant_id}/recalculations"])
    operation = template["post"]
    operation.update(
        operationId="preview_calculation_compatibility",
        summary="Preview a semantically compatible calculation",
        description=(
            "Compares measurement type, population, time semantics and dimension versions before "
            "combining inputs. Different units require an exact approved conversion version."
        ),
        **{"x-capability": "calculated-results.read", "x-contract-version": VERSION},
    )
    operation["responses"].pop("202", None)
    operation["responses"]["409"]["description"] = "STATE_TRANSITION_DENIED"
    operation["responses"]["200"] = {
        "description": "Compatible normalized inputs and deterministic combined value",
        "content": {
            "application/json": {"schema": {"$ref": "#/components/schemas/CalculationCompatibilityPreview"}}
        },
    }
    operation["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/CalculationCompatibilityPreviewRequest"
    }
    path = "/v1/tenants/{tenant_id}/" + ROOT
    paths[path] = template
    policy["operations"] = [
        row for row in policy["operations"] if row["operation_id"] != "preview_calculation_compatibility"
    ]
    policy["operations"].append(
        {
            "operation_id": "preview_calculation_compatibility",
            "method": "POST",
            "path": path,
            "capability": "calculated-results.read",
            "role_templates": [
                "MEL_ADMIN",
                "PROGRAMME_MANAGER",
                "AUTHOR",
                "REVIEWER",
                "ANALYST",
                "DATA_STEWARD",
            ],
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": True,
            "state_guard": "Current authority for every exact definition revision; labels never establish compatibility.",
        }
    )
