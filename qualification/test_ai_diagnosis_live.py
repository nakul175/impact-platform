"""US-DX-01a API qualification: synthetic diagnosis order and completion refusals.

Actual run outcomes are recorded separately in the build 0.40 candidate receipt.
Source code is not a test-run or acceptance claim.
Original criteria: AC-US-DX-01a-001 and AC-US-DX-01a-002. Extra negative
checks enforce the proposed slice's security contract; they do not amend criteria.
PGlite execution is not native RLS/concurrency or browser acceptance evidence.
"""

from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
import json
import time
from uuid import uuid4

import pytest

from impact_api.contracts import validate
from test_live_application import cmd, expect

ROUTE = "ai-enablement/diagnoses"
DATA_FIELDS = ("title", "problems", "priority_order")


def diagnosis():
    first, second = str(uuid4()), str(uuid4())
    return {
        "title": "Synthetic organisation diagnosis",
        "problems": [
            {
                "problem_id": first,
                "description": "Synthetic staff spend too long preparing a public newsletter",
                "affected_area": "Communications",
                "supporting_evidence": "Synthetic exercise log: five drafts took two staff hours.",
            },
            {
                "problem_id": second,
                "description": "Synthetic programme data definitions need a shared checklist",
                "affected_area": "Monitoring and evaluation",
                "supporting_evidence": "Synthetic review log: three labels differed in a sample.",
            },
        ],
        "priority_order": [second, first],
    }


def save(live, data=None, body=None):
    result = expect(
        live.request(
            live.path(ROUTE),
            actor="admin",
            method="POST",
            body=body or cmd(data or diagnosis()),
        ),
        201,
    )
    validate("AIDiagnosisReceipt", result)
    return result


def get(live, row):
    result = expect(live.request(live.path(ROUTE, row["object_id"]), actor="admin"), 200)
    validate("AIDiagnosis", result)
    return result


def action_body(row, **extra):
    return {
        "operation_id": str(uuid4()),
        "expected_revision": row["revision_id"],
        **extra,
    }


def action(live, row, name, body=None, status=200, **kwargs):
    result = expect(
        live.request(
            live.path(ROUTE, row["object_id"]) + "/actions/" + name,
            actor=kwargs.pop("actor", "admin"),
            method="POST",
            body=body or action_body(row),
            **kwargs,
        ),
        status,
    )
    validate("AIDiagnosisReceipt" if status == 200 else "AIDiagnosisError", result)
    return result


def domain_counts(live):
    """Authorization-denial audit is separate from prohibited domain writes."""
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        return {
            table: c.execute(
                "SELECT count(*) AS n FROM impact." + table + " WHERE tenant_id=%s",
                (tenant,),
            ).fetchone()["n"]
            for table in (
                "object_registry",
                "object_revision",
                "audit_event_current",
                "outbox_event",
                "operation_receipt",
                "ai_advisory_request",
                "ai_advisory_result",
            )
        }


@contextmanager
def narrowed(live, capability):
    """Remove only an actual existing fixture grant, then restore its prior purpose."""
    tenant = live.fixture["tenant_a"]
    principal = live.fixture["actors"]["admin"]["principal_id"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        grants = c.execute(
            "SELECT object_id,purpose FROM impact.grant_current WHERE tenant_id=%s AND subject_id=%s "
            "AND capability=%s AND purpose IS NULL",
            (tenant, principal, capability),
        ).fetchall()
        assert grants, "Bootstrap must supply a real synthetic diagnosis grant"
        c.execute(
            "UPDATE impact.grant_current SET purpose='QUALIFICATION' WHERE tenant_id=%s "
            "AND object_id=ANY(%s::uuid[])",
            (tenant, [str(row["object_id"]) for row in grants]),
        )
    try:
        yield
    finally:
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            for row in grants:
                c.execute(
                    "UPDATE impact.grant_current SET purpose=%s WHERE tenant_id=%s AND object_id=%s",
                    (row["purpose"], tenant, row["object_id"]),
                )


# qa:TC-IMPRANA-US-DX-01a-001@REV_4f85d88e01dae94d79c7ef07eaa4d10143cec16d2993de038b45c90d961a0c9e
def test_diagnosis_saves_exact_order_stable_ids_and_supporting_evidence(live):
    # AC-US-DX-01a-001: every original action and expected oracle.
    before = domain_counts(live)
    data = diagnosis()
    row = save(live, data)
    current = get(live, row)
    assert current["business_state"] == "Draft"
    assert {key: current["data"][key] for key in DATA_FIELDS} == data
    assert current["data"]["priority_order"] != [problem["problem_id"] for problem in data["problems"]]
    changed = deepcopy(data)
    changed["priority_order"].reverse()
    updated = expect(
        live.request(
            live.path(ROUTE, row["object_id"]),
            actor="admin",
            method="PUT",
            body=cmd(changed, row["revision_id"]),
        ),
        200,
    )
    assert updated["object_id"] == row["object_id"] and updated["revision_id"] != row["revision_id"]
    assert {key: get(live, updated)["data"][key] for key in DATA_FIELDS} == changed
    old = expect(
        live.request(
            live.path(ROUTE, row["object_id"]) + "/revisions/" + row["revision_id"],
            actor="admin",
        ),
        200,
    )
    assert {key: old["data"][key] for key in DATA_FIELDS} == data
    after = domain_counts(live)
    for table in ("ai_advisory_request", "ai_advisory_result"):
        assert after[table] == before[table], "Manual diagnosis must not invoke a provider or reserve AI work"


@pytest.mark.parametrize("missing", ["supporting_evidence", "priority_order", "description", "affected_area"])
# qa:TC-IMPRANA-US-DX-01a-002@REV_27f93f742b8a06852b47491b146ef5709d3068d7e9702d193418d5be563d3b21
def test_diagnosis_completion_names_each_incomplete_problem_without_writing(live, missing):
    # AC-US-DX-01a-002: missing evidence/order; supplemental closed completion fields.
    data = diagnosis()
    problem = data["problems"][0]
    if missing == "priority_order":
        data["priority_order"].remove(problem["problem_id"])
        field = "priority"
    else:
        problem[missing] = "   "
        field = missing
    row = save(live, data)
    before = domain_counts(live)
    denied = action(live, row, "complete", status=422)
    assert denied["code"] == "VALIDATION_FAILED" and denied["reason_code"] == "DIAGNOSIS_INCOMPLETE"
    path = "problems." + problem["problem_id"] + "." + field
    fields = [item for item in denied["field_errors"] if item["path"] == path]
    assert fields
    expected_name = problem["description"].strip()[:150] or problem["problem_id"]
    assert expected_name in fields[0]["message"]
    assert domain_counts(live) == before
    assert get(live, row)["revision_id"] == row["revision_id"]
    assert get(live, row)["business_state"] == "Draft"


def test_diagnosis_empty_draft_is_saved_but_cannot_complete(live):
    data = {"title": "Synthetic empty diagnosis", "problems": [], "priority_order": []}
    row = save(live, data)
    before = domain_counts(live)
    denied = action(live, row, "complete", status=422)
    assert denied["reason_code"] == "DIAGNOSIS_INCOMPLETE"
    assert any(item["path"] == "problems" for item in denied["field_errors"])
    assert domain_counts(live) == before and get(live, row)["business_state"] == "Draft"


def test_completion_has_server_identity_and_time_and_explicit_revision_preserves_history(
    live,
):
    row = save(live)
    complete_body = action_body(row)
    completed = action(live, row, "complete", complete_body)
    current = get(live, completed)
    assert current["business_state"] == "Completed"
    assert current["data"]["completed_by"] == live.fixture["actors"]["admin"]["principal_id"]
    assert datetime.fromisoformat(current["data"]["completed_at"].replace("Z", "+00:00")).tzinfo
    immutable = deepcopy(current)
    before = domain_counts(live)
    action(live, row, "complete", complete_body)
    assert domain_counts(live) == before
    expect(
        live.request(
            live.path(ROUTE, row["object_id"]),
            actor="admin",
            method="PUT",
            body=cmd(diagnosis(), completed["revision_id"]),
        ),
        409,
    )
    assert get(live, completed) == immutable and domain_counts(live) == before
    correction = action(
        live,
        completed,
        "revise",
        action_body(completed, reason="Synthetic correction of draft priorities"),
    )
    assert correction["revision_id"] != completed["revision_id"]
    revised = get(live, correction)
    assert revised["business_state"] == "Draft"
    historical = expect(
        live.request(
            live.path(ROUTE, row["object_id"]) + "/revisions/" + completed["revision_id"],
            actor="admin",
        ),
        200,
    )
    assert historical == immutable
    history = expect(
        live.request(live.path(ROUTE, row["object_id"]) + "/revisions", actor="admin"),
        200,
    )
    by_id = {item["revision_id"]: item for item in history["items"]}
    assert by_id[completed["revision_id"]]["business_state"] == "Completed"
    assert by_id[correction["revision_id"]]["business_state"] == "Draft"
    assert len(by_id) == 3


def test_create_update_and_complete_exact_replays_are_atomic_and_changed_payload_conflicts(
    live,
):
    data = diagnosis()
    body = cmd(data)
    first = save(live, body=body)
    after_first = domain_counts(live)
    assert save(live, body=body) == first and domain_counts(live) == after_first
    denied = expect(
        live.request(
            live.path(ROUTE),
            actor="admin",
            method="POST",
            body={**body, "data": {**data, "title": "Changed operation intent"}},
        ),
        409,
    )
    assert denied["code"] == "CONFLICT_OPERATION" and domain_counts(live) == after_first
    changed = deepcopy(data)
    changed["priority_order"].reverse()
    update = cmd(changed, first["revision_id"])
    second = expect(
        live.request(
            live.path(ROUTE, first["object_id"]),
            actor="admin",
            method="PUT",
            body=update,
        ),
        200,
    )
    after_second = domain_counts(live)
    assert (
        expect(
            live.request(
                live.path(ROUTE, first["object_id"]),
                actor="admin",
                method="PUT",
                body=update,
            ),
            200,
        )
        == second
    )
    assert domain_counts(live) == after_second
    stale = expect(
        live.request(
            live.path(ROUTE, first["object_id"]),
            actor="admin",
            method="PUT",
            body=cmd(data, first["revision_id"]),
        ),
        409,
    )
    assert stale["code"] == "CONFLICT_VERSION" and domain_counts(live) == after_second
    complete = action_body(second)
    third = action(live, second, "complete", complete)
    after_third = domain_counts(live)
    assert action(live, second, "complete", complete) == third and domain_counts(live) == after_third
    with live.db() as c:
        tenant = live.fixture["tenant_a"]
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        rows = c.execute(
            "SELECT revision_id,payload FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s ORDER BY revision_number",
            (tenant, first["object_id"]),
        ).fetchall()
        assert len(rows) == 3 and rows[0]["payload"]["priority_order"] == data["priority_order"]
        assert rows[1]["payload"]["priority_order"] == changed["priority_order"]
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s AND object_reference=%s",
                (tenant, first["object_id"]),
            ).fetchone()["n"]
            == 3
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.outbox_event WHERE tenant_id=%s AND payload->>'aggregate_id'=%s",
                (tenant, first["object_id"]),
            ).fetchone()["n"]
            == 3
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s AND operation_id=ANY(%s::uuid[])",
                (
                    tenant,
                    [
                        body["operation_id"],
                        update["operation_id"],
                        complete["operation_id"],
                    ],
                ),
            ).fetchone()["n"]
            == 3
        )


@pytest.mark.parametrize("actor", ["partner", "owner", "other_tenant", "revoked", None])
def test_specific_tenant_admin_capability_does_not_follow_persona_custody_or_tenant_selector(live, actor):
    row = save(live)
    before = domain_counts(live)
    status = 401 if actor is None else 404
    for path in [
        live.path(ROUTE),
        live.path(ROUTE, row["object_id"]),
        live.path(ROUTE, row["object_id"]) + "/revisions",
        live.path(ROUTE, row["object_id"]) + "/revisions/" + row["revision_id"],
    ]:
        denied = expect(live.request(path, actor=actor), status)
        assert denied["code"] == ("AUTH_REQUIRED" if actor is None else "RESOURCE_UNAVAILABLE")
    expect(
        live.request(live.path(ROUTE), actor=actor, method="POST", body=cmd(diagnosis())),
        status,
    )
    expect(
        live.request(
            live.path(ROUTE, row["object_id"]),
            actor=actor,
            method="PUT",
            body=cmd(diagnosis(), row["revision_id"]),
        ),
        status,
    )
    action(live, row, "complete", status=status, actor=actor)
    assert domain_counts(live) == before


@pytest.mark.parametrize("capability", ["ai.diagnosis.manage", "ai.diagnosis.read"])
def test_create_and_replay_recheck_current_grants_before_receipt_access(live, capability):
    body = cmd(diagnosis())
    row = save(live, body=body)
    before = domain_counts(live)
    with narrowed(live, capability):
        expect(live.request(live.path(ROUTE), actor="admin", method="POST", body=body), 404)
        action(live, row, "complete", status=404)
    assert domain_counts(live) == before
    assert save(live, body=body) == row and domain_counts(live) == before


@pytest.mark.parametrize("action_name", ["complete", "revise"])
def test_sensitive_actions_require_fresh_signed_authentication_on_initial_call_and_replay(live, action_name):
    row = save(live)
    if action_name == "revise":
        row = action(live, row, "complete")
    body = action_body(
        row,
        **({"reason": "Synthetic explicit correction"} if action_name == "revise" else {}),
    )
    token = live.signed(live.fixture["actors"]["admin"]["identity_id"], auth_time=time.time() - 301)
    kwargs = {"actor": None, "headers": {"Authorization": "Bearer " + token}}
    before = domain_counts(live)
    denied = action(live, row, action_name, body, status=403, **kwargs)
    assert denied["reason_code"] == "FRESH_AUTHENTICATION_REQUIRED" and domain_counts(live) == before
    action(live, row, action_name, body)
    after = domain_counts(live)
    denied = action(live, row, action_name, body, status=403, **kwargs)
    assert denied["reason_code"] == "FRESH_AUTHENTICATION_REQUIRED" and domain_counts(live) == after


@pytest.mark.parametrize("location", ["top", "data", "problem"])
@pytest.mark.parametrize("field", ["completed_at", "completed_by", "diagnosis_state", "evidence_revision_id"])
def test_unknown_server_fields_and_reference_selectors_are_rejected_before_writes(live, location, field):
    body = cmd(diagnosis())
    target = (
        body if location == "top" else body["data"] if location == "data" else body["data"]["problems"][0]
    )
    target[field] = "synthetic-forged-server-field"
    before = domain_counts(live)
    expect(live.request(live.path(ROUTE), actor="admin", method="POST", body=body), 422)
    assert domain_counts(live) == before


@pytest.mark.parametrize(
    "problem_field,maximum",
    [("description", 1000), ("affected_area", 150), ("supporting_evidence", 4000)],
)
def test_problem_text_boundaries_accept_exact_limit_and_refuse_one_character_over(
    live, problem_field, maximum
):
    data = diagnosis()
    data["problems"][0][problem_field] = "x" * maximum
    row = save(live, data)
    assert get(live, row)["data"]["problems"][0][problem_field] == data["problems"][0][problem_field]
    data["problems"][0][problem_field] += "x"
    before = domain_counts(live)
    expect(
        live.request(live.path(ROUTE), actor="admin", method="POST", body=cmd(data)),
        422,
    )
    assert domain_counts(live) == before


@pytest.mark.parametrize(
    "fault",
    [
        "duplicate_id",
        "invalid_id",
        "duplicate_priority",
        "unknown_priority",
        "too_many",
        "overlong_title",
        "blank_title",
    ],
)
def test_invalid_identity_order_and_collection_bounds_cannot_create_a_draft(live, fault):
    data = diagnosis()
    if fault == "duplicate_id":
        data["problems"][1]["problem_id"] = data["problems"][0]["problem_id"]
    elif fault == "invalid_id":
        data["problems"][0]["problem_id"] = "not-a-uuid"
    elif fault == "duplicate_priority":
        data["priority_order"] = [data["problems"][0]["problem_id"]] * 2
    elif fault == "unknown_priority":
        data["priority_order"][0] = str(uuid4())
    elif fault == "too_many":
        data["problems"] = [{**data["problems"][0], "problem_id": str(uuid4())} for _ in range(21)]
        data["priority_order"] = [item["problem_id"] for item in data["problems"]]
    elif fault == "overlong_title":
        data["title"] = "x" * 151
    else:
        data["title"] = "   "
    before = domain_counts(live)
    expect(
        live.request(live.path(ROUTE), actor="admin", method="POST", body=cmd(data)),
        422,
    )
    assert domain_counts(live) == before


def test_nested_duplicate_json_key_is_not_silently_overwritten(live):
    body = cmd(diagnosis())
    raw = json.dumps(body).replace(
        '"supporting_evidence":',
        '"supporting_evidence": "forged first value", "supporting_evidence":',
        1,
    )
    before = domain_counts(live)
    expect(
        live.request(
            live.path(ROUTE),
            actor="admin",
            method="POST",
            headers={"Content-Type": "application/json"},
            content=raw,
        ),
        400,
    )
    assert domain_counts(live) == before


def test_wrong_kind_missing_and_other_tenant_selectors_share_unavailable_response(live):
    row = save(live)
    before = domain_counts(live)
    for selector in [live.fixture["programme_a"], str(uuid4())]:
        denied = expect(live.request(live.path(ROUTE, selector), actor="admin"), 404)
        assert denied["code"] == "RESOURCE_UNAVAILABLE"
        expect(
            live.request(
                live.path(ROUTE, selector),
                actor="admin",
                method="PUT",
                body=cmd(diagnosis(), str(uuid4())),
            ),
            404,
        )
    denied = expect(
        live.request(
            live.path(ROUTE, row["object_id"], tenant=live.fixture["tenant_b"]),
            actor="admin",
        ),
        404,
    )
    assert denied["code"] == "RESOURCE_UNAVAILABLE"
    expect(
        live.request(
            live.path(ROUTE, row["object_id"]) + "/revisions/" + str(uuid4()),
            actor="admin",
        ),
        404,
    )
    assert domain_counts(live) == before


def test_list_has_bounded_signed_cursor_and_no_row_total(live):
    created = [save(live) for _ in range(3)]
    first = expect(live.request(live.path(ROUTE), actor="admin", params={"limit": 2}), 200)
    validate("AIDiagnosisList", first)
    assert len(first["items"]) == 2 and first["next_cursor"] and "total_rows" not in first
    seen = {item["object_id"] for item in first["items"]}
    cursor = first["next_cursor"]
    while cursor:
        page = expect(
            live.request(live.path(ROUTE), actor="admin", params={"limit": 2, "cursor": cursor}),
            200,
        )
        validate("AIDiagnosisList", page)
        ids = {item["object_id"] for item in page["items"]}
        assert not seen.intersection(ids)
        seen.update(ids)
        cursor = page["next_cursor"]
    assert {item["object_id"] for item in created} <= seen
    expect(live.request(live.path(ROUTE), actor="admin", params={"limit": 101}), 422)
    expect(
        live.request(
            live.path(ROUTE),
            actor="admin",
            params={"cursor": first["next_cursor"] + "forged"},
        ),
        400,
    )
