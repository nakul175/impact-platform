"""Qualification of the retention sweep (v0.25 part B): job class RETENTION_SWEEP, queued by the
worker's scan through a definer, leased with a generation fence on database time, and executed in
one transaction that deletes or redacts only expired items per data class and writes an insert-only
proof record (count, cutoff, SHA-256 of the affected keys). The worker runs in-process, as in
test_worker.py; natively it uses the provisioned worker login."""
# ruff: noqa: F811

import hashlib
import uuid

import psycopg
import pytest
from psycopg.rows import dict_row

from impact_api.contracts import validate
from impact_api.retention import CLASSES, SCHEDULE, digest
from impact_api.worker import ConfigurationError, empty_summary
from test_live_application import cmd, draft, expect
from test_privacy_requests import approve, create_case, execute, export, member
from test_worker import Clock, make_worker, settings, worker_dsn

TENANT_KEY = "tenant_a"


def tenant(live):
    return live.fixture[TENANT_KEY]


def make_due(live):
    """Let the next scan queue a sweep for tenant A: earlier sweeps of this suite completed long ago,
    and any sweep another test left open is cancelled."""
    with live.db() as c:
        c.execute(
            "UPDATE impact.retention_sweep SET completed_at=now()-interval '2 days' WHERE tenant_id=%s "
            "AND completed_at IS NOT NULL",
            (tenant(live),),
        )
        c.execute(
            "UPDATE impact.job SET state='Cancelled',lease_expires_at=NULL WHERE tenant_id=%s "
            "AND job_class='RETENTION_SWEEP' AND state IN ('Queued','Running')",
            (tenant(live),),
        )


def proofs(live, job_id):
    with live.db() as c:
        return {
            r["data_class"]: r
            for r in c.execute("SELECT * FROM impact.retention_proof WHERE job_id=%s", (job_id,)).fetchall()
        }


def sweep_jobs(live):
    with live.db() as c:
        return c.execute(
            "SELECT j.*,s.attempts,s.lease_owner,s.completed_at FROM impact.job j JOIN impact.retention_sweep s "
            "USING(tenant_id,job_id) WHERE j.tenant_id=%s ORDER BY s.next_attempt_at",
            (tenant(live),),
        ).fetchall()


def expected_items(live):
    """The keys each class would affect now, computed independently with the superuser connection."""
    t = tenant(live)
    with live.db() as c:
        receipts = [
            r["k"]
            for r in c.execute(
                "SELECT actor_id::text||':'||command_type||':'||operation_id::text AS k FROM impact.operation_receipt "
                "WHERE tenant_id=%s AND expires_at<=now()",
                (t,),
            ).fetchall()
        ]
        uploads = [
            r["k"]
            for r in c.execute(
                "SELECT upload_id::text AS k FROM impact.upload_session WHERE tenant_id=%s AND state='OPEN' "
                "AND expires_at<=now()",
                (t,),
            ).fetchall()
        ]
        packages = [
            r["k"]
            for r in c.execute(
                "SELECT package_id::text||':'||encode(content_sha256,'hex') AS k FROM impact.privacy_export_package "
                "WHERE tenant_id=%s AND expires_at<=now()",
                (t,),
            ).fetchall()
        ]
        recipients = [
            r["k"]
            for r in c.execute(
                "SELECT event_id::text AS k FROM impact.outbox_delivery WHERE tenant_id=%s AND channel='EMAIL' "
                "AND recipient_redacted_at IS NULL AND state IN ('SENT','DEAD','SUPERSEDED') "
                "AND completed_at<=now()-interval '30 days'",
                (t,),
            ).fetchall()
        ]
    return {
        "OPERATION_RECEIPT": receipts,
        "UPLOAD_SESSION": uploads,
        "PRIVACY_EXPORT_PACKAGE": packages,
        "OUTBOX_RECIPIENT": recipients,
    }


def receipt_of(live, operation_id):
    with live.db() as c:
        return c.execute(
            "SELECT * FROM impact.operation_receipt WHERE operation_id=%s", (operation_id,)
        ).fetchone()


def open_upload(live):
    content = b"household,visited\nH9,no\n" + uuid.uuid4().hex.encode()
    response = live.request(
        live.path("uploads"),
        method="POST",
        body=cmd(
            {
                "purpose": "EVIDENCE_MEDIA",
                "content_type": "text/csv",
                "expected_bytes": len(content),
                "content_sha256": hashlib.sha256(content).hexdigest(),
                "mode": "WHOLE",
                "filename": "unfinished.csv",
            }
        ),
    )
    return expect(response, 201)["upload_id"]


def email_delivery(live, completed_days_ago):
    """An invitation e-mail intent marked SENT the given number of days ago."""
    from test_administration import invite

    _, receipt = invite(live, "retention-" + uuid.uuid4().hex[:10] + "@example.test")
    with live.db() as c:
        row = c.execute(
            "UPDATE impact.outbox_delivery SET state='SENT',sent_at=now()-make_interval(days=>%s),"
            "completed_at=now()-make_interval(days=>%s) WHERE reference_id=%s AND channel='EMAIL' "
            "RETURNING event_id,recipient_sealed",
            (completed_days_ago, completed_days_ago, receipt["object_id"]),
        ).fetchone()
    return str(row["event_id"]), bytes(row["recipient_sealed"])


def test_sweep_removes_only_expired_items_and_proves_each_class(live):
    # Expired and current items of every class.
    old = expect(live.request(live.path("observations"), method="POST", body=cmd(draft(live))), 201)
    new = expect(live.request(live.path("observations"), method="POST", body=cmd(draft(live))), 201)
    with live.db() as c:
        c.execute(
            "UPDATE impact.operation_receipt SET expires_at=now()-interval '1 second' WHERE operation_id=%s",
            (old["operation_id"],),
        )
    stale_upload, live_upload = open_upload(live), open_upload(live)
    with live.db() as c:
        c.execute(
            "UPDATE impact.upload_session SET expires_at=now()-interval '1 second' WHERE upload_id=%s",
            (stale_upload,),
        )
    subject = member(live)
    created = create_case(live, subject)
    approve(live, created["object_id"])
    execute(live, created["object_id"])
    with live.db() as c:
        c.execute(
            "UPDATE impact.privacy_export_package SET created_at=now()-interval '8 days',"
            "expires_at=now()-interval '1 day' WHERE case_id=%s",
            (created["object_id"],),
        )
    old_mail, old_sealed = email_delivery(live, 31)
    new_mail, new_sealed = email_delivery(live, 1)

    make_due(live)
    expected = expected_items(live)
    assert old["operation_id"] in {k.split(":")[2] for k in expected["OPERATION_RECEIPT"]}
    assert stale_upload in expected["UPLOAD_SESSION"] and old_mail in expected["OUTBOX_RECIPIENT"]
    assert len(expected["PRIVACY_EXPORT_PACKAGE"]) >= 1
    worker = make_worker(live)
    summary = empty_summary()
    worker.run_retention(tenant(live), summary)
    assert (summary["retention_scheduled"], summary["retention_claimed"], summary["retention_swept"]) == (
        1,
        1,
        1,
    )
    job = sweep_jobs(live)[-1]
    assert job["state"] == "Succeeded" and job["lease_generation"] == 1 and job["completed_at"]
    proof = proofs(live, job["job_id"])
    assert set(proof) == set(CLASSES)
    for data_class, items in expected.items():
        row = proof[data_class]
        assert row["affected_count"] == len(items), data_class
        assert bytes(row["items_sha256"]) == digest(items), data_class
        assert row["action"] == CLASSES[data_class]["action"]
        assert row["retention_days"] == CLASSES[data_class]["retention_days"]
        assert row["lease_generation"] == 1 and row["worker_id"] == worker.worker_id

    # Expired items are gone or redacted; current ones are untouched.
    assert receipt_of(live, old["operation_id"]) is None
    assert receipt_of(live, new["operation_id"]) is not None
    with live.db() as c:
        states = {
            str(r["upload_id"]): r["state"]
            for r in c.execute(
                "SELECT upload_id,state FROM impact.upload_session WHERE upload_id=ANY(%s::uuid[])",
                ([stale_upload, live_upload],),
            ).fetchall()
        }
        mail = {
            str(r["event_id"]): r
            for r in c.execute(
                "SELECT event_id,recipient_sealed,recipient_redacted_at,state FROM impact.outbox_delivery "
                "WHERE event_id=ANY(%s::uuid[])",
                ([old_mail, new_mail],),
            ).fetchall()
        }
        packages = c.execute(
            "SELECT count(*) AS n FROM impact.privacy_export_package WHERE case_id=%s",
            (created["object_id"],),
        ).fetchone()["n"]
        access_log = c.execute(
            "SELECT count(*) AS n FROM impact.job_item WHERE job_id=%s AND item_key='sweep' AND outcome='SUCCEEDED'",
            (job["job_id"],),
        ).fetchone()["n"]
    assert states == {stale_upload: "EXPIRED", live_upload: "OPEN"}
    assert mail[old_mail]["recipient_redacted_at"] and bytes(mail[old_mail]["recipient_sealed"]) != old_sealed
    assert (
        mail[new_mail]["recipient_redacted_at"] is None
        and bytes(mail[new_mail]["recipient_sealed"]) == new_sealed
    )
    assert mail[old_mail]["state"] == "SENT"
    assert packages == 0 and access_log == 1
    # The expired package is no longer downloadable; the case itself stays.
    gone = export(live, created["object_id"])
    assert gone.status_code == 404 and gone.json()["reason_code"] == "EXPORT_EXPIRED"

    # Idempotent: a second pass inside the interval queues nothing; a forced later sweep finds nothing.
    again = empty_summary()
    worker.run_retention(tenant(live), again)
    assert (again["retention_scheduled"], again["retention_swept"]) == (0, 0)
    make_due(live)
    later = empty_summary()
    make_worker(live).run_retention(tenant(live), later)
    assert later["retention_swept"] == 1
    repeat = proofs(live, sweep_jobs(live)[-1]["job_id"])
    for data_class in ["UPLOAD_SESSION", "PRIVACY_EXPORT_PACKAGE", "OUTBOX_RECIPIENT"]:
        assert repeat[data_class]["affected_count"] == 0
        assert bytes(repeat[data_class]["items_sha256"]) == digest([])
    assert receipt_of(live, new["operation_id"]) is not None

    # The proofs, newest first, through the API; the schedule is the catalogue.
    listed = expect(live.request(live.path("retention-proofs"), actor="privacy"), 200)
    validate("RetentionProofList", listed)
    assert {p["job_id"] for p in listed["items"][:4]} == {str(sweep_jobs(live)[-1]["job_id"])}
    schedule = expect(live.request(live.path("retention-schedule"), actor="admin"), 200)
    validate("RetentionSchedule", schedule)
    # v0.27: the read is the effective schedule; every class still on its default equals the catalogue.
    expected = {c["data_class"]: c for c in SCHEDULE}
    assert {i["data_class"] for i in schedule["items"]} == set(expected)
    for item in schedule["items"]:
        if item["source"] == "DEFAULT":
            assert {k: v for k, v in item.items() if k not in {"source", "policy_id"}} == expected[
                item["data_class"]
            ]
    expect(live.request(live.path("retention-proofs"), actor="author"), 403)
    expect(live.request(live.path("retention-proofs"), actor="other_tenant"), 404)


def test_a_stale_lease_holder_neither_deletes_nor_proves(live):
    make_due(live)
    first_clock, second_clock = Clock(), Clock()
    first, second = make_worker(live, clock=first_clock), make_worker(live, clock=second_clock)
    rows = first.claim_retention(tenant(live), empty_summary())
    assert len(rows) == 1 and rows[0]["lease_generation"] == 1
    # The first holder stalls past its lease; the second takes the sweep over (generation 2).
    second_clock.advance(seconds=first.s.lease_seconds + 5)
    taken = second.claim_retention(tenant(live), empty_summary(), schedule=False)
    assert [str(r["job_id"]) for r in taken] == [str(rows[0]["job_id"])] and taken[0]["lease_generation"] == 2
    old = expect(live.request(live.path("observations"), method="POST", body=cmd(draft(live))), 201)
    with live.db() as c:
        c.execute(
            "UPDATE impact.operation_receipt SET expires_at=now()-interval '1 second' WHERE operation_id=%s",
            (old["operation_id"],),
        )
    stale = empty_summary()
    assert first.process_retention(tenant(live), rows[0], stale) is False
    assert stale["stale_refused"] == 1 and stale["retention_swept"] == 0
    assert proofs(live, rows[0]["job_id"]) == {}
    assert receipt_of(live, old["operation_id"]) is not None
    fresh = empty_summary()
    assert second.process_retention(tenant(live), taken[0], fresh) is True
    proof = proofs(live, rows[0]["job_id"])
    assert set(proof) == set(CLASSES) and {p["lease_generation"] for p in proof.values()} == {2}
    assert {p["worker_id"] for p in proof.values()} == {second.worker_id}
    assert receipt_of(live, old["operation_id"]) is None
    # The finished job is not processed twice.
    assert second.process_retention(tenant(live), taken[0], empty_summary()) is False


def test_a_sweep_that_keeps_failing_backs_off_then_fails_with_an_error_class(live, monkeypatch):
    import impact_api.retention as retention

    make_due(live)
    worker = make_worker(live, max_attempts=2)
    clock = worker.skew

    def broken(c, tenant):
        c.execute("SELECT 1/0")

    monkeypatch.setattr(retention, "apply", broken)
    first = empty_summary()
    worker.run_retention(tenant(live), first)
    job = sweep_jobs(live)[-1]
    assert (job["state"], job["attempts"], first["retention_swept"]) == ("Queued", 1, 0)
    with live.db() as c:
        sweep = c.execute("SELECT * FROM impact.retention_sweep WHERE job_id=%s", (job["job_id"],)).fetchone()
    assert sweep["last_error_class"] == "SWEEP_FAILED" and sweep["lease_owner"] is None
    clock.advance(hours=2)
    second = empty_summary()
    worker.run_retention(tenant(live), second)
    job = sweep_jobs(live)[-1]
    assert job["state"] == "Failed" and job["output_manifest"]["error_class"] == "SWEEP_FAILED"
    assert second["retention_failed"] == 1 and proofs(live, job["job_id"]) == {}


def test_worker_holds_exactly_the_retention_privileges(live):
    every = ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"]
    expected = {
        "retention_sweep": {"SELECT", "UPDATE"},
        "retention_proof": {"SELECT", "INSERT"},
        "privacy_export_package": {"SELECT", "DELETE"},
        "privacy_export_access": set(),
        "operation_receipt": set(),
        "upload_session": set(),
        "privacy_case_current": set(),
        "privacy_store_action": set(),
        "deletion_ledger": set(),
    }
    with live.db() as c:
        for table, privileges in expected.items():
            held = {
                p
                for p in every
                if c.execute(
                    "SELECT has_table_privilege('impact_worker',%s,%s) AS h", ("impact." + table, p)
                ).fetchone()["h"]
            }
            assert held == privileges, (table, held)
        for function, worker in [
            ("impact.retention_purge_receipts(integer)", True),
            ("impact.retention_expire_uploads(integer)", True),
            ("impact.worker_schedule_retention(uuid,integer)", True),
            ("impact.privacy_remove_revisions(uuid,uuid,uuid)", False),
            ("impact.privacy_supersede_deliveries(uuid,uuid)", False),
            ("impact.privacy_redact_uploads(uuid,uuid)", False),
        ]:
            assert (
                c.execute(
                    "SELECT has_function_privilege('impact_worker',%s,'EXECUTE') AS h", (function,)
                ).fetchone()["h"]
                is worker
            ), function
            assert (
                c.execute(
                    "SELECT has_function_privilege('impact_app',%s,'EXECUTE') AS h", (function,)
                ).fetchone()["h"]
                is not worker
            ), function
    # The worker cannot rewrite a proof, nor schedule for a principal that is not a SERVICE principal.
    for statement in [
        "UPDATE impact.retention_proof SET affected_count=0",
        "DELETE FROM impact.retention_proof",
        "SELECT * FROM impact.operation_receipt",
    ]:
        with psycopg.connect(worker_dsn(), prepare_threshold=None) as c:
            c.execute("SET LOCAL ROLE impact_worker")
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant(live),))
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                c.execute(statement)
    with psycopg.connect(worker_dsn(), row_factory=dict_row, prepare_threshold=None) as c:
        c.execute("SET LOCAL ROLE impact_worker")
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant(live),))
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            c.execute(
                "SELECT impact.worker_schedule_retention(%s,3600)",
                (live.fixture["actors"]["author"]["principal_id"],),
            )
    with psycopg.connect(worker_dsn(), row_factory=dict_row, prepare_threshold=None) as c:
        c.execute("SET LOCAL ROLE impact_worker")
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_b"],))
        # Tenant-fenced: from tenant B nothing of tenant A's sweeps is visible.
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.retention_proof WHERE tenant_id=%s", (tenant(live),)
            ).fetchone()["n"]
            == 0
        )
    with pytest.raises(ConfigurationError):
        settings(live, retention_seconds=10)
