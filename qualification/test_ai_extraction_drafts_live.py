"""Positive user journey for FR-AI-002 / APL-531 traceable extraction drafts."""

from uuid import uuid4

from test_evidence import evidence, unique, uploaded
from test_live_application import expect


def _enable_extraction(live):
    path = live.path("ai-enablement/policy")
    current = expect(live.request(path, actor="admin"), 200)
    rules = [rule for rule in current["use_cases"] if rule["use_case"] != "EXTRACTION"]
    rules.append(
        {
            "use_case": "EXTRACTION",
            "enabled": True,
            "data_classes": ["INTERNAL"],
            "destinations": ["openai-us"],
            "purposes": ["PROPOSAL_LOGFRAME_EXTRACTION"],
            "languages": ["en"],
            "review_mode": "HUMAN_REVIEW",
            "budget_units": 1,
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


def _domain_count(live):
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        return c.execute(
            "SELECT count(*) AS n FROM impact.object_registry WHERE tenant_id=%s "
            "AND object_type IN "
            "('Programme','ResultsFramework','ResultNode','IndicatorDefinition','IndicatorInstance','Target')",
            (tenant,),
        ).fetchone()["n"]


def test_manager_reviews_exact_source_proposals_without_creating_domain_objects(live):
    content = unique(
        b"# Outcome commitments\n"
        b"Title: Safer water access\n"
        b"Title: Reliable water access\n"
        b"Start date: 2026-10-01\n"
    )
    source = expect(
        evidence(
            live,
            uploaded(live, content, "text/plain", "outcome-commitments.txt")["upload_id"],
            evidence_type="PROGRAMME_DOCUMENT",
            source="Synthetic outcome workshop",
        ),
        201,
    )
    policy_version = _enable_extraction(live)
    before = _domain_count(live)
    create_body = {
        "operation_id": str(uuid4()),
        "source_object_id": source["object_id"],
        "source_revision_id": source["revision_id"],
        "policy_version": policy_version,
        "language": "en",
    }
    denied = expect(
        live.request(
            live.path("ai-enablement/extractions"),
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
            "SELECT 1 FROM impact.ai_extraction_draft WHERE tenant_id=%s AND operation_id=%s",
            (tenant, create_body["operation_id"]),
        ).fetchone()
    created = expect(
        live.request(
            live.path("ai-enablement/extractions"),
            method="POST",
            body={**create_body, "operation_id": str(uuid4())},
        ),
        200,
    )

    assert created["source_object_id"] == source["object_id"]
    assert created["source_revision_id"] == source["revision_id"]
    assert created["domain_objects_changed"] is False
    assert created["activation_blocked"] is True
    assert set(created["missing_fields"]) == {"end_date", "target", "population"}
    titles = [item for item in created["proposals"] if item["field_key"] == "title"]
    assert len(titles) == 2 and all(item["conflict"] for item in titles)
    assert all(item["classification"] == "EXTRACTED" for item in created["proposals"])
    assert {item["location"]["section"] for item in created["proposals"]} == {"Outcome commitments"}
    assert {item["location"]["line"] for item in created["proposals"]} == {2, 3, 4}
    assert {item["evidence_span"] for item in titles} == {
        "Title: Safer water access",
        "Title: Reliable water access",
    }

    start = next(item for item in created["proposals"] if item["field_key"] == "start_date")
    reviewed = expect(
        live.request(
            live.path("ai-enablement/extractions", created["draft_id"]) + "/actions/apply",
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "selected_proposal_ids": [titles[0]["proposal_id"], start["proposal_id"]],
                "human_additions": [
                    {
                        "field_key": "end_date",
                        "value": "2027-09-30",
                        "rationale": "Confirmed in the signed programme schedule.",
                    },
                    {
                        "field_key": "target",
                        "value": "600 households",
                        "rationale": "Confirmed by the accountable programme manager.",
                    },
                    {
                        "field_key": "population",
                        "value": "Households in Ward 4",
                        "rationale": "Confirmed against the approved participant scope.",
                    },
                ],
            },
        ),
        200,
    )
    assert reviewed["state"] == "READY_FOR_DOMAIN_DRAFT"
    assert reviewed["unresolved_fields"] == []
    assert reviewed["domain_objects_changed"] is False
    assert reviewed["accepted_fields"]["title"]["classification"] == "EXTRACTED"
    assert reviewed["accepted_fields"]["population"] == {
        "value": "Households in Ward 4",
        "classification": "HUMAN_ADDED",
        "rationale": "Confirmed against the approved participant scope.",
    }
    assert _domain_count(live) == before

    reviewer = live.fixture["actors"]["author"]["principal_id"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        stored = c.execute(
            "SELECT reviewed_by::text,unresolved_fields,accepted_fields "
            "FROM impact.ai_extraction_review WHERE tenant_id=%s AND draft_id=%s",
            (tenant, created["draft_id"]),
        ).fetchone()
    assert stored["reviewed_by"] == reviewer
    assert stored["unresolved_fields"] == []
    assert stored["accepted_fields"]["population"]["classification"] == "HUMAN_ADDED"
