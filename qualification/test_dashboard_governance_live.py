"""Whole-story application qualification for FR-ANA-008 / APL-614 dashboard governance."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

from test_calculation_methods import build, calculate_result, observation_data
from test_forms import temporary_grants
from test_live_application import expect
from test_measurement import approve, create, submit


def _enrol_author_in_funder_workspace(live):
    """Synthetic fixture setup only: one real fixture identity is a member of both tenants."""
    from impact_api.store import Context, write

    actor = live.fixture["actors"]["author"]
    tenant = live.fixture["tenant_b"]
    principal_id, membership_id = str(uuid4()), str(uuid4())
    identity = SimpleNamespace(natural_identity_id=actor["natural_identity_id"])
    ctx = Context(tenant, principal_id, membership_id, identity, 0, 0, [])
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        c.execute(
            "INSERT INTO impact.tenant_principal(tenant_id,principal_id,identity_id,principal_kind) VALUES(%s,%s,%s,'HUMAN')",
            (tenant, principal_id, actor["identity_id"]),
        )
        member = write(
            c,
            ctx,
            "Membership",
            {"identity_id": actor["identity_id"], "authority_source": "LOCAL_TEST", "external": False},
            "Active",
            object_id=membership_id,
            track_author=False,
        )
        ctx.membership_id = member["object_id"]
        scope = c.execute(
            "SELECT scope_id FROM impact.scope_definition WHERE tenant_id=%s AND scope_type='TENANT' LIMIT 1",
            (tenant,),
        ).fetchone()["scope_id"]
        for capability in ["dashboards.draft.create", "dashboards.read"]:
            write(
                c,
                ctx,
                "Grant",
                {
                    "subject_id": principal_id,
                    "capability": capability,
                    "scope_id": str(scope),
                    "starts_at": "2026-01-01T00:00:00Z",
                    "expires_at": "2027-01-01T00:00:00Z",
                    "issuer_id": principal_id,
                },
                "Active",
                track_author=False,
            )


def _dashboard(live):
    _, indicator, period, keys = build(live, scheme=None)
    row = create(live, "observations", observation_data(indicator, keys[0], "7", {}))
    approve(live, submit(live, "observations", row))
    result = calculate_result(live, indicator, period)
    widget_id = str(uuid4())
    dashboard = create(
        live,
        "dashboards",
        {
            "title": "Reviewed public result",
            "mode": "PRIVATE_DRAFT",
            "widgets": [
                {
                    "widget_id": widget_id,
                    "type": "METRIC",
                    "title": "Delivery metric",
                    "binding": {
                        "resource_type": "CALCULATED_RESULT",
                        "object_id": result["object_id"],
                        "revision_id": result["revision_id"],
                    },
                    "view_mode": "OFFICIAL",
                    "period_id": period["object_id"],
                    "dimensions": [],
                    "disclosure_context": {
                        "classification": "PUBLIC",
                        "quality_context_required": True,
                    },
                    "position": 0,
                    "width": 12,
                    "compatible_filters": [],
                    "drilldown_levels": [],
                    "approved_slices": [],
                }
            ],
            "filters": {"terms": []},
        },
    )
    return dashboard, result, widget_id


def _post(live, suffix, body, actor="author", status=201):
    return expect(live.request(suffix, actor=actor, method="POST", body=body), status)


def test_reviewed_disclosure_public_content_owner_transfer_and_durable_recovery(live):
    author_revoke = temporary_grants(
        live,
        "author",
        ["dashboards.draft.create", "dashboards.draft.edit", "dashboards.read", "calculated-results.read"],
    )
    reviewer_revoke = temporary_grants(
        live,
        "reviewer",
        ["dashboards.draft.edit", "dashboards.read", "calculated-results.read"],
    )
    try:
        dashboard, result, widget_id = _dashboard(live)
        base = live.path("dashboards", dashboard["object_id"])
        expiry = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()

        _enrol_author_in_funder_workspace(live)
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_b"],))
            grants_before = c.execute(
                "SELECT count(*) AS n FROM impact.grant_current WHERE tenant_id=%s",
                (live.fixture["tenant_b"],),
            ).fetchone()["n"]
        cross_body = {
            "operation_id": str(uuid4()),
            "expected_revision": dashboard["revision_id"],
            "data": {"target_tenant_id": live.fixture["tenant_b"], "title": "Funder draft"},
        }
        copied = _post(live, base + "/actions/copy-to-workspace", cross_body)
        assert copied["grants_created"] is False and copied["unavailable_binding_count"] == 1
        assert _post(live, base + "/actions/copy-to-workspace", cross_body) == copied
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_b"],))
            assert (
                c.execute(
                    "SELECT count(*) AS n FROM impact.grant_current WHERE tenant_id=%s",
                    (live.fixture["tenant_b"],),
                ).fetchone()["n"]
                == grants_before
            )
            copied_payload = c.execute(
                "SELECT payload FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s "
                "ORDER BY revision_number DESC LIMIT 1",
                (live.fixture["tenant_b"], copied["object_id"]),
            ).fetchone()["payload"]
            assert copied_payload["widgets"][0]["binding"]["object_id"] != result["object_id"]
            assert copied_payload["widgets"][0]["binding"]["revision_id"] != result["revision_id"]
        assert "source_tenant_id" not in copied and "source_dashboard_id" not in copied
        preview = expect(
            live.request(
                live.path("dashboards", copied["object_id"], tenant=live.fixture["tenant_b"])
                + "/preview?viewport=TABLE"
            ),
            200,
        )
        assert preview["mode"] == "PRIVATE_DRAFT"
        assert preview["widgets"][0]["availability"] == "UNAVAILABLE"

        refused = live.request(
            base + "/actions/publish",
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "expected_revision": dashboard["revision_id"],
                "data": {"audience": "PUBLIC", "expires_at": expiry},
            },
        )
        assert refused.status_code == 422 and refused.json()["reason_code"] == "PUBLIC_DISCLOSURE_REQUIRED", (
            refused.text
        )

        prepare_body = {
            "operation_id": str(uuid4()),
            "expected_revision": dashboard["revision_id"],
            "data": {
                "widgets": [
                    {
                        "widget_id": widget_id,
                        "title": "Delivery metric",
                        "content": "7",
                        "quality_context": "Approved source; synthetic qualification fixture.",
                    }
                ]
            },
        }
        artifact = _post(live, base + "/disclosure-artifacts", prepare_body)
        self_review = live.request(
            base + f"/disclosure-artifacts/{artifact['object_id']}/actions/review",
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "expected_revision": artifact["revision_id"],
                "data": {"decision": "APPROVE"},
            },
        )
        assert self_review.status_code == 403 and self_review.json()["reason_code"] == "INDEPENDENCE_REQUIRED"
        approved = _post(
            live,
            base + f"/disclosure-artifacts/{artifact['object_id']}/actions/review",
            {
                "operation_id": str(uuid4()),
                "expected_revision": artifact["revision_id"],
                "data": {"decision": "APPROVE"},
            },
            actor="reviewer",
        )
        publish_body = {
            "operation_id": str(uuid4()),
            "expected_revision": dashboard["revision_id"],
            "data": {
                "audience": "PUBLIC",
                "expires_at": expiry,
                "disclosure_artifact_id": artifact["object_id"],
            },
        }
        publication = _post(live, base + "/actions/publish", publish_body)
        assert _post(live, base + "/actions/publish", publish_body) == publication
        changed = {**publish_body, "data": {**publish_body["data"], "audience": "INTERNAL"}}
        assert live.request(base + "/actions/publish", method="POST", body=changed).status_code == 409

        content = expect(live.request(base + f"/publications/{publication['object_id']}/content"), 200)
        assert content["widgets"][0]["content"] == "7"
        transfer = _post(
            live,
            base + f"/publications/{publication['object_id']}/actions/transfer-owner",
            {
                "operation_id": str(uuid4()),
                "expected_revision": publication["revision_id"],
                "data": {"owner_id": live.fixture["actors"]["reviewer"]["principal_id"]},
            },
        )

        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
            c.execute(
                "UPDATE impact.object_registry SET classification='CONFIDENTIAL' WHERE tenant_id=%s AND object_id=%s",
                (live.fixture["tenant_a"], result["object_id"]),
            )
        assert live.request(base + f"/publications/{publication['object_id']}/content").status_code == 404
        status = expect(live.request(base + f"/publications/{publication['object_id']}"), 200)
        assert status["status"] == "SUSPENDED"
        assert (
            expect(live.request(base + f"/publications/{publication['object_id']}"), 200)["status"]
            == "SUSPENDED"
        )
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
            c.execute(
                "UPDATE impact.object_registry SET classification='INTERNAL' WHERE tenant_id=%s AND object_id=%s",
                (live.fixture["tenant_a"], result["object_id"]),
            )
            current = c.execute(
                "SELECT head_revision FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
                (live.fixture["tenant_a"], publication["object_id"]),
            ).fetchone()["head_revision"]
        former_owner = live.request(
            base + f"/publications/{publication['object_id']}/actions/revalidate",
            method="POST",
            body={"operation_id": str(uuid4()), "expected_revision": str(current), "data": {}},
        )
        assert former_owner.status_code == 404
        revalidated = _post(
            live,
            base + f"/publications/{publication['object_id']}/actions/revalidate",
            {"operation_id": str(uuid4()), "expected_revision": str(current), "data": {}},
            actor="reviewer",
        )
        resumed = _post(
            live,
            base + f"/publications/{publication['object_id']}/actions/resume",
            {"operation_id": str(uuid4()), "expected_revision": revalidated["revision_id"], "data": {}},
            actor="reviewer",
        )
        assert resumed["business_state"] == "Published" and transfer["business_state"] == "Published"
        assert (
            expect(live.request(base + f"/publications/{publication['object_id']}"), 200)["status"]
            == "ACTIVE"
        )
        assert approved["business_state"] == "Approved"
        with live.db() as c:
            policies = c.execute(
                "SELECT polname,polpermissive FROM pg_policy WHERE polname IN "
                "('worker_dashboard_disclosure_registry_fence','worker_dashboard_disclosure_revision_fence') "
                "ORDER BY polname"
            ).fetchall()
        assert [row["polname"] for row in policies] == [
            "worker_dashboard_disclosure_registry_fence",
            "worker_dashboard_disclosure_revision_fence",
        ]
        assert all(row["polpermissive"] is False for row in policies)
    finally:
        reviewer_revoke()
        author_revoke()
