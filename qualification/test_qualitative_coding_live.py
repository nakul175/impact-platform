"""Positive user journey for FR-EVD-005 / APL-641 qualitative coding."""

from uuid import uuid4

import pytest

from test_evidence import CSV, evidence, unique, uploaded
from test_forms import temporary_grants
from test_live_application import expect
from test_story_error_recovery_analytics_live import _durable_counts


@pytest.fixture(autouse=True)
def qualitative_journey_grants(live):
    revokes = [
        temporary_grants(live, "author", ["evidence.read"]),
        temporary_grants(
            live,
            "reviewer",
            ["evaluations.draft.edit", "evaluations.read", "evidence.read"],
        ),
        temporary_grants(live, "admin", ["evaluations.draft.edit", "evaluations.read"]),
    ]
    try:
        yield
    finally:
        for revoke in reversed(revokes):
            revoke()


def _post(live, route, data, actor="author"):
    body = {"operation_id": str(uuid4()), "data": data}
    path = live.path(route)
    before = _durable_counts(live, body["operation_id"])
    expect(live.request(path, actor=actor, method="POST", body={**body, "unapproved_action": True}), 422)
    assert _durable_counts(live, body["operation_id"]) == before
    result = expect(live.request(path, actor=actor, method="POST", body=body), 201)
    assert expect(live.request(path, actor=actor, method="POST", body=body), 201) == result
    return result


def _stored(live, object_id):
    tenant = live.fixture["actors"]["author"]["tenant_id"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        return c.execute(
            "SELECT r.object_type,r.lifecycle_state,r.classification,v.revision_id::text,v.payload "
            "FROM impact.object_registry r JOIN impact.object_revision v "
            "ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
            "WHERE r.tenant_id=%s AND r.object_id=%s",
            (tenant, object_id),
        ).fetchone()


def test_two_coders_preserve_assignments_and_adjudicate_one_disagreement(live):
    """The API preserves a versioned codebook, both coders and the final rationale."""
    source = expect(evidence(live, uploaded(live, unique(CSV))["upload_id"]), 201)
    codebook = _post(
        live,
        "qualitative-codebooks",
        {
            "version": "1.0",
            "codes": [
                {
                    "code_id": "ACCESS_BARRIER",
                    "meaning": "A stated obstacle to reaching the service.",
                    "inclusion_examples": ["Travel cost prevented attendance."],
                    "exclusion_examples": ["The participant attended as planned."],
                },
                {
                    "code_id": "SERVICE_REACHED",
                    "meaning": "The participant reached the intended service.",
                    "inclusion_examples": ["The participant attended the clinic."],
                    "exclusion_examples": ["The visit was cancelled."],
                },
            ],
        },
    )
    common = {
        "source_type": "Evidence",
        "source_id": source["object_id"],
        "unit_id": "interview-01/segment-03",
        "excerpt": "Travel cost prevented my clinic visit.",
        "memo": "Synthetic interview excerpt.",
        "codebook_id": codebook["object_id"],
        "codebook_revision": codebook["revision_id"],
    }
    left = _post(live, "qualitative-assignments", {**common, "code_ids": ["ACCESS_BARRIER"]})
    right = _post(
        live,
        "qualitative-assignments",
        {**common, "code_ids": ["SERVICE_REACHED"]},
        actor="reviewer",
    )
    adjudication = _post(
        live,
        "qualitative-adjudications",
        {
            "left_assignment_id": left["object_id"],
            "right_assignment_id": right["object_id"],
            "final_code_ids": ["ACCESS_BARRIER"],
            "rationale": "The excerpt describes inability to reach the service.",
        },
        actor="admin",
    )
    agreement = _post(
        live,
        "qualitative-agreements",
        {
            "pairs": [
                {
                    "left_assignment_id": left["object_id"],
                    "right_assignment_id": right["object_id"],
                }
            ]
        },
    )

    saved_codebook = _stored(live, codebook["object_id"])
    saved_left = _stored(live, left["object_id"])
    saved_right = _stored(live, right["object_id"])
    saved_adjudication = _stored(live, adjudication["object_id"])
    saved_agreement = _stored(live, agreement["object_id"])
    assert saved_codebook["payload"]["version"] == "1.0"
    assert (
        saved_left["payload"]["coder_natural_identity_id"]
        != saved_right["payload"]["coder_natural_identity_id"]
    )
    assert saved_left["payload"]["code_ids"] == ["ACCESS_BARRIER"]
    assert saved_right["payload"]["code_ids"] == ["SERVICE_REACHED"]
    assert saved_adjudication["payload"]["individual_assignments_preserved"] is True
    assert saved_adjudication["payload"]["codebook_revision"] == codebook["revision_id"]
    assert saved_adjudication["payload"]["rationale"].startswith("The excerpt")
    assert saved_adjudication["classification"] == saved_left["classification"]
    assert saved_agreement["payload"]["matched_units_only"] is True
    assert saved_agreement["payload"]["matched_count"] == 1
    assert saved_agreement["payload"]["agreement_count"] == 0

    denied = expect(
        live.request(
            live.path("qualitative-adjudications"),
            actor="partner",
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "data": {
                    "left_assignment_id": left["object_id"],
                    "right_assignment_id": right["object_id"],
                    "final_code_ids": ["ACCESS_BARRIER"],
                    "rationale": "An external recipient cannot adjudicate coding.",
                },
            },
        ),
        403,
    )
    assert denied["code"] == "POLICY_DENIED"
