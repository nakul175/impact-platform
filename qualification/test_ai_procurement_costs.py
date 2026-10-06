"""Pure cost draft checks; no database, supplier, provider or procurement approval."""

from copy import deepcopy
from decimal import Decimal, localcontext

import pytest

from impact_api.ai_procurement_costs import CATEGORIES, compare_costs, validate_comparison
from impact_api.domain import DomainError


def cost_line(identifier="subscription", quantity="1", amount="10", cadence="MONTHLY", **overrides):
    return {
        "id": identifier,
        "category": "SUBSCRIPTION",
        "label": "Synthetic supplied amount",
        "quantity": quantity,
        "unit_amount": amount,
        "cadence": cadence,
        **overrides,
    }


def draft():
    return {
        "currency": "INR",
        "period_months": 12,
        "offers": [{"id": "offer-a", "name": "Synthetic offer A", "lines": [cost_line()]}],
    }


def test_setup_recurring_usage_and_training_have_exact_period_totals():
    body = draft()
    body["offers"][0]["lines"] = [
        cost_line("setup", "1", "125", "ONE_OFF", category="SETUP"),
        cost_line("subscription", "3", "10"),
        cost_line("training", "2.5", "40", "ONE_OFF", category="TRAINING"),
        cost_line("usage", "1.25", "0.008", category="USAGE"),
    ]
    body["offers"].append({"id": "offer-b", "name": "Synthetic offer B", "lines": [cost_line(amount="50")]})
    result = compare_costs(body)
    assert result["currency"] == "INR" and result["period_months"] == 12
    assert result["offers"][0]["known_subtotal"] == "585.12"
    assert result["offers"][0]["complete_total"] == "585.12"
    assert result["offers"][1]["complete_total"] == "600"
    assert result["status"] == "COMPLETE" and result["cheapest_offer_ids"] == ["offer-a"]
    assert "Draft" in result["disclaimer"] and len(result["disclaimer"]) <= 250


def test_an_unknown_line_never_becomes_zero_or_a_false_cheapest_offer():
    body = draft()
    body["offers"][0]["lines"].extend(
        [
            cost_line("training", amount=None, cadence="ONE_OFF", category="TRAINING"),
            cost_line("exit", amount=None, cadence="ONE_OFF", category="EXIT"),
        ]
    )
    body["offers"].append({"id": "offer-b", "name": "Synthetic offer B", "lines": [cost_line(amount="20")]})
    result = compare_costs(body)
    assert result["status"] == "INCOMPLETE" and result["cheapest_offer_ids"] == []
    assert result["offers"][0] == {
        "id": "offer-a",
        "name": "Synthetic offer A",
        "known_subtotal": "120",
        "complete_total": None,
        "missing_line_ids": ["training", "exit"],
    }
    assert result["offers"][1]["complete_total"] == "240"


def test_unknown_amount_with_zero_quantity_still_requires_an_explicit_amount():
    body = draft()
    body["offers"][0]["lines"] = [cost_line(quantity="0", amount=None)]
    result = compare_costs(body)
    assert result["offers"][0]["known_subtotal"] == "0"
    assert result["offers"][0]["complete_total"] is None
    assert result["status"] == "INCOMPLETE" and result["cheapest_offer_ids"] == []


def test_explicit_zero_costs_are_complete_and_equal_costs_preserve_every_tie():
    body = draft()
    body["offers"][0]["lines"] = [cost_line(amount="0.0000")]
    body["offers"].append({"id": "offer-b", "name": "Synthetic offer B", "lines": [cost_line(quantity="0")]})
    result = compare_costs(body)
    assert result["status"] == "COMPLETE" and result["cheapest_offer_ids"] == ["offer-a", "offer-b"]
    assert all(offer["complete_total"] == "0" for offer in result["offers"])
    assert all(offer["missing_line_ids"] == [] for offer in result["offers"])


def test_fractional_costs_are_summed_before_any_display_rounding():
    body = draft()
    body["offers"][0]["lines"] = [
        cost_line(f"component-{index}", amount="0.005", cadence="ONE_OFF") for index in range(3)
    ]
    assert compare_costs(body)["offers"][0]["complete_total"] == "0.015"


def test_twenty_maximum_products_retain_every_digit_independently_of_global_decimal_context():
    maximum = "9" * 26 + "." + "9" * 12
    body = draft()
    body["period_months"] = 60
    body["offers"][0]["lines"] = [
        cost_line(f"component-{index}", quantity=maximum, amount=maximum) for index in range(20)
    ]
    # Independent integer arithmetic: each input is a 38-digit integer scaled by 10**12.
    scaled_total = 20 * 60 * (10**38 - 1) ** 2
    digits = str(scaled_total)
    expected = (digits[:-24] + "." + digits[-24:]).rstrip("0").rstrip(".")
    with localcontext() as context:
        context.prec, context.Emax, context.Emin = 2, 2, -2
        assert compare_costs(body)["offers"][0]["complete_total"] == expected


def test_smallest_inputs_preserve_twenty_four_fractional_places_without_exponents():
    body = draft()
    body["offers"][0]["lines"] = [
        cost_line(quantity="0.000000000001", amount="0.000000000001", cadence="ONE_OFF")
    ]
    assert compare_costs(body)["offers"][0]["complete_total"] == "0.000000000000000000000001"


@pytest.mark.parametrize("months", [1, 60])
def test_period_boundaries_include_one_and_sixty_months(months):
    body = draft()
    body["period_months"] = months
    assert compare_costs(body)["offers"][0]["complete_total"] == str(months * 10)


@pytest.mark.parametrize("category", CATEGORIES)
def test_every_declared_category_accepts_an_explicit_bounded_cost(category):
    body = draft()
    body["offers"][0]["lines"][0]["category"] = category
    assert compare_costs(body)["offers"][0]["complete_total"] == "120"


def test_comparison_and_validation_never_mutate_supplied_cost_drafts():
    body = draft()
    before = deepcopy(body)
    validate_comparison(body)
    first = compare_costs(body)
    second = compare_costs(body)
    assert body == before and first == second
    first["offers"][0]["name"] = "Changed response only"
    assert body == before


@pytest.mark.parametrize("field", ["quantity", "unit_amount"])
@pytest.mark.parametrize(
    "value",
    [
        "-1",
        "-0",
        "+1",
        "1e3",
        "1E-3",
        "NaN",
        "Infinity",
        "0,1",
        "01",
        " 1",
        "1 ",
        "1.",
        ".1",
        "",
        "9" * 27,
        "0." + "1" * 13,
        True,
        False,
        1,
        1.0,
        Decimal("1"),
        [],
        {},
    ],
)
def test_cost_inputs_refuse_negative_exponential_nonfinite_coerced_or_out_of_storage_bounds(field, value):
    body = draft()
    body["offers"][0]["lines"][0][field] = value
    with pytest.raises(DomainError) as denied:
        compare_costs(body)
    assert denied.value.code == "VALIDATION_FAILED" and denied.value.status == 422
    assert denied.value.reason == "AI_PROCUREMENT_COSTS_INVALID"


@pytest.mark.parametrize("months", [True, False, 0, 61, -1, 12.0, "12", None])
def test_period_requires_a_bounded_integer_without_boolean_or_string_coercion(months):
    body = draft()
    body["period_months"] = months
    with pytest.raises(DomainError):
        compare_costs(body)


@pytest.mark.parametrize("currency", ["inr", "InR", " INR", "INR ", "US", "USDD", "123", True, None])
def test_currency_requires_three_uppercase_letters(currency):
    body = draft()
    body["currency"] = currency
    with pytest.raises(DomainError):
        compare_costs(body)


@pytest.mark.parametrize(
    "edit",
    [
        lambda body: body.update(approved=True),
        lambda body: body.pop("currency"),
        lambda body: body["offers"][0].update(currency="USD"),
        lambda body: body["offers"][0].pop("name"),
        lambda body: body["offers"][0]["lines"][0].update(currency="USD"),
        lambda body: body["offers"][0]["lines"][0].update(exchange_rate="1"),
        lambda body: body["offers"][0]["lines"][0].pop("unit_amount"),
        lambda body: body.update(offers=[]),
        lambda body: body.update(offers=None),
        lambda body: body.update(offers=tuple(body["offers"])),
        lambda body: body["offers"][0].update(lines=[]),
        lambda body: body["offers"][0].update(lines=None),
        lambda body: body["offers"][0].update(name=" "),
        lambda body: body["offers"][0].update(name="x" * 151),
        lambda body: body["offers"][0].update(name=12),
        lambda body: body["offers"][0].update(id="Invalid Slug"),
        lambda body: body["offers"][0].update(id="a" * 65),
        lambda body: body["offers"][0].update(id="1-offer"),
        lambda body: body["offers"][0]["lines"][0].update(id="bad slug"),
        lambda body: body["offers"][0]["lines"][0].update(label=""),
        lambda body: body["offers"][0]["lines"][0].update(label="x" * 151),
        lambda body: body["offers"][0]["lines"][0].update(quantity=None),
        lambda body: body["offers"][0]["lines"][0].update(category="TAX"),
        lambda body: body["offers"][0]["lines"][0].update(category=["SETUP"]),
        lambda body: body["offers"][0]["lines"][0].update(cadence="ANNUAL"),
        lambda body: body["offers"].append(deepcopy(body["offers"][0])),
        lambda body: body["offers"][0]["lines"].append(deepcopy(body["offers"][0]["lines"][0])),
    ],
)
def test_closed_cost_drafts_reject_missing_unknown_duplicate_and_unbounded_members(edit):
    body = draft()
    edit(body)
    with pytest.raises(DomainError) as denied:
        compare_costs(body)
    assert denied.value.reason == "AI_PROCUREMENT_COSTS_INVALID"


@pytest.mark.parametrize("count", [4, 5])
def test_four_offers_are_allowed_but_a_fifth_offer_is_refused(count):
    body = draft()
    body["offers"] = [
        {"id": f"offer-{index}", "name": f"Synthetic offer {index}", "lines": [cost_line()]}
        for index in range(count)
    ]
    if count == 4:
        assert len(compare_costs(body)["offers"]) == 4
    else:
        with pytest.raises(DomainError):
            compare_costs(body)


@pytest.mark.parametrize("count", [20, 21])
def test_twenty_lines_are_allowed_but_a_twenty_first_line_is_refused(count):
    body = draft()
    body["offers"][0]["lines"] = [cost_line(f"component-{index}") for index in range(count)]
    if count == 20:
        assert compare_costs(body)["offers"][0]["complete_total"] == "2400"
    else:
        with pytest.raises(DomainError):
            compare_costs(body)


@pytest.mark.parametrize("body", [None, [], "", False])
def test_nonobject_requests_return_only_a_generic_validation_failure(body):
    with pytest.raises(DomainError) as denied:
        compare_costs(body)
    assert denied.value.fields == [] and denied.value.message == "Check the supplied values."


def test_maximum_bounded_labels_and_identifiers_are_accepted_without_truncation():
    body = draft()
    body["offers"][0].update(id="a" * 64, name="n" * 150)
    body["offers"][0]["lines"][0].update(id="b" * 64, label="l" * 150)
    result = compare_costs(body)
    assert result["offers"][0]["id"] == "a" * 64 and result["offers"][0]["name"] == "n" * 150
