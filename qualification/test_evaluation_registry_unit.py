"""Focused pure checks for FR-EVA-001 controlled evaluation registration."""

import json
from pathlib import Path

import pytest

from impact_api.domain import DomainError
from impact_api.evaluation_registry import required_stage_documents, validate_stage_transition

ROOT = Path(__file__).resolve().parents[1]


def test_sensitive_stage_documents_are_server_owned():
    payload = {
        "required_documents": {"FIELD_COLLECTION": [], "PUBLICATION": []},
        "sensitive_processing": True,
    }
    assert required_stage_documents(payload, "FIELD_COLLECTION") == {
        "METHODOLOGY",
        "ETHICS",
        "SAFEGUARDING",
    }
    assert "DISCLOSURE_REVIEW" in required_stage_documents(payload, "PUBLICATION")


def test_stage_order_is_monotonic():
    validate_stage_transition("REGISTERED", "FIELD_COLLECTION")
    validate_stage_transition("FIELD_COLLECTION", "PUBLICATION")
    with pytest.raises(DomainError):
        validate_stage_transition("REGISTERED", "PUBLICATION")
    with pytest.raises(DomainError):
        validate_stage_transition("PUBLICATION", "FIELD_COLLECTION")


def test_contract_has_dedicated_evaluation_operations():
    operations = {
        row["operation_id"]: row
        for row in json.loads((ROOT / "packages/contracts/access-policy.json").read_text())["operations"]
    }
    expected = {
        "create_evaluation_registration",
        "list_evaluation_registrations",
        "get_evaluations",
        "list_evaluation_stage_gates",
        "evaluate_evaluation_stage_gate",
    }
    assert expected <= operations.keys()
    assert operations["evaluate_evaluation_stage_gate"]["capability"] == "evaluations.draft.edit"
    assert operations["evaluate_evaluation_stage_gate"]["independence_required"] is True


def test_registry_migration_fences_worker():
    migration = (ROOT / "infrastructure/migrations/0104_evaluation_registration_kind.sql").read_text()
    assert "EvaluationRegistration" in migration
    assert migration.count("AS RESTRICTIVE") == 2
    assert "TO impact_worker" in migration
