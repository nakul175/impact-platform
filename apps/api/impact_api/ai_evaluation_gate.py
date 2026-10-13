"""Fail-closed, code-owned evaluation gate for controlled AI exposure."""

import json
from pathlib import Path

from .domain import DomainError

ROOT = Path(__file__).resolve().parents[3]
MANIFESTS = ROOT / "config" / "ai-evaluations"
CRITICAL_KINDS = {"CROSS_TENANT_LEAK", "UNSUPPORTED_CRITICAL_CLAIM", "UNAUTHORISED_ACTION"}


def _invalid():
    raise DomainError("SERVICE_UNAVAILABLE", 503, reason="AI_EVALUATION_NOT_PASSED")


def require_exposure(use_case, configuration):
    """Return the manifest only when this exact configuration has passed every release gate."""
    path = MANIFESTS / (use_case.lower().replace("_", "-") + ".json")
    try:
        manifest = json.loads(path.read_text())
    except (OSError, ValueError, TypeError):
        _invalid()
    required = {
        "schema_version",
        "use_case",
        "owner",
        "configuration",
        "held_out_dataset_ref",
        "expected_judgements",
        "language_sector_matrix",
        "release_report_ref",
        "regression",
        "critical_findings",
        "exceptions",
    }
    if set(manifest) != required or manifest["use_case"] != use_case:
        _invalid()
    if manifest["configuration"] != configuration or manifest["regression"] != "PASSED":
        _invalid()
    if not all(
        isinstance(manifest[field], str) and manifest[field].strip()
        for field in ("owner", "held_out_dataset_ref", "release_report_ref")
    ):
        _invalid()
    if (
        not isinstance(manifest["expected_judgements"], list)
        or not manifest["expected_judgements"]
        or any(not isinstance(item, str) or not item.strip() for item in manifest["expected_judgements"])
    ):
        _invalid()
    matrix = manifest["language_sector_matrix"]
    if (
        not isinstance(matrix, list)
        or not matrix
        or any(
            not isinstance(item, dict)
            or set(item) != {"language", "sector"}
            or any(not isinstance(value, str) or not value.strip() for value in item.values())
            for item in matrix
        )
    ):
        _invalid()
    findings = manifest["critical_findings"]
    if not isinstance(findings, list) or any(
        not isinstance(item, dict) or item.get("kind") in CRITICAL_KINDS for item in findings
    ):
        _invalid()
    exceptions = manifest["exceptions"]
    if not isinstance(exceptions, list) or any(
        not isinstance(item, dict)
        or not isinstance(item.get("justification"), str)
        or not item["justification"].strip()
        for item in exceptions
    ):
        _invalid()
    return manifest
