"""Supplemental US-DX-01a current visibility and history cursor checks.

Actual run outcomes are separate; this source does not claim qualification.

Uses synthetic records and the existing owner qualification DB connection. Scope
and classification changes narrow actual fixture authority and restore only that
mutable current projection. Unavailable versions are NEW append-only fixtures,
not operated privacy removals. No old revision, receipt, payload, trigger or
historical criterion is changed. PGlite checks are not native RLS proof.
"""

from contextlib import contextmanager
from uuid import uuid4

import pytest

from impact_api.contracts import validate
from test_ai_diagnosis_live import ROUTE, action, action_body, diagnosis, domain_counts, get, narrowed, save
from test_live_application import cmd, expect


def refused(live, path, *, method="GET", body=None, params=None, status=404, code="RESOURCE_UNAVAILABLE"):
    result = expect(live.request(path, actor="admin", method=method, body=body, params=params), status)
    validate("AIDiagnosisError", result)
    assert result["code"] == code
    return result


def history(live, row, **params):
    result = expect(
        live.request(live.path(ROUTE, row["object_id"]) + "/revisions", actor="admin", params=params),
        200,
    )
    validate("AIDiagnosisHistory", result)
    return result


def listed_ids(live):
    ids, cursor = set(), None
    while True:
        page = expect(
            live.request(live.path(ROUTE), actor="admin", params={"limit": 100, "cursor": cursor}), 200
        )
        validate("AIDiagnosisList", page)
        page_ids = {item["object_id"] for item in page["items"]}
        assert not ids.intersection(page_ids)
        ids.update(page_ids)
        cursor = page["next_cursor"]
        if cursor is None:
            return ids


def stored_versions(live, row):
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        return c.execute(
            "SELECT revision_id,revision_number,predecessor_revision,payload,payload_sha256,"
            "restriction_state,created_at,author_id FROM impact.object_revision "
            "WHERE tenant_id=%s AND object_id=%s ORDER BY revision_number",
            (tenant, row["object_id"]),
        ).fetchall()


@contextmanager
def rescoped(live, capability, *, scope_type, members=()):
    """Narrow real current grants, keeping their membership/predicate version intact."""
    tenant = live.fixture["tenant_a"]
    principal = live.fixture["actors"]["admin"]["principal_id"]
    scope = str(uuid4())
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        grants = c.execute(
            "SELECT g.object_id,g.scope_id,s.predicate_version,s.scope_type FROM impact.grant_current g "
            "JOIN impact.scope_definition s ON s.tenant_id=g.tenant_id AND s.scope_id=g.scope_id "
            "WHERE g.tenant_id=%s AND g.subject_id=%s AND g.capability=%s AND g.purpose IS NULL",
            (tenant, principal, capability),
        ).fetchall()
        assert grants and all(row["scope_type"] == "TENANT" for row in grants)
        assert len({row["predicate_version"] for row in grants}) == 1
        c.execute(
            "INSERT INTO impact.scope_definition(tenant_id,scope_id,scope_type,predicate_version) "
            "VALUES(%s,%s,%s,%s)",
            (tenant, scope, scope_type, grants[0]["predicate_version"]),
        )
        for member in members:
            c.execute("INSERT INTO impact.scope_member VALUES(%s,%s,%s)", (tenant, scope, member))
        c.execute(
            "UPDATE impact.grant_current SET scope_id=%s WHERE tenant_id=%s AND object_id=ANY(%s::uuid[])",
            (scope, tenant, [str(row["object_id"]) for row in grants]),
        )
    try:
        yield
    finally:
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            for row in grants:
                c.execute(
                    "UPDATE impact.grant_current SET scope_id=%s WHERE tenant_id=%s AND object_id=%s",
                    (row["scope_id"], tenant, row["object_id"]),
                )


@pytest.mark.parametrize("capability", ["ai.diagnosis.read", "ai.diagnosis.manage"])
def test_object_only_grants_do_not_authorize_tenant_diagnosis_commands_or_reads(live, capability):
    creation = cmd(diagnosis())
    draft = save(live, body=creation)
    completed = action(live, save(live), "complete")
    draft_path, completed_path = (
        live.path(ROUTE, draft["object_id"]),
        live.path(ROUTE, completed["object_id"]),
    )
    with rescoped(
        live, capability, scope_type="OBJECT_SET", members=(draft["object_id"], completed["object_id"])
    ):
        before = domain_counts(live)
        if capability == "ai.diagnosis.read":
            for path in (
                live.path(ROUTE),
                draft_path,
                draft_path + "/revisions",
                draft_path + "/revisions/" + draft["revision_id"],
                completed_path,
                completed_path + "/revisions/" + completed["revision_id"],
            ):
                refused(live, path)
        else:
            assert get(live, draft)["business_state"] == "Draft"
            assert history(live, draft)["object_id"] == draft["object_id"]
            assert draft["object_id"] in listed_ids(live)
        # These existing objects really are scope members; an OBJECT_SET grant
        # still cannot substitute for the declared TENANT operation capability.
        refused(live, live.path(ROUTE), method="POST", body=creation)
        refused(live, draft_path, method="PUT", body=cmd(diagnosis(), draft["revision_id"]))
        action(live, draft, "complete", status=404)
        action(
            live, completed, "revise", action_body(completed, reason="Synthetic scope refusal"), status=404
        )
        assert domain_counts(live) == before
    assert get(live, draft)["business_state"] == "Draft"
    assert get(live, completed)["business_state"] == "Completed"
    assert save(live, body=creation) == draft


def test_current_classification_hides_current_exact_history_and_receipt_without_rewriting(live):
    creation = cmd(diagnosis())
    draft = save(live, body=creation)
    completion = action_body(draft)
    completed = action(live, draft, "complete", completion)
    original, versions = get(live, completed), stored_versions(live, completed)
    tenant, path = live.fixture["tenant_a"], live.path(ROUTE, completed["object_id"])
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        classification = c.execute(
            "SELECT classification FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
            (tenant, completed["object_id"]),
        ).fetchone()["classification"]
        c.execute(
            "UPDATE impact.object_registry SET classification='RESTRICTED' WHERE tenant_id=%s AND object_id=%s",
            (tenant, completed["object_id"]),
        )
    try:
        before = domain_counts(live)
        for address in (
            path,
            path + "/revisions",
            path + "/revisions/" + draft["revision_id"],
            path + "/revisions/" + completed["revision_id"],
        ):
            refused(live, address)
        assert completed["object_id"] not in listed_ids(live)
        refused(live, live.path(ROUTE), method="POST", body=creation)
        action(live, draft, "complete", completion, status=404)
        assert domain_counts(live) == before
        assert stored_versions(live, completed) == versions
    finally:
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            c.execute(
                "UPDATE impact.object_registry SET classification=%s WHERE tenant_id=%s AND object_id=%s",
                (classification, tenant, completed["object_id"]),
            )
    assert get(live, completed) == original
    assert action(live, draft, "complete", completion) == completed
    assert stored_versions(live, completed) == versions


def append_fixture_version(live, row, predecessor, state):
    """Append a NEW version and advance only forward; never mutate existing history."""
    tenant, revision = live.fixture["tenant_a"], str(uuid4())
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
        c.execute(
            "INSERT INTO impact.object_revision(tenant_id,object_id,revision_id,object_type,"
            "predecessor_revision,schema_version,payload,payload_sha256,author_id,created_at,"
            "restriction_state,revision_number) "
            "SELECT tenant_id,object_id,%s,object_type,%s,schema_version,"
            "CASE WHEN %s='REMOVED' THEN NULL ELSE payload END,payload_sha256,"
            "author_id,statement_timestamp(),%s,(SELECT max(n.revision_number)+1 "
            "FROM impact.object_revision n WHERE n.tenant_id=v.tenant_id AND n.object_id=v.object_id) "
            "FROM impact.object_revision v WHERE tenant_id=%s AND object_id=%s AND revision_id=%s",
            (revision, predecessor, state, state, tenant, row["object_id"], row["revision_id"]),
        )
        c.execute(
            "UPDATE impact.object_registry SET head_revision=%s,updated_at=statement_timestamp() "
            "WHERE tenant_id=%s AND object_id=%s",
            (revision, tenant, row["object_id"]),
        )
    return revision


@pytest.mark.parametrize("restriction", ["RESTRICTED", "REMOVED"])
def test_unavailable_new_head_hides_all_reads_then_available_head_keeps_exact_old_version_opaque(
    live, restriction
):
    creation = cmd(diagnosis())
    row = save(live, body=creation)
    original, original_versions = get(live, row), stored_versions(live, row)
    hidden_revision = append_fixture_version(live, row, row["revision_id"], restriction)
    hidden_versions, path = stored_versions(live, row), live.path(ROUTE, row["object_id"])
    before = domain_counts(live)
    for address in (
        path,
        path + "/revisions",
        path + "/revisions/" + row["revision_id"],
        path + "/revisions/" + hidden_revision,
    ):
        refused(live, address)
    assert row["object_id"] not in listed_ids(live)
    refused(live, live.path(ROUTE), method="POST", body=creation)
    refused(live, path, method="PUT", body=cmd(diagnosis(), hidden_revision))
    assert domain_counts(live) == before and stored_versions(live, row) == hidden_versions
    # This constructs a later synthetic AVAILABLE version, preserving both old
    # versions. It is not a removal/recovery workflow or privacy approval claim.
    available_revision = append_fixture_version(live, row, hidden_revision, "AVAILABLE")
    current = get(live, row)
    assert current["revision_id"] == available_revision and current["data"] == original["data"]
    before = domain_counts(live)
    refused(live, path + "/revisions/" + hidden_revision)
    refused(live, path + "/revisions/" + str(uuid4()))
    assert {item["revision_id"] for item in history(live, row)["items"]} == {
        row["revision_id"],
        available_revision,
    }
    assert save(live, body=creation) == row
    assert domain_counts(live) == before
    retained = stored_versions(live, row)
    assert retained[:1] == original_versions and retained[:2] == hidden_versions


def test_history_cursor_binds_object_route_scope_and_current_grant(live):
    row, other = save(live), save(live)
    update = expect(
        live.request(
            live.path(ROUTE, row["object_id"]),
            actor="admin",
            method="PUT",
            body=cmd(diagnosis(), row["revision_id"]),
        ),
        200,
    )
    validate("AIDiagnosisReceipt", update)
    page = history(live, row, limit=1)
    assert page["items"][0]["revision_id"] == update["revision_id"] and page["next_cursor"]
    cursor, path = page["next_cursor"], live.path(ROUTE, row["object_id"]) + "/revisions"
    before = domain_counts(live)
    for address in (live.path(ROUTE, other["object_id"]) + "/revisions", live.path(ROUTE)):
        refused(live, address, params={"cursor": cursor}, status=400, code="INVALID_CURSOR")
    # Another TENANT scope still authorizes the read, but changes the visibility
    # binding. Reusing its predecessor's signed cursor must be refused.
    with rescoped(live, "ai.diagnosis.read", scope_type="TENANT"):
        assert get(live, row)["revision_id"] == update["revision_id"]
        refused(live, path, params={"cursor": cursor}, status=400, code="INVALID_CURSOR")
    with narrowed(live, "ai.diagnosis.read"):
        refused(live, path, params={"cursor": cursor})
    assert history(live, row, cursor=cursor)["items"][0]["revision_id"] == row["revision_id"]
    assert domain_counts(live) == before
