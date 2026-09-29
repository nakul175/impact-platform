"""Back-channel logout token validation (v0.15) with a local RSA key standing in for the provider's
JWKS: Keycloak cannot be made to sign arbitrary logout tokens, so each refusal rule is exercised
here in-process against the suite database, and the live provider path in test_live_idp.py."""

import time
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from impact_api.auth import BACKCHANNEL_LOGOUT_EVENT, Auth, digest
from impact_api.config import Settings
from impact_api.domain import DomainError
from impact_api.store import Database

ISSUER = "http://127.0.0.1:9/realms/unit-backchannel"


@pytest.fixture
def provider(live):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    settings = Settings(
        **{
            **live.config,
            "dev_auth": False,
            "dev_users_file": "",
            "dev_public_key": "",
            "issuer": ISSUER,
            "jwks_url": ISSUER + "/protocol/openid-connect/certs",
            "authorization_url": ISSUER + "/protocol/openid-connect/auth",
            "token_url": ISSUER + "/protocol/openid-connect/token",
        }
    )
    auth = Auth(settings, Database(settings))
    auth.jwks = SimpleNamespace(get_signing_key_from_jwt=lambda _: SimpleNamespace(key=key.public_key()))
    subject = str(uuid.uuid4())
    identity_id = str(uuid.uuid4())
    with live.db() as c:
        c.execute(
            "INSERT INTO impact.auth_identity VALUES(%s,%s,%s,%s)",
            (identity_id, ISSUER, subject, str(uuid.uuid4())),
        )
    pem = key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )

    def token(header=None, **claims):
        now = int(time.time())
        body = {
            "iss": ISSUER,
            "aud": settings.client_id,
            "iat": now,
            "exp": now + 120,
            "jti": str(uuid.uuid4()),
            "sub": subject,
            "sid": "sid-" + uuid.uuid4().hex,
            "events": {BACKCHANNEL_LOGOUT_EVENT: {}},
        }
        body.update(claims)
        body = {k: v for k, v in body.items() if v is not None}
        return jwt.encode(body, pem, algorithm="RS256", headers={"typ": "logout+jwt", **(header or {})})

    def session(sid):
        identity = auth.identity({"sub": subject, "auth_time": time.time()})
        cookie = (
            auth.session(identity, provider_sid=sid).headers["set-cookie"].split(";", 1)[0].split("=", 1)[1]
        )
        return cookie

    return SimpleNamespace(auth=auth, token=token, session=session, live=live, subject=subject)


def refused(provider, token):
    with pytest.raises(DomainError) as error:
        provider.auth.backchannel_logout(token)
    assert error.value.status == 400 and error.value.reason == "LOGOUT_TOKEN_INVALID"


def revoked(live, cookie):
    with live.db() as c:
        return (
            c.execute(
                "SELECT revoked_at FROM impact.web_session WHERE session_hash=%s", (digest(cookie),)
            ).fetchone()["revoked_at"]
            is not None
        )


def test_valid_logout_token_is_accepted_once(provider):
    sid = "sid-" + uuid.uuid4().hex
    cookie, other = provider.session(sid), provider.session("sid-" + uuid.uuid4().hex)
    token = provider.token(sid=sid)
    response = provider.auth.backchannel_logout(token)
    assert response.status_code == 200 and response.body == b'{"revoked":1}'
    assert revoked(provider.live, cookie) and not revoked(provider.live, other)
    # The same token again (same issuer and jti) is a replay.
    refused(provider, token)
    with provider.live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.oidc_logout_token WHERE issuer=%s AND jti=%s",
                (ISSUER, jwt.decode(token, options={"verify_signature": False})["jti"]),
            ).fetchone()["n"]
            == 1
        )


@pytest.mark.parametrize(
    "header,claims",
    [
        ({}, {"nonce": "n"}),
        ({}, {"iat": int(time.time()) - 400}),
        ({}, {"sid": None}),
        ({}, {"sid": ""}),
        ({}, {"jti": None}),
        ({}, {"exp": None}),
        ({}, {"events": None}),
        ({}, {"events": {"http://schemas.openid.net/event/other": {}}}),
        ({}, {"events": {BACKCHANNEL_LOGOUT_EVENT: "yes"}}),
        ({}, {"aud": "another-client"}),
        ({}, {"iss": "http://127.0.0.1:9/realms/other"}),
        ({"typ": "JWT"}, {}),
    ],
    ids=[
        "nonce",
        "old-iat",
        "no-sid",
        "empty-sid",
        "no-jti",
        "no-exp",
        "no-events",
        "other-event",
        "event-not-object",
        "wrong-aud",
        "wrong-iss",
        "wrong-typ",
    ],
)
def test_invalid_logout_tokens_are_refused(provider, header, claims):
    sid = "sid-" + uuid.uuid4().hex
    cookie = provider.session(sid)
    refused(provider, provider.token(header, **{"sid": sid, **claims}))
    assert not revoked(provider.live, cookie)


def test_expired_replay_records_are_purged(provider):
    old = str(uuid.uuid4())
    with provider.live.db() as c:
        c.execute(
            "INSERT INTO impact.oidc_logout_token(issuer,jti,expires_at) VALUES(%s,%s,%s)",
            (ISSUER, old, datetime.now(timezone.utc) - timedelta(hours=1)),
        )
    provider.auth.backchannel_logout(provider.token())
    with provider.live.db() as c:
        assert not c.execute(
            "SELECT 1 FROM impact.oidc_logout_token WHERE issuer=%s AND jti=%s", (ISSUER, old)
        ).fetchone()
