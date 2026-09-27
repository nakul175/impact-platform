"""Self-service preferences and browser-session revocation, never identity editing."""

from datetime import datetime, timezone
from uuid import uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from jsonschema import Draft202012Validator, FormatChecker
from .auth import digest
from .domain import DomainError, unavailable

PREFERENCES = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "expected_revision": {"type": ["string", "null"], "format": "uuid"},
        "display_name": {"type": "string", "minLength": 1, "maxLength": 120},
        "language": {"const": "en"},
        "timezone": {"type": "string", "minLength": 1, "maxLength": 80},
        "reduced_motion": {"type": "boolean"},
    },
    "required": ["expected_revision", "display_name", "language", "timezone", "reduced_motion"],
}


class Account:
    def __init__(self, auth):
        self.auth, self.db = auth, auth.db

    def fresh(self, identity):
        if (
            datetime.now(timezone.utc) - identity.auth_time
        ).total_seconds() > 300 or not identity.assurance_verified:
            raise DomainError("ASSURANCE_REQUIRED", 403, reason="FRESH_AUTHENTICATION_REQUIRED")

    def event(self, c, identity, action, target=None):
        c.execute(
            "INSERT INTO impact.identity_security_event(event_id,identity_id,action,target_session) VALUES(%s,%s,%s,%s)",
            (str(uuid4()), identity.identity_id, action, target),
        )

    def preferences(self, identity):
        with self.db.transaction(identity=True) as c:
            row = c.execute(
                "SELECT * FROM impact.identity_preferences WHERE identity_id=%s", (identity.identity_id,)
            ).fetchone()
        return {
            "revision_id": str(row["revision_id"]) if row else None,
            "display_name": row["display_name"] if row else identity.display_name or "Member",
            "language": row["language"] if row else "en",
            "timezone": row["timezone"] if row else "UTC",
            "reduced_motion": row["reduced_motion"] if row else False,
        }

    def save_preferences(self, identity, body):
        if not Draft202012Validator(PREFERENCES, format_checker=FormatChecker()).is_valid(body):
            raise DomainError("VALIDATION_FAILED")
        try:
            ZoneInfo(body["timezone"])
        except (ZoneInfoNotFoundError, ValueError):
            raise DomainError("VALIDATION_FAILED", reason="TIMEZONE_INVALID") from None
        name = body["display_name"].strip()
        if not name or any(ord(c) < 32 for c in name):
            raise DomainError("VALIDATION_FAILED")
        with self.db.transaction(identity=True) as c:
            c.execute(
                "SELECT identity_id FROM impact.auth_identity WHERE identity_id=%s FOR UPDATE",
                (identity.identity_id,),
            )
            row = c.execute(
                "SELECT revision_id FROM impact.identity_preferences WHERE identity_id=%s",
                (identity.identity_id,),
            ).fetchone()
            if body["expected_revision"] != (str(row["revision_id"]) if row else None):
                raise DomainError("CONFLICT_VERSION", 409)
            revision = str(uuid4())
            c.execute(
                "INSERT INTO impact.identity_preferences(identity_id,display_name,language,timezone,reduced_motion,revision_id) VALUES(%s,%s,%s,%s,%s,%s) ON CONFLICT(identity_id) DO UPDATE SET display_name=EXCLUDED.display_name,language=EXCLUDED.language,timezone=EXCLUDED.timezone,reduced_motion=EXCLUDED.reduced_motion,revision_id=EXCLUDED.revision_id,updated_at=now()",
                (
                    identity.identity_id,
                    name,
                    body["language"],
                    body["timezone"],
                    body["reduced_motion"],
                    revision,
                ),
            )
            self.event(c, identity, "preferences.changed")
        return {
            "revision_id": revision,
            **{k: v for k, v in body.items() if k != "expected_revision"},
            "display_name": name,
        }

    def sessions(self, identity):
        with self.db.transaction(identity=True) as c:
            rows = c.execute(
                "SELECT session_id,session_hash,device_label,created_at,last_seen_at,expires_at FROM impact.web_session WHERE identity_id=%s AND revoked_at IS NULL AND expires_at>now() AND last_seen_at>now()-interval '15 minutes' ORDER BY created_at DESC LIMIT 50",
                (identity.identity_id,),
            ).fetchall()
        return {
            "items": [
                {
                    "session_id": str(r["session_id"]),
                    "device_label": r["device_label"],
                    "created_at": r["created_at"].isoformat(),
                    "last_seen_at": r["last_seen_at"].isoformat(),
                    "expires_at": r["expires_at"].isoformat(),
                    "current": bool(
                        identity.session_id and bytes(r["session_hash"]) == digest(identity.session_id)
                    ),
                }
                for r in rows
            ],
            "idle_minutes": 15,
            "absolute_hours": 8,
            "provider_account_url": self.auth.s.provider_account_url or None,
        }

    def revoke(self, identity, session_id=None):
        self.fresh(identity)
        with self.db.transaction(identity=True) as c:
            c.execute(
                "SELECT identity_id FROM impact.auth_identity WHERE identity_id=%s FOR UPDATE",
                (identity.identity_id,),
            )
            if session_id:
                row = c.execute(
                    "UPDATE impact.web_session SET revoked_at=COALESCE(revoked_at,now()) WHERE identity_id=%s AND session_id=%s RETURNING session_hash",
                    (identity.identity_id, session_id),
                ).fetchone()
                if not row:
                    unavailable()
                current = bool(
                    identity.session_id and bytes(row["session_hash"]) == digest(identity.session_id)
                )
            else:
                c.execute(
                    "UPDATE impact.web_session SET revoked_at=COALESCE(revoked_at,now()) WHERE identity_id=%s",
                    (identity.identity_id,),
                )
                c.execute(
                    "INSERT INTO impact.identity_security_state VALUES(%s,now()) ON CONFLICT(identity_id) DO UPDATE SET auth_not_before=EXCLUDED.auth_not_before",
                    (identity.identity_id,),
                )
                current = True
            self.event(
                c, identity, "sessions.revoke_all" if not session_id else "session.revoked", session_id
            )
        return {"revoked": True, "signed_out": current}
