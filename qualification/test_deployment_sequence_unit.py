"""Execute the actual deployment main with fake host/container boundaries only.

No Docker, accounts, services, metadata requests or deployment are operated.
Separate quiescence/native/container tests qualify the mocked boundaries.
"""

import os
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


def sequence(tmp_path, scenario):
    source = (ROOT / "deploy/update.sh").read_text()
    main = "main() {" + source.split("main() {", 1)[1].rsplit('\nmain "$@"', 1)[0]
    on_exit = "on_exit() {" + source.split("on_exit() {", 1)[1].split("\ntrap on_exit EXIT", 1)[0]
    definitions = tmp_path / "main-definitions.sh"
    definitions.write_text(main + "\n" + on_exit)
    home = tmp_path / "owned-home"
    state = home / "state"
    state.mkdir(parents=True)
    (home / "config.env").write_text("IMPACT_APP_HOST=example.test\nIMPACT_AUTH_HOST=auth.example.test\n")
    if scenario == "unchanged":
        (state / "last-success").write_text("synthetic-current-commit\n")
        (state / "schema").write_text("47\n")
    elif scenario != "fresh":
        (state / "last-success").write_text("synthetic-old-commit\n")
    operations = tmp_path / "fake-deploy"
    operations.mkdir()
    helper = operations / "ops-check.sh"
    helper.write_text("#!/bin/bash\nexit 0\n")
    helper.chmod(0o700)
    trace = tmp_path / "trace"
    script = r"""
set -euo pipefail
source "$LIB"
source "$DEFINITIONS"
DEPLOY_DIR="$FAKE_DEPLOY"
CURRENT_STEP=start
STARTED_AT=synthetic-time
COMMIT=""
RUN_LOG=""
WRITER_QUIESCENCE=not-started
MIGRATION_STARTED=false
WRITER_CHECKPOINT=""
WRITER_SCHEMA_BEFORE=""
record() { printf '%s\n' "$*" >> "$TRACE"; }
step() { CURRENT_STEP=$1; record "step $1"; }
require_root() { record require_root; }
flock() { record flock; }
systemctl() { return 1; }
ensure_secret() { printf '%s=synthetic-placeholder\n' "$1" >> "$SECRETS_FILE"; }
readable_password() { printf 'synthetic-placeholder\n'; }
install_host_units() { record host_units; }
container_health() { [ "$1" = worker ] || [ "$1" = executor ] && printf 'running\n' || printf 'healthy\n'; }
wait_for() {
 record "wait $*"
 if [ "$SCENARIO" = health_failure ] && [ "$1" = api ]; then return 12; fi
}
quiesce_writers() { record quiesce; WRITER_QUIESCENCE=stopped; }
verify_writer_quiescence() {
 record probe
 [ "$SCENARIO" != probe_failure ] || return 11
 WRITER_QUIESCENCE=verified
 WRITER_SCHEMA_BEFORE=46
}
write_status() { record "status $1 step=$CURRENT_STEP phase=$WRITER_QUIESCENCE migration=$MIGRATION_STARTED"; }
docker() {
 record "docker $*"
 case "$*" in
  'compose version') return 0 ;;
  image\ inspect*) return 1 ;;
  image\ ls*|image\ prune*) return 0 ;;
  *) return 90 ;;
 esac
}
compose() {
 record "compose $*"
 case "$*" in
  'build --pull api'|'up -d postgres'|'up -d caddy'|'up -d --remove-orphans') return 0 ;;
  'run --rm -T migrate')
    if [ "$SCENARIO" = migration_failure ]; then printf 'partial migration; failed\n'; return 13; fi
    printf '%s\n' '{"schema_version":47}' ;;
  *keycloak_admin.py\ realm*) printf '%s\n' '{"outcome":"existing"}' ;;
  *keycloak_admin.py\ provisioner*) printf '%s\n' '{"outcome":"existing"}' ;;
  *keycloak_admin.py\ user*) printf '%s\n' '{"subject":"synthetic-owner"}' ;;
  *bootstrap_operator.py*) printf '%s\n' '{"outcome":"existing"}' ;;
  *) return 91 ;;
 esac
}
trap on_exit EXIT
main
"""
    env = os.environ.copy()
    env.update(
        {
            "IMPACT_HOME": str(home),
            "LIB": str(ROOT / "deploy/lib.sh"),
            "DEFINITIONS": str(definitions),
            "FAKE_DEPLOY": str(operations),
            "IMPACT_COMMIT": "synthetic-current-commit",
            "SCENARIO": scenario,
            "TRACE": str(trace),
        }
    )
    result = subprocess.run(
        ["/bin/bash", "-c", script], text=True, capture_output=True, env=env, check=False, timeout=20
    )
    return result, trace.read_text().splitlines(), state


def test_actual_main_existing_healthy_commit_returns_without_writer_stop_or_migration(tmp_path):
    result, calls, state = sequence(tmp_path, "unchanged")
    assert result.returncode == 0, result.stderr
    assert "step unchanged" in calls
    assert not any(x in calls for x in ["quiesce", "probe", "step image build", "step database migration"])
    assert not any(x.startswith("compose ") for x in calls)
    assert calls[-1].startswith("status ok step=unchanged")
    assert (state / "last-success").read_text().strip() == "synthetic-current-commit"


def test_actual_main_fresh_path_builds_then_stops_probes_migrates_starts_and_checks_health(tmp_path):
    result, calls, state = sequence(tmp_path, "fresh")
    assert result.returncode == 0, result.stderr
    ordered = [
        "compose build --pull api",
        "compose up -d postgres",
        "wait postgres healthy 180",
        "quiesce",
        "probe",
        "compose run --rm -T migrate",
        "compose up -d caddy",
        "compose up -d --remove-orphans",
        "wait api healthy 240",
        "step done",
    ]
    positions = [calls.index(item) for item in ordered]
    assert positions == sorted(positions)
    assert calls[-1] == "status ok step=done phase=verified migration=true"
    assert (state / "schema").read_text().strip() == "47"
    assert (state / "last-success").read_text().strip() == "synthetic-current-commit"


@pytest.mark.parametrize("scenario", ["probe_failure", "migration_failure"])
def test_actual_main_prestart_failures_leave_writers_stopped_and_no_success(tmp_path, scenario):
    result, calls, state = sequence(tmp_path, scenario)
    assert result.returncode != 0
    assert "quiesce" in calls and "probe" in calls
    assert "compose up -d caddy" not in calls and "compose up -d --remove-orphans" not in calls
    assert not any(x.startswith("status ok") for x in calls)
    assert calls[-1].startswith("status failed")
    assert (state / "last-success").read_text().strip() == "synthetic-old-commit"
    if scenario == "probe_failure":
        assert "compose run --rm -T migrate" not in calls
        assert "migration=false" in calls[-1]
    else:
        assert "migration=true" in calls[-1]


def test_actual_main_postmigration_readiness_failure_records_failure_not_success(tmp_path):
    result, calls, state = sequence(tmp_path, "health_failure")
    assert result.returncode != 0
    assert "compose run --rm -T migrate" in calls
    assert "compose up -d --remove-orphans" in calls
    assert "wait api healthy 240" in calls
    assert calls[-1] == "status failed step=health phase=verified migration=true"
    assert not any(x.startswith("status ok") for x in calls)
    assert "step done" not in calls
    assert (state / "schema").read_text().strip() == "47"
    assert (state / "last-success").read_text().strip() == "synthetic-old-commit"
