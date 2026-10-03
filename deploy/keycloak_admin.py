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
    list                 every account of the realm (at most 500): e-mail, name, enabled, whether a
                         temporary password is pending, whether an authenticator is configured,
                         whether sign-in is temporarily locked after failed attempts
    rotate-provisioner   (v0.27) set the `impact-provisioner` client secret to IMPACT_PROVISIONER_SECRET
                       after scripts/rotate_secrets.py rotated it (deploy/rotate-secrets.sh runs it)
  provisioner          (v0.26a) ensure the confidential client `impact-provisioner` with a service
                         account holding only the realm-management roles manage-users, view-users
                         and query-users, and the client secret from IMPACT_PROVISIONER_SECRET; the
                         API uses it to create sign-in accounts from the control plane

The account functions (`ensure_user`, `user_status`, `reset_user`) live in
apps/api/impact_api/provider_admin.py, which the control plane calls with the provisioner's service
account: add-user.sh and the platform's "create sign-in" operation run the same logic.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

try:  # in the image PYTHONPATH holds /app/apps/api
    from impact_api.provider_admin import (  # noqa: F401
        REQUIRED_ACTIONS,
        AdminError,
        check_password,
        ensure_user,
        find_user,
        reset_user,
        user_status,
    )
except ImportError:  # a repository checkout
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps/api"))
    from impact_api.provider_admin import (  # noqa: F401
        REQUIRED_ACTIONS,
        AdminError,
        check_password,
        ensure_user,
        find_user,
        reset_user,
        user_status,
    )

ORIGIN_PLACEHOLDER = "${PUBLIC_ORIGIN}"
CLIENT_ID = "impact-web"
PROVISIONER_ID = "impact-provisioner"
PROVISIONER_ROLES = ["manage-users", "view-users", "query-users"]


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
        return {"realm": realm, "imported": True, "client_updated": False, "policy_updated": False}
    # The password policy is the one realm setting kept aligned after import (the staging owner
    # may relax or tighten it in the repository); every other realm setting is import-only.
    policy_updated = current_policy(admin, realm) != document.get("passwordPolicy")
    if policy_updated:
        admin.call("PUT", "/" + realm, {"passwordPolicy": document.get("passwordPolicy")})
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
    return {"realm": realm, "imported": False, "client_updated": changed, "policy_updated": policy_updated}


def current_policy(admin, realm):
    _, body, _ = admin.call("GET", "/" + realm)
    return (body or {}).get("passwordPolicy")


def ensure_provisioner(admin, realm, secret, client_id=PROVISIONER_ID):
    """The confidential client the API uses to create sign-in accounts (v0.26a): client credentials
    only (no browser, password or implicit flow), its service account holding exactly the
    realm-management roles manage-users, view-users and query-users. Idempotent; the secret is
    re-aligned when it changed and never printed."""
    if len(secret) < 32:
        raise AdminError("IMPACT_PROVISIONER_SECRET must be at least 32 characters")
    wanted = {
        "clientId": client_id,
        "name": "Impact Platform account provisioning",
        "description": "Service account of the platform API: creates sign-in accounts only (v0.26a)",
        "enabled": True,
        "publicClient": False,
        "clientAuthenticatorType": "client-secret",
        "secret": secret,
        "serviceAccountsEnabled": True,
        "standardFlowEnabled": False,
        "implicitFlowEnabled": False,
        "directAccessGrantsEnabled": False,
        "frontchannelLogout": False,
        "protocol": "openid-connect",
        "attributes": {"use.refresh.tokens": "false", "client_credentials.use_refresh_token": "false"},
    }
    _, clients, _ = admin.call("GET", "/" + realm + "/clients?clientId=" + urllib.parse.quote(client_id))
    created = not clients
    if created:
        admin.call("POST", "/" + realm + "/clients", wanted)
        _, clients, _ = admin.call("GET", "/" + realm + "/clients?clientId=" + urllib.parse.quote(client_id))
        if not clients:
            raise AdminError("The provisioner client was not created")
        updated = False
    else:
        current = clients[0]
        updated = any(current.get(k) != wanted[k] for k in wanted if k not in {"secret", "attributes"})
        _, stored, _ = admin.call("GET", "/" + realm + "/clients/" + current["id"] + "/client-secret")
        if updated or (stored or {}).get("value") != secret:
            admin.call("PUT", "/" + realm + "/clients/" + current["id"], dict(current, **wanted))
            updated = True
    client = clients[0]
    _, account, _ = admin.call("GET", "/" + realm + "/clients/" + client["id"] + "/service-account-user")
    _, management, _ = admin.call("GET", "/" + realm + "/clients?clientId=realm-management")
    if not account or not management:
        raise AdminError("The provisioner's service account or realm-management is missing")
    management_id = management[0]["id"]
    mapping = "/" + realm + "/users/" + account["id"] + "/role-mappings/clients/" + management_id
    _, held, _ = admin.call("GET", mapping)
    held_names = {r["name"] for r in held or []}
    missing = []
    for name in PROVISIONER_ROLES:
        if name not in held_names:
            _, role, _ = admin.call("GET", "/" + realm + "/clients/" + management_id + "/roles/" + name)
            missing.append(role)
    if missing:
        admin.call("POST", mapping, missing)
    extra = sorted(held_names - set(PROVISIONER_ROLES))
    if extra:
        # Nothing beyond user management, whoever added it.
        admin.call("DELETE", mapping, [r for r in held if r["name"] in extra])
    return {
        "client_id": client_id,
        "created": created,
        "updated": updated,
        "roles_added": sorted(r["name"] for r in missing),
        "roles_removed": extra,
    }


def rotate_provisioner(admin, realm, secret, client_id=PROVISIONER_ID):
    """Set the provisioner client's secret to `secret` (v0.27: deploy/rotate-secrets.sh after
    scripts/rotate_secrets.py wrote the new value to secrets.env). The client must already exist
    (deploy/update.sh creates it; its flags and roles stay as ensure_provisioner left them). Idempotent:
    a secret the provider already holds changes nothing. The value is never printed or returned."""
    if len(secret) < 32:
        raise AdminError("IMPACT_PROVISIONER_SECRET must be at least 32 characters")
    _, clients, _ = admin.call("GET", "/" + realm + "/clients?clientId=" + urllib.parse.quote(client_id))
    if not clients:
        raise AdminError("The provisioner client does not exist yet; run deploy/update.sh first")
    current = clients[0]
    path = "/" + realm + "/clients/" + current["id"]
    _, stored, _ = admin.call("GET", path + "/client-secret")
    changed = (stored or {}).get("value") != secret
    if changed:
        admin.call("PUT", path, dict(current, secret=secret))
        _, applied, _ = admin.call("GET", path + "/client-secret")
        if (applied or {}).get("value") != secret:
            raise AdminError("The provisioner secret was not applied by the identity provider")
    return {"client_id": client_id, "changed": changed}


def list_users(admin, realm, limit=500):
    _, users, _ = admin.call(
        "GET",
        "/"
        + realm
        + "/users?"
        + urllib.parse.urlencode({"briefRepresentation": "false", "first": 0, "max": limit}),
    )
    result = []
    for user in sorted(users or [], key=lambda u: (u.get("email") or u.get("username") or "").lower()):
        path = "/" + realm + "/users/" + user["id"]
        _, credentials, _ = admin.call("GET", path + "/credentials")
        _, attacks, _ = admin.call(
            "GET", "/" + realm + "/attack-detection/brute-force/users/" + user["id"], expect=(200, 404)
        )
        result.append(
            {
                "email": user.get("email") or user.get("username"),
                "name": " ".join(n for n in (user.get("firstName"), user.get("lastName")) if n),
                "enabled": bool(user.get("enabled")),
                "temporary_password_pending": "UPDATE_PASSWORD" in (user.get("requiredActions") or []),
                "totp_configured": any(c.get("type") == "otp" for c in credentials or []),
                "locked": bool((attacks or {}).get("disabled")),
                "created": user.get("createdTimestamp"),
            }
        )
    return {"users": result, "truncated": len(users or []) >= limit}


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
    sub.add_parser("list")
    sub.add_parser("provisioner")
    sub.add_parser("rotate-provisioner")
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
        elif args.command == "list":
            result = list_users(admin, realm)
        elif args.command == "provisioner":
            result = ensure_provisioner(admin, realm, env.get("IMPACT_PROVISIONER_SECRET", ""))
        elif args.command == "rotate-provisioner":
            result = rotate_provisioner(admin, realm, env.get("IMPACT_PROVISIONER_SECRET", ""))
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
