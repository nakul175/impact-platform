from dataclasses import dataclass
import json
import os
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[3]
BOOLEAN_FIELDS = {"dev_auth", "dev_db_serial", "require_unprivileged_db"}
TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off", ""}


def boolean(name, value):
    """An environment flag: 1/true/yes/on or 0/false/no/off, case-insensitively; anything else is
    a configuration error rather than a silent False."""
    lowered = value.strip().lower()
    if lowered in TRUE_VALUES:
        return True
    if lowered in FALSE_VALUES:
        return False
    raise ValueError(
        "IMPACT_" + name.upper() + " must be one of 1/true/yes/on or 0/false/no/off, not " + repr(value)
    )


@dataclass(frozen=True)
class Settings:
    environment: str
    app_dsn: str
    identity_dsn: str
    public_origin: str
    issuer: str
    client_id: str
    audience: str
    jwks_url: str
    authorization_url: str
    token_url: str
    cookie_secret: str
    dev_auth: bool = False
    dev_db_serial: bool = False
    dev_users_file: str = ""
    dev_public_key: str = ""
    fixture_id: str = ""
    invitation_secret: str = ""
    required_acr: str = ""
    provider_account_url: str = ""
    platform_dsn: str = ""
    # A live provider (dev_auth off): the RP-initiated logout endpoint the browser is sent to after
    # the local session is revoked, and the client secret for a confidential client (normally
    # supplied as IMPACT_CLIENT_SECRET; a public client with S256 PKCE leaves it empty). The
    # platform holds no provider refresh token, so no revocation endpoint is configured.
    end_session_url: str = ""
    client_secret: str = ""
    # Refuse superuser, BYPASSRLS or owner database connections outside staging/production too;
    # native qualification sets it so the API runs on the provisioned login roles only.
    require_unprivileged_db: bool = False
    # Seals delivery addresses in the outbox and keys recovery-channel verification codes (v0.16).
    # Shared with the worker; empty disables email intents (invitations stay manual-only).
    delivery_secret: str = ""

    @property
    def unprivileged_db_required(self):
        return self.environment in {"staging", "production"} or self.require_unprivileged_db

    @property
    def secure(self):
        return self.public_origin.startswith("https://")

    @property
    def cookie_name(self):
        return "__Host-impact_session" if self.secure else "impact_dev_session"

    @classmethod
    def load(cls):
        data = (
            json.loads(Path(os.environ["IMPACT_CONFIG_FILE"]).read_text())
            if os.environ.get("IMPACT_CONFIG_FILE")
            else {}
        )
        for name in cls.__dataclass_fields__:
            value = os.environ.get("IMPACT_" + name.upper())
            if value is not None:
                data[name] = boolean(name, value) if name in BOOLEAN_FIELDS else value
        for name in BOOLEAN_FIELDS:
            if name in data and not isinstance(data[name], bool):
                raise ValueError("Configuration field " + name + " must be a JSON boolean")
        s = cls(**data)
        if s.environment not in {"development", "test", "staging", "production"} or len(s.cookie_secret) < 48:
            raise ValueError("Invalid environment or cookie secret")
        if s.environment in {"staging", "production"}:
            if len(s.invitation_secret) < 48 or s.invitation_secret == s.cookie_secret:
                raise ValueError("A separate invitation signing secret is required")
            if s.dev_auth or s.dev_db_serial or s.fixture_id:
                raise ValueError("Development settings are forbidden in production")
            if len(s.delivery_secret) < 48 or s.delivery_secret in {s.cookie_secret, s.invitation_secret}:
                raise ValueError("A separate delivery secret is required")
            if not s.required_acr or len(s.required_acr) > 200:
                raise ValueError("A provider-verified MFA assurance class is required")
            if any(
                urlparse(u).scheme != "https"
                for u in [s.public_origin, s.issuer, s.jwks_url, s.authorization_url, s.token_url]
                + ([s.end_session_url] if s.end_session_url else [])
            ):
                raise ValueError("HTTPS required")
        if s.delivery_secret and len(s.delivery_secret) < 48:
            raise ValueError("A delivery secret must be at least 48 characters")
        if s.client_secret and (len(s.client_secret) < 32 or s.dev_auth):
            raise ValueError("A client secret must be at least 32 characters and needs a live provider")
        if not s.dev_auth and s.environment in {"development", "test"} and s.jwks_url:
            for u in [s.issuer, s.jwks_url, s.authorization_url, s.token_url] + (
                [s.end_session_url] if s.end_session_url else []
            ):
                parsed = urlparse(u)
                if parsed.scheme != "https" and not (
                    parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost"}
                ):
                    raise ValueError("A plain-HTTP identity provider is allowed only on loopback")
        if s.provider_account_url and (
            urlparse(s.provider_account_url).scheme != "https"
            or urlparse(s.provider_account_url).username
            or urlparse(s.provider_account_url).fragment
        ):
            raise ValueError("Provider account management requires a fixed HTTPS URL")
        if s.dev_auth and (
            s.environment not in {"development", "test"}
            or urlparse(s.public_origin).hostname not in {"127.0.0.1", "localhost"}
        ):
            raise ValueError("Local identity requires loopback development")
        return s
