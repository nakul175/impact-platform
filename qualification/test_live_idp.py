"""Live identity-provider qualification (v0.15) against the Keycloak that
`scripts/run.py test --idp keycloak` starts (scripts/idp.py, realm tools/idp/qualification-realm.json).

Every check drives the real authorization-code flow over HTTP the way a browser does: the platform's
/auth/login redirect, Keycloak's login (and TOTP) forms, the redirect back to /auth/callback, then
the session cookie. The provider's cookies are Secure; browsers send them to http://127.0.0.1
because loopback is a secure context, and `LoopbackJar` does the same. Credentials come from the
per-run <local>/idp.json and are never printed.

Deterministic substitutes, stated where used: elapsed time since authentication is produced by
moving the session's recorded auth_time back 301 s in the database (the platform's own rule is
what is being tested; Keycloak cannot be clock-skewed); token expiry uses a realm access-token
lifespan lowered through the administration API for one token.
"""

import base64
import hashlib
import hmac
import html
import http.cookiejar
import json
import os
import re
import secrets
import struct
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

import httpx
import jwt
import psycopg
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from psycopg.rows import dict_row

pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_IDP") != "keycloak",
    reason="Live identity-provider checks need scripts/run.py test --idp keycloak (a local Keycloak); "
    "the default suites sign in through the development login",
)

ROOT = Path(__file__).resolve().parents[1]
FRESH_WINDOW_SECONDS = 300
# TOTP steps already submitted per user: Keycloak refuses a code it has accepted before.
USED_STEPS = {}


class LoopbackJar(http.cookiejar.CookieJar):
    """A browser's view of loopback: Secure cookies are sent to http://127.0.0.1 (a secure
    context), and Keycloak's Version=1 attribute is not RFC 2965 negotiation."""

    def make_cookies(self, response, request):
        cookies = super().make_cookies(response, request)
        for cookie in cookies:
            cookie.version, cookie.secure = 0, False
        return cookies


def form_action(page, form_id=None):
    for tag in re.findall(r"<form\b[^>]*>", page):
        attrs = dict(re.findall(r'([a-zA-Z-]+)="([^"]*)"', tag))
        if (form_id is None or attrs.get("id") == form_id) and attrs.get("action"):
            return html.unescape(attrs["action"])
    raise AssertionError("No form " + str(form_id) + " on the provider page")


def feedback(page):
    found = re.findall(r'(?s)id="input-error[^"]*"[^>]*>(.*?)<|kc-feedback-text[^>]*>(.*?)<', page)
    return " ".join(" ".join(x).strip() for x in found)


def totp(actor, secret, period=30, digits=6):
    """RFC 6238 over HMAC-SHA1 with the UTF-8 bytes of Keycloak's stored secret; picks a step the
    realm's look-around window (1) accepts and that has not been submitted yet."""
    used = USED_STEPS.setdefault(actor, set())
    while True:
        now = int(time.time()) // period
        step = next((s for s in (now, now + 1) if s not in used), None)
        if step is not None:
            break
        time.sleep(period - time.time() % period + 0.5)
    used.add(step)
    mac = hmac.new(secret.encode(), struct.pack(">Q", step), hashlib.sha1).digest()
    offset = mac[-1] & 15
    return str((struct.unpack(">I", mac[offset : offset + 4])[0] & 0x7FFFFFFF) % 10**digits).zfill(digits)


def challenge(verifier):
    return base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()


def query(url):
    return {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}


def replace_query(url, **params):
    parsed = urlparse(url)
    values = query(url)
    for key, value in params.items():
        if value is None:
            values.pop(key, None)
        else:
            values[key] = value
    return parsed._replace(query=urlencode(values)).geturl()


@pytest.fixture(scope="module")
def idp():
    local = Path(os.environ["IMPACT_TEST_LOCAL"])
    details = json.loads(Path(os.environ["IMPACT_IDP_FILE"]).read_text())
    details["config"] = json.loads((local / "config.json").read_text())
    details["fixture"] = json.loads((ROOT / "specification/fixtures/api-fixture.json").read_text())
    details["origin"] = details["config"]["public_origin"]
    return details


def db():
    return psycopg.connect(os.environ["IMPACT_FIXTURE_DSN"], row_factory=dict_row, prepare_threshold=None)


def sha(value):
    return hashlib.sha256(value.encode()).digest()


class Browser:
    def __init__(self, idp):
        self.idp, self.origin = idp, idp["origin"]
        self.client = httpx.Client(trust_env=False, follow_redirects=False, timeout=30, cookies=LoopbackJar())
        self.csrf = None

    def close(self):
        self.client.close()

    @property
    def session(self):
        return self.client.cookies.get(self.idp["config"].get("cookie_name", "impact_dev_session"))

    def begin(self):
        """The platform's /auth/login redirect: returns the provider authorization URL."""
        response = self.client.get(self.origin + "/auth/login")
        assert response.status_code == 303, response.text
        return response.headers["location"]

    def provider(self, url, actor, otp=True):
        """Keycloak's forms for `actor`; returns the last provider response."""
        user = self.idp["users"][actor]
        page = self.client.get(url)
        assert page.status_code == 200, page.text[:500]
        page = self.client.post(
            form_action(page.text, "kc-form-login"),
            data={"username": user["username"], "password": user["password"], "credentialId": ""},
        )
        if page.status_code == 200 and 'name="otp"' in page.text and otp:
            page = self.client.post(
                form_action(page.text, "kc-otp-login-form"), data={"otp": totp(actor, user["totp_secret"])}
            )
        return page

    def returned(self, page):
        """The redirect back to the platform callback carried by a provider response."""
        assert page.status_code == 302, (page.status_code, feedback(page.text))
        location = page.headers["location"]
        assert location.startswith(self.origin + "/auth/callback?"), location
        return location

    def sign_in(self, actor, strip=(), otp=True):
        url = self.begin()
        if strip:
            url = replace_query(url, **{k: None for k in strip})
        response = self.client.get(self.returned(self.provider(url, actor, otp)))
        assert response.status_code == 303, response.text
        assert self.session
        me = self.get("/auth/me")
        assert me.status_code == 200, me.text
        self.csrf = me.json()["csrf_token"]
        return response

    def get(self, path, **kwargs):
        return self.client.get(self.origin + path, **kwargs)

    def post(self, path, body=None):
        return self.client.post(
            self.origin + path,
            json=body,
            headers={"Origin": self.origin, "X-CSRF-Token": self.csrf or ""},
        )


@pytest.fixture
def browser(idp):
    opened = []

    def make():
        b = Browser(idp)
        opened.append(b)
        return b

    yield make
    for b in opened:
        b.close()


def provider_tokens(idp, actor, acr=None, otp=False, client=None):
    """The test acting as the platform's own client at the provider: authorization code with a
    fresh PKCE pair, then the code exchange. Returns the provider's token response."""
    b = Browser(idp)
    try:
        verifier = secrets.token_urlsafe(48)
        params = {
            "response_type": "code",
            "client_id": idp["client_id"],
            "redirect_uri": idp["origin"] + "/auth/callback",
            "scope": "openid profile email",
            "state": secrets.token_urlsafe(16),
            "nonce": secrets.token_urlsafe(16),
            "code_challenge": challenge(verifier),
            "code_challenge_method": "S256",
            "max_age": "0",
        }
        if acr:
            params["acr_values"] = acr
        base = client or idp["discovery"]
        code = query(
            b.returned(b.provider(base["authorization_endpoint"] + "?" + urlencode(params), actor, otp))
        )["code"]
        response = httpx.post(
            base["token_endpoint"],
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": idp["client_id"],
                "redirect_uri": idp["origin"] + "/auth/callback",
                "code_verifier": verifier,
            },
            trust_env=False,
        )
        assert response.status_code == 200, response.text
        return response.json()
    finally:
        b.close()


def admin(idp):
    response = httpx.post(
        idp["base_url"] + "/realms/master/protocol/openid-connect/token",
        data={
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": idp["admin"]["username"],
            "password": idp["admin"]["password"],
        },
        trust_env=False,
    )
    response.raise_for_status()
    return httpx.Client(
        base_url=idp["base_url"] + "/admin/realms/" + idp["realm"],
        headers={"Authorization": "Bearer " + response.json()["access_token"]},
        trust_env=False,
        timeout=30,
    )


def bearer(idp, token, path):
    return httpx.get(idp["origin"] + path, headers={"Authorization": "Bearer " + token}, trust_env=False)


def tenant_path(idp, route):
    return "/v1/tenants/" + idp["fixture"]["tenant_a"] + "/" + route


def invitation(b, idp):
    """A fresh-assurance operation (invite_member, fresh_assurance_seconds 300) as a session."""
    roles = b.get(tenant_path(idp, "role-templates") + "?limit=100")
    scopes = b.get(tenant_path(idp, "access-scopes") + "?limit=100")
    assert roles.status_code == 200 and scopes.status_code == 200, (roles.text, scopes.text)
    now = datetime.now(timezone.utc)
    return b.post(
        tenant_path(idp, "member-invitations"),
        {
            "operation_id": str(uuid.uuid4()),
            "data": {
                "email": "idp-" + uuid.uuid4().hex[:10] + "@example.test",
                "role_template_id": next(r for r in roles.json()["items"] if r["name"] == "AUTHOR")[
                    "object_id"
                ],
                "scope_ids": [
                    next(s for s in scopes.json()["items"] if s["scope_type"] == "TENANT")["object_id"]
                ],
                "expires_at": (now + timedelta(days=5)).isoformat(),
                "membership_expires_at": (now + timedelta(days=20)).isoformat(),
                "external": True,
                "reason": "Live identity-provider qualification",
            },
        },
    )


def session_row(b):
    with db() as c:
        return c.execute(
            "SELECT * FROM impact.web_session WHERE session_hash=%s", (sha(b.session),)
        ).fetchone()


def test_platform_runs_against_the_live_provider(idp):
    config = idp["config"]
    assert config["dev_auth"] is False and config["issuer"] == idp["issuer"]
    assert config["required_acr"] == idp["required_acr"]
    with httpx.Client(base_url=idp["origin"], trust_env=False) as c:
        assert c.get("/auth/mode").json() == {"development": False}
        refused = c.post(
            "/auth/development-login",
            json={"username": "x", "password": "y"},
            headers={"Origin": idp["origin"]},
        )
        assert refused.status_code == 404
    with db() as c:
        issuers = {
            r["issuer"]
            for r in c.execute(
                "SELECT issuer FROM impact.auth_identity WHERE provider_subject=ANY(%s)",
                ([u["subject"] for u in idp["users"].values()],),
            ).fetchall()
        }
    assert issuers == {idp["issuer"]}


def test_authorization_code_with_pkce_establishes_a_session(idp, browser):
    b = browser()
    url = b.begin()
    params = query(url)
    assert url.startswith(idp["discovery"]["authorization_endpoint"] + "?")
    assert params["code_challenge_method"] == "S256" and len(params["code_challenge"]) == 43
    assert params["max_age"] == "0" and params["acr_values"] == idp["required_acr"]
    assert params["redirect_uri"] == idp["origin"] + "/auth/callback" and params["nonce"] and params["state"]
    callback = b.client.get(b.returned(b.provider(url, "reviewer")))
    assert callback.status_code == 303 and callback.headers["location"] == "/"
    me = b.get("/auth/me")
    assert (
        me.status_code == 200
        and me.json()["identity_id"] == idp["fixture"]["actors"]["reviewer"]["identity_id"]
    )
    assert b.get(tenant_path(idp, "me/access")).status_code == 200
    row = session_row(b)
    assert row["assurance_acr"] == idp["required_acr"] and row["provider_sid"]
    # The logout hint is sealed: the ID token (a JWT, "eyJ...") never appears in the row.
    assert row["provider_logout_hint"] and b"eyJ" not in bytes(row["provider_logout_hint"])
    with db() as c:
        login = c.execute(
            "SELECT consumed_at FROM impact.oidc_login WHERE state_hash=%s", (sha(params["state"]),)
        ).fetchone()
    assert login["consumed_at"] is not None


def test_state_replay_and_browser_binding_are_refused(idp, browser):
    b = browser()
    location = b.returned(b.provider(replace_query(b.begin(), acr_values=None), "author"))
    # Another browser (no impact_oidc cookie) and a wrong cookie value are refused, and neither
    # consumes the state: the browser that started the sign-in can still finish it.
    other = browser()
    assert other.client.get(location).status_code == 401
    forged = browser()
    forged.client.cookies.set("impact_oidc", secrets.token_urlsafe(48), domain="127.0.0.1", path="/auth")
    assert forged.client.get(location).status_code == 401
    assert b.client.get(location).status_code == 303 and b.get("/auth/me").status_code == 200
    # The consumed state cannot be replayed, even by the browser that owned it.
    b.client.cookies.set(
        "impact_oidc", "x", domain="127.0.0.1", path="/auth"
    )  # the callback deleted the real one; any value
    assert b.client.get(location).status_code == 401
    fresh = browser()
    fresh.begin()
    assert fresh.client.get(location).status_code == 401


def test_nonce_mismatch_is_refused(idp, browser):
    """A code minted for the platform's PKCE challenge and state but a different nonce (an injected
    authorization response) passes the provider's PKCE check and fails the platform's nonce check;
    the same crafted request with the stored nonce succeeds, so the nonce is the only difference."""
    results = {}
    for label in ["tampered", "control"]:
        b = browser()
        url = b.begin()
        state = query(url)["state"]
        with db() as c:
            stored = c.execute(
                "SELECT nonce FROM impact.oidc_login WHERE state_hash=%s", (sha(state),)
            ).fetchone()
        nonce = secrets.token_urlsafe(48) if label == "tampered" else stored["nonce"]
        crafted = replace_query(url, nonce=nonce, acr_values=None)
        results[label] = b.client.get(b.returned(b.provider(crafted, "author"))).status_code
        with db() as c:
            consumed = c.execute(
                "SELECT consumed_at FROM impact.oidc_login WHERE state_hash=%s", (sha(state),)
            ).fetchone()["consumed_at"]
        assert consumed is not None
    assert results == {"tampered": 401, "control": 303}


def test_pkce_verifier_mismatch_is_refused(idp, browser):
    # At the provider: a code bound to one challenge is not redeemable with another verifier or
    # without one.
    b = browser()
    verifier = secrets.token_urlsafe(48)
    url = (
        idp["discovery"]["authorization_endpoint"]
        + "?"
        + urlencode(
            {
                "response_type": "code",
                "client_id": idp["client_id"],
                "redirect_uri": idp["origin"] + "/auth/callback",
                "scope": "openid",
                "state": "s",
                "nonce": "n",
                "code_challenge": challenge(verifier),
                "code_challenge_method": "S256",
            }
        )
    )
    code = query(b.returned(b.provider(url, "author")))["code"]
    for supplied in [secrets.token_urlsafe(48), None]:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": idp["client_id"],
            "redirect_uri": idp["origin"] + "/auth/callback",
        }
        if supplied:
            data["code_verifier"] = supplied
        refused = httpx.post(idp["discovery"]["token_endpoint"], data=data, trust_env=False)
        assert refused.status_code == 400 and refused.json()["error"] == "invalid_grant", refused.text
    # At the platform: a code from one sign-in attempt delivered to another attempt's state (same
    # browser, valid cookie) is exchanged with the other attempt's verifier and refused.
    b = browser()
    first = b.returned(b.provider(replace_query(b.begin(), acr_values=None), "author"))
    second = b.begin()
    swapped = (
        b.origin
        + "/auth/callback?"
        + urlencode({"state": query(second)["state"], "code": query(first)["code"]})
    )
    assert b.client.get(swapped).status_code == 401
    assert b.get("/auth/me").status_code == 401


def test_disabled_provider_account_cannot_sign_in(idp, browser):
    b = browser()
    page = b.provider(replace_query(b.begin(), acr_values=None), "revoked")
    assert page.status_code == 200 and "disabled" in feedback(page.text).lower()
    assert b.session is None and b.get("/auth/me").status_code == 401


def test_password_only_session_cannot_perform_fresh_assurance_operations(idp, browser):
    # A user agent that drops acr_values gets a level-1 (password) session: ordinary reads work,
    # a fresh-assurance operation is refused for MFA assurance, whatever the request asked for.
    b = browser()
    b.sign_in("admin", strip=("acr_values",))
    assert session_row(b)["assurance_acr"] == idp["password_acr"]
    assert b.get(tenant_path(idp, "me/access")).status_code == 200
    refused = invitation(b, idp)
    assert refused.status_code == 403, refused.text
    assert (
        refused.json()["code"] == "ASSURANCE_REQUIRED"
        and refused.json()["reason_code"] == "MFA_ASSURANCE_REQUIRED"
    )
    # Account-level fresh-assurance actions follow the same rule.
    assert b.post("/auth/sessions/revoke-all").status_code == 403
    # The unmodified sign-in request makes the provider demand the second factor: a user without
    # one is sent to enrol a TOTP authenticator before any code is issued.
    enrol = browser()
    page = enrol.provider(enrol.begin(), "author")
    assert page.status_code in {200, 302}
    if page.status_code == 302:
        assert "/login-actions/required-action" in page.headers["location"]
        page = enrol.client.get(page.headers["location"])
    assert "totp" in page.text.lower() and enrol.session is None


def test_totp_step_up_allows_fresh_assurance_until_300_seconds(idp, browser):
    b = browser()
    b.sign_in("admin")
    row = session_row(b)
    assert row["assurance_acr"] == idp["required_acr"]
    accepted = invitation(b, idp)
    assert accepted.status_code == 200, accepted.text
    # 301 s after the provider authentication (the recorded auth_time moved back; see module
    # docstring) the same operation needs a new sign-in, while reads still work.
    with db() as c:
        c.execute(
            "UPDATE impact.web_session SET auth_time=auth_time-make_interval(secs=>%s) WHERE session_hash=%s",
            (FRESH_WINDOW_SECONDS + 1, sha(b.session)),
        )
    stale = invitation(b, idp)
    assert stale.status_code == 403 and stale.json()["reason_code"] == "FRESH_AUTHENTICATION_REQUIRED", (
        stale.text
    )
    assert b.get(tenant_path(idp, "me/access")).status_code == 200


def test_bearer_tokens_are_validated_through_the_provider_jwks(idp):
    tokens = provider_tokens(idp, "author")
    # The realm issues no refresh token to this client; the platform holds none either.
    assert "refresh_token" not in tokens
    access = jwt.decode(tokens["access_token"], options={"verify_signature": False})
    assert access["iss"] == idp["issuer"] and access["azp"] == idp["client_id"]
    assert idp["audience"] in ([access["aud"]] if isinstance(access["aud"], str) else access["aud"])
    assert bearer(idp, tokens["access_token"], tenant_path(idp, "me/access")).status_code == 200
    # The ID token (audience impact-web, typ ID) is not a bearer credential.
    assert bearer(idp, tokens["id_token"], tenant_path(idp, "me/access")).status_code == 401
    # A tampered signature, and a token signed by a key outside the provider's JWKS.
    head, body, signature = tokens["access_token"].split(".")
    flipped = signature[:-2] + ("AA" if signature[-2:] != "AA" else "BB")
    assert bearer(idp, ".".join([head, body, flipped]), tenant_path(idp, "me/access")).status_code == 401
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    forged = jwt.encode(
        access,
        key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
        ),
        algorithm="RS256",
        headers={"kid": jwt.get_unverified_header(tokens["access_token"])["kid"]},
    )
    assert bearer(idp, forged, tenant_path(idp, "me/access")).status_code == 401
    # A token from another realm of the same provider (different issuer and keys).
    foreign_base = idp["base_url"] + "/realms/" + idp["foreign_realm"] + "/protocol/openid-connect"
    foreign = dict(idp, users=idp["foreign_users"])
    other = provider_tokens(
        foreign,
        "author",
        client={"authorization_endpoint": foreign_base + "/auth", "token_endpoint": foreign_base + "/token"},
    )
    assert (
        jwt.decode(other["access_token"], options={"verify_signature": False})["iss"] == idp["foreign_issuer"]
    )
    assert bearer(idp, other["access_token"], tenant_path(idp, "me/access")).status_code == 401


def test_expired_provider_token_is_refused(idp):
    with admin(idp) as kc:
        realm = kc.get("").json()
        try:
            assert kc.put("", json={"accessTokenLifespan": 5}).status_code == 204
            tokens = provider_tokens(idp, "author")
        finally:
            assert kc.put("", json={"accessTokenLifespan": realm["accessTokenLifespan"]}).status_code == 204
    expires = jwt.decode(tokens["access_token"], options={"verify_signature": False})["exp"]
    assert bearer(idp, tokens["access_token"], tenant_path(idp, "me/access")).status_code == 200
    # PyJWT allows the platform's 5 s leeway past exp.
    time.sleep(max(0, expires + 7 - time.time()))
    assert bearer(idp, tokens["access_token"], tenant_path(idp, "me/access")).status_code == 401


def test_provider_role_claims_grant_nothing(idp, browser):
    tokens = provider_tokens(idp, "author")
    roles = jwt.decode(tokens["access_token"], options={"verify_signature": False})["realm_access"]["roles"]
    assert {"OWNER", "TENANT_ADMIN"} <= set(roles)
    # author holds no member-invitation or grant capability on the platform; the provider's
    # OWNER/TENANT_ADMIN roles add none, through a bearer token or through a session.
    for route in ["member-invitations", "grants"]:
        assert bearer(idp, tokens["access_token"], tenant_path(idp, route)).status_code == 403
    b = browser()
    b.sign_in("author", strip=("acr_values",))
    assert b.get(tenant_path(idp, "member-invitations")).status_code == 403
    # Nor does the provider's OWNER role make the author a platform operator or tenant owner.
    directory = b.get("/v1/platform/tenants")
    assert directory.status_code == 200 and directory.json()["operator"] is False
    assert directory.json()["items"] == []


def test_logout_revokes_the_session_and_ends_the_provider_session(idp, browser):
    b = browser()
    b.sign_in("owner")
    cookie, sid = b.session, session_row(b)["provider_sid"]
    response = b.post("/auth/logout")
    assert response.status_code == 200 and response.json()["authenticated"] is False
    url = response.json()["logout_url"]
    params = query(url)
    assert url.startswith(idp["discovery"]["end_session_endpoint"] + "?")
    assert (
        params["post_logout_redirect_uri"] == idp["origin"] + "/" and params["client_id"] == idp["client_id"]
    )
    hint = jwt.decode(params["id_token_hint"], options={"verify_signature": False})
    assert hint["sid"] == sid and hint["aud"] == idp["client_id"]
    # The local session is dead at once, whether or not the browser reaches the provider.
    assert b.session is None
    replay = httpx.get(idp["origin"] + "/auth/me", cookies={"impact_dev_session": cookie}, trust_env=False)
    assert replay.status_code == 401
    assert session_row_by(cookie)["revoked_at"] is not None
    # The browser visits the provider logout: with a valid hint there is no confirmation page.
    ended = b.client.get(url)
    assert ended.status_code == 302 and ended.headers["location"] == idp["origin"] + "/", ended.text[:300]
    # The provider session is gone: a silent authorization request needs a new sign-in.
    silent = b.client.get(
        idp["discovery"]["authorization_endpoint"]
        + "?"
        + urlencode(
            {
                "response_type": "code",
                "client_id": idp["client_id"],
                "redirect_uri": idp["origin"] + "/auth/callback",
                "scope": "openid",
                "prompt": "none",
                "state": "s",
                "code_challenge": challenge("v" * 43),
                "code_challenge_method": "S256",
            }
        )
    )
    assert silent.status_code == 302 and query(silent.headers["location"]).get("error") == "login_required"
    with admin(idp) as kc:
        subject = idp["users"]["owner"]["subject"]
        assert all(s["id"] != sid for s in kc.get("/users/" + subject + "/sessions").json())
    # Nothing refresh-capable is held server-side: no column for a provider access or refresh
    # token exists, and the sealed hint is an ID token (not usable at the token endpoint).
    with db() as c:
        columns = {
            r["column_name"]
            for r in c.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_schema='impact' AND table_name IN ('web_session','oidc_login')"
            ).fetchall()
        }
    assert not {c for c in columns if "refresh" in c or "access_token" in c}


def session_row_by(cookie):
    with db() as c:
        return c.execute("SELECT * FROM impact.web_session WHERE session_hash=%s", (sha(cookie),)).fetchone()


def test_provider_administrator_logout_revokes_exactly_that_session(idp, browser):
    first, second = browser(), browser()
    first.sign_in("owner")
    second.sign_in("owner")
    sid_first, sid_second = session_row(first)["provider_sid"], session_row(second)["provider_sid"]
    assert sid_first != sid_second
    with admin(idp) as kc:
        # The administrator ends one provider session; Keycloak sends a signed logout token to
        # the client's back-channel logout URL before answering.
        assert kc.delete("/sessions/" + sid_first).status_code == 204
    deadline = time.time() + 10
    while first.get("/auth/me").status_code != 401 and time.time() < deadline:
        time.sleep(0.2)
    assert first.get("/auth/me").status_code == 401
    assert second.get("/auth/me").status_code == 200
    with db() as c:
        events = c.execute(
            "SELECT count(*) AS n FROM impact.identity_security_event e JOIN impact.web_session s ON s.session_id=e.target_session WHERE e.action='session.provider_logout' AND s.provider_sid=%s",
            (sid_first,),
        ).fetchone()["n"]
    assert events == 1
    # Ending every provider session of the user ends the remaining platform session as well.
    with admin(idp) as kc:
        assert kc.post("/users/" + idp["users"]["owner"]["subject"] + "/logout").status_code == 204
    deadline = time.time() + 10
    while second.get("/auth/me").status_code != 401 and time.time() < deadline:
        time.sleep(0.2)
    assert second.get("/auth/me").status_code == 401


def test_backchannel_logout_refuses_unverified_tokens(idp):
    url = idp["origin"] + "/auth/backchannel-logout"
    form = {"Content-Type": "application/x-www-form-urlencoded"}

    def post(content, headers=form):
        return httpx.post(url, content=content, headers=headers, trust_env=False)

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    tokens = provider_tokens(idp, "author")
    kid = jwt.get_unverified_header(tokens["id_token"])["kid"]
    claims = {
        "iss": idp["issuer"],
        "aud": idp["client_id"],
        "iat": int(time.time()),
        "jti": str(uuid.uuid4()),
        "sid": jwt.decode(tokens["id_token"], options={"verify_signature": False})["sid"],
        "events": {"http://schemas.openid.net/event/backchannel-logout": {}},
    }
    forged = jwt.encode(claims, pem, algorithm="RS256", headers={"kid": kid})
    for response in [
        post("logout_token=not-a-token"),
        post(urlencode({"logout_token": forged})),
        # A provider-signed ID token is not a logout token (no events claim, carries a nonce).
        post(urlencode({"logout_token": tokens["id_token"]})),
        post(urlencode({"logout_token": tokens["id_token"], "extra": "1"})),
        post(json.dumps({"logout_token": tokens["id_token"]}), {"Content-Type": "application/json"}),
        post(""),
    ]:
        assert response.status_code == 400, response.text
        assert response.json()["code"] == "VALIDATION_FAILED"


def test_backchannel_logout_body_is_bounded(idp):
    """A chunked body carries no Content-Length for the middleware to check; the route reads at
    most 16 KiB + 64 bytes and answers 413."""

    def chunks():
        for _ in range(16):
            yield b"logout_token=" + b"a" * 4096

    response = httpx.post(
        idp["origin"] + "/auth/backchannel-logout",
        content=chunks(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        trust_env=False,
    )
    assert response.status_code == 413 and response.json()["code"] == "LIMIT_EXCEEDED", response.text
