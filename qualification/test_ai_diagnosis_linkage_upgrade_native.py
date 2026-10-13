"""Unregistered linkage candidate on populated schema46; no registration/release claim.

Only fresh disposable databases: never rewrite a saved revision or applied SQL.
Actual restricted migrator executes the sealed candidate through migrate's script
primitive. Invalid current/older synthetic history must leave no candidate DDL.
"""

from copy import deepcopy
import os
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID, uuid4

import psycopg
from psycopg.errors import CheckViolation, DuplicateFunction, ForeignKeyViolation
from psycopg.types.json import Jsonb
import pytest

from impact_api.store import Context, hash_data, write
from test_ai_diagnosis_live import diagnosis
from test_ai_diagnosis_upgrade_native import legacy_database, snapshot

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "docs/engineering/delivery-system-20261011/diagnosis-evidence-linkage.CANDIDATE.sql"
pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Populated candidate rollback requires actual restricted PostgreSQL migrator",
)


def seed(fixture, live, fault=None):
    actors = sorted(
        [live.fixture["actors"][name] for name in ("admin", "other_tenant")],
        key=lambda actor: actor["tenant_id"],
    )
    sources, records = [], []
    with psycopg.connect(fixture) as c:
        for actor in actors:
            tenant = actor["tenant_id"]
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            ctx = Context(
                tenant,
                actor["principal_id"],
                actor["membership_id"],
                SimpleNamespace(natural_identity_id=actor["natural_identity_id"]),
                0,
                0,
                [],
            )
            sources.append(write(c, ctx, "Evidence", {"external_reference": "https://example.test/upgrade"}))
        for tenant_index, actor in enumerate(actors):
            tenant, author = actor["tenant_id"], actor["principal_id"]
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            obj, revisions = str(uuid4()), [str(uuid4()) for _ in range(3)]
            data = {**diagnosis(), "diagnosis_state": "Draft"}
            reference = {
                "object_id": sources[tenant_index]["object_id"],
                "revision_id": sources[tenant_index]["revision_id"],
            }
            data["problems"][0]["evidence_references"] = [reference]
            # Both absent and explicitly empty references remain compatible.
            data["problems"][1]["evidence_references"] = []
            completed = {
                **deepcopy(data),
                "diagnosis_state": "Completed",
                "completed_at": "2026-10-11T15:00:00Z",
                "completed_by": author,
            }
            corrected = {**deepcopy(data), "correction_reason": "Synthetic legacy correction"}
            del corrected["problems"][1]["evidence_references"]
            bodies = [data, completed, corrected]
            if tenant_index == 1 and fault:
                selected = bodies[2 if fault.endswith("current") else 1]
                refs = selected["problems"][0]["evidence_references"]
                if fault == "duplicate_current":
                    refs.append(deepcopy(refs[0]))
                elif fault == "extra_key_history":
                    refs[0]["title"] = "untrusted metadata"
                elif fault == "missing_history":
                    refs[0]["revision_id"] = str(uuid4())
                elif fault == "wrong_object_current":
                    refs[0]["object_id"] = str(uuid4())
                elif fault == "wrong_kind_history":
                    refs[0] = {"object_id": obj, "revision_id": revisions[0]}
                elif fault == "foreign_tenant_history":
                    refs[0] = {
                        "object_id": sources[0]["object_id"],
                        "revision_id": sources[0]["revision_id"],
                    }
                else:
                    raise AssertionError(fault)
            c.execute(
                "INSERT INTO impact.object_registry(tenant_id,object_id,object_type,head_revision,"
                "lifecycle_state,classification,owner_id,created_by,created_at,updated_at) "
                "VALUES(%s,%s,'AIDiagnosis',%s,'Draft','INTERNAL',%s,%s,now(),now())",
                (tenant, obj, revisions[-1], author, author),
            )
            for index, body in enumerate(bodies):
                c.execute(
                    "INSERT INTO impact.object_revision(tenant_id,object_id,revision_id,object_type,"
                    "predecessor_revision,schema_version,payload,payload_sha256,author_id,created_at,revision_number) "
                    "VALUES(%s,%s,%s,'AIDiagnosis',%s,'1.30.0',%s,%s,%s,now(),%s)",
                    (
                        tenant,
                        obj,
                        revisions[index],
                        revisions[index - 1] if index else None,
                        Jsonb(body),
                        hash_data(body),
                        author,
                        index + 1,
                    ),
                )
            records.append((tenant, obj, revisions, data["problems"][0]["problem_id"], reference))
    return records


def apply(migrate, migration):
    with psycopg.connect(migration, autocommit=True) as c:
        assert c.execute(
            "SELECT session_user,rolsuper,rolbypassrls FROM pg_roles WHERE rolname=session_user"
        ).fetchone() == ("impact_migrator", False, False)
        with c.transaction():
            migrate.execute_script(c, CANDIDATE.read_text())


def candidate_absent(fixture):
    with psycopg.connect(fixture) as c:
        assert c.execute("SELECT to_regclass('impact.diagnosis_evidence_binding')").fetchone() == (None,)
        for name in (
            "diagnosis_reference_shape_valid(jsonb)",
            "guard_diagnosis_binding()",
            "populate_diagnosis_bindings()",
            "cleanup_diagnosis_bindings()",
        ):
            assert c.execute("SELECT to_regprocedure(%s)", ("impact." + name,)).fetchone() == (None,)
        assert (
            c.execute(
                "SELECT 1 FROM pg_constraint WHERE conname='diagnosis_reference_shape_valid'"
            ).fetchone()
            is None
        )
        assert (
            c.execute(
                "SELECT 1 FROM pg_trigger WHERE tgname IN ('populate_diagnosis_bindings','cleanup_diagnosis_bindings','diagnosis_binding_guard')"
            ).fetchone()
            is None
        )
        assert c.execute("SELECT max(version) FROM impact.schema_migration").fetchone() == (46,)


def test_valid_populated_candidate_preserves_history_and_reapply_refuses_without_changes(live, monkeypatch):
    with legacy_database(monkeypatch) as (migrate, migration, fixture):
        migrate.run(migration, until=46)
        records = seed(fixture, live)
        before = [snapshot(fixture, record[1]) for record in records]
        candidate_absent(fixture)
        apply(migrate, migration)
        assert [snapshot(fixture, record[1]) for record in records] == before
        with psycopg.connect(migration) as c:
            c.execute("SET LOCAL ROLE impact_owner")
            for tenant, obj, revisions, problem, ref in records:
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
                bindings = c.execute(
                    "SELECT revision_id,problem_id,reference_position,evidence_id,evidence_revision FROM impact.diagnosis_evidence_binding WHERE tenant_id=%s AND object_id=%s ORDER BY revision_id",
                    (tenant, obj),
                ).fetchall()
                assert bindings == sorted(
                    [
                        (
                            UUID(rev),
                            UUID(problem),
                            1,
                            UUID(ref["object_id"]),
                            UUID(ref["revision_id"]),
                        )
                        for rev in revisions
                    ]
                )
        with pytest.raises(DuplicateFunction):
            apply(migrate, migration)
        assert [snapshot(fixture, record[1]) for record in records] == before
        # This is DDL reapply refusal, explicitly not checksum-ledgered migration retry.


@pytest.mark.parametrize(
    "fault",
    [
        "duplicate_current",
        "extra_key_history",
        "missing_history",
        "wrong_object_current",
        "wrong_kind_history",
        "foreign_tenant_history",
    ],
)
def test_invalid_populated_candidate_rolls_back_every_new_object_and_history(live, monkeypatch, fault):
    with legacy_database(monkeypatch) as (migrate, migration, fixture):
        migrate.run(migration, until=46)
        records = seed(fixture, live, fault)
        before = [snapshot(fixture, record[1]) for record in records]
        exception = (
            CheckViolation if fault in {"duplicate_current", "extra_key_history"} else ForeignKeyViolation
        )
        for _ in range(2):
            with pytest.raises(exception) as error:
                apply(migrate, migration)
            if exception is CheckViolation:
                assert error.value.diag.constraint_name == "diagnosis_reference_shape_valid"
            assert [snapshot(fixture, record[1]) for record in records] == before
            candidate_absent(fixture)
