"""Explicit control-plane authority, reviewed tenant activation and fail-closed lifecycle."""

from datetime import timedelta
from uuid import uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from psycopg.types.json import Jsonb
from .clock import now
from .domain import DomainError, unavailable
from .store import Context, write, hash_data, load
from .tenant_contracts import ACTIONS, validate_body


class TenantLifecycle:
    def __init__(self, settings, db):
        self.s, self.db = settings, db

    def operator(self, c, identity):
        return (
            c.execute(
                "SELECT 1 FROM impact.lock_platform_operator(%s) AS permitted WHERE permitted",
                (identity.identity_id,),
            ).fetchone()
            is not None
        )

    def assurance(self, identity):
        if not identity.assurance_verified or (now() - identity.auth_time).total_seconds() > 300:
            raise DomainError("ASSURANCE_REQUIRED", 403, reason="FRESH_MFA_REQUIRED")

    def entry(self, c, tenant):
        return c.execute(
            "SELECT o.*,r.lifecycle_state,r.region_policy FROM impact.tenant_onboarding o JOIN impact.tenant_root r USING(tenant_id) WHERE o.tenant_id=%s FOR UPDATE OF o,r",
            (tenant,),
        ).fetchone()

    def readiness(self, c, row):
        from .recovery_contacts import current_status

        q = c.execute(
            "SELECT * FROM impact.lock_deployment_qualification(%s)",
            (row["qualification_id"],),
        ).fetchone()
        checks = {
            "owner_accepted": row["owner_accepted_at"] is not None,
            "qualified_deployment": bool(q and q["active"] and q["valid_until"] > now()),
            "qualification_unchanged": bool(q and q["revision_id"] == row["qualification_revision"]),
            "environment_matches": bool(q and q["environment"] == self.s.environment),
            "region_matches": bool(q and q["region"] == row["region_policy"]),
            "identity_policy_matches": bool(
                q and q["issuer"] == self.s.issuer and q["required_acr"] == self.s.required_acr
            ),
            "privacy_policy_matches": bool(q and q["privacy_reference"] == row["privacy_reference"]),
            "retention_supported": bool(q and row["retention_days"] <= q["retention_max_days"]),
            "recovery_evidence_present": bool(q and q["recovery_reference"].strip()),
            "owner_membership_active": False,
            "recovery_contact_verified": current_status(c, row, self.s.issuer)["eligible"],
        }
        if row["owner_membership_id"]:
            checks["owner_membership_active"] = bool(
                c.execute(
                    "SELECT 1 FROM impact.membership_current m JOIN impact.object_registry r ON r.tenant_id=m.tenant_id AND r.object_id=m.object_id JOIN impact.tenant_principal p ON p.tenant_id=m.tenant_id AND p.identity_id=m.identity_id JOIN impact.tenant_custody t ON t.tenant_id=m.tenant_id AND t.owner_membership_id=m.object_id WHERE m.tenant_id=%s AND p.active AND r.lifecycle_state='Active' AND (m.expires_at IS NULL OR m.expires_at>now())",
                    (row["tenant_id"],),
                ).fetchone()
            )
        return checks

    def present(self, c, row):
        from .recovery_contacts import current_status

        return {
            "tenant_id": str(row["tenant_id"]),
            "revision_id": str(row["revision_id"]),
            "state": row["lifecycle_state"],
            "operating_name": row["operating_name"],
            "owner_identity_id": str(row["owner_identity_id"]),
            "region": row["region_policy"],
            "reporting_zone": row["reporting_zone"],
            "retention_days": row["retention_days"],
            "privacy_reference": row["privacy_reference"],
            "owner_expires_at": row["owner_expires_at"].isoformat(),
            "readiness": self.readiness(c, row),
            "recovery_contact": current_status(c, row, self.s.issuer),
            "impact": c.execute(
                "SELECT impact.tenant_work_impact(%s) AS impact", (row["tenant_id"],)
            ).fetchone()["impact"],
        }

    def directory(self, identity, after=None):
        if not self.s.platform_dsn:
            return {"operator": False, "items": [], "next_cursor": None, "qualifications": []}
        with self.db.transaction(platform=True) as c:
            operator = self.operator(c, identity)
            rows = c.execute(
                "SELECT tenant_id FROM impact.tenant_onboarding WHERE (%s OR owner_identity_id=%s) AND (%s::uuid IS NULL OR tenant_id>%s::uuid) ORDER BY tenant_id LIMIT 51",
                (operator, identity.identity_id, after, after),
            ).fetchall()
            qualifications = (
                c.execute(
                    "SELECT qualification_id,region,environment,privacy_reference,retention_max_days FROM impact.deployment_qualification WHERE active AND valid_until>now() AND environment=%s ORDER BY qualification_id LIMIT 100",
                    (self.s.environment,),
                ).fetchall()
                if operator
                else []
            )
            result = []
            for item in rows[:50]:
                tenant = str(item["tenant_id"])
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
                result.append(self.present(c, self.entry(c, tenant)))
            return {
                "operator": operator,
                "items": result,
                "next_cursor": str(rows[49]["tenant_id"]) if len(rows) > 50 else None,
                "qualifications": [
                    dict(q, qualification_id=str(q["qualification_id"])) for q in qualifications
                ],
            }

    def command(self, identity, action, body, tenant=None):
        if action not in ACTIONS | {"request"}:
            unavailable()
        validate_body(body, create=action == "request")
        self.assurance(identity)
        fingerprint = hash_data({"action": action, "tenant": tenant, "body": body})
        with self.db.transaction(platform=True) as c:
            # Same identity operation serialises even when it creates a new tenant UUID.
            c.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",
                ("platform:" + identity.identity_id + ":" + body["operation_id"],),
            )
            operator = self.operator(c, identity)
            if action != "accept-owner" and not operator:
                raise DomainError("POLICY_DENIED", 403, reason="PLATFORM_OPERATOR_REQUIRED")
            row = None
            if tenant:
                c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
                c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
                row = self.entry(c, tenant)
                if not row or (
                    action == "accept-owner" and str(row["owner_identity_id"]) != identity.identity_id
                ):
                    unavailable()
            old = c.execute(
                "SELECT * FROM impact.platform_receipt WHERE identity_id=%s AND operation_id=%s",
                (identity.identity_id, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["fingerprint"]) != fingerprint or old["expires_at"] <= now():
                    raise DomainError("CONFLICT_VERSION", 409, reason="OPERATION_REUSE")
                return old["response"]
            if row and str(row["revision_id"]) != body["expected_revision"]:
                raise DomainError("CONFLICT_VERSION", 409)
            if action == "request":
                row = self.request(c, identity, body["data"])
                tenant = str(row["tenant_id"])
            elif action == "accept-owner":
                self.accept(c, identity, row)
            else:
                self.transition(c, identity, row, action)
            revision = str(uuid4())
            c.execute(
                "UPDATE impact.tenant_onboarding SET revision_id=%s,updated_at=now() WHERE tenant_id=%s",
                (revision, tenant),
            )
            row = self.entry(c, tenant)
            response = self.present(c, row)
            response["operation_id"] = body["operation_id"]
            c.execute(
                "INSERT INTO impact.platform_event(event_id,tenant_id,identity_id,action,revision_id,reason,payload) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                (
                    str(uuid4()),
                    tenant,
                    identity.identity_id,
                    action,
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

    def request(self, c, identity, data):
        try:
            ZoneInfo(data["reporting_zone"])
        except (ZoneInfoNotFoundError, ValueError):
            raise DomainError("VALIDATION_FAILED", reason="INVALID_TIME_ZONE") from None
        q = c.execute(
            "SELECT * FROM impact.lock_deployment_qualification(%s) WHERE active AND valid_until>now()",
            (data["qualification_id"],),
        ).fetchone()
        owner = c.execute(
            "SELECT i.* FROM impact.auth_identity i JOIN impact.identity_profile p USING(identity_id) WHERE identity_id=%s AND p.verified_email_hash IS NOT NULL",
            (data["owner_identity_id"],),
        ).fetchone()
        if not q or not owner or owner["issuer"] != self.s.issuer:
            unavailable()
        # The row carries a UUID and the resolved identity a str: compare one representation.
        if str(owner["natural_identity_id"]) == str(identity.natural_identity_id):
            raise DomainError("POLICY_DENIED", 403, reason="INDEPENDENCE_REQUIRED")
        tenant = str(uuid4())
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        c.execute("INSERT INTO impact.tenant_root VALUES(%s,%s,'Requested',0)", (tenant, q["region"]))
        c.execute(
            "INSERT INTO impact.tenant_onboarding(tenant_id,revision_id,requested_by,owner_identity_id,qualification_id,qualification_revision,operating_name,reporting_zone,retention_days,privacy_reference,owner_expires_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                tenant,
                str(uuid4()),
                identity.identity_id,
                data["owner_identity_id"],
                q["qualification_id"],
                q["revision_id"],
                data["operating_name"].strip(),
                data["reporting_zone"],
                data["retention_days"],
                data["privacy_reference"],
                now() + timedelta(days=7),
            ),
        )
        row = self.entry(c, tenant)
        checks = self.readiness(c, row)
        if not all(
            v
            for k, v in checks.items()
            if k not in {"owner_accepted", "owner_membership_active", "recovery_contact_verified"}
        ):
            raise DomainError("VALIDATION_FAILED", reason="DEPLOYMENT_POLICY_MISMATCH")
        return row

    def accept(self, c, identity, row):
        if (
            row["lifecycle_state"] != "Requested"
            or row["owner_expires_at"] <= now()
            or not identity.verified_email_hash
        ):
            raise DomainError("POLICY_DENIED", 403, reason="OWNER_ACCEPTANCE_UNAVAILABLE")
        tenant = str(row["tenant_id"])
        principal = str(uuid4())
        c.execute(
            "INSERT INTO impact.tenant_principal(tenant_id,principal_id,identity_id,principal_kind) VALUES(%s,%s,%s,'HUMAN')",
            (tenant, principal, identity.identity_id),
        )
        ctx = Context(tenant, principal, "", identity, 0, 0, [])
        membership = write(
            c,
            ctx,
            "Membership",
            {
                "identity_id": identity.identity_id,
                "authority_source": "Accepted tenant custody nomination",
                "external": False,
                "status": "Active",
                "joined_at": now().isoformat(),
            },
            "Active",
            track_author=False,
        )
        c.execute("INSERT INTO impact.tenant_custody VALUES(%s,%s)", (tenant, membership["object_id"]))
        c.execute(
            "INSERT INTO impact.member_profile VALUES(%s,%s,%s,%s)",
            (tenant, membership["object_id"], identity.display_name or "Owner", identity.email_mask),
        )
        policy_ids = {}
        for kind, payload in [
            (
                "HostingPolicy",
                {"region": row["region_policy"], "qualification_id": str(row["qualification_id"])},
            ),
            ("PrivacyPolicy", {"reference": row["privacy_reference"]}),
            (
                "RetentionPolicy",
                {
                    "data_class": "TENANT_DATA",
                    "purpose": "IMPACT_MANAGEMENT",
                    "trigger": "CLOSURE",
                    "duration_days": row["retention_days"],
                    "expiry_action": "REVIEW",
                },
            ),
        ]:
            policy_ids[kind] = write(c, ctx, kind, payload, "Configured", track_author=False)["object_id"]
        record = write(
            c,
            ctx,
            "Tenant",
            {
                "operating_name": row["operating_name"],
                "owner_membership_id": membership["object_id"],
                "reporting_zone": row["reporting_zone"],
                "hosting_policy_id": policy_ids["HostingPolicy"],
                "privacy_policy_id": policy_ids["PrivacyPolicy"],
                "retention_policy_id": policy_ids["RetentionPolicy"],
            },
            "Provisioning",
            track_author=False,
        )
        c.execute(
            "UPDATE impact.tenant_onboarding SET owner_accepted_at=now(),owner_membership_id=%s,tenant_object_id=%s WHERE tenant_id=%s",
            (membership["object_id"], record["object_id"], tenant),
        )
        c.execute(
            "UPDATE impact.tenant_root SET lifecycle_state='Provisioning' WHERE tenant_id=%s", (tenant,)
        )

    def transition(self, c, identity, row, action):
        states = {
            "activate": ({"Provisioning"}, "Active"),
            "suspend": ({"Active"}, "Suspended"),
            "reactivate": ({"Suspended"}, "Active"),
            "begin-closure": ({"Active", "Suspended"}, "Closing"),
        }
        allowed, target = states[action]
        if row["lifecycle_state"] not in allowed:
            raise DomainError("CONFLICT_VERSION", 409, reason="INVALID_TENANT_TRANSITION")
        if target == "Active":
            requester = c.execute(
                "SELECT natural_identity_id FROM impact.auth_identity WHERE identity_id=%s",
                (row["requested_by"],),
            ).fetchone()
            owner = c.execute(
                "SELECT natural_identity_id FROM impact.auth_identity WHERE identity_id=%s",
                (row["owner_identity_id"],),
            ).fetchone()
            if identity.natural_identity_id in {
                str(requester["natural_identity_id"]),
                str(owner["natural_identity_id"]),
            }:
                raise DomainError("POLICY_DENIED", 403, reason="INDEPENDENCE_REQUIRED")
            if not all(self.readiness(c, row).values()):
                raise DomainError("POLICY_DENIED", 403, reason="TENANT_NOT_READY")
        tenant = str(row["tenant_id"])
        operator_principal = c.execute(
            "INSERT INTO impact.tenant_principal(tenant_id,principal_id,identity_id,principal_kind) VALUES(%s,%s,%s,'HUMAN') ON CONFLICT(tenant_id,identity_id) DO UPDATE SET identity_id=EXCLUDED.identity_id RETURNING principal_id",
            (tenant, str(uuid4()), identity.identity_id),
        ).fetchone()
        # Provenance principal is not a membership and conveys no tenant access.
        ctx = Context(tenant, str(operator_principal["principal_id"]), "", identity, 0, 0, [])
        record = load(c, ctx, row["tenant_object_id"], "Tenant", lock=True)
        write(c, ctx, "Tenant", record["payload"], target, record, track_author=False)
        c.execute(
            "UPDATE impact.tenant_root SET lifecycle_state=%s,policy_epoch=policy_epoch+1 WHERE tenant_id=%s",
            (target, tenant),
        )
        if target in {"Suspended", "Closing"}:
            c.execute(
                "UPDATE impact.tenant_principal SET auth_not_before=now(),subject_epoch=subject_epoch+1 WHERE tenant_id=%s",
                (tenant,),
            )
            c.execute("SELECT impact.quiesce_tenant(%s)", (tenant,))
