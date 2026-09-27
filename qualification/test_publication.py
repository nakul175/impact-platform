"""Numeric reconciliation and controlled, revocable report publication."""
# ruff: noqa: F811

from datetime import datetime, timedelta, timezone

import psycopg
import pytest

from impact_api.contracts import OPERATIONS
from test_live_application import cmd, expect
from test_measurement import get, create, action, submit, approve  # noqa: F401
from test_reporting import package_data


def approved_report(live, narrative="The verified result is {{water}}."):
    data = package_data(live)
    data["sections"][0]["narrative"] = narrative
    report = create(live, "reports", data)
    approve(live, submit(live, "reports", report))
    return get(live, "reports", report["object_id"])


def request_disclosure(live, report, *, allow_download=True, recipient=None, **changes):
    template = get(live, "workflow-templates")["items"][0]
    body = cmd(
        {
            "artifact_version": report["revision_id"],
            "recipients": [
                {
                    "membership_id": recipient or live.fixture["member_partner"],
                    "allow_download": allow_download,
                }
            ],
            "purpose": "PARTNER_REPORTING",
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "public": False,
            "workflow_version": template["revision_id"],
            **changes,
        }
    )
    receipt = expect(
        live.request(live.path("disclosure-requests"), method="POST", body=body),
        200,
    )
    return get(live, "workflows", receipt["object_id"]), body


def publish(live, report, disclosure, body=None):
    body = body or cmd(
        {
            "approved_candidate_revision": report["revision_id"],
            "disclosure_id": disclosure["object_id"],
        },
        report["revision_id"],
    )
    receipt = action(
        live,
        "reports",
        report,
        "publish",
        actor="reviewer",
        body=body,
    )
    return receipt, body


def test_narrative_numbers_require_exact_bindings_and_csv_is_deterministic(live):
    data = package_data(live)
    data["sections"][0]["narrative"] = "The narrative claims 200 participants."
    report = create(live, "reports", data)
    denied = action(
        live,
        "reports",
        report,
        "submit",
        {"workflow_version": get(live, "workflow-templates")["items"][0]["revision_id"]},
        status=422,
    )
    assert denied["reason_code"] == "UNBOUND_NARRATIVE_NUMBER"

    data = package_data(live)
    data["sections"][0]["narrative"] = "The verified result is {{unknown}}."
    report = create(live, "reports", data)
    denied = action(
        live,
        "reports",
        report,
        "submit",
        {"workflow_version": get(live, "workflow-templates")["items"][0]["revision_id"]},
        status=422,
    )
    assert denied["reason_code"] == "UNKNOWN_NARRATIVE_BINDING"

    report = approved_report(live)
    html = live.request(live.path("reports", report["object_id"]) + "/export")
    csv_export = live.request(live.path("reports", report["object_id"]) + "/export.csv")
    assert html.status_code == csv_export.status_code == 200
    assert "style-src 'sha256-" in html.headers["content-security-policy"]
    assert "unsafe-inline" not in html.headers["content-security-policy"]
    assert 'data-binding="water">46.36 PERCENT' in html.text
    assert csv_export.headers["content-type"].startswith("text/csv")
    assert csv_export.headers["content-disposition"].startswith("attachment;")
    assert "46.36,PERCENT" in csv_export.text
    assert report["revision_id"] in csv_export.text
    assert (
        csv_export.headers["etag"]
        == live.request(live.path("reports", report["object_id"]) + "/export.csv").headers["etag"]
    )


def test_controlled_publication_is_independently_reviewed_recipient_only_and_idempotent(live):
    report = approved_report(live)
    workflow, _ = request_disclosure(live, report)
    candidate = get(
        live,
        "workflows",
        workflow["object_id"] + "/candidate",
        actor="reviewer",
    )
    assert candidate["kind"] == "Disclosure"
    assert candidate["record"]["data"]["artifact_version"] == report["revision_id"]
    denied = action(
        live,
        "workflows",
        workflow,
        "approve",
        {
            "candidate_revision": workflow["data"]["candidate_revision"],
            "reason": "Self approval attempt",
        },
        status=403,
    )
    assert denied["reason_code"] == "INDEPENDENCE_REQUIRED"
    approve(live, workflow)
    disclosure = get(
        live,
        "disclosures",
        candidate["record"]["object_id"],
        actor="reviewer",
    )
    receipt, body = publish(live, report, disclosure)
    assert receipt["business_state"] == "Published"
    assert publish(live, report, disclosure, body)[0] == receipt

    hidden = live.request(
        live.path("publications", disclosure["object_id"]) + "/view",
        actor="author",
    )
    assert hidden.status_code == 404
    viewed = live.request(
        live.path("publications", disclosure["object_id"]) + "/view",
        actor="partner",
    )
    downloaded = live.request(
        live.path("publications", disclosure["object_id"]) + "/download.csv",
        actor="partner",
    )
    assert viewed.status_code == downloaded.status_code == 200
    assert "46.36 PERCENT" in viewed.text
    assert "46.36,PERCENT" in downloaded.text
    assert viewed.headers["etag"] and downloaded.headers["etag"]
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.report_publication_artifact WHERE disclosure_id=%s",
                (disclosure["object_id"],),
            ).fetchone()["n"]
            == 2
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.report_publication_access WHERE disclosure_id=%s",
                (disclosure["object_id"],),
            ).fetchone()["n"]
            == 2
        )
    with live.db() as c:
        c.execute("SET LOCAL ROLE impact_app")
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_b"],))
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.report_publication_artifact WHERE tenant_id=%s",
                (live.fixture["tenant_a"],),
            ).fetchone()["n"]
            == 0
        )
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            c.execute(
                "SELECT count(*) AS n FROM impact.report_publication_access WHERE tenant_id=%s",
                (live.fixture["tenant_a"],),
            )
    with live.db() as c:
        c.execute("SET LOCAL ROLE impact_app")
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            c.execute(
                "UPDATE impact.report_publication_artifact SET body=body WHERE disclosure_id=%s",
                (disclosure["object_id"],),
            )


def test_download_right_expiry_recipient_state_and_withdrawal_are_enforced(live):
    assert OPERATIONS["action_reports_publish"]["fresh_assurance_seconds"] == 300
    assert OPERATIONS["action_reports_withdraw"]["fresh_assurance_seconds"] == 300
    report = approved_report(live)
    workflow, _ = request_disclosure(live, report, allow_download=False)
    approve(live, workflow)
    disclosure_id = workflow["data"]["candidate_id"]
    disclosure = get(live, "disclosures", disclosure_id, actor="reviewer")
    publish(live, report, disclosure)
    assert (
        live.request(live.path("publications", disclosure_id) + "/view", actor="partner").status_code == 200
    )
    assert (
        live.request(
            live.path("publications", disclosure_id) + "/download.csv",
            actor="partner",
        ).status_code
        == 404
    )
    action(
        live,
        "reports",
        report,
        "withdraw",
        {"reason": "Superseded after a governed correction."},
        actor="reviewer",
    )
    assert (
        live.request(live.path("publications", disclosure_id) + "/view", actor="partner").status_code == 404
    )
    withdrawn = get(live, "disclosures", disclosure_id, actor="reviewer")
    assert withdrawn["lifecycle_state"] == "Withdrawn"
    assert withdrawn["data"]["withdrawal_reason"].startswith("Superseded")
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.report_publication_artifact WHERE disclosure_id=%s",
                (disclosure_id,),
            ).fetchone()["n"]
            == 2
        )


def test_disclosure_rejects_public_expired_duplicate_and_inactive_recipients(live):
    report = approved_report(live)
    _, valid = request_disclosure(live, report)
    data = valid["data"]
    denied = expect(
        live.request(
            live.path("disclosure-requests"),
            method="POST",
            body=cmd({**data, "public": True}),
        ),
        422,
    )
    assert denied["code"] == "VALIDATION_FAILED"
    denied = expect(
        live.request(
            live.path("disclosure-requests"),
            method="POST",
            body=cmd(
                {
                    **data,
                    "expires_at": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
                }
            ),
        ),
        422,
    )
    assert denied["reason_code"] == "PUBLICATION_EXPIRY_INVALID"
    recipient = data["recipients"][0]
    denied = expect(
        live.request(
            live.path("disclosure-requests"),
            method="POST",
            body=cmd({**data, "recipients": [recipient, recipient]}),
        ),
        422,
    )
    assert denied["reason_code"] == "PUBLICATION_RECIPIENTS_INVALID"
    denied = expect(
        live.request(
            live.path("disclosure-requests"),
            method="POST",
            body=cmd(
                {
                    **data,
                    "recipients": [
                        {
                            "membership_id": live.fixture["member_revoked"],
                            "allow_download": True,
                        }
                    ],
                }
            ),
        ),
        404,
    )
    assert denied["code"] == "RESOURCE_UNAVAILABLE"
