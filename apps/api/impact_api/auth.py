from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
import hashlib
import hmac
import json
import secrets
import time
import base64
import httpx
import jwt
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi.responses import JSONResponse, RedirectResponse
from .domain import DomainError, unavailable
from .identity_profile import normalize_email, email_hash, masked_email


SESSION_ACTIVITY_INTERVAL_SECONDS = 30
# OpenID Connect Back-Channel Logout 1.0, section 2.4.
BACKCHANNEL_LOGOUT_EVENT = "http://schemas.openid.net/event/backchannel-logout"
# A logout token older than this is refused; the provider sends it at the moment of logout.
LOGOUT_TOKEN_MAX_AGE_SECONDS = 300
LOGOUT_HINT_CONTEXT = b"impact-provider-logout-hint"


def digest(value):
    return hashlib.sha256(value.encode()).digest()


@dataclass(frozen=True)
class Identity:
    identity_id: str
    natural_identity_id: str
    subject: str
    auth_time: datetime
    session_id: str | None = None
    verified_email_hash: bytes | None = None
    display_name: str = ""
    email_mask: str | None = None
    assurance_acr: str = ""
    assurance_amr: tuple = ()
    assurance_verified: bool = False


class Auth:
    def __init__(self, s, db):
        self.s, self.db = s, db
        self.jwks = (
            jwt.PyJWKClient(s.jwks_url, cache_keys=False, lifespan=60, timeout=5) if s.jwks_url else None
        )

    def csrf(self, session):
        return hmac.new(
            self.s.cookie_secret.encode(), ("csrf:" + session).encode(), hashlib.sha256
        ).hexdigest()

    def origin(self, request):
        if request.headers.get("origin") != self.s.public_origin:
            raise DomainError("POLICY_DENIED", 403, reason="ORIGIN_REQUIRED")

    def claims(self, token, audience=None):
        try:
            if len(token) > 16384:
                raise ValueError
            key = (
                Path(self.s.dev_public_key).read_bytes()
                if self.s.dev_auth
                else self.jwks.get_signing_key_from_jwt(token).key
            )
            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                issuer=self.s.issuer,
                audience=audience or self.s.audience,
                options={"require": ["exp", "iat", "iss", "sub", "aud"]},
                leeway=5,
            )
            if claims.get("azp", self.s.client_id) != self.s.client_id:
                raise ValueError
            return claims
        except (jwt.PyJWTError, ValueError, OSError):
            raise DomainError("AUTH_REQUIRED", 401) from None

    def identity(self, claims):
        try:
            # Token issuance is not evidence of a recent human authentication.
            # Missing auth_time permits ordinary reads but never fresh-assurance commands.
            instant = claims.get("auth_time", 0)
            if (
                not isinstance(instant, (int, float))
                or isinstance(instant, bool)
                or instant < 0
                or instant > time.time() + 5
            ):
                raise ValueError
            authenticated = datetime.fromtimestamp(instant, timezone.utc)
        except (ValueError, TypeError, OverflowError):
            raise DomainError("AUTH_REQUIRED", 401) from None
        acr, amr = claims.get("acr", ""), claims.get("amr", [])
        if (
            not isinstance(acr, str)
            or len(acr) > 200
            or not isinstance(amr, list)
            or len(amr) > 20
            or any(not isinstance(a, str) or len(a) > 100 for a in amr)
        ):
            raise DomainError("AUTH_REQUIRED", 401)
        with self.db.transaction(identity=True) as c:
            row = c.execute(
                "SELECT i.identity_id,i.natural_identity_id,s.auth_not_before FROM impact.auth_identity i LEFT JOIN impact.identity_security_state s USING(identity_id) WHERE i.issuer=%s AND i.provider_subject=%s",
                (self.s.issuer, claims["sub"]),
            ).fetchone()
        if not row or (row.get("auth_not_before") and authenticated <= row["auth_not_before"]):
            raise DomainError("AUTH_REQUIRED", 401)
        profile = {}
        with self.db.transaction(identity=True) as c:
            if claims.get("email_verified") is True:
                email = normalize_email(claims.get("email"))
                name = claims.get("name") or "Member"
                name = " ".join(str(name).split())[:120]
                profile = {
                    "verified_email_hash": email_hash(email),
                    "display_name": name,
                    "email_mask": masked_email(email),
                }
                c.execute(
                    "INSERT INTO impact.identity_profile(identity_id,display_name,verified_email_hash,email_mask,verified_at) VALUES(%s,%s,%s,%s,now()) ON CONFLICT(identity_id) DO UPDATE SET display_name=EXCLUDED.display_name,verified_email_hash=EXCLUDED.verified_email_hash,email_mask=EXCLUDED.email_mask,verified_at=EXCLUDED.verified_at",
                    (row["identity_id"], name, profile["verified_email_hash"], profile["email_mask"]),
                )
            elif self.s.dev_auth:
                profile = (
                    c.execute(
                        "SELECT * FROM impact.identity_profile WHERE identity_id=%s", (row["identity_id"],)
                    ).fetchone()
                    or {}
                )
        return Identity(
            str(row["identity_id"]),
            str(row["natural_identity_id"]),
            claims["sub"],
            authenticated,
            verified_email_hash=bytes(profile["verified_email_hash"])
            if profile.get("verified_email_hash")
            else None,
            display_name=profile.get("display_name", ""),
            email_mask=profile.get("email_mask"),
            assurance_acr=acr,
            assurance_amr=tuple(amr),
            assurance_verified=acr == self.s.required_acr if self.s.required_acr else self.s.dev_auth,
        )

    def resolve(self, request):
        bearer = request.headers.get("authorization")
        session = request.cookies.get(self.s.cookie_name)
        if bearer and session:
            raise DomainError("AUTH_REQUIRED", 401, reason="CONFLICTING_IDENTITY")
        if bearer:
            if not bearer.startswith("Bearer "):
                raise DomainError("AUTH_REQUIRED", 401)
            claims = self.claims(bearer[7:])
            # A provider marks its tokens by type; only an access token is a bearer credential
            # here, never an ID or logout token, whatever audience the deployment configures.
            if claims.get("typ", "Bearer") != "Bearer":
                raise DomainError("AUTH_REQUIRED", 401)
            return self.identity(claims)
        if not session or len(session) > 256:
            raise DomainError("AUTH_REQUIRED", 401)
        now = datetime.now(timezone.utc)
        with self.db.transaction(identity=True) as c:
            # A plain read: a browser's parallel requests on one session must not queue behind
            # each other. The idle limit (15 min since last activity) and the absolute limit
            # (expires_at, 8 h from sign-in) are evaluated on the row as read.
            row = c.execute(
                "SELECT s.*,i.natural_identity_id,i.provider_subject FROM impact.web_session s JOIN impact.auth_identity i USING(identity_id) WHERE s.session_hash=%s",
                (digest(session),),
            ).fetchone()
            if (
                not row
                or row["revoked_at"]
                or row["expires_at"] <= now
                or row["last_seen_at"] < now - timedelta(minutes=15)
            ):
                raise DomainError("AUTH_REQUIRED", 401)
            if request.method not in {"GET", "HEAD", "OPTIONS"}:
                self.origin(request)
                if not hmac.compare_digest(request.headers.get("x-csrf-token", ""), self.csrf(session)):
                    raise DomainError("POLICY_DENIED", 403, reason="CSRF_REQUIRED")
            # Activity is recorded at most every 30 s. In a burst of N requests on one session
            # after 30 s of inactivity, all N pass the check on the row as read; the first UPDATE
            # takes the row lock and the other N-1 wait briefly on it, then match zero rows once
            # the predicate is re-evaluated against the advanced last_seen_at, so exactly one
            # write happens. A 30 s lag never extends the 15-minute idle window beyond what the
            # last recorded activity allows.
            if row["last_seen_at"] < now - timedelta(seconds=SESSION_ACTIVITY_INTERVAL_SECONDS):
                c.execute(
                    "UPDATE impact.web_session SET last_seen_at=%s WHERE session_hash=%s AND last_seen_at<%s",
                    (now, digest(session), now - timedelta(seconds=SESSION_ACTIVITY_INTERVAL_SECONDS)),
                )
        return Identity(
            str(row["identity_id"]),
            str(row["natural_identity_id"]),
            row["provider_subject"],
            row["auth_time"],
            session,
            bytes(row["verified_email_hash"]) if row["verified_email_hash"] else None,
            row["display_name"] or "",
            row["email_mask"],
            row["assurance_acr"],
            tuple(row["assurance_amr"]),
            row["assurance_acr"] == self.s.required_acr if self.s.required_acr else self.s.dev_auth,
        )

    def hint_key(self, session):
        return hmac.new(
            self.s.cookie_secret.encode(), b"logout-hint:" + session.encode(), hashlib.sha256
        ).digest()

    def seal_hint(self, session, id_token):
        """The ID token for the provider's logout request, encrypted under a key derived from the
        session cookie value (never stored) and the cookie secret."""
        nonce = secrets.token_bytes(12)
        return nonce + AESGCM(self.hint_key(session)).encrypt(nonce, id_token.encode(), LOGOUT_HINT_CONTEXT)

    def open_hint(self, session, sealed):
        try:
            sealed = bytes(sealed)
            return (
                AESGCM(self.hint_key(session)).decrypt(sealed[:12], sealed[12:], LOGOUT_HINT_CONTEXT).decode()
            )
        except (InvalidTag, ValueError, UnicodeDecodeError):
            return None

    def session(
        self, identity, redirect=False, device_label="Browser session", provider_sid=None, id_token=None
    ):
        session = secrets.token_urlsafe(48)
        now = datetime.now(timezone.utc)
        with self.db.transaction(identity=True) as c:
            c.execute(
                "SELECT identity_id FROM impact.auth_identity WHERE identity_id=%s FOR UPDATE",
                (identity.identity_id,),
            )
            cutoff = c.execute(
                "SELECT auth_not_before FROM impact.identity_security_state WHERE identity_id=%s",
                (identity.identity_id,),
            ).fetchone()
            if cutoff and identity.auth_time <= cutoff["auth_not_before"]:
                raise DomainError("AUTH_REQUIRED", 401)
            if (
                c.execute(
                    "SELECT count(*) AS n FROM impact.web_session WHERE identity_id=%s AND revoked_at IS NULL AND expires_at>now() AND last_seen_at>now()-interval '15 minutes'",
                    (identity.identity_id,),
                ).fetchone()["n"]
                >= 50
            ):
                raise DomainError("LIMIT_EXCEEDED", 429, reason="SESSION_LIMIT")
            c.execute(
                "INSERT INTO impact.web_session(session_hash,identity_id,created_at,last_seen_at,expires_at,auth_time,verified_email_hash,display_name,email_mask,assurance_acr,assurance_amr,device_label,provider_sid,provider_logout_hint) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    digest(session),
                    identity.identity_id,
                    now,
                    now,
                    now + timedelta(hours=8),
                    identity.auth_time,
                    identity.verified_email_hash,
                    identity.display_name,
                    identity.email_mask,
                    identity.assurance_acr,
                    list(identity.assurance_amr),
                    device_label,
                    provider_sid,
                    self.seal_hint(session, id_token) if id_token else None,
                ),
            )
        response = RedirectResponse("/", 303) if redirect else JSONResponse({"authenticated": True})
        response.set_cookie(
            self.s.cookie_name,
            session,
            httponly=True,
            secure=self.s.secure,
            samesite="lax",
            max_age=28800,
            path="/",
        )
        response.headers["Cache-Control"] = "no-store"
        return response

    def dev_login(self, request, body):
        if not self.s.dev_auth:
            unavailable()
        self.origin(request)
        if set(body) != {"username", "password"} or not all(isinstance(x, str) for x in body.values()):
            raise DomainError("VALIDATION_FAILED")
        username, password = body["username"], body["password"]
        if len(username) > 200 or len(password) > 256:
            raise DomainError("AUTH_REQUIRED", 401)
        now = datetime.now(timezone.utc)
        keys = [
            digest("account:" + username),
            digest("network:" + (request.client.host if request.client else "local")),
        ]
        with self.db.transaction(identity=True) as c:
            for key in sorted(keys):
                c.execute(
                    "INSERT INTO impact.login_attempt VALUES(%s,%s,0) ON CONFLICT DO NOTHING", (key, now)
                )
                row = c.execute(
                    "SELECT * FROM impact.login_attempt WHERE attempt_hash=%s FOR UPDATE", (key,)
                ).fetchone()
                if row["window_start"] < now - timedelta(minutes=5):
                    c.execute(
                        "UPDATE impact.login_attempt SET failures=0,window_start=%s WHERE attempt_hash=%s",
                        (now, key),
                    )
                elif row["failures"] >= 10:
                    raise DomainError(
                        "LIMIT_EXCEEDED", 429, message="Too many sign-in attempts. Try again later."
                    )
                c.execute("UPDATE impact.login_attempt SET failures=failures+1 WHERE attempt_hash=%s", (key,))
        user = json.loads(Path(self.s.dev_users_file).read_text()).get(username)
        salt = bytes.fromhex(user["salt"]) if user else b"unknown-account-salt"
        computed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600000).hex()
        if not user or not hmac.compare_digest(computed, user["password_hash"]):
            raise DomainError("AUTH_REQUIRED", 401)
        return self.session(
            self.identity({"sub": user["subject"], "iat": int(time.time()), "auth_time": time.time()}),
            device_label=self.device_label(request),
        )

    def device_label(self, request):
        agent = request.headers.get("user-agent", "")
        browser = next(
            (
                label
                for token, label in [
                    ("Edg/", "Edge"),
                    ("Firefox/", "Firefox"),
                    ("Chrome/", "Chrome"),
                    ("Safari/", "Safari"),
                ]
                if token in agent
            ),
            "Browser",
        )
        platform = next(
            (
                label
                for token, label in [
                    ("Android", "Android"),
                    ("iPhone", "iPhone"),
                    ("Windows", "Windows"),
                    ("Macintosh", "macOS"),
                    ("Linux", "Linux"),
                ]
                if token in agent
            ),
            "unknown device",
        )
        return browser + " on " + platform

    def login(self):
        state, browser, nonce, verifier = [secrets.token_urlsafe(48) for _ in range(4)]
        challenge = base64.urlsafe_b64encode(digest(verifier)).rstrip(b"=").decode()
        with self.db.transaction(identity=True) as c:
            c.execute(
                "INSERT INTO impact.oidc_login(state_hash,browser_hash,nonce,verifier,expires_at) VALUES(%s,%s,%s,%s,%s)",
                (
                    digest(state),
                    digest(browser),
                    nonce,
                    verifier,
                    datetime.now(timezone.utc) + timedelta(minutes=5),
                ),
            )
        params = {
            "response_type": "code",
            "client_id": self.s.client_id,
            "redirect_uri": self.s.public_origin + "/auth/callback",
            "scope": "openid profile email",
            "max_age": "0",
            "state": state,
            "nonce": nonce,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
        if self.s.required_acr:
            params["acr_values"] = self.s.required_acr
        response = RedirectResponse(self.s.authorization_url + "?" + urlencode(params), 303)
        response.set_cookie(
            "impact_oidc",
            browser,
            httponly=True,
            secure=self.s.secure,
            samesite="lax",
            max_age=300,
            path="/auth",
        )
        return response

    def callback(self, request):
        state, code = request.query_params.get("state", ""), request.query_params.get("code", "")
        if len(state) > 256 or not code or len(code) > 4096:
            raise DomainError("AUTH_REQUIRED", 401)
        with self.db.transaction(identity=True) as c:
            login = c.execute(
                "SELECT * FROM impact.oidc_login WHERE state_hash=%s FOR UPDATE", (digest(state),)
            ).fetchone()
            if (
                not login
                or login["consumed_at"]
                or login["expires_at"] < datetime.now(timezone.utc)
                or not hmac.compare_digest(
                    bytes(login["browser_hash"]), digest(request.cookies.get("impact_oidc", ""))
                )
            ):
                raise DomainError("AUTH_REQUIRED", 401)
            c.execute("UPDATE impact.oidc_login SET consumed_at=now() WHERE state_hash=%s", (digest(state),))
        # The code exchange is an external call and runs after the state row is committed as
        # consumed, never inside a database transaction. Only the ID token is read from the
        # response; an access or refresh token the provider may return is discarded unread.
        try:
            response = httpx.post(
                self.s.token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": self.s.client_id,
                    "redirect_uri": self.s.public_origin + "/auth/callback",
                    "code_verifier": login["verifier"],
                },
                auth=(self.s.client_id, self.s.client_secret) if self.s.client_secret else None,
                timeout=8,
                follow_redirects=False,
            )
            response.raise_for_status()
            id_token = response.json()["id_token"]
            claims = self.claims(id_token, self.s.client_id)
            if not isinstance(claims.get("nonce"), str) or not hmac.compare_digest(
                claims["nonce"], login["nonce"]
            ):
                raise ValueError
            sid = claims.get("sid")
            if sid is not None and (not isinstance(sid, str) or not sid or len(sid) > 255):
                raise ValueError
        except (httpx.HTTPError, KeyError, ValueError, TypeError):
            raise DomainError("AUTH_REQUIRED", 401) from None
        identity = self.identity(claims)
        if (datetime.now(timezone.utc) - identity.auth_time).total_seconds() > 300:
            raise DomainError("AUTH_REQUIRED", 401)
        response = self.session(identity, True, self.device_label(request), sid, id_token)
        response.delete_cookie("impact_oidc", path="/auth")
        return response

    def logout(self, request):
        """Revoke the presented browser session and, with a live provider, return the provider's
        RP-initiated logout URL for the browser to visit (the ID token hint is unsealed with the
        session cookie). Nothing is sent to the provider from here."""
        identity = self.resolve(request)
        sealed = None
        if identity.session_id:
            with self.db.transaction(identity=True) as c:
                row = c.execute(
                    "UPDATE impact.web_session SET revoked_at=COALESCE(revoked_at,now()) WHERE session_hash=%s RETURNING provider_logout_hint",
                    (digest(identity.session_id),),
                ).fetchone()
                sealed = row["provider_logout_hint"] if row else None
        url = None
        if identity.session_id and not self.s.dev_auth and self.s.end_session_url:
            params = {"client_id": self.s.client_id, "post_logout_redirect_uri": self.s.public_origin + "/"}
            hint = self.open_hint(identity.session_id, sealed) if sealed else None
            if hint:
                params["id_token_hint"] = hint
            url = self.s.end_session_url + "?" + urlencode(params)
        response = JSONResponse({"authenticated": False, "logout_url": url})
        response.delete_cookie(self.s.cookie_name, path="/")
        return response

    def backchannel_logout(self, token):
        """OpenID Connect Back-Channel Logout: a logout token signed by the configured provider for
        this client revokes the platform sessions created from the named provider session (sid,
        and the subject when present). Each token (issuer, jti) is accepted once. The signing key
        is fetched before any transaction."""
        if self.s.dev_auth or not self.jwks:
            unavailable()
        claims = self.logout_claims(token)
        sid, subject = claims["sid"], claims.get("sub")
        with self.db.transaction(identity=True) as c:
            # Opportunistic, bounded purge of replay records whose tokens have expired.
            c.execute(
                "DELETE FROM impact.oidc_logout_token WHERE ctid IN (SELECT ctid FROM impact.oidc_logout_token WHERE expires_at<now()-interval '5 minutes' LIMIT 100)"
            )
            if not c.execute(
                "INSERT INTO impact.oidc_logout_token(issuer,jti,expires_at) VALUES(%s,%s,%s) ON CONFLICT DO NOTHING RETURNING jti",
                (
                    self.s.issuer,
                    claims["jti"],
                    datetime.fromtimestamp(claims["exp"], timezone.utc),
                ),
            ).fetchone():
                raise DomainError("VALIDATION_FAILED", 400, reason="LOGOUT_TOKEN_INVALID")
            rows = c.execute(
                "UPDATE impact.web_session s SET revoked_at=now() FROM impact.auth_identity i WHERE i.identity_id=s.identity_id AND i.issuer=%s AND s.provider_sid=%s AND (%s::text IS NULL OR i.provider_subject=%s) AND s.revoked_at IS NULL RETURNING s.identity_id,s.session_id",
                (self.s.issuer, sid, subject, subject),
            ).fetchall()
            for row in rows:
                c.execute(
                    "INSERT INTO impact.identity_security_event(event_id,identity_id,action,target_session) VALUES(gen_random_uuid(),%s,'session.provider_logout',%s)",
                    (row["identity_id"], row["session_id"]),
                )
        response = JSONResponse({"revoked": len(rows)})
        response.headers["Cache-Control"] = "no-store"
        return response

    def logout_claims(self, token):
        """The verified claims of a logout token, or VALIDATION_FAILED 400: RS256 signature from the
        provider JWKS, header typ logout+jwt, issuer, audience = client_id, iat (at most 300 s old),
        exp, jti, the back-channel event, no nonce, and a provider session identifier."""
        try:
            if not isinstance(token, str) or len(token) > 16384:
                raise ValueError
            if jwt.get_unverified_header(token).get("typ") != "logout+jwt":
                raise ValueError
            claims = jwt.decode(
                token,
                self.jwks.get_signing_key_from_jwt(token).key,
                algorithms=["RS256"],
                issuer=self.s.issuer,
                audience=self.s.client_id,
                options={"require": ["iat", "exp", "iss", "aud", "jti"]},
                leeway=5,
            )
            events = claims.get("events")
            if (
                not isinstance(events, dict)
                or not isinstance(events.get(BACKCHANNEL_LOGOUT_EVENT), dict)
                or "nonce" in claims
                or not isinstance(claims["iat"], (int, float))
                or isinstance(claims["iat"], bool)
                or claims["iat"] < time.time() - LOGOUT_TOKEN_MAX_AGE_SECONDS
                or not isinstance(claims["exp"], (int, float))
                or isinstance(claims["exp"], bool)
                or not isinstance(claims["jti"], str)
                or not claims["jti"]
                or len(claims["jti"]) > 255
            ):
                raise ValueError
            sid, subject = claims.get("sid"), claims.get("sub")
            # This client registers with session-required back-channel logout, so a token
            # without a provider session identifier is refused rather than widened to a subject.
            if not isinstance(sid, str) or not sid or len(sid) > 255:
                raise ValueError
            if subject is not None and (not isinstance(subject, str) or not subject or len(subject) > 255):
                raise ValueError
            return claims
        except (jwt.PyJWTError, ValueError, TypeError, KeyError, OverflowError, OSError):
            raise DomainError("VALIDATION_FAILED", 400, reason="LOGOUT_TOKEN_INVALID") from None
