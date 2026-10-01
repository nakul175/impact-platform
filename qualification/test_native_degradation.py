"""Qualified degradation (QA 2026-10, VF-AVL-002): what the platform does when one dependency fails.

Each scenario fails exactly one dependency while the others stay healthy, then restores it:

- the outbox worker is not running: the API keeps serving and intents wait as PENDING, then one
  worker pass delivers each once;
- the database refuses connections (a TCP proxy this test controls sits between an in-process API and
  the suite database): requests answer 503 with the error envelope and reason DATABASE_UNAVAILABLE,
  readiness names the same reason, nothing commits, and the same process recovers when the proxy
  forwards again; natively a connection cut in the middle of a write leaves no partial commit;
- the identity provider is down (a stub key-set and token endpoint this test starts and stops):
  bearer validation serves the cached key set for its lifespan and then fails closed with 503
  IDENTITY_PROVIDER_UNAVAILABLE, cookie sessions keep working, and a sign-in callback creates no
  session;
- the SMTP server refuses connections: the intent is retried with backoff, then DEAD with an error
  class, and no secret or address reaches the log;
- the evidence object store is full or unreadable: uploads answer 503 OBJECT_STORE_FULL or
  OBJECT_STORE_UNAVAILABLE with nothing recorded, and a download of an existing object fails closed
  with the envelope instead of bytes.

The in-process API is impact_api.main.create_app over the suite's own configuration (only the
named fields differ), so it runs the same code as the suite's API process. Every scenario runs on
PGlite and on native PostgreSQL except the mid-write cut, which is native-only (stated below).
"""

import copy
import errno
import json
import logging
import os
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from impact_api import object_store as object_store_module
from impact_api.config import Settings
from impact_api.worker import BACKOFF_BASE_SECONDS, empty_summary
from test_evidence import CSV, declare, download, evidence, put, unique, uploaded
from test_live_application import cmd, draft, expect
from test_worker import Clock, deliveries, invitation, make_worker, sink_lines

NATIVE = os.environ.get("IMPACT_NATIVE_TEST") == "1"
NATIVE_REASON = (
    "native PostgreSQL only: PGlite serves one session over its socket, so an abrupt disconnect in "
    "the middle of a transaction is not a meaningful server rollback test there"
)
ENVELOPE = {"code", "message", "retryable", "correlation_id", "permitted_actions"}


# -- harness ---------------------------------------------------------------------------------------


class Proxy:
    """A TCP proxy on a fixed loopback port in front of the suite database. `refuse()` stops
    listening and drops every forwarded connection (new connections are refused), `restore()`
    listens again on the same port, and `cut_on(pattern)` drops the next connection whose client
    bytes contain `pattern` before forwarding them (a connection lost in the middle of a write)."""

    def __init__(self, upstream):
        self.upstream = upstream
        self.port = None
        self.pairs = []
        self.lock = threading.Lock()
        self.cut = None
        self.cuts = 0
        self.listener = None

    def __enter__(self):
        self.restore()
        return self

    def __exit__(self, *exc):
        self.refuse()

    def restore(self):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", self.port or 0))
        listener.listen(64)
        self.port = listener.getsockname()[1]
        self.listener = listener
        threading.Thread(target=self.accept, args=(listener,), daemon=True).start()

    def refuse(self):
        listener, self.listener = self.listener, None
        if listener:
            listener.close()
        with self.lock:
            pairs, self.pairs = self.pairs, []
        for pair in pairs:
            for s in pair:
                close(s)

    def cut_on(self, pattern):
        self.cut = pattern

    def connect_upstream(self):
        family, address = self.upstream
        s = socket.socket(family, socket.SOCK_STREAM)
        s.connect(address)
        return s

    def accept(self, listener):
        while True:
            try:
                client, _ = listener.accept()
            except OSError:
                return
            try:
                server = self.connect_upstream()
            except OSError:
                close(client)
                continue
            with self.lock:
                self.pairs.append((client, server))
            threading.Thread(target=self.pump, args=(client, server, True), daemon=True).start()
            threading.Thread(target=self.pump, args=(server, client, False), daemon=True).start()

    def pump(self, source, target, outbound):
        try:
            while True:
                data = source.recv(65536)
                if not data:
                    break
                if outbound and self.cut and self.cut in data:
                    self.cut = None
                    self.cuts += 1
                    break
                target.sendall(data)
        except OSError:
            pass
        close(source)
        close(target)


def close(s):
    try:
        s.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    try:
        s.close()
    except OSError:
        pass


def upstream_of(dsn):
    params = conninfo_to_dict(dsn)
    host, port = params.get("host") or "/var/run/postgresql", int(params.get("port") or 5432)
    if host.startswith("/"):
        return socket.AF_UNIX, os.path.join(host, ".s.PGSQL." + str(port))
    return socket.AF_INET, (host if host != "localhost" else "127.0.0.1", port)


def through(dsn, proxy):
    params = conninfo_to_dict(dsn)
    params.update(host="127.0.0.1", port=str(proxy.port))
    return make_conninfo(**params)


def local_api(live, monkeypatch, tmp_path, **overrides):
    """An in-process API over the suite configuration with `overrides`, exposed with the same
    request helpers as the `live` fixture (test helpers from other modules work unchanged)."""
    config = {**live.config, **overrides}
    path = tmp_path / ("config-" + uuid4().hex[:8] + ".json")
    path.write_text(json.dumps(config))
    for name in Settings.__dataclass_fields__:
        monkeypatch.delenv("IMPACT_" + name.upper(), raising=False)
    monkeypatch.setenv("IMPACT_CONFIG_FILE", str(path))
    from impact_api.main import create_app

    app = create_app()
    local = copy.copy(live)
    local.client = TestClient(app, raise_server_exceptions=False)
    local.app = app
    local.config = config
    return local


def envelope(response, status=503, reason=None):
    assert response.status_code == status, response.text
    assert response.headers["content-type"].startswith("application/json")
    body = response.json()
    assert ENVELOPE <= set(body), body
    assert body["retryable"] is (status == 503)
    assert "Traceback" not in response.text and "psycopg" not in response.text
    if reason:
        assert body.get("reason_code") == reason, body
    return body


def receipts(live, operation):
    with live.db() as c:
        return c.execute(
            "SELECT count(*) AS n FROM impact.operation_receipt WHERE operation_id=%s", (operation,)
        ).fetchone()["n"]


def secrets_of(config):
    values = []
    for key in ["app_dsn", "identity_dsn", "platform_dsn"]:
        password = conninfo_to_dict(config.get(key) or "").get("password")
        if password:
            values.append(password)
    return values + [config["cookie_secret"]]


# -- worker down -----------------------------------------------------------------------------------


def test_worker_down_api_serves_intents_wait_and_one_pass_delivers_each_once(live):
    # The suite runs no worker process: this is the worker-down state.
    email, receipt = invitation(live)
    [row] = deliveries(live, receipt["object_id"])
    assert (row["state"], row["attempts"], row["sent_at"]) == ("PENDING", 0, None)
    # Core manual work continues while delivery is down.
    saved = expect(live.request(live.path("observations"), method="POST", body=cmd(draft(live))), 201)
    expect(live.request(live.path("observations", saved["object_id"])), 200)
    time.sleep(1)
    [still] = deliveries(live, receipt["object_id"])
    assert (still["state"], still["attempts"]) == ("PENDING", 0)
    # The worker comes back: one pass delivers the waiting intent, a second pass sends nothing more.
    worker = make_worker(live)
    tenant = live.fixture["tenant_a"]
    worker.dispatch(tenant, empty_summary())
    worker.dispatch(tenant, empty_summary())
    [sent] = deliveries(live, receipt["object_id"])
    assert (sent["state"], sent["attempts"]) == ("SENT", 1) and sent["sent_at"]
    mine = [line for line in sink_lines(worker.s) if line["event_id"] == str(row["event_id"])]
    assert len(mine) == 1 and mine[0]["to"] == email


# -- database unavailable --------------------------------------------------------------------------


def test_database_refused_answers_503_readiness_names_it_and_recovers_without_restart(
    live, monkeypatch, tmp_path, caplog
):
    with Proxy(upstream_of(live.config["app_dsn"])) as proxy:
        dsns = {
            k: through(live.config[k], proxy)
            for k in ["app_dsn", "identity_dsn", "platform_dsn"]
            if live.config.get(k)
        }
        local = local_api(live, monkeypatch, tmp_path, **dsns)
        expect(local.client.get("/health/ready"), 200)
        expect(local.request(local.path("observations")), 200)
        body = cmd(draft(local))  # built while the database is reachable (draft() reads)
        operation = body["operation_id"]

        proxy.refuse()
        caplog.set_level(logging.INFO)
        envelope(local.request(local.path("observations")), reason="DATABASE_UNAVAILABLE")
        envelope(local.client.get("/health/ready"), reason="DATABASE_UNAVAILABLE")
        expect(local.client.get("/health/live"), 200)
        envelope(
            local.request(local.path("observations"), method="POST", body=body), reason="DATABASE_UNAVAILABLE"
        )
        assert receipts(live, operation) == 0
        for secret in secrets_of(local.config):
            assert secret not in caplog.text

        proxy.restore()
        expect(local.client.get("/health/ready"), 200)
        created = expect(local.request(local.path("observations"), method="POST", body=body), 201)
        replay = expect(local.request(local.path("observations"), method="POST", body=body), 201)
        assert replay == created and receipts(live, operation) == 1


@pytest.mark.skipif(not NATIVE, reason=NATIVE_REASON)
def test_native_connection_lost_mid_write_commits_nothing_and_the_retry_commits_once(
    live, monkeypatch, tmp_path
):
    with Proxy(upstream_of(live.config["app_dsn"])) as proxy:
        dsns = {
            k: through(live.config[k], proxy)
            for k in ["app_dsn", "identity_dsn", "platform_dsn"]
            if live.config.get(k)
        }
        local = local_api(live, monkeypatch, tmp_path, **dsns)
        body = cmd(draft(local))
        proxy.cut_on(b"INSERT INTO impact.object_revision")
        envelope(
            local.request(local.path("observations"), method="POST", body=body), reason="DATABASE_UNAVAILABLE"
        )
        assert proxy.cuts == 1
        # The server rolled the transaction back with the connection: no receipt, no observation.
        assert receipts(live, body["operation_id"]) == 0
        with live.db() as c:
            assert (
                c.execute(
                    "SELECT count(*) AS n FROM impact.object_revision WHERE payload->>'source_key'=%s",
                    (body["data"]["source_key"],),
                ).fetchone()["n"]
                == 0
            )
        created = expect(local.request(local.path("observations"), method="POST", body=body), 201)
        assert receipts(live, body["operation_id"]) == 1
        expect(local.request(local.path("observations", created["object_id"])), 200)


# -- identity provider outage ----------------------------------------------------------------------


class Provider:
    """A stub OpenID provider: a JWKS endpoint for one RSA key and a token endpoint, on a loopback
    port that `stop()` closes (connections refused) and `start()` reopens."""

    def __init__(self):
        self.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.kid = "degradation-" + uuid4().hex[:8]
        public = jwt.algorithms.RSAAlgorithm.to_jwk(self.key.public_key(), as_dict=True)
        self.jwks = {"keys": [{**public, "kid": self.kid, "use": "sig", "alg": "RS256"}]}
        self.port = None
        self.server = None
        self.fetches = 0

    def start(self):
        provider = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                provider.fetches += 1
                data = json.dumps(provider.jwks).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", self.port or 0), Handler)
        self.server.allow_reuse_address = True
        self.port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()

    def url(self, path):
        return "http://127.0.0.1:" + str(self.port) + path

    def token(self, config, subject):
        now = int(time.time())
        claims = {
            "iss": config["issuer"],
            "sub": subject,
            "aud": config["audience"],
            "azp": config["client_id"],
            "iat": now,
            "exp": now + 600,
            "auth_time": time.time(),
        }
        pem = self.key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
        )
        return jwt.encode(claims, pem, algorithm="RS256", headers={"kid": self.kid})


def test_identity_provider_outage_fails_closed_and_cookie_sessions_continue(live, monkeypatch, tmp_path):
    provider = Provider()
    provider.start()
    local = local_api(
        live,
        monkeypatch,
        tmp_path,
        dev_auth=False,
        dev_users_file="",
        jwks_url=provider.url("/certs"),
        authorization_url=provider.url("/auth"),
        token_url=provider.url("/token"),
    )
    auth = local.app.state.services[2]
    subject = live.fixture["actors"]["author"]["identity_id"]
    access = local.path("me/access")

    def bearer():
        return local.client.get(
            access, headers={"Authorization": "Bearer " + provider.token(live.config, subject)}
        )

    expect(bearer(), 200)
    cookie = auth.session(auth.identity({"sub": subject, "auth_time": time.time()}))
    session = cookie.headers["set-cookie"].split(";", 1)[0]

    provider.stop()
    try:
        # Within the key-set cache lifespan (60 s) the cached keys still verify a valid token.
        expect(bearer(), 200)
        # Once the cache has expired the key set cannot be refetched: no bearer token is accepted.
        auth.jwks.jwk_set_cache.lifespan = 0
        envelope(bearer(), reason="IDENTITY_PROVIDER_UNAVAILABLE")
        # A token naming an unknown key (which forces a refetch) is refused too, never accepted.
        forged = jwt.encode(
            {"sub": subject}, "x" * 32, algorithm="HS256", headers={"kid": "unknown-" + uuid4().hex[:6]}
        )
        assert local.client.get(access, headers={"Authorization": "Bearer " + forged}).status_code in {
            401,
            503,
        }
        # Cookie sessions do not depend on the provider and keep working until their own limits.
        expect(local.client.get(access, headers={"Cookie": session}), 200)
        # Sign-in: /auth/login only redirects (the provider is never contacted there); the callback
        # cannot exchange the code and creates no session.
        login = local.client.get("/auth/login", follow_redirects=False)
        assert login.status_code == 303
        state = parse_qs(urlparse(login.headers["location"]).query)["state"][0]
        callback = local.client.get(
            "/auth/callback", params={"state": state, "code": "c"}, follow_redirects=False
        )
        envelope(callback, reason="IDENTITY_PROVIDER_UNAVAILABLE")
        assert auth.s.cookie_name not in callback.headers.get("set-cookie", "")
    finally:
        provider.start()
    # The provider is back: a fresh key-set fetch verifies bearer tokens again.
    auth.jwks.jwk_set_cache.lifespan = 60
    expect(bearer(), 200)
    provider.stop()


# -- SMTP refusing ---------------------------------------------------------------------------------


def test_smtp_refusing_connections_backs_off_then_dead_without_secrets_in_logs(live, caplog):
    email, receipt = invitation(live)
    [row] = deliveries(live, receipt["object_id"])
    probe = socket.socket()
    probe.bind(("127.0.0.1", 0))
    closed_port = probe.getsockname()[1]
    probe.close()
    clock = Clock()
    password = "degradation-smtp-" + uuid4().hex
    worker = make_worker(
        live,
        clock=clock,
        max_attempts=3,
        email_adapter="smtp",
        smtp_port=closed_port,
        smtp_timeout=2,
        smtp_password=password,
    )
    tenant = live.fixture["tenant_a"]
    caplog.set_level(logging.DEBUG)
    for attempt in [1, 2, 3]:
        held = next(
            r for r in worker.claim(tenant, empty_summary()) if str(r["event_id"]) == str(row["event_id"])
        )
        started = clock.now()
        worker.process(tenant, held, empty_summary())
        [state] = deliveries(live, receipt["object_id"])
        assert state["attempts"] == attempt and state["last_error_class"] == "SMTP_CONNECTION"
        if attempt < 3:
            assert state["state"] == "PENDING"
            delay = (state["next_attempt_at"] - started).total_seconds()
            base = BACKOFF_BASE_SECONDS * 2 ** (attempt - 1)
            assert base * 0.5 - 1 <= delay <= base + 1
            clock.advance(seconds=base + 1)
    assert state["state"] == "DEAD" and state["completed_at"] and state["sent_at"] is None
    for secret in [
        password,
        email,
        worker.s.delivery_secret,
        worker.s.invitation_secret,
        worker.s.worker_dsn,
    ]:
        assert secret not in caplog.text
    assert "SMTP_CONNECTION" in caplog.text or "ConnectionRefused" in caplog.text or "class=" in caplog.text


# -- object store ----------------------------------------------------------------------------------


def blob_rows(live, content):
    import hashlib

    with live.db() as c:
        return c.execute(
            "SELECT scan_state FROM impact.file_blob WHERE tenant_id=%s AND sha256=%s",
            (live.fixture["tenant_a"], hashlib.sha256(content).digest()),
        ).fetchall()


def test_object_store_full_or_unreadable_fails_cleanly_and_downloads_fail_closed(live, monkeypatch, tmp_path):
    store = tmp_path / "objects"
    store.mkdir(mode=0o700)
    local = local_api(
        live, monkeypatch, tmp_path, object_store_dir=str(store), evidence_scanner="eicar-signature"
    )

    # Full volume: the write fails at fsync; nothing is recorded and no temporary file remains.
    content = unique(CSV)
    status = expect(declare(local, content)[0], 201)
    real = object_store_module.os

    def full(_):
        raise OSError(errno.ENOSPC, "No space left on device")

    monkeypatch.setattr(object_store_module, "os", SimpleNamespace(**{**vars(real), "fsync": full}))
    envelope(put(local, status["upload_id"], content), reason="OBJECT_STORE_FULL")
    monkeypatch.setattr(object_store_module, "os", real)
    assert blob_rows(live, content) == []
    assert [p for p in store.rglob("*") if p.is_file()] == []
    # Space is back: the same upload succeeds without any repair.
    received = expect(put(local, status["upload_id"], content), 200)
    assert received["content_received"] is True

    # Store unavailable (its directory replaced by something that is not a directory).
    other = unique(CSV)
    status = expect(declare(local, other)[0], 201)
    moved = tmp_path / "objects-away"
    store.rename(moved)
    store.write_bytes(b"not a directory")
    envelope(put(local, status["upload_id"], other), reason="OBJECT_STORE_UNAVAILABLE")
    assert blob_rows(live, other) == []
    store.unlink()
    moved.rename(store)

    # An existing CLEAN object that can no longer be read: the download fails closed, no bytes leave
    # and no access is recorded; a missing object is OBJECT_MISSING; neither changes the verdict.
    sealed = unique(CSV)
    done = uploaded(local, sealed)
    assert done["scan_state"] == "CLEAN"
    item = expect(evidence(local, done["upload_id"]), 201)
    assert download(local, item["object_id"]).content == sealed
    [target] = [p for p in store.rglob("*") if p.is_file() and p.name == done["content_sha256"]]
    with live.db() as c:
        before = c.execute(
            "SELECT count(*) AS n FROM impact.evidence_access WHERE evidence_id=%s", (item["object_id"],)
        ).fetchone()["n"]
    target.rename(target.with_name("held"))
    target.mkdir()
    response = download(local, item["object_id"])
    envelope(response, reason="OBJECT_STORE_UNAVAILABLE")
    assert sealed not in response.content
    target.rmdir()
    response = download(local, item["object_id"])
    envelope(response, reason="OBJECT_MISSING")
    with live.db() as c:
        after = c.execute(
            "SELECT count(*) AS n FROM impact.evidence_access WHERE evidence_id=%s", (item["object_id"],)
        ).fetchone()["n"]
    assert after == before
    assert [r["scan_state"] for r in blob_rows(live, sealed)] == ["CLEAN"]
    target.with_name("held").rename(target)
    assert download(local, item["object_id"]).content == sealed
