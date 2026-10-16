"""Focused pure checks for FR-EVA-002 sampling methodology."""

import json
from pathlib import Path
import pytest
from impact_api.domain import DomainError
from impact_api.evaluation_methodology import _validate, sample_export

ROOT = Path(__file__).resolve().parents[1]


def methodology(**changes):
    value = {
        "methodology_revision": "2",
        "strata": [
            {"code": "A", "eligible_count": 100, "sampled_count": 10, "nonresponse_count": 2, "weight": "10"},
            {"code": "B", "eligible_count": 50, "sampled_count": 5, "nonresponse_count": 1, "weight": "10"},
        ],
        "nonresponse_rules": "Retain missingness",
        "expansion_method": "POST_STRATIFIED_WEIGHTED_SUM",
    }
    value.update(changes)
    return value


def test_denominator_and_population_expansion_are_explicit():
    result = sample_export(methodology(), True, True)
    assert result["eligible_denominator"] == 150 and result["sample_count"] == 15
    assert (
        result["population_estimate"] == "150"
        and result["sample_count_label"] == "SAMPLE_COUNT_NOT_ALL_BENEFICIARIES"
    )


def test_missing_or_invalid_weights_never_default_to_one():
    with pytest.raises(DomainError):
        sample_export(
            methodology(
                strata=[
                    {
                        "code": "A",
                        "eligible_count": 2,
                        "sampled_count": 1,
                        "nonresponse_count": 0,
                        "weight": None,
                    }
                ]
            ),
            True,
            False,
        )
    with pytest.raises(DomainError):
        _validate(
            methodology(
                strata=[
                    {
                        "code": "A",
                        "eligible_count": 2,
                        "sampled_count": 1,
                        "nonresponse_count": 0,
                        "weight": "0",
                    }
                ]
            )
        )


def test_population_estimate_requires_weighted_output():
    with pytest.raises(DomainError):
        sample_export(methodology(), False, True)


def test_nonresponse_cannot_exceed_sample():
    with pytest.raises(DomainError):
        _validate(
            methodology(
                strata=[
                    {
                        "code": "A",
                        "eligible_count": 2,
                        "sampled_count": 1,
                        "nonresponse_count": 2,
                        "weight": "2",
                    }
                ]
            )
        )


def test_policy_exposes_dedicated_operations_and_independent_review():
    operations = {
        r["operation_id"]: r
        for r in json.loads((ROOT / "packages/contracts/access-policy.json").read_text())["operations"]
    }
    expected = {
        "create_evaluation_methodology",
        "list_evaluation_methodologies",
        "read_evaluation_methodology",
        "list_evaluation_methodology_history",
        "amend_evaluation_methodology",
        "review_evaluation_methodology",
        "export_evaluation_sample",
    }
    assert expected <= operations.keys()
    assert operations["review_evaluation_methodology"]["independence_required"] is True
