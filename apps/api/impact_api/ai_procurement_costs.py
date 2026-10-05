"""Deterministic, unapproved cost drafts using only the supplied decimal amounts.

No supplier price, exchange rate, eligibility or procurement decision is inferred.
Inputs fit NUMERIC(38,12); calculated values retain their exact additional precision
and are not a representation suitable for a NUMERIC(38,12) result column.
"""

import re
from decimal import Context, Decimal, ROUND_HALF_UP, localcontext

from .domain import DomainError

CATEGORIES = (
    "SETUP",
    "SUBSCRIPTION",
    "USAGE",
    "INTEGRATION",
    "TRAINING",
    "REVIEW",
    "SUPPORT",
    "EXIT",
    "OTHER",
)
CADENCES = ("ONE_OFF", "MONTHLY")
IDENTIFIER_PATTERN = r"[a-z][a-z0-9_-]{0,63}"
DECIMAL_PATTERN = r"(?:0|[1-9][0-9]{0,25})(?:\.[0-9]{1,12})?"
REQUEST_FIELDS = {"currency", "period_months", "offers"}
OFFER_FIELDS = {"id", "name", "lines"}
LINE_FIELDS = {"id", "category", "label", "quantity", "unit_amount", "cadence"}
DISCLAIMER = (
    "Draft comparison of supplied amounts only. Missing costs are unknown, not zero. "
    "No exchange conversion, supplier verification or procurement approval is provided."
)


def _invalid():
    raise DomainError("VALIDATION_FAILED", reason="AI_PROCUREMENT_COSTS_INVALID")


def _closed(value, fields):
    if not isinstance(value, dict) or set(value) != fields:
        _invalid()


def _identifier(value):
    if not isinstance(value, str) or not re.fullmatch(IDENTIFIER_PATTERN, value):
        _invalid()


def _text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 150:
        _invalid()


def _decimal(value):
    if not isinstance(value, str) or not re.fullmatch(DECIMAL_PATTERN, value):
        _invalid()
    return Decimal(value)


def validate_comparison(body):
    """Reject coercion, unknown fields, unlike currencies and unbounded drafts."""
    _closed(body, REQUEST_FIELDS)
    currency, months, offers = body["currency"], body["period_months"], body["offers"]
    if not isinstance(currency, str) or not re.fullmatch(r"[A-Z]{3}", currency):
        _invalid()
    if type(months) is not int or not 1 <= months <= 60:
        _invalid()
    if not isinstance(offers, list) or not 1 <= len(offers) <= 4:
        _invalid()
    offer_ids = set()
    for offer in offers:
        _closed(offer, OFFER_FIELDS)
        _identifier(offer["id"])
        _text(offer["name"])
        if offer["id"] in offer_ids:
            _invalid()
        offer_ids.add(offer["id"])
        lines = offer["lines"]
        if not isinstance(lines, list) or not 1 <= len(lines) <= 20:
            _invalid()
        line_ids = set()
        for line in lines:
            _closed(line, LINE_FIELDS)
            _identifier(line["id"])
            _text(line["label"])
            if line["id"] in line_ids:
                _invalid()
            line_ids.add(line["id"])
            if line["category"] not in CATEGORIES or line["cadence"] not in CADENCES:
                _invalid()
            _decimal(line["quantity"])
            if line["unit_amount"] is not None:
                _decimal(line["unit_amount"])


def _plain_decimal(value):
    result = format(value, "f")
    return result.rstrip("0").rstrip(".") if "." in result else result


def compare_costs(body):
    """One-off lines count once; monthly lines count for the chosen whole months.

    Every explicit unknown amount keeps the offer incomplete, even when quantity
    is zero. An incomplete offer excludes cheapest selection for the whole draft.
    Precision 100 exceeds the 80 significant digits possible for twenty products
    of bounded 38-digit inputs, multiplied by at most sixty months and summed.
    """
    validate_comparison(body)
    results, totals = [], []
    with localcontext(Context(prec=100, rounding=ROUND_HALF_UP, Emin=-999999, Emax=999999)):
        for offer in body["offers"]:
            subtotal, missing = Decimal(0), []
            for line in offer["lines"]:
                amount = line["unit_amount"]
                if amount is None:
                    missing.append(line["id"])
                    continue
                quantity = _decimal(line["quantity"])
                multiplier = body["period_months"] if line["cadence"] == "MONTHLY" else 1
                subtotal += quantity * _decimal(amount) * multiplier
            complete = not missing
            totals.append(subtotal if complete else None)
            results.append(
                {
                    "id": offer["id"],
                    "name": offer["name"],
                    "known_subtotal": _plain_decimal(subtotal),
                    "complete_total": _plain_decimal(subtotal) if complete else None,
                    "missing_line_ids": missing,
                }
            )
    complete = all(total is not None for total in totals)
    minimum = min(totals) if complete else None
    return {
        "currency": body["currency"],
        "period_months": body["period_months"],
        "status": "COMPLETE" if complete else "INCOMPLETE",
        "offers": results,
        "cheapest_offer_ids": [
            result["id"] for result, total in zip(results, totals) if complete and total == minimum
        ],
        "disclaimer": DISCLAIMER,
    }
