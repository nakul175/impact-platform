"""Tenant administration with explicit delegation ceilings and independent access decisions."""

import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4
from psycopg.types.json import Jsonb
from .administration_contracts import ADMIN_READS, COMMANDS
from .contracts import validate
from .domain import DomainError, unavailable
from .delivery import enqueue, invitation_token, invitation_url, seal_recipient
from .identity_profile import email_hash, masked_email
from .store import context, authorize, scopes, load, write, audit, hash_data
from .workspace_contracts import COMMANDS as WORKSPACE_COMMANDS, KINDS as WORKSPACE_KINDS
from .workspace_administration import WorkspaceAdministration


def now():
    return datetime.now(timezone.utc)


def timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def deny(reason="DELEGATION_NOT_PERMITTED"):
    raise DomainError("POLICY_DENIED", 403, reason=reason)


class Administration:
    def __init__(self, s, db, service):
        self.s, self.db, self.service = s, db, service
        self.workspace = WorkspaceAdministration(self)

    def role(self, c, ctx, object_id, revision_id=None):
        row = load(c, ctx, object_id, "RoleTemplate")
        if row["lifecycle_state"] != "Active" or row["payload"].get("managed_by") != "impact-access-v1":
            unavailable()
        if revision_id and str(row["head_revision"]) != revision_id:
            raise DomainError("CONFLICT_VERSION", 409)
        return row

    def delegation(self, c, ctx, capabilities, scope_ids, expiry):
        if not scope_ids or len(set(scope_ids)) != len(scope_ids) or expiry <= now():
            deny()
        target_scopes = []
        for scope_id in scope_ids:
            row = c.execute(
                "SELECT * FROM impact.scope_definition WHERE tenant_id=%s AND scope_id=%s",
                (ctx.tenant_id, scope_id),
            ).fetchone()
            if not row:
                unavailable()
            target_scopes.append(row)
        authorities = c.execute(
            "SELECT a.*,s.scope_type FROM impact.grant_authority a JOIN impact.scope_definition s ON s.tenant_id=a.tenant_id AND s.scope_id=a.scope_id WHERE a.tenant_id=%s AND a.principal_id=%s AND a.expires_at>=%s",
            (ctx.tenant_id, ctx.principal_id, expiry),
        ).fetchall()
        for capability in capabilities:
            for target in target_scopes:
                allowed = False
                for authority in authorities:
                    if authority["capability"] != capability:
                        continue
                    if authority["scope_type"] == "TENANT" or authority["scope_id"] == target["scope_id"]:
                        allowed = True
                        break
                    if target["scope_type"] == "TENANT":
                        continue
                    count = c.execute(
                        "SELECT count(*) AS n FROM impact.scope_member WHERE tenant_id=%s AND scope_id=%s",
                        (ctx.tenant_id, target["scope_id"]),
                    ).fetchone()["n"]
                    outside = c.execute(
                        "SELECT 1 FROM impact.scope_member target WHERE target.tenant_id=%s AND target.scope_id=%s AND NOT EXISTS(SELECT 1 FROM impact.scope_member allowed WHERE allowed.tenant_id=target.tenant_id AND allowed.scope_id=%s AND allowed.object_id=target.object_id) LIMIT 1",
                        (ctx.tenant_id, target["scope_id"], authority["scope_id"]),
                    ).fetchone()
                    if count and not outside:
                        allowed = True
                        break
                if not allowed:
                    deny()

    def require_tenant_admin_scope(self, ctx, cap):
        if not any(
            g["capability"] == cap and g["scope_type"] == "TENANT" and g["purpose"] is None
            for g in ctx.grants
        ):
            deny("TENANT_ADMIN_SCOPE_REQUIRED")

    def principal(self, c, ctx, membership):
        row = c.execute(
            "SELECT * FROM impact.tenant_principal WHERE tenant_id=%s AND identity_id=%s",
            (ctx.tenant_id, membership["payload"]["identity_id"]),
        ).fetchone()
        if not row:
            unavailable()
        return row

    def protect_owner(self, c, ctx, membership):
        owner = c.execute(
            "SELECT owner_membership_id FROM impact.tenant_custody WHERE tenant_id=%s", (ctx.tenant_id,)
        ).fetchone()
        if not owner:
            deny("CUSTODY_NOT_CONFIGURED")
        if str(owner["owner_membership_id"]) == str(membership["object_id"]):
            deny("LAST_OWNER_PROTECTED")

    def bump(self, c, ctx, principal_id):
        c.execute(
            "UPDATE impact.tenant_root SET policy_epoch=policy_epoch+1 WHERE tenant_id=%s", (ctx.tenant_id,)
        )
        c.execute(
            "UPDATE impact.tenant_principal SET subject_epoch=subject_epoch+1 WHERE tenant_id=%s AND principal_id=%s",
            (ctx.tenant_id, principal_id),
        )

    def issue_role(self, c, ctx, member, role, scope_ids, expiry, issuer_id):
        principal = self.principal(c, ctx, member)
        existing = c.execute(
            "SELECT count(*) AS n FROM impact.grant_current g JOIN impact.object_registry r ON r.tenant_id=g.tenant_id AND r.object_id=g.object_id WHERE g.tenant_id=%s AND g.subject_id=%s AND r.lifecycle_state='Active' AND (g.expires_at IS NULL OR g.expires_at>now())",
            (ctx.tenant_id, principal["principal_id"]),
        ).fetchone()["n"]
        existing += c.execute(
            "SELECT count(*) AS n FROM impact.group_entitlement WHERE tenant_id=%s AND membership_id=%s AND expires_at>now()",
            (ctx.tenant_id, member["object_id"]),
        ).fetchone()["n"]
        if existing + len(role["payload"]["capabilities"]) * len(scope_ids) > 500:
            raise DomainError("LIMIT_EXCEEDED", 422, reason="MEMBER_GRANT_LIMIT")
        if member["payload"].get("expires_at") and expiry > timestamp(member["payload"]["expires_at"]):
            deny("MEMBERSHIP_EXPIRY_EXCEEDED")
        for scope_id in scope_ids:
            grant_ids = []
            for capability in role["payload"]["capabilities"]:
                data = {
                    "subject_id": str(principal["principal_id"]),
                    "capability": capability,
                    "scope_id": scope_id,
                    "starts_at": now().isoformat(),
                    "expires_at": expiry.isoformat(),
                    "issuer_id": issuer_id,
                }
                grant_ids.append(write(c, ctx, "Grant", data, "Active", track_author=False)["object_id"])
            c.execute(
                "INSERT INTO impact.member_role_assignment VALUES(%s,%s,%s,%s,%s,%s,%s,%s::uuid[])",
                (
                    ctx.tenant_id,
                    str(uuid4()),
                    member["object_id"],
                    role["object_id"],
                    role["head_revision"],
                    scope_id,
                    expiry,
                    grant_ids,
                ),
            )
        self.bump(c, ctx, principal["principal_id"])

    def invitation_token(self, tenant, invitation, generation):
        return invitation_token(
            self.s.invitation_secret or self.s.cookie_secret, tenant, invitation, generation
        )

    def present_receipt(self, tenant, receipt):
        result = dict(receipt)
        if receipt.get("invitation_generation"):
            token = self.invitation_token(tenant, receipt["object_id"], receipt["invitation_generation"])
            result["invitation_url"] = invitation_url(self.s.public_origin, tenant, token)
        return result

    def email_invitation(self, c, ctx, invitation_id, generation, address=None):
        """Record an email delivery intent for the current generation (v0.16). The outbox row holds
        the invitation and generation only; the worker re-derives the link and rechecks that this
        generation is still current and unconsumed before sending. On resend the address sealed for
        the invitation's first intent is reused, since only its hash is kept elsewhere; an
        invitation created before v0.16, or with no delivery secret configured, stays manual-only."""
        if not self.s.delivery_secret:
            return None
        if address is not None:
            sealed = seal_recipient(
                self.s.delivery_secret, ctx.tenant_id, "MEMBER_INVITATION", invitation_id, address
            )
        else:
            row = c.execute(
                "SELECT recipient_sealed FROM impact.outbox_delivery WHERE tenant_id=%s AND reference_id=%s "
                "AND template='MEMBER_INVITATION' ORDER BY last_attempt_at NULLS LAST LIMIT 1",
                (ctx.tenant_id, invitation_id),
            ).fetchone()
            if not row:
                return None
            sealed = bytes(row["recipient_sealed"])
        return enqueue(c, ctx.tenant_id, "MEMBER_INVITATION", invitation_id, generation, sealed)

    def receipt_row(self, c, ctx, operation, body, fingerprint):
        existing = c.execute(
            "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type=%s AND operation_id=%s",
            (ctx.tenant_id, ctx.principal_id, operation, body["operation_id"]),
        ).fetchone()
        if not existing:
            return None
        if bytes(existing["payload_hash"]) != fingerprint:
            raise DomainError("CONFLICT_OPERATION", 409)
        if existing["expires_at"] <= now():
            raise DomainError("IDEMPOTENCY_EXPIRED", 409)
        load(c, ctx, existing["outcome"]["object_id"])
        return existing["outcome"]

    def record(self, c, ctx, operation, body, fingerprint, receipt, correlation):
        receipt.update(operation_id=body["operation_id"], correlation_id=correlation)
        audit(c, ctx, operation, receipt, correlation)
        if body["data"].get("reason"):
            c.execute(
                "INSERT INTO impact.admin_reason VALUES(%s,%s,%s)",
                (ctx.tenant_id, receipt["revision_id"], body["data"]["reason"].strip()),
            )
        c.execute(
            "INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,'SUCCEEDED',%s,%s)",
            (
                ctx.tenant_id,
                ctx.principal_id,
                operation,
                body["operation_id"],
                fingerprint,
                Jsonb(receipt),
                now() + timedelta(days=7),
            ),
        )
        return self.present_receipt(ctx.tenant_id, receipt)

    def command(self, identity, tenant, route, body, correlation, obj=None, action=None):
        definition = COMMANDS.get((route, action))
        if not definition:
            unavailable()
        operation, cap, schema, expected, _ = definition
        validate(schema, body)
        if body["data"].get("reason") is not None and not body["data"]["reason"].strip():
            raise DomainError("VALIDATION_FAILED", reason="REASON_REQUIRED")
        fingerprint = hash_data([operation, obj, body])
        with self.db.transaction(tenant) as c:
            # Same first lock as all domain commands; revocation cannot be passed by a waiting write.
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            if route == "invitation-acceptances":
                return self.accept(c, identity, tenant, body, fingerprint, correlation)
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, operation, obj)
            self.require_tenant_admin_scope(ctx, cap)
            old = self.receipt_row(c, ctx, operation, body, fingerprint)
            if old:
                return self.present_receipt(tenant, old)
            previous = load(c, ctx, obj, lock=True) if obj else None
            if expected and (not previous or str(previous["head_revision"]) != body["expected_revision"]):
                raise DomainError("CONFLICT_VERSION", 409)
            if (route, action) in WORKSPACE_COMMANDS:
                result = self.workspace.command(c, ctx, route, previous, action, body["data"])
            elif route == "memberships":
                result = self.lifecycle(c, ctx, previous, action, body["data"])
            elif route == "grants":
                result = self.revoke_grant(c, ctx, previous)
            elif route == "member-invitations":
                result = self.invitation(c, ctx, previous, action, body["data"])
            elif route == "access-scopes":
                result = self.create_scope(c, ctx, body["data"])
            elif route == "access-requests":
                result = self.access_request(c, ctx, previous, action, body["data"])
            else:
                unavailable()
            return self.record(c, ctx, operation, body, fingerprint, result, correlation)

    def lifecycle(self, c, ctx, member, action, data):
        if member["object_type"] != "Membership":
            unavailable()
        self.protect_owner(c, ctx, member)
        allowed = {"suspend": {"Active"}, "reactivate": {"Suspended"}, "revoke": {"Active", "Suspended"}}
        if member["lifecycle_state"] not in allowed[action]:
            raise DomainError("STATE_TRANSITION_DENIED", 409)
        payload = dict(member["payload"])
        principal = self.principal(c, ctx, member)
        if action == "reactivate" and payload.get("expires_at") and timestamp(payload["expires_at"]) <= now():
            raise DomainError("STATE_TRANSITION_DENIED", 409, reason="MEMBERSHIP_EXPIRED")
        state = {"suspend": "Suspended", "reactivate": "Active", "revoke": "Revoked"}[action]
        payload["status"] = state
        c.execute(
            "UPDATE impact.tenant_principal SET active=%s WHERE tenant_id=%s AND principal_id=%s",
            (action == "reactivate", ctx.tenant_id, principal["principal_id"]),
        )
        if action != "reactivate":
            c.execute(
                "UPDATE impact.tenant_principal SET auth_not_before=%s WHERE tenant_id=%s AND principal_id=%s",
                (now(), ctx.tenant_id, principal["principal_id"]),
            )
            invitations = c.execute(
                "SELECT invitation_id FROM impact.member_invitation WHERE tenant_id=%s AND inviter_id=%s AND consumed_at IS NULL AND revoked_at IS NULL",
                (ctx.tenant_id, principal["principal_id"]),
            ).fetchall()
            for invitation in invitations:
                item = load(c, ctx, invitation["invitation_id"], "EntitlementApproval", lock=True)
                write(c, ctx, "EntitlementApproval", item["payload"], "Revoked", item, track_author=False)
            c.execute(
                "UPDATE impact.member_invitation SET revoked_at=%s WHERE tenant_id=%s AND inviter_id=%s AND consumed_at IS NULL AND revoked_at IS NULL",
                (now(), ctx.tenant_id, principal["principal_id"]),
            )
            c.execute(
                "UPDATE impact.job SET cancellation_requested_at=%s,state=CASE WHEN state IN ('Requested','Validating','Queued') THEN 'Cancelled' ELSE state END WHERE tenant_id=%s AND requester_id=%s AND state NOT IN ('Succeeded','SucceededWithIssues','Failed','Cancelled')",
                (now(), ctx.tenant_id, principal["principal_id"]),
            )
            schedules = c.execute(
                "SELECT object_id FROM impact.object_registry WHERE tenant_id=%s AND object_type='Schedule' AND owner_id=%s AND lifecycle_state='Active'",
                (ctx.tenant_id, principal["principal_id"]),
            ).fetchall()
            for schedule in schedules:
                item = load(c, ctx, schedule["object_id"], "Schedule", lock=True)
                write(c, ctx, "Schedule", item["payload"], "Paused", item, track_author=False)
        if action == "revoke":
            grants = c.execute(
                "SELECT g.object_id FROM impact.grant_current g JOIN impact.object_registry r ON r.tenant_id=g.tenant_id AND r.object_id=g.object_id WHERE g.tenant_id=%s AND g.subject_id=%s AND r.lifecycle_state='Active'",
                (ctx.tenant_id, principal["principal_id"]),
            ).fetchall()
            for grant in grants:
                item = load(c, ctx, grant["object_id"], "Grant", lock=True)
                write(c, ctx, "Grant", item["payload"], "Revoked", item, track_author=False)
        self.bump(c, ctx, principal["principal_id"])
        return write(c, ctx, "Membership", payload, state, member, track_author=False)

    def revoke_grant(self, c, ctx, grant):
        if grant["object_type"] != "Grant":
            unavailable()
        if grant["lifecycle_state"] != "Active":
            raise DomainError("STATE_TRANSITION_DENIED", 409)
        target = c.execute(
            "SELECT m.object_id FROM impact.membership_current m JOIN impact.tenant_principal p ON p.tenant_id=m.tenant_id AND p.identity_id=m.identity_id WHERE p.tenant_id=%s AND p.principal_id=%s",
            (ctx.tenant_id, grant["payload"]["subject_id"]),
        ).fetchone()
        if not target:
            unavailable()
        self.protect_owner(c, ctx, load(c, ctx, target["object_id"], "Membership"))
        self.bump(c, ctx, grant["payload"]["subject_id"])
        return write(c, ctx, "Grant", grant["payload"], "Revoked", grant, track_author=False)

    def invitation(self, c, ctx, row, action, data):
        if row:
            if (
                row["object_type"] != "EntitlementApproval"
                or row["payload"].get("kind") != "MEMBER_INVITATION"
            ):
                unavailable()
            current = c.execute(
                "SELECT * FROM impact.member_invitation WHERE tenant_id=%s AND invitation_id=%s FOR UPDATE",
                (ctx.tenant_id, row["object_id"]),
            ).fetchone()
            if not current or current["consumed_at"] or current["revoked_at"]:
                raise DomainError("STATE_TRANSITION_DENIED", 409)
            if action == "revoke":
                c.execute(
                    "UPDATE impact.member_invitation SET revoked_at=%s WHERE tenant_id=%s AND invitation_id=%s",
                    (now(), ctx.tenant_id, row["object_id"]),
                )
                return write(
                    c, ctx, "EntitlementApproval", row["payload"], "Revoked", row, track_author=False
                )
            role = self.role(c, ctx, current["role_template_id"], str(current["role_revision"]))
            expiry = current["membership_expires_at"]
            scope_ids = [str(x) for x in current["scope_ids"]]
            self.delegation(c, ctx, role["payload"]["capabilities"], scope_ids, expiry)
            generation = str(uuid4())
            expires = min(now() + timedelta(days=7), expiry)
            if expires <= now():
                raise DomainError("STATE_TRANSITION_DENIED", 409, reason="MEMBERSHIP_EXPIRED")
            token = self.invitation_token(ctx.tenant_id, str(row["object_id"]), generation)
            payload = {
                **row["payload"],
                "expires_at": expires.isoformat(),
                "inviter_id": ctx.principal_id,
                "inviter_identity_id": ctx.identity.identity_id,
                "inviter_auth_time": ctx.identity.auth_time.isoformat(),
            }
            c.execute(
                "UPDATE impact.member_invitation SET token_hash=%s,generation=%s,expires_at=%s,inviter_id=%s WHERE tenant_id=%s AND invitation_id=%s",
                (
                    hashlib.sha256(token.encode()).digest(),
                    generation,
                    expires,
                    ctx.principal_id,
                    ctx.tenant_id,
                    row["object_id"],
                ),
            )
            receipt = write(c, ctx, "EntitlementApproval", payload, "Invited", row, track_author=False)
            self.email_invitation(c, ctx, str(row["object_id"]), generation)
        else:
            expiry = timestamp(data["membership_expires_at"])
            expires = timestamp(data["expires_at"])
            if not now() < expires <= now() + timedelta(days=7) or not expires <= expiry <= now() + timedelta(
                days=90
            ):
                raise DomainError("VALIDATION_FAILED", reason="INVITATION_EXPIRY_BOUNDS")
            role = self.role(c, ctx, data["role_template_id"])
            if role["payload"]["administrative"]:
                deny("ADMIN_ROLE_REQUIRES_INDEPENDENT_APPROVAL")
            scope_ids = data["scope_ids"]
            self.delegation(c, ctx, role["payload"]["capabilities"], scope_ids, expiry)
            digest = email_hash(data["email"])
            pending = c.execute(
                "SELECT invitation_id,expires_at FROM impact.member_invitation WHERE tenant_id=%s AND intended_email_hash=%s AND consumed_at IS NULL AND revoked_at IS NULL",
                (ctx.tenant_id, digest),
            ).fetchone()
            if pending:
                if pending["expires_at"] > now():
                    raise DomainError("CONFLICT_OPERATION", 409, reason="INVITATION_ALREADY_PENDING")
                old = load(c, ctx, pending["invitation_id"], "EntitlementApproval", lock=True)
                write(c, ctx, "EntitlementApproval", old["payload"], "Expired", old, track_author=False)
                c.execute(
                    "UPDATE impact.member_invitation SET revoked_at=%s WHERE tenant_id=%s AND invitation_id=%s",
                    (now(), ctx.tenant_id, pending["invitation_id"]),
                )
            obj = str(uuid4())
            generation = str(uuid4())
            token = self.invitation_token(ctx.tenant_id, obj, generation)
            payload = {
                "kind": "MEMBER_INVITATION",
                "email_mask": masked_email(data["email"]),
                "role_template_id": str(role["object_id"]),
                "role_revision": str(role["head_revision"]),
                "role_name": role["payload"]["name"],
                "scope_ids": scope_ids,
                "expires_at": expires.isoformat(),
                "membership_expires_at": expiry.isoformat(),
                "inviter_id": ctx.principal_id,
                "inviter_identity_id": ctx.identity.identity_id,
                "inviter_auth_time": ctx.identity.auth_time.isoformat(),
            }
            receipt = write(
                c, ctx, "EntitlementApproval", payload, "Invited", object_id=obj, track_author=False
            )
            c.execute(
                "INSERT INTO impact.member_invitation(tenant_id,invitation_id,token_hash,intended_issuer,intended_email_hash,inviter_id,role_template_id,scope_ids,expires_at,generation,membership_expires_at,external,role_revision) VALUES(%s,%s,%s,%s,%s,%s,%s,%s::uuid[],%s,%s,%s,true,%s)",
                (
                    ctx.tenant_id,
                    obj,
                    hashlib.sha256(token.encode()).digest(),
                    self.s.issuer,
                    digest,
                    ctx.principal_id,
                    role["object_id"],
                    scope_ids,
                    expires,
                    generation,
                    expiry,
                    role["head_revision"],
                ),
            )
            self.email_invitation(c, ctx, obj, generation, data["email"])
        receipt["invitation_generation"] = generation
        return receipt

    def accept(self, c, identity, tenant, body, fingerprint, correlation):
        token = body["data"]["invitation_token"]
        invitation = c.execute(
            "SELECT * FROM impact.member_invitation WHERE tenant_id=%s AND token_hash=%s FOR UPDATE",
            (tenant, hashlib.sha256(token.encode()).digest()),
        ).fetchone()
        if (
            not invitation
            or not identity.verified_email_hash
            or invitation["revoked_at"]
            or invitation["expires_at"] <= now()
            or not hmac.compare_digest(bytes(invitation["intended_email_hash"]), identity.verified_email_hash)
        ):
            raise DomainError("INVITATION_UNAVAILABLE", 410)
        if invitation["intended_issuer"] != self.s.issuer or (
            invitation["intended_subject"] and invitation["intended_subject"] != identity.subject
        ):
            raise DomainError("INVITATION_UNAVAILABLE", 410)
        invitation_row = c.execute(
            "SELECT payload FROM impact.object_revision WHERE tenant_id=%s AND revision_id=(SELECT head_revision FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s)",
            (tenant, tenant, invitation["invitation_id"]),
        ).fetchone()
        if not invitation_row:
            raise DomainError("INVITATION_UNAVAILABLE", 410)
        payload = invitation_row["payload"]
        inviter_identity = SimpleNamespace(
            identity_id=payload["inviter_identity_id"], auth_time=timestamp(payload["inviter_auth_time"])
        )
        inviter = context(c, inviter_identity, tenant, write=True)
        if not scopes(c, inviter, "member.invite"):
            deny("INVITER_NO_LONGER_AUTHORIZED")
        role = self.role(c, inviter, invitation["role_template_id"], str(invitation["role_revision"]))
        scope_ids = [str(x) for x in invitation["scope_ids"]]
        self.delegation(
            c, inviter, role["payload"]["capabilities"], scope_ids, invitation["membership_expires_at"]
        )
        if invitation["consumed_at"]:
            ctx = context(c, identity, tenant, write=True)
            old = self.receipt_row(c, ctx, "accept_invitation", body, fingerprint)
            if old:
                return old
            raise DomainError("INVITATION_UNAVAILABLE", 410)
        if c.execute(
            "SELECT 1 FROM impact.tenant_principal WHERE tenant_id=%s AND identity_id=%s",
            (tenant, identity.identity_id),
        ).fetchone():
            raise DomainError("INVITATION_UNAVAILABLE", 410)
        principal_id = str(uuid4())
        membership_id = str(uuid4())
        c.execute(
            "INSERT INTO impact.tenant_principal(tenant_id,principal_id,identity_id,principal_kind) VALUES(%s,%s,%s,'HUMAN')",
            (tenant, principal_id, identity.identity_id),
        )
        from .store import Context

        ctx = Context(tenant, principal_id, membership_id, identity, inviter.policy_epoch, 0, [])
        receipt = write(
            c,
            ctx,
            "Membership",
            {
                "identity_id": identity.identity_id,
                "authority_source": "VERIFIED_INVITATION",
                "external": True,
                "expires_at": invitation["membership_expires_at"].isoformat(),
                "status": "Active",
                "joined_at": now().isoformat(),
            },
            "Active",
            object_id=membership_id,
            track_author=False,
        )
        c.execute(
            "INSERT INTO impact.member_profile VALUES(%s,%s,%s,%s)",
            (tenant, membership_id, identity.display_name or "Member", identity.email_mask),
        )
        member = load(c, ctx, membership_id, "Membership")
        self.issue_role(
            c,
            ctx,
            member,
            role,
            scope_ids,
            invitation["membership_expires_at"],
            str(invitation["inviter_id"]),
        )
        invite = load(c, ctx, invitation["invitation_id"], "EntitlementApproval", lock=True)
        write(c, ctx, "EntitlementApproval", invite["payload"], "Accepted", invite, track_author=False)
        c.execute(
            "UPDATE impact.member_invitation SET consumed_at=%s,accepted_membership_id=%s,intended_subject=%s WHERE tenant_id=%s AND invitation_id=%s",
            (now(), membership_id, identity.subject, tenant, invitation["invitation_id"]),
        )
        return self.record(c, ctx, "accept_invitation", body, fingerprint, receipt, correlation)

    def create_scope(self, c, ctx, data):
        for obj in data["object_ids"]:
            row = load(c, ctx, obj)
            if row["object_type"] in {
                "Membership",
                "Grant",
                "RoleTemplate",
                "EntitlementApproval",
                "Tenant",
                "AccessGroup",
                "GroupChangeRequest",
                "MembershipRenewal",
                "CustodyTransfer",
            }:
                deny("ADMINISTRATIVE_OBJECT_SCOPE_DENIED")
        receipt = write(
            c,
            ctx,
            "Predicate",
            {
                "title": data["title"],
                "object_ids": sorted(data["object_ids"]),
                "managed_by": "impact-access-v1",
            },
            "Active",
            track_author=False,
        )
        c.execute(
            "INSERT INTO impact.scope_definition VALUES(%s,%s,'OBJECT_SET',%s)",
            (ctx.tenant_id, receipt["object_id"], receipt["revision_id"]),
        )
        for obj in data["object_ids"]:
            c.execute(
                "INSERT INTO impact.scope_member VALUES(%s,%s,%s)", (ctx.tenant_id, receipt["object_id"], obj)
            )
        return receipt

    def access_request(self, c, ctx, previous, action, data):
        if not previous:
            member = load(c, ctx, data["membership_id"], "Membership")
            self.protect_owner(c, ctx, member)
            if member["lifecycle_state"] != "Active":
                raise DomainError("STATE_TRANSITION_DENIED", 409)
            if str(member["head_revision"]) != data["expected_membership_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            role = self.role(c, ctx, data["role_template_id"])
            expiry = timestamp(data["expires_at"])
            if not now() < expiry <= now() + timedelta(days=90):
                raise DomainError("VALIDATION_FAILED", reason="GRANT_EXPIRY_BOUNDS")
            self.delegation(c, ctx, role["payload"]["capabilities"], data["scope_ids"], expiry)
            if role["payload"]["administrative"]:
                for scope in data["scope_ids"]:
                    if (
                        c.execute(
                            "SELECT scope_type FROM impact.scope_definition WHERE tenant_id=%s AND scope_id=%s",
                            (ctx.tenant_id, scope),
                        ).fetchone()["scope_type"]
                        != "TENANT"
                    ):
                        deny("ADMIN_ROLE_REQUIRES_TENANT_SCOPE")
            payload = {
                "kind": "ACCESS_REQUEST",
                **data,
                "requested_by": ctx.principal_id,
                "requester_identity_id": ctx.identity.identity_id,
                "requester_natural_id": ctx.identity.natural_identity_id,
                "requester_auth_time": ctx.identity.auth_time.isoformat(),
                "role_revision": str(role["head_revision"]),
                "role_name": role["payload"]["name"],
            }
            return write(c, ctx, "EntitlementApproval", payload, "Requested", track_author=False)
        if (
            previous["object_type"] != "EntitlementApproval"
            or previous["payload"].get("kind") != "ACCESS_REQUEST"
        ):
            unavailable()
        if previous["lifecycle_state"] != "Requested":
            raise DomainError("STATE_TRANSITION_DENIED", 409)
        request = previous["payload"]
        member = load(c, ctx, request["membership_id"], "Membership", lock=True)
        target_principal = self.principal(c, ctx, member)
        target_natural = c.execute(
            "SELECT impact.member_natural_identity(%s,%s) AS natural_id",
            (ctx.tenant_id, target_principal["principal_id"]),
        ).fetchone()["natural_id"]
        if not target_natural or ctx.identity.natural_identity_id in {
            request["requester_natural_id"],
            str(target_natural),
        }:
            deny("INDEPENDENCE_REQUIRED")
        if action == "reject":
            return write(
                c,
                ctx,
                "EntitlementApproval",
                {**request, "decision_reason": data["reason"], "decided_by": ctx.principal_id},
                "Rejected",
                previous,
                track_author=False,
            )
        self.protect_owner(c, ctx, member)
        if (
            member["lifecycle_state"] != "Active"
            or str(member["head_revision"]) != request["expected_membership_revision"]
        ):
            raise DomainError("CONFLICT_VERSION", 409)
        requester = context(
            c,
            SimpleNamespace(
                identity_id=request["requester_identity_id"],
                auth_time=timestamp(request["requester_auth_time"]),
            ),
            ctx.tenant_id,
            write=True,
        )
        if not scopes(c, requester, "grant.request"):
            deny("REQUESTER_NO_LONGER_AUTHORIZED")
        role = self.role(c, ctx, request["role_template_id"], request["role_revision"])
        expiry = timestamp(request["expires_at"])
        self.delegation(c, requester, role["payload"]["capabilities"], request["scope_ids"], expiry)
        self.delegation(c, ctx, role["payload"]["capabilities"], request["scope_ids"], expiry)
        self.issue_role(c, ctx, member, role, request["scope_ids"], expiry, ctx.principal_id)
        write(c, ctx, "Membership", member["payload"], "Active", member, track_author=False)
        return write(
            c,
            ctx,
            "EntitlementApproval",
            {**request, "decision_reason": data["reason"], "decided_by": ctx.principal_id},
            "Applied",
            previous,
            track_author=False,
        )

    def listing(self, identity, tenant, route, limit=50, cursor=None):
        if route not in ADMIN_READS or not 1 <= limit <= 100:
            raise DomainError("VALIDATION_FAILED")
        name, cap = ADMIN_READS[route]
        with self.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "list_" + route.replace("-", "_"))
            self.require_tenant_admin_scope(ctx, cap)
            binding = self.service.cursor_binding(ctx, route)
            key = None
            if cursor:
                import base64

                try:
                    raw, mac = cursor.split(".")
                    if len(cursor) > 4096 or not hmac.compare_digest(
                        mac, hmac.new(self.s.cookie_secret.encode(), raw.encode(), hashlib.sha256).hexdigest()
                    ):
                        raise ValueError
                    data = json.loads(base64.urlsafe_b64decode(raw + "=" * ((-len(raw)) % 4)))
                    if data["binding"] != binding or data["expires"] < time.time():
                        raise ValueError
                    key = data["key"]
                except (ValueError, KeyError, TypeError):
                    raise DomainError("INVALID_CURSOR", 400) from None
            if route == "access-scopes":
                query = "SELECT scope_id AS object_id,scope_type,predicate_version FROM impact.scope_definition WHERE tenant_id=%s"
                args = [tenant]
                if key:
                    query += " AND scope_id>%s::uuid"
                    args.append(key)
                rows = c.execute(query + " ORDER BY scope_id LIMIT %s", args + [limit + 1]).fetchall()
            else:
                kind = {"membership-directory": "Membership", "role-templates": "RoleTemplate"}.get(
                    route, WORKSPACE_KINDS.get(route, "EntitlementApproval")
                )
                query = "SELECT r.*,v.payload FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_type=%s AND r.classification<>'RESTRICTED' AND v.restriction_state='AVAILABLE'"
                args = [tenant, kind]
                if route == "member-invitations":
                    query += " AND v.payload->>'kind'='MEMBER_INVITATION'"
                if route == "access-requests":
                    query += " AND v.payload->>'kind'='ACCESS_REQUEST'"
                if route == "role-templates":
                    query += " AND v.payload->>'managed_by'='impact-access-v1' AND r.lifecycle_state='Active'"
                if key:
                    query += " AND r.object_id>%s::uuid"
                    args.append(key)
                rows = c.execute(query + " ORDER BY r.object_id LIMIT %s", args + [limit + 1]).fetchall()
            items = [self.list_item(c, ctx, route, row) for row in rows[:limit]]
            next_cursor = (
                self.service.cursor(
                    {
                        "binding": binding,
                        "expires": int(time.time()) + 900,
                        "key": str(rows[limit - 1]["object_id"]),
                    }
                )
                if len(rows) > limit
                else None
            )
            result = {
                "items": items,
                "next_cursor": next_cursor,
                "scope_label": "Administrative metadata within this workspace",
            }
            validate(name + "List", result)
            return result

    def list_item(self, c, ctx, route, row):
        obj = str(row["object_id"])
        if route == "access-scopes":
            rev = c.execute(
                "SELECT payload FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
                (ctx.tenant_id, row["predicate_version"]),
            ).fetchone()
            ids = c.execute(
                "SELECT object_id FROM impact.scope_member WHERE tenant_id=%s AND scope_id=%s ORDER BY object_id LIMIT 10000",
                (ctx.tenant_id, obj),
            ).fetchall()
            return {
                "object_id": obj,
                "title": (rev["payload"].get("title") if rev and rev["payload"] else None)
                or ("All workspace records" if row["scope_type"] == "TENANT" else "Scope " + obj[:8]),
                "scope_type": row["scope_type"],
                "object_ids": [str(x["object_id"]) for x in ids],
            }
        data = row["payload"]
        common = {"object_id": obj, "revision_id": str(row["head_revision"]), "state": row["lifecycle_state"]}
        if route in WORKSPACE_KINDS:
            return self.workspace.list_item(route, common, data)
        if route == "role-templates":
            return {
                **common,
                "name": data["name"],
                "capabilities": data["capabilities"],
                "administrative": data["administrative"],
            }
        if route == "member-invitations":
            if common["state"] == "Invited" and timestamp(data["expires_at"]) <= now():
                common["state"] = "Expired"
            return {
                **common,
                **{
                    k: data[k]
                    for k in [
                        "email_mask",
                        "role_name",
                        "scope_ids",
                        "expires_at",
                        "membership_expires_at",
                        "inviter_id",
                    ]
                },
            }
        if route == "access-requests":
            return {
                **common,
                **{
                    k: data[k]
                    for k in [
                        "membership_id",
                        "requested_by",
                        "role_name",
                        "scope_ids",
                        "expires_at",
                        "reason",
                    ]
                },
            }
        principal = self.principal(c, ctx, row)
        profile = (
            c.execute(
                "SELECT * FROM impact.member_profile WHERE tenant_id=%s AND membership_id=%s",
                (ctx.tenant_id, obj),
            ).fetchone()
            or {}
        )
        owner = (
            c.execute(
                "SELECT 1 FROM impact.tenant_custody WHERE tenant_id=%s AND owner_membership_id=%s",
                (ctx.tenant_id, obj),
            ).fetchone()
            is not None
        )
        grants = c.execute(
            "SELECT g.*,r.head_revision FROM impact.grant_current g JOIN impact.object_registry r ON r.tenant_id=g.tenant_id AND r.object_id=g.object_id WHERE g.tenant_id=%s AND g.subject_id=%s AND r.lifecycle_state='Active' AND g.purpose IS NULL AND g.starts_at<=%s AND (g.expires_at IS NULL OR g.expires_at>%s) ORDER BY g.capability,g.object_id LIMIT 501",
            (ctx.tenant_id, principal["principal_id"], now(), now()),
        ).fetchall()
        if len(grants) > 500:
            raise DomainError("LIMIT_EXCEEDED", 422, reason="MEMBER_GRANT_LIMIT")
        assignments = c.execute(
            "SELECT a.grant_ids,v.payload FROM impact.member_role_assignment a JOIN impact.object_revision v ON v.tenant_id=a.tenant_id AND v.revision_id=a.role_revision WHERE a.tenant_id=%s AND a.membership_id=%s AND a.expires_at>%s",
            (ctx.tenant_id, obj, now()),
        ).fetchall()
        grant_ids = {str(g["object_id"]) for g in grants}
        roles = sorted(
            {
                a["payload"]["name"]
                + (" (partial)" if not set(map(str, a["grant_ids"])).issubset(grant_ids) else "")
                for a in assignments
                if set(map(str, a["grant_ids"])) & grant_ids
            }
        )
        if owner:
            roles = ["OWNER"] + roles
        if data.get("expires_at") and timestamp(data["expires_at"]) <= now() and common["state"] == "Active":
            common["state"] = "Expired"
        return {
            **common,
            "principal_id": str(principal["principal_id"]),
            "identity_id": data["identity_id"],
            "display_name": profile.get("display_name", "Member " + data["identity_id"][:8]),
            "email_mask": profile.get("email_mask"),
            "external": bool(data.get("external")),
            "expires_at": data.get("expires_at"),
            "owner": owner,
            "roles": roles,
            "grants": [
                {
                    "object_id": str(g["object_id"]),
                    "revision_id": str(g["head_revision"]),
                    "capability": g["capability"],
                    "scope_id": str(g["scope_id"]),
                    "expires_at": g["expires_at"].isoformat() if g["expires_at"] else None,
                }
                for g in grants
                if scopes(c, ctx, "grants.read", g["object_id"])
            ],
        }
