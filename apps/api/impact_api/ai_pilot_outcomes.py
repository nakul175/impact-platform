"""Self-reported pilot time comparisons; no official impact or causal conclusions."""

from copy import deepcopy
from decimal import Context, Decimal, ROUND_HALF_UP, localcontext
import re

from .domain import DomainError, NUMBER

PILOT_FIELDS = {"task_label", "baseline", "pilot", "comparable", "notes"}
SAMPLE_FIELDS = {
    "sample_size",
    "total_drafting_minutes",
    "total_review_minutes",
    "factual_corrections",
}
UNSIGNED_DECIMAL = re.compile(r"(?:0|[1-9][0-9]{0,25})(?:\.[0-9]{1,12})?")
DISCLAIMER = (
    "Self-reported draft: drafting and human review minutes are combined and normalized per item. "
    "A comparison is undefined when samples are reported as not comparable or baseline time is zero. "
    "Different sample sizes are normalized, but this does not establish equivalent task difficulty, "
    "quality, accepted impact, ROI, certification or causal benefit. Staff must verify the observations "
    "and interpretation; factual corrections are reported counts, not a quality score."
)


def _invalid():
    raise DomainError("VALIDATION_FAILED", reason="AI_PILOT_OUTCOMES_INVALID")


def _minutes(value):
    if not isinstance(value, str) or not UNSIGNED_DECIMAL.fullmatch(value):
        _invalid()
    return Decimal(value)


def validate_pilot_outcomes(body):
    """Check the closed source DTO without altering any reported value."""
    if not isinstance(body, dict) or set(body) != PILOT_FIELDS:
        _invalid()
    if (
        not isinstance(body["task_label"], str)
        or not body["task_label"].strip()
        or len(body["task_label"]) > 150
        or type(body["comparable"]) is not bool
        or not isinstance(body["notes"], str)
        or len(body["notes"]) > 1000
    ):
        _invalid()
    for key in ("baseline", "pilot"):
        sample = body[key]
        if not isinstance(sample, dict) or set(sample) != SAMPLE_FIELDS:
            _invalid()
        if (
            type(sample["sample_size"]) is not int
            or not 1 <= sample["sample_size"] <= 10000
            or type(sample["factual_corrections"]) is not int
            or not 0 <= sample["factual_corrections"] <= 1000000
        ):
            _invalid()
        _minutes(sample["total_drafting_minutes"])
        _minutes(sample["total_review_minutes"])


def _display(value):
    """Round at the response boundary; never reuse these values in arithmetic."""
    shown = value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
    result = "0" if shown == 0 else format(shown, "f").rstrip("0").rstrip(".")
    if not NUMBER.fullmatch(result):
        _invalid()
    return result


def _sample_result(sample):
    total = _minutes(sample["total_drafting_minutes"]) + _minutes(sample["total_review_minutes"])
    return total, {
        "total_minutes": _display(total),
        "minutes_per_item": _display(total / Decimal(sample["sample_size"])),
        "factual_corrections_per_item": _display(
            Decimal(sample["factual_corrections"]) / Decimal(sample["sample_size"])
        ),
    }


def evaluate_pilot_outcomes(body):
    """Compare raw per-item staff time, including review, without a provider or persistence."""
    validate_pilot_outcomes(body)
    # Bounded source values require no more than 100 significant intermediate digits. A local
    # context keeps the caller's Decimal precision and rounding from changing this calculation.
    with localcontext(Context(prec=100, rounding=ROUND_HALF_UP, Emin=-999999, Emax=999999)):
        baseline_total, baseline = _sample_result(body["baseline"])
        pilot_total, pilot = _sample_result(body["pilot"])
        improvement = {"status": "UNDEFINED", "percent": None, "reason": "SAMPLES_NOT_COMPARABLE"}
        if body["comparable"]:
            improvement["reason"] = "ZERO_BASELINE"
            if baseline_total:
                baseline_size = Decimal(body["baseline"]["sample_size"])
                pilot_size = Decimal(body["pilot"]["sample_size"])
                # This is algebraically the relative change in raw time per item. Do not divide
                # or round the individual per-item values before calculating the percentage.
                percent = (
                    (baseline_total * pilot_size - pilot_total * baseline_size)
                    * Decimal(100)
                    / (baseline_total * pilot_size)
                )
                improvement = {
                    "status": "DEFINED",
                    "percent": _display(percent),
                    "reason": "COMPARABLE_SAMPLES",
                }
        return {
            "status": "SELF_REPORTED_DRAFT",
            "task_label": body["task_label"],
            "comparable": body["comparable"],
            "notes": body["notes"],
            "source": {"baseline": deepcopy(body["baseline"]), "pilot": deepcopy(body["pilot"])},
            "baseline": baseline,
            "pilot": pilot,
            "improvement": improvement,
            "disclaimer": DISCLAIMER,
        }
