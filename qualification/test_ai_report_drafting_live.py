"""Positive live journey for FR-AI-007 / APL-339 snapshot-bound report drafting."""

from uuid import uuid4

from test_live_application import expect
from test_reporting import package_data


def _enable(live):
    path = live.path("ai-enablement/policy")
    current = expect(live.request(path, actor="admin"), 200)
    rules = [rule for rule in current["use_cases"] if rule["use_case"] != "REPORT_DRAFT"]
    rules.append(
        {
            "use_case": "REPORT_DRAFT",
            "enabled": True,
            "data_classes": ["INTERNAL"],
            "destinations": ["openai-us"],
            "purposes": ["SNAPSHOT_BOUND_REPORT_DRAFT"],
            "languages": ["en"],
            "review_mode": "HUMAN_REVIEW",
            "budget_units": 10,
            "tools": [],
        }
    )
    return expect(
        live.request(
            path,
            actor="admin",
            method="PUT",
            body={
                "operation_id": str(uuid4()),
                "expected_version": current["policy_version"],
                "data": {"use_cases": rules},
            },
        ),
        200,
    )["policy_version"]


def _domain_counts(live):
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        return {
            row["object_type"]: row["n"]
            for row in c.execute(
                "SELECT object_type,count(*) AS n FROM impact.object_registry WHERE tenant_id=%s "
                "AND object_type IN ('Report','Snapshot') GROUP BY object_type",
                (tenant,),
            ).fetchall()
        }


def test_author_reviews_snapshot_bound_draft_without_publishing_or_changing_sources(live):
    snapshot = live.records["snapshot"]
    template = live.records["report_template"]
    section = package_data(live)["sections"][0]
    section["narrative"] = "Verified access is {{water}} with the pinned evidence."
    policy_version = _enable(live)
    before = _domain_counts(live)
    create_body = {
        "operation_id": str(uuid4()),
        "snapshot_id": snapshot["object_id"],
        "snapshot_revision_id": snapshot["revision_id"],
        "template_revision_id": template["revision_id"],
        "language": "en",
        "policy_version": policy_version,
        "section_inputs": [section],
        "prior_draft_id": None,
        "regenerated_section_codes": [],
    }
    denied = expect(
        live.request(
            live.path("ai-enablement/report-drafts"),
            actor="partner",
            method="POST",
            body=create_body,
        ),
        404,
    )
    assert denied["code"] == "RESOURCE_UNAVAILABLE"
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        assert not c.execute(
            "SELECT 1 FROM impact.ai_report_draft WHERE tenant_id=%s AND operation_id=%s",
            (tenant, create_body["operation_id"]),
        ).fetchone()
    draft = expect(
        live.request(
            live.path("ai-enablement/report-drafts"),
            method="POST",
            body={**create_body, "operation_id": str(uuid4())},
        ),
        200,
    )
    assert draft["generation"] == 1
    assert draft["ai_origin"] is True and draft["domain_objects_changed"] is False
    assert draft["proposed_sections"][0]["bindings"] == section["bindings"]
    assert draft["proposed_sections"][0]["evidence_revisions"] == section["evidence_revisions"]
    assert _domain_counts(live) == before

    final_sections = draft["proposed_sections"]
    final_sections[0] = {
        **final_sections[0],
        "narrative": "Human-reviewed access remains {{water}} with the pinned evidence.",
    }
    reviewed = expect(
        live.request(
            live.path("ai-enablement/report-drafts", draft["draft_id"]) + "/actions/review",
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "final_sections": final_sections,
                "mandatory_caveat_codes": draft["mandatory_caveat_codes"],
            },
        ),
        200,
    )
    assert reviewed["state"] == "HUMAN_REVIEWED"
    assert reviewed["ai_origin_retained"] is True
    assert reviewed["domain_objects_changed"] is False
    assert reviewed["corrections"][0]["before"]["narrative"] == section["narrative"]
    assert reviewed["corrections"][0]["after"]["narrative"].startswith("Human-reviewed")
    assert _domain_counts(live) == before
