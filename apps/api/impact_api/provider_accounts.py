"""Identity-provider accounts created through the control plane (v0.26a, gap A3).

Two backends, chosen by configuration (`provider_admin`):

- "keycloak" (staging): the realm's admin REST API through the `impact-provisioner` service account
  (client credentials; realm-management roles manage-users, view-users and query-users only, never the
  master realm). Account creation and credential reissue use exactly the functions behind
  deploy/add-user.sh and deploy/reset-user.sh (impact_api/provider_admin.py): e-mail as username,
  e-mail marked verified, a temporary password and the required actions UPDATE_PASSWORD and
  CONFIGURE_TOTP, so the person chooses a password and enrols an authenticator at first sign-in.
- "development" (local development and the PGlite suites only, with development sign-in): the
  development users file, so a created account can sign in on the development login page.

The temporary password is generated here and returned to the caller once; it is never stored, logged,
written to a receipt or event, or returned on a replay.
"""

import fcntl
import hashlib
import json
import os
import secrets
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4
from .domain import DomainError
from .provider_admin import (
    AdminError,
    ServiceAccountAdmin,
    ensure_user,
    find_user,
    readable_password,
    reset_user,
    user_status,
)


def unavailable_provider():
    raise DomainError("SERVICE_UNAVAILABLE", 503, reason="PROVIDER_ADMIN_UNAVAILABLE")


class KeycloakAccounts:
    def __init__(self, s):
        self.s = s

    def admin(self):
        try:
            return ServiceAccountAdmin(
                self.s.provider_admin_url,
                self.s.provider_admin_realm,
                self.s.provider_admin_client_id,
                self.s.provider_admin_client_secret,
            )
        except AdminError:
            unavailable_provider()

    def create(self, email, first, last):
        password = readable_password()
        try:
            result = ensure_user(self.admin(), self.s.provider_admin_realm, email, password, first, last)
        except AdminError:
            unavailable_provider()
        return {
            "subject": result["subject"],
            "created": result["created"],
            "password": password if result["created"] else None,
        }

    def pending(self, email):
        try:
            status = user_status(self.admin(), self.s.provider_admin_realm, email)
        except AdminError:
            unavailable_provider()
        return status

    def reissue(self, email):
        password = readable_password()
        try:
            admin = self.admin()
            if not find_user(admin, self.s.provider_admin_realm, email):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            result = reset_user(admin, self.s.provider_admin_realm, email, password, totp=False)
        except AdminError:
            unavailable_provider()
        return {"subject": result["subject"], "password": password}


class DevelopmentAccounts:
    """Accounts in the development users file (development sign-in only). The file maps a user name
    (here the e-mail address) to a subject and a PBKDF2 password hash; `temporary` marks an account
    whose first password has not been used yet (cleared by the first development sign-in)."""

    def __init__(self, s):
        self.path = Path(s.dev_users_file)

    @contextmanager
    def users(self):
        lock = self.path.with_suffix(".lock")
        with open(lock, "a") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                data = json.loads(self.path.read_text()) if self.path.exists() else {}
                yield data
                temporary = self.path.with_suffix(".tmp")
                fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
                with os.fdopen(fd, "w") as f:
                    f.write(json.dumps(data))
                os.replace(temporary, self.path)
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    @staticmethod
    def entry(password, subject, email, name):
        salt = secrets.token_bytes(24)
        return {
            "subject": subject,
            "salt": salt.hex(),
            "password_hash": hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600000).hex(),
            "email": email,
            "name": name,
            "temporary": True,
        }

    def create(self, email, first, last):
        with self.users() as data:
            existing = data.get(email)
            if existing:
                return {"subject": existing["subject"], "created": False, "password": None}
            password = readable_password()
            subject = str(uuid4())
            data[email] = self.entry(password, subject, email, (first + " " + last).strip())
            return {"subject": subject, "created": True, "password": password}

    def pending(self, email):
        data = json.loads(self.path.read_text()) if self.path.exists() else {}
        user = data.get(email)
        if not user:
            return {"exists": False}
        return {
            "exists": True,
            "subject": user["subject"],
            "temporary_password_pending": bool(user.get("temporary")),
        }

    def reissue(self, email):
        with self.users() as data:
            user = data.get(email)
            if not user:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            password = readable_password()
            data[email] = self.entry(password, user["subject"], email, user.get("name", ""))
            return {"subject": user["subject"], "password": password}


def mark_signed_in(users_file, username):
    """The first development sign-in consumes the temporary flag of a created account."""
    path = Path(users_file)
    lock = path.with_suffix(".lock")
    with open(lock, "a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            data = json.loads(path.read_text())
            if data.get(username, {}).get("temporary"):
                data[username]["temporary"] = False
                temporary = path.with_suffix(".tmp")
                fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
                with os.fdopen(fd, "w") as f:
                    f.write(json.dumps(data))
                os.replace(temporary, path)
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def backend(s):
    if s.provider_admin == "keycloak":
        return KeycloakAccounts(s)
    if s.provider_admin == "development":
        return DevelopmentAccounts(s)
    return None
