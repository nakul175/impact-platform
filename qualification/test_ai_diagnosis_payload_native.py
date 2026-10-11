"""Native storage rejects malformed diagnosis IDs/order independently of HTTP validation."""

from copy import deepcopy
import os
from uuid import uuid4

from psycopg.errors import CheckViolation
from psycopg.types.json import Jsonb
import pytest

from test_ai_diagnosis_live import action, action_body, get, save
from test_ai_diagnosis_native import login
from test_native_roles import Rollback

pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Actual application login SQL constraints require native PostgreSQL",
)


def payload(live, row):
    with live.db() as c:
        return c.execute(
            "SELECT payload FROM impact.object_revision WHERE revision_id=%s", (row["revision_id"],)
        ).fetchone()["payload"]


def insert_copy(c, row, body, restriction="AVAILABLE"):
    c.execute(
        "INSERT INTO impact.object_revision(tenant_id,object_id,revision_id,object_type,schema_version,"
        "payload,payload_sha256,author_id,created_at,restriction_state,revision_number) "
        "SELECT tenant_id,object_id,%s,object_type,schema_version,%s,payload_sha256,author_id,"
        "created_at,%s,revision_number+1 FROM impact.object_revision WHERE revision_id=%s",
        (str(uuid4()), Jsonb(body) if body is not None else None, restriction, row["revision_id"]),
    )


@pytest.mark.parametrize(
    "fault",
    [
        "missing_problems",
        "null_problems",
        "object_problems",
        "scalar_problem",
        "missing_id",
        "null_id",
        "number_id",
        "invalid_id",
        "uppercase_id",
        "duplicate_id",
        "too_many_problems",
        "missing_order",
        "null_order",
        "object_order",
        "number_priority",
        "foreign_priority",
        "duplicate_priority",
        "too_many_priorities",
        "missing_state",
        "unknown_state",
        "null_state",
        "completed_partial_order",
        "completed_no_problems",
    ],
)
def test_application_sql_rejects_malformed_diagnosis_problem_order(live, fault):
    row = save(live)
    original = get(live, row)
    data = deepcopy(payload(live, row))
    problems, order = data["problems"], data["priority_order"]
    if fault == "missing_problems":
        del data["problems"]
    elif fault == "null_problems":
        data["problems"] = None
    elif fault == "object_problems":
        data["problems"] = {}
    elif fault == "scalar_problem":
        problems[0] = "invalid"
    elif fault == "missing_id":
        del problems[0]["problem_id"]
    elif fault == "null_id":
        problems[0]["problem_id"] = None
    elif fault == "number_id":
        problems[0]["problem_id"] = 1
    elif fault == "invalid_id":
        problems[0]["problem_id"] = "not-a-uuid"
    elif fault == "uppercase_id":
        problems[0]["problem_id"] = "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA"
    elif fault == "duplicate_id":
        problems[1]["problem_id"] = problems[0]["problem_id"]
    elif fault == "too_many_problems":
        data["problems"] = [{**problems[0], "problem_id": str(uuid4())} for _ in range(21)]
    elif fault == "missing_order":
        del data["priority_order"]
    elif fault == "null_order":
        data["priority_order"] = None
    elif fault == "object_order":
        data["priority_order"] = {}
    elif fault == "number_priority":
        order[0] = 1
    elif fault == "foreign_priority":
        order[0] = str(uuid4())
    elif fault == "duplicate_priority":
        order[1] = order[0]
    elif fault == "too_many_priorities":
        data["priority_order"] = [order[0]] * 21
    elif fault == "missing_state":
        del data["diagnosis_state"]
    elif fault == "unknown_state":
        data["diagnosis_state"] = "Approved"
    elif fault == "null_state":
        data["diagnosis_state"] = None
    elif fault == "completed_partial_order":
        data.update(diagnosis_state="Completed", priority_order=order[:1])
    elif fault == "completed_no_problems":
        data.update(diagnosis_state="Completed", problems=[], priority_order=[])
    with login("APP") as c:
        with pytest.raises(CheckViolation) as error:
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
                insert_copy(c, row, data)
        assert error.value.diag.constraint_name == "diagnosis_problem_order_valid"
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.object_revision WHERE object_id=%s", (row["object_id"],)
            ).fetchone()["n"]
            == 1
        )
    assert get(live, row) == original


def test_partial_drafts_completion_correction_and_exact_history_remain_valid(live):
    row = save(live)
    completed = action(live, row, "complete")
    correction = action(live, completed, "revise", body=action_body(completed, reason="Synthetic correction"))
    draft = deepcopy(payload(live, correction))
    for body in (
        {**draft, "problems": [], "priority_order": []},
        {**draft, "priority_order": []},
        {**draft, "priority_order": draft["priority_order"][:1]},
        {
            **draft,
            "problems": [{**draft["problems"][0], "problem_id": "00000000-0000-0000-0000-000000000000"}],
            "priority_order": ["00000000-0000-0000-0000-000000000000"],
        },
    ):
        with login("APP") as c:
            with pytest.raises(Rollback):
                with c.transaction():
                    c.execute("SET LOCAL ROLE impact_app")
                    c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
                    insert_copy(c, correction, body)
                    raise Rollback()
    assert get(live, correction)["business_state"] == "Draft"
    historical = live.request(
        live.path("ai-enablement/diagnoses", row["object_id"]) + "/revisions/" + completed["revision_id"],
        actor="admin",
    )
    assert historical.status_code == 200
    assert historical.json()["business_state"] == "Completed"


def test_removed_revision_storage_shape_and_constraint_validation(live):
    # Verify the pre-existing SQL NULL removal shape can satisfy the new CHECK.
    # This rolled-back storage probe is not privacy workflow or removal acceptance.
    row = save(live)
    with live.db() as c:
        meta = c.execute(
            "SELECT convalidated FROM pg_constraint WHERE conrelid='impact.object_revision'::regclass "
            "AND conname='diagnosis_problem_order_valid'"
        ).fetchone()
        assert meta and meta["convalidated"]
    with login("APP") as c:
        with pytest.raises(Rollback):
            with c.transaction():
                c.execute("SET LOCAL ROLE impact_app")
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
                insert_copy(c, row, None, restriction="REMOVED")
                raise Rollback()
    assert get(live, row)["business_state"] == "Draft"


def test_constraint_helper_has_no_definer_or_identity_data_authority(live):
    with live.db() as c:
        meta = c.execute(
            "SELECT prosecdef,provolatile,proconfig FROM pg_proc "
            "WHERE oid='impact.diagnosis_problem_order_valid(jsonb)'::regprocedure"
        ).fetchone()
        assert meta["prosecdef"] is False and meta["provolatile"] == "i"
        assert meta["proconfig"] == ["search_path=pg_catalog"]
        for role in ("impact_app", "impact_worker", "impact_platform", "impact_privacy"):
            assert c.execute(
                "SELECT has_function_privilege(%s,'impact.diagnosis_problem_order_valid(jsonb)','EXECUTE') AS ok",
                (role,),
            ).fetchone()["ok"]
        assert not c.execute(
            "SELECT has_function_privilege('impact_identity','impact.diagnosis_problem_order_valid(jsonb)','EXECUTE') AS ok"
        ).fetchone()["ok"]
