"""Local Keycloak for live identity-provider qualification (v0.15); never used in production.

The pinned Keycloak distribution is downloaded once into .local/keycloak/ and verified against the
SHA-256 recorded below before it is unpacked. `start()` runs it in development mode on a loopback
port chosen by the operating system with the in-memory H2 database (`--db=dev-mem`, so nothing
survives a stop), creates a throwaway bootstrap administrator, and imports two realms through the
administration API:

- the qualification realm (`tools/idp/qualification-realm.json`, derived from
  specification/environment/keycloak-dev-realm.json by `scripts/idp.py realm`): the public
  `impact-web` client with S256 PKCE, the platform callback and post-logout redirect, back-channel
  logout to `<origin>/auth/backchannel-logout`, no refresh tokens, an `impact-api` audience, a
  step-up browser flow (level 1 password, level 2 TOTP) with an ACR-to-level map, short token
  lifetimes, and the fixture users under their fixture subjects;
- a foreign realm with the same client and one user carrying the author's subject, whose tokens
  the platform must refuse.

Passwords, TOTP secrets and the administrator password are generated at every start and written
only to <local>/idp.json (mode 0600); they are never printed and never reach the repository or the
evidence. The realm files are imported over HTTP, so no credential is written into the Keycloak
distribution either.

    python scripts/idp.py fetch              # download and verify the distribution (CI cache step)
    python scripts/idp.py realm              # regenerate tools/idp/qualification-realm.json
    python scripts/idp.py serve [--origin]   # run until interrupted, for manual exploration
"""

import argparse
import copy
import hashlib
import json
import os
import secrets
import shutil
import signal
import socket
import string
import subprocess
import sys
import tarfile
import time
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import httpx

ROOT = Path(__file__).resolve().parents[1]
KEYCLOAK_VERSION = "26.7.4"
# SHA-256 of keycloak-26.7.4.tar.gz from the GitHub release, computed 29 Sep 2026.
KEYCLOAK_SHA256 = "04823c336b797a7e18889a44262a7a64e6bf624cbbcc518c85e2622176ff2eee"
KEYCLOAK_URL = "https://github.com/keycloak/keycloak/releases/download/{0}/keycloak-{0}.tar.gz"
CACHE = Path(os.environ.get("IMPACT_KEYCLOAK_CACHE") or ROOT / ".local/keycloak")
SPEC_REALM = ROOT / "specification/environment/keycloak-dev-realm.json"
REALM_FILE = ROOT / "tools/idp/qualification-realm.json"
REALM = "impact-qualification"
FOREIGN_REALM = "impact-foreign"
CLIENT_ID = "impact-web"
AUDIENCE = "impact-api"
ORIGIN_PLACEHOLDER = "${PUBLIC_ORIGIN}"
# Level 1 is a password; level 2 adds the TOTP step. The platform requires the level-2 class.
PASSWORD_ACR = "urn:impact:acr:password"
REQUIRED_ACR = "urn:impact:acr:mfa"
# Fixture users that hold a TOTP credential; every other enabled user has a password only.
OTP_USERS = ("admin", "owner", "reviewer")
# Provider roles named like platform role templates; the platform must ignore them.
PROVIDER_ROLES = ("OWNER", "TENANT_ADMIN")
ROLE_CLAIM_USER = "author"
OTP_POLICY = {"digits": 6, "period": 30, "algorithm": "HmacSHA1"}
DEFAULT_ADMIN = "impact-qualification-admin"


def actor_name(username):
    return username.split("@", 1)[0]


def realm_template():
    """The qualification realm derived from the specification realm: same realm settings and
    users (same subjects, enabled flags and e-mail addresses), with the qualification client,
    the step-up flow and short lifetimes. It holds no credential and no port; `realm()` adds both."""
    spec = json.loads(SPEC_REALM.read_text())
    origin = ORIGIN_PLACEHOLDER
    realm = {k: v for k, v in spec.items() if k not in {"clients", "users"}}
    realm.update(
        {
            "realm": REALM,
            "displayName": "Impact qualification (synthetic)",
            "sslRequired": "external",
            "resetPasswordAllowed": False,
            "accessTokenLifespan": 120,
            "accessCodeLifespan": 60,
            "ssoSessionIdleTimeout": 600,
            "ssoSessionMaxLifespan": 1800,
            "revokeRefreshToken": True,
            "refreshTokenMaxReuse": 0,
            "otpPolicyType": "totp",
            "otpPolicyAlgorithm": OTP_POLICY["algorithm"],
            "otpPolicyDigits": OTP_POLICY["digits"],
            "otpPolicyPeriod": OTP_POLICY["period"],
            "otpPolicyLookAheadWindow": 1,
            "otpPolicyCodeReusable": False,
            "browserFlow": "impact step-up browser",
            "attributes": {"acr.loa.map": json.dumps({PASSWORD_ACR: 1, REQUIRED_ACR: 2})},
            "roles": {
                "realm": [
                    {"name": role, "description": "Provider role; grants nothing on the platform"}
                    for role in PROVIDER_ROLES
                ]
            },
            "authenticationFlows": [
                {
                    "alias": "impact step-up browser",
                    "description": "Cookie, or password (level 1) then TOTP (level 2) on request",
                    "providerId": "basic-flow",
                    "topLevel": True,
                    "builtIn": False,
                    "authenticationExecutions": [
                        {
                            "authenticator": "auth-cookie",
                            "authenticatorFlow": False,
                            "requirement": "ALTERNATIVE",
                            "priority": 10,
                            "userSetupAllowed": False,
                        },
                        {
                            "authenticatorFlow": True,
                            "flowAlias": "impact step-up forms",
                            "requirement": "ALTERNATIVE",
                            "priority": 20,
                            "userSetupAllowed": False,
                        },
                    ],
                },
                {
                    "alias": "impact step-up forms",
                    "providerId": "basic-flow",
                    "topLevel": False,
                    "builtIn": False,
                    "authenticationExecutions": [
                        {
                            "authenticatorFlow": True,
                            "flowAlias": "impact level 1",
                            "requirement": "CONDITIONAL",
                            "priority": 10,
                            "userSetupAllowed": False,
                        },
                        {
                            "authenticatorFlow": True,
                            "flowAlias": "impact level 2",
                            "requirement": "CONDITIONAL",
                            "priority": 20,
                            "userSetupAllowed": False,
                        },
                    ],
                },
                {
                    "alias": "impact level 1",
                    "providerId": "basic-flow",
                    "topLevel": False,
                    "builtIn": False,
                    "authenticationExecutions": [
                        {
                            "authenticator": "conditional-level-of-authentication",
                            "authenticatorConfig": "impact level 1 condition",
                            "authenticatorFlow": False,
                            "requirement": "REQUIRED",
                            "priority": 10,
                            "userSetupAllowed": False,
                        },
                        {
                            "authenticator": "auth-username-password-form",
                            "authenticatorFlow": False,
                            "requirement": "REQUIRED",
                            "priority": 20,
                            "userSetupAllowed": False,
                        },
                    ],
                },
                {
                    "alias": "impact level 2",
                    "providerId": "basic-flow",
                    "topLevel": False,
                    "builtIn": False,
                    "authenticationExecutions": [
                        {
                            "authenticator": "conditional-level-of-authentication",
                            "authenticatorConfig": "impact level 2 condition",
                            "authenticatorFlow": False,
                            "requirement": "REQUIRED",
                            "priority": 10,
                            "userSetupAllowed": False,
                        },
                        {
                            "authenticator": "auth-otp-form",
                            "authenticatorFlow": False,
                            "requirement": "REQUIRED",
                            "priority": 20,
                            "userSetupAllowed": False,
                        },
                    ],
                },
            ],
            "authenticatorConfig": [
                {
                    "alias": "impact level 1 condition",
                    "config": {"loa-condition-level": "1", "loa-max-age": "1800"},
                },
                {
                    "alias": "impact level 2 condition",
                    "config": {"loa-condition-level": "2", "loa-max-age": "0"},
                },
            ],
        }
    )
    client = copy.deepcopy(next(c for c in spec["clients"] if c["clientId"] == CLIENT_ID))
    client.update(
        {
            "publicClient": True,
            "standardFlowEnabled": True,
            "implicitFlowEnabled": False,
            "directAccessGrantsEnabled": False,
            "serviceAccountsEnabled": False,
            "frontchannelLogout": False,
            "redirectUris": [origin + "/auth/callback"],
            "webOrigins": [origin],
            "attributes": {
                "pkce.code.challenge.method": "S256",
                "post.logout.redirect.uris": origin + "/",
                "backchannel.logout.url": origin + "/auth/backchannel-logout",
                "backchannel.logout.session.required": "true",
                "backchannel.logout.revoke.offline.tokens": "false",
                # The platform never stores a provider token; the code exchange returns none.
                "use.refresh.tokens": "false",
                "client_credentials.use_refresh_token": "false",
            },
            "protocolMappers": [
                {
                    "name": "impact-api audience",
                    "protocol": "openid-connect",
                    "protocolMapper": "oidc-audience-mapper",
                    "consentRequired": False,
                    "config": {
                        "included.custom.audience": AUDIENCE,
                        "access.token.claim": "true",
                        "id.token.claim": "false",
                        "introspection.token.claim": "true",
                    },
                }
            ],
        }
    )
    realm["clients"] = [client]
    users = []
    for user in spec["users"]:
        user = {k: v for k, v in user.items() if k != "requiredActions"}
        name = actor_name(user["username"])
        user["firstName"], user["lastName"] = name.replace("_", " ").title(), "Synthetic"
        if name == ROLE_CLAIM_USER:
            user["realmRoles"] = list(PROVIDER_ROLES)
        user["attributes"] = {"impact_fixture_actor": [name]}
        users.append(user)
    realm["users"] = users
    return realm


def foreign_template():
    """A second realm with the same client and an author look-alike (same username and e-mail;
    Keycloak user IDs are unique across realms, so its subject is derived, not reused)."""
    base = realm_template()
    author = next(u for u in base["users"] if actor_name(u["username"]) == "author")
    author = {**author, "id": str(uuid5(NAMESPACE_URL, "impact-foreign-realm:" + author["id"]))}
    return {
        "realm": FOREIGN_REALM,
        "enabled": True,
        "sslRequired": "external",
        "accessTokenLifespan": 120,
        "clients": base["clients"],
        "users": [{k: v for k, v in author.items() if k != "realmRoles"}],
    }


def totp_secret():
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(32))


def credentials_for(realm):
    """Fresh password for every user and a TOTP secret for the OTP users."""
    result = {}
    for user in realm["users"]:
        name = actor_name(user["username"])
        entry = {"username": user["username"], "subject": user["id"], "password": secrets.token_urlsafe(18)}
        if name in OTP_USERS and realm["realm"] == REALM:
            entry["totp_secret"] = totp_secret()
        result[name] = entry
    return result


def realm(template, origin, credentials):
    text = json.dumps(template).replace(ORIGIN_PLACEHOLDER, origin)
    data = json.loads(text)
    for user in data["users"]:
        entry = credentials[actor_name(user["username"])]
        user["credentials"] = [{"type": "password", "value": entry["password"], "temporary": False}]
        if entry.get("totp_secret"):
            user["credentials"].append(
                {
                    "type": "otp",
                    "userLabel": "qualification authenticator",
                    # Keycloak keys the HMAC with the UTF-8 bytes of this value.
                    "secretData": json.dumps({"value": entry["totp_secret"]}),
                    "credentialData": json.dumps(
                        {
                            "subType": "totp",
                            "digits": OTP_POLICY["digits"],
                            "counter": 0,
                            "period": OTP_POLICY["period"],
                            "algorithm": OTP_POLICY["algorithm"],
                        }
                    ),
                }
            )
    return data


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def distribution(cache=CACHE):
    """The unpacked, verified Keycloak home; downloads and verifies the tarball when missing."""
    cache.mkdir(parents=True, exist_ok=True)
    home = cache / ("keycloak-" + KEYCLOAK_VERSION)
    archive = cache / ("keycloak-" + KEYCLOAK_VERSION + ".tar.gz")
    if (home / "bin/kc.sh").exists() and (home / ".verified-sha256").exists():
        if (home / ".verified-sha256").read_text().strip() == KEYCLOAK_SHA256:
            return home
    if not archive.exists() or sha256(archive) != KEYCLOAK_SHA256:
        partial = archive.with_suffix(".partial")
        with httpx.stream(
            "GET", KEYCLOAK_URL.format(KEYCLOAK_VERSION), follow_redirects=True, timeout=120
        ) as r:
            r.raise_for_status()
            with open(partial, "wb") as f:
                for chunk in r.iter_bytes(1 << 20):
                    f.write(chunk)
        actual = sha256(partial)
        if actual != KEYCLOAK_SHA256:
            partial.unlink()
            raise RuntimeError(
                "Keycloak "
                + KEYCLOAK_VERSION
                + " archive SHA-256 mismatch: got "
                + actual
                + ", pinned "
                + KEYCLOAK_SHA256
            )
        partial.rename(archive)
    if home.exists():
        shutil.rmtree(home)
    with tarfile.open(archive) as tar:
        tar.extractall(cache, filter="data")
    (home / ".verified-sha256").write_text(KEYCLOAK_SHA256 + "\n")
    return home


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def java_major():
    out = subprocess.run(["java", "-version"], capture_output=True, text=True).stderr
    for line in out.splitlines():
        if " version " in line:
            version = line.split('"')[1]
            return int(version.split(".")[0])
    raise RuntimeError("Cannot determine the Java version")


def admin_token(client, base, username, password):
    response = client.post(
        base + "/realms/master/protocol/openid-connect/token",
        data={"grant_type": "password", "client_id": "admin-cli", "username": username, "password": password},
    )
    response.raise_for_status()
    return response.json()["access_token"]


def import_realm(client, base, token, data):
    response = client.post(
        base + "/admin/realms", json=data, headers={"Authorization": "Bearer " + token}, timeout=60
    )
    if response.status_code != 201:
        raise RuntimeError("Realm import failed: " + str(response.status_code) + " " + response.text[:500])


def start(local, origin, log=None):
    """Start Keycloak, import both realms and return the connection details (also written to
    <local>/idp.json with the generated credentials, mode 0600)."""
    if java_major() < 21:
        raise RuntimeError("Keycloak " + KEYCLOAK_VERSION + " needs Java 21 or newer")
    home = distribution()
    port, management = free_port(), free_port()
    admin_password = secrets.token_urlsafe(24)
    log = log or local / "keycloak.log"
    env = {
        **os.environ,
        "KC_BOOTSTRAP_ADMIN_USERNAME": DEFAULT_ADMIN,
        "KC_BOOTSTRAP_ADMIN_PASSWORD": admin_password,
    }
    started = time.monotonic()
    process = subprocess.Popen(
        [
            str(home / "bin/kc.sh"),
            "start-dev",
            "--http-host=127.0.0.1",
            "--http-port=" + str(port),
            "--http-management-port=" + str(management),
            "--db=dev-mem",
            "--hostname-strict=false",
            "--log-level=info",
        ],
        cwd=home,
        env=env,
        stdout=open(log, "w"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    base = "http://127.0.0.1:" + str(port)
    try:
        with httpx.Client(trust_env=False, timeout=10) as client:
            for _ in range(480):
                if process.poll() is not None:
                    raise RuntimeError("Keycloak exited; see " + str(log))
                try:
                    if (
                        client.get(base + "/realms/master/.well-known/openid-configuration").status_code
                        == 200
                    ):
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(0.25)
            else:
                raise RuntimeError("Keycloak startup timeout; see " + str(log))
            ready = round(time.monotonic() - started, 2)
            token = admin_token(client, base, DEFAULT_ADMIN, admin_password)
            template = json.loads(REALM_FILE.read_text())
            if template != realm_template():
                raise RuntimeError(
                    str(REALM_FILE.relative_to(ROOT)) + " is stale; regenerate it with scripts/idp.py realm"
                )
            credentials = credentials_for(template)
            import_realm(client, base, token, realm(template, origin, credentials))
            foreign = foreign_template()
            foreign_credentials = credentials_for(foreign)
            import_realm(client, base, token, realm(foreign, origin, foreign_credentials))
            discovery = client.get(base + "/realms/" + REALM + "/.well-known/openid-configuration")
            discovery.raise_for_status()
            discovery = discovery.json()
            for _ in range(40):
                if client.get(discovery["jwks_uri"]).status_code == 200:
                    break
                time.sleep(0.25)
    except BaseException:
        stop(process)
        raise
    details = {
        "keycloak_version": KEYCLOAK_VERSION,
        "keycloak_sha256": KEYCLOAK_SHA256,
        "base_url": base,
        "realm": REALM,
        "foreign_realm": FOREIGN_REALM,
        "client_id": CLIENT_ID,
        "audience": AUDIENCE,
        "required_acr": REQUIRED_ACR,
        "password_acr": PASSWORD_ACR,
        "issuer": discovery["issuer"],
        "discovery": {
            k: discovery.get(k)
            for k in [
                "authorization_endpoint",
                "token_endpoint",
                "jwks_uri",
                "end_session_endpoint",
                "revocation_endpoint",
                "userinfo_endpoint",
            ]
        },
        "foreign_issuer": base + "/realms/" + FOREIGN_REALM,
        "ready_seconds": ready,
        "imported_seconds": round(time.monotonic() - started, 2),
        "admin": {"username": DEFAULT_ADMIN, "password": admin_password},
        "users": credentials,
        "foreign_users": foreign_credentials,
        "otp": OTP_POLICY,
    }
    path = local / "idp.json"
    path.write_text(json.dumps(details, indent=2))
    path.chmod(0o600)
    return process, details


def stop(process):
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("command", choices=["fetch", "realm", "serve"])
    parser.add_argument("--origin", default="http://127.0.0.1:" + os.environ.get("IMPACT_PORT", "8000"))
    args = parser.parse_args()
    if args.command == "fetch":
        print("Keycloak " + KEYCLOAK_VERSION + " ready at " + str(distribution()))
        return 0
    if args.command == "realm":
        REALM_FILE.parent.mkdir(parents=True, exist_ok=True)
        REALM_FILE.write_text(json.dumps(realm_template(), indent=2) + "\n")
        print("Wrote " + str(REALM_FILE.relative_to(ROOT)))
        return 0
    local = ROOT / ".local/idp"
    local.mkdir(parents=True, exist_ok=True)
    # SIGTERM must also stop Keycloak: the finally below runs only on an exception or exit.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    process, details = start(local, args.origin)
    print("Keycloak " + KEYCLOAK_VERSION + " issuer " + details["issuer"] + "; credentials in " + str(local))
    try:
        while process.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        stop(process)
    return 0


if __name__ == "__main__":
    sys.exit(main())
