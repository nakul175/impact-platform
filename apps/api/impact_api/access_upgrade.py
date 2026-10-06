"""Three-party, exact-profile widening of existing managed delegation ceilings.

An upgrade adds capabilities introduced since the last applied manifest. An old
capability removed before proposal is never restored, and any authority change
after proposal invalidates its consent. Existing expiries are never extended.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from psycopg.types.json import Jsonb

from .access_bootstrap import PROFILE, PROFILE_HASH
from .access_upgrade_contracts import ACTIONS, validate_body
from .authority_renewal import AuthorityRenewal, changed, denied
from .domain import DomainError, unavailable
from .platform_security import current_owner, registered_person
from .store import Context, hash_data, load, write
from .tenant_lifecycle import now

VERSION = "reviewed-access-upgrade-v1"


def capabilities(manifest):
    return set(manifest.get("purpose_bound", [])) | {
        cap for bundle in manifest["roles"].values() for cap in bundle
    }


def compatible(source, target):
    """A widening may never remove a previously reviewed bundle or capability."""
    return (
        capabilities(source) <= capabilities(target)
        and set(source.get("purpose_bound", [])) <= set(target.get("purpose_bound", []))
        and all(
            name in target["roles"] and set(caps) <= set(target["roles"][name])
            for name, caps in source["roles"].items()
        )
    )


def profile_manifest():
    return {key: value for key, value in PROFILE.items() if key in {"version", "roles", "purpose_bound"}}


class AccessUpgrade:
    def __init__(self, lifecycle):
        self.lifecycle, self.db, self.s = lifecycle, lifecycle.db, lifecycle.s
        self.renewal = AuthorityRenewal(lifecycle)

    def entry(self, c, tenant_id, request_id, lock=False):
        return c.execute(
            "SELECT u.*,o.operating_name FROM impact.tenant_access_upgrade u "
            "JOIN impact.tenant_onboarding o USING(tenant_id) WHERE u.tenant_id=%s AND u.request_id=%s"
            + (" FOR UPDATE OF u" if lock else ""),
            (tenant_id, request_id),
        ).fetchone()

    def pending(self, c, tenant_id):
        return c.execute(
            "SELECT 1 FROM impact.tenant_access_upgrade WHERE tenant_id=%s AND state IN ('Requested','Accepted')",
            (tenant_id,),
        ).fetchone()

    def present(self, row):
        keys = [
            "request_id",
            "tenant_id",
            "revision_id",
            "operating_name",
            "bootstrap_request_id",
            "owner_identity_id",
            "second_identity_id",
            "state",
            "current_manifest",
            "authority_hash",
            "profile_hash",
            "target_manifest",
            "new_capabilities",
            "reason",
        ]
        return {
            **{key: str(row[key]) if key.endswith("_id") else row[key] for key in keys},
            "review_expires_at": row["review_expires_at"].isoformat(),
            "accepted_at": row["accepted_at"].isoformat() if row["accepted_at"] else None,
            "approved_by": str(row["approved_by"]) if row["approved_by"] else None,
            "applied_at": row["applied_at"].isoformat() if row["applied_at"] else None,
        }

    def visible(self, c, identity, tenant, operator):
        if operator:
            return True
        if str(tenant["owner_identity_id"]) == identity.identity_id:
            try:
                owner = current_owner(c, tenant)
                return not owner["auth_not_before"] or identity.auth_time > owner["auth_not_before"]
            except DomainError:
                return False
        applied = self.renewal.applied(c, str(tenant["tenant_id"]))
        if not applied:
            return False
        original = c.execute(
            "SELECT second_identity_id FROM impact.tenant_access_bootstrap WHERE tenant_id=%s AND request_id=%s",
            (tenant["tenant_id"], applied["request_id"]),
        ).fetchone()
        if not original or str(original["second_identity_id"]) != identity.identity_id:
            return False
        holding = self.renewal.holding(c, str(tenant["tenant_id"]), identity.identity_id)
        if not holding:
            return False
        principal = c.execute(
            "SELECT auth_not_before FROM impact.tenant_principal WHERE tenant_id=%s AND principal_id=%s",
            (tenant["tenant_id"], holding[0]["principal_id"]),
        ).fetchone()
        return not principal["auth_not_before"] or identity.auth_time > principal["auth_not_before"]

    def tenant_read(self, c, identity, tenant_id):
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_id,))
        tenant = c.execute(
            "SELECT o.*,r.lifecycle_state,r.region_policy FROM impact.tenant_onboarding o "
            "JOIN impact.tenant_root r USING(tenant_id) WHERE o.tenant_id=%s",
            (tenant_id,),
        ).fetchone()
        operator = self.lifecycle.operator(c, identity)
        if not tenant or not self.visible(c, identity, tenant, operator):
            unavailable()
        return tenant, operator

    def cursor(self, payload):
        from .service import Service

        return Service.cursor(self, payload)

    def directory(self, identity, tenant_id=None, after=None):
        from .service import Service

        if not self.s.platform_dsn:
            unavailable()
        with self.db.transaction(platform=True) as c:
            visibility = c.execute(
                "SELECT impact.access_upgrade_visibility(%s) AS value", (identity.identity_id,)
            ).fetchone()["value"]
            tenant_visibility = None
            if tenant_id:
                tenant, _ = self.tenant_read(c, identity, tenant_id)
                tenant_visibility = [
                    str(tenant["revision_id"]),
                    str(tenant["owner_identity_id"]),
                    c.execute(
                        "SELECT policy_epoch FROM impact.tenant_root WHERE tenant_id=%s", (tenant_id,)
                    ).fetchone()["policy_epoch"],
                ]
            binding = hash_data(
                [
                    "access-upgrade-inbox" if tenant_id is None else "tenant-access-upgrades",
                    tenant_id,
                    identity.identity_id,
                    visibility,
                    tenant_visibility,
                ]
            ).hex()
            key = Service.cursor_key(self, binding, after)
            if key is not None:
                try:
                    key = str(UUID(key))
                except (ValueError, TypeError, AttributeError):
                    raise DomainError("INVALID_CURSOR", 400) from None
            if tenant_id is None:
                operator = self.lifecycle.operator(c, identity)
                refs = c.execute(
                    "SELECT * FROM impact.access_upgrade_refs(%s,%s)", (identity.identity_id, key)
                ).fetchall()
                items = []
                for ref in refs[:50]:
                    scoped = str(ref["tenant_id"])
                    try:
                        self.tenant_read(c, identity, scoped)
                    except DomainError as error:
                        if error.code == "RESOURCE_UNAVAILABLE":
                            continue
                        raise
                    items.append(self.present(self.entry(c, scoped, str(ref["request_id"]))))
                return {
                    "operator": operator,
                    "items": items,
                    "next_cursor": Service.next_cursor(self, binding, str(refs[49]["request_id"]))
                    if len(refs) > 50
                    else None,
                }
            _, operator = self.tenant_read(c, identity, tenant_id)
            rows = c.execute(
                "SELECT u.*,o.operating_name FROM impact.tenant_access_upgrade u "
                "JOIN impact.tenant_onboarding o USING(tenant_id) WHERE u.tenant_id=%s "
                "AND (%s OR %s IN(u.owner_identity_id,u.second_identity_id)) "
                "AND (%s::uuid IS NULL OR u.request_id>%s::uuid) ORDER BY u.request_id LIMIT 51",
                (tenant_id, operator, identity.identity_id, key, key),
            ).fetchall()
            return {
                "operator": operator,
                "items": [self.present(row) for row in rows[:50]],
                "next_cursor": Service.next_cursor(self, binding, str(rows[49]["request_id"]))
                if len(rows) > 50
                else None,
            }

    def snapshot(self, c, tenant, second_identity):
        tenant_id = str(tenant["tenant_id"])
        holdings = [
            self.renewal.holding(c, tenant_id, person)
            for person in [str(tenant["owner_identity_id"]), second_identity]
        ]
        if not all(holdings):
            return None
        manifest, authority_rows = self.renewal.assemble(holdings)
        row_principals = {
            str(row["authority_id"]): entry["principal_id"] for entry, rows in holdings for row in rows
        }
        applied = self.renewal.applied(c, tenant_id)
        if not manifest or not applied:
            return None
        source = (
            c.execute(
                "SELECT request_id,target_manifest AS manifest FROM impact.tenant_access_upgrade "
                "WHERE tenant_id=%s AND state='Applied' ORDER BY applied_at DESC,request_id DESC LIMIT 1",
                (tenant_id,),
            ).fetchone()
            or c.execute(
                "SELECT request_id,manifest FROM impact.tenant_access_bootstrap WHERE tenant_id=%s AND request_id=%s",
                (tenant_id, applied["request_id"]),
            ).fetchone()
        )

        def revisions(ids):
            rows = c.execute(
                "SELECT r.object_id,r.head_revision,v.payload_sha256 FROM impact.object_registry r "
                "JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
                "WHERE r.tenant_id=%s AND r.object_id=ANY(%s::uuid[]) ORDER BY r.object_id",
                (tenant_id, ids),
            ).fetchall()
            return [
                {
                    "object_id": str(r["object_id"]),
                    "revision_id": str(r["head_revision"]),
                    "payload_sha256": bytes(r["payload_sha256"]).hex(),
                }
                for r in rows
            ]

        roles = c.execute(
            "SELECT r.object_id,r.head_revision,r.lifecycle_state,v.payload_sha256,v.payload->>'name' AS name "
            "FROM impact.object_registry r JOIN impact.object_revision v "
            "ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
            "WHERE r.tenant_id=%s AND r.object_type='RoleTemplate' "
            "AND v.payload->>'managed_by'='impact-access-v1' "
            "AND COALESCE(v.payload->>'custom','false')<>'true' ORDER BY r.object_id",
            (tenant_id,),
        ).fetchall()
        if len({r["name"] for r in roles}) != len(roles):
            denied("AUTHORITY_UNAVAILABLE")
        return {
            **manifest,
            "version": VERSION,
            "authority_rows": [
                {
                    "authority_id": str(r["authority_id"]),
                    "principal_id": row_principals[str(r["authority_id"])],
                    "capability": r["capability"],
                    "scope_id": str(r["scope_id"]),
                    "expires_at": r["expires_at"].astimezone(timezone.utc).isoformat(),
                }
                for r in sorted(authority_rows, key=lambda r: str(r["authority_id"]))
            ],
            "grant_revisions": revisions(sorted({g for p in manifest["principals"] for g in p["grant_ids"]})),
            "membership_revisions": revisions([p["membership_id"] for p in manifest["principals"]]),
            "managed_roles": [
                {
                    "object_id": str(r["object_id"]),
                    "revision_id": str(r["head_revision"]),
                    "payload_sha256": bytes(r["payload_sha256"]).hex(),
                    "state": r["lifecycle_state"],
                    "name": r["name"],
                }
                for r in roles
            ],
            "source_request_id": str(source["request_id"]),
            "source_manifest": source["manifest"],
        }

    def describe(self, c, tenant):
        existing = self.renewal.describe(c, tenant)
        second = existing["second_identity_id"]
        manifest = self.snapshot(c, tenant, second) if second else None
        target = profile_manifest()
        registered = c.execute(
            "SELECT 1 FROM impact.platform_access_profile WHERE profile_hash=%s AND manifest=%s",
            (PROFILE_HASH, Jsonb(target)),
        ).fetchone()
        conflict = c.execute(
            "SELECT 1 FROM impact.object_registry r JOIN impact.object_revision v "
            "ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
            "WHERE r.tenant_id=%s AND r.object_type='RoleTemplate' AND r.lifecycle_state='Active' "
            "AND v.payload->>'custom'='true' AND lower(v.payload->>'name')=ANY(%s) LIMIT 1",
            (tenant["tenant_id"], [name.lower() for name in target["roles"]]),
        ).fetchone()
        new = []
        if manifest:
            # The applicator (migration 0036) orders its delta with the database's default collation, so the
            # stored list must use that order too; a code-point sort differs under en_US-style collations.
            added = sorted(capabilities(target) - capabilities(manifest["source_manifest"]))
            new = [
                r["value"]
                for r in c.execute(
                    "SELECT value FROM jsonb_array_elements_text(%s::jsonb) ORDER BY value", (Jsonb(added),)
                ).fetchall()
            ]
        reason = (
            "ACCESS_PROFILE_NOT_REGISTERED"
            if not registered
            else "ACCESS_PROFILE_ROLE_CONFLICT"
            if conflict
            else existing["reason_unavailable"]
        )
        if manifest and reason is None:
            reason = (
                "ACCESS_UPGRADE_PENDING"
                if self.pending(c, tenant["tenant_id"])
                else "ACCESS_PROFILE_INCOMPATIBLE"
                if not compatible(manifest["source_manifest"], target)
                else "ACCESS_PROFILE_ALREADY_HELD"
                if manifest["source_manifest"] == target
                else None
            )
        return {
            "tenant_id": str(tenant["tenant_id"]),
            "tenant_revision": str(tenant["revision_id"]),
            "owner_identity_id": str(tenant["owner_identity_id"]),
            "second_identity_id": second,
            "authority_hash": hash_data(manifest).hex() if manifest else None,
            "profile_hash": PROFILE_HASH,
            "target_manifest": target,
            "current_manifest": manifest,
            "new_capabilities": new,
            "upgradable": reason is None,
            "reason_unavailable": reason,
        }

    def preview(self, identity, tenant_id):
        if not self.s.platform_dsn:
            unavailable()
        with self.db.transaction(platform=True) as c:
            tenant, _ = self.tenant_read(c, identity, tenant_id)
            return self.describe(c, tenant)

    def command(self, identity, action, body, tenant_id, request_id=None):
        if action not in ACTIONS | {"request"}:
            unavailable()
        validate_body(body, create=action == "request")
        self.lifecycle.assurance(identity)
        fingerprint = hash_data(
            {"access_upgrade_action": action, "tenant": tenant_id, "request": request_id, "body": body}
        )
        with self.db.transaction(platform=True) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant_id,))
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_id,))
            operator = self.lifecycle.operator(c, identity)
            tenant = self.lifecycle.entry(c, tenant_id)
            row = self.entry(c, tenant_id, request_id, lock=True) if request_id else None
            if not tenant or (
                request_id
                and (
                    not row
                    or not (
                        operator
                        or identity.identity_id
                        in {str(row["owner_identity_id"]), str(row["second_identity_id"])}
                    )
                )
            ):
                unavailable()
            if action in {"approve", "reject"}:
                if not operator:
                    denied("PLATFORM_OPERATOR_REQUIRED")
            elif action == "accept":
                if str(row["second_identity_id"]) != identity.identity_id:
                    unavailable()
                # A historical nomination does not authorise a replay after membership ends.
                if not self.renewal.holding(c, tenant_id, identity.identity_id):
                    denied("SECOND_ADMIN_UNAVAILABLE")
                if not self.visible(c, identity, tenant, False):
                    denied("REAUTHENTICATION_REQUIRED")
            else:
                if str(tenant["owner_identity_id"]) != identity.identity_id:
                    unavailable()
                owner = current_owner(c, tenant)
                if owner["auth_not_before"] and identity.auth_time <= owner["auth_not_before"]:
                    denied("REAUTHENTICATION_REQUIRED")
            if action not in {"cancel", "reject"} and tenant["lifecycle_state"] != "Active":
                denied("TENANT_NOT_ACTIVE")
            c.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",
                ("platform:" + identity.identity_id + ":" + body["operation_id"],),
            )
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
            response = {
                **self.present(self.entry(c, tenant_id, request_id)),
                "operation_id": body["operation_id"],
            }
            c.execute(
                "INSERT INTO impact.platform_event(event_id,tenant_id,identity_id,action,revision_id,reason,payload) "
                "VALUES(%s,%s,%s,%s,%s,%s,%s)",
                (
                    str(uuid4()),
                    tenant_id,
                    identity.identity_id,
                    "access-upgrade-" + action,
                    response["revision_id"],
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

    def request(self, c, identity, tenant, data):
        described = self.describe(c, tenant)
        if not described["upgradable"]:
            reason = described["reason_unavailable"]
            if reason in {"ACCESS_UPGRADE_PENDING", "RENEWAL_PENDING", "ACCESS_PROFILE_ALREADY_HELD"}:
                raise DomainError("CONFLICT_VERSION", 409, reason=reason)
            denied(reason)
        if data["second_identity_id"] != described["second_identity_id"]:
            denied("SECOND_ADMIN_UNAVAILABLE")
        second = registered_person(c, data["second_identity_id"], self.s.issuer)
        if str(second["natural_identity_id"]) == identity.natural_identity_id:
            denied("INDEPENDENCE_REQUIRED")
        if data["authority_hash"] != described["authority_hash"]:
            changed()
        if data["profile_hash"] != PROFILE_HASH:
            raise DomainError("CONFLICT_VERSION", 409, reason="ACCESS_PROFILE_CHANGED")
        owner = current_owner(c, tenant)
        applied = self.renewal.applied(c, str(tenant["tenant_id"]))
        manifest = described["current_manifest"]
        created_at = now()
        deadline = min(
            created_at + timedelta(days=7),
            *[datetime.fromisoformat(r["expires_at"]) for r in manifest["authority_rows"]],
        )
        request_id = str(uuid4())
        c.execute(
            "INSERT INTO impact.tenant_access_upgrade(tenant_id,request_id,revision_id,state,bootstrap_request_id,"
            "owner_identity_id,second_identity_id,tenant_revision,owner_revision,current_manifest,authority_hash,"
            "profile_hash,target_manifest,new_capabilities,review_expires_at,owner_auth_time,reason,created_at) "
            "VALUES(%s,%s,%s,'Requested',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                tenant["tenant_id"],
                request_id,
                str(uuid4()),
                applied["request_id"],
                identity.identity_id,
                data["second_identity_id"],
                tenant["revision_id"],
                owner["head_revision"],
                Jsonb(manifest),
                described["authority_hash"],
                PROFILE_HASH,
                Jsonb(described["target_manifest"]),
                Jsonb(described["new_capabilities"]),
                deadline,
                identity.auth_time,
                data["reason"],
                created_at,
            ),
        )
        return request_id

    def recheck(self, c, tenant, row):
        owner = current_owner(c, tenant)
        if (
            tenant["revision_id"] != row["tenant_revision"]
            or owner["head_revision"] != row["owner_revision"]
            or tenant["owner_identity_id"] != row["owner_identity_id"]
        ):
            raise DomainError("CONFLICT_VERSION", 409, reason="ACCESS_UPGRADE_CONTEXT_CHANGED")
        if row["review_expires_at"] <= now():
            denied("ACCESS_UPGRADE_EXPIRED")
        if not all(self.lifecycle.readiness(c, tenant).values()):
            denied("TENANT_NOT_READY")
        if row["profile_hash"] != PROFILE_HASH or row["target_manifest"] != profile_manifest():
            raise DomainError("CONFLICT_VERSION", 409, reason="ACCESS_PROFILE_CHANGED")
        if not c.execute(
            "SELECT 1 FROM impact.platform_access_profile WHERE profile_hash=%s AND manifest=%s",
            (row["profile_hash"], Jsonb(row["target_manifest"])),
        ).fetchone():
            denied("ACCESS_PROFILE_NOT_REGISTERED")
        applied = self.renewal.applied(c, str(tenant["tenant_id"]))
        manifest = self.snapshot(c, tenant, str(row["second_identity_id"]))
        if (
            not applied
            or applied["request_id"] != row["bootstrap_request_id"]
            or not manifest
            or hash_data(manifest).hex() != row["authority_hash"]
            or hash_data(row["current_manifest"]).hex() != row["authority_hash"]
        ):
            changed()
        people = [
            registered_person(c, row[key], self.s.issuer)
            for key in ["owner_identity_id", "second_identity_id"]
        ]
        if people[0]["natural_identity_id"] == people[1]["natural_identity_id"]:
            denied("INDEPENDENCE_REQUIRED")
        for person, instant in zip(people, [row["owner_auth_time"], row["second_auth_time"]]):
            if instant and person["auth_not_before"] and instant <= person["auth_not_before"]:
                denied("REAUTHENTICATION_REQUIRED")
        if owner["auth_not_before"] and row["owner_auth_time"] <= owner["auth_not_before"]:
            denied("REAUTHENTICATION_REQUIRED")
        return people

    def transition(self, c, identity, tenant, row, action):
        allowed = {
            "accept": {"Requested"},
            "approve": {"Accepted"},
            "reject": {"Requested", "Accepted"},
            "cancel": {"Requested", "Accepted"},
        }
        if row["state"] not in allowed[action]:
            raise DomainError("CONFLICT_VERSION", 409, reason="INVALID_ACCESS_UPGRADE_TRANSITION")
        if action in {"cancel", "reject"}:
            c.execute(
                "UPDATE impact.tenant_access_upgrade SET state=%s,revision_id=%s,updated_at=now() "
                "WHERE tenant_id=%s AND request_id=%s",
                (
                    "Cancelled" if action == "cancel" else "Rejected",
                    str(uuid4()),
                    tenant["tenant_id"],
                    row["request_id"],
                ),
            )
            return
        people = self.recheck(c, tenant, row)
        if action == "accept":
            c.execute(
                "UPDATE impact.tenant_access_upgrade SET state='Accepted',revision_id=%s,updated_at=now(),"
                "accepted_at=now(),second_auth_time=%s WHERE tenant_id=%s AND request_id=%s",
                (str(uuid4()), identity.auth_time, tenant["tenant_id"], row["request_id"]),
            )
            return
        if identity.natural_identity_id in {str(person["natural_identity_id"]) for person in people}:
            denied("INDEPENDENCE_REQUIRED")
        self.apply(c, identity, tenant, row)

    def apply(self, c, identity, tenant, row):
        tenant_id = str(tenant["tenant_id"])
        # The narrow definer rechecks the pinned pre-change authority and is the sole ceiling writer.
        applied = c.execute(
            "SELECT impact.apply_access_upgrade(%s,%s,%s,%s) AS count",
            (tenant_id, row["request_id"], identity.identity_id, identity.auth_time),
        ).fetchone()
        principal = c.execute(
            "INSERT INTO impact.tenant_principal(tenant_id,principal_id,identity_id,principal_kind) "
            "VALUES(%s,%s,%s,'HUMAN') ON CONFLICT(tenant_id,identity_id) DO UPDATE SET identity_id=EXCLUDED.identity_id "
            "RETURNING principal_id",
            (tenant_id, str(uuid4()), identity.identity_id),
        ).fetchone()
        ctx = Context(tenant_id, str(principal["principal_id"]), "", identity, 0, 0, [])
        roles = {}
        source = row["current_manifest"]["source_manifest"]
        pinned = {entry["name"]: entry for entry in row["current_manifest"]["managed_roles"]}
        for name, caps in row["target_manifest"]["roles"].items():
            entry = pinned.get(name)
            if entry and entry["state"] != "Active":
                continue  # A retired managed template is never resurrected by an upgrade.
            if not entry and name in source["roles"]:
                continue  # A missing previously reviewed template is not recreated.
            previous = load(c, ctx, entry["object_id"], "RoleTemplate", lock=True) if entry else None
            payload = {
                "managed_by": "impact-access-v1",
                "name": name,
                "capabilities": caps,
                "administrative": name == "TENANT_ADMIN",
            }
            if previous:
                # Preserve explicit old omissions. Only capabilities introduced
                # for this role after the last applied profile may be added.
                role_delta = set(caps) - set(source["roles"].get(name, []))
                payload = {
                    **previous["payload"],
                    "capabilities": sorted(set(previous["payload"].get("capabilities", [])) | role_delta),
                }
            if previous and previous["payload"] == payload:
                roles[name] = {
                    "object_id": str(previous["object_id"]),
                    "revision_id": str(previous["head_revision"]),
                }
            else:
                roles[name] = write(c, ctx, "RoleTemplate", payload, "Active", previous, track_author=False)
        delta = sorted(
            set(row["target_manifest"]["roles"]["TENANT_ADMIN"]) - set(source["roles"]["TENANT_ADMIN"])
        )
        if delta and "TENANT_ADMIN" not in roles:
            changed()
        expected = 0
        for entry in row["current_manifest"]["principals"]:
            expiry = min(
                r["expires_at"]
                for r in row["current_manifest"]["authority_rows"]
                if r["principal_id"] == entry["principal_id"]
            )
            absent = set(row["new_capabilities"]) - set(entry["capabilities"])
            expected += len(absent)
            grants = [
                write(
                    c,
                    ctx,
                    "Grant",
                    {
                        "subject_id": entry["principal_id"],
                        "capability": cap,
                        "scope_id": entry["scope_id"],
                        "starts_at": now().isoformat(),
                        "expires_at": expiry,
                        "issuer_id": ctx.principal_id,
                    },
                    "Active",
                    track_author=False,
                )["object_id"]
                for cap in delta
                if cap in absent
            ]
            if grants:
                admin = roles["TENANT_ADMIN"]
                c.execute(
                    "INSERT INTO impact.member_role_assignment VALUES(%s,%s,%s,%s,%s,%s,%s,%s::uuid[])",
                    (
                        tenant_id,
                        str(uuid4()),
                        entry["membership_id"],
                        admin["object_id"],
                        admin["revision_id"],
                        entry["scope_id"],
                        expiry,
                        grants,
                    ),
                )
            c.execute(
                "UPDATE impact.tenant_principal SET subject_epoch=subject_epoch+1 WHERE tenant_id=%s AND principal_id=%s",
                (tenant_id, entry["principal_id"]),
            )
        if applied["count"] != expected:
            changed()
        c.execute(
            "UPDATE impact.tenant_root SET policy_epoch=policy_epoch+1 WHERE tenant_id=%s", (tenant_id,)
        )
