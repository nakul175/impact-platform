"""Identity-bound recovery-contact evidence; never a grant or account recovery action."""

import hmac
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from psycopg.types.json import Jsonb
from .keyring import ring
from .delivery import channel_code, channel_code_hash, seal_recipient
from .domain import DomainError, unavailable
from .identity_profile import email_hash
from .platform_security import current_owner, registered_person
from .recovery_contracts import ACTIONS, CHANNEL_ACTIONS, validate_body
from .store import hash_data

CHANNEL_CODE_TTL = timedelta(minutes=15)
CHANNEL_CODE_ATTEMPTS = 5
# At most this many challenges (codes emailed) per contact within CHANNEL_REQUEST_WINDOW.
CHANNEL_REQUESTS_PER_WINDOW = 3
CHANNEL_REQUEST_WINDOW = timedelta(hours=1)


def now():
    return datetime.now(timezone.utc)


def denied(reason):
    raise DomainError("POLICY_DENIED", 403, reason=reason)


def lock_people(c, identities):
    c.execute("SELECT impact.lock_recovery_identities(%s::uuid[])", (list(map(str, identities)),))


def status_for(c, row, tenant, issuer):
    if not row:
        return {
            "contact_id": None,
            "revision_id": None,
            "eligible": False,
            "reason": "NONE",
            "expires_at": None,
        }
    reason = "VERIFIED"
    if row["state"] != "Active":
        reason = "NOT_ACTIVE"
    elif row["expires_at"] <= now():
        reason = "EXPIRED"
    elif (
        row["owner_identity_id"] != tenant["owner_identity_id"]
        or row["owner_membership_id"] != tenant["owner_membership_id"]
    ):
        reason = "OWNER_CHANGED"
    else:
        lock_people(c, [row["nominee_identity_id"], row["owner_identity_id"]])
        person = c.execute(
            "SELECT i.issuer,i.natural_identity_id,p.verified_email_hash,s.auth_not_before FROM impact.auth_identity i LEFT JOIN impact.identity_profile p USING(identity_id) LEFT JOIN impact.identity_security_state s USING(identity_id) WHERE identity_id=%s",
            (row["nominee_identity_id"],),
        ).fetchone()
        owner = c.execute(
            "SELECT natural_identity_id FROM impact.auth_identity WHERE identity_id=%s",
            (tenant["owner_identity_id"],),
        ).fetchone()
        if (
            not person
            or not owner
            or person["issuer"] != issuer
            or person["verified_email_hash"] != row["email_hash"]
            or person["natural_identity_id"] == owner["natural_identity_id"]
        ):
            reason = "IDENTITY_CHANGED"
        elif not row["verified_auth_time"] or (
            person["auth_not_before"] and row["verified_auth_time"] <= person["auth_not_before"]
        ):
            reason = "AUTHENTICATION_REVOKED"
    return {
        "contact_id": str(row["contact_id"]),
        "revision_id": str(row["revision_id"]),
        "eligible": reason == "VERIFIED",
        "reason": reason,
        "expires_at": row["expires_at"].isoformat(),
    }


def current_status(c, tenant, issuer):
    row = c.execute(
        "SELECT * FROM impact.tenant_recovery_contact WHERE tenant_id=%s AND state='Active'",
        (tenant["tenant_id"],),
    ).fetchone()
    return status_for(c, row, tenant, issuer)


class RecoveryContacts:
    def __init__(self, lifecycle):
        self.lifecycle, self.db, self.s = lifecycle, lifecycle.db, lifecycle.s

    def entry(self, c, contact):
        return c.execute(
            "SELECT r.*,o.operating_name FROM impact.tenant_recovery_contact r JOIN impact.tenant_onboarding o USING(tenant_id) WHERE contact_id=%s FOR UPDATE OF r",
            (contact,),
        ).fetchone()

    def present(self, c, row, tenant):
        keys = [
            "contact_id",
            "tenant_id",
            "revision_id",
            "operating_name",
            "owner_identity_id",
            "nominee_identity_id",
            "state",
            "display_name",
            "email_mask",
            "reason",
            "replaces_contact_id",
        ]
        return {
            **{key: str(row[key]) if key.endswith("_id") and row[key] else row[key] for key in keys},
            "expires_at": row["expires_at"].isoformat(),
            "review_expires_at": row["review_expires_at"].isoformat(),
            "verified_at": row["verified_at"].isoformat() if row["verified_at"] else None,
            "approved_at": row["approved_at"].isoformat() if row["approved_at"] else None,
            "approved_by": str(row["approved_by"]) if row["approved_by"] else None,
            "verification_method": "REGISTERED_IDENTITY_MFA",
            "verification": status_for(c, row, tenant, self.s.issuer),
            "channel_verification": self.channel_status(c, row),
        }

    def channel_status(self, c, row):
        """The latest mailbox-control challenge of this contact (the caller has set the tenant
        context). VERIFIED is evidence only; it grants and unlocks nothing."""
        challenge = (
            c.execute(
                "SELECT * FROM impact.recovery_channel_challenge WHERE tenant_id=%s AND challenge_id=%s",
                (row["tenant_id"], row["channel_challenge_id"]),
            ).fetchone()
            if row.get("channel_challenge_id")
            else None
        )
        if not challenge:
            return {
                "state": "NONE",
                "challenge_id": None,
                "expires_at": None,
                "verified_at": None,
                "attempts_remaining": CHANNEL_CODE_ATTEMPTS,
            }
        state = challenge["state"]
        if state == "PENDING" and challenge["expires_at"] <= now():
            state = "EXPIRED"
        return {
            "state": state,
            "challenge_id": str(challenge["challenge_id"]),
            "expires_at": challenge["expires_at"].isoformat(),
            "verified_at": challenge["consumed_at"].isoformat() if challenge["consumed_at"] else None,
            "attempts_remaining": CHANNEL_CODE_ATTEMPTS - challenge["attempts"],
        }

    def directory(self, identity, after=None):
        result = {"operator": False, "items": [], "next_cursor": None}
        if not self.s.platform_dsn:
            return result
        with self.db.transaction(platform=True) as c:
            result["operator"] = self.lifecycle.operator(c, identity)
            rows = c.execute(
                "SELECT r.*,o.operating_name FROM impact.tenant_recovery_contact r JOIN impact.tenant_onboarding o USING(tenant_id) WHERE (%s OR %s IN(o.owner_identity_id,r.nominee_identity_id)) AND (%s::uuid IS NULL OR r.contact_id>%s::uuid) ORDER BY r.contact_id LIMIT 51",
                (result["operator"], identity.identity_id, after, after),
            ).fetchall()
            for row in rows[:50]:
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (str(row["tenant_id"]),))
                # Read-only directory does not take tenant row locks before identity locks.
                tenant = c.execute(
                    "SELECT * FROM impact.tenant_onboarding WHERE tenant_id=%s", (row["tenant_id"],)
                ).fetchone()
                result["items"].append(self.present(c, row, tenant))
            result["next_cursor"] = str(rows[49]["contact_id"]) if len(rows) > 50 else None
            return result

    def event(self, c, identity, action, row, tenant, reason):
        payload = self.present(c, row, tenant)
        c.execute(
            "INSERT INTO impact.platform_event(event_id,tenant_id,identity_id,action,revision_id,reason,payload) VALUES(%s,%s,%s,%s,%s,%s,%s)",
            (
                str(uuid4()),
                tenant["tenant_id"],
                identity.identity_id,
                "recovery-" + action,
                row["revision_id"],
                reason,
                Jsonb(payload),
            ),
        )
        return payload

    def command(self, identity, action, body, tenant_id=None, contact_id=None):
        if action not in ACTIONS | set(CHANNEL_ACTIONS) | {"nominate"}:
            unavailable()
        validate_body(body, create=action == "nominate", action=action)
        self.lifecycle.assurance(identity)
        fingerprint = hash_data(
            {"recovery_action": action, "tenant": tenant_id, "contact": contact_id, "body": body}
        )
        with self.db.transaction(platform=True) as c:
            c.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",
                ("platform:" + identity.identity_id + ":" + body["operation_id"],),
            )
            operator = self.lifecycle.operator(c, identity)
            if contact_id:
                ref = c.execute(
                    "SELECT r.tenant_id FROM impact.tenant_recovery_contact r JOIN impact.tenant_onboarding o USING(tenant_id) WHERE r.contact_id=%s AND (%s OR %s IN(o.owner_identity_id,r.nominee_identity_id))",
                    (contact_id, operator, identity.identity_id),
                ).fetchone()
                if not ref:
                    unavailable()
                tenant_id = str(ref["tenant_id"])
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant_id,))
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant_id,))
            tenant = self.lifecycle.entry(c, tenant_id)
            if not tenant:
                unavailable()
            row = self.entry(c, contact_id) if contact_id else None
            owner = str(tenant["owner_identity_id"]) == identity.identity_id
            nominee = bool(row and str(row["nominee_identity_id"]) == identity.identity_id)
            permitted = (
                owner
                if action in {"nominate", "cancel"}
                else nominee
                if action in {"verify", "decline"} | set(CHANNEL_ACTIONS)
                else operator
                if action in {"approve", "reject"}
                else owner or nominee or operator
            )
            if not permitted:
                unavailable()
            # Auth.resolve runs before this transaction. Recheck the caller under
            # the same identity locks used by account revocation before any replay/write.
            lock_people(
                c,
                {
                    identity.identity_id,
                    str(tenant["owner_identity_id"]),
                    str(row["nominee_identity_id"]) if row else body["data"]["nominee_identity_id"],
                },
            )
            caller = registered_person(c, identity.identity_id, self.s.issuer)
            if caller["auth_not_before"] and identity.auth_time <= caller["auth_not_before"]:
                denied("REAUTHENTICATION_REQUIRED")
            if action in {"nominate", "verify", "approve"} | set(CHANNEL_ACTIONS) and tenant[
                "lifecycle_state"
            ] not in {
                "Provisioning",
                "Active",
                "Suspended",
            }:
                denied("RECOVERY_TENANT_UNAVAILABLE")
            if owner:
                membership = current_owner(c, tenant)
                if membership["auth_not_before"] and identity.auth_time <= membership["auth_not_before"]:
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
            failure = None
            if action == "nominate":
                contact_id = self.nominate(c, identity, tenant, body["data"])
            elif action in CHANNEL_ACTIONS:
                failure = self.channel(c, identity, tenant, row, action, body["data"])
            else:
                self.transition(c, identity, tenant, row, action, body["data"]["reason"])
            if failure:
                # A wrong or expired code is refused, but the spent attempt (or the expiry) is
                # committed with an event; no receipt is written, so no revision advances.
                self.event(
                    c,
                    identity,
                    action + "-refused",
                    self.entry(c, contact_id),
                    tenant,
                    body["data"]["reason"],
                )
            else:
                c.execute(
                    "UPDATE impact.tenant_recovery_contact SET revision_id=%s,updated_at=now() WHERE contact_id=%s",
                    (str(uuid4()), contact_id),
                )
                response = {
                    **self.event(
                        c, identity, action, self.entry(c, contact_id), tenant, body["data"]["reason"]
                    ),
                    "operation_id": body["operation_id"],
                }
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
        if failure:
            raise failure
        return response

    def channel(self, c, identity, tenant, row, action, data):
        """Request or confirm mailbox control for the nominee's registered address. Returns a
        DomainError to raise after commit (a spent attempt or an expiry must persist), or None."""
        if row["state"] not in {"Nominated", "Verified", "Active"}:
            raise DomainError("CONFLICT_VERSION", 409, reason="INVALID_RECOVERY_TRANSITION")
        if not self.s.delivery_secret:
            raise DomainError("SERVICE_UNAVAILABLE", 503, reason="DELIVERY_NOT_CONFIGURED")
        keys, at = ring(self.s, "delivery"), now()
        secret = keys.current
        lock_people(c, [row["nominee_identity_id"]])
        person = registered_person(c, row["nominee_identity_id"], self.s.issuer)
        if action == "channel-request":
            digest = email_hash(data["email"])
            if digest != bytes(row["email_hash"]) or digest != bytes(person["verified_email_hash"]):
                denied("CHANNEL_ADDRESS_MISMATCH")
            recent = c.execute(
                "SELECT count(*) AS n FROM impact.recovery_channel_challenge WHERE tenant_id=%s AND contact_id=%s AND created_at>%s",
                (row["tenant_id"], row["contact_id"], at - CHANNEL_REQUEST_WINDOW),
            ).fetchone()["n"]
            if recent >= CHANNEL_REQUESTS_PER_WINDOW:
                raise DomainError("LIMIT_EXCEEDED", 429, reason="CHANNEL_REQUEST_LIMIT")
            c.execute(
                "UPDATE impact.recovery_channel_challenge SET state='SUPERSEDED' WHERE tenant_id=%s AND contact_id=%s AND state='PENDING'",
                (row["tenant_id"], row["contact_id"]),
            )
            challenge = str(uuid4())
            c.execute(
                "INSERT INTO impact.recovery_channel_challenge(tenant_id,challenge_id,contact_id,contact_revision,requested_by,email_hash,code_hash,state,created_at,expires_at) VALUES(%s,%s,%s,%s,%s,%s,%s,'PENDING',%s,%s)",
                (
                    row["tenant_id"],
                    challenge,
                    row["contact_id"],
                    row["revision_id"],
                    identity.identity_id,
                    digest,
                    channel_code_hash(secret, challenge, channel_code(secret, challenge)),
                    at,
                    at + CHANNEL_CODE_TTL,
                ),
            )
            # The worker sends the code; the intent carries the challenge and the sealed address only.
            c.execute(
                "SELECT impact.enqueue_recovery_channel_delivery(%s,%s)",
                (
                    challenge,
                    seal_recipient(
                        keys, row["tenant_id"], "RECOVERY_CHANNEL_VERIFICATION", challenge, data["email"]
                    ),
                ),
            )
            c.execute(
                "UPDATE impact.tenant_recovery_contact SET channel_challenge_id=%s WHERE contact_id=%s",
                (challenge, row["contact_id"]),
            )
            return None
        challenge = c.execute(
            "SELECT * FROM impact.recovery_channel_challenge WHERE tenant_id=%s AND challenge_id=%s AND contact_id=%s FOR UPDATE",
            (row["tenant_id"], data["challenge_id"], row["contact_id"]),
        ).fetchone()
        if not challenge:
            unavailable()
        if challenge["state"] == "VERIFIED":
            raise DomainError("CONFLICT_VERSION", 409, reason="CHANNEL_CODE_USED")
        if challenge["state"] != "PENDING":
            raise DomainError("CONFLICT_VERSION", 409, reason="CHANNEL_CHALLENGE_CLOSED")
        if challenge["expires_at"] <= at:
            c.execute(
                "UPDATE impact.recovery_channel_challenge SET state='EXPIRED' WHERE tenant_id=%s AND challenge_id=%s",
                (row["tenant_id"], challenge["challenge_id"]),
            )
            return DomainError("POLICY_DENIED", 403, reason="CHANNEL_CODE_EXPIRED")
        # Any non-retired delivery secret: a code issued just before a rotation still confirms.
        if not any(
            hmac.compare_digest(
                channel_code_hash(candidate, challenge["challenge_id"], data["code"]),
                bytes(challenge["code_hash"]),
            )
            for candidate in keys.secrets()
        ):
            attempts = challenge["attempts"] + 1
            c.execute(
                "UPDATE impact.recovery_channel_challenge SET attempts=%s,state=%s WHERE tenant_id=%s AND challenge_id=%s",
                (
                    attempts,
                    "FAILED" if attempts >= CHANNEL_CODE_ATTEMPTS else "PENDING",
                    row["tenant_id"],
                    challenge["challenge_id"],
                ),
            )
            return DomainError(
                "POLICY_DENIED",
                403,
                reason="CHANNEL_CODE_ATTEMPTS_EXCEEDED"
                if attempts >= CHANNEL_CODE_ATTEMPTS
                else "CHANNEL_CODE_INVALID",
            )
        if bytes(person["verified_email_hash"]) != bytes(challenge["email_hash"]):
            c.execute(
                "UPDATE impact.recovery_channel_challenge SET state='SUPERSEDED' WHERE tenant_id=%s AND challenge_id=%s",
                (row["tenant_id"], challenge["challenge_id"]),
            )
            return DomainError("POLICY_DENIED", 403, reason="RECOVERY_IDENTITY_CHANGED")
        c.execute(
            "UPDATE impact.recovery_channel_challenge SET state='VERIFIED',consumed_at=%s WHERE tenant_id=%s AND challenge_id=%s",
            (at, row["tenant_id"], challenge["challenge_id"]),
        )
        c.execute(
            "UPDATE impact.tenant_recovery_contact SET channel_verified_at=%s,channel_challenge_id=%s WHERE contact_id=%s",
            (at, challenge["challenge_id"], row["contact_id"]),
        )
        return None

    def current(self, c, tenant_id):
        return c.execute(
            "SELECT * FROM impact.tenant_recovery_contact WHERE tenant_id=%s AND state='Active' FOR UPDATE",
            (tenant_id,),
        ).fetchone()

    def nominate(self, c, identity, tenant, data):
        if c.execute(
            "SELECT 1 FROM impact.tenant_recovery_contact WHERE tenant_id=%s AND state IN ('Nominated','Verified')",
            (tenant["tenant_id"],),
        ).fetchone():
            raise DomainError("CONFLICT_VERSION", 409, reason="RECOVERY_PENDING")
        current = self.current(c, tenant["tenant_id"])
        if data["expected_contact_revision"] != (str(current["revision_id"]) if current else None):
            raise DomainError("CONFLICT_VERSION", 409, reason="RECOVERY_CONTACT_CHANGED")
        expires = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
        if not now() < expires <= now() + timedelta(days=90):
            raise DomainError("VALIDATION_FAILED", reason="RECOVERY_EXPIRY_BOUNDS")
        lock_people(c, [identity.identity_id, data["nominee_identity_id"]])
        person = registered_person(c, data["nominee_identity_id"], self.s.issuer)
        if str(person["natural_identity_id"]) == identity.natural_identity_id:
            denied("INDEPENDENCE_REQUIRED")
        owner = current_owner(c, tenant)
        contact_id = str(uuid4())
        c.execute(
            "INSERT INTO impact.tenant_recovery_contact(contact_id,tenant_id,revision_id,state,owner_identity_id,owner_membership_id,owner_revision,tenant_revision,nominee_identity_id,email_hash,display_name,email_mask,replaces_contact_id,replaces_revision,owner_auth_time,expires_at,review_expires_at,reason) VALUES(%s,%s,%s,'Nominated',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                contact_id,
                tenant["tenant_id"],
                str(uuid4()),
                identity.identity_id,
                tenant["owner_membership_id"],
                owner["head_revision"],
                tenant["revision_id"],
                data["nominee_identity_id"],
                person["verified_email_hash"],
                person["display_name"] or "Recovery contact",
                person["email_mask"],
                current["contact_id"] if current else None,
                current["revision_id"] if current else None,
                identity.auth_time,
                expires,
                min(expires, now() + timedelta(days=7)),
                data["reason"],
            ),
        )
        return contact_id

    def recheck(self, c, tenant, row):
        lock_people(c, [row["owner_identity_id"], row["nominee_identity_id"]])
        owner = current_owner(c, tenant)
        if (
            tenant["revision_id"] != row["tenant_revision"]
            or tenant["owner_identity_id"] != row["owner_identity_id"]
            or tenant["owner_membership_id"] != row["owner_membership_id"]
            or owner["head_revision"] != row["owner_revision"]
        ):
            raise DomainError("CONFLICT_VERSION", 409, reason="RECOVERY_CONTEXT_CHANGED")
        if row["review_expires_at"] <= now() or row["expires_at"] <= now():
            denied("RECOVERY_REVIEW_EXPIRED")
        people = [
            registered_person(c, row[key], self.s.issuer)
            for key in ["owner_identity_id", "nominee_identity_id"]
        ]
        if people[0]["natural_identity_id"] == people[1]["natural_identity_id"]:
            denied("INDEPENDENCE_REQUIRED")
        if people[1]["verified_email_hash"] != row["email_hash"]:
            denied("RECOVERY_IDENTITY_CHANGED")
        if (owner["auth_not_before"] and row["owner_auth_time"] <= owner["auth_not_before"]) or (
            people[0]["auth_not_before"] and row["owner_auth_time"] <= people[0]["auth_not_before"]
        ):
            denied("REAUTHENTICATION_REQUIRED")
        if (
            row["verified_auth_time"]
            and people[1]["auth_not_before"]
            and row["verified_auth_time"] <= people[1]["auth_not_before"]
        ):
            denied("RECOVERY_VERIFICATION_REVOKED")
        current = self.current(c, tenant["tenant_id"])
        if (current["contact_id"] if current else None) != row["replaces_contact_id"] or (
            current["revision_id"] if current else None
        ) != row["replaces_revision"]:
            raise DomainError("CONFLICT_VERSION", 409, reason="RECOVERY_CONTACT_CHANGED")
        return people, current

    def transition(self, c, identity, tenant, row, action, reason):
        allowed = {
            "verify": {"Nominated"},
            "approve": {"Verified"},
            "reject": {"Nominated", "Verified"},
            "cancel": {"Nominated", "Verified"},
            "decline": {"Nominated", "Verified"},
            "revoke": {"Active"},
        }
        if row["state"] not in allowed[action]:
            raise DomainError("CONFLICT_VERSION", 409, reason="INVALID_RECOVERY_TRANSITION")
        if action in {"reject", "cancel", "decline", "revoke"}:
            state = {"reject": "Rejected", "cancel": "Cancelled", "decline": "Declined", "revoke": "Revoked"}[
                action
            ]
            c.execute(
                "UPDATE impact.tenant_recovery_contact SET state=%s WHERE contact_id=%s",
                (state, row["contact_id"]),
            )
            return
        people, current = self.recheck(c, tenant, row)
        if action == "verify":
            c.execute(
                "UPDATE impact.tenant_recovery_contact SET state='Verified',verified_at=now(),verified_auth_time=%s WHERE contact_id=%s",
                (identity.auth_time, row["contact_id"]),
            )
            return
        if identity.natural_identity_id in {str(p["natural_identity_id"]) for p in people}:
            denied("INDEPENDENCE_REQUIRED")
        if not row["verified_at"] or row["verified_at"] + timedelta(days=1) <= now():
            denied("RECOVERY_VERIFICATION_STALE")
        if current:
            c.execute(
                "UPDATE impact.tenant_recovery_contact SET state='Replaced',revision_id=%s,updated_at=now() WHERE contact_id=%s",
                (str(uuid4()), current["contact_id"]),
            )
            self.event(c, identity, "replaced", self.entry(c, current["contact_id"]), tenant, reason)
        c.execute(
            "UPDATE impact.tenant_recovery_contact SET state='Active',approved_by=%s,approved_at=now() WHERE contact_id=%s",
            (identity.identity_id, row["contact_id"]),
        )
