"""Deterministic 1-3 year value-case arithmetic from explicit baseline and trial inputs."""

from copy import deepcopy
from decimal import Context, Decimal, ROUND_HALF_UP, localcontext
import re

from .domain import DomainError

DECIMAL = re.compile(r"(?:0|[1-9][0-9]{0,25})(?:\.[0-9]{1,12})?")
ROOT_FIELDS = {"opportunity_id", "horizon_years", "currency", "baseline", "trial", "costs", "assumptions"}
SOURCE_FIELDS = {"source_label", "annual_operating_cost"}
COST_FIELDS = {"licences_annual", "setup_one_off", "training_one_off", "staff_time_annual"}
DISCLAIMER = (
    "Self-reported planning calculation only. Amounts, attribution and assumptions require human "
    "review; this is not an official result, forecast, funding decision or procurement approval."
)


def _invalid(reason="AI_VALUE_CASE_INVALID"):
    raise DomainError("VALIDATION_FAILED", reason=reason)


def _amount(value):
    if not isinstance(value, str) or not DECIMAL.fullmatch(value):
        _invalid()
    return Decimal(value)


def _display(value):
    shown = value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
    return "0" if shown == 0 else format(shown, "f").rstrip("0").rstrip(".")


def validate_value_case(body):
    if not isinstance(body, dict) or set(body) != ROOT_FIELDS:
        _invalid()
    if (
        not isinstance(body["opportunity_id"], str)
        or not body["opportunity_id"].strip()
        or len(body["opportunity_id"]) > 100
        or type(body["horizon_years"]) is not int
        or body["horizon_years"] not in {1, 2, 3}
        or not isinstance(body["currency"], str)
        or not re.fullmatch(r"[A-Z]{3}", body["currency"])
        or not isinstance(body["assumptions"], list)
        or not 1 <= len(body["assumptions"]) <= 20
        or any(
            not isinstance(item, str) or not item.strip() or len(item) > 500 for item in body["assumptions"]
        )
    ):
        _invalid()
    for key in ("baseline", "trial"):
        source = body[key]
        if not isinstance(source, dict) or set(source) != SOURCE_FIELDS:
            _invalid("AI_VALUE_CASE_SOURCE_REQUIRED")
        if (
            not isinstance(source["source_label"], str)
            or not source["source_label"].strip()
            or len(source["source_label"]) > 200
        ):
            _invalid("AI_VALUE_CASE_SOURCE_REQUIRED")
        _amount(source["annual_operating_cost"])
    costs = body["costs"]
    if not isinstance(costs, dict) or set(costs) != COST_FIELDS:
        _invalid("AI_VALUE_CASE_COST_COMPONENTS_REQUIRED")
    for field in COST_FIELDS:
        _amount(costs[field])


def calculate_value_case(body):
    """Calculate exact planning arithmetic; missing source or cost components are refused."""
    validate_value_case(body)
    years = Decimal(body["horizon_years"])
    with localcontext(Context(prec=100, rounding=ROUND_HALF_UP, Emin=-999999, Emax=999999)):
        baseline_total = _amount(body["baseline"]["annual_operating_cost"]) * years
        trial_total = _amount(body["trial"]["annual_operating_cost"]) * years
        costs = {field: _amount(body["costs"][field]) for field in COST_FIELDS}
        components = {
            "licences": costs["licences_annual"] * years,
            "setup": costs["setup_one_off"],
            "training": costs["training_one_off"],
            "staff_time": costs["staff_time_annual"] * years,
        }
        tco = sum(components.values(), Decimal(0))
        if tco == 0:
            _invalid("AI_VALUE_CASE_ZERO_TCO")
        gross_benefit = baseline_total - trial_total
        net_benefit = gross_benefit - tco
        roi = net_benefit * Decimal(100) / tco
        ratio = gross_benefit / tco
        return {
            "status": "COMPLETE_SELF_REPORTED_DRAFT",
            "opportunity_id": body["opportunity_id"],
            "horizon_years": body["horizon_years"],
            "currency": body["currency"],
            "source": {"baseline": deepcopy(body["baseline"]), "trial": deepcopy(body["trial"])},
            "costs": {key: _display(value) for key, value in components.items()},
            "total_cost_of_ownership": _display(tco),
            "baseline_operating_cost": _display(baseline_total),
            "trial_operating_cost": _display(trial_total),
            "gross_cost_benefit": _display(gross_benefit),
            "net_benefit": _display(net_benefit),
            "roi_percent": _display(roi),
            "cost_benefit_ratio": _display(ratio),
            "assumptions": deepcopy(body["assumptions"]),
            "disclaimer": DISCLAIMER,
        }
