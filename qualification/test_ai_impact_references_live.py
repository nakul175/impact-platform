"""AI-plan links qualified against real governed measurement and period-close flows.

Prepared separately from route registration. All facts are synthetic. Native contention tests
are explicitly skipped in serialized PGlite and do not qualify hosted operation or causality.
"""

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from uuid import uuid4

import pytest
from starlette.requests import Request

import impact_api.ai_impact_references as module
from impact_api.ai_impact_references import AIImpactReferences
from impact_api.contracts import validate
from impact_api.auth import Auth
from impact_api.config import Settings
from impact_api.domain import DomainError
from test_ai_adoption_plans import plan
from test_ai_adoption_plans_live import management_disabled, save
from test_ai_content_archives_live import (
    counts,
    legacy_revision,
    local_engine as archive_engine,
    path as guidance_path,
)
from test_dashboards import calculate, card, close, measure, ratio_source, target
from test_live_application import cmd, expect
from test_measurement import action, approve, create, get, submit


def local_engine(live):
    plans, db, _ = archive_engine(live)
    # Tenant administrators manage AI drafts but do not implicitly read programme evidence.
    # Use the existing authorised ProgrammeManager for this internal atomic fixture.
    identity = Auth(Settings(**live.config), db).resolve(
        Request(
            {
                "type": "http",
                "method": "POST",
                "headers": [(b"authorization", ("Bearer " + live.token("author")).encode())],
            }
        )
    )
    return plans, db, identity


def path(live, receipt, result=False):
    base = live.path("ai-enablement/plans", receipt["object_id"]) + "/impact-reference"
    return base + "/result" if result else base


def inputs(programme, indicator, period):
    return {
        "programme_id": programme["object_id"],
        "indicator_id": indicator["object_id"],
        "period_id": period["object_id"],
        "interpretation_note": "Synthetic programme evidence for review; no causal attribution to AI.",
    }


def link(live, receipt, data, actor="author"):
    return expect(
        live.request(path(live, receipt), actor=actor, method="PUT", body=cmd(data, receipt["revision_id"])),
        200,
    )


def result(live, receipt, actor="author"):
    answer = expect(live.request(path(live, receipt, True), actor=actor), 200)
    validate("AIImpactReferenceResult", answer)
    return answer


def core_state(live):
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        return {
            "heads": c.execute(
                "SELECT r.object_id,r.object_type,r.head_revision,r.classification,v.restriction_state,"
                "v.payload_sha256,md5(v.payload::text) AS actual_payload_digest "
                "FROM impact.object_registry r JOIN impact.object_revision v "
                "ON v.tenant_id=r.tenant_id AND v.object_id=r.object_id AND v.revision_id=r.head_revision "
                "WHERE r.tenant_id=%s AND r.object_type NOT IN ('AIAdoptionPlan','AuditEvent') ORDER BY r.object_id",
                (tenant,),
            ).fetchall(),
            "snapshots": c.execute(
                "SELECT snapshot_id,snapshot_revision,snapshot_version FROM impact.period_snapshot_binding WHERE tenant_id=%s ORDER BY snapshot_id",
                (tenant,),
            ).fetchall(),
            "official": c.execute(
                "SELECT snapshot_id,indicator_id,result_revision FROM impact.official_result_snapshot WHERE tenant_id=%s ORDER BY snapshot_id,indicator_id",
                (tenant,),
            ).fetchall(),
        }


@contextmanager
def disabled(live, actor, capability):
    tenant, principal = live.fixture["tenant_a"], live.fixture["actors"][actor]["principal_id"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        grants = c.execute(
            "SELECT object_id,purpose FROM impact.grant_current WHERE tenant_id=%s AND subject_id=%s AND capability=%s AND purpose IS NULL",
            (tenant, principal, capability),
        ).fetchall()
        assert grants, "Synthetic actor must actually hold the capability being revoked"
        c.execute(
            "UPDATE impact.grant_current SET purpose='QUALIFICATION' WHERE tenant_id=%s AND object_id=ANY(%s::uuid[])",
            (tenant, [str(row["object_id"]) for row in grants]),
        )
    try:
        yield
    finally:
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            for row in grants:
                c.execute(
                    "UPDATE impact.grant_current SET purpose=%s WHERE tenant_id=%s AND object_id=%s",
                    (row["purpose"], tenant, row["object_id"]),
                )


@contextmanager
def scoped_programme(live, actor, programme_id, capability="programmes.read"):
    tenant, principal, scope = (
        live.fixture["tenant_a"],
        live.fixture["actors"][actor]["principal_id"],
        str(uuid4()),
    )
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        grants = c.execute(
            "SELECT object_id,scope_id FROM impact.grant_current WHERE tenant_id=%s AND subject_id=%s AND capability=%s AND purpose IS NULL",
            (tenant, principal, capability),
        ).fetchall()
        assert grants
        version = c.execute(
            "SELECT predicate_version FROM impact.scope_definition WHERE tenant_id=%s AND scope_id=%s",
            (tenant, grants[0]["scope_id"]),
        ).fetchone()["predicate_version"]
        c.execute(
            "INSERT INTO impact.scope_definition(tenant_id,scope_id,scope_type,predicate_version) VALUES(%s,%s,'OBJECT_SET',%s)",
            (tenant, scope, version),
        )
        c.execute("INSERT INTO impact.scope_member VALUES(%s,%s,%s)", (tenant, scope, programme_id))
        for grant in grants:
            c.execute(
                "UPDATE impact.grant_current SET scope_id=%s WHERE tenant_id=%s AND object_id=%s",
                (scope, tenant, grant["object_id"]),
            )
    try:
        yield
    finally:
        with live.db() as c:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            for grant in grants:
                c.execute(
                    "UPDATE impact.grant_current SET scope_id=%s WHERE tenant_id=%s AND object_id=%s",
                    (grant["scope_id"], tenant, grant["object_id"]),
                )


@pytest.fixture(scope="module")
def governed(live):
    programme, indicator, period, keys = measure(live, keys=2)
    ratio_source(live, indicator, keys[0], "50", "100")
    ratio_source(live, indicator, keys[1], "1", "10")
    calculate(live, indicator, period)
    target(live, indicator, period, "50")
    close(live, programme, period)
    return programme, indicator, period, inputs(programme, indicator, period)


def test_reference_pins_actual_official_snapshot_and_cannot_change_core_results(live, governed):
    programme, indicator, period, data = governed
    first = save(live)
    before = core_state(live)
    before_events = counts(live)
    linked = link(live, first, data)
    answer = result(live, first)
    dashboard, core = card(live, programme, indicator, period, actor="author")
    assert answer["status"] == "LINKED"
    assert answer["revision_id"] == linked["revision_id"]
    assert answer["reference"]["snapshot_id"] == dashboard["snapshot"]["snapshot_id"]
    assert answer["reference"]["snapshot_revision"]
    assert answer["indicator"]["official"] == core["official"]
    assert answer["indicator"]["official"]["value"] == "46.363636363636"
    assert answer["indicator"]["official"]["displayed_value"] == "46.36"
    assert answer["indicator"]["provisional"] is None
    assert answer["indicator"]["target"]["displayed_value"] == "50.00"
    assert answer["indicator"]["coverage"]["approved_count"] == 2
    assert core_state(live) == before
    after_events = counts(live)
    assert after_events["audit_event_current"] == before_events["audit_event_current"] + 1
    assert after_events["outbox_event"] == before_events["outbox_event"] + 1
    assert after_events["operation_receipt"] == before_events["operation_receipt"] + 1
    assert "do not establish that AI caused" in answer["disclaimer"]


def test_ai_admin_draft_management_does_not_imply_programme_evidence_authority(live, governed):
    unlinked, linked = save(live), save(live)
    before = counts(live)
    expect(
        live.request(
            path(live, linked), actor="admin", method="PUT", body=cmd(governed[3], linked["revision_id"])
        ),
        404,
    )
    assert counts(live) == before
    link(live, linked, governed[3], "author")
    errors = []
    for receipt in (unlinked, linked):
        current = expect(
            live.request(live.path("ai-enablement/plans", receipt["object_id"]), actor="admin"), 200
        )
        assert "impact_reference" not in current["data"]
        error = expect(live.request(path(live, receipt, True), actor="admin"), 404)
        errors.append({name: error.get(name) for name in ("code", "message", "reason_code")})
    assert errors[0] == errors[1]


def test_retries_write_one_relationship_revision_receipt_audit_outbox_and_archive_binding(live, governed):
    first = save(live)
    original = expect(live.request(guidance_path(live, first), actor="author"), 200)
    command = cmd(governed[3], first["revision_id"])
    linked = expect(live.request(path(live, first), actor="author", method="PUT", body=command), 200)
    before = counts(live)
    assert expect(live.request(path(live, first), actor="author", method="PUT", body=command), 200) == linked
    assert counts(live) == before
    inherited = expect(live.request(guidance_path(live, linked), actor="author"), 200)
    assert inherited["snapshot_sha256"] == original["snapshot_sha256"]
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s",
                (tenant, first["object_id"]),
            ).fetchone()["n"]
            == 2
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.ai_plan_content_binding WHERE tenant_id=%s AND object_id=%s",
                (tenant, first["object_id"]),
            ).fetchone()["n"]
            == 2
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s AND object_reference=%s AND action_type=%s",
                (tenant, first["object_id"], module.SAVE_OPERATION),
            ).fetchone()["n"]
            == 1
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.outbox_event WHERE tenant_id=%s AND payload->>'aggregate_id'=%s",
                (tenant, first["object_id"]),
            ).fetchone()["n"]
            == 2
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, module.SAVE_OPERATION, command["operation_id"]),
            ).fetchone()["n"]
            == 1
        )
    assert set(linked) == {
        "operation_id",
        "object_id",
        "revision_id",
        "business_state",
        "saved_at",
        "correlation_id",
    }


@pytest.mark.parametrize(
    "capability", [cap for _, _, cap in module.CORE_PINS] + ["snapshots.read", "dashboards.read"]
)
def test_current_core_read_revocation_hides_dedicated_evidence_and_generic_drafts_leak_no_pins(
    live, governed, capability
):
    first = save(live)
    link(live, first, governed[3])
    with disabled(live, "reviewer", capability):
        expect(live.request(path(live, first, True), actor="reviewer"), 404)
        draft = expect(
            live.request(live.path("ai-enablement/plans", first["object_id"]), actor="reviewer"), 200
        )
        validate("AIAdoptionPlan", draft)
        assert "impact_reference" not in draft["data"]
        assert governed[0]["object_id"] not in str(draft)
        listing = expect(live.request(live.path("ai-enablement/plans"), actor="reviewer"), 200)
        validate("AIAdoptionPlanList", listing)
        assert all("impact_reference" not in row["data"] for row in listing["items"])


def test_read_only_plan_actor_can_read_evidence_but_cannot_refresh_it(live, governed):
    first = save(live)
    linked = link(live, first, governed[3])
    with management_disabled(live, "reviewer"):
        assert result(live, first, "reviewer")["status"] == "LINKED"
        expect(
            live.request(
                path(live, first),
                actor="reviewer",
                method="PUT",
                body=cmd(governed[3], linked["revision_id"]),
            ),
            404,
        )


def test_ai_only_actor_cannot_probe_reference_presence_on_linked_or_unlinked_plan(live, governed):
    unlinked, linked = save(live), save(live)
    link(live, linked, governed[3])
    with disabled(live, "reviewer", "dashboards.read"):
        for receipt in (unlinked, linked):
            error = expect(live.request(path(live, receipt, True), actor="reviewer"), 404)
            assert error["code"] == "RESOURCE_UNAVAILABLE"
            draft = expect(
                live.request(live.path("ai-enablement/plans", receipt["object_id"]), actor="reviewer"), 200
            )
            assert "impact_reference" not in draft["data"]
        listing = expect(live.request(live.path("ai-enablement/plans"), actor="reviewer"), 200)
        assert all("impact_reference" not in row["data"] for row in listing["items"])


@pytest.mark.parametrize("capability", ["programmes.read", "dashboards.read"])
def test_same_tenant_core_object_scope_does_not_follow_ai_plan_scope(live, governed, capability):
    first = save(live)
    link(live, first, governed[3])
    with scoped_programme(live, "reviewer", live.fixture["programme_a"], capability):
        expect(live.request(live.path("ai-enablement/plans", first["object_id"]), actor="reviewer"), 200)
        expect(live.request(path(live, first, True), actor="reviewer"), 404)


def test_unrelated_dashboard_scope_sees_identical_absent_hidden_and_corrupt_reference_errors(live, governed):
    unlinked, linked = save(live), save(live)
    link(live, linked, governed[3])
    corrupt = save(live)
    plans, db, identity = local_engine(live)
    tenant, correlation = live.fixture["tenant_a"], str(uuid4())
    # Append synthetic malformed server metadata through the governed store. Never alter
    # an immutable prior revision, disable its guards, or expose such a client command.
    with db.transaction(tenant) as c:
        c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
        ctx = module.context(c, identity, tenant, write=True)
        module.authorize(c, ctx, module.SAVE_OPERATION, corrupt["object_id"], hidden=True)
        previous = module.load(c, ctx, corrupt["object_id"], module.KIND, module.READ_CAP, lock=True)
        payload = {**deepcopy(previous["payload"]), "impact_reference": {}}
        receipt = module.write(c, ctx, module.KIND, payload, "Draft", previous=previous)
        module._inherit_guidance(c, ctx, previous, receipt)
        module.audit(c, ctx, module.SAVE_OPERATION, receipt, correlation)
    with scoped_programme(live, "reviewer", live.fixture["programme_a"], "dashboards.read"):
        errors = []
        for receipt in (unlinked, linked, corrupt):
            error = expect(live.request(path(live, receipt, True), actor="reviewer"), 404)
            errors.append({key: error.get(key) for key in ("code", "message", "reason_code", "fields")})
            draft = expect(
                live.request(live.path("ai-enablement/plans", receipt["object_id"]), actor="reviewer"), 200
            )
            assert "impact_reference" not in draft["data"]
        assert errors[0] == errors[1] == errors[2]


def test_official_value_visibility_and_source_freshness_follow_current_core_permissions(live, governed):
    first = save(live)
    link(live, first, governed[3])
    with disabled(live, "reviewer", "calculated-results.read"):
        answer = result(live, first, "reviewer")
        assert answer["indicator"]["official"] is answer["indicator"]["provisional"] is None
    with disabled(live, "reviewer", "observations.read"):
        answer = result(live, first, "reviewer")
        assert answer["indicator"]["official"]["value"] == "46.363636363636"
        assert answer["indicator"]["freshness"]["source_check"] == "NOT_PERMITTED"
        assert answer["indicator"]["freshness"]["stale"] is None


def test_generic_plan_edit_retains_private_reference_without_repointing_and_canonicalizes_lesson_alias(
    live, governed
):
    first = save(live)
    linked = link(live, first, governed[3])
    original = result(live, first)["reference"]
    data = {**plan(), "title": "Synthetic revised draft title", "learning_completed": ["foundations:0"]}
    edited = expect(
        live.request(
            live.path("ai-enablement/plans", first["object_id"]),
            actor="author",
            method="PUT",
            body=cmd(data, linked["revision_id"]),
        ),
        200,
    )
    answer = result(live, first)
    assert answer["revision_id"] == edited["revision_id"] and answer["reference"] == original
    draft = expect(live.request(live.path("ai-enablement/plans", first["object_id"]), actor="author"), 200)
    assert draft["data"]["learning_completed"] == ["foundations:safe-practice-task"]
    assert "impact_reference" not in draft["data"]
    forged = {**data, "impact_reference": original}
    expect(
        live.request(
            live.path("ai-enablement/plans", first["object_id"]),
            actor="author",
            method="PUT",
            body=cmd(forged, edited["revision_id"]),
        ),
        422,
    )


def test_clear_is_deliberate_revision_after_core_access_revocation_and_receipt_replay_stays_label_free(
    live, governed
):
    first = save(live)
    command = cmd(governed[3], first["revision_id"])
    linked = expect(live.request(path(live, first), actor="author", method="PUT", body=command), 200)
    with disabled(live, "author", "programmes.read"):
        assert (
            expect(live.request(path(live, first), actor="author", method="PUT", body=command), 200) == linked
        )
        cleared = link(live, linked, None)
        expect(live.request(path(live, first, True), actor="author"), 404)
        assert cleared["revision_id"] != linked["revision_id"]


def test_legacy_plan_relationship_edit_does_not_invent_guidance_archive(live, governed):
    legacy, saved = legacy_revision(live)
    linked = link(live, legacy, governed[3])
    guide = expect(live.request(guidance_path(live, linked), actor="author"), 200)
    assert guide["status"] == "UNAVAILABLE" and guide["snapshot_sha256"] is None
    draft = expect(live.request(live.path("ai-enablement/plans", legacy["object_id"]), actor="author"), 200)
    assert draft["data"]["content_versions"] == saved["content_versions"]


def test_atomic_failure_after_inherited_binding_restores_plan_head_events_receipt_and_binding(
    live, governed, monkeypatch
):
    first = save(live)
    plans, db, identity = local_engine(live)
    api = AIImpactReferences(plans.service)
    command = cmd(governed[3], first["revision_id"])
    before = counts(live)
    original = module._inherit_guidance

    def fail(*args):
        original(*args)
        raise DomainError("RESOURCE_UNAVAILABLE", 503, reason="SYNTHETIC_AFTER_BINDING_FAILURE")

    monkeypatch.setattr(module, "_inherit_guidance", fail)
    with pytest.raises(DomainError) as denied:
        api.save(identity, live.fixture["tenant_a"], first["object_id"], command, str(uuid4()))
    assert denied.value.reason == "SYNTHETIC_AFTER_BINDING_FAILURE"
    assert counts(live) == before
    draft = expect(live.request(live.path("ai-enablement/plans", first["object_id"]), actor="author"), 200)
    assert draft["revision_id"] == first["revision_id"]


def test_mismatched_programme_and_alien_tenant_are_refused_without_mutation(live, governed):
    first = save(live)
    data = {**governed[3], "programme_id": live.fixture["programme_a"]}
    before = counts(live)
    error = expect(
        live.request(path(live, first), actor="author", method="PUT", body=cmd(data, first["revision_id"])),
        422,
    )
    assert error["reason_code"] == "INDICATOR_NOT_IN_PROGRAMME"
    data["programme_id"] = live.fixture["programme_b"]
    expect(
        live.request(path(live, first), actor="author", method="PUT", body=cmd(data, first["revision_id"])),
        404,
    )
    assert counts(live) == before


def test_closed_link_command_cannot_submit_snapshot_pins_or_official_numbers(live, governed):
    first = save(live)
    for forged in (
        {**governed[3], "snapshot_revision": str(uuid4())},
        {**governed[3], "official_value": "100"},
        {**governed[3], "interpretation_note": "x" * 1001},
    ):
        expect(
            live.request(
                path(live, first), actor="author", method="PUT", body=cmd(forged, first["revision_id"])
            ),
            422,
        )


def test_dedicated_reads_are_domain_read_only_and_foreign_revoked_wrong_kind_ids_are_opaque(live, governed):
    first = save(live)
    link(live, first, governed[3])
    before = counts(live)
    assert result(live, first)["status"] == "LINKED"
    assert counts(live) == before
    for actor in ("other_tenant", "revoked", "partner"):
        expect(live.request(path(live, first, True), actor=actor), 404)
    wrong = {"object_id": governed[0]["object_id"]}
    expect(live.request(path(live, wrong, True), actor="author"), 404)
    missing = {"object_id": str(uuid4())}
    expect(live.request(path(live, missing, True), actor="author"), 404)


def test_stale_and_changed_operation_ids_cannot_refresh_a_pinned_snapshot(live, governed):
    first = save(live)
    command = cmd(governed[3], first["revision_id"])
    linked = expect(live.request(path(live, first), actor="author", method="PUT", body=command), 200)
    before = counts(live)
    expect(
        live.request(
            path(live, first), actor="author", method="PUT", body=cmd(governed[3], first["revision_id"])
        ),
        409,
    )
    changed = deepcopy(command)
    changed["data"]["interpretation_note"] = "Changed command using the same operation ID"
    error = expect(live.request(path(live, first), actor="author", method="PUT", body=changed), 409)
    assert error["code"] == "CONFLICT_OPERATION" and counts(live) == before
    assert result(live, first)["revision_id"] == linked["revision_id"]


def test_pinned_official_survives_restatement_and_provisional_changes_until_explicit_refresh(live):
    programme, indicator, period, keys = measure(live, keys=2)
    sources = [
        ratio_source(live, indicator, keys[0], "50", "100"),
        ratio_source(live, indicator, keys[1], "1", "10"),
    ]
    calculate(live, indicator, period)
    first = save(live)
    open_link = link(live, first, inputs(programme, indicator, period))
    assert result(live, first)["indicator"]["official"] is None
    close(live, programme, period)
    assert result(live, first)["indicator"]["official"] is None, (
        "An absent pin cannot silently become a later official snapshot"
    )
    linked = link(live, open_link, inputs(programme, indicator, period))
    pinned = result(live, first)
    template = get(live, "workflow-templates")["items"][0]
    restatement = action(
        live,
        "periods",
        get(live, "periods", period["object_id"]),
        "restate",
        {
            "workflow_version": template["revision_id"],
            "programme_id": programme["object_id"],
            "reason": "Synthetic verified transcription correction",
            "source_ids": [sources[0]["object_id"]],
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        },
    )
    approve(live, get(live, "workflows", restatement["object_id"]))
    proposal = create(
        live,
        "measurement-changes",
        {
            "target_kind": "Observation",
            "target_id": sources[0]["object_id"],
            "target_revision": sources[0]["revision_id"],
            "reason": "Synthetic correction through governed review",
            "proposed_data": {"numerator": "60", "source_version": "2"},
        },
    )
    approve(live, submit(live, "measurement-changes", proposal))
    calculate(live, indicator, period)
    changed = result(live, first)
    assert changed["reference"] == pinned["reference"]
    assert changed["indicator"]["official"]["displayed_value"] == "46.36"
    assert changed["indicator"]["provisional"]["displayed_value"] == "55.45"
    assert changed["indicator"]["freshness"]["stale"] is True
    close(live, programme, period)
    changed = result(live, first)
    assert changed["reference_status"]["snapshot"] == "CHANGED"
    assert changed["indicator"]["official"]["displayed_value"] == "46.36"
    refreshed = link(live, linked, inputs(programme, indicator, period))
    final = result(live, first)
    assert refreshed["revision_id"] != linked["revision_id"]
    assert final["reference"]["snapshot_id"] != pinned["reference"]["snapshot_id"]
    assert final["indicator"]["official"]["displayed_value"] == "55.45"


@pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Real competing transaction qualification requires native PostgreSQL",
)
def test_native_competing_exact_links_create_one_plan_revision_and_guidance_binding(live, governed):
    first = save(live)
    command = cmd(governed[3], first["revision_id"])
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(
            pool.map(
                lambda _: live.request(path(live, first), actor="author", method="PUT", body=command),
                range(2),
            )
        )
    receipts = [expect(response, 200) for response in responses]
    assert receipts[0] == receipts[1]
    tenant = live.fixture["tenant_a"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s",
                (tenant, first["object_id"]),
            ).fetchone()["n"]
            == 2
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.ai_plan_content_binding WHERE tenant_id=%s AND object_id=%s",
                (tenant, first["object_id"]),
            ).fetchone()["n"]
            == 2
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s AND command_type=%s AND operation_id=%s",
                (tenant, module.SAVE_OPERATION, command["operation_id"]),
            ).fetchone()["n"]
            == 1
        )
