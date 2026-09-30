"""Identity-provider administration for the deployment: realm import and account setup.

Runs inside the application image on the internal network and talks to Keycloak's admin REST API
directly (http://keycloak:8080 by default), never through the public reverse proxy. Standard
library only. Credentials arrive through the environment and are never printed:

    KC_URL                      Keycloak base URL on the internal network
    KC_ADMIN_USER / KC_ADMIN_PASSWORD   the master-realm bootstrap administrator
    IMPACT_REALM                realm name (default impact)
    IMPACT_PUBLIC_ORIGIN        https://<application host>, substituted into the client
    IMPACT_TEMP_PASSWORD        the temporary password for `user` / `reset`

Commands (each prints one JSON object without secrets):

    realm  --file F      import the realm when absent; when present, only re-align the web
                         client's origin-dependent URLs (users and credentials are never touched)
    user   --email E     create the account when absent: e-mail as username, e-mail marked
                         verified, required actions UPDATE_PASSWORD and CONFIGURE_TOTP and the
                         temporary password; an existing account is left unchanged
    status --email E     subject, whether the temporary password is still pending, whether a TOTP
                         authenticator is configured
    reset  --email E [--totp]   set a new temporary password (UPDATE_PASSWORD again); with --totp
                         also remove the account's TOTP authenticators (CONFIGURE_TOTP again)
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ORIGIN_PLACEHOLDER = "${PUBLIC_ORIGIN}"
CLIENT_ID = "impact-web"
REQUIRED_ACTIONS = ["UPDATE_PASSWORD", "CONFIGURE_TOTP"]


class AdminError(RuntimeError):
    pass


class Admin:
    def __init__(self, base, user, password, timeout=20):
        self.base, self.timeout = base.rstrip("/"), timeout
        self.token = self._token(user, password)

    def _token(self, user, password):
        body = urllib.parse.urlencode(
            {"grant_type": "password", "client_id": "admin-cli", "username": user, "password": password}
        ).encode()
        request = urllib.request.Request(
            self.base + "/realms/master/protocol/openid-connect/token", data=body, method="POST"
        )
        request.add_header("Content-Type", "application/x-www-form-urlencoded")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as r:
                return json.load(r)["access_token"]
        except urllib.error.HTTPError as e:
            if e.code >= 500:
                raise  # still starting (503 during bootstrap): connect() waits and retries
            raise AdminError("Administrator sign-in refused: HTTP " + str(e.code)) from None

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
            with urllib.request.urlopen(request, timeout=self.timeout) as r:
                raw = r.read()
                return r.status, (json.loads(raw) if raw else None), r.headers
        except urllib.error.HTTPError as e:
            if e.code in expect:
                return e.code, None, e.headers
            raise AdminError(method + " " + path.split("?")[0] + " failed: HTTP " + str(e.code)) from None


def realm_document(path, origin):
    if not origin.startswith("https://") and not origin.startswith("http://127.0.0.1"):
        raise AdminError("IMPACT_PUBLIC_ORIGIN must be an https:// origin")
    text = open(path, encoding="utf-8").read()
    if ORIGIN_PLACEHOLDER not in text:
        raise AdminError("The realm file carries no " + ORIGIN_PLACEHOLDER + " placeholder")
    document = json.loads(text.replace(ORIGIN_PLACEHOLDER, origin.rstrip("/")))
    if document.get("users"):
        raise AdminError("The deployment realm file must not contain users")
    return document


def client_fields(document):
    client = next(c for c in document["clients"] if c["clientId"] == CLIENT_ID)
    keys = ("post.logout.redirect.uris", "backchannel.logout.url")
    return {
        "redirectUris": client["redirectUris"],
        "webOrigins": client["webOrigins"],
        "attributes": {k: client["attributes"][k] for k in keys},
    }


def ensure_realm(admin, realm, document):
    status, _, _ = admin.call("GET", "/" + realm, expect=(200, 404))
    if status == 404:
        admin.call("POST", "", document)
        return {"realm": realm, "imported": True, "client_updated": False}
    status, clients, _ = admin.call("GET", "/" + realm + "/clients?clientId=" + CLIENT_ID)
    if not clients:
        raise AdminError("The realm exists without the " + CLIENT_ID + " client")
    current, wanted = clients[0], client_fields(document)
    changed = (
        current.get("redirectUris") != wanted["redirectUris"]
        or current.get("webOrigins") != wanted["webOrigins"]
        or any(current.get("attributes", {}).get(k) != v for k, v in wanted["attributes"].items())
    )
    if changed:
        updated = dict(current, redirectUris=wanted["redirectUris"], webOrigins=wanted["webOrigins"])
        updated["attributes"] = dict(current.get("attributes", {}), **wanted["attributes"])
        admin.call("PUT", "/" + realm + "/clients/" + current["id"], updated)
    return {"realm": realm, "imported": False, "client_updated": changed}


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
    return {"subject": user["id"], "password_reset": True, "totp_removed": removed}


def connect(env, attempts=60, delay=5):
    """The admin API, waiting for a provider that is still starting."""
    last = None
    for _ in range(attempts):
        try:
            return Admin(
                env.get("KC_URL", "http://keycloak:8080"), env["KC_ADMIN_USER"], env["KC_ADMIN_PASSWORD"]
            )
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            last = e
            time.sleep(delay)
    raise AdminError("Keycloak did not answer: " + type(last).__name__ + " " + str(last)[:100])


def main(argv=None, env=os.environ):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("realm").add_argument("--file", required=True)
    for name in ("user", "status", "reset"):
        s = sub.add_parser(name)
        s.add_argument("--email", required=True)
    sub.choices["user"].add_argument("--first-name", default="")
    sub.choices["user"].add_argument("--last-name", default="")
    sub.choices["reset"].add_argument("--totp", action="store_true")
    args = p.parse_args(argv)
    realm = env.get("IMPACT_REALM", "impact")
    try:
        admin = connect(env)
        if args.command == "realm":
            result = ensure_realm(
                admin, realm, realm_document(args.file, env.get("IMPACT_PUBLIC_ORIGIN", ""))
            )
        elif args.command == "user":
            result = ensure_user(
                admin, realm, args.email, env.get("IMPACT_TEMP_PASSWORD", ""), args.first_name, args.last_name
            )
        elif args.command == "status":
            result = user_status(admin, realm, args.email)
        else:
            result = reset_user(admin, realm, args.email, env.get("IMPACT_TEMP_PASSWORD", ""), args.totp)
    except AdminError as e:
        print(json.dumps({"error": str(e)}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
