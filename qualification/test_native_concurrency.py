"""Native-only concurrency qualification of the transactional write path.

Every case releases its requests together through a barrier against the API running on native
PostgreSQL, where uvicorn serves the synchronous endpoints on a thread pool and nothing serialises
transactions in the process (the development database serialises every transaction behind one
lock, so these cases skip there). The expected outcomes are derived from the write path in
service.py, administration.py and authority_renewal.py: the tenant advisory lock taken first by
every command, the operation lock and receipt replay, the expected-revision check under
`FOR UPDATE`, the period-state check inside `apply_close`, and the renewal manifest recheck.
Each case asserts the HTTP outcomes and the database state through the superuser fixture
connection, and every case uses fresh objects so the rest of the suite stays order-independent.
"""

import json
import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import httpx
import pytest
from impact_api.store import hash_data
from test_administration import command, expect, invitation_token, invite, provision_identity, request_as
from test_authority_renewal import action as renewal_action, authority, bootstrapped_tenant, propose, snapshot
from test_live_application import cmd, draft
from test_measurement import create, get, measurement_builder, submit
from test_measurement_unit import definition
from test_period_governance import complete_period, request_close

pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="native PostgreSQL only: the PGlite development database serialises every transaction "
    "behind one process lock, so simultaneous commands cannot contend there (run scripts/run.py test --native)",
)
LOCK_TIMEOUT_SECONDS = 3  # SET LOCAL lock_timeout='3s' in store.Database.transaction
# A read that runs beside a held tenant lock must return well inside the lock timeout; the bound
# is generous for slow runners because the claim is completion while the lock is held, not speed.
READ_SECONDS = 2.5
# Five repetitions of the renewal race: three unbiased, then one per forced order so that both
# outcomes are asserted in every run whatever the unbiased races happened to produce.
RENEWAL_RACE_MODES = ["race", "race", "race", "revocation_first", "approval_first"]
RENEWAL_RACE_HEAD_START_SECONDS = 0.05
RENEWAL_RACE_FILE = "renewal-race-winners.json"


def race(*calls, timeout=60, delays=None):
    """Run the calls on their own threads, released together by a barrier; results in call order.
    `delays` holds one pause in seconds per call, applied after the barrier, to give the others a
    head start when a test needs a particular order rather than an unbiased race."""
    barrier = threading.Barrier(len(calls))

    def run(index, call):
        barrier.wait(timeout=10)
        if delays and delays[index]:
            time.sleep(delays[index])
        return call()

    with ThreadPoolExecutor(max_workers=len(calls)) as pool:
        futures = [pool.submit(run, index, call) for index, call in enumerate(calls)]
        return [future.result(timeout=timeout) for future in futures]


def sender(live, token, method, path, body=None, cookie=None):
    """A request closure with its own connection and a token minted before the race starts."""

    def send():
        headers = {"Authorization": "Bearer " + token} if token else {}
        if cookie:
            headers["Cookie"] = cookie
        with httpx.Client(base_url=str(live.client.base_url), trust_env=False, timeout=30) as client:
            started = time.monotonic()
            response = client.request(method, path, json=body, headers=headers)
            return {
                "status": response.status_code,
                "body": response.json(),
                "seconds": round(time.monotonic() - started, 3),
            }

    return send


def outcomes(results):
    return sorted(r["status"] for r in results)


def count(live, query, *params):
    with live.db() as c:
        return c.execute(query, params).fetchone()["n"]


def revisions(live, tenant, object_id):
    return count(
        live,
        "SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s",
        tenant,
        object_id,
    )


def receipts(live, tenant, operation_id):
    return count(
        live,
        "SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s AND operation_id=%s",
        tenant,
        operation_id,
    )


def audit_events(live, tenant, object_id, action_type):
    return count(
        live,
        "SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s AND object_reference=%s AND action_type=%s",
        tenant,
        object_id,
        action_type,
    )


def outbox_events(live, tenant, revision_id):
    return count(
        live,
        "SELECT count(*) AS n FROM impact.outbox_event e JOIN impact.outbox_delivery d USING(tenant_id,event_id) WHERE e.tenant_id=%s AND e.payload->>'aggregate_revision'=%s",
        tenant,
        revision_id,
    )


def second_reviewer(live):
    """A further REVIEWER member of tenant A who is a distinct natural person from every fixture actor."""
    identity, email = provision_identity(live)
    _, receipt = invite(live, email, role_name="REVIEWER")
    expect(
        request_as(
            live,
            identity,
            live.path("invitation-acceptances"),
            "POST",
            command({"invitation_token": invitation_token(receipt)}),
        ),
        200,
    )
    return identity


def approval(workflow, reason):
    return command(
        {"candidate_revision": workflow["data"]["candidate_revision"], "reason": reason},
        workflow["revision_id"],
    )


def test_simultaneous_independent_approvals_admit_exactly_one(live):
    """Two independent reviewers approve the same candidate revision at once. The tenant advisory
    lock orders them; the second finds the workflow head moved under `load(lock=True)` and fails
    the expected-revision check with CONFLICT_VERSION before any decision is written."""
    tenant = live.fixture["tenant_a"]
    other = second_reviewer(live)
    candidate = create(live, "indicator-definitions", definition(code="RACE"))
    workflow = submit(live, "indicator-definitions", candidate)
    path = live.path("workflows", workflow["object_id"]) + "/actions/approve"
    attempts = [
        (live.token("reviewer"), approval(workflow, "First independent review")),
        (live.signed(other), approval(workflow, "Second independent review")),
    ]
    before = {
        "candidate": revisions(live, tenant, candidate["object_id"]),
        "workflow": revisions(live, tenant, workflow["object_id"]),
    }
    results = race(*[sender(live, token, "POST", path, body) for token, body in attempts])
    assert outcomes(results) == [200, 409], results
    (winner, winner_token, winner_body), (loser, loser_token, loser_body) = sorted(
        [(result, *attempt) for result, attempt in zip(results, attempts)], key=lambda item: item[0]["status"]
    )
    assert winner["body"]["business_state"] == "Approved"
    assert loser["body"]["code"] == "CONFLICT_VERSION" and "reason_code" not in loser["body"]
    approved = get(live, "workflows", workflow["object_id"])
    assert approved["lifecycle_state"] == "Approved"
    assert approved["revision_id"] == winner["body"]["revision_id"]
    assert get(live, "indicator-definitions", candidate["object_id"])["lifecycle_state"] == "Approved"
    assert revisions(live, tenant, candidate["object_id"]) == before["candidate"] + 1
    assert revisions(live, tenant, workflow["object_id"]) == before["workflow"] + 1
    assert (
        count(
            live,
            "SELECT count(*) AS n FROM impact.review_decision WHERE tenant_id=%s AND workflow_id=%s",
            tenant,
            workflow["object_id"],
        )
        == 1
    )
    assert (
        count(
            live,
            "SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s AND object_type='Decision' AND payload->>'candidate_revision'=%s",
            tenant,
            workflow["data"]["candidate_revision"],
        )
        == 1
    )
    assert audit_events(live, tenant, workflow["object_id"], "action_workflows_approve") == 1
    assert outbox_events(live, tenant, approved["revision_id"]) == 1
    assert receipts(live, tenant, winner_body["operation_id"]) == 1
    assert receipts(live, tenant, loser_body["operation_id"]) == 0
    # Once the race is over the outcomes are stable: the winner's exact retry replays its receipt,
    # the loser's exact retry is still refused (it earned no receipt), and a fresh decision against
    # the approved workflow is refused the same way.
    assert sender(live, winner_token, "POST", path, winner_body)()["body"] == winner["body"]
    retried = sender(live, loser_token, "POST", path, loser_body)()
    assert retried["status"] == 409 and retried["body"]["code"] == "CONFLICT_VERSION"
    fresh = sender(live, loser_token, "POST", path, approval(workflow, "Fresh decision after approval"))()
    assert fresh["status"] == 409 and fresh["body"]["code"] == "CONFLICT_VERSION"
    assert revisions(live, tenant, workflow["object_id"]) == before["workflow"] + 1


def test_same_operation_from_two_threads_returns_the_one_receipt(live):
    """The same command (same actor, operation identifier and payload) from two threads at once:
    both callers receive the original receipt and exactly one revision, audit event, outbox event
    and receipt row exist."""
    tenant = live.fixture["tenant_a"]
    body = cmd({"title": "Concurrent exact retry " + str(uuid.uuid4()), "code": "RETRY"})
    path = live.path("programmes")
    token = live.token("author")
    results = race(sender(live, token, "POST", path, body), sender(live, token, "POST", path, body))
    assert outcomes(results) == [201, 201], results
    assert results[0]["body"] == results[1]["body"]
    receipt = results[0]["body"]
    assert receipt["operation_id"] == body["operation_id"] and receipt["business_state"] == "Draft"
    assert revisions(live, tenant, receipt["object_id"]) == 1
    assert receipts(live, tenant, body["operation_id"]) == 1
    assert audit_events(live, tenant, receipt["object_id"], "create_programmes") == 1
    assert outbox_events(live, tenant, receipt["revision_id"]) == 1
    assert get(live, "programmes", receipt["object_id"])["revision_id"] == receipt["revision_id"]


def test_same_operation_with_different_payloads_admits_exactly_one(live):
    """Same operation identifier, different payloads, at once: whichever command commits first owns
    the identifier; the other is refused with CONFLICT_OPERATION and writes nothing."""
    tenant = live.fixture["tenant_a"]
    operation = str(uuid.uuid4())
    titles = ["Operation reuse A " + operation[:8], "Operation reuse B " + operation[:8]]
    bodies = [cmd({"title": title, "code": "REUSE"}, operation=operation) for title in titles]
    path = live.path("programmes")
    token = live.token("author")
    results = race(*[sender(live, token, "POST", path, body) for body in bodies])
    assert outcomes(results) == [201, 409], results
    winner, loser = sorted(zip(results, bodies), key=lambda pair: pair[0]["status"])
    assert loser[0]["body"]["code"] == "CONFLICT_OPERATION"
    saved = get(live, "programmes", winner[0]["body"]["object_id"])
    assert saved["data"]["title"] == winner[1]["data"]["title"]
    assert receipts(live, tenant, operation) == 1
    assert (
        count(
            live,
            "SELECT count(*) AS n FROM impact.programme_current WHERE tenant_id=%s AND title=ANY(%s)",
            tenant,
            titles,
        )
        == 1
    )
    assert revisions(live, tenant, winner[0]["body"]["object_id"]) == 1
    # The identifier stays bound to the winning payload afterwards.
    assert sender(live, token, "POST", path, loser[1])()["status"] == 409
    assert sender(live, token, "POST", path, winner[1])()["body"] == winner[0]["body"]


def test_simultaneous_period_close_reviews_lock_the_period_once(live):
    """Two independent close reviews of one programme period are approved at once. The first
    applies the close and locks the period; the second, serialised behind it, re-runs the preview
    inside apply_close and is refused with INVALID_STATE / PERIOD_ALREADY_SNAPSHOTTED. No second
    snapshot version, official result or close job survives."""
    tenant = live.fixture["tenant_a"]
    programme, _, _, period, _, _ = complete_period(live, measurement_builder(live))
    workflows = [request_close(live, programme, period) for _ in range(2)]
    bodies = [approval(workflow, "Independent close review") for workflow in workflows]
    paths = [live.path("workflows", workflow["object_id"]) + "/actions/approve" for workflow in workflows]
    token = live.token("reviewer")
    results = race(*[sender(live, token, "POST", path, body) for path, body in zip(paths, bodies)])
    assert outcomes(results) == [200, 409], results
    (winner, winner_body, winner_workflow), (loser, loser_body, loser_workflow) = sorted(
        zip(results, bodies, workflows), key=lambda item: item[0]["status"]
    )
    assert winner["body"]["business_state"] == "Approved"
    assert loser["body"]["code"] == "INVALID_STATE"
    assert loser["body"]["reason_code"] == "PERIOD_ALREADY_SNAPSHOTTED"
    with live.db() as c:
        bindings = c.execute(
            "SELECT snapshot_version,snapshot_id,close_id,supersedes_snapshot_id FROM impact.period_snapshot_binding WHERE tenant_id=%s AND programme_id=%s AND period_id=%s ORDER BY snapshot_version",
            (tenant, programme["object_id"], period["object_id"]),
        ).fetchall()
        assert [b["snapshot_version"] for b in bindings] == [1]
        assert str(bindings[0]["close_id"]) == winner_workflow["data"]["candidate_id"]
        assert bindings[0]["supersedes_snapshot_id"] is None
        state = c.execute(
            "SELECT lifecycle_state,current_snapshot_version FROM impact.programme_period_state WHERE tenant_id=%s AND programme_id=%s AND period_id=%s",
            (tenant, programme["object_id"], period["object_id"]),
        ).fetchone()
        assert state["lifecycle_state"] == "Locked" and state["current_snapshot_version"] == 1
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.official_result_snapshot WHERE tenant_id=%s AND snapshot_id=%s",
                (tenant, bindings[0]["snapshot_id"]),
            ).fetchone()["n"]
            == 1
        )
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.snapshot_current WHERE tenant_id=%s AND programme_id=%s AND period_id=%s",
                (tenant, programme["object_id"], period["object_id"]),
            ).fetchone()["n"]
            == 1
        )
        jobs = c.execute(
            "SELECT job_id,state FROM impact.job WHERE tenant_id=%s AND job_class='PERIOD_CLOSE' AND input_manifest->>'programme_id'=%s",
            (tenant, programme["object_id"]),
        ).fetchall()
        assert [(str(j["job_id"]), j["state"]) for j in jobs] == [
            (winner_workflow["data"]["candidate_id"], "Succeeded")
        ]
    assert get(live, "workflows", winner_workflow["object_id"])["lifecycle_state"] == "Approved"
    refused = get(live, "workflows", loser_workflow["object_id"])
    assert (
        refused["lifecycle_state"] == "InReview" and refused["revision_id"] == loser_workflow["revision_id"]
    )
    assert revisions(live, tenant, loser_workflow["data"]["candidate_id"]) == 1
    assert receipts(live, tenant, winner_body["operation_id"]) == 1
    assert receipts(live, tenant, loser_body["operation_id"]) == 0
    # Once locked, the refused review stays refused for the same reason.
    again = sender(live, token, "POST", paths[bodies.index(loser_body)], loser_body)()
    assert again["status"] == 409 and again["body"]["reason_code"] == "PERIOD_ALREADY_SNAPSHOTTED"


def grant_head(live, tenant_id, grant_id):
    with live.db() as c:
        return str(
            c.execute(
                "SELECT head_revision FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s",
                (tenant_id, grant_id),
            ).fetchone()["head_revision"]
        )


def renewal_row(live, request_id):
    with live.db() as c:
        return c.execute(
            "SELECT state,approved_by,applied_at,manifest,authority_hash FROM impact.tenant_authority_renewal WHERE request_id=%s",
            (request_id,),
        ).fetchone()


def record_winner(live, repetition, mode, winner):
    """Append this repetition's mode and observed winner to <local>/renewal-race-winners.json,
    which scripts/run.py copies into the native evidence."""
    path = live.local / RENEWAL_RACE_FILE
    recorded = json.loads(path.read_text()) if path.exists() else {}
    recorded[str(repetition)] = {"mode": mode, "winner": winner}
    path.write_text(json.dumps(recorded, indent=2) + "\n")


@pytest.mark.parametrize("repetition,mode", list(enumerate(RENEWAL_RACE_MODES)))
def test_renewal_approval_raced_with_pinned_grant_revocation(live, repetition, mode):
    """An operator approves an accepted renewal while the owner revokes one of the pinned grants
    of the second administrator. Both commands take the tenant advisory lock, so exactly one
    order applies: approval first re-dates every pinned ceiling and grant, after which the
    revocation carries a stale expected revision (CONFLICT_VERSION) and succeeds only against the
    renewed revision; revocation first removes the grant from the recomputed manifest, so the
    approval fails with AUTHORITY_CHANGED and no ceiling moves. Three repetitions race without
    bias; the last two give one side a 50 ms head start so that both orders are asserted in every
    run. The mode and observed winner of each repetition are recorded in
    <local>/renewal-race-winners.json."""
    tenant, _ = bootstrapped_tenant(live)
    tenant_id = tenant["tenant_id"]
    row, _, _, _ = propose(live, tenant)
    row = renewal_action(live, row, "accept")
    pinned = row["manifest"]["principals"][1]
    grant_id = pinned["grant_ids"][0]
    head = grant_head(live, tenant_id, grant_id)
    before = snapshot(live, tenant_id)
    approve_body = command({"reason": "Independent operator review"}, row["revision_id"])
    revoke_body = command({"reason": "Revoke one administrative grant"}, head)
    approve_path = "/v1/platform/authority-renewals/" + row["request_id"] + "/actions/approve"
    revoke_path = live.path("grants", grant_id, tenant=tenant_id) + "/actions/revoke"
    owner = live.fixture["actors"]["author"]["identity_id"]
    head_start = {
        "race": None,
        "revocation_first": (RENEWAL_RACE_HEAD_START_SECONDS, 0),
        "approval_first": (0, RENEWAL_RACE_HEAD_START_SECONDS),
    }[mode]
    approved, revoked = race(
        sender(live, live.token("admin"), "POST", approve_path, approve_body),
        sender(live, live.signed(owner), "POST", revoke_path, revoke_body),
        delays=head_start,
    )
    after = snapshot(live, tenant_id)
    stored = renewal_row(live, row["request_id"])
    assert hash_data(stored["manifest"]).hex() == stored["authority_hash"] == row["authority_hash"]
    # The pinned instant is a hashed field of the manifest; both outcomes keep it byte-identical.
    assert stored["manifest"] == row["manifest"]
    assert set(after["grants"]) == set(before["grants"]) and set(after["authority"]) == set(
        before["authority"]
    )
    if approved["status"] == 200:
        winner = "approval"
        assert approved["body"]["state"] == "Applied" and stored["state"] == "Applied"
        assert revoked["status"] == 409 and revoked["body"]["code"] == "CONFLICT_VERSION"
        assert "reason_code" not in revoked["body"]
        renewed = datetime.fromisoformat(approved["body"]["expires_at"])
        assert all(value == renewed for value in after["authority"].values())
        assert all(value == renewed for value in after["assignments"].values())
        for object_id, (expires_at, state, revision_number) in after["grants"].items():
            assert state == "Active" and expires_at == renewed
            assert revision_number == before["grants"][object_id][2] + 1
        assert receipts(live, tenant_id, revoke_body["operation_id"]) == 0
        # The later revocation applies to the renewed revision, not to the one it raced against.
        head = grant_head(live, tenant_id, grant_id)
        assert head != revoke_body["expected_revision"]
        applied = sender(
            live, live.signed(owner), "POST", revoke_path, command({"reason": "Revoke after renewal"}, head)
        )()
        assert applied["status"] == 200 and applied["body"]["business_state"] == "Revoked"
        final = snapshot(live, tenant_id)
        assert final["grants"][grant_id][1] == "Revoked"
        assert final["grants"][grant_id][0] == renewed
        assert final["grants"][grant_id][2] == before["grants"][grant_id][2] + 2
        assert {k: v for k, v in final["grants"].items() if k != grant_id} == {
            k: v for k, v in after["grants"].items() if k != grant_id
        }
        assert final["authority"] == after["authority"]
    else:
        winner = "revocation"
        assert revoked["status"] == 200 and revoked["body"]["business_state"] == "Revoked"
        assert approved["status"] == 409 and approved["body"]["reason_code"] == "AUTHORITY_CHANGED"
        assert stored["state"] == "Accepted" and not stored["approved_by"] and not stored["applied_at"]
        assert after["grants"][grant_id][1] == "Revoked"
        assert after["grants"][grant_id][0] == before["grants"][grant_id][0]
        assert after["grants"][grant_id][2] == before["grants"][grant_id][2] + 1
        assert {k: v for k, v in after["grants"].items() if k != grant_id} == {
            k: v for k, v in before["grants"].items() if k != grant_id
        }
        for key in ["authority", "assignments", "memberships", "marker"]:
            assert after[key] == before[key], key
        assert after["policy_epoch"] == before["policy_epoch"] + 1
        assert after["epochs"][pinned["principal_id"]] == before["epochs"][pinned["principal_id"]] + 1
        with live.db() as c:
            assert not c.execute(
                "SELECT 1 FROM impact.platform_receipt WHERE operation_id=%s", (approve_body["operation_id"],)
            ).fetchone()
        # The exact retry of the approval is refused the same way: nothing revoked is resurrected.
        again = sender(live, live.token("admin"), "POST", approve_path, approve_body)()
        assert again["status"] == 409 and again["body"]["reason_code"] == "AUTHORITY_CHANGED"
        assert snapshot(live, tenant_id) == after
    # The recomputed authority differs from the pinned manifest in either order: the ceilings
    # moved, or a pinned grant is gone.
    assert authority(live, tenant, "admin")["authority_hash"] != row["authority_hash"]
    if mode != "race":
        assert winner == mode.split("_")[0], (mode, winner)
    record_winner(live, repetition, mode, winner)


def test_reads_are_not_blocked_by_a_write_holding_the_tenant_advisory_lock(live):
    """While a transaction holds the tenant advisory lock every command takes first, a write queues
    behind it and ten parallel reads all complete before the lock is released, each inside a
    generous bound; a write that waits longer than lock_timeout is refused with CONFLICT_VERSION
    (sqlstate 55P03) and leaves no receipt."""
    tenant = live.fixture["tenant_a"]
    token = live.token("author")
    read_paths = [
        live.path("programmes") + "?limit=5",
        live.path("programmes", live.fixture["programme_a"]),
        live.path("me/access"),
        live.path("indicator-instances", live.records["indicator_a"]["object_id"]),
        live.path("observations") + "?limit=5",
    ] * 2
    queued = cmd({"title": "Queued behind the tenant lock " + str(uuid.uuid4())})
    with ThreadPoolExecutor(max_workers=12) as pool:
        with live.db() as holder:
            holder.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            submitted = time.monotonic()
            write = pool.submit(sender(live, token, "POST", live.path("programmes"), queued))
            time.sleep(0.5)
            assert not write.done(), "the write must wait for the tenant advisory lock"
            reads = list(pool.map(lambda call: call(), [sender(live, token, "GET", p) for p in read_paths]))
            # The claim: every read has returned while the lock is still held, which the write,
            # still queued at this instant (it can only finish once the lock is released or its
            # lock_timeout expires), proves; the holder releases only after this assertion.
            assert not write.done(), "the write must still be queued when the reads have completed"
            holder.rollback()
            held = time.monotonic() - submitted
        assert [r["status"] for r in reads] == [200] * len(read_paths), reads
        assert max(r["seconds"] for r in reads) < READ_SECONDS, reads
        result = write.result(timeout=10)
        assert result["status"] == 201, result
        # The write completed only after the lock was released: it waited at least as long as
        # the lock was held after it was sent.
        assert result["seconds"] >= held - 0.05, (result["seconds"], held)
        assert receipts(live, tenant, queued["operation_id"]) == 1
        # Negative control: held beyond lock_timeout, the queued write is refused and writes nothing.
        refused_body = cmd({"title": "Refused behind the tenant lock " + str(uuid.uuid4())})
        with live.db() as holder:
            holder.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            refused = pool.submit(sender(live, token, "POST", live.path("programmes"), refused_body))
            reads = list(pool.map(lambda call: call(), [sender(live, token, "GET", p) for p in read_paths]))
            assert [r["status"] for r in reads] == [200] * len(read_paths)
            result = refused.result(timeout=LOCK_TIMEOUT_SECONDS + 10)
            holder.rollback()
        assert result["status"] == 409 and result["body"]["code"] == "CONFLICT_VERSION", result
        assert result["body"]["retryable"] is False
        assert result["seconds"] >= LOCK_TIMEOUT_SECONDS
        assert receipts(live, tenant, refused_body["operation_id"]) == 0
        assert (
            count(
                live,
                "SELECT count(*) AS n FROM impact.programme_current WHERE tenant_id=%s AND title=%s",
                tenant,
                refused_body["data"]["title"],
            )
            == 0
        )


def deadlocks(live):
    with live.db() as c:
        return c.execute(
            "SELECT deadlocks AS n FROM pg_stat_database WHERE datname=current_database()"
        ).fetchone()["n"]


class Worker:
    """One thread's own connection; tokens come from the shared per-actor cache minted up front."""

    def __init__(self, live, number):
        self.live, self.number, self.statuses = live, number, []
        self.client = httpx.Client(base_url=str(live.client.base_url), trust_env=False, timeout=30)

    def request(self, path, actor="author", method="GET", body=None, status=200):
        response = self.client.request(
            method, path, json=body, headers={"Authorization": "Bearer " + self.live.token(actor)}
        )
        self.statuses.append((response.status_code, response.json().get("code")))
        assert response.status_code == status, response.text
        return response.json()

    def tenant_a(self, rounds, observation):
        """Programme drafts, a submitted and independently approved definition review, and
        observation drafts on tenant A as the fixture author and reviewer: twelve requests a round."""
        path = self.live.path
        for round_number in range(rounds):
            label = "Deadlock worker " + str(self.number) + " round " + str(round_number)
            programme = self.request(
                path("programmes"), method="POST", body=cmd({"title": label}), status=201
            )
            self.request(
                path("programmes", programme["object_id"]),
                method="PATCH",
                body=cmd({"title": label + " revised"}, programme["revision_id"]),
            )
            saved = self.request(
                path("indicator-definitions"),
                method="POST",
                body=cmd(definition(code="DL" + str(self.number))),
                status=201,
            )
            self.request(
                path("indicator-definitions", saved["object_id"]),
                method="PATCH",
                body=cmd({"name": label}, saved["revision_id"]),
            )
            current = self.request(path("indicator-definitions", saved["object_id"]))
            template = self.request(path("workflow-templates"))["items"][0]
            submitted = self.request(
                path("indicator-definitions", saved["object_id"]) + "/actions/submit",
                method="POST",
                body=cmd({"workflow_version": template["revision_id"]}, current["revision_id"]),
            )
            workflow = self.request(path("workflows", submitted["object_id"]))
            self.request(
                path("workflows", workflow["object_id"]) + "/actions/approve",
                actor="reviewer",
                method="POST",
                body=approval(workflow, label),
            )
            row = self.request(
                path("observations"),
                method="POST",
                body=cmd({**observation, "source_key": str(uuid.uuid4())}),
                status=201,
            )
            self.request(
                path("observations", row["object_id"]),
                method="PATCH",
                body=cmd(
                    {"value_state": "PRESENT", "value": "70", "numerator": "7", "denominator": "10"},
                    row["revision_id"],
                ),
            )
            self.request(path("programmes") + "?limit=3")
        return self.statuses

    def tenant_b(self, rounds):
        """Definition drafts on tenant B as its author, the only writes that tenant's fixture
        permits, plus reads: five requests a round."""
        live, tenant = self.live, self.live.fixture["tenant_b"]
        path = live.path
        for round_number in range(rounds):
            label = "Deadlock worker " + str(self.number) + " round " + str(round_number)
            saved = self.request(
                path("indicator-definitions", tenant=tenant),
                actor="other_tenant",
                method="POST",
                body=cmd(definition(code="DL" + str(self.number))),
                status=201,
            )
            revision = saved["revision_id"]
            for suffix in [" revised", " revised again"]:
                revision = self.request(
                    path("indicator-definitions", saved["object_id"], tenant=tenant),
                    actor="other_tenant",
                    method="PATCH",
                    body=cmd({"name": label + suffix}, revision),
                )["revision_id"]
            self.request(path("indicator-definitions", tenant=tenant) + "?limit=3", actor="other_tenant")
            self.request(path("programmes", live.fixture["programme_b"], tenant=tenant), actor="other_tenant")
        return self.statuses


def test_mixed_writes_on_both_tenants_complete_without_deadlock(live):
    """No-regression smoke test, not lock-order evidence. Eight threads, four per fixture tenant,
    each running rounds of creates, patches, a submitted and independently approved definition
    review and reads at once: every response is the expected 2xx, PostgreSQL records no deadlock
    for the database, and the API log gains no deadlock (40P01), database-failure or
    unexpected-failure line. By construction the case cannot deadlock: every write serialises on
    its tenant's advisory lock before touching a row, and the two tenants share no rows, so a
    deadlock here could only come from a regression that takes a row or a second advisory lock
    before the tenant lock. The lock order across objects within one tenant is not exercised by
    concurrent writers, because there are none once the tenant lock is held."""
    workers, rounds = 8, 3
    for actor in ["author", "reviewer", "other_tenant"]:
        live.token(actor)
    observation = draft(live)
    log = live.local / "api.log"
    log_offset = log.stat().st_size if log.exists() else 0
    deadlocks_before = deadlocks(live)
    started = time.monotonic()
    threads = [Worker(live, number) for number in range(workers)]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(worker.tenant_a, rounds, observation)
            if worker.number % 2 == 0
            else pool.submit(worker.tenant_b, rounds)
            for worker in threads
        ]
        results = [future.result(timeout=300) for future in futures]
    for worker in threads:
        worker.client.close()
    elapsed = time.monotonic() - started
    statuses = [status for worker_statuses in results for status in worker_statuses]
    assert len(statuses) == 4 * rounds * 12 + 4 * rounds * 5
    assert all(status in {200, 201} for status, _ in statuses), sorted(set(statuses))
    assert deadlocks(live) == deadlocks_before
    with log.open("rb") as handle:
        handle.seek(log_offset)
        appended = handle.read().decode(errors="replace")
    assert "40P01" not in appended and "database failure" not in appended, appended
    assert "unexpected failure" not in appended, appended
    assert elapsed < 240, elapsed
