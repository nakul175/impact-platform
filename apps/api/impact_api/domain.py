from datetime import datetime
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


# Calculation methods of the approved measurement contract (FR-CAL-003/005/012, FR-IND-002). Each
# method names the measurement types and time semantics it accepts; anything else is refused when the
# definition is submitted and again at calculation, never approximated. WEIGHTED_INDEX (R2), UNIQUE_COUNT
# (needs participant identities, R2) and NONE are not implemented.
METHODS = {
    "SUM": ({"COUNT", "DECIMAL"}, {"FLOW"}),
    "POOLED_RATIO": ({"RATIO", "PERCENTAGE"}, {"FLOW"}),
    "COUNT": ({"COUNT"}, {"EVENT"}),
    "LAST_VALID": ({"COUNT", "DECIMAL", "RATIO", "PERCENTAGE"}, {"STOCK", "CUMULATIVE"}),
    "MEAN": ({"COUNT", "DECIMAL", "RATIO", "PERCENTAGE"}, {"FLOW", "STOCK"}),
    "MEDIAN": ({"COUNT", "DECIMAL"}, {"FLOW", "STOCK"}),
    "MIN": ({"COUNT", "DECIMAL"}, {"FLOW", "STOCK"}),
    "MAX": ({"COUNT", "DECIMAL"}, {"FLOW", "STOCK"}),
}
RATIO_TYPES = {"RATIO", "PERCENTAGE"}
# The one reserved category a result uses for contributions without a code on a non-exhaustive dimension.
UNSPECIFIED = "UNSPECIFIED"
PRECISION = 100


def method_supported(definition):
    rule = METHODS.get(definition.get("combination_rule"))
    return bool(
        rule and definition.get("measurement_type") in rule[0] and definition.get("time_semantic") in rule[1]
    )


def display(value, places):
    with localcontext() as c:
        c.prec = PRECISION
        shown = value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)
        # A negative value that rounds to zero is displayed as zero, never as "-0.00".
        return format(shown.copy_abs() if shown == 0 else shown, f".{places}f")


def ratio(definition, n, d):
    """One contributor's or one pool's ratio; the multiplier is applied after pooling (FR-CAL-003)."""
    if n < 0 or d < 0 or (definition["measurement_type"] == "PERCENTAGE" and n > d):
        raise DomainError("INCOMPATIBLE_MEASURE")
    if d == 0:
        return None
    return n / d * (100 if definition["measurement_type"] == "PERCENTAGE" else 1)


def components(o):
    return decimal_value(o.get("numerator")), decimal_value(o.get("denominator"))


def aware(value):
    """An RFC 3339 instant with an explicit offset; a naive or malformed timestamp is refused (422),
    never compared with an aware one."""
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        parsed = None
    if parsed is None or parsed.tzinfo is None or parsed.utcoffset() is None:
        raise DomainError("VALIDATION_FAILED", reason="TIMESTAMP_OFFSET_REQUIRED")
    return parsed


def event_order(o):
    return aware(o.get("event_at", ""))


def calculate(definition, observations):
    """Deterministic result of one approved definition over approved PRESENT source values.

    Only APPROVED rows in value state PRESENT contribute; MISSING, NOT_COLLECTED, NOT_APPLICABLE,
    INVALID and UNDEFINED rows never become zero and never enter a denominator. Arithmetic runs at 100
    significant digits; the stored value is rounded half-up once to 12 places and the displayed value is
    rounded half-up from that stored value (the exported raw decimal), never from a displayed value."""
    rule = definition["combination_rule"]
    places = definition.get("display_decimals", 2)
    if rule not in METHODS:
        raise DomainError("INCOMPATIBLE_MEASURE", reason="RULE_NOT_IMPLEMENTED")
    if not method_supported(definition):
        raise DomainError("INCOMPATIBLE_MEASURE", reason="CONFIGURATION_NOT_IMPLEMENTED")
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
    ratio_type = definition["measurement_type"] in RATIO_TYPES
    with localcontext() as c:
        c.prec = PRECISION
        if rule == "POOLED_RATIO":
            pairs = [components(o) for o in values]
            for n, d in pairs:
                ratio(definition, n, d)
            n = sum((n for n, d in pairs), Decimal(0))
            d = sum((d for n, d in pairs), Decimal(0))
            base.update(numerator=stored(n), denominator=stored(d))
            value = ratio(definition, n, d)
            if value is None:
                return {**base, "reason_code": "ZERO_DENOMINATOR"}
        elif rule == "LAST_VALID":
            ordered = sorted(values, key=event_order)
            latest = event_order(ordered[-1])
            tied = [o for o in ordered if event_order(o) == latest]
            if ratio_type:
                keys = {components(o) for o in tied}
            else:
                keys = {decimal_value(o["value"]) for o in tied}
            if len(keys) != 1:
                return {**base, "reason_code": "TIED_LATEST_VALUES"}
            if definition["time_semantic"] == "CUMULATIVE":
                series = [components(o) if ratio_type else (decimal_value(o["value"]),) for o in ordered]
                if any(
                    any(b < a for a, b in zip(earlier, later)) for earlier, later in zip(series, series[1:])
                ):
                    return {**base, "reason_code": "CUMULATIVE_DECLINE"}
            if ratio_type:
                n, d = keys.pop()
                base.update(numerator=stored(n), denominator=stored(d))
                value = ratio(definition, n, d)
                if value is None:
                    return {**base, "reason_code": "ZERO_DENOMINATOR"}
            else:
                value = keys.pop()
        elif rule == "MEAN" and ratio_type:
            parts = [ratio(definition, *components(o)) for o in values]
            if any(p is None for p in parts):
                return {**base, "reason_code": "ZERO_DENOMINATOR"}
            value = sum(parts, Decimal(0)) / len(parts)
        else:
            numbers = [decimal_value(o["value"]) for o in values]
            if rule == "SUM":
                value = sum(numbers, Decimal(0))
            elif rule == "COUNT":
                if any(v != 1 for v in numbers):
                    raise DomainError("INCOMPATIBLE_MEASURE")
                value = Decimal(len(numbers))
            elif rule == "MEAN":
                value = sum(numbers, Decimal(0)) / len(numbers)
            elif rule == "MEDIAN":
                ordered = sorted(numbers)
                middle = len(ordered) // 2
                value = ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2
            elif rule == "MIN":
                value = min(numbers)
            else:
                value = max(numbers)
        # The display is derived from the stored 12-place value, so every artifact that carries the
        # raw decimal (snapshot, export, attainment) reproduces its displayed figure exactly.
        raw = stored(value)
        return {
            **base,
            "value_state": "PRESENT",
            "value": raw,
            "displayed_value": display(Decimal(raw), places),
            "reason_code": "CALCULATED",
        }


def method_limitations(definition):
    """Labels a statistic that must never be read as the pooled or summed figure (CAL02, CAL05)."""
    rule = definition.get("combination_rule")
    labels = {
        "MEAN": (
            "UNWEIGHTED_MEAN",
            "Unweighted mean of contributor values; not a pooled or weighted figure.",
        ),
        "MEDIAN": ("POOLED_MEDIAN", "Median of the approved raw contributor values in this period."),
        "LAST_VALID": (
            "LATEST_POSITION",
            "Latest approved position by event time; positions are never summed across the period.",
        ),
    }
    return [{"code": labels[rule][0], "message": labels[rule][1]}] if rule in labels else []


def dimension_codes(raw):
    return raw.split("|") if raw else []


def validate_scheme(definition):
    """FR-IND-006: a definition's disaggregation scheme is closed, uniquely coded and versioned."""
    scheme = definition.get("disaggregation")
    if scheme is None:
        return
    seen = set()
    for dim in scheme.get("dimensions", []):
        categories = [c["code"] for c in dim["categories"]]
        if dim["code"] in seen or len(set(categories)) != len(categories) or UNSPECIFIED in categories:
            raise DomainError("VALIDATION_FAILED", reason="INVALID_DISAGGREGATION")
        seen.add(dim["code"])


def validate_dimensions(definition, payload, complete=True):
    """An observation's codes must belong to the pinned scheme; exhaustive dimensions need a code on
    every PRESENT value and only multiselect dimensions accept several codes (separated by |)."""
    values = payload.get("dimension_values") or {}
    dims = {d["code"]: d for d in (definition.get("disaggregation") or {}).get("dimensions", [])}
    fail = DomainError("VALIDATION_FAILED", reason="INVALID_DIMENSION_VALUES")
    if set(values) - set(dims):
        raise fail
    for code, dim in dims.items():
        codes = dimension_codes(values.get(code))
        allowed = {c["code"] for c in dim["categories"]}
        if complete and not codes and dim["exhaustive"] and payload.get("value_state") == "PRESENT":
            raise fail
        if len(set(codes)) != len(codes) or not set(codes) <= allowed:
            raise fail
        if len(codes) > 1 and not dim["multiselect"]:
            raise fail


def disaggregate(definition, observations):
    """Category results computed from source values, one bucket per declared category. The total is
    never derived from these entries: it is calculated independently from the same source rows. A
    multiselect dimension counts a contribution in every selected category, so its categories are
    labelled NONADDITIVE; so is every method whose category values cannot be added (FR-IND-006)."""
    entries = []
    for dim in (definition.get("disaggregation") or {}).get("dimensions", []):
        categories = [c["code"] for c in dim["categories"]] + ([] if dim["exhaustive"] else [UNSPECIFIED])
        additive = not dim["multiselect"] and definition["combination_rule"] in {"SUM", "COUNT"}
        for category in categories:
            rows = [
                o
                for o in observations
                if (category in dimension_codes((o.get("dimension_values") or {}).get(dim["code"])))
                or (category == UNSPECIFIED and not (o.get("dimension_values") or {}).get(dim["code"]))
            ]
            result = calculate(definition, rows)
            entries.append(
                {
                    "dimension": dim["code"],
                    "dimension_version": dim["version"],
                    "category": category,
                    "additivity": "ADDITIVE" if additive else "NONADDITIVE",
                    "contributor_count": sum(
                        o["approval_state"] == "APPROVED" and o["value_state"] == "PRESENT" for o in rows
                    ),
                    **{
                        k: result[k]
                        for k in [
                            "value_state",
                            "value",
                            "numerator",
                            "denominator",
                            "displayed_value",
                            "reason_code",
                        ]
                    },
                }
            )
    return entries
