"""Real backup/restore of unregistered linkage; not registration or API recovery."""

from copy import deepcopy
import json
import os
import sys

import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo
from psycopg.errors import ForeignKeyViolation, InsufficientPrivilege
import pytest

from test_ai_diagnosis_evidence_live import external, linked, source_access
from test_ai_diagnosis_linkage_candidate_native import ROOT, linkage, rows  # noqa: F401
from test_ai_diagnosis_live import action, action_body, save
from test_ai_diagnosis_payload_native import insert_copy, payload
from test_ai_diagnosis_upgrade_native import snapshot

pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Actual pg_dump/pg_restore and restricted runtime logins required",
)


@pytest.mark.usefixtures("linkage")
def test_real_restored_linkage_preserves_history_triggers_and_runtime_fences(live):
    sys.path.insert(0, str(ROOT / "scripts"))
    import restore_drill

    fixture = os.environ["IMPACT_FIXTURE_DSN"]
    target = restore_drill.conninfo_to_dict(fixture)["dbname"] + "_restored"
    restored = make_conninfo(fixture, dbname=target)
    source = external(live)
    with source_access(live, source):
        draft = save(live, data=linked(source))
        completed = action(live, draft, "complete")
        current = action(live, completed, "revise", action_body(completed, reason="Synthetic linked restore"))
        original = snapshot(fixture, current["object_id"])
        bindings = {row["revision_id"]: rows(live, row) for row in [draft, completed, current]}
        data = payload(live, current)
        try:
            result = restore_drill.run(
                fixture,
                fixture,
                restore_drill.passwords_from_env(os.environ),
                os.environ["IMPACT_PG_BIN"],
                keep=True,
            )
            # Private run artifact contains no password or signed session.
            (live.local / "diagnosis-linkage-restore.json").write_text(json.dumps(result, indent=2) + "\n")
            assert result["outcome"] == "PASS" and all(result["checks"].values())
            assert result["dump"]["bytes"] > 0 and result["restore"]["warnings"] is None
            assert result["migration"]["schema_version"] == 46
            assert result["migration"]["applied"] == []
            assert snapshot(restored, current["object_id"]) == original
            with psycopg.connect(
                make_conninfo(os.environ["IMPACT_LOGIN_DSN_APP"], dbname=target), autocommit=True
            ) as c:
                assert c.execute(
                    "SELECT rolsuper,rolbypassrls FROM pg_roles WHERE rolname=session_user"
                ).fetchone() == (False, False)
                for tenant in [None, live.fixture["tenant_b"], live.fixture["tenant_a"]]:
                    with c.transaction():
                        c.execute("SET LOCAL ROLE impact_app")
                        if tenant:
                            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
                        for revision, expected in bindings.items():
                            actual = c.execute(
                                "SELECT problem_id,reference_position,evidence_id,evidence_revision "
                                "FROM impact.diagnosis_evidence_binding WHERE object_id=%s AND revision_id=%s "
                                "ORDER BY problem_id,reference_position",
                                (current["object_id"], revision),
                            ).fetchall()
                            assert actual == (expected if tenant == live.fixture["tenant_a"] else [])
                with c.transaction(force_rollback=True):
                    c.execute("SET LOCAL ROLE impact_app")
                    c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
                    before = c.execute(
                        "SELECT count(*) FROM impact.diagnosis_evidence_binding WHERE object_id=%s",
                        (current["object_id"],),
                    ).fetchone()[0]
                    # Only inside a rolled-back transaction: prove the restored
                    # population trigger creates one exact reference binding.
                    insert_copy(c, current, data)
                    assert (
                        c.execute(
                            "SELECT count(*) FROM impact.diagnosis_evidence_binding WHERE object_id=%s",
                            (current["object_id"],),
                        ).fetchone()[0]
                        == before + 1
                    )
                    assert (
                        c.execute(
                            "SELECT problem_id,reference_position,evidence_id,evidence_revision "
                            "FROM impact.diagnosis_evidence_binding WHERE object_id=%s "
                            "AND revision_id<>ALL(%s::uuid[]) ORDER BY problem_id,reference_position",
                            (current["object_id"], list(bindings)),
                        ).fetchall()
                        == bindings[current["revision_id"]]
                    )
                invalid = deepcopy(data)
                invalid["problems"][0]["evidence_references"][0]["revision_id"] = current["revision_id"]
                with pytest.raises(ForeignKeyViolation):
                    with c.transaction():
                        c.execute("SET LOCAL ROLE impact_app")
                        c.execute(
                            "SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],)
                        )
                        insert_copy(c, current, invalid)
            for name, role in [
                ("WORKER", "impact_worker"),
                ("PLATFORM", "impact_platform"),
                ("IDENTITY", "impact_identity"),
            ]:
                with psycopg.connect(
                    make_conninfo(os.environ["IMPACT_LOGIN_DSN_" + name], dbname=target),
                    autocommit=True,
                ) as c:
                    with pytest.raises(InsufficientPrivilege):
                        with c.transaction():
                            c.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))
                            c.execute(
                                "SELECT set_config('impact.tenant_id',%s,true)",
                                (live.fixture["tenant_a"],),
                            )
                            c.execute("SELECT * FROM impact.diagnosis_evidence_binding")
            assert snapshot(restored, current["object_id"]) == original
        finally:
            with psycopg.connect(fixture, autocommit=True) as c:
                c.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(target)))
                assert c.execute("SELECT 1 FROM pg_database WHERE datname=%s", (target,)).fetchone() is None
