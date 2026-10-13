"""FR-CAL-012/013 typed formula validation and governed composite preview."""

from decimal import Decimal, localcontext
from .contracts import validate
from .domain import DomainError, decimal_value, stored, unavailable
from .store import authorize, context, load, write


def _definition(c, ctx, revision_id):
    row = c.execute(
        "SELECT * FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
        (ctx.tenant_id, revision_id),
    ).fetchone()
    if not row or row["object_type"] != "IndicatorDefinition" or row["restriction_state"] != "AVAILABLE":
        unavailable()
    load(c, ctx, row["object_id"], "IndicatorDefinition", "indicator-definitions.read")
    approved = c.execute(
        "SELECT 1 FROM impact.decision_current WHERE tenant_id=%s AND candidate_revision=%s AND action='APPROVE' LIMIT 1",
        (ctx.tenant_id, revision_id),
    ).fetchone()
    if not approved:
        raise DomainError("INVALID_STATE", 409, reason="APPROVED_DEFINITION_REVISION_REQUIRED")
    return row


def _dimension(definition, dimension_code, category_code):
    dimensions = (definition.get("disaggregation") or {}).get("dimensions", [])
    dimension = next((x for x in dimensions if x["code"] == dimension_code), None)
    if not dimension or category_code not in {x["code"] for x in dimension["categories"]}:
        raise DomainError("VALIDATION_FAILED", reason="FILTER_CATEGORY_NOT_FOUND")


def _analyse(c, ctx, node, target_definition_id, references):
    kind = node["kind"]
    if kind == "LITERAL":
        return node["unit"]
    if kind in {"REFERENCE", "FILTER"}:
        definition = _definition(c, ctx, node["definition_revision"])
        if str(definition["object_id"]) == target_definition_id:
            raise DomainError("VALIDATION_FAILED", reason="CIRCULAR_FORMULA_REFERENCE")
        references[node["definition_revision"]] = definition
        if kind == "FILTER":
            _dimension(definition["payload"], node["dimension_code"], node["category_code"])
        return definition["payload"]["unit"]
    if kind == "COMPOSITE":
        components = node["components"]
        if len({item["code"] for item in components}) != len(components):
            raise DomainError("VALIDATION_FAILED", reason="DUPLICATE_COMPOSITE_COMPONENT")
        weights = [decimal_value(item["weight"]) for item in components]
        if any(weight < 0 for weight in weights) or sum(weights, Decimal(0)) != Decimal(1):
            raise DomainError("VALIDATION_FAILED", reason="COMPOSITE_WEIGHTS_TOTAL")
        for item in components:
            low, high = decimal_value(item["input_min"]), decimal_value(item["input_max"])
            if low >= high:
                raise DomainError("VALIDATION_FAILED", reason="COMPOSITE_NORMALISATION_RANGE")
            definition = _definition(c, ctx, item["definition_revision"])
            if str(definition["object_id"]) == target_definition_id:
                raise DomainError("VALIDATION_FAILED", reason="CIRCULAR_FORMULA_REFERENCE")
            references[item["definition_revision"]] = definition
        if node["missing_policy"] == "RENORMALIZE_OPTIONAL" and all(item["required"] for item in components):
            raise DomainError("VALIDATION_FAILED", reason="COMPOSITE_RENORMALISATION_UNUSED")
        return "score"
    function = node["function"]
    args = node["args"]
    units = [_analyse(c, ctx, arg, target_definition_id, references) for arg in args]
    arity = {
        "ADD": 2,
        "SUB": 2,
        "MUL": 2,
        "DIV": 2,
        "RATIO": 2,
        "COUNT": 1,
        "SUM": 1,
        "MIN": 1,
        "MAX": 1,
        "ELIGIBLE_DISTINCT": 1,
    }
    if len(args) != arity[function]:
        raise DomainError("VALIDATION_FAILED", reason="FORMULA_ARITY_MISMATCH")
    set_nodes = {"REFERENCE", "FILTER"}
    if function in {"COUNT", "SUM", "MIN", "MAX", "ELIGIBLE_DISTINCT"} and args[0]["kind"] not in set_nodes:
        raise DomainError("VALIDATION_FAILED", reason="REFERENCE_SET_REQUIRED")
    if function in {"ADD", "SUB", "MUL", "DIV", "RATIO"} and any(arg["kind"] in set_nodes for arg in args):
        raise DomainError("VALIDATION_FAILED", reason="FORMULA_AGGREGATION_REQUIRED")
    if function in {"ADD", "SUB", "RATIO", "DIV"} and units[0] != units[1]:
        raise DomainError("INCOMPATIBLE_MEASURE", reason="FORMULA_UNIT_MISMATCH")
    if function == "MUL":
        if "1" not in units:
            raise DomainError("INCOMPATIBLE_MEASURE", reason="SCALAR_MULTIPLICATION_REQUIRED")
        return units[1] if units[0] == "1" else units[0]
    if function in {"COUNT", "ELIGIBLE_DISTINCT"}:
        return "count"
    if function in {"RATIO", "DIV"}:
        return "ratio"
    return units[0]


def validate_formula(c, ctx, data):
    target = load(c, ctx, data["target_definition_id"], "IndicatorDefinition", "indicator-definitions.read")
    references = {}
    unit = _analyse(c, ctx, data["ast"], str(target["object_id"]), references)
    if unit != data["output_unit"]:
        raise DomainError("INCOMPATIBLE_MEASURE", reason="FORMULA_OUTPUT_UNIT_MISMATCH")
    return references


def _evaluate(node, samples):
    if node["kind"] == "LITERAL":
        return Decimal(node["value"])
    if node["kind"] in {"REFERENCE", "FILTER"}:
        rows = samples.get(node["definition_revision"], [])
        if node["kind"] == "FILTER":
            rows = [x for x in rows if x["dimensions"].get(node["dimension_code"]) == node["category_code"]]
        return [x for x in rows if x["eligible"]]
    if node["kind"] == "COMPOSITE":
        prepared = []
        for item in node["components"]:
            rows = [x for x in samples.get(item["definition_revision"], []) if x["eligible"]]
            if not rows:
                prepared.append((item, None))
                continue
            if len(rows) != 1:
                raise DomainError("VALIDATION_FAILED", reason="COMPOSITE_ONE_VALUE_PER_COMPONENT")
            value = decimal_value(rows[0]["value"])
            low, high = decimal_value(item["input_min"]), decimal_value(item["input_max"])
            if value < low or value > high:
                raise DomainError("VALIDATION_FAILED", reason="COMPOSITE_INPUT_OUT_OF_RANGE")
            prepared.append((item, (value - low) * Decimal(100) / (high - low)))
        present_weight = sum(
            (decimal_value(item["weight"]) for item, value in prepared if value is not None),
            Decimal(0),
        )
        blocked = any(
            value is None and (item["required"] or node["missing_policy"] == "BLOCK")
            for item, value in prepared
        )
        contributions, score = [], Decimal(0)
        for item, value in prepared:
            if value is None:
                contributions.append(
                    {
                        "code": item["code"],
                        "definition_revision": item["definition_revision"],
                        "value_state": "MISSING",
                        "normalized_value": None,
                        "effective_weight": None,
                        "contribution": None,
                    }
                )
                continue
            if blocked or present_weight == 0:
                contributions.append(
                    {
                        "code": item["code"],
                        "definition_revision": item["definition_revision"],
                        "value_state": "PRESENT",
                        "normalized_value": stored(value),
                        "effective_weight": None,
                        "contribution": None,
                    }
                )
                continue
            weight = decimal_value(item["weight"]) / present_weight
            contribution = value * weight
            score += contribution
            contributions.append(
                {
                    "code": item["code"],
                    "definition_revision": item["definition_revision"],
                    "value_state": "PRESENT",
                    "normalized_value": stored(value),
                    "effective_weight": stored(weight),
                    "contribution": stored(contribution),
                }
            )
        if blocked or present_weight == 0:
            return {"state": "MISSING", "components": contributions, "sensitivity": []}
        sensitivity = []
        for focus, focus_value in prepared:
            if focus_value is None:
                continue
            raised = decimal_value(focus["weight"]) * Decimal("1.1")
            total = present_weight + raised - decimal_value(focus["weight"])
            alternate = sum(
                value * (raised if item["code"] == focus["code"] else decimal_value(item["weight"])) / total
                for item, value in prepared
                if value is not None
            )
            sensitivity.append(
                {
                    "code": focus["code"],
                    "plus_ten_percent_weight_score": stored(alternate),
                }
            )
        return {
            "state": "PRESENT",
            "value": score,
            "components": contributions,
            "sensitivity": sensitivity,
        }
    function = node["function"]
    values = [_evaluate(arg, samples) for arg in node["args"]]

    def scalar(value):
        if isinstance(value, list):
            raise DomainError("VALIDATION_FAILED", reason="FORMULA_AGGREGATION_REQUIRED")
        if isinstance(value, dict):
            return value.get("value") if value["state"] == "PRESENT" else None
        return value

    if function in {"COUNT", "ELIGIBLE_DISTINCT", "SUM", "MIN", "MAX"}:
        rows = values[0]
        if not isinstance(rows, list):
            raise DomainError("VALIDATION_FAILED", reason="REFERENCE_SET_REQUIRED")
        if function == "COUNT":
            return Decimal(len(rows))
        if function == "ELIGIBLE_DISTINCT":
            return Decimal(len({x["distinct_key"] for x in rows if x.get("distinct_key") is not None}))
        numbers = [decimal_value(x["value"]) for x in rows]
        if not numbers:
            return None
        return (
            sum(numbers, Decimal(0))
            if function == "SUM"
            else min(numbers)
            if function == "MIN"
            else max(numbers)
        )
    left, right = scalar(values[0]), scalar(values[1])
    if left is None or right is None:
        return None
    if function == "ADD":
        return left + right
    if function == "SUB":
        return left - right
    if function == "MUL":
        return left * right
    if right == 0:
        return "UNDEFINED"
    return left / right


class FormulaAuthoring:
    def __init__(self, service):
        self.service = service

    def preview(self, identity, tenant, body, correlation):
        validate("FormulaPreviewRequest", body)
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "preview_formula_definition", hidden=True)
            references = validate_formula(c, ctx, body["data"])
            supplied = {row["definition_revision"]: row["values"] for row in body["samples"]}
            if len(supplied) != len(body["samples"]):
                raise DomainError("VALIDATION_FAILED", reason="DUPLICATE_SAMPLE_REFERENCE")
            if set(supplied) != set(references):
                raise DomainError("VALIDATION_FAILED", reason="EXACT_SAMPLE_SET_REQUIRED")
            with localcontext() as decimal_context:
                decimal_context.prec = 100
                value = _evaluate(body["data"]["ast"], supplied)
            composite = value if isinstance(value, dict) else None
            if composite:
                value = composite.get("value")
            state = (
                composite["state"]
                if composite
                else "UNDEFINED"
                if value == "UNDEFINED"
                else "MISSING"
                if value is None
                else "PRESENT"
            )
            result = {
                "output_unit": body["data"]["output_unit"],
                "value_state": state,
                "value": stored(value) if state == "PRESENT" else None,
                "referenced_definition_revisions": sorted(references),
                **(
                    {
                        "component_contributions": composite["components"],
                        "sensitivity": composite["sensitivity"],
                    }
                    if composite
                    else {}
                ),
            }
            validate("FormulaPreview", result)
            observed = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
            write(
                c,
                ctx,
                "AuditEvent",
                {
                    "real_actor_id": str(ctx.principal_id),
                    "effective_actor_id": str(ctx.principal_id),
                    "action_type": "formula.preview",
                    "object_reference": str(body["data"]["target_definition_id"]),
                    "outcome": "SUCCEEDED",
                    "occurred_at": observed.isoformat(),
                    "correlation_id": correlation,
                    "specification_ref": "FR-CAL-012",
                },
                "Recorded",
                track_author=False,
            )
            return result
