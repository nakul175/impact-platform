"""v0.26a unit checks without a database: the generated initial-access-v2 profile, calendar period
generation, the provider account backends (a fake Keycloak admin API over real HTTP and the
development users file), the provisioner client set-up and the configuration rules."""

import json
import sys
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse
from uuid import uuid4
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "deploy"))
import build_access_profile  # noqa: E402
import keycloak_admin  # noqa: E402
from impact_api.access_bootstrap import PROFILE, manifest_for  # noqa: E402
from impact_api.bootstrap_contracts import MANIFEST, ROLE_NAMES  # noqa: E402
from impact_api.contracts import DELEGABLE_CAPABILITIES  # noqa: E402
from impact_api.domain import DomainError  # noqa: E402
from impact_api.provider_accounts import DevelopmentAccounts, KeycloakAccounts, mark_signed_in  # noqa: E402
from impact_api.provider_admin import AdminError, readable_password  # noqa: E402
from impact_api.purpose_grants import PURPOSE_CAPABILITIES  # noqa: E402
from impact_api.reference_data import periods  # noqa: E402
from jsonschema import Draft202012Validator  # noqa: E402


# ---- A2: the onboarding profile -------------------------------------------------------------------


def test_profile_is_generated_from_the_policy_and_covers_every_implemented_capability():
    assert PROFILE == build_access_profile.build()
    assert PROFILE["version"] == "initial-access-v2"
    roles = PROFILE["roles"]
    assert set(roles) == {"TENANT_ADMIN", *ROLE_NAMES}
    union = set().union(*map(set, roles.values()))
    # Every delegable capability of an implemented operation is in some role bundle ...
    assert DELEGABLE_CAPABILITIES <= union
    # ... no role bundle carries a purpose-required capability ...
    assert not union & set(PURPOSE_CAPABILITIES)
    # ... and the purpose-required ones enter the ceiling as purpose-bound only.
    assert set(PROFILE["purpose_bound"]) == set(PURPOSE_CAPABILITIES)
    assert PURPOSE_CAPABILITIES["privacy.approve"] == {"DATA_SUBJECT_REQUEST"}
    assert "INTERNAL_AUDIT" in PURPOSE_CAPABILITIES["audit.export"]
    assert "reference-data.manage" in roles["TENANT_ADMIN"]
    # Separation of duties is still decided per action by natural person; the bundles keep the
    # administrator's access administration apart from programme data.
    assert not {"workflow.approve", "observations.draft.create", "programmes.read"} & set(
        roles["TENANT_ADMIN"]
    )
    Draft202012Validator(MANIFEST).validate(PROFILE)
    Draft202012Validator(MANIFEST).validate(manifest_for(["AUTHOR"]))


def test_v1_manifests_still_validate():
    v1 = {"version": "initial-access-v1", "roles": {"TENANT_ADMIN": ["grant.request"], "AUTHOR": ["x.read"]}}
    Draft202012Validator(MANIFEST).validate(v1)


# ---- A1: calendar periods -----------------------------------------------------------------------


def test_quarterly_periods_are_contiguous_local_midnights():
    result = list(periods("QUARTERLY", "Asia/Kolkata", 2026, 2))
    assert [code for code, _, _ in result] == [
        "2026-Q1",
        "2026-Q2",
        "2026-Q3",
        "2026-Q4",
        "2027-Q1",
        "2027-Q2",
        "2027-Q3",
        "2027-Q4",
    ]
    assert result[0][1] == "2025-12-31T18:30:00+00:00"
    assert result[-1][2] == "2027-12-31T18:30:00+00:00"
    for (_, _, end), (_, start, _) in zip(result, result[1:]):
        assert end == start


def test_monthly_periods_follow_summer_time_and_annual_is_one_period():
    monthly = list(periods("MONTHLY", "Europe/London", 2026, 1))
    assert len(monthly) == 12 and monthly[2] == (
        "2026-03",
        "2026-03-01T00:00:00+00:00",
        "2026-03-31T23:00:00+00:00",
    )
    assert list(periods("ANNUAL", "UTC", 2030, 1)) == [
        ("2030", "2030-01-01T00:00:00+00:00", "2031-01-01T00:00:00+00:00")
    ]
    with pytest.raises(DomainError):
        list(periods("ANNUAL", "Nowhere/City", 2030, 1))


# ---- A3: provider accounts --------------------------------------------------------------------------


class FakeRealm(BaseHTTPRequestHandler):
    """The admin REST calls of impact_api/provider_admin.py over HTTP, with a client-credentials
    token endpoint that accepts only the configured provisioner secret."""

    users = {}
    calls = []
    secret = "s" * 40

    def log_message(self, *args):
        pass

    def reply(self, status, body=None):
        raw = b"" if body is None else json.dumps(body).encode()
        self.send_response(status)
        if raw:
            self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def body(self):
        length = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(length) if length else b""

    def authorised(self):
        return self.headers.get("Authorization") == "Bearer service-token"

    def handle_any(self, method):
        url = urlparse(self.path)
        raw = self.body()
        FakeRealm.calls.append((method, url.path, raw.decode(errors="replace")))
        if url.path == "/realms/impact/protocol/openid-connect/token":
            form = parse_qs(raw.decode())
            if form.get("grant_type") == ["client_credentials"] and form.get("client_secret") == [
                self.secret
            ]:
                return self.reply(200, {"access_token": "service-token"})
            return self.reply(401, {"error": "unauthorized_client"})
        if not self.authorised():
            return self.reply(401)
        parts = url.path.split("/")
        if url.path == "/admin/realms/impact/users" and method == "GET":
            email = parse_qs(url.query)["email"][0].lower()
            return self.reply(200, [u for u in self.users.values() if u["email"] == email])
        if url.path == "/admin/realms/impact/users" and method == "POST":
            user = dict(json.loads(raw), id=str(uuid4()))
            self.users[user["id"]] = user
            return self.reply(201)
        if "attack-detection" in url.path:
            return self.reply(204)
        user = self.users[parts[5]]
        if url.path.endswith("/credentials"):
            return self.reply(200, [])
        if url.path.endswith("/reset-password"):
            user["credentials"] = [json.loads(raw)]
            return self.reply(204)
        if method == "PUT":
            user.update(json.loads(raw))
            return self.reply(204)
        return self.reply(404)

    def do_GET(self):
        self.handle_any("GET")

    def do_POST(self):
        self.handle_any("POST")

    def do_PUT(self):
        self.handle_any("PUT")

    def do_DELETE(self):
        self.handle_any("DELETE")


@pytest.fixture
def fake_realm():
    FakeRealm.users, FakeRealm.calls = {}, []
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeRealm)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield "http://127.0.0.1:" + str(server.server_address[1])
    server.shutdown()


def settings(url, secret=FakeRealm.secret):
    return SimpleNamespace(
        provider_admin="keycloak",
        provider_admin_url=url,
        provider_admin_realm="impact",
        provider_admin_client_id="impact-provisioner",
        provider_admin_client_secret=secret,
    )


def test_keycloak_accounts_create_once_reissue_and_never_echo_passwords(fake_realm):
    accounts = KeycloakAccounts(settings(fake_realm))
    first = accounts.create("New.Person@Example.org", "New", "Person")
    assert first["created"] and len(first["password"]) == 24
    user = FakeRealm.users[first["subject"]]
    # The same account shape as deploy/add-user.sh: e-mail username, verified, required actions.
    assert user["username"] == "new.person@example.org" and user["emailVerified"] is True
    assert user["requiredActions"] == ["UPDATE_PASSWORD", "CONFIGURE_TOTP"]
    assert user["credentials"] == [{"type": "password", "value": first["password"], "temporary": True}]
    again = accounts.create("new.person@example.org", "New", "Person")
    assert again == {"subject": first["subject"], "created": False, "password": None}
    assert accounts.pending("new.person@example.org")["temporary_password_pending"] is True
    reissued = accounts.reissue("new.person@example.org")
    assert reissued["password"] != first["password"]
    assert user["credentials"] == [{"type": "password", "value": reissued["password"], "temporary": True}]
    with pytest.raises(DomainError) as missing:
        accounts.reissue("nobody@example.org")
    assert missing.value.status == 404
    # Only the realm's own token endpoint and admin API were called; no master-realm sign-in.
    assert all(
        path.startswith(("/realms/impact/", "/admin/realms/impact/")) for _, path, _ in FakeRealm.calls
    )


def test_keycloak_accounts_fail_closed_without_the_service_account(fake_realm):
    with pytest.raises(DomainError) as refused:
        KeycloakAccounts(settings(fake_realm, secret="w" * 40)).create("a@example.org", "A", "B")
    assert refused.value.status == 503 and refused.value.reason == "PROVIDER_ADMIN_UNAVAILABLE"
    with pytest.raises(DomainError) as down:
        KeycloakAccounts(settings("http://127.0.0.1:9")).create("a@example.org", "A", "B")
    assert down.value.status == 503


def test_development_accounts_and_first_sign_in(tmp_path):
    accounts = DevelopmentAccounts(SimpleNamespace(dev_users_file=str(tmp_path / "users.json")))
    created = accounts.create("dev@example.org", "Dev", "Person")
    assert created["created"] and created["password"]
    assert accounts.create("dev@example.org", "Dev", "Person")["password"] is None
    stored = json.loads((tmp_path / "users.json").read_text())
    assert created["password"] not in json.dumps(stored) and stored["dev@example.org"]["temporary"] is True
    assert accounts.pending("dev@example.org")["temporary_password_pending"] is True
    mark_signed_in(str(tmp_path / "users.json"), "dev@example.org")
    assert accounts.pending("dev@example.org")["temporary_password_pending"] is False
    assert (tmp_path / "users.json").stat().st_mode & 0o777 == 0o600


def test_readable_passwords_are_long_and_unambiguous():
    values = {readable_password() for _ in range(200)}
    assert len(values) == 200
    assert all(len(v) == 24 and not set(v) & set("01ilo") for v in values)


class FakeProvisioning:
    """The client and role-mapping calls of keycloak_admin.ensure_provisioner."""

    def __init__(self):
        self.clients, self.secrets, self.mappings, self.calls = {}, {}, [], []

    def call(self, method, path, data=None, expect=(200, 201, 204)):
        self.calls.append((method, path.split("?")[0]))
        if path.startswith("/impact/clients?clientId=realm-management"):
            return 200, [{"id": "rm", "clientId": "realm-management"}], {}
        if path.startswith("/impact/clients?clientId="):
            return 200, [c for c in self.clients.values()], {}
        if method == "POST" and path == "/impact/clients":
            self.clients["p1"] = {k: v for k, v in data.items() if k != "secret"} | {"id": "p1"}
            self.secrets["p1"] = data["secret"]
            return 201, None, {}
        if path == "/impact/clients/p1/client-secret":
            return 200, {"type": "secret", "value": self.secrets["p1"]}, {}
        if method == "PUT" and path == "/impact/clients/p1":
            self.secrets["p1"] = data["secret"]
            return 204, None, {}
        if path == "/impact/clients/p1/service-account-user":
            return 200, {"id": "sa"}, {}
        if path.startswith("/impact/clients/rm/roles/"):
            return 200, {"id": "r-" + path.split("/")[-1], "name": path.split("/")[-1]}, {}
        if path == "/impact/users/sa/role-mappings/clients/rm":
            if method == "GET":
                return 200, list(self.mappings), {}
            if method == "POST":
                self.mappings.extend(data)
            else:
                self.mappings = [r for r in self.mappings if r not in data]
            return 204, None, {}
        raise AssertionError((method, path))


def test_provisioner_client_holds_exactly_user_management():
    fake = FakeProvisioning()
    with pytest.raises(AdminError):
        keycloak_admin.ensure_provisioner(fake, "impact", "short")
    first = keycloak_admin.ensure_provisioner(fake, "impact", "p" * 48)
    assert first["created"] and first["roles_added"] == ["manage-users", "query-users", "view-users"]
    client = fake.clients["p1"]
    assert client["serviceAccountsEnabled"] and not client["publicClient"]
    assert not client["standardFlowEnabled"] and not client["directAccessGrantsEnabled"]
    again = keycloak_admin.ensure_provisioner(fake, "impact", "p" * 48)
    assert again == {
        "client_id": "impact-provisioner",
        "created": False,
        "updated": False,
        "roles_added": [],
        "roles_removed": [],
    }
    fake.mappings.append({"id": "r-realm-admin", "name": "realm-admin"})
    changed = keycloak_admin.ensure_provisioner(fake, "impact", "q" * 48)
    assert changed["updated"] and changed["roles_removed"] == ["realm-admin"]
    assert fake.secrets["p1"] == "q" * 48
    assert {r["name"] for r in fake.mappings} == {"manage-users", "view-users", "query-users"}


def test_provider_admin_configuration_rules(monkeypatch, tmp_path):
    from impact_api.config import Settings

    base = {
        "environment": "test",
        "app_dsn": "x",
        "identity_dsn": "x",
        "public_origin": "http://127.0.0.1:8000",
        "issuer": "http://127.0.0.1:8080/realms/impact-dev",
        "client_id": "impact-web",
        "audience": "impact-api",
        "jwks_url": "",
        "authorization_url": "",
        "token_url": "",
        "cookie_secret": "c" * 64,
        "dev_auth": True,
        "dev_users_file": str(tmp_path / "users.json"),
    }

    def load(**changes):
        path = tmp_path / "config.json"
        path.write_text(json.dumps({**base, **changes}))
        monkeypatch.setenv("IMPACT_CONFIG_FILE", str(path))
        return Settings.load()

    assert load(provider_admin="development").provider_admin == "development"
    with pytest.raises(ValueError):
        load(provider_admin="ldap")
    with pytest.raises(ValueError):
        load(provider_admin="development", dev_auth=False)
    with pytest.raises(ValueError):
        load(
            provider_admin="keycloak",
            provider_admin_url="http://keycloak:8080",
            provider_admin_realm="impact",
        )
    settings = load(
        provider_admin="keycloak",
        provider_admin_url="http://keycloak:8080",
        provider_admin_realm="impact",
        provider_admin_client_id="impact-provisioner",
        provider_admin_client_secret="z" * 40,
    )
    assert "z" * 40 not in repr(settings)


def test_account_creation_without_a_provider_is_unavailable():
    from impact_api.operators import Operators

    lifecycle = SimpleNamespace(
        db=None,
        s=SimpleNamespace(provider_admin="", platform_dsn="x"),
        assurance=lambda identity: None,
    )
    operators = Operators(lifecycle)
    identity = SimpleNamespace(identity_id=str(uuid4()), auth_time=datetime.now(timezone.utc))
    body = {
        "operation_id": str(uuid4()),
        "data": {
            "email": "a@example.org",
            "first_name": "A",
            "last_name": "B",
            "nomination_id": None,
            "tenant_id": None,
            "reason": "r",
        },
    }
    with pytest.raises(DomainError) as refused:
        operators.account(identity, "create", body)
    assert refused.value.status == 503 and refused.value.reason == "PROVIDER_ADMIN_NOT_CONFIGURED"
