"""Reviewed renewal of the delegation ceilings created by initial tenant access."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4
from psycopg.types.json import Jsonb
from .domain import DomainError, unavailable
from .platform_security import current_owner, registered_person
from .renewal_contracts import ACTIONS, validate_body
from .store import Context, hash_data, load, write
from .tenant_lifecycle import now

VERSION = "authority-renewal-v1"
MANAGED_ADMIN = ("impact-access-v1", "TENANT_ADMIN")


def denied(reason):
    raise DomainError("POLICY_DENIED", 403, reason=reason)


def changed():
    raise DomainError("CONFLICT_VERSION", 409, reason="AUTHORITY_CHANGED")


def instant(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        raise DomainError("VALIDATION_FAILED") from None
    if parsed.tzinfo is None:
        raise DomainError("VALIDATION_FAILED")
    return parsed


class AuthorityRenewal:
    def __init__(self, lifecycle):
        self.lifecycle, self.db, self.s = lifecycle, lifecycle.db, lifecycle.s

    def person(self, c, identity):
        return registered_person(c, identity, self.s.issuer)

    def entry(self, c, request):
        return c.execute(
            "SELECT b.*,o.operating_name FROM impact.tenant_authority_renewal b JOIN impact.tenant_onboarding o USING(tenant_id) WHERE request_id=%s FOR UPDATE OF b",
            (request,),
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
            "manifest",
            "authority_hash",
            "reason",
        ]
        return {
            **{key: str(row[key]) if key.endswith("_id") else row[key] for key in keys},
            "previous_expires_at": row["previous_expires_at"].isoformat(),
            "expires_at": row["expires_at"].isoformat(),
            "review_expires_at": row["review_expires_at"].isoformat(),
            "accepted_at": row["accepted_at"].isoformat() if row["accepted_at"] else None,
            "approved_by": str(row["approved_by"]) if row["approved_by"] else None,
            "applied_at": row["applied_at"].isoformat() if row["applied_at"] else None,
        }

    def directory(self, identity, after=None):
        result = {"operator": False, "items": [], "next_cursor": None}
        if not self.s.platform_dsn:
            return result
        with self.db.transaction(platform=True) as c:
            result["operator"] = self.lifecycle.operator(c, identity)
            rows = c.execute(
                "SELECT b.*,o.operating_name FROM impact.tenant_authority_renewal b JOIN impact.tenant_onboarding o USING(tenant_id) WHERE (%s OR %s IN(b.owner_identity_id,b.second_identity_id)) AND (%s::uuid IS NULL OR b.request_id>%s::uuid) ORDER BY b.request_id LIMIT 51",
                (result["operator"], identity.identity_id, after, after),
            ).fetchall()
            result["items"] = [self.present(row) for row in rows[:50]]
            result["next_cursor"] = str(rows[49]["request_id"]) if len(rows) > 50 else None
            return result

    def applied(self, c, tenant_id):
        return c.execute(
            "SELECT request_id FROM impact.tenant_access_bootstrap_applied WHERE tenant_id=%s", (tenant_id,)
        ).fetchone()

    def pending(self, c, tenant_id):
        return c.execute(
            "SELECT 1 FROM impact.tenant_authority_renewal WHERE tenant_id=%s AND state IN ('Requested','Accepted')",
            (tenant_id,),
        ).fetchone()

    def upgrade_pending(self, c, tenant_id):
        return c.execute(
            "SELECT 1 FROM impact.tenant_access_upgrade WHERE tenant_id=%s AND state IN ('Requested','Accepted')",
            (tenant_id,),
        ).fetchone()

    def holding(self, c, tenant_id, identity_id):
        """Current delegated authority of one identity, or None when it holds none that is usable."""
        principal = c.execute(
            "SELECT principal_id FROM impact.tenant_principal WHERE tenant_id=%s AND identity_id=%s AND active",
            (tenant_id, identity_id),
        ).fetchone()
        if not principal:
            return None
        principal_id = str(principal["principal_id"])
        rows = c.execute(
            "SELECT authority_id,capability,scope_id,expires_at FROM impact.grant_authority WHERE tenant_id=%s AND principal_id=%s AND expires_at>now() ORDER BY authority_id",
            (tenant_id, principal_id),
        ).fetchall()
        if not rows or len({str(r["scope_id"]) for r in rows}) != 1:
            return None
        scope_id = str(rows[0]["scope_id"])
        member = c.execute(
            "SELECT m.object_id FROM impact.membership_current m JOIN impact.object_registry r ON r.tenant_id=m.tenant_id AND r.object_id=m.object_id WHERE m.tenant_id=%s AND m.identity_id=%s AND r.lifecycle_state='Active' AND (m.status IS NULL OR m.status='Active') AND (m.expires_at IS NULL OR m.expires_at>now())",
            (tenant_id, identity_id),
        ).fetchone()
        if not member:
            return None
        membership_id = str(member["object_id"])
        # Only the managed administrative assignment created by initial access is renewed;
        # business role assignments keep their own reviewed expiry.
        assignments = c.execute(
            "SELECT a.assignment_id,a.grant_ids FROM impact.member_role_assignment a JOIN impact.object_revision v ON v.tenant_id=a.tenant_id AND v.revision_id=a.role_revision WHERE a.tenant_id=%s AND a.membership_id=%s AND a.scope_id=%s AND a.expires_at>now() AND v.object_type='RoleTemplate' AND v.payload->>'managed_by'=%s AND v.payload->>'name'=%s ORDER BY a.assignment_id",
            (tenant_id, membership_id, scope_id, *MANAGED_ADMIN),
        ).fetchall()
        candidates = sorted({str(g) for a in assignments for g in a["grant_ids"]})
        grants = c.execute(
            "SELECT g.object_id FROM impact.grant_current g JOIN impact.object_registry r ON r.tenant_id=g.tenant_id AND r.object_id=g.object_id WHERE g.tenant_id=%s AND g.object_id=ANY(%s::uuid[]) AND g.subject_id=%s AND g.scope_id=%s AND r.lifecycle_state='Active' AND g.expires_at>now() ORDER BY g.object_id",
            (tenant_id, candidates, principal_id, scope_id),
        ).fetchall()
        entry = {
            "principal_id": principal_id,
            "identity_id": str(identity_id),
            "membership_id": membership_id,
            "scope_id": scope_id,
            "capabilities": sorted({r["capability"] for r in rows}),
            # Hashed value: normalised to UTC so the manifest does not depend on session time zone.
            "expires_at": max(r["expires_at"] for r in rows).astimezone(timezone.utc).isoformat(),
            "assignment_ids": [str(a["assignment_id"]) for a in assignments],
            "grant_ids": [str(g["object_id"]) for g in grants],
        }
        return entry, rows

    def assemble(self, holdings):
        rows = [row for _, held in holdings for row in held]
        manifest = {
            "version": VERSION,
            "authority_ids": sorted(str(r["authority_id"]) for r in rows),
            "principals": [entry for entry, _ in holdings],
        }
        return manifest, rows

    def manifest_for(self, c, tenant, owner_identity, second_identity):
        """Manifest and pinned authority rows for the two administrators, or (None, []) if unavailable."""
        holdings = [self.holding(c, str(tenant["tenant_id"]), i) for i in [owner_identity, second_identity]]
        if not all(holdings):
            return None, []
        return self.assemble(holdings)

    def describe(self, c, tenant):
        tenant_id, owner_identity = str(tenant["tenant_id"]), str(tenant["owner_identity_id"])
        applied = self.applied(c, tenant_id)
        holders = [
            str(r["identity_id"])
            for r in c.execute(
                "SELECT DISTINCT p.identity_id FROM impact.grant_authority a JOIN impact.tenant_principal p ON p.tenant_id=a.tenant_id AND p.principal_id=a.principal_id WHERE a.tenant_id=%s AND a.expires_at>now() AND p.active AND p.identity_id IS NOT NULL ORDER BY 1",
                (tenant_id,),
            ).fetchall()
        ]
        others = [h for h in holders if h != owner_identity]
        result = {
            "tenant_id": tenant_id,
            "tenant_revision": str(tenant["revision_id"]),
            "bootstrap_request_id": str(applied["request_id"]) if applied else None,
            "owner_identity_id": owner_identity,
            "second_identity_id": None,
            "authority_hash": None,
            "earliest_expires_at": None,
            "principals": [],
            "renewable": False,
            "reason_unavailable": None,
        }
        owner = self.holding(c, tenant_id, owner_identity) if applied else None
        second = self.holding(c, tenant_id, others[0]) if owner and len(others) == 1 else None
        if not owner:
            reason = "AUTHORITY_UNAVAILABLE"
        elif not second:
            reason = "SECOND_ADMIN_UNAVAILABLE"
        else:
            manifest, rows = self.assemble([owner, second])
            result.update(
                second_identity_id=others[0],
                authority_hash=hash_data(manifest).hex(),
                earliest_expires_at=min(r["expires_at"] for r in rows).isoformat(),
                principals=manifest["principals"],
            )
            reason = (
                "TENANT_NOT_ACTIVE"
                if tenant["lifecycle_state"] != "Active"
                else "TENANT_NOT_READY"
                if not all(self.lifecycle.readiness(c, tenant).values())
                else "RENEWAL_PENDING"
                if self.pending(c, tenant_id)
                else "ACCESS_UPGRADE_PENDING"
                if self.upgrade_pending(c, tenant_id)
                else None
            )
        result["renewable"], result["reason_unavailable"] = reason is None, reason
        return result

    def authority(self, identity, tenant_id):
        if not self.s.platform_dsn:
            unavailable()
        with self.db.transaction(platform=True) as c:
            operator = self.lifecycle.operator(c, identity)
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_id,))
            # Read-only description takes no tenant row locks (readiness takes shared identity locks).
            tenant = c.execute(
                "SELECT o.*,r.lifecycle_state,r.region_policy FROM impact.tenant_onboarding o JOIN impact.tenant_root r USING(tenant_id) WHERE o.tenant_id=%s",
                (tenant_id,),
            ).fetchone()
            if not tenant or not (operator or str(tenant["owner_identity_id"]) == identity.identity_id):
                unavailable()
            return self.describe(c, tenant)

    def command(self, identity, action, body, tenant_id=None, request_id=None):
        if action not in ACTIONS | {"request"}:
            unavailable()
        validate_body(body, create=action == "request")
        self.lifecycle.assurance(identity)
        fingerprint = hash_data(
            {"renewal_action": action, "tenant": tenant_id, "request": request_id, "body": body}
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
                    "SELECT tenant_id FROM impact.tenant_authority_renewal WHERE request_id=%s AND (%s OR %s IN(owner_identity_id,second_identity_id))",
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
                owner = current_owner(c, tenant)
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
                "UPDATE impact.tenant_authority_renewal SET revision_id=%s,updated_at=now() WHERE request_id=%s",
                (revision, request_id),
            )
            response = {**self.present(self.entry(c, request_id)), "operation_id": body["operation_id"]}
            c.execute(
                "INSERT INTO impact.platform_event(event_id,tenant_id,identity_id,action,revision_id,reason,payload) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                (
                    str(uuid4()),
                    tenant_id,
                    identity.identity_id,
                    "authority-renewal-" + action,
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

    def request(self, c, identity, tenant, data):
        tenant_id = str(tenant["tenant_id"])
        applied = self.applied(c, tenant_id)
        owner_holding = self.holding(c, tenant_id, identity.identity_id)
        if not applied or not owner_holding:
            denied("AUTHORITY_UNAVAILABLE")
        if not all(self.lifecycle.readiness(c, tenant).values()):
            denied("TENANT_NOT_READY")
        second = self.person(c, data["second_identity_id"])
        if str(second["natural_identity_id"]) == identity.natural_identity_id:
            denied("INDEPENDENCE_REQUIRED")
        second_holding = self.holding(c, tenant_id, data["second_identity_id"])
        if not second_holding:
            denied("SECOND_ADMIN_UNAVAILABLE")
        if self.pending(c, tenant_id):
            raise DomainError("CONFLICT_VERSION", 409, reason="RENEWAL_PENDING")
        if self.upgrade_pending(c, tenant_id):
            raise DomainError("CONFLICT_VERSION", 409, reason="ACCESS_UPGRADE_PENDING")
        manifest, rows = self.assemble([owner_holding, second_holding])
        authority_hash = hash_data(manifest).hex()
        if data["authority_hash"] != authority_hash:
            changed()
        previous = max(r["expires_at"] for r in rows)
        expiry = instant(data["expires_at"])
        if not previous < expiry <= now() + timedelta(days=90):
            raise DomainError("VALIDATION_FAILED", reason="GRANT_EXPIRY_BOUNDS")
        owner = current_owner(c, tenant)
        request_id = str(uuid4())
        c.execute(
            "INSERT INTO impact.tenant_authority_renewal(request_id,tenant_id,revision_id,state,bootstrap_request_id,owner_identity_id,second_identity_id,tenant_revision,owner_revision,manifest,authority_hash,previous_expires_at,expires_at,review_expires_at,owner_auth_time,reason) VALUES(%s,%s,%s,'Requested',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                request_id,
                tenant_id,
                str(uuid4()),
                applied["request_id"],
                identity.identity_id,
                data["second_identity_id"],
                tenant["revision_id"],
                owner["head_revision"],
                Jsonb(manifest),
                authority_hash,
                previous,
                expiry,
                min(expiry, now() + timedelta(days=7), min(r["expires_at"] for r in rows)),
                identity.auth_time,
                data["reason"],
            ),
        )
        return request_id

    def recheck(self, c, tenant, row):
        tenant_id = str(tenant["tenant_id"])
        owner = current_owner(c, tenant)
        if (
            tenant["revision_id"] != row["tenant_revision"]
            or owner["head_revision"] != row["owner_revision"]
            or tenant["owner_identity_id"] != row["owner_identity_id"]
        ):
            raise DomainError("CONFLICT_VERSION", 409, reason="RENEWAL_CONTEXT_CHANGED")
        if row["review_expires_at"] <= now() or row["expires_at"] <= now():
            denied("RENEWAL_EXPIRED")
        if not all(self.lifecycle.readiness(c, tenant).values()):
            denied("TENANT_NOT_READY")
        # The recomputed manifest must be byte-identical to the pinned one: a ceiling removed,
        # a grant revoked or a membership ended after the proposal invalidates it, and nothing
        # absent from the pinned manifest is ever recreated.
        applied = self.applied(c, tenant_id)
        manifest, _ = self.manifest_for(
            c, tenant, str(row["owner_identity_id"]), str(row["second_identity_id"])
        )
        if (
            not applied
            or applied["request_id"] != row["bootstrap_request_id"]
            or not manifest
            or hash_data(manifest).hex() != row["authority_hash"]
            or hash_data(row["manifest"]).hex() != row["authority_hash"]
        ):
            changed()
        people = [self.person(c, row[key]) for key in ["owner_identity_id", "second_identity_id"]]
        if people[0]["natural_identity_id"] == people[1]["natural_identity_id"]:
            denied("INDEPENDENCE_REQUIRED")
        for person, auth_time in zip(people, [row["owner_auth_time"], row["second_auth_time"]]):
            if auth_time and person["auth_not_before"] and auth_time <= person["auth_not_before"]:
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
            raise DomainError("CONFLICT_VERSION", 409, reason="INVALID_RENEWAL_TRANSITION")
        if action in {"cancel", "reject"}:
            c.execute(
                "UPDATE impact.tenant_authority_renewal SET state=%s WHERE request_id=%s",
                ("Cancelled" if action == "cancel" else "Rejected", row["request_id"]),
            )
            return
        people = self.recheck(c, tenant, row)
        if action == "accept":
            c.execute(
                "UPDATE impact.tenant_authority_renewal SET state='Accepted',accepted_at=now(),second_auth_time=%s WHERE request_id=%s",
                (identity.auth_time, row["request_id"]),
            )
            return
        if identity.natural_identity_id in {str(p["natural_identity_id"]) for p in people}:
            denied("INDEPENDENCE_REQUIRED")
        self.apply(c, identity, tenant, row)

    def apply(self, c, identity, tenant, row):
        tenant_id, expiry = str(tenant["tenant_id"]), row["expires_at"]
        # Provenance principal for the approving operator; it is not a membership and conveys no access.
        operator_principal = c.execute(
            "INSERT INTO impact.tenant_principal(tenant_id,principal_id,identity_id,principal_kind) VALUES(%s,%s,%s,'HUMAN') ON CONFLICT(tenant_id,identity_id) DO UPDATE SET identity_id=EXCLUDED.identity_id RETURNING principal_id",
            (tenant_id, str(uuid4()), identity.identity_id),
        ).fetchone()
        ctx = Context(tenant_id, str(operator_principal["principal_id"]), "", identity, 0, 0, [])

        def pinned(object_id, kind):
            try:
                record = load(c, ctx, object_id, kind, lock=True)
            except DomainError:
                changed()
            if record["lifecycle_state"] != "Active":
                changed()
            return record

        for entry in row["manifest"]["principals"]:
            for grant_id in entry["grant_ids"]:
                record = pinned(grant_id, "Grant")
                if record["payload"].get("subject_id") != entry["principal_id"]:
                    changed()
                payload = {**record["payload"], "expires_at": expiry.isoformat()}
                write(c, ctx, "Grant", payload, "Active", record, track_author=False)
            if entry["identity_id"] == str(row["second_identity_id"]):
                member = pinned(entry["membership_id"], "Membership")
                current = member["payload"].get("expires_at")
                # The owner membership is custody and stays untouched; the second administrator's
                # membership follows the renewed ceiling and is never shortened.
                if current and instant(current) < expiry:
                    payload = {**member["payload"], "expires_at": expiry.isoformat()}
                    write(c, ctx, "Membership", payload, "Active", member, track_author=False)
            c.execute(
                "UPDATE impact.tenant_principal SET subject_epoch=subject_epoch+1 WHERE tenant_id=%s AND principal_id=%s",
                (tenant_id, entry["principal_id"]),
            )
        c.execute(
            "UPDATE impact.tenant_root SET policy_epoch=policy_epoch+1 WHERE tenant_id=%s", (tenant_id,)
        )
        c.execute(
            "UPDATE impact.tenant_authority_renewal SET state='Applied',approved_by=%s,applied_at=now() WHERE request_id=%s",
            (identity.identity_id, row["request_id"]),
        )
        # Delegation ceilings and role assignment expiry are re-dated only inside the
        # database-owned applicator; the HTTP role holds no UPDATE on either table.
        extended = c.execute(
            "SELECT authorities,assignments FROM impact.apply_authority_renewal(%s)", (row["request_id"],)
        ).fetchone()
        manifest = row["manifest"]
        if extended["authorities"] != len(manifest["authority_ids"]) or extended["assignments"] != sum(
            len(p["assignment_ids"]) for p in manifest["principals"]
        ):
            changed()
