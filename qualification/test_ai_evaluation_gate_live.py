"""Exact-candidate evaluation-gate qualification for FR-AI-015 / APL-344."""

import json

import pytest

from impact_api import ai_evaluation_gate
from impact_api.domain import DomainError


def _manifest(configuration):
    return {
        "schema_version": 1,
        "use_case": "ADVISORY_DRAFT",
        "owner": "Synthetic platform release owner",
        "configuration": configuration,
        "held_out_dataset_ref": "evidence://synthetic-held-out-v1",
        "expected_judgements": ["No cross-tenant disclosure", "Human review retained"],
        "language_sector_matrix": [{"language": "en", "sector": "GENERAL"}],
        "release_report_ref": "evidence://synthetic-release-report-v1",
        "regression": "PASSED",
        "critical_findings": [],
        "exceptions": [],
    }


def test_exact_ready_manifest_passes_and_drift_fails_closed(tmp_path, monkeypatch):
    configuration = {
        "model": "synthetic-model-v1",
        "prompt_version": "synthetic-prompt-v1",
        "retrieval": "NONE",
        "tools": [],
        "policy_gate_version": "synthetic-policy-v1",
    }
    path = tmp_path / "advisory-draft.json"
    path.write_text(json.dumps(_manifest(configuration)))
    monkeypatch.setattr(ai_evaluation_gate, "MANIFESTS", tmp_path)

    assert ai_evaluation_gate.require_exposure("ADVISORY_DRAFT", configuration)["owner"]
    with pytest.raises(DomainError) as drift:
        ai_evaluation_gate.require_exposure(
            "ADVISORY_DRAFT", {**configuration, "prompt_version": "unreviewed-prompt"}
        )
    assert drift.value.status == 503 and drift.value.reason == "AI_EVALUATION_NOT_PASSED"


@pytest.mark.parametrize(
    "change",
    [
        {"regression": "PENDING"},
        {"critical_findings": [{"kind": "CROSS_TENANT_LEAK"}]},
        {"exceptions": [{"kind": "SPECIALIST", "justification": ""}]},
        {"owner": ""},
    ],
)
def test_incomplete_critical_or_unjustified_manifest_fails_closed(tmp_path, monkeypatch, change):
    configuration = {"model": "synthetic-model-v1"}
    path = tmp_path / "advisory-draft.json"
    path.write_text(json.dumps({**_manifest(configuration), **change}))
    monkeypatch.setattr(ai_evaluation_gate, "MANIFESTS", tmp_path)

    with pytest.raises(DomainError) as blocked:
        ai_evaluation_gate.require_exposure("ADVISORY_DRAFT", configuration)
    assert blocked.value.status == 503 and blocked.value.reason == "AI_EVALUATION_NOT_PASSED"


def test_repository_manifest_truthfully_remains_not_ready():
    with pytest.raises(DomainError) as blocked:
        ai_evaluation_gate.require_exposure(
            "ADVISORY_DRAFT",
            json.loads((ai_evaluation_gate.MANIFESTS / "advisory-draft.json").read_text())["configuration"],
        )
    assert blocked.value.reason == "AI_EVALUATION_NOT_PASSED"
