"""Pure deterministic draft comparisons with bounded, synthetic self-reported input."""

from copy import deepcopy
from decimal import Decimal, ROUND_DOWN, localcontext

import pytest

from impact_api.ai_pilot_outcomes import DISCLAIMER, evaluate_pilot_outcomes, validate_pilot_outcomes
from impact_api.domain import DomainError


def sample(**changes):
    return {
        "sample_size": 10,
        "total_drafting_minutes": "100",
        "total_review_minutes": "20",
        "factual_corrections": 2,
        **changes,
    }


def body(**changes):
    return {
        "task_label": "Draft a synthetic newsletter",
        "baseline": sample(),
        "pilot": sample(total_drafting_minutes="40", total_review_minutes="20", factual_corrections=4),
        "comparable": True,
        "notes": "Synthetic public examples only; no causal interpretation.",
        **changes,
    }


def invalid(request):
    with pytest.raises(DomainError) as caught:
        evaluate_pilot_outcomes(request)
    assert caught.value.code == "VALIDATION_FAILED"
    assert caught.value.reason == "AI_PILOT_OUTCOMES_INVALID"
    assert caught.value.status == 422


def test_comparison_includes_human_review_time_and_never_claims_accepted_impact():
    result = evaluate_pilot_outcomes(body())
    assert result["baseline"] == {
        "total_minutes": "120",
        "minutes_per_item": "12",
        "factual_corrections_per_item": "0.2",
    }
    assert result["pilot"] == {
        "total_minutes": "60",
        "minutes_per_item": "6",
        "factual_corrections_per_item": "0.4",
    }
    assert result["improvement"] == {
        "status": "DEFINED",
        "percent": "50",
        "reason": "COMPARABLE_SAMPLES",
    }
    assert result["status"] == "SELF_REPORTED_DRAFT"
    assert result["disclaimer"] == DISCLAIMER
    assert "not a quality score" in result["disclaimer"]
    assert "accepted impact, ROI, certification or causal benefit" in result["disclaimer"]
    assert not {"approved", "quality_score", "roi", "official_result"}.intersection(result)


def test_higher_review_effort_can_make_a_faster_drafting_pilot_slower_overall():
    result = evaluate_pilot_outcomes(
        body(pilot=sample(total_drafting_minutes="20", total_review_minutes="160"))
    )
    assert result["pilot"]["total_minutes"] == "180"
    assert result["pilot"]["minutes_per_item"] == "18"
    assert result["improvement"]["percent"] == "-50"


def test_different_sample_sizes_are_normalized_before_comparison():
    result = evaluate_pilot_outcomes(
        body(pilot=sample(sample_size=20, total_drafting_minutes="80", total_review_minutes="40"))
    )
    assert result["baseline"]["total_minutes"] == result["pilot"]["total_minutes"] == "120"
    assert result["baseline"]["minutes_per_item"] == "12"
    assert result["pilot"]["minutes_per_item"] == "6"
    assert result["improvement"]["percent"] == "50"
    assert "does not establish equivalent task difficulty" in result["disclaimer"]


def test_recurring_values_round_half_up_at_display_without_reusing_displayed_values():
    result = evaluate_pilot_outcomes(
        body(
            baseline=sample(sample_size=3, total_drafting_minutes="1", total_review_minutes="0"),
            pilot=sample(sample_size=3, total_drafting_minutes="0.5", total_review_minutes="0"),
        )
    )
    assert result["baseline"]["minutes_per_item"] == "0.333333"
    assert result["pilot"]["minutes_per_item"] == "0.166667"
    assert result["baseline"]["factual_corrections_per_item"] == "0.666667"
    assert result["improvement"]["percent"] == "50"


def test_display_rounds_exact_half_up_and_normalizes_zero():
    result = evaluate_pilot_outcomes(
        body(
            baseline=sample(sample_size=1, total_drafting_minutes="0.0000005", total_review_minutes="0"),
            pilot=sample(sample_size=1, total_drafting_minutes="0.0000004", total_review_minutes="0"),
        )
    )
    assert result["baseline"]["total_minutes"] == "0.000001"
    assert result["pilot"]["total_minutes"] == "0"
    assert result["improvement"]["percent"] == "20"


def test_zero_baseline_is_undefined_instead_of_zero_or_infinite_improvement():
    result = evaluate_pilot_outcomes(
        body(baseline=sample(total_drafting_minutes="0", total_review_minutes="0"))
    )
    assert result["baseline"]["total_minutes"] == "0"
    assert result["improvement"] == {"status": "UNDEFINED", "percent": None, "reason": "ZERO_BASELINE"}


def test_nonzero_raw_baseline_remains_defined_even_when_display_rounds_to_zero():
    result = evaluate_pilot_outcomes(
        body(
            baseline=sample(total_drafting_minutes="0.000000000001", total_review_minutes="0"),
            pilot=sample(total_drafting_minutes="0", total_review_minutes="0"),
        )
    )
    assert result["baseline"]["minutes_per_item"] == "0"
    assert result["improvement"]["percent"] == "100"
    assert result["improvement"]["status"] == "DEFINED"


@pytest.mark.parametrize("zero_baseline", [False, True])
def test_reported_incomparability_keeps_observations_but_withholds_percentage(zero_baseline):
    request = body(comparable=False)
    if zero_baseline:
        request["baseline"] = sample(total_drafting_minutes="0", total_review_minutes="0")
    result = evaluate_pilot_outcomes(request)
    assert result["source"]["baseline"] == request["baseline"]
    assert result["pilot"]["total_minutes"] == "60"
    assert result["improvement"] == {
        "status": "UNDEFINED",
        "percent": None,
        "reason": "SAMPLES_NOT_COMPARABLE",
    }
    assert "reported as not comparable" in result["disclaimer"]


def test_exact_sources_are_preserved_and_results_cannot_mutate_the_request():
    request = body(
        task_label="  Synthetic task  ",
        baseline=sample(total_drafting_minutes="100.000000000001", total_review_minutes="20.00"),
    )
    before = deepcopy(request)
    result = evaluate_pilot_outcomes(request)
    assert request == before
    assert result["source"]["baseline"]["total_drafting_minutes"] == "100.000000000001"
    assert result["source"]["baseline"]["total_review_minutes"] == "20.00"
    assert result["task_label"] == request["task_label"]
    result["source"]["baseline"]["total_review_minutes"] = "999"
    assert request == before


def test_calculation_is_deterministic_and_independent_of_callers_decimal_context():
    request = body(
        baseline=sample(total_drafting_minutes="0.123456789012", total_review_minutes="10.1"),
        pilot=sample(sample_size=3, total_drafting_minutes="0.1", total_review_minutes="2.000000000001"),
    )
    expected = evaluate_pilot_outcomes(request)
    with localcontext() as caller:
        caller.prec = 5
        caller.rounding = ROUND_DOWN
        assert evaluate_pilot_outcomes(request) == expected
        assert caller.prec == 5
        assert caller.rounding == ROUND_DOWN
    assert evaluate_pilot_outcomes(request) == expected


def test_bounds_accept_maximum_source_precision_counts_and_text_lengths():
    request = body(
        task_label="x" * 150,
        notes="x" * 1000,
        baseline=sample(
            sample_size=10000,
            total_drafting_minutes="99999999999999999999999999.999999999999",
            total_review_minutes="0",
            factual_corrections=1000000,
        ),
        pilot=sample(sample_size=1, total_drafting_minutes="1", total_review_minutes="0"),
    )
    # Validation accepts the maximum numeric source even if its six-place display overflows.
    assert validate_pilot_outcomes(request) is None
    request["baseline"]["total_drafting_minutes"] = "99999999999999999999999999.999999"
    result = evaluate_pilot_outcomes(request)
    assert result["baseline"]["total_minutes"] == "99999999999999999999999999.999999"
    assert result["baseline"]["factual_corrections_per_item"] == "100"


@pytest.mark.parametrize("key", ["task_label", "baseline", "pilot", "comparable", "notes"])
def test_top_level_required_fields_are_not_defaulted(key):
    request = body()
    del request[key]
    invalid(request)


@pytest.mark.parametrize("sample_key", ["baseline", "pilot"])
@pytest.mark.parametrize(
    "field", ["sample_size", "total_drafting_minutes", "total_review_minutes", "factual_corrections"]
)
def test_sample_required_fields_are_not_defaulted(sample_key, field):
    request = body()
    del request[sample_key][field]
    invalid(request)


@pytest.mark.parametrize("key", ["approved", "author", "official_result", "operation_id"])
def test_top_level_body_is_closed(key):
    invalid(body(**{key: True}))


@pytest.mark.parametrize("sample_key", ["baseline", "pilot"])
def test_nested_samples_are_closed(sample_key):
    request = body()
    request[sample_key]["quality_score"] = "100"
    invalid(request)


@pytest.mark.parametrize("payload", [None, [], "{}", 1, True])
def test_non_object_body_is_rejected(payload):
    invalid(payload)


@pytest.mark.parametrize(
    "field,value",
    [
        ("task_label", ""),
        ("task_label", " \n\t "),
        ("task_label", "x" * 151),
        ("task_label", None),
        ("task_label", 12),
        ("notes", "x" * 1001),
        ("notes", None),
        ("notes", False),
        ("comparable", "true"),
        ("comparable", 1),
        ("comparable", 0),
        ("comparable", None),
        ("baseline", None),
        ("pilot", []),
    ],
)
def test_text_boolean_and_nested_shape_validation(field, value):
    invalid(body(**{field: value}))


@pytest.mark.parametrize("sample_key", ["baseline", "pilot"])
@pytest.mark.parametrize(
    "field,value",
    [
        ("sample_size", 0),
        ("sample_size", -1),
        ("sample_size", 10001),
        ("sample_size", 1.0),
        ("sample_size", "1"),
        ("sample_size", True),
        ("factual_corrections", -1),
        ("factual_corrections", 1000001),
        ("factual_corrections", 0.0),
        ("factual_corrections", "0"),
        ("factual_corrections", False),
    ],
)
def test_counts_require_bounded_integers_without_boolean_or_numeric_coercion(sample_key, field, value):
    request = body()
    request[sample_key][field] = value
    invalid(request)


@pytest.mark.parametrize("field", ["total_drafting_minutes", "total_review_minutes"])
@pytest.mark.parametrize(
    "value",
    [
        -1,
        1,
        1.0,
        Decimal("1"),
        True,
        None,
        "",
        "-1",
        "-0",
        "+1",
        "01",
        ".1",
        "1.",
        "1e2",
        "1E-2",
        "NaN",
        "Infinity",
        " 1",
        "1 ",
        "1\n",
        "1,000",
        "١",
        "100000000000000000000000000",
        "0.1234567890123",
    ],
)
def test_minutes_require_bounded_plain_decimal_strings(field, value):
    request = body()
    request["pilot"][field] = value
    invalid(request)


def test_total_overflow_is_rejected_rather_than_rounded_into_an_unbounded_number():
    invalid(
        body(baseline=sample(total_drafting_minutes="99999999999999999999999999", total_review_minutes="1"))
    )


def test_percentage_overflow_is_rejected_instead_of_an_unbounded_negative_percentage():
    invalid(
        body(
            baseline=sample(total_drafting_minutes="0.000000000001", total_review_minutes="0"),
            pilot=sample(total_drafting_minutes="99999999999999999999999999", total_review_minutes="0"),
        )
    )


def test_incomparable_samples_do_not_attempt_a_percentage_that_would_overflow():
    result = evaluate_pilot_outcomes(
        body(
            comparable=False,
            baseline=sample(total_drafting_minutes="0.000000000001", total_review_minutes="0"),
            pilot=sample(total_drafting_minutes="99999999999999999999999999", total_review_minutes="0"),
        )
    )
    assert result["improvement"]["percent"] is None
