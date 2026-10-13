"""Real schema45 diagnosis history upgrades, including atomic refusal of corrupt history.

Only disposable synthetic fixture databases are created, using existing login roles.
No applied migration, role membership, immutable history or original criterion changes.
"""

from contextlib import contextmanager
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo
from psycopg.errors import CheckViolation
from psycopg.types.json import Jsonb
import pytest

from test_ai_diagnosis_live import diagnosis

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Real restricted migration login and atomic PostgreSQL upgrade need the native harness",
)


@contextmanager
def legacy_database(monkeypatch):
    sys.path.insert(0, str(ROOT / "scripts"))
    import migrate

    target = "impact_test_diagnosis_upgrade_" + uuid4().hex
    admin = os.environ["IMPACT_FIXTURE_DSN"]
    migration = make_conninfo(os.environ["IMPACT_LOGIN_DSN_MIGRATOR"], dbname=target)
    fixture = make_conninfo(admin, dbname=target)
    with psycopg.connect(admin, autocommit=True) as c:
        assert c.execute("SELECT rolsuper FROM pg_roles WHERE rolname=current_user").fetchone() == (True,)
        c.execute(sql.SQL("CREATE DATABASE {} OWNER impact_owner").format(sql.Identifier(target)))
    try:
        monkeypatch.setenv("IMPACT_ALLOW_FIXTURE_LOAD", "1")
        baseline = migrate.run(migration, fixture, until=45, fixture=True)
        assert baseline["schema_version"] == 45 and baseline["fixture_loaded"]
        assert baseline["session_user"] == "impact_migrator"
        assert baseline["migration_role"] == "impact_owner"
        yield migrate, migration, fixture
    finally:
        with psycopg.connect(admin, autocommit=True) as c:
            c.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(target)))
            assert c.execute("SELECT 1 FROM pg_database WHERE datname=%s", (target,)).fetchone() is None


def seed_history(fixture, live, fault=None):
    tenant = live.fixture["tenant_a"]
    author = live.fixture["actors"]["admin"]["principal_id"]
    object_id = str(uuid4())
    revisions = [str(uuid4()) for _ in range(3)]
    draft = {**diagnosis(), "diagnosis_state": "Draft"}
    completed = {
        **deepcopy(draft),
        "diagnosis_state": "Completed",
        "completed_at": "2026-10-11T12:00:00+00:00",
        "completed_by": author,
    }
    corrected = {**deepcopy(draft), "correction_reason": "Synthetic legacy correction"}
    if fault == "bad_id":
        corrected["problems"][0]["problem_id"] = "not-a-uuid"
    elif fault == "duplicate_priority":
        completed["priority_order"][1] = completed["priority_order"][0]
    with psycopg.connect(fixture) as c:
        c.execute(
            "INSERT INTO impact.object_registry(tenant_id,object_id,object_type,head_revision,"
            "lifecycle_state,classification,owner_id,created_by,created_at,updated_at) "
            "VALUES(%s,%s,'AIDiagnosis',%s,'Draft','INTERNAL',%s,%s,now(),now())",
            (tenant, object_id, revisions[-1], author, author),
        )
        for index, body in enumerate((draft, completed, corrected)):
            encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
            c.execute(
                "INSERT INTO impact.object_revision(tenant_id,object_id,revision_id,object_type,"
                "predecessor_revision,schema_version,payload,payload_sha256,author_id,created_at,revision_number) "
                "VALUES(%s,%s,%s,'AIDiagnosis',%s,'1.29.0',%s,%s,%s,now(),%s)",
                (
                    tenant,
                    object_id,
                    revisions[index],
                    revisions[index - 1] if index else None,
                    Jsonb(body),
                    hashlib.sha256(encoded).digest(),
                    author,
                    index + 1,
                ),
            )
    return object_id


def snapshot(fixture, object_id):
    with psycopg.connect(fixture) as c:
        return {
            "registry": c.execute(
                "SELECT to_jsonb(r)::text FROM impact.object_registry r WHERE object_id=%s", (object_id,)
            ).fetchall(),
            "revisions": c.execute(
                "SELECT to_jsonb(v)::text FROM impact.object_revision v WHERE object_id=%s "
                "ORDER BY revision_number",
                (object_id,),
            ).fetchall(),
            "migration_ledger": c.execute(
                "SELECT version,sha256 FROM impact.schema_migration ORDER BY version"
            ).fetchall(),
            "worker_fences": c.execute(
                "SELECT polname,polpermissive,pg_get_expr(polqual,polrelid),pg_get_expr(polwithcheck,polrelid) "
                "FROM pg_policy WHERE polname IN ('worker_diagnosis_registry_fence',"
                "'worker_diagnosis_revision_fence') ORDER BY polname"
            ).fetchall(),
        }


def test_valid_legacy_diagnosis_upgrade_preserves_exact_all_revision_history(live, monkeypatch):
    with legacy_database(monkeypatch) as (migrate, migration, fixture):
        object_id = seed_history(fixture, live)
        before = snapshot(fixture, object_id)
        result = migrate.run(migration, until=46)
        assert result["applied"] == ["0046_diagnosis_problem_order.sql"]
        assert result["schema_version"] == 46
        after = snapshot(fixture, object_id)
        assert after["registry"] == before["registry"]
        assert after["revisions"] == before["revisions"] and len(after["revisions"]) == 3
        assert after["worker_fences"] == before["worker_fences"] and len(after["worker_fences"]) == 2
        assert after["migration_ledger"][:-1] == before["migration_ledger"]
        assert after["migration_ledger"][-1] == (
            46,
            hashlib.sha256(
                (ROOT / "infrastructure/migrations/0046_diagnosis_problem_order.sql").read_bytes()
            ).hexdigest(),
        )
        assert migrate.run(migration, until=46)["applied"] == []
        assert snapshot(fixture, object_id) == after


@pytest.mark.parametrize("fault", ["bad_id", "duplicate_priority"])
def test_invalid_legacy_diagnosis_refuses_upgrade_and_rolls_back_every_new_object(live, monkeypatch, fault):
    with legacy_database(monkeypatch) as (migrate, migration, fixture):
        object_id = seed_history(fixture, live, fault=fault)
        before = snapshot(fixture, object_id)
        for _ in range(2):
            with pytest.raises(CheckViolation) as error:
                migrate.run(migration, until=46)
            assert error.value.diag.constraint_name == "diagnosis_problem_order_valid"
            assert snapshot(fixture, object_id) == before
            with psycopg.connect(fixture) as c:
                assert c.execute(
                    "SELECT to_regprocedure('impact.diagnosis_problem_order_valid(jsonb)')"
                ).fetchone() == (None,)
                assert (
                    c.execute(
                        "SELECT 1 FROM pg_constraint WHERE conrelid='impact.object_revision'::regclass "
                        "AND conname='diagnosis_problem_order_valid'"
                    ).fetchone()
                    is None
                )
                assert c.execute("SELECT max(version) FROM impact.schema_migration").fetchone() == (45,)
