"""Additive calculation contracts: governed methods, deterministic provenance and reproduction."""

from copy import deepcopy

CODE = {"type": "string", "pattern": "^[A-Za-z][A-Za-z0-9_]{0,63}$"}
CATEGORY = {"type": "string", "pattern": "^[A-Za-z0-9][A-Za-z0-9_-]{0,31}$"}
NUMBER = {"type": ["string", "null"], "pattern": r"^-?(0|[1-9][0-9]{0,25})(\.[0-9]{1,12})?$"}
UUID = {"type": "string", "format": "uuid"}
METHODS = ["SUM", "POOLED_RATIO", "COUNT", "LAST_VALID", "MEAN", "MEDIAN", "MIN", "MAX"]
VERSION = "1.66.0"
SPECIAL_READS = {
    "calculated-results/{object_id}/reproduction",
    "calculated-results/{object_id}/explanation",
    "calculated-results/{object_id}/comparison/{later_result_id}",
}


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

STATISTICAL_INTERPRETATION = closed(
    {
        "sample_basis": {"enum": ["RAW_VALUES", "SUBGROUP_MEDIANS", "SAMPLE_ESTIMATE"]},
        "weighting": {"enum": ["NONE", "FREQUENCY"]},
        "uncertainty_method": {"enum": ["NONE", "STANDARD_ERROR", "CONFIDENCE_INTERVAL"]},
        "uncertainty_level": NUMBER,
        "population_interpretation": {"enum": ["SAMPLE", "POPULATION"]},
        "expansion_method": {
            "oneOf": [
                {"type": "null"},
                closed({"code": CODE, "basis": text(2000), "factor": NUMBER}),
            ]
        },
    }
)


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    error_codes = schemas["Error"]["properties"]["code"]["enum"]
    if "IDEMPOTENCY_EXPIRED" not in error_codes:
        error_codes.append("IDEMPOTENCY_EXPIRED")
    for name in ["IndicatorDefinitionData", "IndicatorDefinitionDraftData"]:
        properties = schemas[name]["properties"]
        rules = properties["combination_rule"]["enum"]
        properties["combination_rule"]["enum"] = rules + [m for m in METHODS if m not in rules]
        properties["disaggregation"] = SCHEME
        properties["cumulative_baseline"] = NUMBER
        properties["cumulative_baseline_basis"] = text(2000)
        properties["allows_negative_adjustments"] = {"type": "boolean"}
        properties["negative_adjustment_basis"] = text(2000)
        properties["statistical_interpretation"] = STATISTICAL_INTERPRETATION
    for name in ["ObservationData", "ObservationDraftData"]:
        schemas[name]["properties"]["statistical_weight"] = NUMBER
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
                "input_scale_digits": {"type": "integer", "const": 12},
                "stored_scale_digits": {"type": "integer", "const": 12},
                "rounding_boundary": {"const": "OUTPUT_ONLY"},
                "max_contributors": {"type": "integer", "const": 10000},
                "allows_negative_adjustments": {"type": "boolean"},
                "negative_adjustment_basis": {"type": ["string", "null"], "maxLength": 2000},
                "statistic_label": {
                    "enum": METHODS + ["UNWEIGHTED_MEAN", "WEIGHTED_MEAN", "MEAN_OF_MEDIANS", "POOLED_MEDIAN"]
                },
                "weighting_basis": {
                    "enum": [
                        "DENOMINATOR_WEIGHTED",
                        "EQUAL_CONTRIBUTOR_WEIGHT",
                        "FREQUENCY_WEIGHTED",
                        "NOT_APPLICABLE",
                    ]
                },
                "component_requirement": {"enum": ["NUMERATOR_AND_DENOMINATOR_REQUIRED", "VALUE_REQUIRED"]},
                "multiplier_stage": {
                    "enum": ["AFTER_POOLING", "PER_CONTRIBUTOR_BEFORE_MEAN", "NOT_APPLICABLE"]
                },
                "cumulative_baseline": NUMBER,
                "cumulative_baseline_basis": {"type": "string", "minLength": 1, "maxLength": 2000},
                "sample_basis": STATISTICAL_INTERPRETATION["properties"]["sample_basis"],
                "weighting": STATISTICAL_INTERPRETATION["properties"]["weighting"],
                "uncertainty_method": STATISTICAL_INTERPRETATION["properties"]["uncertainty_method"],
                "uncertainty_level": NUMBER,
                "population_interpretation": STATISTICAL_INTERPRETATION["properties"][
                    "population_interpretation"
                ],
                "expansion_method": STATISTICAL_INTERPRETATION["properties"]["expansion_method"],
            },
            required=[
                "method",
                "measurement_type",
                "time_semantic",
                "unit",
                "display_decimals",
                "rounding_rule",
            ],
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
        permission_epoch={"type": "integer", "minimum": 0},
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
    schemas["CalculationReproduction"] = closed(
        {
            "result_id": UUID,
            "result_revision": UUID,
            "lineage_manifest_id": UUID,
            "execution_id": UUID,
            "formula": {"$ref": "#/components/schemas/CalculatedResultData/properties/formula"},
            "filters": closed({}),
            "definition_revision": UUID,
            "indicator_revision": UUID,
            "period_id": UUID,
            "sources": {
                "type": "array",
                "maxItems": 10000,
                "items": closed(
                    {
                        "object_id": UUID,
                        "revision_id": UUID,
                        "disposition": {"enum": ["INCLUDED", "EXCLUDED"]},
                        "reason_code": text(64),
                        "arithmetic_input": closed(
                            {
                                "approval_state": {"type": ["string", "null"], "maxLength": 64},
                                "value_state": {"type": ["string", "null"], "maxLength": 64},
                                "value": NUMBER,
                                "numerator": NUMBER,
                                "denominator": NUMBER,
                                "statistical_weight": NUMBER,
                                "event_at": {"type": ["string", "null"], "format": "date-time"},
                            }
                        ),
                    }
                ),
            },
            "stored": closed(
                {
                    "value_state": {"type": "string", "maxLength": 64},
                    "value": NUMBER,
                    "numerator": NUMBER,
                    "denominator": NUMBER,
                    "displayed_value": {"type": "string", "maxLength": 64},
                }
            ),
            "recomputed": closed(
                {
                    "value_state": {"type": "string", "maxLength": 64},
                    "value": NUMBER,
                    "numerator": NUMBER,
                    "denominator": NUMBER,
                    "displayed_value": {"type": "string", "maxLength": 64},
                }
            ),
            "exact_match": {"type": "boolean"},
        }
    )
    schemas["CalculationExplanation"] = closed(
        {
            "result_id": UUID,
            "result_revision": UUID,
            "rule_version": UUID,
            "source_set": closed(
                {
                    "manifest_id": UUID,
                    "execution_id": UUID,
                    "included_count": {"type": "integer", "minimum": 0},
                    "excluded_count": {"type": "integer", "minimum": 0},
                    "excluded_reasons": {
                        "type": "array",
                        "maxItems": 100,
                        "items": closed(
                            {
                                "reason_code": text(64),
                                "count": {"type": "integer", "minimum": 1},
                            }
                        ),
                    },
                }
            ),
            "formula": {"$ref": "#/components/schemas/CalculatedResultData/properties/formula"},
            "filters": closed({}),
            "adjustments": {
                "type": "array",
                "maxItems": 100,
                "items": closed({"code": text(64), "message": text(2100)}),
            },
            "coverage": {"$ref": "#/components/schemas/CalculatedResultData/properties/coverage"},
            "approval": closed(
                {
                    "mode": {"enum": ["PROVISIONAL", "OFFICIAL"]},
                    "lifecycle_state": text(64),
                }
            ),
        }
    )
    schemas["CalculationDifferenceCause"] = closed(
        {
            "category": {
                "enum": ["SOURCE", "FILTER", "RULE", "PERIOD", "TARGET", "PERMISSION", "DISCLOSURE"]
            },
            "effect": NUMBER,
            "reference_state": {"enum": ["PERMITTED", "WITHHELD"]},
        }
    )
    schemas["CalculationComparison"] = closed(
        {
            "earlier_result_revision": UUID,
            "later_result_revision": UUID,
            "difference": NUMBER,
            "causes": {
                "type": "array",
                "maxItems": 7,
                "items": {"$ref": "#/components/schemas/CalculationDifferenceCause"},
            },
            "explained_difference": NUMBER,
            "reconciled": {"type": "boolean"},
            "approval_blocked": {"type": "boolean"},
        }
    )
    prefix = "/v1/tenants/{tenant_id}/calculated-results/{object_id}/reproduction"
    template = deepcopy(paths["/v1/tenants/{tenant_id}/calculated-results/{object_id}"])
    get = template["get"]
    get["operationId"] = "get_calculated_result_reproduction"
    get["summary"] = "Reproduce a calculated result from its frozen inputs"
    get["description"] = (
        "Returns a bounded arithmetic bundle only after current authority is rechecked for the result, "
        "indicator, definition, period, lineage manifest and every source revision."
    )
    get["x-capability"] = "lineage-manifests.read"
    get["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/CalculationReproduction"
    }
    paths[prefix] = {"parameters": template["parameters"], "get": get}
    explanation_path = "/v1/tenants/{tenant_id}/calculated-results/{object_id}/explanation"
    explanation = deepcopy(get)
    explanation.update(
        operationId="get_calculated_result_explanation",
        summary="Explain a calculated result without exposing restricted source records",
        **{"x-capability": "lineage-manifests.read", "x-contract-version": VERSION},
    )
    explanation["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/CalculationExplanation"
    }
    paths[explanation_path] = {"parameters": deepcopy(template["parameters"]), "get": explanation}
    comparison_path = "/v1/tenants/{tenant_id}/calculated-results/{object_id}/comparison/{later_result_id}"
    comparison = deepcopy(get)
    comparison.update(
        operationId="compare_calculated_result_runs",
        summary="Classify and reconcile the numerical difference between two result runs",
        **{"x-capability": "lineage-manifests.read", "x-contract-version": VERSION},
    )
    comparison["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/CalculationComparison"
    }
    comparison_parameters = deepcopy(template["parameters"])
    comparison_parameters.append(
        {
            "name": "later_result_id",
            "in": "path",
            "required": True,
            "schema": deepcopy(UUID),
        }
    )
    paths[comparison_path] = {"parameters": comparison_parameters, "get": comparison}
    policy["operations"] = [
        row for row in policy["operations"] if row["operation_id"] != "get_calculated_result_reproduction"
    ]
    policy["operations"].append(
        {
            "operation_id": "get_calculated_result_reproduction",
            "method": "GET",
            "path": prefix,
            "capability": "lineage-manifests.read",
            "role_templates": ["AUTHOR", "REVIEWER", "MEL_ADMIN", "PROGRAMME_MANAGER"],
            "purpose_required": False,
            "fresh_assurance_seconds": None,
            "audit": True,
            "state_guard": "Current authority for the result and every frozen dependency; bounded arithmetic fields only.",
        }
    )
    policy["operations"] = [
        row
        for row in policy["operations"]
        if row["operation_id"] not in {"get_calculated_result_explanation", "compare_calculated_result_runs"}
    ]
    for operation_id, path, guard in (
        (
            "get_calculated_result_explanation",
            explanation_path,
            "Current result and lineage authority; excluded sources are aggregate counts only.",
        ),
        (
            "compare_calculated_result_runs",
            comparison_path,
            "Current authority for both results and permitted sources; withheld references cannot be inspected and prevent a reconciled approval claim.",
        ),
    ):
        policy["operations"].append(
            {
                "operation_id": operation_id,
                "method": "GET",
                "path": path,
                "capability": "lineage-manifests.read",
                "role_templates": ["AUTHOR", "REVIEWER", "MEL_ADMIN", "PROGRAMME_MANAGER"],
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": True,
                "state_guard": guard,
            }
        )
