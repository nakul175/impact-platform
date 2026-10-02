"""Identity-provider (Keycloak) account administration shared by the deployment console scripts and
the control plane (v0.26a). Standard library only, so deploy/keycloak_admin.py imports it unchanged.

`ensure_user`, `user_status` and `reset_user` are the logic behind deploy/add-user.sh and
deploy/reset-user.sh; the control plane's account operations (impact_api/operators.py) call the same
functions with a realm-scoped service account (`ServiceAccountAdmin`: client credentials of the
`impact-provisioner` client, realm-management roles manage-users and view-users only) instead of the
master-realm administrator. Neither ever logs or returns a password; the caller supplies the
temporary password and decides where it is shown.
"""

import json
import secrets
import urllib.error
import urllib.parse
import urllib.request

REQUIRED_ACTIONS = ["UPDATE_PASSWORD", "CONFIGURE_TOTP"]
# Unambiguous lower-case letters and digits, as deploy/lib.sh readable_password.
ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"


class AdminError(RuntimeError):
    pass


def readable_password():
    """A one-time password of five groups of four (about 99 bits)."""
    return "-".join("".join(secrets.choice(ALPHABET) for _ in range(4)) for _ in range(5))


class ServiceAccountAdmin:
    """The admin REST API of one realm through a confidential client's service account. `call` has the
    signature of deploy/keycloak_admin.py Admin.call; paths start at /admin/realms."""

    def __init__(self, base, realm, client_id, client_secret, timeout=10, opener=None):
        self.base, self.realm, self.timeout = base.rstrip("/"), realm, timeout
        self.opener = opener or urllib.request.build_opener(urllib.request.ProxyHandler({}))
        body = urllib.parse.urlencode(
            {"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret}
        ).encode()
        request = urllib.request.Request(
            self.base + "/realms/" + urllib.parse.quote(realm) + "/protocol/openid-connect/token",
            data=body,
            method="POST",
        )
        request.add_header("Content-Type", "application/x-www-form-urlencoded")
        try:
            with self.opener.open(request, timeout=timeout) as r:
                self.token = json.load(r)["access_token"]
        except urllib.error.HTTPError as e:
            raise AdminError("Provider administrator sign-in refused: HTTP " + str(e.code)) from None
        except (urllib.error.URLError, OSError, ValueError, KeyError):
            raise AdminError("The identity provider did not answer") from None

    def call(self, method, path, data=None, expect=(200, 201, 204)):
        request = urllib.request.Request(
            self.base + "/admin/realms" + path,
            data=None if data is None else json.dumps(data).encode(),
            method=method,
        )
        request.add_header("Authorization", "Bearer " + self.token)
        if data is not None:
            request.add_header("Content-Type", "application/json")
        try:
            with self.opener.open(request, timeout=self.timeout) as r:
                raw = r.read()
                return r.status, (json.loads(raw) if raw else None), r.headers
        except urllib.error.HTTPError as e:
            if e.code in expect:
                return e.code, None, e.headers
            raise AdminError(method + " " + path.split("?")[0] + " failed: HTTP " + str(e.code)) from None
        except (urllib.error.URLError, OSError):
            raise AdminError("The identity provider did not answer") from None


def find_user(admin, realm, email):
    query = urllib.parse.urlencode({"email": email, "exact": "true", "briefRepresentation": "false"})
    _, users, _ = admin.call("GET", "/" + realm + "/users?" + query)
    matches = [u for u in users or [] if (u.get("email") or "").lower() == email.lower()]
    return matches[0] if matches else None


def check_password(password):
    if len(password) < 12:
        raise AdminError("IMPACT_TEMP_PASSWORD must be at least 12 characters")


def ensure_user(admin, realm, email, password, first="", last=""):
    user = find_user(admin, realm, email)
    if user:
        return {"subject": user["id"], "created": False}
    check_password(password)
    body = {
        "username": email.lower(),
        "email": email.lower(),
        "enabled": True,
        "emailVerified": True,
        "requiredActions": REQUIRED_ACTIONS,
        "credentials": [{"type": "password", "value": password, "temporary": True}],
    }
    if first:
        body["firstName"] = first
    if last:
        body["lastName"] = last
    admin.call("POST", "/" + realm + "/users", body)
    user = find_user(admin, realm, email)
    if not user:
        raise AdminError("The account was not created")
    return {"subject": user["id"], "created": True}


def user_status(admin, realm, email):
    user = find_user(admin, realm, email)
    if not user:
        return {"exists": False}
    _, credentials, _ = admin.call("GET", "/" + realm + "/users/" + user["id"] + "/credentials")
    return {
        "exists": True,
        "subject": user["id"],
        "enabled": bool(user.get("enabled")),
        "temporary_password_pending": "UPDATE_PASSWORD" in (user.get("requiredActions") or []),
        "totp_configured": any(c.get("type") == "otp" for c in credentials or []),
    }


def reset_user(admin, realm, email, password, totp=False):
    user = find_user(admin, realm, email)
    if not user:
        raise AdminError("No account with that e-mail address")
    check_password(password)
    path = "/" + realm + "/users/" + user["id"]
    admin.call("PUT", path + "/reset-password", {"type": "password", "value": password, "temporary": True})
    removed = 0
    if totp:
        _, credentials, _ = admin.call("GET", path + "/credentials")
        for credential in credentials or []:
            if credential.get("type") == "otp":
                admin.call("DELETE", path + "/credentials/" + credential["id"])
                removed += 1
    actions = list(dict.fromkeys((user.get("requiredActions") or []) + REQUIRED_ACTIONS))
    admin.call("PUT", path, {"requiredActions": actions, "enabled": True})
    # A reset is the recovery path after failed sign-ins, so it also lifts any temporary
    # brute-force lockout; otherwise the new password is refused until the lockout expires.
    admin.call("DELETE", "/" + realm + "/attack-detection/brute-force/users/" + user["id"])
    return {"subject": user["id"], "password_reset": True, "totp_removed": removed, "lockout_cleared": True}
