from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from uuid import uuid4
import hashlib
import json
import re
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from jsonschema import Draft202012Validator, FormatChecker
from .config import ROOT
from .contracts import ENTITIES, REFERENCES, OPERATIONS, validate
from .domain import DomainError, unavailable


class Database:
    def __init__(self, s):
        self.s = s
        self.lock = RLock() if s.dev_db_serial else None

    @contextmanager
    def transaction(self, tenant=None, identity=False, platform=False):
        if platform and not self.s.platform_dsn:
            raise DomainError("SERVICE_UNAVAILABLE", 503, reason="PLATFORM_NOT_CONFIGURED")
        with self.lock if self.lock else nullcontext():
            with psycopg.connect(
                self.s.platform_dsn if platform else self.s.identity_dsn if identity else self.s.app_dsn,
                row_factory=dict_row,
                connect_timeout=5,
                prepare_threshold=None,
            ) as c:
                if self.s.environment in {"staging", "production"}:
                    row = c.execute(
                        "SELECT rolsuper,rolbypassrls,pg_has_role(current_user,'impact_owner','MEMBER') AS owns_schema FROM pg_roles WHERE rolname=current_user"
                    ).fetchone()
                    if any(row.values()):
                        raise RuntimeError("Privileged runtime connection refused")
                c.execute(
                    sql.SQL("SET LOCAL ROLE {}").format(
                        sql.Identifier(
                            "impact_platform" if platform else "impact_identity" if identity else "impact_app"
                        )
                    )
                )
                c.execute("SET LOCAL statement_timeout='8s'")
                c.execute("SET LOCAL lock_timeout='3s'")
                if tenant:
                    c.execute("SELECT set_config('impact.tenant_id',%s,true)", (str(tenant),))
                yield c


@dataclass
class Context:
    tenant_id: str
    principal_id: str
    membership_id: str
    identity: object
    policy_epoch: int
    subject_epoch: int
    grants: list


def context(c, identity, tenant, write=False):
    suffix = " FOR SHARE" if write else ""
    root = c.execute("SELECT * FROM impact.tenant_root WHERE tenant_id=%s" + suffix, (tenant,)).fetchone()
    if not root or root["lifecycle_state"] != "Active":
        unavailable()
    p = c.execute(
        "SELECT * FROM impact.tenant_principal WHERE tenant_id=%s AND identity_id=%s" + suffix,
        (tenant, identity.identity_id),
    ).fetchone()
    if not p or not p["active"]:
        unavailable()
    if p.get("auth_not_before") and identity.auth_time <= p["auth_not_before"]:
        raise DomainError("AUTH_REQUIRED", 401, reason="REAUTHENTICATION_REQUIRED")
    m = c.execute(
        "SELECT m.* FROM impact.membership_current m JOIN impact.object_registry r ON r.tenant_id=m.tenant_id AND r.object_id=m.object_id WHERE m.tenant_id=%s AND m.identity_id=%s AND r.lifecycle_state='Active' AND (m.status IS NULL OR m.status='Active')",
        (tenant, identity.identity_id),
    ).fetchone()
    now = datetime.now(timezone.utc)
    if not m or (m["expires_at"] and m["expires_at"] <= now):
        unavailable()
    grants = c.execute(
        "SELECT g.*,s.scope_type FROM impact.grant_current g JOIN impact.object_registry r ON r.tenant_id=g.tenant_id AND r.object_id=g.object_id JOIN impact.scope_definition s ON s.tenant_id=g.tenant_id AND s.scope_id=g.scope_id WHERE g.tenant_id=%s AND g.subject_id=%s AND r.lifecycle_state='Active' AND g.starts_at<=%s AND (g.expires_at IS NULL OR g.expires_at>%s)",
        (tenant, p["principal_id"], now, now),
    ).fetchall()
    # Group entitlements are evaluated on every permission check. The immutable group
    # revision is the source record; the relation is only its current access projection.
    grants += c.execute(
        "SELECT e.group_id AS object_id,e.capability,e.scope_id,e.expires_at,NULL AS purpose,s.scope_type "
        "FROM impact.group_entitlement e JOIN impact.object_registry r ON r.tenant_id=e.tenant_id AND r.object_id=e.group_id "
        "JOIN impact.scope_definition s ON s.tenant_id=e.tenant_id AND s.scope_id=e.scope_id "
        "WHERE e.tenant_id=%s AND e.membership_id=%s AND e.expires_at>%s AND r.lifecycle_state='Active'",
        (tenant, m["object_id"], now),
    ).fetchall()
    return Context(
        str(tenant),
        str(p["principal_id"]),
        str(m["object_id"]),
        identity,
        root["policy_epoch"],
        p["subject_epoch"],
        grants,
    )


def scopes(c, ctx, cap, object_id=None, purpose=None):
    for g in ctx.grants:
        if g["capability"] != cap or (g["purpose"] is not None and g["purpose"] != purpose):
            continue
        if g["scope_type"] == "TENANT":
            return True
        if (
            object_id
            and c.execute(
                "SELECT 1 FROM impact.scope_member WHERE tenant_id=%s AND scope_id=%s AND object_id=%s",
                (ctx.tenant_id, g["scope_id"], str(object_id)),
            ).fetchone()
        ):
            return True
    return False


def authorize(c, ctx, operation, object_id=None, hidden=False):
    p = OPERATIONS[operation]
    if not scopes(c, ctx, p["capability"], object_id):
        if hidden:
            unavailable()
        raise DomainError("POLICY_DENIED", 403)
    if p.get("purpose_required"):
        raise DomainError("POLICY_DENIED", 403, reason="PURPOSE_REQUIRED")
    seconds = p.get("fresh_assurance_seconds")
    if seconds and not getattr(ctx.identity, "assurance_verified", True):
        raise DomainError("ASSURANCE_REQUIRED", 403, reason="MFA_ASSURANCE_REQUIRED")
    if seconds and (datetime.now(timezone.utc) - ctx.identity.auth_time).total_seconds() > seconds:
        raise DomainError("ASSURANCE_REQUIRED", 403, reason="FRESH_AUTHENTICATION_REQUIRED")


def visible_sql(ctx, cap):
    grants = [g for g in ctx.grants if g["capability"] == cap and g["purpose"] is None]
    if any(g["scope_type"] == "TENANT" for g in grants):
        return "TRUE", []
    return (
        "EXISTS(SELECT 1 FROM impact.scope_member sm WHERE sm.tenant_id=r.tenant_id AND sm.object_id=r.object_id AND sm.scope_id=ANY(%s::uuid[]))",
        [[str(g["scope_id"]) for g in grants]],
    )


def canonical(data):
    return json.dumps(
        data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode()


def hash_data(data):
    return hashlib.sha256(canonical(data)).digest()


KINDS = {e["entity"]: e for e in ENTITIES.values()}


def table(kind):
    return (
        re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", kind)).lower()
        + "_current"
    )


def load(c, ctx, obj, kind=None, capability=None, lock=False):
    row = c.execute(
        "SELECT r.*,v.payload,v.schema_version,v.author_id,v.revision_number,v.restriction_state FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.object_id=r.object_id AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_id=%s"
        + (" FOR UPDATE OF r" if lock else ""),
        (ctx.tenant_id, str(obj)),
    ).fetchone()
    if (
        not row
        or (kind and row["object_type"] != kind)
        or row["restriction_state"] != "AVAILABLE"
        or row["classification"] == "RESTRICTED"
    ):
        unavailable()
    if capability and not scopes(c, ctx, capability, obj):
        unavailable()
    return row


def envelope(row):
    result = {
        "object_id": str(row["object_id"]),
        "tenant_id": str(row["tenant_id"]),
        "revision_id": str(row["head_revision"]),
        "schema_version": row["schema_version"],
        "lifecycle_state": row["lifecycle_state"],
        "classification": row["classification"],
        "created_at": row["created_at"].isoformat(),
        "created_by": str(row["created_by"]),
        "updated_at": row["updated_at"].isoformat(),
        "updated_by": str(row["author_id"]),
        "data": row["payload"],
    }
    if row["owner_id"]:
        result["owner_id"] = str(row["owner_id"])
    return result


def references(c, ctx, kind, data):
    for rule in [x for x in REFERENCES if x["entity"] == kind]:
        value = data.get(rule["field"])
        ref = rule["reference"]
        if value is None:
            continue
        if ref.startswith("O:"):
            row = load(c, ctx, value, ref[2:] if ref[2:] != "*" else None)
            target = KINDS.get(row["object_type"])
            if target and not scopes(c, ctx, target["route"] + ".read", value):
                unavailable()
        elif ref.startswith("R:"):
            row = c.execute(
                "SELECT object_id,object_type,restriction_state FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
                (ctx.tenant_id, value),
            ).fetchone()
            if (
                not row
                or row["restriction_state"] != "AVAILABLE"
                or (ref[2:] != "*" and row["object_type"] != ref[2:])
            ):
                unavailable()
            load(c, ctx, row["object_id"])
            target = KINDS.get(row["object_type"])
            if target and not scopes(c, ctx, target["route"] + ".read", row["object_id"]):
                unavailable()
        elif ref == "P":
            if not c.execute(
                "SELECT 1 FROM impact.tenant_principal WHERE tenant_id=%s AND principal_id=%s AND active",
                (ctx.tenant_id, value),
            ).fetchone():
                unavailable()


def write(c, ctx, kind, data, state="Draft", previous=None, object_id=None, track_author=True):
    now = datetime.now(timezone.utc)
    obj = str(previous["object_id"]) if previous else str(object_id or uuid4())
    rev = str(uuid4())
    if kind in KINDS:
        validate(kind + "Data", data)
    if previous:
        c.execute(
            "UPDATE impact.object_registry SET head_revision=%s,lifecycle_state=%s,updated_at=%s WHERE tenant_id=%s AND object_id=%s",
            (rev, state, now, ctx.tenant_id, obj),
        )
    else:
        c.execute(
            "INSERT INTO impact.object_registry(tenant_id,object_id,object_type,head_revision,lifecycle_state,classification,owner_id,created_at,created_by,updated_at) VALUES(%s,%s,%s,%s,%s,'INTERNAL',%s,%s,%s,%s)",
            (ctx.tenant_id, obj, kind, rev, state, ctx.principal_id, now, ctx.principal_id, now),
        )
    c.execute(
        "INSERT INTO impact.object_revision(tenant_id,object_id,revision_id,object_type,predecessor_revision,schema_version,payload,payload_sha256,author_id,created_at,revision_number) VALUES(%s,%s,%s,%s,%s,'1.2',%s,%s,%s,%s,%s)",
        (
            ctx.tenant_id,
            obj,
            rev,
            kind,
            previous["head_revision"] if previous else None,
            Jsonb(data),
            hash_data(data),
            ctx.principal_id,
            now,
            previous["revision_number"] + 1 if previous else 1,
        ),
    )
    if kind in KINDS:
        columns = ["tenant_id", "object_id", "revision_id"] + list(data)
        values = [ctx.tenant_id, obj, rev] + [
            Jsonb(v) if isinstance(v, (dict, list)) else v for v in data.values()
        ]
        query = sql.SQL("INSERT INTO impact.{} ({}) VALUES ({})").format(
            sql.Identifier(table(kind)),
            sql.SQL(",").join(map(sql.Identifier, columns)),
            sql.SQL(",").join(sql.Placeholder() for _ in values),
        )
        if previous:
            query += sql.SQL(" ON CONFLICT(tenant_id,object_id) DO UPDATE SET {}").format(
                sql.SQL(",").join(
                    sql.SQL("{}=EXCLUDED.{}").format(sql.Identifier(k), sql.Identifier(k))
                    for k in columns[2:]
                )
            )
        c.execute(query, values)
    if track_author:
        c.execute(
            "INSERT INTO impact.object_natural_author VALUES(%s,%s,%s) ON CONFLICT DO NOTHING",
            (ctx.tenant_id, obj, ctx.identity.natural_identity_id),
        )
    return {
        "operation_id": "",
        "object_id": obj,
        "revision_id": rev,
        "business_state": state,
        "saved_at": now.isoformat(),
        "correlation_id": "",
    }


EVENT_VALIDATOR = Draft202012Validator(
    json.loads((ROOT / "packages/contracts/event.schema.json").read_text()), format_checker=FormatChecker()
)


def audit(c, ctx, op, receipt, correlation):
    write(
        c,
        ctx,
        "AuditEvent",
        {
            "real_actor_id": ctx.principal_id,
            "effective_actor_id": ctx.principal_id,
            "action_type": op,
            "object_reference": receipt["object_id"],
            "outcome": "SUCCEEDED",
            "occurred_at": receipt["saved_at"],
            "correlation_id": correlation,
            "specification_ref": "F06",
        },
        "Recorded",
        track_author=False,
    )
    row = c.execute(
        "SELECT object_type,revision_number FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
        (ctx.tenant_id, receipt["revision_id"]),
    ).fetchone()
    event = {
        "event_id": str(uuid4()),
        "tenant_id": ctx.tenant_id,
        "event_type": "object.changed",
        "schema_version": "1.1",
        "aggregate_type": row["object_type"],
        "aggregate_id": receipt["object_id"],
        "aggregate_revision": receipt["revision_id"],
        "aggregate_sequence": row["revision_number"],
        "occurred_at": receipt["saved_at"],
        "actor_id": ctx.principal_id,
        "correlation_id": correlation,
        "payload": {
            "object_id": receipt["object_id"],
            "revision_id": receipt["revision_id"],
            "state": receipt["business_state"],
        },
    }
    EVENT_VALIDATOR.validate(event)
    c.execute(
        "INSERT INTO impact.outbox_event VALUES(%s,%s,%s,%s,%s)",
        (ctx.tenant_id, event["event_id"], event["event_type"], event["occurred_at"], Jsonb(event)),
    )
    c.execute(
        "INSERT INTO impact.outbox_delivery(tenant_id,event_id) VALUES(%s,%s)",
        (ctx.tenant_id, event["event_id"]),
    )
    return event["event_id"]
