"""Native-only API restart persistence, in two phases driven by scripts/run.py test --native.

Phase 1 writes through the running API process: a programme draft under an operation identifier,
an observation draft that is then submitted for review, and a cookie session signed in through
the development login. It records every identifier in <local>/restart-state.json. The runner then
stops that process cleanly and starts a fresh one against the same database and configuration.
Phase 2 asserts on the new process that the exact retries of the phase-1 commands return the
identical receipts, that the objects read back with unchanged revisions, that the cookie session
and its CSRF token are still valid, that readiness and the runtime manifest are unchanged, and
that the database holds exactly the rows phase 1 left. Both phases skip unless the runner names
them, so the ordinary suite collects them as skipped.
"""

import hashlib
import json
import os
from pathlib import Path

import httpx
import pytest
from test_administration import expect
from test_live_application import cmd, draft
from test_native_sessions import sign_in

NATIVE = os.environ.get("IMPACT_NATIVE_TEST") == "1"
NATIVE_REASON = (
    "native PostgreSQL only: the PGlite development database lives inside the test process tree "
    "and does not outlive an API restart the way a server does (run scripts/run.py test --native)"
)
pytestmark = pytest.mark.skipif(not NATIVE, reason=NATIVE_REASON)
PHASE = os.environ.get("IMPACT_RESTART_PHASE")
STATE_FILE = "restart-state.json"


def phase(number):
    """Skip unless the runner names this phase; on PGlite the native reason is the one reported."""
    reason = (
        "runs only as restart phase "
        + str(number)
        + " of scripts/run.py test --native, which restarts the API between the phases"
        if NATIVE
        else NATIVE_REASON
    )
    return pytest.mark.skipif(not NATIVE or PHASE != str(number), reason=reason)


def state_path(live):
    return live.local / STATE_FILE


def browser(live, cookie=None):
    headers = {"Cookie": cookie} if cookie else {}
    return httpx.Client(base_url=str(live.client.base_url), trust_env=False, timeout=20, headers=headers)


def counts(live, state):
    """The database rows the phase-1 writes own: revisions per object and receipts per operation."""
    with live.db() as c:
        revisions = {
            key: c.execute(
                "SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s",
                (live.fixture["tenant_a"], object_id),
            ).fetchone()["n"]
            for key, object_id in [
                ("programme", state["programme"]["receipt"]["object_id"]),
                ("observation", state["observation"]["receipt"]["object_id"]),
                ("workflow", state["submission"]["receipt"]["object_id"]),
            ]
        }
        receipts = {
            key: c.execute(
                "SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s AND operation_id=%s",
                (live.fixture["tenant_a"], state[key]["body"]["operation_id"]),
            ).fetchone()["n"]
            for key in ["programme", "observation", "submission"]
        }
        session = c.execute(
            "SELECT count(*) AS n FROM impact.web_session WHERE session_hash=%s AND identity_id=%s AND revoked_at IS NULL",
            (session_hash(state["session"]["cookie"]), state["session"]["identity_id"]),
        ).fetchone()["n"]
    return {"revisions": revisions, "receipts": receipts, "open_sessions": session}


def session_hash(cookie):
    """The stored hash of a `name=value` session cookie, as auth.digest computes it."""
    return hashlib.sha256(cookie.split("=", 1)[1].encode()).digest()


# Never in the API process environment: the privileged connections and passwords the runner
# holds, and any libpq variable that could supply a credential or redirect a connection.
FORBIDDEN_API_ENVIRONMENT = [
    "IMPACT_FIXTURE_DSN",
    "IMPACT_MIGRATION_DSN",
    "IMPACT_ADMIN_DSN",
    "IMPACT_LOGIN_",
    "PGPASSWORD",
    "PGPASSFILE",
    "PGSERVICE",
    "PGHOST",
    "PGPORT",
    "PGUSER",
    "PGDATABASE",
    "PGOPTIONS",
]


def api_environment(pid):
    """The environment of the running API process, as the kernel reports it."""
    raw = Path("/proc/" + str(pid) + "/environ").read_bytes()
    return [entry.decode(errors="replace") for entry in raw.split(b"\0") if entry]


def assert_api_process_holds_no_privileged_connection(live, pid):
    environment = api_environment(pid)
    leaked = [
        entry.split("=", 1)[0]
        for entry in environment
        if entry.split("=", 1)[0].startswith(("PG", *FORBIDDEN_API_ENVIRONMENT))
    ]
    assert not leaked, leaked
    assert "IMPACT_CONFIG_FILE=" + str(live.local / "config.json") in environment
    # The configuration file names the three provisioned logins and never the fixture connection.
    fixture_dsn = os.environ["IMPACT_FIXTURE_DSN"]
    for name, login in [("app", "APP"), ("identity", "IDENTITY"), ("platform", "PLATFORM")]:
        dsn = live.config[name + "_dsn"]
        assert dsn == os.environ["IMPACT_LOGIN_DSN_" + login], name
        assert dsn != fixture_dsn and "user=impact_" + login.lower() + "_login" in dsn, name


@phase(1)
def test_phase_1(live):
    """Writes on the first API process, recorded for phase 2."""
    assert os.environ.get("IMPACT_API_PID"), "scripts/run.py exports the API process id"
    assert_api_process_holds_no_privileged_connection(live, int(os.environ["IMPACT_API_PID"]))
    programme = cmd({"title": "Survives an API restart", "code": "RESTART"})
    programme_receipt = expect(live.request(live.path("programmes"), method="POST", body=programme), 201)
    observation = cmd(draft(live))
    observation_receipt = expect(
        live.request(live.path("observations"), method="POST", body=observation), 201
    )
    template = expect(live.request(live.path("workflow-templates")), 200)["items"][0]
    submission = cmd({"workflow_version": template["revision_id"]}, observation_receipt["revision_id"])
    submission_receipt = expect(
        live.request(
            live.path("observations", observation_receipt["object_id"]) + "/actions/submit",
            method="POST",
            body=submission,
        ),
        200,
    )
    workflow = expect(live.request(live.path("workflows", submission_receipt["object_id"])), 200)
    assert workflow["lifecycle_state"] == "InReview"
    cookie = sign_in(live, "partner")
    with browser(live, cookie) as client:
        me = expect(client.get("/auth/me"), 200)
    assert me["csrf_token"]
    manifest = expect(live.request("/v1/runtime-manifest"), 200)
    ready = expect(live.request("/health/ready", actor=None), 200)
    state = {
        "api_pid": int(os.environ["IMPACT_API_PID"]),
        "programme": {"body": programme, "receipt": programme_receipt},
        "observation": {"body": observation, "receipt": observation_receipt},
        "submission": {"body": submission, "receipt": submission_receipt, "workflow": workflow},
        "session": {"cookie": cookie, "identity_id": me["identity_id"], "csrf_token": me["csrf_token"]},
        "manifest": manifest,
        "ready": ready,
    }
    state["counts"] = counts(live, state)
    assert state["counts"] == {
        "revisions": {"programme": 1, "observation": 2, "workflow": 1},
        "receipts": {"programme": 1, "observation": 1, "submission": 1},
        "open_sessions": 1,
    }
    state_path(live).write_text(json.dumps(state, indent=2) + "\n")
    state_path(live).chmod(0o600)


@phase(2)
def test_phase_2(live):
    """Assertions on the replacement API process against the same database and configuration."""
    assert state_path(live).exists(), "phase 1 must have run first"
    state = json.loads(state_path(live).read_text())
    assert int(os.environ["IMPACT_API_PID"]) != state["api_pid"], "a fresh API process is required"
    assert_api_process_holds_no_privileged_connection(live, int(os.environ["IMPACT_API_PID"]))
    assert expect(live.request("/health/ready", actor=None), 200) == state["ready"]
    assert expect(live.request("/v1/runtime-manifest"), 200) == state["manifest"]
    # Exact retries replay the receipts recorded by the previous process, byte for byte.
    assert (
        expect(live.request(live.path("programmes"), method="POST", body=state["programme"]["body"]), 201)
        == state["programme"]["receipt"]
    )
    assert (
        expect(live.request(live.path("observations"), method="POST", body=state["observation"]["body"]), 201)
        == state["observation"]["receipt"]
    )
    assert (
        expect(
            live.request(
                live.path("observations", state["observation"]["receipt"]["object_id"]) + "/actions/submit",
                method="POST",
                body=state["submission"]["body"],
            ),
            200,
        )
        == state["submission"]["receipt"]
    )
    # The objects read back with the revisions the previous process wrote.
    programme = expect(live.request(live.path("programmes", state["programme"]["receipt"]["object_id"])), 200)
    assert programme["revision_id"] == state["programme"]["receipt"]["revision_id"]
    assert programme["lifecycle_state"] == "Draft"
    assert programme["data"]["title"] == state["programme"]["body"]["data"]["title"]
    workflow = expect(live.request(live.path("workflows", state["submission"]["receipt"]["object_id"])), 200)
    assert workflow == state["submission"]["workflow"]
    observation = expect(
        live.request(live.path("observations", state["observation"]["receipt"]["object_id"])), 200
    )
    assert observation["revision_id"] == workflow["data"]["candidate_revision"]
    assert observation["lifecycle_state"] == "Submitted"
    assert observation["data"]["source_key"] == state["observation"]["body"]["data"]["source_key"]
    # A stale expected revision is still refused: nothing was rewound or replayed by the restart.
    expect(
        live.request(
            live.path("observations", state["observation"]["receipt"]["object_id"]),
            method="PATCH",
            body=cmd(
                {"value": "1", "value_state": "PRESENT"}, state["observation"]["receipt"]["revision_id"]
            ),
        ),
        409,
    )
    # The cookie session is server-side state and its CSRF token derives from the same secret.
    session = state["session"]
    with browser(live, session["cookie"]) as client:
        me = expect(client.get("/auth/me"), 200)
        assert me["identity_id"] == session["identity_id"]
        assert me["csrf_token"] == session["csrf_token"]
        expect(
            client.post(
                live.path("programmes"),
                headers={"Origin": live.config["public_origin"], "X-CSRF-Token": "not-the-token"},
                json=cmd({"title": "CSRF still enforced"}),
            ),
            403,
        )
        assert counts(live, state) == state["counts"]
        expect(
            client.post(
                "/auth/logout",
                headers={"Origin": live.config["public_origin"], "X-CSRF-Token": session["csrf_token"]},
            ),
            200,
        )
        expect(client.get("/auth/me"), 401)
    assert counts(live, state)["open_sessions"] == 0
