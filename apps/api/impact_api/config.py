from dataclasses import dataclass, field
import json
import os
from pathlib import Path
from urllib.parse import urlparse

from . import keyring

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
    # Connection strings carry login passwords: never part of a repr.
    app_dsn: str = field(repr=False)
    identity_dsn: str = field(repr=False)
    public_origin: str
    issuer: str
    client_id: str
    audience: str
    jwks_url: str
    authorization_url: str
    token_url: str
    cookie_secret: str = field(repr=False)
    dev_auth: bool = False
    dev_db_serial: bool = False
    dev_users_file: str = ""
    dev_public_key: str = ""
    fixture_id: str = ""
    invitation_secret: str = field(default="", repr=False)
    required_acr: str = ""
    provider_account_url: str = ""
    platform_dsn: str = field(default="", repr=False)
    # A live provider (dev_auth off): the RP-initiated logout endpoint the browser is sent to after
    # the local session is revoked, and the client secret for a confidential client (normally
    # supplied as IMPACT_CLIENT_SECRET; a public client with S256 PKCE leaves it empty). The
    # platform holds no provider refresh token, so no revocation endpoint is configured.
    end_session_url: str = ""
    client_secret: str = field(default="", repr=False)
    # Refuse superuser, BYPASSRLS or owner database connections outside staging/production too;
    # native qualification sets it so the API runs on the provisioned login roles only.
    require_unprivileged_db: bool = False
    # Seals delivery addresses in the outbox and keys recovery-channel verification codes (v0.16).
    # Shared with the worker; empty disables email intents (invitations stay manual-only).
    delivery_secret: str = field(default="", repr=False)
    # Key rotation (v0.25 part A, impact_api/keyring.py): the previous secrets of each family kept for
    # a grace window, separated by commas or whitespace, newest first. Values made with one of them
    # (CSRF tokens, cursors, sealed recipients and logout hints, invitation links, recovery codes)
    # keep working until it is removed here; new values always use the current secret.
    cookie_secret_previous: str = field(default="", repr=False)
    invitation_secret_previous: str = field(default="", repr=False)
    delivery_secret_previous: str = field(default="", repr=False)
    # Development sign-in only: a JSON key set {"keys": [{"kid", "public_pem", "status"}]} of RS256
    # public keys that still verify fixture bearer tokens by their kid header during a grace window
    # (status "grace"); the current key is dev_public_key. scripts/rotate_secrets.py writes it.
    dev_signing_keys: str = ""
    # Private object store for evidence bytes (v0.22): an absolute directory only the API reads
    # (never served directly); empty disables uploads (SERVICE_UNAVAILABLE, OBJECT_STORE_NOT_CONFIGURED).
    # Only the filesystem backend is implemented. The scanner names the content_safety scanner that
    # decides each blob's verdict: "eicar-signature" (deterministic; recognises only the EICAR test
    # file, not an anti-malware engine) or "none" (every scan FAILED, nothing downloadable).
    object_store_backend: str = "filesystem"
    object_store_dir: str = ""
    evidence_scanner: str = ""
    # The server's operations summary (deploy/ops-check.sh: backup age, restore drill, disk, alerts),
    # an absolute path read by GET /v1/platform/metrics; empty reports no operations section.
    ops_status_file: str = ""
    # The published on-call rota (deploy/on-call.example.json), read by GET /v1/status for platform
    # operators; empty means `on-call.json` beside ops_status_file, or none at all.
    on_call_file: str = ""
    # Sign-in accounts created through the control plane (v0.26a, impact_api/provider_accounts.py):
    # "keycloak" (the realm's admin API through a service-account client limited to user management,
    # reached on the deployment's internal network), "development" (the development users file;
    # development sign-in only) or empty (account creation answers 503 PROVIDER_ADMIN_NOT_CONFIGURED).
    provider_admin: str = ""
    provider_admin_url: str = ""
    provider_admin_realm: str = ""
    provider_admin_client_id: str = ""
    provider_admin_client_secret: str = field(default="", repr=False)

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
        if s.object_store_dir and not Path(s.object_store_dir).is_absolute():
            raise ValueError("object_store_dir must be an absolute path")
        if s.ops_status_file and not Path(s.ops_status_file).is_absolute():
            raise ValueError("ops_status_file must be an absolute path")
        if s.on_call_file and not Path(s.on_call_file).is_absolute():
            raise ValueError("on_call_file must be an absolute path")
        if s.object_store_backend != "filesystem":
            raise ValueError("object_store_backend: only 'filesystem' is implemented")
        if s.evidence_scanner not in {"", "eicar-signature", "none"}:
            raise ValueError("evidence_scanner must be eicar-signature or none")
        if s.object_store_dir and not s.evidence_scanner:
            # No silent default: whoever enables evidence storage names the scanner that decides
            # what becomes downloadable.
            raise ValueError("An object store requires an explicitly configured evidence_scanner")
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
        if s.provider_admin not in {"", "keycloak", "development"}:
            raise ValueError("provider_admin must be keycloak, development or empty")
        if s.provider_admin == "development" and (
            not s.dev_auth or s.environment not in {"development", "test"} or not s.dev_users_file
        ):
            raise ValueError("Development provider accounts need development sign-in")
        if s.provider_admin == "keycloak" and (
            urlparse(s.provider_admin_url).scheme not in {"http", "https"}
            or urlparse(s.provider_admin_url).username
            or not s.provider_admin_realm
            or not s.provider_admin_client_id
            or len(s.provider_admin_client_secret) < 32
        ):
            raise ValueError(
                "Keycloak provider accounts need a URL, realm, client and a 32+ character secret"
            )
        keyring.validate(s)
        if s.dev_signing_keys and not s.dev_auth:
            raise ValueError("dev_signing_keys belongs to development sign-in only")
        return s
