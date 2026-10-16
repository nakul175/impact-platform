"""Focused pure checks for FR-DQ-007 suggestion-only anomaly assistance."""

from decimal import Decimal
import json
from pathlib import Path

from impact_api.imports import robust_outlier


ROOT = Path(__file__).resolve().parents[1]


def test_robust_method_records_a_spike_without_reclassifying_normal_values():
    history = [Decimal(value) for value in ["9", "10", "10", "10", "11", "11"]]
    assert robust_outlier(Decimal("10"), history) is None
    finding = robust_outlier(Decimal("100"), history)
    assert finding and Decimal(finding["score"]) > 3
    assert finding["median"] == "10"


def test_contract_exposes_dedicated_current_authority_operations():
    policy = json.loads((ROOT / "packages/contracts/access-policy.json").read_text())
    operations = {row["operation_id"]: row for row in policy["operations"]}
    expected = {
        "create_anomaly_run",
        "list_anomaly_runs",
        "read_anomaly_run",
        "list_anomaly_findings",
        "read_anomaly_finding",
        "review_anomaly_finding",
    }
    assert expected <= operations.keys()
    assert operations["review_anomaly_finding"]["capability"] == "dashboards.draft.edit"
    assert operations["list_anomaly_findings"]["capability"] == "dashboards.read"


def test_registry_migration_denies_worker_access_to_runs_and_feedback():
    migration = (ROOT / "infrastructure/migrations/0103_anomaly_assistance_kinds.sql").read_text()
    assert "AnomalyRun" in migration and "AnomalyFinding" in migration
    assert migration.count("AS RESTRICTIVE") == 2
    assert "TO impact_worker" in migration
