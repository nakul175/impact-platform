"""Registered schema46-to47 upgrade through the actual restricted migration runner.

Fresh synthetic databases only; no applied migration bytes or saved history change.
Historical candidate tests remain distinct from ledger/checksum qualification here.
"""

import hashlib
import os
from pathlib import Path
from uuid import UUID

import psycopg
from psycopg.errors import CheckViolation, ForeignKeyViolation
import pytest

from test_ai_diagnosis_linkage_upgrade_native import candidate_absent, seed
from test_ai_diagnosis_upgrade_native import legacy_database, snapshot

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "infrastructure/migrations/0047_diagnosis_evidence_privacy.sql"
pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Registered populated upgrade needs actual restricted PostgreSQL migrator",
)


def column(fixture):
    with psycopg.connect(fixture) as c:
        return c.execute(
            "SELECT data_type,is_nullable FROM information_schema.columns "
            "WHERE table_schema='impact' AND table_name='privacy_case_current' "
            "AND column_name='diagnosis_ids'"
        ).fetchall()


def bindings(fixture, records):
    with psycopg.connect(fixture) as c:
        return [
            c.execute(
                "SELECT revision_id,problem_id,reference_position,evidence_id,evidence_revision "
                "FROM impact.diagnosis_evidence_binding WHERE tenant_id=%s AND object_id=%s "
                "ORDER BY revision_id",
                (tenant, obj),
            ).fetchall()
            for tenant, obj, _, _, _ in records
        ]


def old_bytes():
    return {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted((ROOT / "infrastructure/migrations").glob("*.sql"))
        if int(p.name[:4]) <= 46
    }


def test_registered_populated_linkage_upgrade_preserves_history_and_checksum_noop(live, monkeypatch):
    pinned = old_bytes()
    assert len(pinned) == 46
    checksum = hashlib.sha256(MIGRATION.read_bytes()).hexdigest()
    with legacy_database(monkeypatch) as (migrate, migration, fixture):
        migrate.run(migration, until=46)
        records = seed(fixture, live)
        before = [snapshot(fixture, record[1]) for record in records]
        candidate_absent(fixture)
        assert column(fixture) == []
        result = migrate.run(migration, until=47)
        assert result["session_user"] == "impact_migrator"
        assert result["migration_role"] == "impact_owner"
        assert result["applied"] == [MIGRATION.name] and result["schema_version"] == 47
        assert column(fixture) == [("jsonb", "YES")]
        after = [snapshot(fixture, record[1]) for record in records]
        for old, new in zip(before, after, strict=True):
            assert new["registry"] == old["registry"]
            assert new["revisions"] == old["revisions"]
            assert new["worker_fences"] == old["worker_fences"]
            assert new["migration_ledger"][:-1] == old["migration_ledger"]
            assert new["migration_ledger"][-1] == (47, checksum)
            assert len(new["migration_ledger"]) == 47
        actual = bindings(fixture, records)
        for record, rows in zip(records, actual, strict=True):
            _, _, revisions, problem, ref = record
            assert rows == sorted(
                [
                    (UUID(rev), UUID(problem), 1, UUID(ref["object_id"]), UUID(ref["revision_id"]))
                    for rev in revisions
                ]
            )
        second = migrate.run(migration, until=47)
        assert second["applied"] == [] and second["schema_version"] == 47
        assert [snapshot(fixture, record[1]) for record in records] == after
        assert bindings(fixture, records) == actual
        assert column(fixture) == [("jsonb", "YES")]
    assert old_bytes() == pinned
    assert hashlib.sha256(MIGRATION.read_bytes()).hexdigest() == checksum


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
def test_registered_invalid_history_rolls_back_privacy_column_linkage_and_ledger(live, monkeypatch, fault):
    pinned = old_bytes()
    checksum = hashlib.sha256(MIGRATION.read_bytes()).hexdigest()
    with legacy_database(monkeypatch) as (migrate, migration, fixture):
        migrate.run(migration, until=46)
        records = seed(fixture, live, fault)
        before = [snapshot(fixture, record[1]) for record in records]
        exception = (
            CheckViolation if fault in {"duplicate_current", "extra_key_history"} else ForeignKeyViolation
        )
        for _ in range(2):
            with pytest.raises(exception) as error:
                migrate.run(migration, until=47)
            if exception is CheckViolation:
                assert error.value.diag.constraint_name == "diagnosis_reference_shape_valid"
            assert [snapshot(fixture, record[1]) for record in records] == before
            candidate_absent(fixture)
            assert column(fixture) == []
    assert old_bytes() == pinned
    assert hashlib.sha256(MIGRATION.read_bytes()).hexdigest() == checksum


def test_registered_checksum_mismatch_refuses_without_applied_file_or_database_change(
    live, monkeypatch, tmp_path
):
    pinned = old_bytes()
    actual_bytes = MIGRATION.read_bytes()
    with legacy_database(monkeypatch) as (migrate, migration, fixture):
        migrate.run(migration, until=46)
        records = seed(fixture, live)
        migrate.run(migration, until=47)
        before = [snapshot(fixture, record[1]) for record in records]
        linked = bindings(fixture, records)
        copied = tmp_path / MIGRATION.name
        copied.write_bytes(actual_bytes + b"\n-- Synthetic checksum mismatch probe only.\n")
        original_files = migrate.migration_files()
        monkeypatch.setattr(
            migrate,
            "migration_files",
            lambda: [(version, copied if version == 47 else path) for version, path in original_files],
        )
        with pytest.raises(RuntimeError, match="Migration checksum mismatch: " + MIGRATION.name):
            migrate.run(migration, until=47)
        assert [snapshot(fixture, record[1]) for record in records] == before
        assert bindings(fixture, records) == linked
        assert column(fixture) == [("jsonb", "YES")]
        assert MIGRATION.read_bytes() == actual_bytes
    assert old_bytes() == pinned
    assert MIGRATION.read_bytes() == actual_bytes
