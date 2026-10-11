"""Real Bash helper execution with isolated fake commands; no container/native proof."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


def shell(tmp_path, scenario):
    script = r"""
set -eu
source "$LIB"
compose() {
 printf 'compose %s\n' "$*" >> "$TRACE"
 case "$1" in
 ps)
   [ "$SCENARIO" != enumerate_failure ] || return 8
   [ "$SCENARIO" != empty ] || return 0
   printf '%s\n' "$4-container"
   ;;
 stop)
   [ "$SCENARIO" != stop_failure ] || return 9
   touch "$STOPPED"
   ;;
 run)
   [ "$SCENARIO" != probe_failure ] || return 10
   case "$SCENARIO" in
    missing_schema) printf '%s\n' '{"other_client_sessions":0,"prepared_transactions":0}'; return 0 ;;
    malformed_schema) printf '%s\n' '{"schema_before":"not-a-number"}'; return 0 ;;
    negative_schema) printf '%s\n' '{"schema_before":-1}'; return 0 ;;
   esac
   printf '%s\n' '{"other_client_sessions":0,"prepared_transactions":0,"schema_before":47}'
   ;;
 *) return 99 ;;
 esac
}
docker() {
 printf 'docker %s\n' "$*" >> "$TRACE"
 [ "$1" = inspect ] || return 99
 [ "$SCENARIO" != inspect_failure ] || return 7
 case "$3" in
 *ExitCode*)
   case "$SCENARIO" in
    forced) printf 'false 137 false\n' ;;
    unexpected_exit) printf 'false 1 false\n' ;;
    term_signal) printf 'false 143 false\n' ;;
    oom) printf 'false 0 true\n' ;;
    running) printf 'true 0 false\n' ;;
    *) printf 'false 0 false\n' ;;
   esac ;;
 *Image*) printf 'sha256:synthetic-image\n' ;;
 *)
   if [ -f "$STOPPED" ]; then
     [ "$SCENARIO" != replacement ] && printf 'false\n' || printf 'true\n'
   else
     [ "$SCENARIO" != invalid ] && printf 'true\n' || printf 'unknown\n'
   fi ;;
 esac
}
quiesce_writers
verify_writer_quiescence
printf 'migration\n' >> "$TRACE"
printf 'state=%s\n' "$WRITER_QUIESCENCE"
printf 'schema_before=%s\n' "$WRITER_SCHEMA_BEFORE"
"""
    trace = tmp_path / "trace"
    result = subprocess.run(
        ["/bin/bash", "-c", script],
        text=True,
        capture_output=True,
        env={
            "PATH": "/usr/bin:/bin",
            "LIB": str(ROOT / "deploy/lib.sh"),
            "TRACE": str(trace),
            "STOPPED": str(tmp_path / "stopped"),
            "SCENARIO": scenario,
        },
        check=False,
    )
    return result, trace.read_text().splitlines() if trace.exists() else []


@pytest.mark.parametrize("scenario", ["normal", "empty", "term_signal"])
def test_real_bash_stop_probe_migration_order_and_service_isolation(tmp_path, scenario):
    result, trace = shell(tmp_path, scenario)
    assert result.returncode == 0, result.stderr
    assert "state=verified" in result.stdout
    assert "schema_before=47" in result.stdout
    stop = "compose stop --timeout 120 api worker executor"
    probe = "compose run --rm -T --entrypoint python migrate deploy/check_writer_quiescence.py"
    assert trace.index(stop) < trace.index(probe) < trace.index("migration")
    assert all("postgres" not in line and "caddy" not in line and "keycloak" not in line for line in trace)
    assert trace.count("compose ps --all -q api") == 2
    if scenario == "empty":
        assert not any(line.startswith("docker ") for line in trace)


@pytest.mark.parametrize(
    "scenario",
    [
        "enumerate_failure",
        "inspect_failure",
        "stop_failure",
        "forced",
        "unexpected_exit",
        "oom",
        "running",
        "replacement",
        "invalid",
        "probe_failure",
        "missing_schema",
        "malformed_schema",
        "negative_schema",
    ],
)
def test_real_bash_failures_never_start_migration_or_restart_writers(tmp_path, scenario):
    result, trace = shell(tmp_path, scenario)
    assert result.returncode != 0
    assert "migration" not in trace
    assert not any(" up " in line or "start" in line for line in trace)
    if scenario not in {"probe_failure", "missing_schema", "malformed_schema", "negative_schema"}:
        assert not any(line.startswith("compose run") for line in trace)


@pytest.fixture
def probe():
    spec = importlib.util.spec_from_file_location("writer_probe", ROOT / "deploy/check_writer_quiescence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Connection:
    def __init__(self, *, administrator=True, sessions=0, prepared=0, exists=True):
        self.values = {
            "administrator": administrator,
            "sessions": sessions,
            "prepared": prepared,
            "exists": exists,
        }
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def transaction(self):
        return self

    def execute(self, sql):
        self.calls.append(sql)
        return self

    def fetchone(self):
        query = self.calls[-1]
        if "is_superuser" in query:
            return (self.values["administrator"],)
        if "pg_stat_activity" in query:
            return (self.values["sessions"],)
        if "pg_prepared_xacts" in query:
            return (self.values["prepared"],)
        if "to_regclass" in query:
            return ("impact.schema_migration" if self.values["exists"] else None,)
        return (47,)


@pytest.mark.parametrize("exists", [True, False])
def test_probe_read_only_visibility_and_empty_database(monkeypatch, probe, exists):
    connection = Connection(exists=exists)
    calls = []

    def connect(*args, **kwargs):
        calls.append((args, kwargs))
        return connection

    monkeypatch.setattr(probe.psycopg, "connect", connect)
    assert probe.check("synthetic-private-dsn") == {
        "other_client_sessions": 0,
        "prepared_transactions": 0,
        "schema_before": 47 if exists else 0,
    }
    assert calls == [(("synthetic-private-dsn",), {"connect_timeout": 10, "prepare_threshold": None})]
    assert connection.calls[0] == "SET TRANSACTION READ ONLY"
    assert "pid <> pg_backend_pid()" in connection.calls[2]
    assert "backend_type = 'client backend'" in connection.calls[2]
    assert not any("terminate" in q or "UPDATE" in q or "ALTER" in q for q in connection.calls)


@pytest.mark.parametrize(
    "options", [{"administrator": False}, {"sessions": 1}, {"prepared": 1}, {"sessions": 2, "prepared": 3}]
)
def test_probe_refuses_incomplete_visibility_and_other_clients(monkeypatch, probe, options):
    connection = Connection(**options)
    monkeypatch.setattr(probe.psycopg, "connect", lambda *a, **kw: connection)
    with pytest.raises(probe.QuiescenceError):
        probe.check("synthetic-private-dsn")
    if options.get("administrator") is False:
        assert len(connection.calls) == 2


def test_probe_main_redacts_driver_errors_and_missing_config(monkeypatch, capsys, probe):
    monkeypatch.delenv("IMPACT_ADMIN_DSN", raising=False)
    assert probe.main() == 1
    assert "Missing administrator" in capsys.readouterr().err
    monkeypatch.setenv("IMPACT_ADMIN_DSN", "synthetic-private-secret")

    def failed(*args, **kwargs):
        raise RuntimeError("private password synthetic-private-secret")

    monkeypatch.setattr(probe.psycopg, "connect", failed)
    assert probe.main() == 1
    output = capsys.readouterr()
    assert output.out == ""
    assert "synthetic-private-secret" not in output.err and "password" not in output.err
    assert "migration remains blocked" in output.err


def test_probe_main_prints_only_success_counts(monkeypatch, capsys, probe):
    monkeypatch.setenv("IMPACT_ADMIN_DSN", "synthetic-private-secret")
    monkeypatch.setattr(probe.psycopg, "connect", lambda *a, **kw: Connection())
    assert probe.main() == 0
    output = capsys.readouterr()
    assert json.loads(output.out) == {
        "other_client_sessions": 0,
        "prepared_transactions": 0,
        "schema_before": 47,
    }
    assert output.err == "" and "synthetic-private-secret" not in output.out


@pytest.mark.parametrize("fresh", [False, True])
def test_actual_write_status_preserves_private_writer_checkpoint_after_log_rotation(tmp_path, fresh):
    source = (ROOT / "deploy/update.sh").read_text()
    definition = "write_status() {" + source.split("write_status() {", 1)[1].split("\non_exit() {", 1)[0]
    helper = tmp_path / "status-function.sh"
    helper.write_text(definition)
    home = tmp_path / "home"
    state = home / "state"
    status = home / "public"
    state.mkdir(parents=True)
    logs = tmp_path / "run.log"
    checkpoint = "" if fresh else "api\tprivate-container-id\tsha256:private-original-image\ttrue\n"
    logs.write_text(
        "writer checkpoint private-container-id sha256:private-original-image\n"
        + "".join(f"later-log-line-{n}\n" for n in range(65))
    )
    secret = tmp_path / "secrets.env"
    secret.write_text("TEST_SECRET=synthetic-secret-value\n")
    env = os.environ.copy()
    env.update(
        {
            "LIB": str(ROOT / "deploy/lib.sh"),
            "FUNCTION": str(helper),
            "IMPACT_HOME": str(home),
            "CURRENT_STEP": "database migration",
            "COMMIT": "synthetic-commit",
            "STARTED_AT": "2026-10-12T00:00:00Z",
            "RUN_LOG": str(logs),
            "SECRETS_FILE": str(secret),
            "WRITER_QUIESCENCE": "verified",
            "WRITER_CHECKPOINT": checkpoint,
            "WRITER_SCHEMA_BEFORE": "46",
            "MIGRATION_STARTED": "true",
        }
    )
    result = subprocess.run(
        ["/bin/bash", "-c", 'set -eu; source "$LIB"; source "$FUNCTION"; write_status failed'],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    private = state / "writer-quiescence.json"
    document = json.loads(private.read_text())
    assert document["schema_before"] == "46"
    assert document["quiescence"] == "verified" and document["migration_started"] is True
    assert document["commit"] == "synthetic-commit"
    assert document["writers"] == (
        []
        if fresh
        else [
            {
                "service": "api",
                "container": "private-container-id",
                "image": "sha256:private-original-image",
                "was_running": "true",
            }
        ]
    )
    assert private.stat().st_mode & 0o777 == 0o600
    assert not list(state.glob(".writer-checkpoint-*"))
    for public in [status / "deploy-status.json", home / "status.json"]:
        text = public.read_text()
        published = json.loads(text)
        assert "private-container-id" not in text and "private-original-image" not in text
        assert published["writer_checkpoint_recorded"] is True
        assert published["writer_schema_before"] == "46" and published["writer_quiescence"] == "verified"
        assert published["migration_started"] is True and published["step"] == "database migration"
        assert len(published["log_tail"]) == 40 and published["log_tail"][0] == "later-log-line-25"
        assert public.stat().st_mode & 0o777 == 0o644


def test_actual_write_status_redacts_short_legacy_checkpoint_log_but_keeps_private_details(tmp_path):
    source = (ROOT / "deploy/update.sh").read_text()
    helper = tmp_path / "status-function.sh"
    helper.write_text(
        "write_status() {" + source.split("write_status() {", 1)[1].split("\non_exit() {", 1)[0]
    )
    home = tmp_path / "home"
    (home / "state").mkdir(parents=True)
    logs = tmp_path / "short-run.log"
    logs.write_text(
        "writer checkpoint service=api container=private-legacy-id image=sha256:private-legacy-image running=true\n"
        "writer checkpoint service=worker running=false\n"
        "migration refused; operator assessment required\n"
    )
    env = os.environ.copy()
    env.update(
        {
            "LIB": str(ROOT / "deploy/lib.sh"),
            "FUNCTION": str(helper),
            "IMPACT_HOME": str(home),
            "CURRENT_STEP": "writer quiescence",
            "COMMIT": "synthetic-commit",
            "STARTED_AT": "2026-10-12T00:00:00Z",
            "RUN_LOG": str(logs),
            "WRITER_QUIESCENCE": "stopping",
            "MIGRATION_STARTED": "false",
            "WRITER_SCHEMA_BEFORE": "",
            "WRITER_CHECKPOINT": "api\tprivate-legacy-id\tsha256:private-legacy-image\ttrue\n",
        }
    )
    result = subprocess.run(
        ["/bin/bash", "-c", 'set -eu; source "$LIB"; source "$FUNCTION"; write_status failed'],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    private = home / "state/writer-quiescence.json"
    saved = json.loads(private.read_text())
    assert saved["writers"] == [
        {
            "service": "api",
            "container": "private-legacy-id",
            "image": "sha256:private-legacy-image",
            "was_running": "true",
        }
    ]
    assert private.stat().st_mode & 0o777 == 0o600
    assert saved["migration_started"] is False and saved["quiescence"] == "stopping"
    for target in [home / "public/deploy-status.json", home / "status.json"]:
        text = target.read_text()
        assert "private-legacy-id" not in text and "private-legacy-image" not in text
        published = json.loads(text)
        assert published["log_tail"] == [
            "writer checkpoint details retained privately",
            "writer checkpoint service=worker running=false",
            "migration refused; operator assessment required",
        ]
        assert published["writer_checkpoint_recorded"] is True
        assert published["migration_started"] is False and published["writer_quiescence"] == "stopping"
