"""Qualification of snapshot-bound internal report approval and deterministic export."""
# ruff: noqa: F811

import uuid

from test_live_application import cmd, expect
from test_measurement import get, create, action, submit, approve  # noqa: F401


def package_data(live, **changes):
    template = live.records["report_template"]
    snapshot = live.records["snapshot"]
    result = live.records["pooled_result"]
    evidence = live.records["evidence_a"]
    data = {
        "template_version": template["revision_id"],
        "snapshot_id": snapshot["object_id"],
        "language": "en",
        "audience_class": "INTERNAL",
        "sections": [
            {
                "section_code": "results",
                "heading": "Verified results",
                "narrative": "Safe water access was verified. <script>alert('x')</script>",
                "bindings": [
                    {
                        "binding_code": "water",
                        "result_revision": result["revision_id"],
                        "display_decimals": 2,
                        "unit": "PERCENT",
                    }
                ],
                "evidence_revisions": [evidence["revision_id"]],
            }
        ],
    }
    return {**data, **changes}


def test_report_package_approval_freezes_binding_and_exports_escaped_html(live):
    report = create(live, "reports", package_data(live))
    workflow = submit(live, "reports", report)
    candidate = get(live, "workflows", workflow["object_id"] + "/candidate", actor="reviewer")
    assert candidate["kind"] == "Report"
    approve(live, workflow)
    approved = get(live, "reports", report["object_id"])
    assert approved["lifecycle_state"] == "Approved"
    response = live.request(live.path("reports", report["object_id"]) + "/export")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert response.headers["etag"].startswith('"')
    assert "46.36 PERCENT" in response.text
    assert "<script>" not in response.text and "&lt;script&gt;" in response.text
    assert approved["revision_id"] in response.text
    with live.db() as c:
        binding = c.execute(
            "SELECT * FROM impact.report_package_binding WHERE report_id=%s",
            (report["object_id"],),
        ).fetchone()
        assert str(binding["report_revision"]) == approved["revision_id"]
        assert bytes(binding["reconciliation_digest"]).hex() in response.text


def test_report_submit_requires_complete_snapshot_reconciled_package(live):
    incomplete = create(
        live,
        "reports",
        {"language": "en", "audience_class": "INTERNAL", "sections": []},
    )
    denied = action(
        live,
        "reports",
        incomplete,
        "submit",
        {"workflow_version": get(live, "workflow-templates")["items"][0]["revision_id"]},
        status=422,
    )
    assert denied["reason_code"] == "SUBMISSION_INCOMPLETE"
    data = package_data(live)
    data["sections"][0]["bindings"][0]["display_decimals"] = 3
    denied = expect(live.request(live.path("reports"), method="POST", body=cmd(data)), 422)
    assert denied["code"] == "INCOMPATIBLE_MEASURE"


def test_report_template_requirements_and_internal_audience_are_enforced(live):
    data = package_data(live)
    data["sections"][0]["section_code"] = "other"
    report = create(live, "reports", data)
    denied = action(
        live,
        "reports",
        report,
        "submit",
        {"workflow_version": get(live, "workflow-templates")["items"][0]["revision_id"]},
        status=422,
    )
    assert denied["reason_code"] == "REQUIRED_REPORT_SECTION_MISSING"
    denied = expect(
        live.request(
            live.path("reports"),
            method="POST",
            body=cmd(package_data(live, audience_class="PUBLIC")),
        ),
        403,
    )
    assert denied["reason_code"] == "INTERNAL_REPORTS_ONLY"


def test_report_export_requires_approved_binding_and_tenant_access(live):
    report = create(live, "reports", package_data(live))
    denied = expect(live.request(live.path("reports", report["object_id"]) + "/export"), 409)
    assert denied["reason_code"] == "APPROVED_REPORT_REQUIRED"
    expect(
        live.request(
            live.path("reports", report["object_id"]) + "/export",
            actor="other_tenant",
        ),
        404,
    )
    missing = str(uuid.uuid4())
    expect(live.request(live.path("reports", missing) + "/export"), 404)
