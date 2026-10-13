"""Unregistered pure storage guard experiment; no FK/linkage or release claim."""

from copy import deepcopy
import os
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg.errors import CheckViolation
from psycopg.types.json import Jsonb
import pytest

from test_ai_diagnosis_live import diagnosis, save
from test_ai_diagnosis_native import login
from test_ai_diagnosis_payload_native import insert_copy, payload
import test_report_exports as exports
import test_worker as worker_tests

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Restricted migration/application login storage experiment requires native PostgreSQL",
)


@pytest.fixture(scope="module")
def installed_shape():
    with psycopg.connect(os.environ["IMPACT_LOGIN_DSN_MIGRATOR"], autocommit=True) as c:
        c.execute(
            (
                ROOT / "docs/engineering/delivery-system-20261011/diagnosis-evidence-shape.DRAFT.sql"
            ).read_text()
        )
    try:
        yield
    finally:
        with psycopg.connect(os.environ["IMPACT_LOGIN_DSN_MIGRATOR"], autocommit=True) as c:
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_owner")
                c.execute("ALTER TABLE impact.object_revision DROP CONSTRAINT diagnosis_evidence_shape_valid")
                c.execute("DROP FUNCTION impact.diagnosis_evidence_shape_valid(jsonb)")
                assert c.execute(
                    "SELECT to_regprocedure('impact.diagnosis_evidence_shape_valid(jsonb)')"
                ).fetchone() == (None,)


@pytest.mark.parametrize(
    "fault",
    [
        "null",
        "object",
        "scalar",
        "missing_key",
        "extra_key",
        "invalid_uuid",
        "uppercase",
        "number",
        "duplicate",
        "too_many",
    ],
)
def test_actual_app_sql_refuses_malformed_optional_references(installed_shape, live, fault):
    row = save(live)
    data = deepcopy(payload(live, row))
    ref = {"object_id": str(uuid4()), "revision_id": str(uuid4())}
    refs = [ref]
    if fault == "null":
        refs = None
    elif fault == "object":
        refs = {}
    elif fault == "scalar":
        refs = ["invalid"]
    elif fault == "missing_key":
        del ref["revision_id"]
    elif fault == "extra_key":
        ref["title"] = "Synthetic source metadata"
    elif fault == "invalid_uuid":
        ref["object_id"] = "not-a-uuid"
    elif fault == "uppercase":
        ref["revision_id"] = "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA"
    elif fault == "number":
        ref["object_id"] = 1
    elif fault == "duplicate":
        refs += [deepcopy(ref)]
    elif fault == "too_many":
        refs = [{"object_id": str(uuid4()), "revision_id": str(uuid4())} for _ in range(6)]
    data["problems"][0]["evidence_references"] = refs
    with login("APP") as c:
        with pytest.raises(CheckViolation) as error:
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
                insert_copy(c, row, data)
        assert error.value.diag.constraint_name == "diagnosis_evidence_shape_valid"
    assert payload(live, row) != data


def test_restricted_migrator_enumerates_both_tenants_without_disabling_rls(installed_shape, live):
    with psycopg.connect(os.environ["IMPACT_LOGIN_DSN_MIGRATOR"]) as c:
        c.execute("SET LOCAL ROLE impact_owner")
        assert c.execute(
            "SELECT rolsuper,rolbypassrls FROM pg_roles WHERE rolname=session_user"
        ).fetchone() == (False, False)
        c.execute("SELECT set_config('impact.tenant_id','',true)")
        tenants = {str(row[0]) for row in c.execute("SELECT tenant_id FROM impact.tenant_root").fetchall()}
        assert {live.fixture["tenant_a"], live.fixture["tenant_b"]} <= tenants
        assert c.execute(
            "SELECT polname FROM pg_policy WHERE polrelid='impact.tenant_root'::regclass AND polname='worker_tenant_directory'"
        ).fetchone()
        assert c.execute(
            "SELECT relrowsecurity,relforcerowsecurity FROM pg_class WHERE oid='impact.object_revision'::regclass"
        ).fetchone() == (True, True)
        assert c.execute("SELECT count(*) FROM impact.object_revision").fetchone() == (0,)
        for tenant in sorted(tenants):
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            seen = {
                str(row[0])
                for row in c.execute("SELECT DISTINCT tenant_id FROM impact.object_revision").fetchall()
            }
            assert seen <= {tenant}


def test_pure_guard_preserves_absent_empty_valid_refs_and_removed_null(installed_shape, live):
    data = diagnosis()
    with login("APP") as c:
        with c.transaction():
            c.execute("SET LOCAL ROLE impact_app")
            assert c.execute(
                "SELECT impact.diagnosis_evidence_shape_valid(%s)", (Jsonb(data),)
            ).fetchone() == (True,)
            data["problems"][0]["evidence_references"] = []
            assert c.execute(
                "SELECT impact.diagnosis_evidence_shape_valid(%s)", (Jsonb(data),)
            ).fetchone() == (True,)
            data["problems"][0]["evidence_references"] = [
                {"object_id": str(uuid4()), "revision_id": str(uuid4())}
            ]
            assert c.execute(
                "SELECT impact.diagnosis_evidence_shape_valid(%s)", (Jsonb(data),)
            ).fetchone() == (True,)
    row = save(live)
    with login("APP") as c:
        with c.transaction():
            c.execute("SET LOCAL ROLE impact_app")
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
            insert_copy(c, row, None, "REMOVED")
            raise psycopg.Rollback()  # SQL NULL branch only; not governed privacy execution.


def test_shape_predicate_is_pure_invoker_with_only_existing_writer_execution(installed_shape, live):
    with login("APP") as c:
        with c.transaction():
            c.execute("SET LOCAL ROLE impact_app")
            assert c.execute(
                "SELECT prosecdef,provolatile,proconfig FROM pg_proc "
                "WHERE oid='impact.diagnosis_evidence_shape_valid(jsonb)'::regprocedure"
            ).fetchone() == (False, "i", ["search_path=pg_catalog"])
            for role in ["impact_app", "impact_worker", "impact_platform", "impact_privacy"]:
                assert c.execute(
                    "SELECT has_function_privilege(%s,'impact.diagnosis_evidence_shape_valid(jsonb)','EXECUTE')",
                    (role,),
                ).fetchone() == (True,)
            assert c.execute(
                "SELECT has_function_privilege('impact_identity','impact.diagnosis_evidence_shape_valid(jsonb)','EXECUTE')"
            ).fetchone() == (False,)


def test_reminders_and_pinned_exports_run_while_experimental_guard_is_installed(installed_shape, live):
    # Existing unchanged assertions execute while the prototype constraint is
    # active, rather than after its module fixture removes it.
    worker_tests.test_authority_expiry_reminders_are_idempotent_per_threshold(live)
    exports.test_worker_renders_immutable_artifacts_whose_numbers_match_the_snapshot_and_html(live)
