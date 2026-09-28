from dataclasses import dataclass
import json
import os
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[3]


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
    # Refuse superuser, BYPASSRLS or owner database connections outside staging/production too;
    # native qualification sets it so the API runs on the provisioned login roles only.
    require_unprivileged_db: bool = False

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
                data[name] = (
                    value == "1"
                    if name in {"dev_auth", "dev_db_serial", "require_unprivileged_db"}
                    else value
                )
        s = cls(**data)
        if s.environment not in {"development", "test", "staging", "production"} or len(s.cookie_secret) < 48:
            raise ValueError("Invalid environment or cookie secret")
        if s.environment in {"staging", "production"}:
            if len(s.invitation_secret) < 48 or s.invitation_secret == s.cookie_secret:
                raise ValueError("A separate invitation signing secret is required")
            if s.dev_auth or s.dev_db_serial or s.fixture_id:
                raise ValueError("Development settings are forbidden in production")
            if not s.required_acr or len(s.required_acr) > 200:
                raise ValueError("A provider-verified MFA assurance class is required")
            if any(
                urlparse(u).scheme != "https"
                for u in [s.public_origin, s.issuer, s.jwks_url, s.authorization_url, s.token_url]
            ):
                raise ValueError("HTTPS required")
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
