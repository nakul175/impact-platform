"""Versioned roles, independently reviewed groups, units, renewal and custody."""

from datetime import datetime, timedelta
from types import SimpleNamespace
from .clock import now
from .contracts import DELEGABLE_CAPABILITIES
from .domain import DomainError, unavailable
from .store import context, scopes, load, write


def timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def deny(reason):
    raise DomainError("POLICY_DENIED", 403, reason=reason)


def conflict():
    raise DomainError("CONFLICT_VERSION", 409)


class WorkspaceAdministration:
    def __init__(self, administration):
        self.a = administration

    def active(self, c, ctx, obj, kind):
        row = load(c, ctx, obj, kind)
        if row["lifecycle_state"] != "Active":
            raise DomainError("STATE_TRANSITION_DENIED", 409)
        return row

    def member(self, c, ctx, obj, revision=None, allow_expired=False):
        row = self.active(c, ctx, obj, "Membership")
        principal = self.a.principal(c, ctx, row)
        if not principal["active"] or (
            not allow_expired
            and row["payload"].get("expires_at")
            and timestamp(row["payload"]["expires_at"]) <= now()
        ):
            deny("MEMBERSHIP_EXPIRED_OR_INACTIVE")
        if revision and str(row["head_revision"]) != revision:
            conflict()
        return row

    def natural(self, c, ctx, member):
        return str(
            c.execute(
                "SELECT impact.member_natural_identity(%s,%s) AS id",
                (ctx.tenant_id, self.a.principal(c, ctx, member)["principal_id"]),
            ).fetchone()["id"]
        )

    def requester(self, ctx, data):
        return {
            **data,
            "requested_by": ctx.principal_id,
            "requester_identity_id": ctx.identity.identity_id,
            "requester_natural_id": ctx.identity.natural_identity_id,
            "requester_auth_time": ctx.identity.auth_time.isoformat(),
        }

    def review(self, c, ctx, previous, kind, cap, members):
        if previous["object_type"] != kind or previous["lifecycle_state"] != "Requested":
            raise DomainError("STATE_TRANSITION_DENIED", 409)
        p = previous["payload"]
        if ctx.identity.natural_identity_id in {
            p["requester_natural_id"],
            *(self.natural(c, ctx, m) for m in members),
        }:
            deny("INDEPENDENCE_REQUIRED")
        requester = context(
            c,
            SimpleNamespace(
                identity_id=p["requester_identity_id"], auth_time=timestamp(p["requester_auth_time"])
            ),
            ctx.tenant_id,
            write=True,
        )
        if not scopes(c, requester, cap):
            deny("REQUESTER_NO_LONGER_AUTHORIZED")
        self.a.require_tenant_admin_scope(requester, cap)
        return requester

    def decision(self, c, ctx, previous, action, data):
        return write(
            c,
            ctx,
            previous["object_type"],
            {**previous["payload"], "decided_by": ctx.principal_id, "decision_reason": data["reason"]},
            "Applied" if action == "approve" else "Rejected",
            previous,
            track_author=False,
        )

    def command(self, c, ctx, route, previous, action, data):
        if route == "role-templates":
            return self.role(c, ctx, previous, action, data)
        if route == "organisation-units":
            return self.unit(c, ctx, previous, action, data)
        if route == "access-groups":
            return self.group(c, ctx, previous, action, data)
        if route == "group-change-requests":
            return self.group_change(c, ctx, previous, action, data)
        if route == "renewal-requests":
            return self.renewal(c, ctx, previous, action, data)
        if route == "ownership-transfers":
            return self.ownership(c, ctx, previous, action, data)
        unavailable()

    def role(self, c, ctx, previous, action, data):
        if previous and (previous["object_type"] != "RoleTemplate" or not previous["payload"].get("custom")):
            deny("SYSTEM_ROLE_PROTECTED")
        if previous and previous["lifecycle_state"] != "Active":
            raise DomainError("STATE_TRANSITION_DENIED", 409)
        if action == "retire":
            return write(c, ctx, "RoleTemplate", previous["payload"], "Retired", previous, track_author=False)
        name = data["name"].strip()
        if not name:
            raise DomainError("VALIDATION_FAILED")
        duplicate = c.execute(
            "SELECT r.object_id FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_type='RoleTemplate' AND lower(v.payload->>'name')=lower(%s) AND r.lifecycle_state='Active'",
            (ctx.tenant_id, name),
        ).fetchone()
        if duplicate and (not previous or duplicate["object_id"] != previous["object_id"]):
            raise DomainError("CONFLICT_VERSION", 409, reason="ROLE_NAME_EXISTS")
        # Creation conveys no privileges. Every capability must nevertheless be inside
        # the creator's explicit, live operator-provisioned delegation ceiling.
        # Only capabilities of operations this build implements are delegable: a design-only
        # capability in a custom role would be dormant authority that a later build activates.
        caps = sorted(data["capabilities"])
        if set(caps) - DELEGABLE_CAPABILITIES:
            deny("CAPABILITY_NOT_DELEGABLE")
        for cap in caps:
            if not c.execute(
                "SELECT 1 FROM impact.grant_authority WHERE tenant_id=%s AND principal_id=%s AND capability=%s AND expires_at>now()",
                (ctx.tenant_id, ctx.principal_id, cap),
            ).fetchone():
                deny("DELEGATION_NOT_PERMITTED")
        from .administration_contracts import COMMANDS, ADMIN_READS

        admin_caps = {d[1] for d in COMMANDS.values()} | {d[1] for d in ADMIN_READS.values()}
        payload = {
            "managed_by": "impact-access-v1",
            "custom": True,
            "name": name,
            "capabilities": caps,
            "administrative": bool(set(caps) & admin_caps),
        }
        return write(c, ctx, "RoleTemplate", payload, "Active", previous, track_author=False)

    def unit(self, c, ctx, previous, action, data):
        if previous and (
            previous["object_type"] != "OrganisationUnit" or previous["lifecycle_state"] != "Active"
        ):
            unavailable()
        rows = c.execute(
            "SELECT u.* FROM impact.organisation_unit_current u JOIN impact.object_registry r ON r.tenant_id=u.tenant_id AND r.object_id=u.object_id WHERE u.tenant_id=%s AND r.lifecycle_state='Active'",
            (ctx.tenant_id,),
        ).fetchall()
        if not previous and len(rows) >= 1000:
            raise DomainError("LIMIT_EXCEEDED", 422)
        payload = (
            dict(previous["payload"]) if previous else {"code": data["code"], "name": data["name"].strip()}
        )
        if "name" in data:
            payload["name"] = data["name"].strip()
            if not payload["name"]:
                raise DomainError("VALIDATION_FAILED")
        # The projection stores NULL on a root move. Omit parent_id in the domain payload.
        if "parent_id" in data:
            parent = data["parent_id"]
            if parent:
                self.active(c, ctx, parent, "OrganisationUnit")
                payload["parent_id"] = parent
            else:
                payload.pop("parent_id", None)
            tree = {str(r["object_id"]): str(r["parent_id"]) if r["parent_id"] else None for r in rows}
            node = str(previous["object_id"]) if previous else "new"
            tree[node] = parent
            for start in tree:
                path, cursor = set(), start
                while cursor:
                    if cursor in path:
                        raise DomainError("VALIDATION_FAILED", reason="ORGANISATION_CYCLE")
                    path.add(cursor)
                    if len(path) > 20:
                        raise DomainError("LIMIT_EXCEEDED", 422, reason="ORGANISATION_DEPTH")
                    cursor = tree.get(cursor)
        receipt = write(c, ctx, "OrganisationUnit", payload, "Active", previous, track_author=False)
        if not payload.get("parent_id"):
            c.execute(
                "UPDATE impact.organisation_unit_current SET parent_id=NULL WHERE tenant_id=%s AND object_id=%s",
                (ctx.tenant_id, receipt["object_id"]),
            )
        return receipt

    def group(self, c, ctx, previous, action, data):
        if not previous:
            if not data["name"].strip():
                raise DomainError("VALIDATION_FAILED")
            return write(
                c,
                ctx,
                "AccessGroup",
                {"name": data["name"].strip(), "membership_ids": [], "bindings": []},
                "Active",
                track_author=False,
            )
        if previous["object_type"] != "AccessGroup" or previous["lifecycle_state"] != "Active":
            unavailable()
        p = dict(previous["payload"])
        removed = p["membership_ids"] if action == "retire" else [data["membership_id"]]
        if any(m not in p["membership_ids"] for m in removed):
            unavailable()
        c.execute(
            "DELETE FROM impact.group_entitlement WHERE tenant_id=%s AND group_id=%s AND membership_id=ANY(%s::uuid[])",
            (ctx.tenant_id, previous["object_id"], removed),
        )
        p["membership_ids"] = [m for m in p["membership_ids"] if m not in removed]
        for m in removed:
            self.a.bump(c, ctx, self.a.principal(c, ctx, load(c, ctx, m, "Membership"))["principal_id"])
        return write(
            c,
            ctx,
            "AccessGroup",
            p,
            "Retired" if action == "retire" else "Active",
            previous,
            track_author=False,
        )

    def bindings(self, c, ctx, data, members, pinned=False):
        bindings, tuples = [], set()
        for item in data:
            role = self.a.role(
                c, ctx, item["role_template_id"], item.get("role_revision") if pinned else None
            )
            expiry = timestamp(item["expires_at"])
            if expiry > now() + timedelta(days=90):
                raise DomainError("VALIDATION_FAILED", reason="ACCESS_EXPIRY_LIMIT")
            self.a.delegation(c, ctx, role["payload"]["capabilities"], item["scope_ids"], expiry)
            if role["payload"]["administrative"]:
                for scope in item["scope_ids"]:
                    if (
                        c.execute(
                            "SELECT scope_type FROM impact.scope_definition WHERE tenant_id=%s AND scope_id=%s",
                            (ctx.tenant_id, scope),
                        ).fetchone()["scope_type"]
                        != "TENANT"
                    ):
                        deny("TENANT_ADMIN_SCOPE_REQUIRED")
            for m in members:
                if m["payload"].get("expires_at") and expiry > timestamp(m["payload"]["expires_at"]):
                    deny("MEMBERSHIP_EXPIRY_EXCEEDED")
            for scope in item["scope_ids"]:
                for cap in role["payload"]["capabilities"]:
                    key = (scope, cap)
                    if key in tuples:
                        raise DomainError("VALIDATION_FAILED", reason="DUPLICATE_GROUP_ENTITLEMENT")
                    tuples.add(key)
            bindings.append(
                {
                    **item,
                    "role_revision": str(role["head_revision"]),
                    "role_name": role["payload"]["name"],
                    "capabilities": role["payload"]["capabilities"],
                }
            )
        if len(tuples) > 500:
            raise DomainError("LIMIT_EXCEEDED", 422, reason="GROUP_GRANT_LIMIT")
        if len(tuples) * len(members) > 2000:
            raise DomainError("LIMIT_EXCEEDED", 422, reason="GROUP_ENTITLEMENT_LIMIT")
        return bindings

    def group_change(self, c, ctx, previous, action, data):
        if not previous:
            group = self.active(c, ctx, data["group_id"], "AccessGroup")
            if str(group["head_revision"]) != data["expected_group_revision"]:
                conflict()
            members = [self.member(c, ctx, m) for m in data["membership_ids"]]
            bindings = self.bindings(c, ctx, data["bindings"], members)
            return write(
                c,
                ctx,
                "GroupChangeRequest",
                self.requester(
                    ctx,
                    {
                        **data,
                        "bindings": bindings,
                        "member_revisions": {str(m["object_id"]): str(m["head_revision"]) for m in members},
                    },
                ),
                "Requested",
                track_author=False,
            )
        p = previous["payload"]
        if previous["object_type"] != "GroupChangeRequest":
            unavailable()
        members = [load(c, ctx, m, "Membership") for m in p["membership_ids"]]
        requester = self.review(c, ctx, previous, "GroupChangeRequest", "groups.request", members)
        if action == "reject":
            return self.decision(c, ctx, previous, action, data)
        group = self.active(c, ctx, p["group_id"], "AccessGroup")
        if str(group["head_revision"]) != p["expected_group_revision"]:
            conflict()
        members = [self.member(c, ctx, m, rev) for m, rev in p["member_revisions"].items()]
        bindings = self.bindings(c, ctx, p["bindings"], members, True)
        self.bindings(c, requester, p["bindings"], members, True)
        c.execute(
            "DELETE FROM impact.group_entitlement WHERE tenant_id=%s AND group_id=%s",
            (ctx.tenant_id, group["object_id"]),
        )
        for m in members:
            added = sum(len(b["scope_ids"]) * len(b["capabilities"]) for b in bindings)
            principal = self.a.principal(c, ctx, m)
            direct = c.execute(
                "SELECT count(*) AS n FROM impact.grant_current g JOIN impact.object_registry r ON r.tenant_id=g.tenant_id AND r.object_id=g.object_id WHERE g.tenant_id=%s AND g.subject_id=%s AND r.lifecycle_state='Active' AND (g.expires_at IS NULL OR g.expires_at>now())",
                (ctx.tenant_id, principal["principal_id"]),
            ).fetchone()["n"]
            derived = c.execute(
                "SELECT count(*) AS n FROM impact.group_entitlement WHERE tenant_id=%s AND membership_id=%s AND expires_at>now()",
                (ctx.tenant_id, m["object_id"]),
            ).fetchone()["n"]
            if direct + derived + added > 500:
                raise DomainError("LIMIT_EXCEEDED", 422, reason="MEMBER_GRANT_LIMIT")
            for b in bindings:
                for scope in b["scope_ids"]:
                    for cap in b["capabilities"]:
                        c.execute(
                            "INSERT INTO impact.group_entitlement VALUES(%s,%s,%s,%s,%s,%s)",
                            (ctx.tenant_id, group["object_id"], m["object_id"], cap, scope, b["expires_at"]),
                        )
        for member_id in set(group["payload"]["membership_ids"]) | set(p["membership_ids"]):
            self.a.bump(
                c, ctx, self.a.principal(c, ctx, load(c, ctx, member_id, "Membership"))["principal_id"]
            )
        write(
            c,
            ctx,
            "AccessGroup",
            {**group["payload"], "membership_ids": p["membership_ids"], "bindings": bindings},
            "Active",
            group,
            track_author=False,
        )
        return self.decision(c, ctx, previous, action, data)

    def renewal(self, c, ctx, previous, action, data):
        if not previous:
            m = self.member(c, ctx, data["membership_id"], data["expected_membership_revision"], True)
            self.a.protect_owner(c, ctx, m)
            expiry = timestamp(data["expires_at"])
            if not now() < expiry <= now() + timedelta(days=90) or (
                m["payload"].get("expires_at") and expiry <= timestamp(m["payload"]["expires_at"])
            ):
                raise DomainError("VALIDATION_FAILED", reason="RENEWAL_EXPIRY_INVALID")
            return write(
                c, ctx, "MembershipRenewal", self.requester(ctx, data), "Requested", track_author=False
            )
        if previous["object_type"] != "MembershipRenewal":
            unavailable()
        p = previous["payload"]
        m = load(c, ctx, p["membership_id"], "Membership")
        self.review(c, ctx, previous, "MembershipRenewal", "membership.renew.request", [m])
        if action == "reject":
            return self.decision(c, ctx, previous, action, data)
        m = self.member(c, ctx, p["membership_id"], p["expected_membership_revision"], True)
        self.a.protect_owner(c, ctx, m)
        if timestamp(p["expires_at"]) <= now():
            raise DomainError("STATE_TRANSITION_DENIED", 409)
        principal = self.a.principal(c, ctx, m)
        # Renewal deliberately requires a fresh access review. Expired grants, old
        # group memberships, and old sessions can never spring back into service.
        grants = c.execute(
            "SELECT g.object_id FROM impact.grant_current g JOIN impact.object_registry r ON r.tenant_id=g.tenant_id AND r.object_id=g.object_id WHERE g.tenant_id=%s AND g.subject_id=%s AND r.lifecycle_state='Active'",
            (ctx.tenant_id, principal["principal_id"]),
        ).fetchall()
        for grant in grants:
            old = load(c, ctx, grant["object_id"], "Grant")
            write(c, ctx, "Grant", old["payload"], "Revoked", old, track_author=False)
        groups = c.execute(
            "SELECT DISTINCT group_id FROM impact.group_entitlement WHERE tenant_id=%s AND membership_id=%s",
            (ctx.tenant_id, m["object_id"]),
        ).fetchall()
        for group in groups:
            old = load(c, ctx, group["group_id"], "AccessGroup")
            self.group(c, ctx, old, "remove-member", {"membership_id": str(m["object_id"])})
        c.execute(
            "UPDATE impact.tenant_principal SET auth_not_before=now() WHERE tenant_id=%s AND principal_id=%s",
            (ctx.tenant_id, principal["principal_id"]),
        )
        self.a.bump(c, ctx, principal["principal_id"])
        write(
            c,
            ctx,
            "Membership",
            {**m["payload"], "expires_at": p["expires_at"]},
            "Active",
            m,
            track_author=False,
        )
        return self.decision(c, ctx, previous, action, data)

    def ownership(self, c, ctx, previous, action, data):
        custody = c.execute(
            "SELECT owner_membership_id FROM impact.tenant_custody WHERE tenant_id=%s", (ctx.tenant_id,)
        ).fetchone()
        if not custody:
            deny("CUSTODY_NOT_CONFIGURED")
        owner = str(custody["owner_membership_id"])
        if not previous:
            if ctx.membership_id != owner:
                deny("CURRENT_OWNER_REQUIRED")
            m = self.member(c, ctx, data["membership_id"], data["expected_membership_revision"])
            if self.natural(c, ctx, m) == ctx.identity.natural_identity_id:
                deny("INDEPENDENCE_REQUIRED")
            # Custody does not create grants or delegation. The successor must already
            # be an eligible administrator through a separately governed assignment.
            successor = self.a.principal(c, ctx, m)
            eligible = context(
                c, SimpleNamespace(identity_id=m["payload"]["identity_id"], auth_time=now()), ctx.tenant_id
            )
            self.a.require_tenant_admin_scope(eligible, "ownership.transfer")
            if not c.execute(
                "SELECT 1 FROM impact.grant_authority WHERE tenant_id=%s AND principal_id=%s AND expires_at>now()",
                (ctx.tenant_id, successor["principal_id"]),
            ).fetchone():
                deny("SUCCESSOR_DELEGATION_REQUIRED")
            return write(
                c,
                ctx,
                "CustodyTransfer",
                self.requester(
                    ctx,
                    {
                        **data,
                        "owner_membership_id": owner,
                        "expires_at": (now() + timedelta(days=7)).isoformat(),
                    },
                ),
                "Requested",
                track_author=False,
            )
        if previous["object_type"] != "CustodyTransfer" or previous["lifecycle_state"] != "Requested":
            raise DomainError("STATE_TRANSITION_DENIED", 409)
        p = previous["payload"]
        if owner != p["owner_membership_id"]:
            conflict()
        if action == "cancel":
            if ctx.membership_id != owner:
                deny("CURRENT_OWNER_REQUIRED")
            return write(
                c,
                ctx,
                "CustodyTransfer",
                {**p, "decision_reason": data["reason"], "decided_by": ctx.principal_id},
                "Cancelled",
                previous,
                track_author=False,
            )
        if ctx.membership_id != p["membership_id"]:
            deny("NOMINATED_SUCCESSOR_REQUIRED")
        self.member(c, ctx, p["membership_id"], p["expected_membership_revision"])
        self.member(c, ctx, owner)
        if timestamp(p["expires_at"]) <= now():
            raise DomainError("STATE_TRANSITION_DENIED", 409, reason="TRANSFER_EXPIRED")
        c.execute(
            "SELECT impact.accept_custody(%s,%s,%s)", (ctx.tenant_id, previous["object_id"], ctx.principal_id)
        )
        tenant_record = c.execute(
            "SELECT object_id FROM impact.tenant_current WHERE tenant_id=%s", (ctx.tenant_id,)
        ).fetchone()
        if tenant_record:
            old_tenant = load(c, ctx, tenant_record["object_id"], "Tenant")
            write(
                c,
                ctx,
                "Tenant",
                {**old_tenant["payload"], "owner_membership_id": ctx.membership_id},
                old_tenant["lifecycle_state"],
                old_tenant,
                track_author=False,
            )
        self.a.bump(c, ctx, ctx.principal_id)
        return write(
            c,
            ctx,
            "CustodyTransfer",
            {**p, "decided_by": ctx.principal_id, "decision_reason": data["reason"]},
            "Applied",
            previous,
            track_author=False,
        )

    def list_item(self, route, common, data):
        fields = {
            "access-groups": ["name", "membership_ids", "bindings"],
            "organisation-units": ["code", "name", "parent_id"],
            "renewal-requests": ["membership_id", "expires_at", "requested_by", "reason"],
            "ownership-transfers": [
                "membership_id",
                "owner_membership_id",
                "expires_at",
                "requested_by",
                "reason",
            ],
            "group-change-requests": ["group_id", "membership_ids", "requested_by", "reason", "bindings"],
        }[route]
        item = {**common, **{k: data.get(k) for k in fields}}
        if route == "group-change-requests":
            item["role_names"] = [b["role_name"] for b in data["bindings"]]
        return item
