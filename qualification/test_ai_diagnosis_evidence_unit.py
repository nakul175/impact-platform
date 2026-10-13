"""Unintegrated selector-shape checks; native authority results remain separate."""

from copy import deepcopy
from uuid import uuid4

import pytest

from impact_api.ai_diagnosis_evidence import validate_references
from impact_api.domain import DomainError


def reference():
    return {"object_id": str(uuid4()), "revision_id": str(uuid4())}


def test_exact_historical_revision_selectors_are_preserved_without_normalization():
    refs = [reference() for _ in range(5)]
    original = deepcopy(refs)
    validate_references(refs)
    assert refs == original
    validate_references([])


@pytest.mark.parametrize(
    "fault",
    [
        "null",
        "object",
        "too_many",
        "duplicate",
        "title",
        "tenant",
        "missing",
        "uppercase",
        "short_uuid",
        "number",
        "null_id",
    ],
)
def test_ambiguous_unbounded_and_metadata_bearing_selectors_are_refused(fault):
    refs = [reference()]
    if fault == "null":
        refs = None
    elif fault == "object":
        refs = refs[0]
    elif fault == "too_many":
        refs = [reference() for _ in range(6)]
    elif fault == "duplicate":
        refs += deepcopy(refs)
    elif fault in {"title", "tenant"}:
        refs[0][fault] = "Synthetic private metadata"
    elif fault == "missing":
        del refs[0]["revision_id"]
    elif fault == "uppercase":
        refs[0]["object_id"] = "ABCDEFAB-1234-1234-1234-ABCDEFABCDEF"
    elif fault == "short_uuid":
        refs[0]["object_id"] = refs[0]["object_id"].replace("-", "")
    elif fault == "number":
        refs[0]["revision_id"] = 42
    else:
        refs[0]["revision_id"] = None
    original = deepcopy(refs)
    with pytest.raises(DomainError) as caught:
        validate_references(refs)
    assert caught.value.code == "VALIDATION_FAILED"
    assert caught.value.reason == "DIAGNOSIS_EVIDENCE_INVALID"
    assert refs == original
