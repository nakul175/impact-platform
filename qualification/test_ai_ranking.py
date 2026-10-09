"""US-MP-03 rank opportunities with the organisation's weights, on the real API and database
(PGlite or native).

Every acceptance scenario of docs/sprints/SPRINT-01.md is exercised here. Weights are the tenant's
single AIRankingWeights object (migration 0042); tenant A's weights change from test to test, so
each test reads the revision in force first and never assumes another test's order. Tenant B never
has weights saved: its only fixture member (other_tenant, AUTHOR) reads AI enablement but cannot
manage it, so tenant B shows the defaults. The scoring maths is also checked database-free in
test_ai_ranking_unit.py.
"""

from contextlib import contextmanager
from decimal import Decimal
import json
import time
from uuid import uuid4

import psycopg
import pytest
from starlette.requests import Request

from impact_api import ai_opportunity_scores as editorial
from impact_api.ai_ranking import AIRanking
from impact_api.auth import Auth
from impact_api.config import Settings
from impact_api.service import Service
from impact_api.store import Database
from test_live_application import expect

WEIGHTS = "ai-enablement/ranking-weights"
RANKING = "ai-enablement/ranking"
DEFAULT = {"impact": 25, "effort": 25, "cost": 25, "readiness": 25}
IMPACT_FIRST = {"impact": 70, "effort": 10, "cost": 10, "readiness": 10}
PROFILE = {
    "sector": "GENERAL",
    "team_size": 8,
    "goal": "Improve impact reporting",
    "data_readiness": "STRUCTURED",
    "ai_experience": "EXPERIMENTING",
    "sensitive_data": False,
}
# Hand-computed from the editorial scores (ai_opportunity_scores.py) and the documented rule.
DEFAULT_ORDER = [
    ("communications", "87.50"),
    ("data_foundation", "81.25"),
    ("mel_narratives", "75.00"),
    ("knowledge_search", "56.25"),
]
IMPACT_FIRST_ORDER = [
    ("data_foundation", "77.50"),
    ("mel_narratives", "75.00"),
    ("communications", "65.00"),
    ("knowledge_search", "52.50"),
]


def tenant_b(live):
    return live.fixture["tenant_b"]


def read_weights(live, actor="admin", tenant=None):
    return expect(live.request(live.path(WEIGHTS, tenant=tenant), actor=actor), 200)


def command(live, data, expected="current", operation=None):
    if expected == "current":
        expected = read_weights(live)["revision_id"]
    return {"operation_id": operation or str(uuid4()), "expected_revision": expected, "data": data}


def put(live, body, actor="admin", tenant=None, token=None):
    if token:
        return live.request(
            live.path(WEIGHTS, tenant=tenant),
            actor=None,
            method="PUT",
            body=body,
            headers={"Authorization": "Bearer " + token},
        )
    return live.request(live.path(WEIGHTS, tenant=tenant), actor=actor, method="PUT", body=body)


def save(live, data, actor="admin"):
    return expect(put(live, command(live, data), actor=actor), 200)


def ranking(live, actor="author", tenant=None, profile=None):
    return expect(
        live.request(
            live.path(RANKING, tenant=tenant),
            actor=actor,
            method="POST",
            body={"profile": profile or PROFILE},
        ),
        200,
    )


def order(result):
    return [(item["use_case_id"], item["weighted_total"]) for item in result["items"]]


def counts(live, tenant=None):
    tenant = tenant or live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))

        def n(sql):
            return c.execute(sql, (tenant,)).fetchone()["n"]

        return {
            "objects": n(
                "SELECT count(*) AS n FROM impact.object_registry WHERE tenant_id=%s "
                "AND object_type='AIRankingWeights'"
            ),
            "revisions": n(
                "SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s "
                "AND object_type='AIRankingWeights'"
            ),
            "audits": n(
                "SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s "
                "AND action_type='ai_ranking_weights.changed'"
            ),
            "receipts": n(
                "SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s "
                "AND command_type='update_ai_ranking_weights'"
            ),
            "registry": n("SELECT count(*) AS n FROM impact.object_registry WHERE tenant_id=%s"),
            "all_receipts": n("SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s"),
        }


@contextmanager
def without_grant(live, actor, capability):
    """The actor's grants of `capability` made inert (purpose-bound) for the block, then restored."""
    tenant = live.fixture["tenant_a"]
    principal = live.fixture["actors"][actor]["principal_id"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        rows = c.execute(
            "SELECT object_id FROM impact.grant_current WHERE tenant_id=%s AND subject_id=%s "
            "AND capability=%s AND purpose IS NULL",
            (tenant, principal, capability),
        ).fetchall()
        assert rows
        c.execute(
            "UPDATE impact.grant_current SET purpose='SYNTHETIC_RANKING_DISABLED' "
            "WHERE tenant_id=%s AND object_id=ANY(%s::uuid[])",
            (tenant, [row["object_id"] for row in rows]),
        )
    try:
        yield
    finally:
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            c.execute(
                "UPDATE impact.grant_current SET purpose=NULL WHERE tenant_id=%s AND object_id=ANY(%s::uuid[])",
                (tenant, [row["object_id"] for row in rows]),
            )


def in_process(live, table, actor="author"):
    """The real AIRanking on the run's database with a replaced editorial score table."""
    settings = Settings(**live.config)
    db = Database(settings)
    identity = Auth(settings, db).resolve(
        Request(
            {
                "type": "http",
                "method": "POST",
                "headers": [(b"authorization", ("Bearer " + live.token(actor)).encode())],
            }
        )
    )
    return AIRanking(Service(settings, db), table), identity


# Scenario: Ranked list with scores


def test_default_weights_rank_opportunities_by_descending_total_and_name_the_defaults(live):
    tenant = tenant_b(live)
    # Precondition: nobody in tenant B can manage AI enablement, so no weights were ever saved.
    assert counts(live, tenant)["objects"] == 0
    assert read_weights(live, actor="other_tenant", tenant=tenant) == {
        "source": "DEFAULT",
        "revision_id": None,
        "weights": DEFAULT,
        "saved_at": None,
        "saved_by": None,
    }
    result = ranking(live, actor="other_tenant", tenant=tenant)
    assert order(result) == DEFAULT_ORDER
    totals = [item["weighted_total"] for item in result["items"]]
    assert [Decimal(t) for t in totals] == sorted((Decimal(t) for t in totals), reverse=True)
    assert [item["rank"] for item in result["items"]] == [1, 2, 3, 4]
    for item in result["items"]:
        assert set(item["scores"]) == {"impact", "effort", "cost", "readiness"}
        assert item["scores"]["readiness"] == 5 and item["readiness_gaps"] == []
    assert result["weights"] == DEFAULT
    assert result["weights_source"] == "DEFAULT" and result["weights_revision_id"] is None
    assert result["unranked"] == []
    assert result["method"] == "WEIGHTED_EDITORIAL_SCORES"
    assert result["score_version"] == editorial.SCORE_VERSION
    assert result["score_status"] == "EDITORIAL_DRAFT_PENDING_ADVISOR_REVIEW"


def test_saved_weights_are_an_audited_revision_and_every_ranking_names_it(live):
    tenant = live.fixture["tenant_a"]
    before = counts(live)
    previous = read_weights(live)["revision_id"]
    body = command(live, DEFAULT)
    receipt = expect(put(live, body), 200)
    assert set(receipt) == {
        "object_id",
        "revision_id",
        "business_state",
        "saved_at",
        "operation_id",
        "correlation_id",
    }
    assert receipt["business_state"] == "Active" and receipt["operation_id"] == body["operation_id"]
    assert receipt["revision_id"] != previous
    # A MEL Manager reads the weights in force and ranks with them.
    seen = read_weights(live, actor="reviewer")
    assert seen["source"] == "SAVED" and seen["revision_id"] == receipt["revision_id"]
    assert seen["weights"] == DEFAULT
    assert seen["saved_by"] == live.fixture["actors"]["admin"]["principal_id"]
    result = ranking(live, actor="reviewer")
    assert order(result) == DEFAULT_ORDER
    assert result["weights_source"] == "SAVED" and result["weights_revision_id"] == receipt["revision_id"]
    after = counts(live)
    assert after["objects"] == 1
    assert after["revisions"] == before["revisions"] + 1
    assert after["audits"] == before["audits"] + 1 and after["receipts"] == before["receipts"] + 1
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        head = c.execute(
            "SELECT r.object_type,r.lifecycle_state,r.classification,v.payload,v.author_id "
            "FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id "
            "AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_id=%s",
            (tenant, receipt["object_id"]),
        ).fetchone()
        assert (head["object_type"], head["lifecycle_state"], head["classification"]) == (
            "AIRankingWeights",
            "Active",
            "INTERNAL",
        )
        assert head["payload"] == DEFAULT
        assert str(head["author_id"]) == live.fixture["actors"]["admin"]["principal_id"]
        assert c.execute(
            "SELECT 1 FROM impact.audit_event_current WHERE tenant_id=%s AND action_type='ai_ranking_weights.changed' "
            "AND object_reference=%s AND real_actor_id=%s",
            (tenant, receipt["object_id"], live.fixture["actors"]["admin"]["principal_id"]),
        ).fetchone()
        assert c.execute(
            "SELECT 1 FROM impact.outbox_event WHERE tenant_id=%s AND payload->>'aggregate_revision'=%s "
            "AND payload->>'aggregate_type'='AIRankingWeights'",
            (tenant, receipt["revision_id"]),
        ).fetchone()
        assert c.execute(
            "SELECT 1 FROM impact.operation_receipt WHERE tenant_id=%s AND command_type='update_ai_ranking_weights' "
            "AND operation_id=%s",
            (tenant, body["operation_id"]),
        ).fetchone()


# Scenario: Changing weights reorders the ranking


def test_changing_weights_reorders_the_ranking_and_cites_the_new_revision(live):
    first = save(live, DEFAULT)
    assert order(ranking(live)) == DEFAULT_ORDER
    second = save(live, IMPACT_FIRST, actor="author")  # a Programme Manager also holds manage
    assert second["object_id"] == first["object_id"] and second["revision_id"] != first["revision_id"]
    result = ranking(live)
    assert order(result) == IMPACT_FIRST_ORDER
    assert result["weights"] == IMPACT_FIRST
    assert result["weights_revision_id"] == second["revision_id"]
    # The earlier revision is kept unchanged (revisions are insert-only).
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        kept = c.execute(
            "SELECT payload FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
            (live.fixture["tenant_a"], first["revision_id"]),
        ).fetchone()
        assert kept["payload"] == DEFAULT


# Scenario: Reject weights that do not total 100


def test_weights_not_totalling_100_are_refused_and_the_previous_weights_stay_in_force(live):
    kept = save(live, IMPACT_FIRST)
    before = counts(live)
    refusal = expect(put(live, command(live, {"impact": 50, "effort": 30, "cost": 30, "readiness": 10})), 422)
    assert (refusal["code"], refusal["reason_code"]) == ("VALIDATION_FAILED", "AI_RANKING_WEIGHTS_TOTAL")
    assert "add up to 120" in refusal["message"]
    in_force = read_weights(live)
    assert in_force["revision_id"] == kept["revision_id"] and in_force["weights"] == IMPACT_FIRST
    result = ranking(live)
    assert result["weights_revision_id"] == kept["revision_id"] and order(result) == IMPACT_FIRST_ORDER
    # Every other malformed command is refused the same way, before anything is written.
    for data in [
        {**DEFAULT, "impact": 25.0},
        {**DEFAULT, "impact": True},
        {**DEFAULT, "impact": "25"},
        {"impact": 125, "effort": -25, "cost": 0, "readiness": 0},
        {"impact": 101, "effort": 0, "cost": 0, "readiness": -1},
        {"impact": 50, "effort": 25, "cost": 25},
        {**DEFAULT, "approved": True},
    ]:
        expect(put(live, command(live, data)), 422)
    for body in [
        {**command(live, DEFAULT), "saved_by": live.fixture["actors"]["admin"]["principal_id"]},
        {**command(live, DEFAULT), "expected_revision": "not-a-revision"},
        {"operation_id": str(uuid4()), "data": DEFAULT},
    ]:
        expect(put(live, body), 422)
    duplicate = live.request(
        live.path(WEIGHTS),
        actor="admin",
        method="PUT",
        content=b'{"operation_id":"' + str(uuid4()).encode() + b'","operation_id":"x"}',
        headers={"Content-Type": "application/json"},
    )
    expect(duplicate, 400)
    assert counts(live) == before
    assert read_weights(live)["revision_id"] == kept["revision_id"]


# Scenario: Reject a stale weights update


def test_second_of_two_editors_from_the_same_revision_is_refused_without_overwriting(live):
    save(live, DEFAULT)
    opened_by_admin = read_weights(live, actor="admin")
    opened_by_mel = read_weights(live, actor="reviewer")
    assert opened_by_admin["revision_id"] == opened_by_mel["revision_id"]
    first = expect(
        put(live, command(live, IMPACT_FIRST, expected=opened_by_admin["revision_id"]), actor="admin"),
        200,
    )
    before = counts(live)
    late = {"impact": 10, "effort": 40, "cost": 40, "readiness": 10}
    stale = expect(
        put(live, command(live, late, expected=opened_by_mel["revision_id"]), actor="reviewer"),
        409,
    )
    assert (stale["code"], stale["reason_code"]) == ("CONFLICT_VERSION", "AI_RANKING_WEIGHTS_CHANGED")
    in_force = read_weights(live)
    assert in_force["revision_id"] == first["revision_id"] and in_force["weights"] == IMPACT_FIRST
    # A first-save claim (null) or an unknown revision is just as stale while weights exist.
    for expected in (None, str(uuid4())):
        refused = expect(put(live, command(live, late, expected=expected), actor="reviewer"), 409)
        assert refused["reason_code"] == "AI_RANKING_WEIGHTS_CHANGED"
    assert counts(live) == before
    assert ranking(live)["weights_revision_id"] == first["revision_id"]


# Scenario: Reject ranking an opportunity without all four scores


def test_opportunity_missing_its_cost_score_appears_only_under_not_ranked(live):
    save(live, DEFAULT)
    table = editorial.scores()
    del table["communications"]["cost"]
    service, identity = in_process(live, table)
    result = service.rank(identity, live.fixture["tenant_a"], PROFILE)
    assert result["unranked"] == [{"use_case_id": "communications", "missing_scores": ["cost"]}]
    assert "communications" not in [item["use_case_id"] for item in result["items"]]
    assert order(result) == [pair for pair in DEFAULT_ORDER if pair[0] != "communications"]
    assert [item["rank"] for item in result["items"]] == [1, 2, 3]
    assert result["weights_revision_id"] == read_weights(live)["revision_id"]
    # The shipped editorial table scores every use case, so nothing is unranked over HTTP.
    assert ranking(live)["unranked"] == []


# Capabilities, tenancy and retries


def test_reads_need_ai_enablement_read_and_are_tenant_fenced(live):
    for actor in ("other_tenant", "revoked", "partner", "enumerator", "owner", "privacy"):
        expect(live.request(live.path(WEIGHTS), actor=actor), 404)
        response = live.request(live.path(RANKING), actor=actor, method="POST", body={"profile": PROFILE})
        expect(response, 404)
    # Client-supplied tenant IDs are selectors only: a tenant A member never reads tenant B.
    expect(live.request(live.path(WEIGHTS, tenant=tenant_b(live)), actor="author"), 404)
    for actor in ("admin", "reviewer", "author"):
        read_weights(live, actor=actor)
        ranking(live, actor=actor)


def test_changing_weights_needs_ai_enablement_manage(live):
    before = counts(live)
    body = command(live, DEFAULT)
    for actor in ("other_tenant", "revoked", "partner", "enumerator", "owner"):
        expect(put(live, {**body, "operation_id": str(uuid4())}, actor=actor), 404)
    # A reader without manage: tenant B's only member (AUTHOR) and a Programme Manager whose manage
    # grant is inert.
    refusal = expect(
        put(live, command(live, DEFAULT, expected=None), actor="other_tenant", tenant=tenant_b(live)), 403
    )
    assert refusal["code"] == "POLICY_DENIED"
    assert counts(live, tenant_b(live))["objects"] == 0
    with without_grant(live, "author", "ai.enablement.manage"):
        ranking(live, actor="author")  # reading is unaffected
        assert expect(put(live, {**body, "operation_id": str(uuid4())}, actor="author"), 403)["code"] == (
            "POLICY_DENIED"
        )
    assert counts(live) == before
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_b(live),))
        assert c.execute(
            "SELECT 1 FROM impact.access_denial WHERE tenant_id=%s AND principal_id=%s "
            "AND operation_id='update_ai_ranking_weights'",
            (tenant_b(live), live.fixture["actors"]["other_tenant"]["principal_id"]),
        ).fetchone()


def test_weights_are_a_preference_not_an_approval(live):
    # No independent review and no fresh sign-in: the same person saves twice in a row, the second
    # time with a sign-in 400 seconds old.
    first = save(live, DEFAULT)
    admin = live.fixture["actors"]["admin"]["identity_id"]
    body = command(live, IMPACT_FIRST, expected=first["revision_id"])
    second = expect(put(live, body, token=live.signed(admin, auth_time=time.time() - 400)), 200)
    assert read_weights(live)["revision_id"] == second["revision_id"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        assert (
            c.execute(
                "SELECT lifecycle_state FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
                (live.fixture["tenant_a"], second["object_id"]),
            ).fetchone()["lifecycle_state"]
            == "Active"
        )
        # No review workflow is opened for the weights.
        assert not c.execute(
            "SELECT 1 FROM impact.workflow_current WHERE tenant_id=%s AND candidate_id=%s",
            (live.fixture["tenant_a"], second["object_id"]),
        ).fetchone()


def test_exact_retry_returns_the_receipt_and_a_changed_payload_conflicts(live):
    body = command(live, {"impact": 40, "effort": 20, "cost": 20, "readiness": 20})
    before = counts(live)
    first = expect(put(live, body), 200)
    assert expect(put(live, body), 200) == first
    assert counts(live)["revisions"] == before["revisions"] + 1
    changed = json.loads(json.dumps(body))
    changed["data"]["impact"], changed["data"]["readiness"] = 20, 40
    assert expect(put(live, changed), 409)["code"] == "CONFLICT_OPERATION"
    assert counts(live)["revisions"] == before["revisions"] + 1


def test_ranking_is_a_read_and_leaves_the_assessment_order_unchanged(live):
    assessment_path = live.path("ai-enablement/assessment")
    original = expect(
        live.request(assessment_path, actor="author", method="POST", body={"profile": PROFILE}), 200
    )
    save(live, IMPACT_FIRST)
    before = counts(live)
    ranking(live)
    ranking(live, actor="reviewer")
    assert counts(live) == before  # nothing is written by a ranking
    after = expect(
        live.request(assessment_path, actor="author", method="POST", body={"profile": PROFILE}), 200
    )
    assert after == original
    assert [item["use_case_id"] for item in after["assessment"]["recommendations"]] == [
        "mel_narratives",
        "communications",
        "data_foundation",
        "knowledge_search",
    ]
    for body in [
        {"profile": {**PROFILE, "sector": "OTHER"}},
        {"profile": {**PROFILE, "extra": 1}},
        {"profile": PROFILE, "weights": DEFAULT},
        {},
    ]:
        expect(live.request(live.path(RANKING), actor="author", method="POST", body=body), 422)


# Database guarantees (migration 0042)


def refused_statement(live, error, statement, values):
    with live.db() as c:
        with pytest.raises(error):
            with c.transaction():
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
                c.execute(statement, values)


def test_one_weights_object_per_tenant_and_the_kind_check_keeps_every_earlier_kind(live):
    save(live, DEFAULT)
    tenant = live.fixture["tenant_a"]
    insert = (
        "INSERT INTO impact.object_registry(tenant_id,object_id,object_type,head_revision,lifecycle_state,"
        "classification,owner_id,created_at,created_by,updated_at) "
        "VALUES(%s,%s,%s,%s,'Active','INTERNAL',NULL,now(),%s,now())"
    )
    admin = live.fixture["actors"]["admin"]["principal_id"]
    refused_statement(
        live,
        psycopg.errors.UniqueViolation,
        insert,
        (tenant, str(uuid4()), "AIRankingWeights", str(uuid4()), admin),
    )
    refused_statement(
        live,
        psycopg.errors.CheckViolation,
        insert,
        (tenant, str(uuid4()), "AIRankingWeightsDraft", str(uuid4()), admin),
    )
    with live.db() as c:
        definition = c.execute(
            "SELECT pg_get_constraintdef(oid) AS d FROM pg_constraint "
            "WHERE conrelid='impact.object_registry'::regclass AND conname='object_registry_object_type_check'"
        ).fetchone()["d"]
    for kind in (
        "AIConfiguration",
        "AIAdvisoryRequest",
        "AIAdoptionPlan",
        "HumanAdviceCase",
        "AIRankingWeights",
    ):
        assert "'" + kind + "'" in definition, kind
