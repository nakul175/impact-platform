"""Additive calculation contracts (v0.19): the approved method catalogue, the disaggregation scheme a
definition pins, and the category breakdown a calculated result carries. Build-time only."""

CODE = {"type": "string", "pattern": "^[A-Za-z][A-Za-z0-9_]{0,63}$"}
CATEGORY = {"type": "string", "pattern": "^[A-Za-z0-9][A-Za-z0-9_-]{0,31}$"}
NUMBER = {"type": ["string", "null"], "pattern": r"^-?(0|[1-9][0-9]{0,25})(\.[0-9]{1,12})?$"}
UUID = {"type": "string", "format": "uuid"}
METHODS = ["SUM", "POOLED_RATIO", "COUNT", "LAST_VALID", "MEAN", "MEDIAN", "MIN", "MAX"]


def text(maximum=200):
    return {"type": "string", "minLength": 1, "maxLength": maximum, "pattern": r"\S"}


def closed(properties, required=None):
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": list(properties) if required is None else required,
    }


SCHEME = closed(
    {
        "dimensions": {
            "type": "array",
            "minItems": 1,
            "maxItems": 5,
            "items": closed(
                {
                    "code": CODE,
                    "label": text(),
                    "version": text(64),
                    "multiselect": {"type": "boolean"},
                    "exhaustive": {"type": "boolean"},
                    "categories": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 50,
                        "items": closed({"code": CATEGORY, "label": text()}),
                    },
                }
            ),
        }
    }
)

BREAKDOWN = {
    "type": "array",
    "maxItems": 255,
    "items": closed(
        {
            "dimension": CODE,
            "dimension_version": text(64),
            "category": CATEGORY,
            "additivity": {"enum": ["ADDITIVE", "NONADDITIVE"]},
            "contributor_count": {"type": "integer", "minimum": 0},
            "value_state": {"enum": ["PRESENT", "UNDEFINED"]},
            "value": NUMBER,
            "numerator": NUMBER,
            "denominator": NUMBER,
            "displayed_value": {"type": "string", "maxLength": 64},
            "reason_code": {"type": "string", "minLength": 1, "maxLength": 64},
        }
    ),
}


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    for name in ["IndicatorDefinitionData", "IndicatorDefinitionDraftData"]:
        properties = schemas[name]["properties"]
        rules = properties["combination_rule"]["enum"]
        properties["combination_rule"]["enum"] = rules + [m for m in METHODS if m not in rules]
        properties["disaggregation"] = SCHEME
    schemas["CalculatedResultData"]["properties"]["disaggregation"] = BREAKDOWN
    schemas["CalculatedResultData"]["properties"].update(
        calculation_precision_digits={"type": "integer", "const": 100},
        formula=closed(
            {
                "method": {"enum": METHODS},
                "measurement_type": {"type": "string", "maxLength": 64},
                "time_semantic": {"type": "string", "maxLength": 64},
                "unit": {"type": "string", "maxLength": 64},
                "display_decimals": {"type": "integer", "minimum": 0, "maximum": 6},
                "rounding_rule": {"const": "HALF_UP"},
            }
        ),
        filters=closed({}),
    )
    schemas["LineageManifestData"]["properties"].update(
        execution_id=UUID,
        executed_by=UUID,
        indicator_id=UUID,
        indicator_revision=UUID,
        definition_revision=UUID,
        period_id=UUID,
        formula={"$ref": "#/components/schemas/CalculatedResultData/properties/formula"},
        filters=closed({}),
        contributions={
            "type": "array",
            "maxItems": 10000,
            "items": closed(
                {
                    "source_object_id": UUID,
                    "source_revision": UUID,
                    "disposition": {"enum": ["INCLUDED", "EXCLUDED"]},
                    "reason_code": text(64),
                }
            ),
        },
    )
    schemas["Freshness"]["properties"]["failed_attempt"] = closed(
        {
            "error_code": text(64),
            "reason_code": {"type": ["string", "null"], "maxLength": 64},
            "failed_at": {"type": "string", "format": "date-time"},
        }
    )
