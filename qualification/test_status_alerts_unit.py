"""Release 0.27 without a database: the user-visible status catalogue (impact_api/status.py), the
on-call rota reader, alert transitions with deduplication and re-notification, the webhook (signed)
and e-mail channels with fakes, the notifier's state file, and the host wiring in ops-check.sh and
the readiness exercise script."""

import io
import json
import os
import stat
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "deploy"
sys.path.insert(0, str(DEPLOY))

import ops_alerts  # noqa: E402
from impact_api import status  # noqa: E402
from impact_api.version import SCHEMA  # noqa: E402

NOW = datetime(2026, 10, 4, 22, 0, tzinfo=timezone.utc)
OPS_CHECK = (DEPLOY / "ops-check.sh").read_text()
EXERCISE = (DEPLOY / "readiness-exercise.sh").read_text()


def fresh_ops(alerts, checked_at=None):
    return {
        "operations": {"checked_at": (checked_at or NOW).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "alerts": alerts,
    }


# ---- status catalogue -----------------------------------------------------------------------


def test_a_healthy_deployment_has_no_notices():
    workers = status.worker_view([{"state": "RUNNING", "age": 3.0}], "staging")
    notices, sources, view = status.compose(
        SCHEMA,
        workers,
        {"free_mb": 4000, "total_mb": 8000, "free_percent": 50.0},
        True,
        fresh_ops([]),
        "staging",
        NOW,
    )
    assert notices == [] and sources == [] and view["stale"] is False and view["alerts"] == []


def test_every_notice_is_catalogue_text_and_ordered_by_severity():
    workers = status.worker_view([{"state": "RUNNING", "age": 900.0}], "staging")
    ops = fresh_ops(
        [
            ops_alerts.alert("CONTAINER_UNHEALTHY", "critical", "mailsink is exited.", "mailsink"),
            ops_alerts.alert("DISK_LOW", "critical", "root: 500 MB free (0.6 %).", "root"),
            ops_alerts.alert("BACKUP_STALE", "critical", "The newest verified backup set is 30 hours old."),
        ]
    )
    notices, sources, view = status.compose(SCHEMA - 1, workers, {"free_mb": 300}, True, ops, "staging", NOW)
    codes = [n["code"] for n in notices]
    assert codes == [
        "UPGRADE_IN_PROGRESS",
        "DELIVERY_DELAYED",
        "EXPORTS_DELAYED",
        "EMAIL_UNAVAILABLE",
        "EVIDENCE_STORAGE_LOW",
    ]
    assert all(n["message"] == status.CATALOGUE[n["code"]][1] for n in notices)
    assert sources == ["OBJECT_STORE_LOW", "OPERATIONS_CHECK", "SCHEMA_MISMATCH", "WORKER_STALE"]
    # Operator detail keeps the server's closed codes; backup problems are detail, not a notice.
    assert [a["code"] for a in view["alerts"]] == ["CONTAINER_UNHEALTHY", "DISK_LOW", "BACKUP_STALE"]
    assert view["alerts"][0]["target"] == "mailsink"
    text = json.dumps(notices)
    for word in ["impact_", "dsn", "password", "secret", "login", "mailsink", "BACKUP"]:
        assert word not in text


def test_server_alerts_map_to_functions_and_a_stale_check_is_ignored():
    assert status.notices_from_alerts([ops_alerts.alert("WORKER_STALE", "critical", "x")]) == [
        "DELIVERY_DELAYED",
        "EXPORTS_DELAYED",
    ]
    assert status.notices_from_alerts(
        [ops_alerts.alert("CONTAINER_UNHEALTHY", "critical", "worker is exited.", "worker")]
    ) == ["DELIVERY_DELAYED", "EXPORTS_DELAYED"]
    assert status.notices_from_alerts(
        [ops_alerts.alert("CONTAINER_UNHEALTHY", "critical", "keycloak is exited.", "keycloak")]
    ) == ["IDENTITY_PROVIDER_UNAVAILABLE"]
    # Older status files without a target: the first word of the message is the target.
    assert status.notices_from_alerts(
        [{"code": "CONTAINER_UNHEALTHY", "severity": "critical", "message": "mailsink is exited."}]
    ) == ["EMAIL_UNAVAILABLE"]
    assert (
        status.notices_from_alerts(
            [ops_alerts.alert("DISK_LOW", "warning", "root: 1500 MB free (1.9 %).", "root")]
        )
        == []
    )
    assert status.notices_from_alerts(
        [ops_alerts.alert("DISK_LOW", "critical", "root: 500 MB free.", "root")]
    ) == ["EVIDENCE_STORAGE_LOW"]
    assert (
        status.notices_from_alerts(
            [ops_alerts.alert("RESTORE_DRILL_STALE", "warning", "x"), {"bad": 1}, None]
        )
        == []
    )
    stale = fresh_ops([ops_alerts.alert("WORKER_STALE", "critical", "x")], NOW - timedelta(hours=2))
    notices, sources, view = status.compose(SCHEMA, None, None, False, stale, "test", NOW)
    assert notices == [] and sources == [] and view["stale"] is True
    notices, _, view = status.compose(SCHEMA, None, None, False, None, "test", NOW)
    assert notices == [] and view["stale"] is True and view["checked_at"] is None


def test_worker_freshness_rules_by_environment():
    assert status.worker_view([], "test")["stale"] is False
    assert status.worker_view([], "development")["stale"] is False
    assert status.worker_view([], "staging")["stale"] is True
    assert status.worker_view([{"state": "STOPPED", "age": 5.0}], "test")["stale"] is True
    assert status.worker_view([{"state": "RUNNING", "age": 121.0}], "test")["stale"] is True
    view = status.worker_view(
        [{"state": "RUNNING", "age": 119.0}, {"state": "RUNNING", "age": 500.0}], "test"
    )
    assert view["stale"] is False and view["running_fresh"] == 1 and view["newest_beat_age_seconds"] == 119.0


def test_storage_thresholds():
    assert status.storage_notices(None, False) == []
    assert status.storage_notices(None, True) == ["EVIDENCE_UPLOADS_UNAVAILABLE"]
    assert status.storage_notices({"free_mb": 10}, True) == ["EVIDENCE_UPLOADS_UNAVAILABLE"]
    assert status.storage_notices({"free_mb": 400}, True) == ["EVIDENCE_STORAGE_LOW"]
    assert status.storage_notices({"free_mb": 4000}, True) == []


def test_store_space_uses_the_nearest_existing_ancestor(tmp_path):
    assert status.store_space("") is None
    # Not created yet (the store makes its tree on first use): the parent's free space counts.
    view = status.store_space(str(tmp_path / "objects" / "deeper"))
    assert view and view["free_mb"] >= 0 and view["total_mb"] > 0
    assert status.store_space(str(tmp_path))["total_mb"] == view["total_mb"]
    # A file where the store directory should be: unavailable.
    (tmp_path / "file").write_text("x")
    assert status.store_space(str(tmp_path / "file")) is None
    assert status.store_space(str(tmp_path / "file" / "objects")) is None


def test_on_call_rota_is_bounded_and_problems_are_closed_codes(tmp_path):
    path = tmp_path / "on-call.json"
    assert status.on_call("") == {"status": "NOT_CONFIGURED"}
    assert status.on_call(str(path)) == {"status": "MISSING"}
    path.write_text("{not json")
    assert status.on_call(str(path)) == {"status": "INVALID"}
    path.write_text(json.dumps({"schema": "other", "primary": {"name": "A"}}))
    assert status.on_call(str(path)) == {"status": "INVALID"}
    path.write_text(json.dumps({"schema": "impact-on-call-v1", "primary": {"role": "no name"}}))
    assert status.on_call(str(path)) == {"status": "INVALID"}
    example = json.loads((DEPLOY / "on-call.example.json").read_text())
    path.write_text(json.dumps(example))
    rota = status.on_call(str(path))
    assert rota["status"] == "OK" and rota["primary"]["name"] and rota["primary"]["contact"]
    assert rota["timezone"] and rota["expired"] is False and len(rota["escalation"]) <= 5
    long = dict(
        example,
        primary={"name": "x" * 1000, "contact": "y" * 1000, "extra": "ignored"},
        escalation=[{"name": str(i)} for i in range(9)],
    )
    long["valid_until"] = "2020-01-01T00:00:00Z"
    path.write_text(json.dumps(long))
    rota = status.on_call(str(path))
    assert len(rota["primary"]["name"]) == status.MAX_ON_CALL_TEXT and "extra" not in rota["primary"]
    assert len(rota["escalation"]) == 5 and rota["expired"] is True


def test_on_call_path_defaults_beside_the_ops_status_file():
    class S:
        on_call_file = ""
        ops_status_file = "/var/lib/impact/ops/ops-status.json"

    assert status.on_call_path(S()) == "/var/lib/impact/ops/on-call.json"
    S.on_call_file = "/elsewhere/rota.json"
    assert status.on_call_path(S()) == "/elsewhere/rota.json"
    S.on_call_file, S.ops_status_file = "", ""
    assert status.on_call_path(S()) == ""


# ---- alert transitions ----------------------------------------------------------------------


def alerts_now():
    return [
        ops_alerts.alert("WORKER_STALE", "critical", "No running worker has reported within 120 seconds."),
        ops_alerts.alert("CONTAINER_UNHEALTHY", "critical", "worker is exited.", "worker"),
        ops_alerts.alert("DISK_LOW", "warning", "root: 1500 MB free (1.9 %).", "root"),
    ]


def events_of(events):
    return {e["event"]: sorted(ops_alerts.alert_key(a) for a in e["alerts"]) for e in events}


def test_transitions_new_then_quiet_then_reminder_then_cleared():
    state, events = ops_alerts.transitions(alerts_now(), {}, NOW)
    assert events_of(events) == {"NEW": ["CONTAINER_UNHEALTHY|worker", "DISK_LOW|root", "WORKER_STALE|"]}
    for record in state["active"].values():
        record["last_notified"] = ops_alerts.stamp(NOW)  # delivered
    # Five minutes later, the same alerts: nothing to say.
    later = NOW + timedelta(minutes=5)
    state2, events = ops_alerts.transitions(alerts_now(), state, later)
    assert events == [] and state2["active"]["WORKER_STALE|"]["first_seen"] == ops_alerts.stamp(NOW)
    # A second disk alert on another file system is a new alert of the same code.
    more = alerts_now() + [ops_alerts.alert("DISK_LOW", "warning", "docker: 1000 MB free.", "docker")]
    _, events = ops_alerts.transitions(more, state2, later)
    assert events_of(events) == {"NEW": ["DISK_LOW|docker"]}
    # The disk alert becomes critical: reported as new again.
    worse = alerts_now()
    worse[2]["severity"] = "critical"
    _, events = ops_alerts.transitions(worse, state2, later)
    assert events_of(events) == {"NEW": ["DISK_LOW|root"]}
    # Still active after the re-notification interval: one reminder.
    _, events = ops_alerts.transitions(alerts_now(), state2, NOW + timedelta(hours=6, seconds=1))
    assert events_of(events) == {"REMINDER": ["CONTAINER_UNHEALTHY|worker", "DISK_LOW|root", "WORKER_STALE|"]}
    # The worker is back: two alerts cleared, the disk one stays quiet.
    state3, events = ops_alerts.transitions([alerts_now()[2]], state2, later)
    assert events_of(events) == {"CLEARED": ["CONTAINER_UNHEALTHY|worker", "WORKER_STALE|"]}
    assert set(state3["active"]) == {"DISK_LOW|root"}
    assert all(a["cleared_at"] for e in events for a in e["alerts"])
    # Unreadable state or alerts: everything current is new, nothing crashes.
    _, events = ops_alerts.transitions(None, None, NOW)
    assert events == []
    _, events = ops_alerts.transitions(alerts_now(), {"active": "garbage"}, NOW)
    assert events_of(events)["NEW"] == ["CONTAINER_UNHEALTHY|worker", "DISK_LOW|root", "WORKER_STALE|"]


def test_an_undelivered_new_alert_is_new_again_next_check():
    state, _ = ops_alerts.transitions(alerts_now(), {}, NOW)
    # last_notified stays null when no channel accepted it.
    _, events = ops_alerts.transitions(alerts_now(), state, NOW + timedelta(minutes=5))
    assert events_of(events) == {"NEW": ["CONTAINER_UNHEALTHY|worker", "DISK_LOW|root", "WORKER_STALE|"]}
    assert all(a["first_seen"] == ops_alerts.stamp(NOW) for e in events for a in e["alerts"])


# ---- channels -------------------------------------------------------------------------------


class FakeOpener:
    def __init__(self, status=200, error=None):
        self.status, self.error, self.requests = status, error, []

    def __call__(self, request, timeout):
        self.requests.append((request, timeout))
        if self.error:
            raise self.error
        opener = self

        class Response:
            status = opener.status

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

        return Response()


def test_webhook_is_signed_slack_compatible_and_free_of_secrets():
    _, events = ops_alerts.transitions(alerts_now(), {}, NOW)
    opener = FakeOpener()
    result = ops_alerts.send_webhook(
        "https://hooks.example/abc",
        "s3cret-value",
        events,
        "168-144-78-191.sslip.io",
        "https://x/deploy-status.json",
        NOW,
        opener,
    )
    assert result == {"outcome": "ok", "http_status": 200}
    request, timeout = opener.requests[0]
    assert timeout == ops_alerts.WEBHOOK_TIMEOUT and request.get_method() == "POST"
    assert request.get_header("Content-type") == "application/json"
    body = json.loads(request.data)
    assert body["schema"] == "impact-alert-v1" and body["events"][0]["event"] == "NEW"
    assert body["text"].startswith(
        "[impact 168-144-78-191.sslip.io] 3 new alerts: CONTAINER_UNHEALTHY (worker), DISK_LOW (root), WORKER_STALE"
    )
    assert "Status: https://x/deploy-status.json" in body["text"]
    assert "s3cret" not in request.data.decode() and "s3cret" not in json.dumps(dict(request.header_items()))
    header = request.get_header("X-impact-signature")
    assert ops_alerts.verify_signature("s3cret-value", header, request.data, NOW)
    assert not ops_alerts.verify_signature("other", header, request.data, NOW)
    assert not ops_alerts.verify_signature("s3cret-value", header, request.data + b" ", NOW)
    assert not ops_alerts.verify_signature("s3cret-value", header, request.data, NOW + timedelta(minutes=10))
    assert not ops_alerts.verify_signature("s3cret-value", "garbage", request.data, NOW)
    # No secret: no signature header, still delivered.
    opener = FakeOpener()
    ops_alerts.send_webhook("https://hooks.example/abc", "", events, "d", "", NOW, opener)
    assert opener.requests[0][0].get_header("X-impact-signature") is None
    # Failures are classes, never bodies.
    import urllib.error

    assert ops_alerts.send_webhook("https://h/x", "", events, "d", "", NOW, FakeOpener(status=500)) == {
        "outcome": "failed",
        "error": "HTTP_500",
    }
    assert ops_alerts.send_webhook(
        "https://h/x", "", events, "d", "", NOW, FakeOpener(error=urllib.error.URLError("refused"))
    ) == {"outcome": "failed", "error": "URLError"}
    assert ops_alerts.send_webhook(
        "https://h/x",
        "",
        events,
        "d",
        "",
        NOW,
        FakeOpener(error=urllib.error.HTTPError("u", 403, "f", {}, io.BytesIO())),
    ) == {"outcome": "failed", "error": "HTTP_403"}


class FakeSmtp:
    instances = []

    def __init__(self, host, port, timeout):
        self.host, self.port, self.timeout, self.calls, self.message = host, port, timeout, [], None
        FakeSmtp.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def ehlo(self):
        self.calls.append("ehlo")

    def has_extn(self, name):
        return name == "starttls"

    def starttls(self):
        self.calls.append("starttls")

    def login(self, user, password):
        self.calls.append(("login", user, password))

    def send_message(self, message):
        self.calls.append("send")
        self.message = message


def test_email_goes_through_the_workers_smtp_and_skips_the_loopback_capture():
    _, events = ops_alerts.transitions(alerts_now(), {}, NOW)
    smtp = {
        "to": "ops@example.org, owner@example.org",
        "host": "smtp.example.org",
        "port": "587",
        "username": "u",
        "password": "p",
        "sender": "impact@example.org",
    }
    FakeSmtp.instances.clear()
    result = ops_alerts.send_email(smtp, events, "example.org", "https://x/s", NOW, FakeSmtp)
    assert result == {"outcome": "ok", "recipients": 2}
    client = FakeSmtp.instances[0]
    assert (client.host, client.port, client.timeout) == ("smtp.example.org", 587, ops_alerts.SMTP_TIMEOUT)
    assert client.calls == ["ehlo", "starttls", "ehlo", ("login", "u", "p"), "send"]
    assert (
        client.message["To"] == "ops@example.org, owner@example.org"
        and client.message["From"] == "impact@example.org"
    )
    assert client.message["Subject"].startswith("[impact example.org] 3 new alerts")
    text = client.message.get_content()
    assert "critical WORKER_STALE:" in text and "Status: https://x/s" in text
    assert "password" not in text.lower() and client.message["Subject"].count("[") == 1
    assert ops_alerts.send_email(dict(smtp, host="127.0.0.1"), events, "d", "", NOW, FakeSmtp) == {
        "outcome": "skipped",
        "error": "LOOPBACK_SMTP",
    }
    assert ops_alerts.send_email(dict(smtp, to=""), events, "d", "", NOW, FakeSmtp) == {
        "outcome": "not_configured"
    }

    class Refusing(FakeSmtp):
        def __init__(self, *a, **k):
            raise ConnectionRefusedError()

    assert ops_alerts.send_email(smtp, events, "d", "", NOW, Refusing) == {
        "outcome": "failed",
        "error": "ConnectionRefusedError",
    }


# ---- the notifier end to end (files) --------------------------------------------------------


def test_notify_delivers_once_records_state_and_retries_after_a_failed_webhook(tmp_path):
    ops_alerts.write_json(str(tmp_path / "ops-status.json"), {"operations": {}, "alerts": alerts_now()})
    env = {"ALERT_WEBHOOK_URL": "https://hooks.example/x", "ALERT_WEBHOOK_SECRET": "topsecret"}
    failing = FakeOpener(status=503)
    record = ops_alerts.notify(str(tmp_path), env, NOW, deployment="d", opener=failing)
    assert record["consumed"] is False and record["channels"]["webhook"]["error"] == "HTTP_503"
    state_path = tmp_path / "alert-state.json"
    assert stat.S_IMODE(os.stat(state_path).st_mode) == 0o600
    state = json.loads(state_path.read_text())
    assert all(v["last_notified"] is None for v in state["active"].values())
    # Next check: the same NEW transitions, now accepted.
    ok = FakeOpener()
    record = ops_alerts.notify(str(tmp_path), env, NOW + timedelta(minutes=5), deployment="d", opener=ok)
    assert record["consumed"] is True and record["events"] == [
        {"event": "NEW", "codes": ["CONTAINER_UNHEALTHY", "DISK_LOW", "WORKER_STALE"]}
    ]
    assert len(ok.requests) == 1 and "topsecret" not in state_path.read_text()
    # Nothing new: no request at all.
    quiet = FakeOpener()
    record = ops_alerts.notify(str(tmp_path), env, NOW + timedelta(minutes=10), deployment="d", opener=quiet)
    assert record["events"] == [] and quiet.requests == [] and record["channels"] == {}
    # The worker recovers: CLEARED is sent once.
    ops_alerts.write_json(str(tmp_path / "ops-status.json"), {"operations": {}, "alerts": [alerts_now()[2]]})
    cleared = FakeOpener()
    record = ops_alerts.notify(
        str(tmp_path), env, NOW + timedelta(minutes=15), deployment="d", opener=cleared
    )
    assert record["events"] == [{"event": "CLEARED", "codes": ["CONTAINER_UNHEALTHY", "WORKER_STALE"]}]
    body = json.loads(cleared.requests[0][0].data)
    assert body["text"].startswith("[impact d] 2 cleared: CONTAINER_UNHEALTHY (worker), WORKER_STALE")
    state = json.loads(state_path.read_text())
    assert set(state["active"]) == {"DISK_LOW|root"} and len(state["deliveries"]) == 3
    # Without any channel the transitions are consumed silently (the status page is the signal).
    ops_alerts.write_json(str(tmp_path / "ops-status.json"), {"operations": {}, "alerts": []})
    record = ops_alerts.notify(str(tmp_path), {}, NOW + timedelta(minutes=20), deployment="d")
    assert (
        record["consumed"] is True and record["channels"] == {} and record["events"][0]["event"] == "CLEARED"
    )
    assert json.loads(state_path.read_text())["active"] == {}


def test_notify_cli_reads_secrets_from_the_environment_only(tmp_path, capsys):
    ops_alerts.write_json(str(tmp_path / "ops-status.json"), {"operations": {}, "alerts": alerts_now()})
    assert ops_alerts.main(["notify", "--ops-dir", str(tmp_path), "--deployment", "d"], env={}, now=NOW) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["consumed"] is True and out["events"][0]["event"] == "NEW"
    assert "topsecret" not in json.dumps(out)


def test_evaluate_alerts_carry_targets():
    _, alerts = ops_alerts.evaluate(
        None, None, None, None, {"root": {"free_mb": 500, "total_mb": 80000}}, NOW
    )
    by_code = {}
    for a in alerts:
        by_code.setdefault(a["code"], []).append(a["target"])
    assert by_code["DISK_LOW"] == ["root"]
    assert sorted(by_code["CONTAINER_UNHEALTHY"]) == sorted(ops_alerts.EXPECTED_SERVICES)
    assert by_code["BACKUP_MISSING"] == [""] and all("target" in a for a in alerts)


# ---- host wiring ----------------------------------------------------------------------------


def test_ops_check_delivers_transitions_with_secrets_in_the_environment_only():
    assert "notify_transitions" in OPS_CHECK and 'ops_alerts.py" notify --ops-dir' in OPS_CHECK
    for key in ["ALERT_WEBHOOK_URL", "ALERT_WEBHOOK_SECRET", "ALERT_EMAIL_TO", "SMTP_HOST", "SMTP_PASSWORD"]:
        assert key + "=" in OPS_CHECK
    # Secrets travel as environment assignments to the python process, never as arguments.
    assert "--webhook-secret" not in OPS_CHECK and "--smtp-password" not in OPS_CHECK
    assert '"${renotify:-21600}"' in OPS_CHECK


def test_readiness_exercise_script_covers_the_checklist():
    for step in [
        "stop worker",
        "start worker",
        "readiness-exercise.json",
        "WORKER_STALE",
        "DISK_LOW",
        "alert-state.json",
    ]:
        assert step in EXERCISE, step
    assert "set -euo pipefail" in EXERCISE
