"""Deployment package (v0.17) without a database or containers: the hashed requirements, the
staging realm, the compose file's wiring, the shell helpers that generate secrets, the Keycloak
administration helper, the first-operator bootstrap, the smoke check and the mail capture sink."""

import json
import os
import re
import smtplib
import socket
import subprocess
import sys
import threading
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "deploy"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(DEPLOY))

import bootstrap_operator  # noqa: E402
import hash_requirements  # noqa: E402
import keycloak_admin  # noqa: E402
import mail_sink  # noqa: E402
import smoke  # noqa: E402

COMPOSE = (DEPLOY / "compose.yaml").read_text()
UPDATE = (DEPLOY / "update.sh").read_text()
REALM = json.loads((DEPLOY / "keycloak/realm-staging.json").read_text())


# ---- image inputs --------------------------------------------------------------------------


def test_hashed_runtime_requirements_match_the_lock():
    lock = hash_requirements.runtime_pins((ROOT / "requirements.lock").read_text())
    text = (DEPLOY / "requirements.runtime.txt").read_text()
    hashed = re.findall(r"^([A-Za-z0-9_.-]+)==(\S+) \\$", text, re.M)
    assert hashed == lock
    blocks = re.split(r"^(?=[A-Za-z0-9_.-]+==)", text, flags=re.M)[1:]
    assert all(re.search(r"--hash=sha256:[0-9a-f]{64}", b) for b in blocks)
    names = {hash_requirements.canonical(n) for n, _ in lock}
    assert not names & {"pytest", "ruff"} and {"fastapi", "psycopg-binary", "pglast"} <= names


def test_dockerfile_copies_only_existing_runtime_files():
    dockerfile = (DEPLOY / "Dockerfile").read_text()
    for line in re.findall(r"^COPY (?!--from)(.+)$", dockerfile, re.M):
        *sources, _ = line.split()
        for source in sources:
            assert (ROOT / source).exists(), source
    assert "--require-hashes" in dockerfile and "USER impact" in dockerfile
    ignored = (ROOT / ".dockerignore").read_text().split()
    assert {".local", ".venv", ".git", "qualification", "docs"} <= set(ignored)


# ---- identity provider realm ---------------------------------------------------------------


def test_staging_realm_is_closed_and_matches_the_platform_configuration():
    assert "users" not in REALM and REALM["realm"] == "impact"
    assert REALM["registrationAllowed"] is False and REALM["resetPasswordAllowed"] is False
    assert REALM["registrationEmailAsUsername"] is True and REALM["loginWithEmailAllowed"] is True
    assert REALM["bruteForceProtected"] is True and REALM["failureFactor"] <= 10
    assert "length(6)" in REALM["passwordPolicy"] and "notEmail" in REALM["passwordPolicy"]
    levels = json.loads(REALM["attributes"]["acr.loa.map"])
    assert levels["urn:impact:acr:mfa"] == 2 and "IMPACT_REQUIRED_ACR: urn:impact:acr:mfa" in COMPOSE
    otp = [
        e
        for f in REALM["authenticationFlows"]
        for e in f["authenticationExecutions"]
        if e.get("authenticator") == "auth-otp-form"
    ]
    assert otp and otp[0]["requirement"] == "REQUIRED"
    (client,) = REALM["clients"]
    assert client["clientId"] == "impact-web" and client["publicClient"] is True
    assert client["directAccessGrantsEnabled"] is False and client["implicitFlowEnabled"] is False
    attributes = client["attributes"]
    assert attributes["pkce.code.challenge.method"] == "S256"
    assert attributes["use.refresh.tokens"] == "false"
    assert attributes["backchannel.logout.url"] == "${PUBLIC_ORIGIN}/auth/backchannel-logout"
    assert attributes["backchannel.logout.session.required"] == "true"
    assert client["redirectUris"] == ["${PUBLIC_ORIGIN}/auth/callback"]
    mapper = client["protocolMappers"][0]["config"]
    assert mapper["included.custom.audience"] == "impact-api" and "IMPACT_AUDIENCE: impact-api" in COMPOSE


def test_realm_document_substitutes_the_origin_and_refuses_users(tmp_path):
    document = keycloak_admin.realm_document(
        DEPLOY / "keycloak/realm-staging.json", "https://app.example.org"
    )
    assert "${PUBLIC_ORIGIN}" not in json.dumps(document)
    assert keycloak_admin.client_fields(document)["redirectUris"] == ["https://app.example.org/auth/callback"]
    with pytest.raises(keycloak_admin.AdminError):
        keycloak_admin.realm_document(DEPLOY / "keycloak/realm-staging.json", "http://app.example.org")
    with_users = tmp_path / "realm.json"
    with_users.write_text(json.dumps({**REALM, "users": [{"username": "x"}]}))
    with pytest.raises(keycloak_admin.AdminError):
        keycloak_admin.realm_document(with_users, "https://app.example.org")


class FakeKeycloak:
    """The admin REST calls keycloak_admin makes, over an in-memory realm."""

    def __init__(self, realm=None):
        self.realm, self.users, self.credentials, self.calls = realm, {}, {}, []
        self.lockouts_cleared = []

    def call(self, method, path, data=None, expect=(200, 201, 204)):
        self.calls.append((method, path.split("?")[0]))
        if method == "GET" and path == "/impact":
            return (200, self.realm, {}) if self.realm else (404, None, {})
        if method == "POST" and path == "":
            self.realm = data
            return 201, None, {}
        if method == "PUT" and path == "/impact":
            self.realm.update(data)
            return 204, None, {}
        if path.startswith("/impact/clients?"):
            return 200, [dict(c, id="c1") for c in self.realm["clients"]], {}
        if method == "PUT" and path == "/impact/clients/c1":
            self.realm["clients"] = [data]
            return 204, None, {}
        if method == "GET" and path == "/impact/clients/c1/client-secret":
            return 200, {"type": "secret", "value": self.realm["clients"][0].get("secret")}, {}
        if path.startswith("/impact/users?"):
            email = re.search(r"email=([^&]+)", path).group(1).replace("%40", "@")
            return 200, [u for u in self.users.values() if u["email"] == email.lower()], {}
        if method == "POST" and path == "/impact/users":
            user = dict(data, id=str(uuid4()))
            self.credentials[user["id"]] = []
            self.users[user["id"]] = user
            return 201, None, {}
        if "/attack-detection/brute-force/users/" in path and method == "DELETE":
            self.lockouts_cleared.append(path.split("/")[-1])
            return 204, None, {}
        user_id = path.split("/")[3]
        if path.endswith("/credentials") and method == "GET":
            return 200, self.credentials[user_id], {}
        if "/credentials/" in path and method == "DELETE":
            self.credentials[user_id] = [
                c for c in self.credentials[user_id] if c["id"] != path.split("/")[-1]
            ]
            return 204, None, {}
        if path.endswith("/reset-password"):
            self.users[user_id]["password"] = data
            return 204, None, {}
        if method == "PUT":
            self.users[user_id].update(data)
            return 204, None, {}
        raise AssertionError((method, path))


def test_realm_import_happens_once_and_later_runs_only_realign_the_client():
    fake = FakeKeycloak()
    document = keycloak_admin.realm_document(DEPLOY / "keycloak/realm-staging.json", "https://a.example.org")
    assert keycloak_admin.ensure_realm(fake, "impact", document)["imported"] is True
    again = keycloak_admin.ensure_realm(fake, "impact", document)
    assert again == {"realm": "impact", "imported": False, "client_updated": False, "policy_updated": False}
    fake.realm = dict(fake.realm, passwordPolicy="length(12) and notUsername and notEmail and maxLength(128)")
    assert keycloak_admin.ensure_realm(fake, "impact", document)["policy_updated"] is True
    assert fake.realm["passwordPolicy"] == document["passwordPolicy"]
    moved = keycloak_admin.realm_document(DEPLOY / "keycloak/realm-staging.json", "https://b.example.org")
    assert keycloak_admin.ensure_realm(fake, "impact", moved)["client_updated"] is True
    assert fake.realm["clients"][0]["redirectUris"] == ["https://b.example.org/auth/callback"]
    assert ("POST", "") in fake.calls and fake.calls.count(("POST", "")) == 1


def test_owner_account_is_created_once_with_required_actions_and_reset_restores_them():
    fake = FakeKeycloak(realm={"clients": []})
    with pytest.raises(keycloak_admin.AdminError):
        keycloak_admin.ensure_user(fake, "impact", "Owner@Example.org", "short")
    first = keycloak_admin.ensure_user(fake, "impact", "Owner@Example.org", "abcd-efgh-jkmn-pqrs", "A", "B")
    user = fake.users[first["subject"]]
    assert first["created"] and user["username"] == "owner@example.org" and user["emailVerified"] is True
    assert user["requiredActions"] == ["UPDATE_PASSWORD", "CONFIGURE_TOTP"]
    assert user["credentials"] == [{"type": "password", "value": "abcd-efgh-jkmn-pqrs", "temporary": True}]
    assert keycloak_admin.ensure_user(fake, "impact", "owner@example.org", "other-password-1") == {
        "subject": first["subject"],
        "created": False,
    }
    user["requiredActions"] = []
    fake.credentials[first["subject"]] = [{"id": "otp1", "type": "otp"}, {"id": "pw", "type": "password"}]
    status = keycloak_admin.user_status(fake, "impact", "owner@example.org")
    assert status["temporary_password_pending"] is False and status["totp_configured"] is True
    reset = keycloak_admin.reset_user(fake, "impact", "owner@example.org", "new1-temp-pass-word", totp=True)
    assert reset["totp_removed"] == 1 and fake.credentials[first["subject"]] == [
        {"id": "pw", "type": "password"}
    ]
    assert fake.users[first["subject"]]["requiredActions"] == ["UPDATE_PASSWORD", "CONFIGURE_TOTP"]
    assert fake.users[first["subject"]]["password"]["temporary"] is True
    # A reset also lifts a sign-in lockout left by earlier failed attempts.
    assert reset["lockout_cleared"] is True and fake.lockouts_cleared == [first["subject"]]


# ---- compose and update.sh wiring ----------------------------------------------------------


def test_only_caddy_publishes_ports_and_the_database_network_is_internal():
    assert COMPOSE.count("ports:") == 1 and '"80:80"' in COMPOSE and '"443:443"' in COMPOSE
    assert re.search(r"backend:\n\s+internal: true", COMPOSE)
    assert COMPOSE.count('IMPACT_REQUIRE_UNPRIVILEGED_DB: "1"') == 3
    executor = COMPOSE.split("  executor:\n", 1)[1].split("\n  caddy:\n", 1)[0]
    assert "networks: [backend]" in executor and "edge" not in executor
    assert "impact_executor_login" in executor and "impact_worker_login" not in executor
    assert "IMPACT_ALLOW_FIXTURE_LOAD" not in COMPOSE and "dev_auth" not in COMPOSE.lower()
    assert "IMPACT_ENVIRONMENT: staging" in COMPOSE
    idp = (ROOT / "scripts/idp.py").read_text()
    version = re.search(r'KEYCLOAK_VERSION = "([^"]+)"', idp).group(1)
    assert "quay.io/keycloak/keycloak:" + version in COMPOSE
    for login in (
        "impact_app_login",
        "impact_identity_login",
        "impact_platform_login",
        "impact_worker_login",
        "impact_executor_login",
    ):
        assert COMPOSE.count("postgresql://" + login + ":") == 1
    assert "postgresql://postgres:" in COMPOSE.split("  migrate:")[1].split("  operator-bootstrap:")[0]
    api = COMPOSE.split("\n  api:\n")[1].split("\n  mailsink:")[0]
    assert "impact_migrator" not in api and "POSTGRES_PASSWORD" not in api and "KEYCLOAK" not in api


def test_every_variable_compose_requires_is_written_by_update_sh():
    required = set(re.findall(r"\$\{([A-Z0-9_]+):\?", COMPOSE))
    generated = set(re.findall(r"^\s+ensure_secret ([A-Z0-9_]+) \d+$", UPDATE, re.M))
    written = set(re.findall(r"([A-Z0-9_]+)=%s", UPDATE))
    assert required <= generated | written, required - generated - written
    assert {"IMPACT_COOKIE_SECRET", "IMPACT_INVITATION_SECRET", "IMPACT_DELIVERY_SECRET"} <= generated
    # The temporary owner password stays in secrets.env; compose never receives it.
    assert "grep -v '^OWNER_TEMP_PASSWORD='" in UPDATE and "OWNER_TEMP_PASSWORD" not in COMPOSE


def bash(script, **env):
    return subprocess.run(
        ["bash", "-c", "set -euo pipefail; source deploy/lib.sh; " + script],
        cwd=ROOT,
        env={**os.environ, **env},
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def test_secret_helpers_generate_strong_distinct_values_and_never_overwrite(tmp_path):
    secrets_file = tmp_path / "secrets.env"
    values = bash("for i in 1 2 3; do random_hex 48; done").split()
    assert len(set(values)) == 3 and all(re.fullmatch(r"[0-9a-f]{96}", v) for v in values)
    password = bash("readable_password").strip()
    assert re.fullmatch(r"([a-z2-9]{4}-){4}[a-z2-9]{4}", password)
    bash(
        f"touch {secrets_file}; chmod 600 {secrets_file}; set_env_value {secrets_file} A one; "
        f"set_env_value {secrets_file} B two; set_env_value {secrets_file} A three"
    )
    assert secrets_file.read_text() == "B=two\nA=three\n"
    assert oct(secrets_file.stat().st_mode & 0o777) == "0o600"
    assert bash(f"env_value {secrets_file} A").strip() == "three"
    assert bash(f"env_value {secrets_file} MISSING; env_value {tmp_path}/absent A") == ""
    # ensure_secret in update.sh only fills a key that is absent.
    assert 'if [ -z "$(env_value "$SECRETS_FILE" "$key")" ]; then' in UPDATE


def test_shell_scripts_are_executable_and_strict():
    for name in ("update.sh", "first-admin.sh", "add-user.sh", "backup.sh"):
        path = DEPLOY / name
        assert os.access(path, os.X_OK), name
        assert "set -euo pipefail" in path.read_text(), name


# ---- first operator bootstrap --------------------------------------------------------------


class FakeDatabase:
    """Just enough of the three control-plane tables for bootstrap_operator's statements."""

    def __init__(self):
        self.identities, self.operators, self.qualifications = [], [], []

    def execute(self, sql, params=()):
        self.last = []
        if sql.startswith("SELECT pg_advisory_xact_lock"):
            pass
        elif sql.startswith("SELECT identity_id,natural_identity_id FROM impact.auth_identity WHERE issuer"):
            self.last = [i for i in self.identities if (i["issuer"], i["provider_subject"]) == params]
        elif sql.startswith(
            "SELECT identity_id,natural_identity_id FROM impact.auth_identity WHERE identity_id"
        ):
            self.last = [i for i in self.identities if i["identity_id"] == params[0]]
        elif sql.startswith("INSERT INTO impact.auth_identity"):
            keys = ("identity_id", "issuer", "provider_subject", "natural_identity_id")
            self.identities.append(dict(zip(keys, params)))
        elif sql.startswith("SELECT identity_id,active,expires_at FROM impact.platform_operator"):
            self.last = list(self.operators)
        elif sql.startswith("INSERT INTO impact.platform_operator"):
            self.operators.append(
                dict(zip(("identity_id", "expires_at", "authority_reference"), params), active=True)
            )
        elif sql.startswith("SELECT * FROM impact.deployment_qualification WHERE active"):
            self.last = [q for q in self.qualifications if (q["environment"], q["issuer"]) == params[:2]]
        elif sql.startswith("INSERT INTO impact.deployment_qualification"):
            keys = (
                "qualification_id",
                "revision_id",
                "environment",
                "region",
                "issuer",
                "required_acr",
                "privacy_reference",
                "recovery_reference",
                "retention_max_days",
                "valid_until",
            )
            self.qualifications.append(dict(zip(keys, params)))
        elif sql.startswith("SELECT * FROM impact.deployment_qualification WHERE qualification_id"):
            self.last = [q for q in self.qualifications if q["qualification_id"] == params[0]]
        else:
            raise AssertionError(sql)
        return self

    def fetchone(self):
        return self.last[0] if self.last else None

    def fetchall(self):
        return self.last


def operator_args(subject="subject-1", **overrides):
    values = dict(
        issuer="https://auth.example.org/realms/impact",
        subject=subject,
        reference="First operator",
        environment="staging",
        required_acr="urn:impact:acr:mfa",
        region="do-blr1",
        privacy_reference="staging-privacy-notice-v1",
        recovery_reference="Droplet backups",
        retention_max_days=3650,
        operator_days=365,
        qualification_days=365,
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def test_first_operator_is_created_once_and_a_second_person_is_refused():
    db = FakeDatabase()
    first = bootstrap_operator.bootstrap_operator(db, operator_args())
    assert first["outcome"] == "created" and first["identity_created"] and first["qualification_created"]
    assert len(db.identities) == len(db.operators) == len(db.qualifications) == 1
    operator = db.operators[0]
    assert operator["expires_at"] - datetime.now(timezone.utc) > timedelta(days=364)
    assert db.qualifications[0]["environment"] == "staging" and db.qualifications[0]["required_acr"].endswith(
        "mfa"
    )
    assert db.identities[0]["natural_identity_id"] != db.identities[0]["identity_id"]
    again = bootstrap_operator.bootstrap_operator(db, operator_args())
    assert again["outcome"] == "already-bootstrapped" and again["identity_id"] == first["identity_id"]
    assert not again["qualification_created"] and len(db.operators) == 1
    with pytest.raises(bootstrap_operator.Refused):
        bootstrap_operator.bootstrap_operator(db, operator_args("subject-2"))


def test_bootstrap_validates_its_inputs():
    db = FakeDatabase()
    for bad in (
        operator_args(issuer="http://auth.example.org/realms/impact"),
        operator_args(subject=""),
        operator_args(reference=" "),
        operator_args(environment="development"),
    ):
        with pytest.raises(ValueError):
            bootstrap_operator.bootstrap_operator(db, bad)
    assert not db.operators
    registered = bootstrap_operator.register_identity(db, "https://auth.example.org/realms/impact", "s-9")
    assert (
        registered["created"]
        and not bootstrap_operator.register_identity(db, "https://auth.example.org/realms/impact", "s-9")[
            "created"
        ]
    )
    assert not db.operators


def test_bootstrap_requires_the_migration_login(monkeypatch):
    monkeypatch.delenv("IMPACT_MIGRATION_DSN", raising=False)
    with pytest.raises(RuntimeError):
        bootstrap_operator.main(
            ["identity", "--issuer", "https://a.example.org/realms/impact", "--subject", "x"]
        )


# ---- smoke check ---------------------------------------------------------------------------

ISSUER = "https://auth.app.example.org/realms/impact"
SECURE = {
    "strict-transport-security": "max-age=31536000; includeSubDomains",
    "content-security-policy": "default-src 'self'; frame-ancestors 'none'",
    "x-content-type-options": "nosniff",
    "cache-control": "no-store",
    "referrer-policy": "no-referrer",
}
WALKTHROUGH_CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; "
    "style-src-attr 'unsafe-inline'; connect-src 'none'; img-src 'none'; "
    "object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
)
WALKTHROUGH_HEADERS = {
    **SECURE,
    "content-type": "text/html; charset=utf-8",
    "content-security-policy": WALKTHROUGH_CSP,
}
WALKTHROUGH_HTML = """<!doctype html><html><head>
<title>Fictional AI walkthrough · Tola / Impact Platform</title>
<script type="module" src="/assets/walkthrough-fixture.js"></script>
<link rel="modulepreload" href="/assets/public-sections.js">
<link rel="stylesheet" href="/assets/walkthrough-fixture.css">
</head><body><div id="root"></div><noscript>
This fictional walkthrough needs JavaScript. It has no sign-in, network actions or persistence.
</noscript></body></html>"""


def fake_site(overrides=None):
    overrides = overrides or {}

    def handler(request):
        url = str(request.url)
        path = request.url.path
        if url in overrides:
            return overrides[url](request)
        if request.url.host == "auth.app.example.org":
            if path.endswith("/.well-known/openid-configuration"):
                return httpx.Response(
                    200,
                    json={
                        "issuer": ISSUER,
                        "authorization_endpoint": ISSUER + "/protocol/openid-connect/auth",
                        "code_challenge_methods_supported": ["plain", "S256"],
                        "backchannel_logout_supported": True,
                    },
                )
            if path.startswith("/admin"):
                return httpx.Response(404)
            return httpx.Response(200, text="<form id='kc-form-login'>")
        if path == "/health/live":
            return httpx.Response(200, json={"status": "live"}, headers=SECURE)
        if path == "/health/ready":
            return httpx.Response(200, json={"status": "ready"}, headers=SECURE)
        if path == "/":
            return httpx.Response(
                200, text='<div id="root"></div><script src="/assets/a.js">', headers=SECURE
            )
        if path == "/ai-walkthrough.html":
            return httpx.Response(200, text=WALKTHROUGH_HTML, headers=WALKTHROUGH_HEADERS)
        if path in {"/assets/walkthrough-fixture.js", "/assets/public-sections.js"}:
            return httpx.Response(
                200, text="/* synthetic compiled fixture */", headers={"content-type": "text/javascript"}
            )
        if path == "/assets/walkthrough-fixture.css":
            return httpx.Response(200, text="body { color: #183b32; }", headers={"content-type": "text/css"})
        if path == "/auth/mode":
            return httpx.Response(200, json={"development": False})
        if path == "/auth/login":
            query = (
                "response_type=code&client_id=impact-web&state=s&nonce=n&code_challenge=c"
                "&code_challenge_method=S256&acr_values=urn%3Aimpact%3Aacr%3Amfa"
                "&redirect_uri=https%3A%2F%2Fapp.example.org%2Fauth%2Fcallback"
            )
            return httpx.Response(
                303, headers={"location": ISSUER + "/protocol/openid-connect/auth?" + query}
            )
        if path == "/deploy-status.json":
            return httpx.Response(
                200,
                json={
                    "commit": "abc",
                    "result": "ok",
                    "services": {"api": {"state": "running"}, "keycloak": {"state": "running"}},
                },
            )
        return httpx.Response(404)

    return httpx.MockTransport(handler)


def run_smoke(transport, **kwargs):
    check = smoke.Smoke("https://app.example.org", required_acr="urn:impact:acr:mfa")
    check.client = httpx.Client(transport=transport, follow_redirects=False)
    check.tls = lambda: ("skip", "test")
    check.https_redirect = lambda: ("skip", "test")
    return check.run(**kwargs)


def test_smoke_passes_a_healthy_deployment():
    report = run_smoke(fake_site())
    assert report["passed"], report
    assert report["issuer"] == ISSUER
    assert {r["check"] for r in report["checks"] if r["status"] == "pass"} >= {
        "ready",
        "headers",
        "login_redirect",
        "provider",
        "provider_admin_hidden",
        "deploy_status",
        "ai_walkthrough",
    }


@pytest.mark.parametrize(
    "url,response,failed",
    [
        (
            "https://app.example.org/health/ready",
            httpx.Response(503, json={"reason_code": "SHARED_RUNTIME_LOGIN"}),
            "ready",
        ),
        ("https://app.example.org/health/live", httpx.Response(200, json={}, headers={}), "headers"),
        (
            "https://app.example.org/auth/mode",
            httpx.Response(200, json={"development": True}),
            "live_provider",
        ),
        (
            "https://app.example.org/auth/login",
            httpx.Response(303, headers={"location": "https://evil.example.org/x"}),
            "login_redirect",
        ),
        (
            "https://auth.app.example.org/admin/master/console/",
            httpx.Response(200, text="console"),
            "provider_admin_hidden",
        ),
        (
            "https://app.example.org/deploy-status.json",
            httpx.Response(200, json={"commit": "a", "db_password": "x"}),
            "deploy_status",
        ),
    ],
)
def test_smoke_fails_each_broken_property(url, response, failed):
    report = run_smoke(fake_site({url: lambda request: response}))
    assert not report["passed"]
    assert [r["check"] for r in report["checks"] if r["status"] == "fail"] == [failed]


def walkthrough_response(text=WALKTHROUGH_HTML, **headers):
    return httpx.Response(200, text=text, headers={**WALKTHROUGH_HEADERS, **headers})


def assert_walkthrough_smoke_refuses(response, path="/ai-walkthrough.html"):
    report = run_smoke(fake_site({"https://app.example.org" + path: lambda request: response}))
    assert not report["passed"]
    assert [row["check"] for row in report["checks"] if row["status"] == "fail"] == ["ai_walkthrough"]


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(404),
        httpx.Response(302, headers={"location": "https://elsewhere.example.org/demo"}),
        httpx.Response(200, json={"message": "source is not built"}, headers=SECURE),
        walkthrough_response(**{"set-cookie": "synthetic_cookie=example"}),
        walkthrough_response(**{"cache-control": "public, max-age=3600"}),
        walkthrough_response(**{"x-content-type-options": ""}),
        walkthrough_response(**{"referrer-policy": "same-origin"}),
    ],
)
def test_smoke_refuses_missing_or_weak_walkthrough_document(response):
    assert_walkthrough_smoke_refuses(response)


@pytest.mark.parametrize(
    "text",
    [
        WALKTHROUGH_HTML.replace('<div id="root"></div>', ""),
        WALKTHROUGH_HTML.replace('<div id="root"></div>', '<div id="root"></div>' * 2),
        WALKTHROUGH_HTML.replace("Fictional AI walkthrough · Tola / Impact Platform", "Impact Platform"),
        WALKTHROUGH_HTML.replace(
            "no sign-in, network actions or persistence", "no sign-in and persistence is enabled"
        ),
        WALKTHROUGH_HTML.replace("<noscript>", "<p>").replace("</noscript>", "</p>"),
        WALKTHROUGH_HTML.replace("/assets/walkthrough-fixture.js", "/src/ai-walkthrough-main.tsx"),
        WALKTHROUGH_HTML.replace('<script type="module"', '<script type="text/javascript"'),
        WALKTHROUGH_HTML.replace('<link rel="stylesheet" href="/assets/walkthrough-fixture.css">', ""),
        WALKTHROUGH_HTML.replace("</head>", '<script>fetch("/auth/me")</script></head>'),
        WALKTHROUGH_HTML.replace(
            "</head>", '<meta http-equiv="refresh" content="0;url=https://elsewhere.example.org"></head>'
        ),
        WALKTHROUGH_HTML.replace('<div id="root"', '<div onclick="signIn()" id="root"'),
        WALKTHROUGH_HTML.replace("</head>", '<base href="https://elsewhere.example.org"></head>'),
    ],
)
def test_smoke_refuses_source_only_or_wrong_walkthrough_structure(text):
    assert_walkthrough_smoke_refuses(walkthrough_response(text))


@pytest.mark.parametrize(
    "reference",
    [
        "https://elsewhere.example.org/assets/public-sections.js",
        "https://app.example.org/assets/public-sections.js",
        "//elsewhere.example.org/assets/public-sections.js",
        "/assets/public-sections.js?auth=example",
        "/assets/public-sections.js#example",
        "/assets/../auth/me.js",
        "/assets/%2e%2e/auth.js",
        "/assets/nested/public-sections.js",
        "data:text/javascript,alert(1)",
    ],
)
def test_smoke_never_follows_unexpected_walkthrough_asset_references(reference):
    requests = []
    site = fake_site(
        {
            "https://app.example.org/ai-walkthrough.html": lambda request: walkthrough_response(
                WALKTHROUGH_HTML.replace("/assets/public-sections.js", reference)
            )
        }
    )

    def record(request):
        requests.append(str(request.url))
        return site.handle_request(request)

    report = run_smoke(httpx.MockTransport(record), provider=False, status=False)
    assert [row["check"] for row in report["checks"] if row["status"] == "fail"] == ["ai_walkthrough"]
    assert not any("/assets/" in url for url in requests)
    assert all(url.startswith("https://app.example.org/") for url in requests)


@pytest.mark.parametrize(
    "directive",
    [
        "default-src",
        "connect-src",
        "img-src",
        "object-src",
        "base-uri",
        "form-action",
        "frame-ancestors",
        "script-src",
        "style-src",
    ],
)
def test_smoke_refuses_relaxed_walkthrough_csp(directive):
    weakened = re.sub(re.escape(directive) + r" [^;]+", directive + " *", WALKTHROUGH_CSP)
    assert_walkthrough_smoke_refuses(walkthrough_response(**{"content-security-policy": weakened}))


@pytest.mark.parametrize(
    "directive",
    [
        "default-src",
        "connect-src",
        "img-src",
        "object-src",
        "base-uri",
        "form-action",
        "frame-ancestors",
        "script-src",
        "style-src",
    ],
)
def test_smoke_refuses_missing_walkthrough_csp_directive(directive):
    missing = "; ".join(part for part in WALKTHROUGH_CSP.split("; ") if not part.startswith(directive + " "))
    assert_walkthrough_smoke_refuses(walkthrough_response(**{"content-security-policy": missing}))


@pytest.mark.parametrize(
    "extra",
    [
        "connect-src *",
        "script-src-elem *",
        "script-src-attr 'unsafe-inline'",
        "frame-src https://elsewhere.example.org",
    ],
)
def test_smoke_refuses_duplicate_or_overridden_walkthrough_csp(extra):
    assert_walkthrough_smoke_refuses(
        walkthrough_response(**{"content-security-policy": WALKTHROUGH_CSP + "; " + extra})
    )


@pytest.mark.parametrize(
    "path,response",
    [
        ("/assets/walkthrough-fixture.js", httpx.Response(404)),
        (
            "/assets/public-sections.js",
            httpx.Response(200, text="<html>fallback</html>", headers={"content-type": "text/html"}),
        ),
        (
            "/assets/walkthrough-fixture.css",
            httpx.Response(
                200, text="body{}", headers={"content-type": "text/css", "set-cookie": "synthetic=example"}
            ),
        ),
        (
            "/assets/walkthrough-fixture.js",
            httpx.Response(302, headers={"location": "https://elsewhere.example.org/script.js"}),
        ),
        (
            "/assets/walkthrough-fixture.css",
            httpx.Response(200, content=b"", headers={"content-type": "text/css"}),
        ),
    ],
)
def test_smoke_refuses_missing_wrong_type_or_cookie_setting_built_asset(path, response):
    assert_walkthrough_smoke_refuses(response, path)


def test_smoke_walkthrough_bounds_document_asset_bytes_and_reference_count():
    assert_walkthrough_smoke_refuses(walkthrough_response(" " * (128 * 1024 + 1)))
    assert_walkthrough_smoke_refuses(
        httpx.Response(
            200, content=b"x" * (8 * 1024 * 1024 + 1), headers={"content-type": "text/javascript"}
        ),
        "/assets/walkthrough-fixture.js",
    )
    refs = "".join(f'<link rel="stylesheet" href="/assets/example-{n}.css">' for n in range(17))
    assert_walkthrough_smoke_refuses(
        walkthrough_response(WALKTHROUGH_HTML.replace("</head>", refs + "</head>"))
    )


def test_smoke_walkthrough_is_default_even_without_auth_provider_and_requests_only_static_assets():
    requests = []
    site = fake_site()

    def record(request):
        requests.append((request.method, str(request.url)))
        return site.handle_request(request)

    report = run_smoke(httpx.MockTransport(record), provider=False, status=False)
    assert report["passed"], report
    result = next(row for row in report["checks"] if row["check"] == "ai_walkthrough")
    assert result["status"] == "pass" and result["detail"]["asset_count"] == 3
    assert "static packaging/header smoke only" in result["detail"]["scope"]
    assert all(method == "GET" and url.startswith("https://app.example.org/") for method, url in requests)
    assert not any("/auth/" in url or "/v1/" in url for _, url in requests)
    assert {url for _, url in requests if "/assets/" in url} == {
        "https://app.example.org/assets/walkthrough-fixture.js",
        "https://app.example.org/assets/public-sections.js",
        "https://app.example.org/assets/walkthrough-fixture.css",
    }


@pytest.mark.parametrize(
    "name",
    [
        "db_password",
        "SMTP_PASSWORD",
        "signingKey",
        "api-key",
        "apikey",
        "signing_keys",
        "clientSecret",
        "IMPACT_DSN",
        "refresh_token",
        "credentials",
    ],
)
def test_smoke_flags_secret_field_names(name):
    assert smoke.secret_looking(name)
    report = run_smoke(
        fake_site(
            {
                "https://app.example.org/deploy-status.json": lambda request: httpx.Response(
                    200, json={"commit": "a", "services": {"keycloak": {"detail": {name: "x"}}}}
                )
            }
        )
    )
    assert [r["check"] for r in report["checks"] if r["status"] == "fail"] == ["deploy_status"]


@pytest.mark.parametrize("name", ["keycloak", "services", "log_tail", "first_operator", "schema_version"])
def test_smoke_does_not_flag_ordinary_status_fields(name):
    assert not smoke.secret_looking(name)


def test_smoke_skips_what_a_local_stack_does_not_have():
    report = run_smoke(fake_site(), provider=False, status=False)
    skipped = {r["check"] for r in report["checks"] if r["status"] == "skip"}
    assert {
        "live_provider",
        "login_redirect",
        "provider",
        "provider_admin_hidden",
        "deploy_status",
    } <= skipped
    with pytest.raises(ValueError):
        smoke.Smoke("https://app.example.org/path")


# ---- mail capture sink ---------------------------------------------------------------------


def test_mail_sink_captures_messages_and_refuses_oversized_ones(tmp_path):
    sink = tmp_path / "captured.jsonl"
    server = mail_sink.Server(("127.0.0.1", 0), mail_sink.handler_for(str(sink)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    try:
        message = EmailMessage()
        message["From"], message["To"], message["Subject"] = "impact@app.example.org", "a@example.org", "Hi"
        message["X-Impact-Delivery"] = "event-1"
        message.set_content("Plain body")
        with smtplib.SMTP("127.0.0.1", port, timeout=5) as smtp:
            smtp.ehlo()
            assert smtp.send_message(message) == {}
            large = EmailMessage()
            large["From"], large["To"] = "impact@app.example.org", "a@example.org"
            large.set_content("x" * (mail_sink.MAX_MESSAGE + 10))
            with pytest.raises(smtplib.SMTPDataError):
                smtp.send_message(large)
        entries = [json.loads(line) for line in sink.read_text().splitlines()]
        assert len(entries) == 1 and entries[0]["event_id"] == "event-1"
        assert entries[0]["envelope_to"] == ["a@example.org"] and entries[0]["body"].strip() == "Plain body"
        assert oct(sink.stat().st_mode & 0o777) == "0o600"
        with socket.create_connection(("127.0.0.1", port), timeout=5) as raw:
            raw.recv(100)
            raw.sendall(b"DATA\r\n")
            assert raw.recv(100).startswith(b"503")
    finally:
        server.shutdown()
        server.server_close()
    with pytest.raises(SystemExit):
        mail_sink.main(["--host", "0.0.0.0", "--sink", str(sink)])


def test_provisioner_secret_rotation_sets_the_client_secret_once_and_prints_no_value():
    """v0.27: deploy/rotate-secrets.sh re-aligns the identity provider's `impact-provisioner` client to
    the secret scripts/rotate_secrets.py wrote; idempotent, refused for a short secret or a missing
    client, and the value appears in no call path or result."""
    old, new = "o" * 48, "n" * 48
    fake = FakeKeycloak(realm={"clients": [{"clientId": "impact-provisioner", "secret": old}]})
    result = keycloak_admin.rotate_provisioner(fake, "impact", new)
    assert result == {"client_id": "impact-provisioner", "changed": True}
    assert fake.realm["clients"][0]["secret"] == new and fake.realm["clients"][0]["clientId"] == (
        "impact-provisioner"
    )
    assert keycloak_admin.rotate_provisioner(fake, "impact", new) == {
        "client_id": "impact-provisioner",
        "changed": False,
    }
    assert [c for c in fake.calls if c[0] == "PUT"] == [("PUT", "/impact/clients/c1")]
    assert new not in json.dumps(fake.calls) and old not in json.dumps(fake.calls)
    with pytest.raises(keycloak_admin.AdminError, match="at least 32"):
        keycloak_admin.rotate_provisioner(fake, "impact", "short")
    with pytest.raises(keycloak_admin.AdminError, match="does not exist"):
        keycloak_admin.rotate_provisioner(FakeKeycloak(realm={"clients": []}), "impact", new)
