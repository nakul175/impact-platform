"""Actual API selector qualification with bounded disposable object-read fixtures.

The extra grant is synthetic test preparation, not a governed grant-flow pass,
default role/profile widening or human approval. No fixture identity is created.
"""

from contextlib import contextmanager
from copy import deepcopy
from types import SimpleNamespace
from uuid import uuid4

import pytest

from impact_api.store import Context, write
from test_ai_diagnosis_evidence_native import external, selectors
from test_ai_diagnosis_live import action, action_body, diagnosis, domain_counts, get, save
from test_ai_diagnosis_visibility_live import append_fixture_version
from test_live_application import cmd, expect as original_expect


def expect(response, status, code=None):
    result = original_expect(response, status)
    if code is not None:
        assert result["code"] == code
    return result


@contextmanager
def source_access(live, row):
    """Grant only a new synthetic source object in the disposable fixture, then narrow it."""
    tenant, actor = live.fixture["tenant_a"], live.fixture["actors"]["admin"]
    scope = str(uuid4())
    ctx = Context(
        tenant,
        actor["principal_id"],
        actor["membership_id"],
        SimpleNamespace(natural_identity_id=actor["natural_identity_id"]),
        0,
        0,
        [],
    )
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        predicate = c.execute(
            "SELECT predicate_version FROM impact.scope_definition WHERE tenant_id=%s LIMIT 1", (tenant,)
        ).fetchone()["predicate_version"]
        c.execute(
            "INSERT INTO impact.scope_definition(tenant_id,scope_id,scope_type,predicate_version) VALUES(%s,%s,'OBJECT_SET',%s)",
            (tenant, scope, predicate),
        )
        c.execute("INSERT INTO impact.scope_member VALUES(%s,%s,%s)", (tenant, scope, row["object_id"]))
        grant = write(
            c,
            ctx,
            "Grant",
            {
                "subject_id": actor["principal_id"],
                "capability": "evidence.read",
                "scope_id": scope,
                "starts_at": "2020-01-01T00:00:00Z",
                "issuer_id": actor["principal_id"],
            },
            "Active",
            track_author=False,
        )
    try:
        yield grant
    finally:
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            c.execute(
                "UPDATE impact.grant_current SET purpose='synthetic-fixture-ended' WHERE tenant_id=%s AND object_id=%s",
                (tenant, grant["object_id"]),
            )


def linked(row):
    data = diagnosis()
    data["problems"][0]["evidence_references"] = selectors(row)
    return data


def request(live, row, suffix="", **kwargs):
    return live.request(
        live.path("ai-enablement/diagnoses", row["object_id"]) + suffix, actor="admin", **kwargs
    )


def test_default_admin_cannot_create_linked_diagnosis_without_source_read_grant(live):
    evidence = external(live)
    before = domain_counts(live)
    expect(
        live.request(
            live.path("ai-enablement/diagnoses"), actor="admin", method="POST", body=cmd(linked(evidence))
        ),
        404,
        "RESOURCE_UNAVAILABLE",
    )
    assert domain_counts(live) == before


def test_exact_reference_save_completion_correction_and_retry_preserve_notes_and_history(live):
    evidence = external(live)
    with source_access(live, evidence):
        data = linked(evidence)
        body = cmd(data)
        row = save(live, body=body)
        assert get(live, row)["data"]["problems"] == data["problems"]
        assert save(live, body=body) == row
        completed = action(live, row, "complete")
        correction = action(
            live, completed, "revise", body=action_body(completed, reason="Synthetic source correction")
        )
        old = expect(request(live, row, "/revisions/" + completed["revision_id"]), 200)
        assert old["business_state"] == "Completed"
        assert old["data"]["problems"] == data["problems"]
        assert get(live, correction)["business_state"] == "Draft"


def test_current_source_grant_loss_refuses_all_reads_completion_and_exact_replay(live):
    evidence = external(live)
    with source_access(live, evidence):
        body = cmd(linked(evidence))
        row = save(live, body=body)
        assert get(live, row)
    before = domain_counts(live)
    for response in [
        request(live, row),
        request(live, row, "/revisions"),
        request(live, row, "/revisions/" + row["revision_id"]),
        request(live, row, "/actions/complete", method="POST", body=action_body(row)),
        live.request(live.path("ai-enablement/diagnoses"), actor="admin", method="POST", body=body),
    ]:
        expect(response, 404, "RESOURCE_UNAVAILABLE")
    visible = expect(live.request(live.path("ai-enablement/diagnoses"), actor="admin"), 200)
    assert row["object_id"] not in {item["object_id"] for item in visible["items"]}
    assert domain_counts(live) == before


@pytest.mark.parametrize("state", ["RESTRICTED", "REMOVED"])
def test_new_source_unavailability_refuses_completion_without_history_rewrite(live, state):
    evidence = external(live)
    with source_access(live, evidence):
        row = save(live, data=linked(evidence))
        append_fixture_version(live, evidence, evidence["revision_id"], state)
        before = domain_counts(live)
        expect(
            request(live, row, "/actions/complete", method="POST", body=action_body(row)),
            404,
            "RESOURCE_UNAVAILABLE",
        )
        assert domain_counts(live) == before
        with live.db() as c:
            stored = c.execute(
                "SELECT payload FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
                (live.fixture["tenant_a"], row["revision_id"]),
            ).fetchone()["payload"]
        assert stored["diagnosis_state"] == "Draft"
        assert stored["problems"][0]["evidence_references"] == selectors(evidence)


def test_object_scoped_source_grant_does_not_authorize_another_evidence_selector(live):
    first, second = external(live), external(live)
    with source_access(live, first):
        data = linked(first)
        data["problems"][0]["evidence_references"] += selectors(second)
        before = domain_counts(live)
        expect(
            live.request(live.path("ai-enablement/diagnoses"), actor="admin", method="POST", body=cmd(data)),
            404,
            "RESOURCE_UNAVAILABLE",
        )
        assert domain_counts(live) == before


def test_invalid_selector_metadata_is_refused_before_write_and_original_notes_contract_remains(live):
    data = diagnosis()
    original = deepcopy(data)
    data["problems"][0]["evidence_references"] = [
        {"object_id": str(uuid4()), "revision_id": str(uuid4()), "title": "Synthetic private source"}
    ]
    before = domain_counts(live)
    expect(
        live.request(live.path("ai-enablement/diagnoses"), actor="admin", method="POST", body=cmd(data)),
        422,
        "VALIDATION_FAILED",
    )
    assert domain_counts(live) == before
    row = save(live, data=original)
    assert get(live, row)["data"]["problems"] == original["problems"]


def test_old_receipt_and_history_require_old_source_access_after_current_reference_removed(live):
    evidence = external(live)
    with source_access(live, evidence):
        body = cmd(linked(evidence))
        original = save(live, body=body)
        current_data = diagnosis()
        current = expect(
            request(live, original, method="PUT", body=cmd(current_data, original["revision_id"])),
            200,
        )
    before = domain_counts(live)
    assert get(live, current)["data"]["problems"] == current_data["problems"]
    expect(request(live, original, "/revisions/" + original["revision_id"]), 404, "RESOURCE_UNAVAILABLE")
    expect(
        live.request(live.path("ai-enablement/diagnoses"), actor="admin", method="POST", body=body),
        404,
        "RESOURCE_UNAVAILABLE",
    )
    # A hidden old row can yield an empty page with a cursor; continuation must
    # advance over scanned rows instead of repeating or disclosing the old row.
    page = expect(request(live, current, "/revisions?limit=1"), 200)
    assert [item["revision_id"] for item in page["items"]] == [current["revision_id"]]
    assert page["next_cursor"]
    tail = expect(request(live, current, "/revisions?limit=1&cursor=" + page["next_cursor"]), 200)
    assert tail == {"object_id": current["object_id"], "items": [], "next_cursor": None}
    assert domain_counts(live) == before
