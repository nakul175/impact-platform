"""Governed platform-operator onboarding and sign-in accounts (v0.26a, gap A3).

Operator nomination. An active platform operator nominates one person, named by e-mail address, for
the operator role with a reason and an expiry no later than their own (at most 365 days). The person
who signs in with that verified address accepts, with fresh MFA; the SECURITY DEFINER
`impact.accept_operator_nomination` (migration 0028) rechecks everything and is the only way an
operator row is written at run time. Never accepted by the nominating operator or anyone sharing
their natural person, never by a natural person who already holds an active operator identity, never
after the nominating operator lost the role. Nominating oneself is refused. Activation of a tenant
keeps excluding the requester and the owner by natural person, so a second operator counts there
only because they are a different natural person.

Sign-in accounts. An operator (for anyone, typically a nominee, a prospective tenant owner or a second
administrator), or the current owner of an Active tenant (only for an address with a pending
invitation of that tenant), creates the person's identity-provider account through
impact_api/provider_accounts.py and registers it as a platform identity without authority. The
one-time password is in the live response only: never stored, logged, written to the receipt or the
event, or returned on a replay. It can be reissued (once more shown once) only while the person has
not yet chosen their own password.

Every step commits a `platform_event` (tenant-less for nominations and operator-created accounts) and
a `platform_receipt` together, after fresh MFA; an exact retry returns the receipt, a changed payload
under the same operation ID is a conflict, a stale `expected_revision` is a conflict.
"""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4
from psycopg.types.json import Jsonb
from .domain import DomainError, unavailable
from .identity_profile import email_hash, masked_email, normalize_email
from .operator_contracts import (
    ACCOUNT_ACTIONS,
    ACCOUNT_CREATE,
    ACCOUNT_REISSUE,
    ACTION,
    NOMINATE,
    NOMINATION_ACTIONS,
    OPERATOR_ACTIONS,
    RENEW,
    validate_body,
)
from .platform_security import current_owner
from .provider_accounts import backend
from .store import hash_data

NOMINATION_DAYS = 7
OPERATOR_MAX_DAYS = 365
LOCK = "platform:operator-onboarding"


def now():
    return datetime.now(timezone.utc)


def denied(reason):
    raise DomainError("POLICY_DENIED", 403, reason=reason)


def iso(value):
    return value.isoformat() if value else None


class Operators:
    def __init__(self, lifecycle):
        self.lifecycle, self.db, self.s = lifecycle, lifecycle.db, lifecycle.s
        self.accounts = backend(self.s)

    # ---- shared ------------------------------------------------------------------------------

    def begin(self, c, identity, operation_id):
        c.execute(
            "SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",
            ("platform:" + identity.identity_id + ":" + operation_id,),
        )
        # One onboarding change at a time across the platform: operator rows are global.
        c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (LOCK,))

    def replay(self, c, identity, operation_id, fingerprint):
        old = c.execute(
            "SELECT * FROM impact.platform_receipt WHERE identity_id=%s AND operation_id=%s",
            (identity.identity_id, operation_id),
        ).fetchone()
        if not old:
            return None
        if bytes(old["fingerprint"]) != fingerprint or old["expires_at"] <= now():
            raise DomainError("CONFLICT_VERSION", 409, reason="OPERATION_REUSE")
        return old["response"]

    def record(self, c, identity, operation_id, fingerprint, action, revision, reason, response, tenant=None):
        c.execute(
            "INSERT INTO impact.platform_event(event_id,tenant_id,identity_id,action,revision_id,reason,payload) VALUES(%s,%s,%s,%s,%s,%s,%s)",
            (str(uuid4()), tenant, identity.identity_id, action, revision, reason, Jsonb(response)),
        )
        c.execute(
            "INSERT INTO impact.platform_receipt VALUES(%s,%s,%s,%s,%s)",
            (identity.identity_id, operation_id, fingerprint, Jsonb(response), now() + timedelta(days=7)),
        )

    def natural(self, c, identity_id):
        row = c.execute(
            "SELECT natural_identity_id FROM impact.auth_identity WHERE identity_id=%s", (str(identity_id),)
        ).fetchone()
        return str(row["natural_identity_id"]) if row else None

    def natural_is_operator(self, c, natural):
        return (
            c.execute(
                "SELECT 1 FROM impact.platform_operator o JOIN impact.auth_identity i USING(identity_id) WHERE i.natural_identity_id=%s AND o.active AND o.expires_at>now()",
                (natural,),
            ).fetchone()
            is not None
        )

    # ---- directory ---------------------------------------------------------------------------

    def present_nomination(self, c, row):
        state = row["state"]
        if state == "Nominated" and row["expires_at"] <= now():
            state = "Expired"
        nominator = c.execute(
            "SELECT display_name FROM impact.identity_profile WHERE identity_id=%s", (row["nominated_by"],)
        ).fetchone()
        created = c.execute(
            "SELECT 1 FROM impact.provider_account WHERE email_hash=%s AND created_by=%s AND provider_created",
            (bytes(row["email_hash"]), row["nominated_by"]),
        ).fetchone()
        return {
            "nomination_id": str(row["nomination_id"]),
            "revision_id": str(row["revision_id"]),
            "state": state,
            "email_mask": row["email_mask"],
            "nominated_by": str(row["nominated_by"]),
            "nominator_name": (nominator and nominator["display_name"]) or "Platform operator",
            "operator_expires_at": row["operator_expires_at"].isoformat(),
            "expires_at": row["expires_at"].isoformat(),
            "reason": row["reason"],
            "nominee_identity_id": str(row["nominee_identity_id"]) if row["nominee_identity_id"] else None,
            "accepted_at": iso(row["accepted_at"]),
            "account_created_by_nominator": created is not None,
        }

    def present_account(self, row):
        return {
            "account_id": str(row["account_id"]),
            "revision_id": str(row["revision_id"]),
            "email_mask": row["email_mask"],
            "identity_id": str(row["identity_id"]) if row["identity_id"] else None,
            "created_by": str(row["created_by"]),
            "tenant_id": str(row["tenant_id"]) if row["tenant_id"] else None,
            "nomination_id": str(row["nomination_id"]) if row["nomination_id"] else None,
            "provider_created": row["provider_created"],
            "credentials_issued": row["credentials_issued"],
            "created_at": row["created_at"].isoformat(),
            "last_issued_at": iso(row["last_issued_at"]),
        }

    def present_operator(self, row):
        return {
            "identity_id": str(row["identity_id"]),
            "revision_id": str(row["revision_id"]),
            "display_name": row["display_name"] or "Registered identity",
            "email_mask": row["email_mask"],
            "active": bool(row["active"] and row["expires_at"] > now()),
            "state": "Deactivated"
            if not row["active"]
            else "Expired"
            if row["expires_at"] <= now()
            else "Active",
            "expires_at": row["expires_at"].isoformat(),
            "updated_at": row["updated_at"].isoformat(),
            "authority_reference": row["authority_reference"],
        }

    def operator_entry(self, c, identity_id):
        # No row lock here: the platform role only reads platform_operator (the definer locks the
        # row FOR UPDATE), and the onboarding advisory lock serialises operator changes.
        return c.execute(
            "SELECT o.*,p.display_name,p.email_mask FROM impact.platform_operator o LEFT JOIN impact.identity_profile p USING(identity_id) WHERE o.identity_id=%s",
            (str(identity_id),),
        ).fetchone()

    def present_change(self, row):
        return {
            "change_id": str(row["change_id"]),
            "operator_identity_id": str(row["operator_identity_id"]),
            "action": row["action"],
            "actor_identity_id": str(row["actor_identity_id"]),
            "actor_name": row["actor_name"] or "Platform operator",
            "reason": row["reason"],
            "previous_expires_at": row["previous_expires_at"].isoformat(),
            "expires_at": row["expires_at"].isoformat(),
            "created_at": row["created_at"].isoformat(),
        }

    def directory(self, identity):
        result = {
            "operator": False,
            "identity_id": identity.identity_id,
            "accounts_enabled": self.accounts is not None,
            "operators": [],
            "changes": [],
            "nominations": [],
            "identities": [],
            "accounts": [],
        }
        if not self.s.platform_dsn:
            return result
        with self.db.transaction(platform=True) as c:
            operator = self.lifecycle.operator(c, identity)
            result["operator"] = operator
            if operator:
                result["operators"] = [
                    self.present_operator(row)
                    for row in c.execute(
                        "SELECT o.*,p.display_name,p.email_mask FROM impact.platform_operator o LEFT JOIN impact.identity_profile p USING(identity_id) ORDER BY o.expires_at DESC,o.identity_id LIMIT 200"
                    ).fetchall()
                ]
                result["changes"] = [
                    self.present_change(row)
                    for row in c.execute(
                        "SELECT g.*,p.display_name AS actor_name FROM impact.platform_operator_change g LEFT JOIN impact.identity_profile p ON p.identity_id=g.actor_identity_id ORDER BY g.created_at DESC,g.change_id LIMIT 100"
                    ).fetchall()
                ]
                nominations = c.execute(
                    "SELECT * FROM impact.platform_operator_nomination ORDER BY created_at DESC,nomination_id LIMIT 100"
                ).fetchall()
                result["identities"] = [
                    {
                        "identity_id": str(row["identity_id"]),
                        "display_name": row["display_name"] or "Not signed in yet",
                        "email_mask": row["email_mask"],
                        "signed_in": row["verified_email_hash"] is not None,
                        "operator": row["operator"],
                    }
                    for row in c.execute(
                        "SELECT i.identity_id,p.display_name,p.email_mask,p.verified_email_hash,EXISTS(SELECT 1 FROM impact.platform_operator o WHERE o.identity_id=i.identity_id AND o.active AND o.expires_at>now()) AS operator FROM impact.auth_identity i LEFT JOIN impact.identity_profile p USING(identity_id) WHERE i.issuer=%s ORDER BY p.display_name NULLS LAST,i.identity_id LIMIT 200",
                        (self.s.issuer,),
                    ).fetchall()
                ]
                accounts = c.execute(
                    "SELECT * FROM impact.provider_account ORDER BY created_at DESC,account_id LIMIT 100"
                ).fetchall()
            else:
                nominations = (
                    c.execute(
                        "SELECT * FROM impact.platform_operator_nomination WHERE email_hash=%s ORDER BY created_at DESC LIMIT 20",
                        (identity.verified_email_hash,),
                    ).fetchall()
                    if identity.verified_email_hash
                    else []
                )
                accounts = c.execute(
                    "SELECT * FROM impact.provider_account WHERE created_by=%s ORDER BY created_at DESC LIMIT 100",
                    (identity.identity_id,),
                ).fetchall()
            result["nominations"] = [self.present_nomination(c, row) for row in nominations]
            result["accounts"] = [self.present_account(row) for row in accounts]
            return result

    # ---- nominations -------------------------------------------------------------------------

    def entry(self, c, nomination):
        return c.execute(
            "SELECT * FROM impact.platform_operator_nomination WHERE nomination_id=%s FOR UPDATE",
            (nomination,),
        ).fetchone()

    def addressed(self, identity, row):
        return bool(identity.verified_email_hash) and bytes(row["email_hash"]) == identity.verified_email_hash

    def nomination(self, identity, action, body, nomination_id=None):
        if action not in NOMINATION_ACTIONS | {"nominate"}:
            unavailable()
        validate_body(body, NOMINATE if action == "nominate" else ACTION)
        self.lifecycle.assurance(identity)
        fingerprint = hash_data({"operator_action": action, "nomination": nomination_id, "body": body})
        with self.db.transaction(platform=True) as c:
            self.begin(c, identity, body["operation_id"])
            operator = self.lifecycle.operator(c, identity)
            row = None
            if nomination_id:
                row = self.entry(c, nomination_id)
                if not row or not (operator or self.addressed(identity, row)):
                    unavailable()
            elif not operator:
                denied("PLATFORM_OPERATOR_REQUIRED")
            old = self.replay(c, identity, body["operation_id"], fingerprint)
            if old:
                return old
            if row and str(row["revision_id"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if action == "nominate":
                nomination_id = self.nominate(c, identity, body["data"])
            elif action == "cancel":
                if not operator:
                    denied("PLATFORM_OPERATOR_REQUIRED")
                self.close(c, identity, row, "Cancelled", body["data"]["reason"])
            elif action == "decline":
                if not self.addressed(identity, row):
                    unavailable()
                self.close(c, identity, row, "Declined", body["data"]["reason"])
            else:
                if not self.addressed(identity, row):
                    unavailable()
                self.accept(c, identity, row)
            revision = str(uuid4())
            c.execute(
                "UPDATE impact.platform_operator_nomination SET revision_id=%s,updated_at=now() WHERE nomination_id=%s",
                (revision, nomination_id),
            )
            response = {
                **self.present_nomination(c, self.entry(c, nomination_id)),
                "operation_id": body["operation_id"],
            }
            self.record(
                c,
                identity,
                body["operation_id"],
                fingerprint,
                "operator-" + action,
                revision,
                body["data"]["reason"],
                response,
            )
            return response

    def nominate(self, c, identity, data):
        email = normalize_email(data["email"])
        digest = email_hash(email)
        if identity.verified_email_hash == digest:
            denied("SELF_NOMINATION")
        nominator_natural = self.natural(c, identity.identity_id)
        holders = c.execute(
            "SELECT i.identity_id,i.natural_identity_id FROM impact.identity_profile p JOIN impact.auth_identity i USING(identity_id) WHERE p.verified_email_hash=%s",
            (digest,),
        ).fetchall()
        if any(str(h["natural_identity_id"]) == nominator_natural for h in holders):
            denied("INDEPENDENCE_REQUIRED")
        if any(self.natural_is_operator(c, str(h["natural_identity_id"])) for h in holders):
            raise DomainError("CONFLICT_OPERATION", 409, reason="ALREADY_OPERATOR")
        own = c.execute(
            "SELECT expires_at FROM impact.platform_operator WHERE identity_id=%s", (identity.identity_id,)
        ).fetchone()
        expiry = datetime.fromisoformat(data["operator_expires_at"].replace("Z", "+00:00"))
        if not now() < expiry <= min(now() + timedelta(days=OPERATOR_MAX_DAYS), own["expires_at"]):
            raise DomainError("VALIDATION_FAILED", reason="OPERATOR_EXPIRY_BOUNDS")
        # An expired, never-answered nomination for this address is closed before a new one.
        c.execute(
            "UPDATE impact.platform_operator_nomination SET state='Cancelled',decision_reason='Expired without an answer',updated_at=now() WHERE email_hash=%s AND state='Nominated' AND expires_at<=now()",
            (digest,),
        )
        if c.execute(
            "SELECT 1 FROM impact.platform_operator_nomination WHERE email_hash=%s AND state='Nominated'",
            (digest,),
        ).fetchone():
            raise DomainError("CONFLICT_OPERATION", 409, reason="NOMINATION_PENDING")
        nomination = str(uuid4())
        c.execute(
            "INSERT INTO impact.platform_operator_nomination(nomination_id,revision_id,state,nominated_by,email_hash,email_mask,reason,operator_expires_at,expires_at,nominator_auth_time) VALUES(%s,%s,'Nominated',%s,%s,%s,%s,%s,%s,%s)",
            (
                nomination,
                str(uuid4()),
                identity.identity_id,
                digest,
                masked_email(email),
                data["reason"].strip(),
                expiry,
                min(expiry, now() + timedelta(days=NOMINATION_DAYS)),
                identity.auth_time,
            ),
        )
        return nomination

    def close(self, c, identity, row, state, reason):
        if row["state"] != "Nominated":
            raise DomainError("CONFLICT_VERSION", 409, reason="NOMINATION_CLOSED")
        c.execute(
            "UPDATE impact.platform_operator_nomination SET state=%s,decided_by=%s,decision_reason=%s WHERE nomination_id=%s",
            (state, identity.identity_id, reason.strip(), row["nomination_id"]),
        )

    def accept(self, c, identity, row):
        if row["state"] != "Nominated":
            raise DomainError("CONFLICT_VERSION", 409, reason="NOMINATION_CLOSED")
        if row["expires_at"] <= now() or row["operator_expires_at"] <= now():
            denied("NOMINATION_EXPIRED")
        # Independence by natural person: never the nominating operator, never someone who already
        # is an operator (another identity of the same person adds no independent operator).
        actor = self.natural(c, identity.identity_id)
        if identity.identity_id == str(row["nominated_by"]) or actor == self.natural(c, row["nominated_by"]):
            denied("INDEPENDENCE_REQUIRED")
        if self.natural_is_operator(c, actor):
            raise DomainError("CONFLICT_OPERATION", 409, reason="ALREADY_OPERATOR")
        if not self.lifecycle.operator(c, SimpleNamespace(identity_id=str(row["nominated_by"]))):
            denied("NOMINATOR_NOT_OPERATOR")
        # The definer rechecks every condition above and writes the operator row.
        c.execute(
            "SELECT impact.accept_operator_nomination(%s,%s)", (row["nomination_id"], identity.identity_id)
        )
        c.execute(
            "UPDATE impact.platform_operator_nomination SET decision_reason=%s WHERE nomination_id=%s",
            ("Accepted with fresh MFA at " + identity.auth_time.isoformat(), row["nomination_id"]),
        )

    # ---- operator lifecycle (v0.27): renewal and deactivation ---------------------------------

    def lifecycle_change(self, identity, action, body, subject_id):
        """Renew (a later expiry, at most 365 days ahead) or deactivate one operator, by a different
        active operator who is a different natural person, with fresh assurance and a reason. The
        definer `impact.apply_operator_change` rechecks everything and is the only writer of
        `platform_operator`; the checks here only choose the reason code. A non-operator never
        learns whether the subject exists (404); the last active operator is never deactivated,
        which the actor rule already implies and the definer counts again."""
        if action not in OPERATOR_ACTIONS:
            unavailable()
        validate_body(body, RENEW if action == "renew" else ACTION)
        self.lifecycle.assurance(identity)
        subject = str(subject_id)
        fingerprint = hash_data({"operator_lifecycle": action, "subject": subject, "body": body})
        with self.db.transaction(platform=True) as c:
            self.begin(c, identity, body["operation_id"])
            if not self.lifecycle.operator(c, identity):
                unavailable()
            row = self.operator_entry(c, subject)
            if not row:
                unavailable()
            old = self.replay(c, identity, body["operation_id"], fingerprint)
            if old:
                return old
            if str(row["revision_id"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if subject == identity.identity_id or self.natural(c, subject) == self.natural(
                c, identity.identity_id
            ):
                denied("INDEPENDENCE_REQUIRED")
            if not row["active"]:
                raise DomainError("CONFLICT_VERSION", 409, reason="OPERATOR_DEACTIVATED")
            if row["expires_at"] <= now():
                raise DomainError("CONFLICT_VERSION", 409, reason="OPERATOR_EXPIRED")
            expiry = None
            if action == "renew":
                expiry = datetime.fromisoformat(body["data"]["expires_at"].replace("Z", "+00:00"))
                if not row["expires_at"] < expiry <= now() + timedelta(days=OPERATOR_MAX_DAYS):
                    raise DomainError("VALIDATION_FAILED", reason="OPERATOR_EXPIRY_BOUNDS")
            else:
                others = c.execute(
                    "SELECT count(*) AS n FROM impact.platform_operator WHERE active AND expires_at>now() AND identity_id<>%s",
                    (subject,),
                ).fetchone()["n"]
                if others < 1:
                    denied("LAST_OPERATOR")
            change = str(uuid4())
            # The definer rechecks every condition above and is the only writer of platform_operator.
            revision = c.execute(
                "SELECT impact.apply_operator_change(%s,%s,%s,%s,%s,%s,%s,%s) AS revision",
                (
                    change,
                    subject,
                    identity.identity_id,
                    action,
                    body["expected_revision"],
                    expiry,
                    identity.auth_time,
                    body["data"]["reason"],
                ),
            ).fetchone()["revision"]
            response = {
                **self.present_operator(self.operator_entry(c, subject)),
                "operation_id": body["operation_id"],
                "change_id": change,
            }
            self.record(
                c,
                identity,
                body["operation_id"],
                fingerprint,
                "operator-" + action,
                str(revision),
                body["data"]["reason"],
                response,
            )
            return response

    # ---- sign-in accounts --------------------------------------------------------------------

    def account_entry(self, c, account, lock=False):
        return c.execute(
            "SELECT * FROM impact.provider_account WHERE account_id=%s" + (" FOR UPDATE" if lock else ""),
            (account,),
        ).fetchone()

    def tenant_owner(self, c, identity, tenant):
        """The tenant row when `identity` is the current owner of this Active tenant, else None."""
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (str(tenant),))
        row = c.execute(
            "SELECT o.*,r.lifecycle_state FROM impact.tenant_onboarding o JOIN impact.tenant_root r USING(tenant_id) WHERE o.tenant_id=%s",
            (str(tenant),),
        ).fetchone()
        if (
            not row
            or str(row["owner_identity_id"]) != identity.identity_id
            or row["lifecycle_state"] != "Active"
        ):
            return None
        try:
            current_owner(c, row)
        except DomainError:
            return None
        return row

    def authorise_account(self, c, identity, action, data, digest, account=None):
        operator = self.lifecycle.operator(c, identity)
        if identity.verified_email_hash == digest:
            denied("SELF_ACCOUNT")
        if action == "reissue":
            if bytes(account["email_hash"]) != digest:
                raise DomainError("VALIDATION_FAILED", reason="EMAIL_MISMATCH")
            if operator:
                return
            if account["tenant_id"] and self.tenant_owner(c, identity, account["tenant_id"]):
                return
            unavailable()
        if data.get("tenant_id"):
            # A tenant owner, operator or not, for an invited address of their own Active tenant.
            if not self.tenant_owner(c, identity, data["tenant_id"]):
                unavailable()
            if data.get("nomination_id"):
                raise DomainError("VALIDATION_FAILED", reason="ONE_PURPOSE_ONLY")
            pending = c.execute(
                "SELECT impact.tenant_pending_invitation(%s,%s) AS pending", (data["tenant_id"], digest)
            ).fetchone()["pending"]
            if not pending:
                denied("INVITATION_REQUIRED")
            return
        if not operator:
            denied("PLATFORM_OPERATOR_REQUIRED")
        if data.get("nomination_id"):
            nomination = c.execute(
                "SELECT * FROM impact.platform_operator_nomination WHERE nomination_id=%s",
                (data["nomination_id"],),
            ).fetchone()
            if not nomination:
                unavailable()
            if (
                bytes(nomination["email_hash"]) != digest
                or nomination["state"] != "Nominated"
                or nomination["expires_at"] <= now()
            ):
                raise DomainError("CONFLICT_VERSION", 409, reason="NOMINATION_MISMATCH")

    def account(self, identity, action, body, account_id=None):
        if action not in ACCOUNT_ACTIONS | {"create"}:
            unavailable()
        validate_body(body, ACCOUNT_CREATE if action == "create" else ACCOUNT_REISSUE)
        self.lifecycle.assurance(identity)
        if self.accounts is None:
            raise DomainError("SERVICE_UNAVAILABLE", 503, reason="PROVIDER_ADMIN_NOT_CONFIGURED")
        data = body["data"]
        email = normalize_email(data["email"])
        digest = email_hash(email)
        fingerprint = hash_data({"account_action": action, "account": account_id, "body": body})
        # 1. Authorise, and answer a replay, before any call to the identity provider.
        with self.db.transaction(platform=True) as c:
            self.begin(c, identity, body["operation_id"])
            row = self.account_entry(c, account_id) if account_id else None
            if account_id and not row:
                unavailable()
            old = self.replay(c, identity, body["operation_id"], fingerprint)
            if old:
                return old
            if row and str(row["revision_id"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            self.authorise_account(c, identity, action, data, digest, row)
        # 2. The provider call, outside any transaction.
        if action == "create":
            result = self.accounts.create(email, data["first_name"].strip(), data["last_name"].strip())
        else:
            status = self.accounts.pending(email)
            if not status.get("exists") or status.get("subject") != row["provider_subject"]:
                unavailable()
            if not status.get("temporary_password_pending"):
                # The person has chosen their own password: their account is theirs alone now.
                raise DomainError("CONFLICT_VERSION", 409, reason="ACCOUNT_IN_USE")
            result = self.accounts.reissue(email)
        password = result["password"]
        # 3. Record it, rechecking the authority that step 1 saw.
        with self.db.transaction(platform=True) as c:
            self.begin(c, identity, body["operation_id"])
            old = self.replay(c, identity, body["operation_id"], fingerprint)
            if old:
                return old
            if account_id:
                row = self.account_entry(c, account_id, lock=True)
                if str(row["revision_id"]) != body["expected_revision"]:
                    raise DomainError("CONFLICT_VERSION", 409)
            self.authorise_account(c, identity, action, data, digest, row)
            revision = str(uuid4())
            if action == "create":
                row = c.execute(
                    "SELECT * FROM impact.provider_account WHERE issuer=%s AND provider_subject=%s FOR UPDATE",
                    (self.s.issuer, result["subject"]),
                ).fetchone()
                if row:
                    c.execute(
                        "UPDATE impact.provider_account SET revision_id=%s,updated_at=now(),credentials_issued=credentials_issued+%s,last_issued_at=CASE WHEN %s THEN now() ELSE last_issued_at END WHERE account_id=%s",
                        (revision, 1 if password else 0, password is not None, row["account_id"]),
                    )
                    account_id = str(row["account_id"])
                else:
                    account_id = str(uuid4())
                    c.execute(
                        "INSERT INTO impact.provider_account(account_id,revision_id,issuer,provider_subject,email_hash,email_mask,created_by,tenant_id,nomination_id,provider_created,credentials_issued,last_issued_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (
                            account_id,
                            revision,
                            self.s.issuer,
                            result["subject"],
                            digest,
                            masked_email(email),
                            identity.identity_id,
                            data.get("tenant_id"),
                            data.get("nomination_id"),
                            result["created"],
                            1 if password else 0,
                            now() if password else None,
                        ),
                    )
                c.execute("SELECT impact.register_provider_account_identity(%s)", (account_id,))
            else:
                c.execute(
                    "UPDATE impact.provider_account SET revision_id=%s,updated_at=now(),credentials_issued=credentials_issued+1,last_issued_at=now() WHERE account_id=%s",
                    (revision, account_id),
                )
            row = self.account_entry(c, account_id)
            response = {
                **self.present_account(row),
                "operation_id": body["operation_id"],
                "temporary_password": None,
                "password_shown": False,
                "sign_in_url": self.s.public_origin.rstrip("/") + "/",
            }
            self.record(
                c,
                identity,
                body["operation_id"],
                fingerprint,
                "account-" + action,
                revision,
                data["reason"],
                response,
                tenant=str(row["tenant_id"]) if row["tenant_id"] else None,
            )
        # The one place the one-time password exists outside the provider: this response.
        return {**response, "temporary_password": password, "password_shown": password is not None}
