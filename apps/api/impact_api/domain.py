from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
import re


class DomainError(Exception):
    def __init__(self, code, status=422, message=None, reason=None, fields=None):
        self.code, self.status, self.reason, self.fields = code, status, reason, fields or []
        self.message = message or {
            "AUTH_REQUIRED": "Sign in to continue.",
            "RESOURCE_UNAVAILABLE": "The resource is unavailable.",
            "POLICY_DENIED": "The action is not permitted.",
            "CONFLICT_VERSION": "This record changed. Reload its current version.",
            "CONFLICT_OPERATION": "This operation identifier belongs to another command.",
            "STATE_TRANSITION_DENIED": "The action is not available in the current state.",
            "VALIDATION_FAILED": "Check the supplied values.",
        }.get(code, "The request could not be completed.")
        super().__init__(self.message)


def unavailable():
    raise DomainError("RESOURCE_UNAVAILABLE", 404)


NUMBER = re.compile(r"^-?(0|[1-9][0-9]{0,25})(\.[0-9]{1,12})?$")


def decimal_value(value):
    if not isinstance(value, str) or not NUMBER.fullmatch(value):
        raise DomainError(
            "VALIDATION_FAILED", message="Use a decimal string with at most 12 fractional places."
        )
    return Decimal(value)


def stored(value):
    try:
        with localcontext() as c:
            c.prec = 60
            value = value.quantize(Decimal("0.000000000001"), rounding=ROUND_HALF_UP)
            result = format(value, "f").rstrip("0").rstrip(".")
            result = "0" if value == 0 else result
            if not NUMBER.fullmatch(result):
                raise InvalidOperation
            return result
    except InvalidOperation:
        raise DomainError("VALIDATION_FAILED", reason="NUMERIC_OVERFLOW") from None


def calculate(definition, observations):
    rule = definition["combination_rule"]
    places = definition.get("display_decimals", 2)
    if rule not in {"SUM", "POOLED_RATIO"}:
        raise DomainError("INCOMPATIBLE_MEASURE", reason="RULE_NOT_IMPLEMENTED")
    values = [o for o in observations if o["approval_state"] == "APPROVED" and o["value_state"] == "PRESENT"]
    base = {
        "value_state": "UNDEFINED",
        "value": None,
        "numerator": None,
        "denominator": None,
        "displayed_value": "Undefined",
        "display_decimals": places,
        "rounding_rule": "HALF_UP",
        "unit": definition["unit"],
        "reason_code": "NO_APPROVED_VALUES",
    }
    if not values:
        return base
    with localcontext() as c:
        c.prec = 60
        if rule == "POOLED_RATIO":
            pairs = [(decimal_value(o.get("numerator")), decimal_value(o.get("denominator"))) for o in values]
            if any(
                n < 0 or d < 0 or (definition["measurement_type"] == "PERCENTAGE" and n > d) for n, d in pairs
            ):
                raise DomainError("INCOMPATIBLE_MEASURE")
            n = sum((n for n, d in pairs), Decimal(0))
            d = sum((d for n, d in pairs), Decimal(0))
            base.update(numerator=stored(n), denominator=stored(d))
            if d == 0:
                return {**base, "reason_code": "ZERO_DENOMINATOR"}
            value = n / d * (100 if definition["measurement_type"] == "PERCENTAGE" else 1)
        else:
            if (
                definition["measurement_type"] in {"RATIO", "PERCENTAGE"}
                or definition["time_semantic"] != "FLOW"
            ):
                raise DomainError("INCOMPATIBLE_MEASURE")
            value = sum((decimal_value(o["value"]) for o in values), Decimal(0))
        return {
            **base,
            "value_state": "PRESENT",
            "value": stored(value),
            "displayed_value": format(
                value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP), f".{places}f"
            ),
            "reason_code": "CALCULATED",
        }
