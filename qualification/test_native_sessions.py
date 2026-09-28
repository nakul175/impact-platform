"""Native-only cookie-session concurrency: parallel requests on one browser session are not
serialised by a row lock, and session activity is recorded at most every 30 seconds while the
15-minute idle and 8-hour absolute limits still apply to the row as read."""

import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import httpx
import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="native PostgreSQL only: the PGlite development database serialises every transaction "
    "behind one lock, so parallel requests cannot show contention there (run scripts/run.py test --native)",
)
PARALLEL = 10


def sign_in(live, actor="partner"):
    passwords = json.loads((live.local / "passwords.json").read_text())
    with httpx.Client(base_url=str(live.client.base_url), trust_env=False, timeout=20) as client:
        response = client.post(
            "/auth/development-login",
            headers={"Origin": live.config["public_origin"]},
            json={"username": actor, "password": passwords[actor]},
        )
        assert response.status_code == 200, response.text
        return response.headers["set-cookie"].split(";", 1)[0]


def parallel_get(live, cookie, path="/auth/me"):
    def one(_):
        with httpx.Client(base_url=str(live.client.base_url), trust_env=False, timeout=20) as client:
            response = client.get(path, headers={"Cookie": cookie})
            return response.status_code, response.headers.get("X-Correlation-ID"), response.text

    with ThreadPoolExecutor(max_workers=PARALLEL) as pool:
        return list(pool.map(one, range(PARALLEL)))


def session_row(live, identity_id):
    with live.db() as c:
        return c.execute(
            "SELECT created_at,last_seen_at,expires_at,revoked_at FROM impact.web_session WHERE identity_id=%s ORDER BY created_at DESC LIMIT 1",
            (identity_id,),
        ).fetchone()


def test_parallel_cookie_requests_all_succeed_without_conflict(live):
    identity_id = live.fixture["actors"]["partner"]["identity_id"]
    cookie = sign_in(live)
    before = session_row(live, identity_id)
    results = parallel_get(live, cookie)
    assert [status for status, _, _ in results] == [200] * PARALLEL, results
    assert all("CONFLICT" not in body for _, _, body in results)
    assert len({correlation for _, correlation, _ in results}) == PARALLEL
    after = session_row(live, identity_id)
    # Within 30 s of the last recorded activity nothing is rewritten: the row is only read.
    assert after["last_seen_at"] == before["last_seen_at"]
    assert after["expires_at"] == before["expires_at"] == before["created_at"] + timedelta(hours=8)


def test_activity_is_recorded_after_thirty_seconds_and_idle_limit_holds(live):
    identity_id = live.fixture["actors"]["partner"]["identity_id"]
    cookie = sign_in(live)
    with live.db() as c:
        c.execute(
            "UPDATE impact.web_session SET last_seen_at=now()-interval '40 seconds' WHERE identity_id=%s AND revoked_at IS NULL",
            (identity_id,),
        )
    stale = session_row(live, identity_id)["last_seen_at"]
    assert [status for status, _, _ in parallel_get(live, cookie)] == [200] * PARALLEL
    refreshed = session_row(live, identity_id)["last_seen_at"]
    assert refreshed > stale and refreshed > datetime.now(timezone.utc) - timedelta(seconds=15)
    with live.db() as c:
        c.execute(
            "UPDATE impact.web_session SET last_seen_at=now()-interval '16 minutes' WHERE identity_id=%s AND revoked_at IS NULL",
            (identity_id,),
        )
    # The idle limit is enforced on the row as read; an idle session gains nothing from a request.
    assert [status for status, _, _ in parallel_get(live, cookie)] == [401] * PARALLEL
    assert session_row(live, identity_id)["last_seen_at"] < datetime.now(timezone.utc) - timedelta(minutes=15)


def test_revoked_session_is_refused_in_parallel(live):
    cookie = sign_in(live)
    with httpx.Client(base_url=str(live.client.base_url), trust_env=False, timeout=20) as client:
        csrf = client.get("/auth/me", headers={"Cookie": cookie}).json()["csrf_token"]
        response = client.post(
            "/auth/logout",
            headers={"Cookie": cookie, "Origin": live.config["public_origin"], "X-CSRF-Token": csrf},
        )
        assert response.status_code == 200, response.text
    assert [status for status, _, _ in parallel_get(live, cookie)] == [401] * PARALLEL
