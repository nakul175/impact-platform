"""Operations hardening without a database or containers: the backup set (deploy/backup.sh with the
PostgreSQL client tools replaced by shell functions), the drill's restore script with stub tools,
the drill's object and blob checks, the alert evaluation and status merge, the host units, the
owner's console helpers, the operations metrics and the compose wiring for all of it."""

import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "deploy"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(DEPLOY))

import keycloak_admin  # noqa: E402
import ops_alerts  # noqa: E402
import restore_check  # noqa: E402
import smoke  # noqa: E402
from impact_api import ops_metrics  # noqa: E402
from impact_api.config import Settings  # noqa: E402
from test_deploy_unit import FakeKeycloak, fake_site, run_smoke  # noqa: E402

COMPOSE = (DEPLOY / "compose.yaml").read_text()
UPDATE = (DEPLOY / "update.sh").read_text()
NOW = datetime(2026, 10, 4, 22, 0, tzinfo=timezone.utc)
TENANT = "11111111-2222-4333-8444-555555555555"


def run_bash(script, env=None, cwd=ROOT, check=True):
    return subprocess.run(
        ["bash", "-c", script],
        cwd=cwd,
        env={**os.environ, **(env or {})},
        capture_output=True,
        text=True,
        check=check,
    )


# ---- backup sets ---------------------------------------------------------------------------

# The PostgreSQL client tools, replaced by shell functions: dumps are small files whose content
# names the database; FAIL_DUMP=<db> makes that dump fail; `date` can be pinned to a weekday.
STUBS = r"""
pg_dump() { local f="" d=""
  while [ $# -gt 0 ]; do case "$1" in -f) f=$2; shift 2;; -d) d=$2; shift 2;; *) shift;; esac; done
  [ "${FAIL_DUMP:-}" = "$d" ] && return 1; printf 'PGDMP dump of %s\n' "$d" >"$f"; }
pg_dumpall() { while [ $# -gt 0 ]; do case "$1" in -f) printf 'CREATE ROLE impact_app;\n' >"$2"; shift 2;; *) shift;; esac; done; }
pg_restore() { [ "$1" = "--list" ] && grep -q PGDMP "$2"; }
psql() { case "$*" in *schema_migration*) echo 26;; *server_version*) echo "17.6 (Debian)";; esac; }
pg_isready() { return 0; }
date() { if [ "${1:-}" = "-u" ] && [ "${2:-}" = "+%u" ] && [ -n "${WEEKDAY:-}" ]; then echo "$WEEKDAY"; else command date "$@"; fi; }
"""


def backup(tmp_path, call="take_set", **env):
    root, objects, status = tmp_path / "backups", tmp_path / "objects", tmp_path / "ops"
    objects.mkdir(exist_ok=True)
    values = {
        "BACKUP_LIBRARY": "1",
        "BACKUP_ROOT": str(root),
        "OBJECTS_DIR": str(objects),
        "STATUS_DIR": str(status),
        "IMPACT_COMMIT": "abcdef123456",
        "MIN_FREE_MB": "1",
        **env,
    }
    result = run_bash(
        "set -euo pipefail; source deploy/backup.sh; " + STUBS + "\n" + call, values, check=False
    )
    return result, root, status


def store_object(objects, data, tenant=TENANT):
    digest = hashlib.sha256(data).hexdigest()
    path = objects / tenant / digest[:2]
    path.mkdir(parents=True, exist_ok=True)
    (path / digest).write_bytes(data)
    (path / (".incoming-" + digest[:6])).write_bytes(b"half written")
    return tenant + "/" + digest[:2] + "/" + digest


def test_backup_set_holds_databases_roles_objects_and_a_verified_manifest(tmp_path):
    key = store_object(tmp_path / "objects", b"evidence bytes")
    result, root, status = backup(tmp_path)
    assert result.returncode == 0, result.stderr + result.stdout
    [day] = [p for p in (root / "daily").iterdir()]
    assert re.fullmatch(r"\d{8}", day.name) and not list((root / "daily").glob(".partial-*"))
    names = {p.name for p in day.iterdir()}
    assert names == {
        "impact.dump",
        "keycloak.dump",
        "globals.sql",
        "objects.tar",
        "SHA256SUMS",
        "manifest.json",
    }
    manifest = json.loads((day / "manifest.json").read_text())
    assert manifest["schema_version"] == 26 and manifest["commit"] == "abcdef123456"
    assert manifest["objects"] == {"files": 1} and manifest["postgres"] == "17.6"
    for entry in manifest["files"]:
        assert entry["sha256"] == hashlib.sha256((day / entry["name"]).read_bytes()).hexdigest()
        assert entry["bytes"] == (day / entry["name"]).stat().st_size
    with tarfile.open(day / "objects.tar") as tar:
        members = [m.name for m in tar.getmembers() if m.isfile()]
    assert members == ["./" + key]  # the half-written temporary file is not taken
    assert oct(day.stat().st_mode & 0o777) == "0o700"
    document = json.loads((status / "backup-status.json").read_text())
    assert (
        document["result"] == "ok" and document["daily_sets"] == [day.name] and document["weekly_sets"] == []
    )
    assert document["last_success"]["set"] == day.name and document["last_success"]["objects"] == 1
    assert not any(smoke.secret_looking(k) for k in json.dumps(document).split('"')[1::2])


def test_a_second_set_the_same_day_replaces_the_first_only_when_complete(tmp_path):
    backup(tmp_path)
    first = json.loads((tmp_path / "ops/backup-status.json").read_text())
    result, root, status = backup(tmp_path, FAIL_DUMP="keycloak")
    assert result.returncode != 0 and "FAILED at step dump_keycloak" in result.stdout
    document = json.loads((status / "backup-status.json").read_text())
    assert (document["result"], document["reason"]) == ("failed", "STEP_FAILED_dump_keycloak")
    # The earlier set and its success record are untouched; nothing partial remains.
    assert document["last_success"] == first["last_success"]
    assert (
        len(list((root / "daily").iterdir())) == 1
        and (root / "daily" / first["set"] / "impact.dump").exists()
    )
    result, root, _ = backup(tmp_path)
    assert result.returncode == 0 and len(list((root / "daily").iterdir())) == 1


def test_disk_guard_refuses_and_reports_without_touching_the_sets(tmp_path):
    backup(tmp_path)
    result, root, status = backup(tmp_path, MIN_FREE_MB=str(10**12))
    assert result.returncode != 0 and "REFUSED" in result.stdout
    document = json.loads((status / "backup-status.json").read_text())
    assert (document["result"], document["reason"]) == ("refused", "DISK_LOW")
    assert document["required_mb"] == 10**12 and document["free_mb"] < document["required_mb"]
    assert len(list((root / "daily").iterdir())) == 1
    # The requirement is twice the newest set when that is larger than the floor.
    big = root / "daily" / "20260101"
    big.mkdir()
    (big / "impact.dump").write_bytes(b"x" * (3 * 1024 * 1024))
    out = run_bash(
        "source deploy/backup.sh; ROOT=" + str(root) + "; MIN_FREE_MB=1; required_mb",
        {"BACKUP_LIBRARY": "1"},
    ).stdout
    assert int(out) >= 2  # rounded-up MiB of the newest set, doubled


def test_sundays_set_is_kept_weekly_by_hard_link_and_retention_prunes_oldest(tmp_path):
    result, root, _ = backup(tmp_path, WEEKDAY="7")
    assert result.returncode == 0, result.stderr
    [day] = list((root / "daily").iterdir())
    weekly = root / "weekly" / day.name
    assert (weekly / "impact.dump").stat().st_ino == (day / "impact.dump").stat().st_ino
    for name in ["20250101", "20250102", "20250103"]:
        (root / "daily" / name).mkdir()
    run_bash(
        "source deploy/backup.sh; ROOT=" + str(root) + "; prune " + str(root / "daily") + " 2",
        {"BACKUP_LIBRARY": "1"},
    )
    assert sorted(p.name for p in (root / "daily").iterdir()) == ["20250103", day.name]
    assert weekly.exists() and (weekly / "manifest.json").exists()


def test_verification_catches_a_changed_file(tmp_path):
    backup(tmp_path)
    [day] = list((tmp_path / "backups/daily").iterdir())
    assert (
        run_bash(
            "source deploy/backup.sh; " + STUBS + "verify_set " + str(day), {"BACKUP_LIBRARY": "1"}
        ).returncode
        == 0
    )
    (day / "globals.sql").write_text("CREATE ROLE intruder;\n")
    bad = run_bash(
        "source deploy/backup.sh; " + STUBS + "verify_set " + str(day), {"BACKUP_LIBRARY": "1"}, check=False
    )
    assert bad.returncode != 0


def test_plain_strips_everything_that_would_need_json_escaping():
    out = run_bash(
        "source deploy/backup.sh; plain 'a\"b\\\\c\nd{e}ok_1.2:3/4-5'", {"BACKUP_LIBRARY": "1"}
    ).stdout
    assert out == "abcdeok_1.2:3/4-5\n"  # cut ends the line; $(plain ...) drops it


# ---- the drill's restore script ------------------------------------------------------------


def stub_tools(directory, failing=()):
    directory.mkdir()
    log = directory / "calls.log"
    for name in ["pg_isready", "createdb", "pg_restore", "psql"]:
        body = '#!/bin/bash\necho "' + name + ' $*" >>' + str(log) + "\n"
        if name == "psql":
            body += "cat >>" + str(directory / "roles.sql") + "\n"
        if name in failing:
            body += "exit 1\n"
        (directory / name).write_text(body)
        (directory / name).chmod(0o755)
    return log


def make_set(root, tier, name, manifest=None):
    directory = root / tier / name
    directory.mkdir(parents=True)
    for file in ["impact.dump", "keycloak.dump", "objects.tar"]:
        (directory / file).write_text(file)
    (directory / "globals.sql").write_text(
        "CREATE ROLE postgres;\nALTER ROLE postgres WITH SUPERUSER;\nCREATE ROLE impact_owner;\n"
        "GRANT impact_owner TO impact_migrator GRANTED BY postgres;\n"
    )
    subprocess.run(
        "sha256sum impact.dump keycloak.dump globals.sql objects.tar > SHA256SUMS",
        shell=True,
        cwd=directory,
        check=True,
    )
    (directory / "manifest.json").write_text(
        json.dumps(manifest or {"set": name, "finished_at": "2026-10-04T21:05:00Z"})
    )
    return directory


def drill_restore(tmp_path, *args, failing=()):
    tools = tmp_path / "bin"
    log = stub_tools(tools, failing)
    result = run_bash(
        "bash deploy/drill_restore.sh " + " ".join(args),
        {"BACKUP_ROOT": str(tmp_path / "backups"), "PATH": str(tools) + ":" + os.environ["PATH"]},
        check=False,
    )
    lines = [line for line in result.stdout.splitlines() if line.startswith("{")]
    return result, json.loads(lines[-1]), log


def test_drill_restores_the_newest_set_and_skips_the_bootstrap_superuser(tmp_path):
    root = tmp_path / "backups"
    make_set(root, "daily", "20261003")
    make_set(root, "daily", "20261004")
    make_set(root, "weekly", "20260927")
    result, report, log = drill_restore(tmp_path)
    assert result.returncode == 0 and report["result"] == "ok", result.stderr
    assert report["set"] == "daily/20261004" and report["manifest"]["set"] == "20261004"
    assert set(report["seconds"]) == {
        "verify_checksums",
        "roles",
        "restore_impact",
        "restore_identity_provider",
    }
    calls = log.read_text()
    assert "createdb impact" in calls and "createdb keycloak" in calls
    assert "--exit-on-error" in calls and "20261004/impact.dump" in calls
    roles = (tmp_path / "bin/roles.sql").read_text()
    assert (
        "ROLE postgres" not in roles
        and "CREATE ROLE impact_owner;" in roles
        and "GRANTED BY postgres" in roles
    )


def case(tmp_path, name):
    directory = tmp_path / name
    (directory / "backups").mkdir(parents=True)
    return directory


def test_drill_restore_reports_a_damaged_set_or_a_failed_restore(tmp_path):
    damaged = case(tmp_path, "damaged")
    (make_set(damaged / "backups", "daily", "20261004") / "impact.dump").write_text(
        "changed after the checksum"
    )
    result, report, _ = drill_restore(damaged)
    assert result.returncode != 0 and (report["result"], report["failed_step"]) == (
        "failed",
        "verify_checksums",
    )
    absent = case(tmp_path, "absent")
    make_set(absent / "backups", "daily", "20261004")
    _, report, _ = drill_restore(absent, "weekly/20990101")
    assert report["failed_step"] == "manifest_missing"
    failing = case(tmp_path, "failing")
    make_set(failing / "backups", "daily", "20261004")
    _, report, _ = drill_restore(failing, failing=("pg_restore",))
    assert (report["result"], report["failed_step"]) == ("failed", "restore_impact")
    _, report, _ = drill_restore(case(tmp_path, "empty"))
    assert report["failed_step"] == "no_backup_set"
    _, report, _ = drill_restore(case(tmp_path, "bad"), "../../etc")
    assert report["failed_step"] == "no_backup_set"


# ---- the drill's checks --------------------------------------------------------------------


def tar_with(tmp_path, entries):
    archive = tmp_path / "objects.tar"
    with tarfile.open(archive, "w") as tar:
        for name, data in entries:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    return archive


def test_object_digests_match_names_and_blob_rows_find_their_objects(tmp_path):
    good, other = b"first object", b"second object"
    g, o = hashlib.sha256(good).hexdigest(), hashlib.sha256(other).hexdigest()
    archive = tar_with(
        tmp_path,
        [
            ("./" + TENANT + "/" + g[:2] + "/" + g, good),
            (TENANT + "/" + o[:2] + "/" + o, b"bytes that are not the named ones"),
            ("./notes.txt", b"not content-addressed"),
        ],
    )
    objects, mismatched, foreign = restore_check.object_digests(archive)
    assert set(objects) == {TENANT + "/" + g[:2] + "/" + g, TENANT + "/" + o[:2] + "/" + o}
    assert mismatched == [TENANT + "/" + o[:2] + "/" + o] and foreign == ["./notes.txt"]
    rows = [(TENANT + "/" + g[:2] + "/" + g, g, len(good)), (TENANT + "/aa/" + "a" * 64, "a" * 64, 3)]
    assert restore_check.blobs_missing(rows, objects) == [TENANT + "/aa/" + "a" * 64]
    assert restore_check.blobs_missing(rows[:1], objects) == []
    # A recorded size that differs is a missing object too.
    assert restore_check.blobs_missing([(rows[0][0], g, len(good) + 1)], objects) == [rows[0][0]]


def test_restore_check_refuses_an_unexpected_set_name(capsys):
    assert restore_check.main(["--set", "../etc"], env={}) == 1
    assert json.loads(capsys.readouterr().out.strip())["outcome"] == "FAIL"
    assert (
        restore_check.migrator_dsn("host=drill-db user=postgres dbname=impact", "pw").count("impact_migrator")
        == 1
    )


# ---- alerts --------------------------------------------------------------------------------


def healthy_inputs():
    backup_status = {
        "result": "ok",
        "attempted_at": "2026-10-04T21:00:00Z",
        "last_success": {
            "set": "20261004",
            "finished_at": "2026-10-04T21:04:00Z",
            "bytes": 5000,
            "objects": 2,
        },
        "free_mb": 40000,
        "required_mb": 1024,
        "daily_sets": ["20261004", "20261003"],
        "weekly_sets": [],
    }
    drill = {
        "outcome": "PASS",
        "finished_at": "2026-10-04T21:30:00Z",
        "duration_seconds": 41,
        "set": "daily/20261004",
    }
    containers = [
        {
            "Service": name,
            "State": "running",
            "Health": "healthy" if name in {"api", "caddy", "keycloak", "postgres"} else "",
        }
        for name in ops_alerts.EXPECTED_SERVICES
    ]
    app = {
        "schema_version": 26,
        "schema_expected": 26,
        "workers": {"running_fresh": 1, "stale_after_seconds": 120, "newest_beat_age_seconds": 3.0},
        "deliveries": {"dead": 0, "held": 0, "capped": False, "unsent": 2},
        "jobs": {"unfinished": 0},
    }
    disks = {"root": {"free_mb": 40000, "total_mb": 80000}}
    return backup_status, drill, containers, app, disks


def codes(alerts):
    return sorted(a["code"] for a in alerts)


def test_a_healthy_server_has_no_alerts():
    view, alerts = ops_alerts.evaluate(*healthy_inputs(), NOW)
    assert alerts == []
    assert view["backup"]["age_hours"] == 0.9 and view["restore_drill"]["outcome"] == "PASS"
    assert view["disk"]["root"]["free_percent"] == 50.0 and view["services"]["api"]["health"] == "healthy"


@pytest.mark.parametrize(
    "change,expected",
    [
        (lambda b, d, c, a, k: b.update(last_success=None), ["BACKUP_MISSING"]),
        (
            lambda b, d, c, a, k: b["last_success"].update(finished_at="2026-10-03T19:00:00Z"),
            ["BACKUP_STALE"],
        ),
        (lambda b, d, c, a, k: b.update(result="failed", reason="STEP_FAILED_objects"), ["BACKUP_FAILED"]),
        (lambda b, d, c, a, k: b.update(result="refused", reason="DISK_LOW"), ["BACKUP_REFUSED_DISK_LOW"]),
        (lambda b, d, c, a, k: k.update(root={"free_mb": 1500, "total_mb": 80000}), ["DISK_LOW"]),
        (lambda b, d, c, a, k: c.pop(), ["CONTAINER_UNHEALTHY"]),
        (lambda b, d, c, a, k: c[2].update(Health="unhealthy"), ["CONTAINER_UNHEALTHY"]),
        (lambda b, d, c, a, k: c[1].update(State="restarting"), ["CONTAINER_UNHEALTHY"]),
        (lambda b, d, c, a, k: a["workers"].update(running_fresh=0), ["WORKER_STALE"]),
        (lambda b, d, c, a, k: a["deliveries"].update(dead=3), ["DELIVERIES_DEAD"]),
        (lambda b, d, c, a, k: a["jobs"].update(unfinished=500), ["QUEUE_BACKLOG"]),
        (lambda b, d, c, a, k: a.update(schema_version=25), ["SCHEMA_MISMATCH"]),
        (lambda b, d, c, a, k: a.clear() or a.update(error="API_NOT_REACHABLE"), ["OPS_SUMMARY_UNAVAILABLE"]),
        (lambda b, d, c, a, k: d.update(outcome="FAIL", error="CHECKS_FAILED"), ["RESTORE_DRILL_FAILED"]),
        (lambda b, d, c, a, k: d.update(finished_at="2026-09-20T21:30:00Z"), ["RESTORE_DRILL_STALE"]),
        (lambda b, d, c, a, k: d.clear(), ["RESTORE_DRILL_STALE"]),
    ],
)
def test_each_problem_raises_its_alert(change, expected):
    inputs = healthy_inputs()
    change(*inputs)
    _, alerts = ops_alerts.evaluate(*inputs, NOW)
    assert codes(alerts) == expected
    assert all(a["severity"] in {"critical", "warning"} and a["message"] for a in alerts)


def test_disk_severity_and_unreadable_inputs():
    b, d, c, a, _ = healthy_inputs()
    _, alerts = ops_alerts.evaluate(b, d, c, a, {"root": {"free_mb": 900, "total_mb": 80000}}, NOW)
    assert alerts[0]["severity"] == "critical"
    _, alerts = ops_alerts.evaluate(None, None, None, None, None, NOW)
    assert "BACKUP_MISSING" in codes(alerts) and "OPS_SUMMARY_UNAVAILABLE" in codes(alerts)
    assert codes(alerts).count("CONTAINER_UNHEALTHY") == len(ops_alerts.EXPECTED_SERVICES)


def test_evaluate_writes_the_ops_file_and_merges_into_the_status_files(tmp_path):
    b, d, c, a, k = healthy_inputs()
    a["deliveries"]["dead"] = 1
    ops = tmp_path / "ops"
    ops.mkdir()
    (ops / "backup-status.json").write_text(json.dumps(b))
    (ops / "restore-drill.json").write_text(json.dumps(d))
    files = {}
    for name, value in {
        "containers": "\n".join(json.dumps(r) for r in c),
        "app": json.dumps(a),
        "disk": json.dumps(k),
    }.items():
        files[name] = tmp_path / (name + ".json")
        files[name].write_text(value)
    status = tmp_path / "status.json"
    status.write_text(json.dumps({"result": "ok", "commit": "abc", "alerts": []}))
    secrets_file = tmp_path / "secrets.env"
    secrets_file.write_text("POSTGRES_PASSWORD=" + "s3cr3t-value-123" + "\n")
    d["error"] = "s3cr3t-value-123"
    (ops / "restore-drill.json").write_text(json.dumps(d))
    code = ops_alerts.main(
        [
            "evaluate",
            "--ops-dir",
            str(ops),
            "--containers",
            str(files["containers"]),
            "--app",
            str(files["app"]),
            "--disk",
            str(files["disk"]),
            "--status-file",
            str(status),
            "--status-file",
            str(tmp_path / "absent.json"),
            "--secrets-file",
            str(secrets_file),
        ],
        now=NOW,
    )
    assert code == 0
    merged = json.loads(status.read_text())
    assert merged["result"] == "ok" and merged["commit"] == "abc"
    assert (
        codes(merged["alerts"]) == ["DELIVERIES_DEAD"]
        and merged["operations"]["backup"]["last_set"] == "20261004"
    )
    written = json.loads((ops / "ops-status.json").read_text())
    assert (
        written["alerts"] == merged["alerts"]
        and "s3cr3t-value-123" not in (ops / "ops-status.json").read_text()
    )
    assert not (tmp_path / "absent.json").exists()
    # The public status file passes the smoke check's secret-field test (keycloak is a service).
    report = run_smoke(
        fake_site({"https://app.example.org/deploy-status.json": lambda r: httpx.Response(200, json=merged)})
    )
    assert report["passed"], report
    assert [c for c in report["checks"] if c["check"] == "deploy_status"][0]["detail"]["alerts"] == [
        "DELIVERIES_DEAD"
    ]


def test_drill_record_measures_duration_and_backup_age(tmp_path):
    started = int(datetime(2026, 10, 4, 23, 20, tzinfo=timezone.utc).timestamp())
    restore = {
        "set": "daily/20261004",
        "result": "ok",
        "seconds": {"restore_impact": 4.2},
        "manifest": {
            "finished_at": "2026-10-04T21:05:00Z",
            "schema_version": 26,
            "files": [{"bytes": 100}, {"bytes": 23}],
        },
    }
    check = {
        "outcome": "PASS",
        "checks": {"a": True},
        "restored": {"tables": 167, "rows": 900},
        "seconds": 3.1,
    }
    env = {
        "OUTCOME": "PASS",
        "STARTED": str(started),
        "FINISHED": str(started + 75),
        "RESTORE": json.dumps(restore),
        "CHECK": json.dumps(check),
        "ERROR": "",
    }
    assert ops_alerts.main(["drill-result", str(tmp_path / "drill.json")], env=env, now=NOW) == 0
    record = json.loads((tmp_path / "drill.json").read_text())
    assert (record["duration_seconds"], record["backup_age_hours"], record["set_bytes"]) == (75, 2.2, 123)
    assert record["set"] == "daily/20261004" and record["checks"] == {"a": True} and record["error"] is None
    env.update(OUTCOME="FAIL", ERROR="RESTORE_FAILED", RESTORE="not json", CHECK="")
    ops_alerts.main(["drill-result", str(tmp_path / "drill.json")], env=env, now=NOW)
    record = json.loads((tmp_path / "drill.json").read_text())
    assert (record["outcome"], record["error"], record["set"]) == ("FAIL", "RESTORE_FAILED", None)


# ---- host units and owner console ----------------------------------------------------------


def test_host_units_run_the_check_every_five_minutes_and_the_drill_weekly(tmp_path):
    function = re.search(
        r"^render_host_units\(\) \{.*?\n\}\n(?=\ninstall_host_units)", UPDATE, re.M | re.S
    ).group(0)
    run_bash(
        function + "\nIMPACT_HOME=/opt/impact DEPLOY_DIR=/opt/impact/repo/deploy STATE_DIR=/opt/impact/state "
        "render_host_units " + str(tmp_path)
    )
    service = (tmp_path / "impact-ops-check.service").read_text()
    assert (
        "ExecStart=/opt/impact/repo/deploy/ops-check.sh" in service and "IMPACT_HOME=/opt/impact" in service
    )
    assert "OnUnitActiveSec=5min" in (tmp_path / "impact-ops-check.timer").read_text()
    drill = (tmp_path / "impact-restore-drill.timer").read_text()
    assert "OnCalendar=Sun *-*-* 23:15:00 UTC" in drill and "Persistent=true" in drill
    assert (
        "ExecStart=/opt/impact/repo/deploy/restore-drill.sh"
        in (tmp_path / "impact-restore-drill.service").read_text()
    )
    rotate = (tmp_path / "logrotate").read_text()
    assert "/var/log/impact-deploy.log" in rotate and "/opt/impact/state/admin-actions.log" in rotate
    assert "copytruncate" in rotate and "maxsize 20M" in rotate
    assert "install_host_units\n" in UPDATE and "IMPACT_HOST_UNITS" in UPDATE


def test_box_and_user_listing_are_plain_text():
    out = run_bash(
        'source deploy/lib.sh; box "Address:  https://a.example.org/" "" "Username: o@example.org"'
    ).stdout
    lines = [line for line in out.splitlines() if line.strip()]
    assert lines[0] == lines[-1] and set(lines[0].strip()) == {"+", "-"}
    assert len({len(line) for line in lines}) == 1 and "|  Username: o@example.org" in out
    listing = {
        "users": [
            {"email": "o@example.org", "name": "Owner", "enabled": True, "totp_configured": True},
            {"email": "n@example.org", "name": "New", "enabled": True, "temporary_password_pending": True},
            {"email": "l@example.org", "name": "", "enabled": True, "locked": True},
            {"email": "x@example.org", "name": "Off", "enabled": False},
        ]
    }
    table = subprocess.run(
        ["bash", "-c", "source deploy/lib.sh; format_user_listing"],
        cwd=ROOT,
        input=json.dumps(listing),
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "accounts on this deployment: 4" in table
    assert re.search(r"o@example.org\s+Owner\s+active, authenticator app set up", table)
    assert re.search(r"n@example.org\s+New\s+has not signed in yet", table)
    assert "temporarily locked" in table and "switched off" in table


class ListingKeycloak(FakeKeycloak):
    def call(self, method, path, data=None, expect=(200, 201, 204)):
        if method == "GET" and path.startswith("/impact/users?") and "email=" not in path:
            return 200, list(self.users.values()), {}
        if method == "GET" and "/attack-detection/brute-force/users/" in path:
            return 200, {"disabled": path.endswith(self.locked)}, {}
        return super().call(method, path, data, expect)


def test_keycloak_listing_reports_status_without_credentials():
    fake = ListingKeycloak(realm={"clients": []})
    first = keycloak_admin.ensure_user(fake, "impact", "b@example.org", "abcd-efgh-jkmn-pqrs", "B", "Person")
    second = keycloak_admin.ensure_user(fake, "impact", "a@example.org", "abcd-efgh-jkmn-pqrs", "A", "")
    fake.users[second["subject"]]["requiredActions"] = []
    fake.credentials[second["subject"]] = [{"id": "o", "type": "otp"}]
    fake.locked = first["subject"]
    listing = keycloak_admin.list_users(fake, "impact")
    assert [u["email"] for u in listing["users"]] == ["a@example.org", "b@example.org"]
    a, b = listing["users"]
    assert (a["totp_configured"], a["temporary_password_pending"], a["locked"], a["name"]) == (
        True,
        False,
        False,
        "A",
    )
    assert (b["temporary_password_pending"], b["locked"], b["name"]) == (True, True, "B Person")
    assert "abcd-efgh-jkmn-pqrs" not in json.dumps(listing) and listing["truncated"] is False


def test_owner_scripts_refuse_pipes_and_bad_arguments(tmp_path):
    for script, args in [
        ("reset-user.sh", "not-an-email"),
        ("reset-user.sh", "a@example.org --bogus"),
        ("list-users.sh", "extra"),
    ]:
        result = run_bash("deploy/" + script + " " + args, {"IMPACT_HOME": str(tmp_path)}, check=False)
        assert result.returncode != 0 and ("usage" in result.stderr or "not an e-mail" in result.stderr)
    reset = (DEPLOY / "reset-user.sh").read_text()
    assert 'if [ ! -t 1 ] && [ "${IMPACT_ALLOW_NON_TTY:-}" != "1" ]' in reset
    assert '>>"$STATE_DIR/admin-actions.log"' in reset and '$password" >>' not in reset
    first_admin = (DEPLOY / "first-admin.sh").read_text()
    assert (
        'box "Impact Platform (staging) - your first sign-in"' in first_admin and "Username:" in first_admin
    )


# ---- compose wiring ------------------------------------------------------------------------


def service(name):
    return re.search(r"\n  " + name + r":\n(.*?)(?=\n  [a-z-]+:\n|\nnetworks:)", COMPOSE, re.S).group(1)


def test_every_service_rotates_its_logs_and_the_drill_is_isolated():
    names = re.findall(r"^  ([a-z-]+):\n", COMPOSE.split("\nservices:\n")[1].split("\nnetworks:\n")[0], re.M)
    assert {"backup", "drill-db", "drill-check", "api", "worker"} <= set(names)
    for name in names:
        body = service(name)
        assert "logging: *logging" in body or "*app" in body, name
    assert 'max-size: "10m"' in COMPOSE and 'max-file: "5"' in COMPOSE
    drill_db, drill_check = service("drill-db"), service("drill-check")
    for body in (drill_db, drill_check):
        assert 'profiles: ["drill"]' in body and "networks: [drill]" in body
        assert "pgdata" not in body and "backups:/backups:ro" in body and "objects" not in body
        assert "POSTGRES_PASSWORD}" not in body and "LOGIN_PASSWORD" not in body
    assert "${DRILL_DB_PASSWORD:-}" in drill_db and "postgresql://postgres@drill-db" in drill_check
    assert re.search(r"\n  drill:\n    internal: true", COMPOSE)
    backup_body = service("backup")
    assert "objects:/objects:ro" in backup_body and "${IMPACT_OPS_DIR:?}:/ops" in backup_body
    assert "${IMPACT_OPS_DIR:?}:/var/lib/impact/ops:ro" in service("api")
    assert "IMPACT_OPS_DIR=%s" in UPDATE and "deploy/restore_check.py" in (DEPLOY / "Dockerfile").read_text()


def test_new_scripts_are_executable_and_strict():
    for name in ["restore-drill.sh", "ops-check.sh", "drill_restore.sh", "list-users.sh", "reset-user.sh"]:
        path = DEPLOY / name
        assert os.access(path, os.X_OK), name
        assert "set -euo pipefail" in path.read_text(), name


# ---- operations metrics --------------------------------------------------------------------


def test_request_metrics_count_families_classes_and_latency_without_paths():
    ticks = iter([100.0, 160.0])
    metrics = ops_metrics.RequestMetrics(clock=lambda: next(ticks))
    metrics.observe("/v1/tenants/" + TENANT + "/programmes", 200, 0.03)
    metrics.observe("/v1/platform/metrics", 404, 0.2)
    metrics.observe("/auth/login", 302, 7.0)
    metrics.observe("/", 500, 0.06)
    snapshot = metrics.snapshot()
    assert snapshot["total"] == 4 and snapshot["uptime_seconds"] == 60
    assert snapshot["by_family"]["tenant"]["2xx"] == 1 and snapshot["by_family"]["platform"]["4xx"] == 1
    assert snapshot["by_family"]["auth"]["3xx"] == 1 and snapshot["by_family"]["client"]["5xx"] == 1
    buckets = snapshot["latency_seconds"]["buckets"]
    assert buckets[0] == {"le": 0.05, "count": 1} and buckets[1] == {"le": 0.1, "count": 2}
    assert buckets[-1] == {"le": None, "count": 4} and snapshot["latency_seconds"]["sum"] == 7.29
    assert TENANT not in json.dumps(snapshot)


def test_operations_file_and_storage_are_optional(tmp_path):
    assert ops_metrics.operations("") is None and ops_metrics.operations(str(tmp_path / "absent")) is None
    (tmp_path / "bad.json").write_text("{")
    assert ops_metrics.operations(str(tmp_path / "bad.json")) is None
    (tmp_path / "ops.json").write_text(json.dumps({"alerts": [], "operations": {"backup": {}}}))
    assert ops_metrics.operations(str(tmp_path / "ops.json"))["alerts"] == []
    assert ops_metrics.storage("") is None
    figures = ops_metrics.storage(str(tmp_path))
    assert figures["total_mb"] > 0 and 0 <= figures["free_percent"] <= 100


def test_ops_status_file_must_be_absolute(monkeypatch):
    monkeypatch.setenv("IMPACT_ENVIRONMENT", "test")
    monkeypatch.setenv("IMPACT_COOKIE_SECRET", "c" * 48)
    for name in [
        "APP_DSN",
        "IDENTITY_DSN",
        "PUBLIC_ORIGIN",
        "ISSUER",
        "CLIENT_ID",
        "AUDIENCE",
        "JWKS_URL",
        "AUTHORIZATION_URL",
        "TOKEN_URL",
    ]:
        monkeypatch.setenv("IMPACT_" + name, "")
    monkeypatch.delenv("IMPACT_CONFIG_FILE", raising=False)
    monkeypatch.setenv("IMPACT_OPS_STATUS_FILE", "relative/ops.json")
    with pytest.raises(ValueError, match="ops_status_file"):
        Settings.load()
    monkeypatch.setenv("IMPACT_OPS_STATUS_FILE", "/var/lib/impact/ops/ops-status.json")
    assert Settings.load().ops_status_file == "/var/lib/impact/ops/ops-status.json"


def test_backup_age_helpers_handle_naive_and_missing_times():
    assert ops_alerts.parse_time("2026-10-04T21:00:00") == datetime(2026, 10, 4, 21, tzinfo=timezone.utc)
    assert ops_alerts.parse_time(None) is None and ops_alerts.parse_time("yesterday") is None
    assert ops_alerts.hours_between(NOW - timedelta(minutes=90), NOW) == 1.5
