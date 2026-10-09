"""FR-AI-001 explicit AI enablement and policy: database-free checks (part of `make unit`).

The real API and database qualification of every acceptance scenario is test_ai_policy.py (PGlite)
and the real-role checks are test_ai_policy_live.py (native PostgreSQL only).
"""

from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
from types import SimpleNamespace
from uuid import uuid4

import pytest

import impact_api.ai_policy as module
from impact_api import ai_enablement_contracts as contracts
from impact_api import store
from impact_api.access_bootstrap import PROFILE, PROFILE_HASH
from impact_api.ai_policy import AIPolicy, require, validate_policy
from impact_api.domain import DomainError

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "infrastructure/migrations/0041_ai_policy.sql"
TENANT = "ce56220a-32a5-5ca5-a45f-860dc3d9c958"


def rule(**changes):
    """The Gherkin example: ADVISORY_DRAFT for INTERNAL data, destination openai-us, purpose
    "planning advice", languages en, human review, budget 100 units, no tools."""
    return {
        "use_case": "ADVISORY_DRAFT",
        "enabled": True,
        "data_classes": ["INTERNAL"],
        "destinations": ["openai-us"],
        "purposes": ["planning advice"],
        "languages": ["en"],
        "review_mode": "HUMAN_REVIEW",
        "budget_units": 100,
        "tools": [],
        **changes,
    }


def policy(version=1, **rules):
    return {
        "version": version,
        "policy_version_id": str(uuid4()),
        "object_id": str(uuid4()),
        "created_at": None,
        "created_by": None,
        "use_cases": {"ADVISORY_DRAFT": rule(**rules)},
    }


def generated():
    spec = {"components": {"schemas": {"Error": {}}}, "paths": {}}
    access = {"operations": []}
    contracts.augment(spec, access)
    return spec, {row["operation_id"]: row for row in access["operations"]}


# Contract and policy rows


def test_policy_change_is_a_fresh_assurance_tenant_admin_capability_and_audited():
    spec, rows = generated()
    update = rows["update_ai_policy"]
    assert update["capability"] == "ai.policy.manage"
    assert update["role_templates"] == ["TENANT_ADMIN"]
    assert update["fresh_assurance_seconds"] == 300
    assert update["audit"] is True and update["method"] == "PUT"
    for read in ("get_ai_policy", "list_ai_policy_revisions"):
        assert rows[read]["capability"] == "ai.enablement.read"
        assert rows[read]["fresh_assurance_seconds"] is None and rows[read]["audit"] is False
    path = "/v1/tenants/{tenant_id}/ai-enablement/policy"
    assert set(spec["paths"][path]) == {"get", "put"}
    assert set(spec["paths"][path + "/revisions"]) == {"get"}


def test_policy_command_and_rules_are_closed_with_empty_tools():
    spec, _ = generated()
    schemas = spec["components"]["schemas"]
    command = schemas["AIPolicyCommand"]
    assert command["additionalProperties"] is False
    assert set(command["required"]) == {"operation_id", "expected_version", "data"}
    assert schemas["AIPolicyData"]["additionalProperties"] is False
    use_case = schemas["AIUseCasePolicy"]
    assert use_case["additionalProperties"] is False and set(use_case["required"]) == set(module.FIELDS)
    assert use_case["properties"]["tools"]["maxItems"] == 0
    assert use_case["properties"]["use_case"]["enum"] == [
        "ADVISORY_DRAFT",
        "EXTRACTION",
        "REPORT_DRAFT",
        "CHAT",
    ]
    assert use_case["properties"]["data_classes"]["items"]["enum"] == [
        "PUBLIC",
        "INTERNAL",
        "CONFIDENTIAL",
        "RESTRICTED",
    ]
    advisory = schemas["AIAdvisoryRequest"]
    assert advisory["additionalProperties"] is False
    assert "policy_version" in advisory["required"] and "tools" not in advisory["required"]


def test_generated_contracts_carry_the_policy_routes():
    access = json.loads((ROOT / "packages/contracts/access-policy.json").read_text())
    rows = {row["operation_id"]: row for row in access["operations"]}
    _, expected = generated()
    for operation in ("get_ai_policy", "update_ai_policy", "list_ai_policy_revisions"):
        assert rows[operation] == expected[operation]
    implemented = json.loads((ROOT / "packages/contracts/openapi-implemented.json").read_text())
    assert set(implemented["paths"]["/v1/tenants/{tenant_id}/ai-enablement/policy"]) >= {"get", "put"}
    assert "/v1/tenants/{tenant_id}/ai-enablement/policy/revisions" in implemented["paths"]


@pytest.mark.parametrize(
    "verified,age,reason",
    [(False, 0, "MFA_ASSURANCE_REQUIRED"), (True, 301, "FRESH_AUTHENTICATION_REQUIRED")],
)
def test_real_authorizer_requires_mfa_and_sign_in_within_300_seconds(monkeypatch, verified, age, reason):
    _, rows = generated()
    monkeypatch.setitem(store.OPERATIONS, "update_ai_policy", rows["update_ai_policy"])
    ctx = SimpleNamespace(
        tenant_id=TENANT,
        principal_id=str(uuid4()),
        identity=SimpleNamespace(
            assurance_verified=verified, auth_time=datetime.now(timezone.utc) - timedelta(seconds=age)
        ),
        grants=[{"capability": "ai.policy.manage", "purpose": None, "scope_type": "TENANT"}],
    )
    with pytest.raises(DomainError) as caught:
        store.authorize(None, ctx, "update_ai_policy")
    assert (caught.value.status, caught.value.code, caught.value.reason) == (
        403,
        "ASSURANCE_REQUIRED",
        reason,
    )
    ctx.identity = SimpleNamespace(assurance_verified=True, auth_time=datetime.now(timezone.utc))
    store.authorize(None, ctx, "update_ai_policy")


def test_real_authorizer_refuses_a_reader_without_the_policy_capability(monkeypatch):
    _, rows = generated()
    monkeypatch.setitem(store.OPERATIONS, "update_ai_policy", rows["update_ai_policy"])
    ctx = SimpleNamespace(
        tenant_id=TENANT,
        principal_id=str(uuid4()),
        identity=SimpleNamespace(assurance_verified=True, auth_time=datetime.now(timezone.utc)),
        grants=[{"capability": "ai.enablement.read", "purpose": None, "scope_type": "TENANT"}],
    )
    with pytest.raises(DomainError) as caught:
        store.authorize(None, ctx, "update_ai_policy")
    assert (caught.value.status, caught.value.code) == (403, "POLICY_DENIED")


def test_onboarding_profile_proposes_the_capability_to_tenant_admin_only():
    holders = [name for name, caps in PROFILE["roles"].items() if "ai.policy.manage" in caps]
    assert holders == ["TENANT_ADMIN"]
    assert "ai.policy.manage" not in PROFILE["purpose_bound"]


def test_web_area_lists_ai_enablement_for_policy_holders_and_card_precedes_request():
    main = (ROOT / "apps/web/src/main.tsx").read_text()
    area = re.search(r'"ai-enablement": \[([^\]]*)\]', main).group(1)
    assert '"ai.policy."' in area and '"ai.enablement.read"' in area
    panel = (ROOT / "apps/web/src/AIEnablement.tsx").read_text()
    # The read-only "Policy in force" card is rendered before the advisory request button.
    assert panel.index("<AIPolicyInForce") < panel.index("Request AI advisory draft")


# Policy validation


def test_valid_policy_is_normalised_in_closed_list_order():
    rules = validate_policy(
        {
            "use_cases": [
                {**rule(enabled=False, use_case="CHAT")},
                rule(data_classes=["CONFIDENTIAL", "INTERNAL"], languages=["en", "hi"]),
            ]
        }
    )
    assert [r["use_case"] for r in rules] == ["ADVISORY_DRAFT", "CHAT"]
    assert rules[0]["data_classes"] == ["INTERNAL", "CONFIDENTIAL"]
    assert rules[0]["languages"] == ["en", "hi"] and rules[0]["tools"] == []
    assert validate_policy({"use_cases": []}) == []


@pytest.mark.parametrize(
    "change,reason",
    [
        ({"tools": ["web_search"]}, "AI_TOOLS_NOT_ALLOWED"),
        ({"use_case": "CHAT"}, "AI_USE_CASE_RESERVED"),
        ({"use_case": "EXTRACTION"}, "AI_USE_CASE_RESERVED"),
        ({"use_case": "REPORT_DRAFT"}, "AI_USE_CASE_RESERVED"),
        ({"destinations": []}, "AI_POLICY_INCOMPLETE"),
        ({"data_classes": []}, "AI_POLICY_INCOMPLETE"),
        ({"purposes": []}, "AI_POLICY_INCOMPLETE"),
        ({"languages": []}, "AI_POLICY_INCOMPLETE"),
        ({"destinations": ["openai-eu"]}, "AI_POLICY_INVALID"),
        ({"data_classes": ["SECRET"]}, "AI_POLICY_INVALID"),
        ({"data_classes": ["INTERNAL", "INTERNAL"]}, "AI_POLICY_INVALID"),
        ({"languages": ["english"]}, "AI_POLICY_INVALID"),
        ({"languages": ["en", "EN"]}, "AI_POLICY_INVALID"),
        ({"purposes": ["planning advice", "Planning advice"]}, "AI_POLICY_INVALID"),
        ({"purposes": [" padded"]}, "AI_POLICY_INVALID"),
        ({"purposes": ["x" * 201]}, "AI_POLICY_INVALID"),
        ({"purposes": ["line\nbreak"]}, "AI_POLICY_INVALID"),
        ({"review_mode": "NONE"}, "AI_POLICY_INVALID"),
        ({"budget_units": -1}, "AI_POLICY_INVALID"),
        ({"budget_units": 1000001}, "AI_POLICY_INVALID"),
        ({"budget_units": True}, "AI_POLICY_INVALID"),
        ({"enabled": "yes"}, "AI_POLICY_INVALID"),
        ({"approved_by": "self"}, "AI_POLICY_INVALID"),
    ],
)
def test_invalid_reserved_or_tool_granting_policies_are_refused(change, reason):
    with pytest.raises(DomainError) as caught:
        validate_policy({"use_cases": [rule(**change)]})
    assert (caught.value.status, caught.value.code, caught.value.reason) == (422, "VALIDATION_FAILED", reason)


@pytest.mark.parametrize(
    "data",
    [
        None,
        {},
        {"use_cases": {}},
        {"use_cases": [], "extra": 1},
        {"use_cases": [rule(), rule()]},
        {"use_cases": [rule(use_case=case, enabled=False) for case in contracts.USE_CASES] + [rule()]},
        {"use_cases": [{k: v for k, v in rule().items() if k != "tools"}]},
    ],
)
def test_malformed_policy_bodies_are_refused(data):
    with pytest.raises(DomainError) as caught:
        validate_policy(data)
    assert caught.value.status == 422


def test_reserved_use_cases_and_zero_budget_may_be_recorded_disabled():
    rules = validate_policy(
        {
            "use_cases": [
                rule(use_case=case, enabled=False, destinations=[], purposes=[], languages=[], budget_units=0)
                for case in contracts.USE_CASES
            ]
        }
    )
    assert [r["use_case"] for r in rules] == contracts.USE_CASES
    assert not any(r["enabled"] for r in rules)


# The gate


def test_gate_order_version_then_enablement_then_rules():
    with pytest.raises(DomainError) as stale:
        require(policy(2, enabled=False), "ADVISORY_DRAFT", 1, "CONFIDENTIAL", "openai-us", "en")
    assert (stale.value.status, stale.value.reason) == (409, "AI_POLICY_CHANGED")
    with pytest.raises(DomainError) as disabled:
        require(policy(2, enabled=False), "ADVISORY_DRAFT", 2, "CONFIDENTIAL", "openai-us", "en")
    assert (disabled.value.status, disabled.value.reason) == (503, "AI_USE_CASE_DISABLED")
    with pytest.raises(DomainError) as blocked:
        require(policy(2), "ADVISORY_DRAFT", 2, "CONFIDENTIAL", "openai-us", "en")
    assert (blocked.value.status, blocked.value.reason) == (422, "AI_POLICY_BLOCKED")
    assert require(policy(2), "ADVISORY_DRAFT", 2, "INTERNAL", "openai-us", "en")["budget_units"] == 100


def test_gate_names_every_unmet_rule_and_refuses_any_tool():
    with pytest.raises(DomainError) as blocked:
        require(
            policy(1, destinations=[], languages=["hi"], budget_units=0),
            "ADVISORY_DRAFT",
            1,
            "RESTRICTED",
            "openai-us",
            "en",
            ["web_search"],
        )
    message = blocked.value.message
    for fragment in ("restricted data", "destination", "language (en)", "no budget", "tools"):
        assert fragment in message


def test_gate_refuses_absent_policy_and_reserved_use_cases():
    empty = deepcopy(module.NO_POLICY)
    with pytest.raises(DomainError) as caught:
        require(empty, "ADVISORY_DRAFT", 0, "INTERNAL", "openai-us", "en")
    assert caught.value.reason == "AI_USE_CASE_DISABLED"
    with pytest.raises(DomainError) as caught:
        require(policy(1), "CHAT", 1, "INTERNAL", "openai-us", "en")
    assert caught.value.reason == "AI_USE_CASE_DISABLED"
    with pytest.raises(DomainError) as caught:
        require(policy(1), "ADVISORY_DRAFT", True, "INTERNAL", "openai-us", "en")
    assert caught.value.reason == "AI_POLICY_CHANGED"


# The save path on a database-free fake (the PGlite suite repeats it on the real database)


class Cursor:
    def __init__(self, row=None, rows=None):
        self.row, self.rows = row, rows or []

    def fetchone(self):
        return self.row

    def fetchall(self):
        return self.rows


class Database:
    def __init__(self):
        self.versions, self.rules, self.receipts, self.statements = [], [], {}, []
        self.active = False

    @contextmanager
    def transaction(self, tenant):
        assert not self.active
        self.active = True
        try:
            yield self
        finally:
            self.active = False

    def execute(self, sql, values=()):
        self.statements.append(sql)
        if sql.startswith("SELECT pg_advisory"):
            return Cursor()
        if "FROM impact.operation_receipt" in sql:
            return Cursor(self.receipts.get(values))
        if "FROM impact.ai_policy_version" in sql:
            rows = sorted(self.versions, key=lambda r: -r["version_no"])
            return Cursor(rows[0] if rows else None)
        if "FROM impact.ai_use_case_policy" in sql:
            return Cursor(rows=[r for r in self.rules if r["policy_version_id"] == values[1]])
        if "FROM impact.object_registry" in sql:
            head = max(self.versions, key=lambda r: r["version_no"])
            return Cursor({"object_id": head["object_id"], "head_revision": head["policy_version_id"]})
        if sql.startswith("INSERT INTO impact.ai_policy_version"):
            tenant, version_id, object_id, number, creator, created = values
            self.versions.append(
                dict(
                    policy_version_id=version_id,
                    object_id=object_id,
                    version_no=number,
                    created_by=creator,
                    created_at=created,
                )
            )
            return Cursor()
        if sql.startswith("INSERT INTO impact.ai_use_case_policy"):
            names = [
                "tenant_id",
                "policy_version_id",
                "use_case",
                "enabled",
                "data_classes",
                "destinations",
                "purposes",
                "languages",
                "review_mode",
                "budget_units",
                "tools",
            ]
            self.rules.append(dict(zip(names, values)))
            return Cursor()
        if sql.startswith("INSERT INTO impact.operation_receipt"):
            tenant, actor, command, operation, digest, outcome, expires = values
            self.receipts[(tenant, actor, command, operation)] = {
                "payload_hash": digest,
                "outcome": outcome.obj,
                "expires_at": expires,
            }
            return Cursor()
        raise AssertionError(sql)


@pytest.fixture
def saver(monkeypatch):
    db = Database()
    events, writes = [], []

    def authorize(c, ctx, operation, object_id=None, hidden=False):
        events.append(operation)
        if operation == "update_ai_policy" and not ctx.admin:
            raise DomainError("POLICY_DENIED", 403)

    def write(c, ctx, kind, data, state, previous=None):
        writes.append((kind, deepcopy(data), state, previous))
        return {
            "operation_id": "",
            "object_id": previous["object_id"] if previous else str(uuid4()),
            "revision_id": str(uuid4()),
            "business_state": state,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "correlation_id": "",
        }

    principal = SimpleNamespace(principal_id=str(uuid4()), admin=True)
    monkeypatch.setattr(module, "context", lambda c, identity, tenant, write=False: principal)
    monkeypatch.setattr(module, "authorize", authorize)
    monkeypatch.setattr(module, "write", write)
    monkeypatch.setattr(
        module, "audit", lambda c, ctx, op, receipt, correlation: events.append((op, deepcopy(receipt)))
    )
    return AIPolicy(SimpleNamespace(db=db), lambda: True), db, events, writes, principal


def command(expected=0, **changes):
    return {
        "operation_id": str(uuid4()),
        "expected_version": expected,
        "data": {"use_cases": [rule(**changes)]},
    }


def test_first_save_stores_version_1_with_exactly_that_use_case_and_audits(saver):
    api, db, events, writes, principal = saver
    receipt = api.save(None, TENANT, command(), str(uuid4()))
    assert receipt["policy_version"] == 1 and receipt["policy_version_id"] == receipt["revision_id"]
    assert [v["version_no"] for v in db.versions] == [1]
    assert db.versions[0]["created_by"] == principal.principal_id
    assert len(db.rules) == 1
    stored = {k: v for k, v in db.rules[0].items() if k not in {"tenant_id", "policy_version_id"}}
    assert stored == rule()
    assert writes[0][0] == "AIConfiguration" and writes[0][1] == {"policy_version": 1, "use_cases": [rule()]}
    audits = [event for event in events if isinstance(event, tuple)]
    assert [a[0] for a in audits] == ["ai_policy.changed"]
    view = api.get(None, TENANT)
    assert view["policy_version"] == 1 and view["use_cases"] == [rule()]
    assert view["advisory_available"] is True and view["server_enabled"] is True
    assert view["reserved_use_cases"] == ["EXTRACTION", "REPORT_DRAFT", "CHAT"]
    assert view["destinations"] == [{"id": "openai-us", "provider": "OpenAI", "region": "United States"}]


def test_second_version_is_a_new_revision_and_never_edits_the_first(saver):
    api, db, events, writes, _ = saver
    first = api.save(None, TENANT, command(), str(uuid4()))
    second = api.save(None, TENANT, command(1, enabled=False), str(uuid4()))
    assert second["policy_version"] == 2 and second["object_id"] == first["object_id"]
    assert writes[1][3]["head_revision"] == first["revision_id"]
    assert [v["version_no"] for v in db.versions] == [1, 2]
    assert [r["enabled"] for r in db.rules] == [True, False]
    assert not any(s.startswith(("UPDATE impact.ai_", "DELETE")) for s in db.statements)


def test_stale_expected_version_and_non_administrator_create_no_version(saver):
    api, db, events, _, principal = saver
    api.save(None, TENANT, command(), str(uuid4()))
    with pytest.raises(DomainError) as stale:
        api.save(None, TENANT, command(0), str(uuid4()))
    assert (stale.value.status, stale.value.reason) == (409, "AI_POLICY_CHANGED")
    principal.admin = False
    with pytest.raises(DomainError) as denied:
        api.save(None, TENANT, command(1), str(uuid4()))
    assert denied.value.status == 403
    assert len(db.versions) == 1 and len(db.rules) == 1


def test_exact_retry_returns_the_receipt_and_changed_payload_conflicts(saver):
    api, db, events, _, _ = saver
    body = command()
    receipt = api.save(None, TENANT, body, str(uuid4()))
    assert api.save(None, TENANT, deepcopy(body), str(uuid4())) == receipt
    changed = deepcopy(body)
    changed["data"]["use_cases"][0]["budget_units"] = 99
    with pytest.raises(DomainError) as caught:
        api.save(None, TENANT, changed, str(uuid4()))
    assert (caught.value.status, caught.value.code) == (409, "CONFLICT_OPERATION")
    assert len(db.versions) == 1


@pytest.mark.parametrize(
    "body",
    [
        None,
        {"operation_id": str(uuid4()), "data": {"use_cases": []}},
        {"operation_id": "not-a-uuid", "expected_version": 0, "data": {"use_cases": []}},
        {"operation_id": str(uuid4()), "expected_version": "0", "data": {"use_cases": []}},
        {"operation_id": str(uuid4()), "expected_version": -1, "data": {"use_cases": []}},
        {"operation_id": str(uuid4()), "expected_version": 0, "data": {"use_cases": []}, "created_by": "x"},
    ],
)
def test_closed_command_is_refused_before_any_database_access(saver, body):
    api, db, _, _, _ = saver
    with pytest.raises(DomainError) as caught:
        api.save(None, TENANT, body, str(uuid4()))
    assert caught.value.status == 422
    assert not db.statements


# Migration 0041


def sql():
    return MIGRATION.read_text()


def test_migration_is_additive_with_one_transaction_as_the_owner():
    text = sql()
    assert text.startswith("BEGIN;\nSET LOCAL ROLE impact_owner;\n")
    assert text.rstrip().endswith("COMMIT;")
    assert text.count("BEGIN;") == 1 and text.count("COMMIT;") == 1
    assert not re.search(r"\b(DROP|TRUNCATE|DELETE FROM|UPDATE impact)\b", text)


@pytest.mark.parametrize("table", ["ai_policy_version", "ai_use_case_policy"])
def test_policy_tables_are_tenant_keyed_fenced_insert_only_and_narrowly_granted(table):
    text = sql()
    body = re.search(r"CREATE TABLE impact\." + table + r"\((.*?)\n\);", text, re.S).group(1)
    assert re.search(r"PRIMARY KEY\(tenant_id,", body)
    assert all(fk.startswith("FOREIGN KEY(tenant_id,") for fk in re.findall(r"FOREIGN KEY\([^)]*\)", body))
    assert "ALTER TABLE impact." + table + " ENABLE ROW LEVEL SECURITY;" in text
    assert "ALTER TABLE impact." + table + " FORCE ROW LEVEL SECURITY;" in text
    assert (
        "CREATE POLICY tenant_fence ON impact." + table + "\n USING(tenant_id=impact.current_tenant()) "
        "WITH CHECK(tenant_id=impact.current_tenant());"
    ) in text
    assert re.search(r"BEFORE UPDATE OR DELETE ON impact\." + table + r"\b", text)
    grants = re.findall(r"GRANT ([A-Z, ]+) ON ([^;]*) TO ([a-z_]+);", text)
    for privileges, objects, role in grants:
        if table in objects:
            assert (privileges, role) == ("SELECT,INSERT", "impact_app")


def test_migration_checks_match_the_closed_contract_lists():
    text = sql()
    quoted = lambda items: ",".join("'" + item + "'" for item in items)  # noqa: E731
    assert "use_case IN (" + quoted(contracts.USE_CASES) + ")" in text
    assert "ARRAY[" + quoted(contracts.DATA_CLASSES) + "]::text[]" in text
    assert "ARRAY[" + quoted(contracts.DESTINATIONS) + "]::text[]" in text
    assert "review_mode IN (" + quoted(contracts.REVIEW_MODES) + ")" in text
    assert "CHECK(cardinality(tools)=0)" in text
    assert "CHECK(NOT enabled OR use_case='ADVISORY_DRAFT')" in text


def test_advisory_reservation_gains_a_nullable_tenant_keyed_policy_pin():
    text = sql()
    assert "ALTER TABLE impact.ai_advisory_request ADD COLUMN policy_version_id uuid;" in text
    assert (
        "FOREIGN KEY(tenant_id,policy_version_id) REFERENCES impact.ai_policy_version(tenant_id,policy_version_id)"
        in text
    )
    assert "CHECK(policy_version_id IS NOT NULL) NOT VALID;" in text


def test_migration_registers_the_generated_profile():
    assert "VALUES('" + PROFILE_HASH + "',$profile_0041$" in sql()
