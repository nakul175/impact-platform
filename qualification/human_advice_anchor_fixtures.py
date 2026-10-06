"""Storage-valid negative fixtures, never an API creation/retention/privacy workflow.

Append unavailable older pins and a readable successor, then insert a schema-valid
case with existing independent fixture members. No old row or trigger is changed.
"""

from datetime import datetime, timezone
import os
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb

from impact_api.auth import Identity
from impact_api.human_advice import STORED_VALIDATOR, brief_digest, initial_payload
from impact_api.human_advice_contracts import operation
from impact_api.store import audit, context, hash_data, write
from test_ai_adoption_plans_live import save as save_plan
from test_human_advice_unit import creation

GUARDS = (
    "revision_removal_guard",
    "human_advice_projection_guard",
    "human_advice_head_consistency",
    "human_advice_brief_immutable",
    "ai_plan_content_binding_immutable",
)


def unavailable_anchor_case(live, restriction):
    assert restriction in {"RESTRICTED", "REMOVED"}
    original = save_plan(live)
    tenant = live.fixture["tenant_a"]
    older, newer, obj, nonce = (str(uuid4()) for _ in range(4))
    requester, adviser = (live.fixture["actors"][name] for name in ("admin", "reviewer"))
    now = datetime.now(timezone.utc)
    request = creation()
    request["data"].update(
        context_plan_id=original["object_id"],
        context_plan_revision=older,
        adviser_membership_id=adviser["membership_id"],
    )
    parties = {
        who + "_" + destination: actor[source]
        for who, actor in (("requester", requester), ("adviser", adviser))
        for destination, source in (
            ("principal_id", "principal_id"),
            ("membership_id", "membership_id"),
            ("natural_id", "natural_identity_id"),
        )
    }
    assert parties["requester_natural_id"] != parties["adviser_natural_id"]
    payload = initial_payload(request["data"], parties, now.isoformat(), nonce)
    STORED_VALIDATOR.validate(payload)
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
        guards = c.execute(
            "SELECT tgname,tgenabled FROM pg_trigger WHERE tgname=ANY(%s) ORDER BY tgname", (list(GUARDS),)
        ).fetchall()
        assert {row["tgname"] for row in guards} == set(GUARDS)
        assert all(row["tgenabled"] == "O" for row in guards)
        for revision, predecessor, state in (
            (older, original["revision_id"], restriction),
            (newer, older, "AVAILABLE"),
        ):
            c.execute(
                "INSERT INTO impact.object_revision(tenant_id,object_id,revision_id,object_type,"
                "predecessor_revision,schema_version,payload,payload_sha256,author_id,created_at,"
                "restriction_state,revision_number) "
                "SELECT tenant_id,object_id,%s,object_type,%s,schema_version,"
                "CASE WHEN %s='REMOVED' THEN NULL ELSE payload END,payload_sha256,author_id,now(),%s,"
                "(SELECT max(n.revision_number)+1 FROM impact.object_revision n "
                "WHERE n.tenant_id=v.tenant_id AND n.object_id=v.object_id) "
                "FROM impact.object_revision v WHERE tenant_id=%s AND object_id=%s AND revision_id=%s",
                (revision, predecessor, state, state, tenant, original["object_id"], original["revision_id"]),
            )
        c.execute(
            "UPDATE impact.object_registry SET head_revision=%s,updated_at=now() WHERE tenant_id=%s AND object_id=%s",
            (newer, tenant, original["object_id"]),
        )
        c.execute(
            "INSERT INTO impact.ai_plan_content_binding(tenant_id,object_id,revision_id,snapshot_id) "
            "SELECT tenant_id,object_id,%s,snapshot_id FROM impact.ai_plan_content_binding "
            "WHERE tenant_id=%s AND object_id=%s AND revision_id=%s",
            (newer, tenant, original["object_id"], original["revision_id"]),
        )
        identity = Identity(
            requester["identity_id"],
            requester["natural_identity_id"],
            requester["identity_id"],
            now,
            assurance_verified=True,
        )
        ctx = context(c, identity, tenant, write=True)
        c.execute("SELECT set_config('impact.human_advice_principal',%s,true)", (ctx.principal_id,))
        c.execute(
            "INSERT INTO impact.human_advice_case_current(tenant_id,object_id,revision_id,context_plan_id,"
            "context_plan_revision,requester_principal_id,requester_membership_id,requester_natural_id,"
            "adviser_principal_id,adviser_membership_id,adviser_natural_id,case_state) "
            "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'Open')",
            (
                tenant,
                obj,
                str(uuid4()),
                original["object_id"],
                older,
                *[
                    parties[key]
                    for key in (
                        "requester_principal_id",
                        "requester_membership_id",
                        "requester_natural_id",
                        "adviser_principal_id",
                        "adviser_membership_id",
                        "adviser_natural_id",
                    )
                ],
            ),
        )
        receipt = write(c, ctx, "HumanAdviceCase", payload, "Open", object_id=obj)
        c.execute(
            "UPDATE impact.human_advice_case_current SET revision_id=%s WHERE tenant_id=%s AND object_id=%s",
            (receipt["revision_id"], tenant, obj),
        )
        c.execute(
            "INSERT INTO impact.human_advice_private_brief(tenant_id,object_id,problem,problem_sha256,brief_nonce) "
            "VALUES(%s,%s,%s,%s,%s)",
            (tenant, obj, request["data"]["problem"], brief_digest(request["data"]["problem"], nonce), nonce),
        )
        receipt.update(operation_id=request["operation_id"], correlation_id=str(uuid4()))
        audit(c, ctx, operation(), receipt, receipt["correlation_id"])
        c.execute(
            "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,now()+interval '7 days')",
            (
                tenant,
                ctx.principal_id,
                operation(),
                request["operation_id"],
                hash_data([operation(), None, request]),
                Jsonb(receipt),
            ),
        )
        event = c.execute(
            "SELECT event_id FROM impact.outbox_event WHERE tenant_id=%s AND payload->>'aggregate_type'='HumanAdviceCase' "
            "AND payload->>'aggregate_id'=%s",
            (tenant, obj),
        ).fetchone()["event_id"]
        c.execute(
            "INSERT INTO impact.consumer_receipt(tenant_id,consumer,event_id,applied_at) "
            "VALUES(%s,'synthetic-unavailable-anchor-fixture',%s,now())",
            (tenant, event),
        )
        assert (
            c.execute(
                "SELECT tgname,tgenabled FROM pg_trigger WHERE tgname=ANY(%s) ORDER BY tgname",
                (list(GUARDS),),
            ).fetchall()
            == guards
        )
    return {
        "case": receipt,
        "request": request,
        "original": original,
        "older": older,
        "newer": newer,
        "event_id": event,
    }


def case_pointer_visibility(live, fixture, connection_methods=None):
    obj, tenant, event = fixture["case"]["object_id"], live.fixture["tenant_a"], fixture["event_id"]
    queries = {
        "case": ("SELECT object_id FROM impact.human_advice_case_current WHERE object_id=%s", obj),
        "registry": ("SELECT object_id FROM impact.object_registry WHERE object_id=%s", obj),
        "revision": ("SELECT revision_id FROM impact.object_revision WHERE object_id=%s", obj),
        "brief": ("SELECT object_id FROM impact.human_advice_private_brief WHERE object_id=%s", obj),
        "author": ("SELECT object_id FROM impact.object_natural_author WHERE object_id=%s", obj),
        "audit": ("SELECT object_id FROM impact.audit_event_current WHERE object_reference=%s", obj),
        "audit_revision": (
            "SELECT object_id FROM impact.object_revision WHERE object_type='AuditEvent' AND payload->>'object_reference'=%s",
            obj,
        ),
        "receipt": (
            "SELECT operation_id FROM impact.operation_receipt WHERE outcome->>'object_id'=%s AND command_type='create_human_advice_case'",
            obj,
        ),
        "event": ("SELECT event_id FROM impact.outbox_event WHERE event_id=%s", event),
        "delivery": ("SELECT event_id FROM impact.outbox_delivery WHERE event_id=%s", event),
        "consumer": ("SELECT event_id FROM impact.consumer_receipt WHERE event_id=%s", event),
    }
    native = os.environ.get("IMPACT_NATIVE_TEST") == "1"
    dsn = os.environ.get("IMPACT_LOGIN_DSN_APP")
    if native and not dsn:
        raise RuntimeError("ACTUAL_NATIVE_APP_DSN_REQUIRED")
    method = (
        "actual impact_app_login with SET LOCAL ROLE impact_app"
        if native
        else "PGlite fixture connection with SET LOCAL ROLE impact_app"
    )
    if connection_methods is not None:
        connection_methods.append(method)
    with psycopg.connect(dsn, prepare_threshold=None) if native else live.db() as c:
        c.execute("SET LOCAL ROLE impact_app")
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        c.execute(
            "SELECT set_config('impact.human_advice_principal',%s,true)",
            (live.fixture["actors"]["admin"]["principal_id"],),
        )
        return {
            key: bool(c.execute(query, (selector,)).fetchall()) for key, (query, selector) in queries.items()
        }
