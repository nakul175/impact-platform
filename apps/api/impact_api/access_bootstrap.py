"""One-time, identity-bound review of initial tenant access and delegation ceilings."""

import json
from datetime import timedelta
from pathlib import Path
from uuid import uuid4
from psycopg.types.json import Jsonb
from .bootstrap_contracts import ACTIONS, validate_body
from .domain import DomainError, unavailable
from .platform_security import registered_person, current_owner
from .store import Context, hash_data, write
from .tenant_lifecycle import now

PROFILE = json.loads(Path(__file__).with_name("bootstrap_profile.json").read_text())
PROFILE_HASH = hash_data(PROFILE).hex()


def denied(reason):
    raise DomainError("POLICY_DENIED", 403, reason=reason)


class AccessBootstrap:
    def __init__(self, lifecycle):
        self.lifecycle, self.db, self.s = lifecycle, lifecycle.db, lifecycle.s

    def person(self, c, identity):
        return registered_person(c, identity, self.s.issuer)

    def entry(self, c, request):
        return c.execute(
            "SELECT b.*,o.operating_name FROM impact.tenant_access_bootstrap b JOIN impact.tenant_onboarding o USING(tenant_id) WHERE request_id=%s FOR UPDATE OF b",
            (request,),
        ).fetchone()

    def present(self, row):
        keys = [
            "request_id",
            "tenant_id",
            "revision_id",
            "operating_name",
            "owner_identity_id",
            "second_identity_id",
            "state",
            "manifest",
            "profile_hash",
            "reason",
            "scope_id",
            "second_membership_id",
        ]
        return {
            **{key: str(row[key]) if key.endswith("_id") and row[key] else row[key] for key in keys},
            "expires_at": row["expires_at"].isoformat(),
            "review_expires_at": row["review_expires_at"].isoformat(),
        }

    def directory(self, identity, after=None):
        result = {
            "operator": False,
            "profile": PROFILE,
            "profile_hash": PROFILE_HASH,
            "items": [],
            "next_cursor": None,
        }
        if not self.s.platform_dsn:
            return result
        with self.db.transaction(platform=True) as c:
            result["operator"] = self.lifecycle.operator(c, identity)
            rows = c.execute(
                "SELECT b.*,o.operating_name FROM impact.tenant_access_bootstrap b JOIN impact.tenant_onboarding o USING(tenant_id) WHERE (%s OR %s IN (b.owner_identity_id,b.second_identity_id)) AND (%s::uuid IS NULL OR b.request_id>%s::uuid) ORDER BY b.request_id LIMIT 51",
                (result["operator"], identity.identity_id, after, after),
            ).fetchall()
            result["items"] = [self.present(row) for row in rows[:50]]
            result["next_cursor"] = str(rows[49]["request_id"]) if len(rows) > 50 else None
            return result

    def owner(self, c, tenant):
        return current_owner(c, tenant)

    def command(self, identity, action, body, tenant_id=None, request_id=None):
        if action not in ACTIONS | {"request"}:
            unavailable()
        validate_body(body, create=action == "request")
        self.lifecycle.assurance(identity)
        fingerprint = hash_data(
            {"bootstrap_action": action, "tenant": tenant_id, "request": request_id, "body": body}
        )
        with self.db.transaction(platform=True) as c:
            c.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",
                ("platform:" + identity.identity_id + ":" + body["operation_id"],),
            )
            operator = self.lifecycle.operator(c, identity)
            # Resolve without row locks, then use the shared tenant lock before all row locks.
            if request_id:
                ref = c.execute(
                    "SELECT tenant_id FROM impact.tenant_access_bootstrap WHERE request_id=%s AND (%s OR %s IN(owner_identity_id,second_identity_id))",
                    (request_id, operator, identity.identity_id),
                ).fetchone()
                if not ref:
                    unavailable()
                tenant_id = str(ref["tenant_id"])
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant_id,))
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_id,))
            tenant = self.lifecycle.entry(c, tenant_id)
            if not tenant:
                unavailable()
            row = self.entry(c, request_id) if request_id else None
            if action in {"approve", "reject"}:
                if not operator:
                    denied("PLATFORM_OPERATOR_REQUIRED")
            elif action == "accept":
                if str(row["second_identity_id"]) != identity.identity_id:
                    unavailable()
            elif str(tenant["owner_identity_id"]) != identity.identity_id:
                unavailable()
            if action not in {"cancel", "reject"} and tenant["lifecycle_state"] != "Active":
                denied("TENANT_NOT_ACTIVE")
            if action in {"request", "cancel"}:
                owner = self.owner(c, tenant)
                if owner["auth_not_before"] and identity.auth_time <= owner["auth_not_before"]:
                    denied("REAUTHENTICATION_REQUIRED")
            old = c.execute(
                "SELECT * FROM impact.platform_receipt WHERE identity_id=%s AND operation_id=%s",
                (identity.identity_id, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["fingerprint"]) != fingerprint or old["expires_at"] <= now():
                    raise DomainError("CONFLICT_VERSION", 409, reason="OPERATION_REUSE")
                return old["response"]
            if str((row or tenant)["revision_id"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if action == "request":
                request_id = self.request(c, identity, tenant, body["data"])
            else:
                self.transition(c, identity, tenant, row, action)
            revision = str(uuid4())
            c.execute(
                "UPDATE impact.tenant_access_bootstrap SET revision_id=%s,updated_at=now() WHERE request_id=%s",
                (revision, request_id),
            )
            response = {**self.present(self.entry(c, request_id)), "operation_id": body["operation_id"]}
            c.execute(
                "INSERT INTO impact.platform_event(event_id,tenant_id,identity_id,action,revision_id,reason,payload) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                (
                    str(uuid4()),
                    tenant_id,
                    identity.identity_id,
                    "initial-access-" + action,
                    revision,
                    body["data"]["reason"],
                    Jsonb(response),
                ),
            )
            c.execute(
                "INSERT INTO impact.platform_receipt VALUES(%s,%s,%s,%s,%s)",
                (
                    identity.identity_id,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(response),
                    now() + timedelta(days=7),
                ),
            )
            return response

    def empty(self, c, tenant_id):
        if (
            c.execute(
                "SELECT 1 FROM impact.tenant_access_bootstrap_applied WHERE tenant_id=%s", (tenant_id,)
            ).fetchone()
            or c.execute(
                "SELECT 1 FROM impact.object_registry WHERE tenant_id=%s AND object_type='Grant' LIMIT 1",
                (tenant_id,),
            ).fetchone()
            or c.execute(
                "SELECT 1 FROM impact.grant_authority WHERE tenant_id=%s LIMIT 1", (tenant_id,)
            ).fetchone()
        ):
            denied("INITIAL_ACCESS_ALREADY_PROVISIONED")

    def request(self, c, identity, tenant, data):
        from datetime import datetime

        self.empty(c, tenant["tenant_id"])
        if c.execute(
            "SELECT 1 FROM impact.tenant_access_bootstrap WHERE tenant_id=%s AND state IN ('Requested','Accepted','Applied')",
            (tenant["tenant_id"],),
        ).fetchone():
            raise DomainError("CONFLICT_VERSION", 409, reason="INITIAL_ACCESS_PENDING")
        if data["profile_hash"] != PROFILE_HASH:
            raise DomainError("CONFLICT_VERSION", 409, reason="ACCESS_PROFILE_CHANGED")
        expiry = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
        if not now() < expiry <= now() + timedelta(days=90):
            raise DomainError("VALIDATION_FAILED", reason="GRANT_EXPIRY_BOUNDS")
        second = self.person(c, data["second_identity_id"])
        if str(second["natural_identity_id"]) == identity.natural_identity_id:
            denied("INDEPENDENCE_REQUIRED")
        self.eligible_second(c, tenant, data["second_identity_id"])
        owner = self.owner(c, tenant)
        manifest = {
            "version": PROFILE["version"],
            "roles": {name: PROFILE["roles"][name] for name in ["TENANT_ADMIN", *sorted(data["role_names"])]},
        }
        request_id = str(uuid4())
        c.execute(
            "INSERT INTO impact.tenant_access_bootstrap(request_id,tenant_id,revision_id,state,owner_identity_id,second_identity_id,tenant_revision,owner_revision,manifest,profile_hash,expires_at,review_expires_at,owner_auth_time,reason) VALUES(%s,%s,%s,'Requested',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                request_id,
                tenant["tenant_id"],
                str(uuid4()),
                identity.identity_id,
                data["second_identity_id"],
                tenant["revision_id"],
                owner["head_revision"],
                Jsonb(manifest),
                PROFILE_HASH,
                expiry,
                min(expiry, now() + timedelta(days=7)),
                identity.auth_time,
                data["reason"],
            ),
        )
        return request_id

    def eligible_second(self, c, tenant, identity):
        if (
            c.execute(
                "SELECT 1 FROM impact.membership_current WHERE tenant_id=%s AND identity_id=%s",
                (tenant["tenant_id"], identity),
            ).fetchone()
            or c.execute(
                "SELECT 1 FROM impact.tenant_principal WHERE tenant_id=%s AND identity_id=%s AND NOT active",
                (tenant["tenant_id"], identity),
            ).fetchone()
        ):
            denied("SECOND_ADMIN_UNAVAILABLE")

    def recheck(self, c, tenant, row):
        self.empty(c, tenant["tenant_id"])
        owner = self.owner(c, tenant)
        if (
            tenant["revision_id"] != row["tenant_revision"]
            or owner["head_revision"] != row["owner_revision"]
            or tenant["owner_identity_id"] != row["owner_identity_id"]
        ):
            raise DomainError("CONFLICT_VERSION", 409, reason="INITIAL_ACCESS_CONTEXT_CHANGED")
        if row["review_expires_at"] <= now() or row["expires_at"] <= now():
            denied("INITIAL_ACCESS_EXPIRED")
        if not all(self.lifecycle.readiness(c, tenant).values()):
            denied("TENANT_NOT_READY")
        if row["profile_hash"] != PROFILE_HASH or row["manifest"] != {
            "version": PROFILE["version"],
            "roles": {name: PROFILE["roles"].get(name) for name in row["manifest"]["roles"]},
        }:
            raise DomainError("CONFLICT_VERSION", 409, reason="ACCESS_PROFILE_CHANGED")
        people = [self.person(c, row[key]) for key in ["owner_identity_id", "second_identity_id"]]
        if people[0]["natural_identity_id"] == people[1]["natural_identity_id"]:
            denied("INDEPENDENCE_REQUIRED")
        for person, auth_time in zip(people, [row["owner_auth_time"], row["second_auth_time"]]):
            if auth_time and person["auth_not_before"] and auth_time <= person["auth_not_before"]:
                denied("REAUTHENTICATION_REQUIRED")
        if owner["auth_not_before"] and row["owner_auth_time"] <= owner["auth_not_before"]:
            denied("REAUTHENTICATION_REQUIRED")
        self.eligible_second(c, tenant, row["second_identity_id"])
        return owner, people

    def transition(self, c, identity, tenant, row, action):
        allowed = {
            "accept": {"Requested"},
            "approve": {"Accepted"},
            "reject": {"Requested", "Accepted"},
            "cancel": {"Requested", "Accepted"},
        }
        if row["state"] not in allowed[action]:
            raise DomainError("CONFLICT_VERSION", 409, reason="INVALID_ACCESS_TRANSITION")
        if action in {"cancel", "reject"}:
            c.execute(
                "UPDATE impact.tenant_access_bootstrap SET state=%s WHERE request_id=%s",
                ("Cancelled" if action == "cancel" else "Rejected", row["request_id"]),
            )
            return
        owner, people = self.recheck(c, tenant, row)
        if action == "accept":
            c.execute(
                "UPDATE impact.tenant_access_bootstrap SET state='Accepted',accepted_at=now(),second_auth_time=%s WHERE request_id=%s",
                (identity.auth_time, row["request_id"]),
            )
            return
        if identity.natural_identity_id in {str(p["natural_identity_id"]) for p in people}:
            denied("INDEPENDENCE_REQUIRED")
        self.apply(c, identity, tenant, row, owner, people[1])

    def apply(self, c, identity, tenant, row, owner, second):
        tenant_id = str(tenant["tenant_id"])

        def principal(identity_id):
            return str(
                c.execute(
                    "INSERT INTO impact.tenant_principal(tenant_id,principal_id,identity_id,principal_kind) VALUES(%s,%s,%s,'HUMAN') ON CONFLICT(tenant_id,identity_id) DO UPDATE SET identity_id=EXCLUDED.identity_id RETURNING principal_id",
                    (tenant_id, str(uuid4()), identity_id),
                ).fetchone()["principal_id"]
            )

        ctx = Context(tenant_id, principal(identity.identity_id), "", identity, 0, 0, [])
        second_principal = principal(row["second_identity_id"])
        member = write(
            c,
            ctx,
            "Membership",
            {
                "identity_id": str(row["second_identity_id"]),
                "authority_source": "Reviewed initial access " + str(row["request_id"]),
                "external": False,
                "status": "Active",
                "joined_at": now().isoformat(),
                "expires_at": row["expires_at"].isoformat(),
            },
            "Active",
            track_author=False,
        )
        c.execute(
            "INSERT INTO impact.member_profile VALUES(%s,%s,%s,%s)",
            (tenant_id, member["object_id"], second["display_name"], second["email_mask"]),
        )
        scope = write(
            c,
            ctx,
            "Predicate",
            {"title": "All workspace records", "scope_type": "TENANT", "managed_by": "impact-access-v1"},
            "Active",
            track_author=False,
        )
        c.execute(
            "INSERT INTO impact.scope_definition VALUES(%s,%s,'TENANT',%s)",
            (tenant_id, scope["object_id"], scope["revision_id"]),
        )
        roles = {}
        for name, caps in row["manifest"]["roles"].items():
            roles[name] = write(
                c,
                ctx,
                "RoleTemplate",
                {
                    "managed_by": "impact-access-v1",
                    "name": name,
                    "capabilities": caps,
                    "administrative": name == "TENANT_ADMIN",
                },
                "Active",
                track_author=False,
            )
        admin = roles["TENANT_ADMIN"]
        for principal_id, membership_id in [
            (str(owner["principal_id"]), str(tenant["owner_membership_id"])),
            (second_principal, member["object_id"]),
        ]:
            grants = [
                write(
                    c,
                    ctx,
                    "Grant",
                    {
                        "subject_id": principal_id,
                        "capability": cap,
                        "scope_id": scope["object_id"],
                        "starts_at": now().isoformat(),
                        "expires_at": row["expires_at"].isoformat(),
                        "issuer_id": ctx.principal_id,
                    },
                    "Active",
                    track_author=False,
                )["object_id"]
                for cap in row["manifest"]["roles"]["TENANT_ADMIN"]
            ]
            c.execute(
                "INSERT INTO impact.member_role_assignment VALUES(%s,%s,%s,%s,%s,%s,%s,%s::uuid[])",
                (
                    tenant_id,
                    str(uuid4()),
                    membership_id,
                    admin["object_id"],
                    admin["revision_id"],
                    scope["object_id"],
                    row["expires_at"],
                    grants,
                ),
            )
            c.execute(
                "UPDATE impact.tenant_principal SET subject_epoch=subject_epoch+1 WHERE tenant_id=%s AND principal_id=%s",
                (tenant_id, principal_id),
            )
        c.execute(
            "UPDATE impact.tenant_root SET policy_epoch=policy_epoch+1 WHERE tenant_id=%s", (tenant_id,)
        )
        c.execute(
            "UPDATE impact.tenant_access_bootstrap SET state='Applied',approved_by=%s,scope_id=%s,second_membership_id=%s WHERE request_id=%s",
            (identity.identity_id, scope["object_id"], member["object_id"], row["request_id"]),
        )
        c.execute("SELECT impact.apply_initial_authority(%s)", (row["request_id"],))
