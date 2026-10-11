"""Native resolver foundation checks; diagnosis routes are not wired to it yet."""

from datetime import datetime, timezone
import os
from types import SimpleNamespace
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
import pytest

from impact_api.ai_diagnosis_evidence import resolve_references
from impact_api.domain import DomainError
from impact_api.store import hash_data
from test_ai_diagnosis_live import domain_counts, save
from test_ai_diagnosis_visibility_live import append_fixture_version
from test_evidence import CSV, evidence, unique, uploaded
from test_live_application import cmd, expect

pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Protected-reference resolver needs actual provisioned native application login",
)


def external(live):
    return expect(
        live.request(
            live.path("evidence"),
            actor="author",
            method="POST",
            body=cmd(
                {
                    "evidence_type": "ATTENDANCE_SHEET",
                    "external_reference": "https://example.test/synthetic/" + str(uuid4()),
                    "source": "Synthetic public citation",
                }
            ),
        ),
        201,
    )


def resolve(live, refs, tenant=None):
    actor = live.fixture["actors"]["author"]
    identity = SimpleNamespace(identity_id=actor["identity_id"], auth_time=datetime.now(timezone.utc))
    with psycopg.connect(
        os.environ["IMPACT_LOGIN_DSN_APP"], autocommit=True, row_factory=dict_row, prepare_threshold=None
    ) as c:
        with c.transaction():
            c.execute("SET LOCAL ROLE impact_app")
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant or actor["tenant_id"],))
            return resolve_references(c, identity, tenant or actor["tenant_id"], refs)


def selectors(row):
    return [{"object_id": row["object_id"], "revision_id": row["revision_id"]}]


def unavailable(live, refs, **kwargs):
    with pytest.raises(DomainError) as caught:
        resolve(live, refs, **kwargs)
    assert caught.value.code == "RESOURCE_UNAVAILABLE" and caught.value.status == 404
    assert caught.value.message == "The resource is unavailable."
    assert not caught.value.fields


def test_available_external_and_clean_upload_return_exact_selectors_without_metadata(live):
    external_row = external(live)
    upload = uploaded(live, unique(CSV))
    upload_row = expect(evidence(live, upload["upload_id"]), 201)
    refs = selectors(external_row) + selectors(upload_row)
    before = domain_counts(live)
    assert resolve(live, refs) == refs
    assert all(set(ref) == {"object_id", "revision_id"} for ref in resolve(live, refs))
    assert domain_counts(live) == before


@pytest.mark.parametrize(
    "fault", ["missing_object", "missing_revision", "wrong_object_revision", "wrong_kind", "foreign_tenant"]
)
def test_non_disclosing_native_selector_refusals(live, fault):
    row = external(live)
    refs = selectors(row)
    kwargs = {}
    if fault == "missing_object":
        refs[0]["object_id"] = str(uuid4())
    elif fault == "missing_revision":
        refs[0]["revision_id"] = str(uuid4())
    elif fault == "wrong_object_revision":
        refs[0]["revision_id"] = external(live)["revision_id"]
    elif fault == "wrong_kind":
        refs = selectors(save(live))
    else:
        kwargs["tenant"] = live.fixture["tenant_b"]
    unavailable(live, refs, **kwargs)


def test_each_call_rechecks_current_evidence_authority_without_cached_context(live):
    row = external(live)
    refs = selectors(row)
    assert resolve(live, refs) == refs
    tenant, principal = live.fixture["tenant_a"], live.fixture["actors"]["author"]["principal_id"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        grants = c.execute(
            "SELECT object_id,purpose FROM impact.grant_current WHERE tenant_id=%s AND subject_id=%s AND capability='evidence.read' AND purpose IS NULL",
            (tenant, principal),
        ).fetchall()
        assert grants
        c.execute(
            "UPDATE impact.grant_current SET purpose='synthetic-resolver-narrowing' WHERE tenant_id=%s AND object_id=ANY(%s::uuid[])",
            (tenant, [str(g["object_id"]) for g in grants]),
        )
    try:
        unavailable(live, refs)
        unavailable(live, refs)
    finally:
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            for grant in grants:
                c.execute(
                    "UPDATE impact.grant_current SET purpose=%s WHERE tenant_id=%s AND object_id=%s",
                    (grant["purpose"], tenant, grant["object_id"]),
                )
    assert resolve(live, refs) == refs


@pytest.mark.parametrize("state", ["RESTRICTED", "REMOVED"])
def test_new_unavailable_evidence_revision_is_refused_without_rewriting_old_payload(live, state):
    row = external(live)
    original = selectors(row)
    assert resolve(live, original) == original
    restricted = append_fixture_version(live, row, row["revision_id"], state)
    unavailable(live, [{"object_id": row["object_id"], "revision_id": restricted}])
    restored = append_fixture_version(live, row, restricted, "AVAILABLE")
    # Available current head does not make the unavailable historical revision readable.
    unavailable(live, [{"object_id": row["object_id"], "revision_id": restricted}])
    assert resolve(live, original) == original
    assert resolve(live, [{"object_id": row["object_id"], "revision_id": restored}])


@pytest.mark.parametrize("fault", ["invalid_upload_id", "object_upload_id", "missing_source"])
def test_malformed_new_synthetic_stored_source_refuses_without_sql_error_or_metadata(live, fault):
    row = external(live)
    tenant, revision = live.fixture["tenant_a"], str(uuid4())
    # Append a new synthetic corruption fixture, never mutate a saved revision.
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        payload = c.execute(
            "SELECT payload FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
            (tenant, row["revision_id"]),
        ).fetchone()["payload"]
        payload.pop("external_reference", None)
        if fault != "missing_source":
            payload["upload_id"] = (
                "not-a-uuid" if fault == "invalid_upload_id" else {"untrusted": "Synthetic"}
            )
        c.execute(
            "INSERT INTO impact.object_revision(tenant_id,object_id,revision_id,object_type,predecessor_revision,schema_version,payload,payload_sha256,author_id,created_at,restriction_state,revision_number) "
            "SELECT tenant_id,object_id,%s,object_type,revision_id,schema_version,%s,%s,author_id,statement_timestamp(),'AVAILABLE',revision_number+1 "
            "FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
            (revision, Jsonb(payload), hash_data(payload), tenant, row["revision_id"]),
        )
    before = domain_counts(live)
    unavailable(live, [{"object_id": row["object_id"], "revision_id": revision}])
    assert domain_counts(live) == before
    assert resolve(live, selectors(row)) == selectors(row)
