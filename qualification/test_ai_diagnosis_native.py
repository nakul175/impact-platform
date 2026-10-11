"""NOT RUN: US-DX-01a native-only tenant fences, history guards and real edit race.

Requires the existing provisioned login harness. A PGlite run skips these checks;
the skip is not passing evidence. No new runtime grants or waiver identities.
"""

from copy import deepcopy
import os

import psycopg
import pytest

from test_ai_diagnosis_live import get, save
from test_live_application import cmd
from test_native_concurrency import count, outcomes, race, sender
from test_native_roles import denied

pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Native PostgreSQL login-role fences and simultaneous transactions cannot be qualified on PGlite",
)


def login(name):
    dsn = os.environ.get("IMPACT_LOGIN_DSN_" + name)
    assert dsn, "Native harness must provision the " + name + " login"
    return psycopg.connect(dsn, autocommit=True, prepare_threshold=None)


def test_native_diagnosis_shared_registry_and_revision_have_forced_tenant_fences(live):
    row = save(live)
    tenant_a, tenant_b = live.fixture["tenant_a"], live.fixture["tenant_b"]
    with login("APP") as c:
        for table in ("object_registry", "object_revision"):
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                assert c.execute(
                    "SELECT relrowsecurity,relforcerowsecurity FROM pg_class WHERE oid=%s::regclass",
                    ("impact." + table,),
                ).fetchone() == (True, True)
                assert (
                    c.execute(
                        "SELECT tenant_id FROM impact." + table + " WHERE object_id=%s",
                        (row["object_id"],),
                    ).fetchall()
                    == []
                )
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_b,))
                assert (
                    c.execute(
                        "SELECT tenant_id FROM impact." + table + " WHERE object_id=%s",
                        (row["object_id"],),
                    ).fetchall()
                    == []
                )
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_a,))
                seen = c.execute(
                    "SELECT tenant_id FROM impact." + table + " WHERE object_id=%s",
                    (row["object_id"],),
                ).fetchall()
                assert seen and {str(item[0]) for item in seen} == {tenant_a}


def test_native_application_cannot_rewrite_or_delete_a_saved_diagnosis_revision(live):
    row = save(live)
    tenant = live.fixture["tenant_a"]
    original = get(live, row)
    with login("APP") as c:
        for statement in (
            "UPDATE impact.object_revision SET payload='{}'::jsonb WHERE tenant_id=%s AND revision_id=%s",
            "DELETE FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
        ):
            denied(
                c,
                statement,
                (tenant, row["revision_id"]),
                role="impact_app",
                tenant=tenant,
            )
    assert get(live, row) == original


def test_native_platform_restrictive_kind_list_does_not_gain_diagnosis_access(live):
    row = save(live)
    tenant = live.fixture["tenant_a"]
    with login("PLATFORM") as c:
        for table in ("object_registry", "object_revision"):
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_platform")
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
                assert (
                    c.execute(
                        "SELECT tenant_id FROM impact." + table + " WHERE object_id=%s",
                        (row["object_id"],),
                    ).fetchall()
                    == []
                )


def test_native_two_diagnosis_edits_publish_one_authoritative_head_and_one_conflict(
    live,
):
    row = save(live)
    original = get(live, row)
    first = {key: deepcopy(original["data"][key]) for key in ("title", "problems", "priority_order")}
    second = deepcopy(first)
    first["title"] = "Synthetic concurrent edit A"
    second["title"] = "Synthetic concurrent edit B"
    first_body, second_body = (
        cmd(first, row["revision_id"]),
        cmd(second, row["revision_id"]),
    )
    token = live.token("admin")
    path = live.path("ai-enablement/diagnoses", row["object_id"])
    results = race(
        sender(live, token, "PUT", path, first_body),
        sender(live, token, "PUT", path, second_body),
    )
    assert outcomes(results) == [200, 409]
    winners = [item for item in results if item["status"] == 200]
    losers = [item for item in results if item["status"] == 409]
    assert losers[0]["body"]["code"] == "CONFLICT_VERSION"
    current = get(live, row)
    assert current["revision_id"] == winners[0]["body"]["revision_id"]
    assert current["data"]["title"] in {first["title"], second["title"]}
    tenant = live.fixture["tenant_a"]
    assert (
        count(
            live,
            "SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s",
            tenant,
            row["object_id"],
        )
        == 2
    )
    assert (
        count(
            live,
            "SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s AND operation_id=ANY(%s::uuid[])",
            tenant,
            [first_body["operation_id"], second_body["operation_id"]],
        )
        == 1
    )
    assert (
        count(
            live,
            "SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s AND object_reference=%s",
            tenant,
            row["object_id"],
        )
        == 2
    )
