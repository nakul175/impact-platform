"""Single process tree keeps local services reachable in sandboxed workspaces.

PGlite modes (dev, test, browser checks) start tools/dev-db/server.mjs, which only serves the
database on IMPACT_DEV_DB_PORT (55432 in dev mode; a port chosen by the operating system in test
and browser modes, so parallel runners and orphaned servers never collide) and reports the
actual port in one JSON status line; scripts/migrate.py then applies the migrations and the
fixture over the wire exactly as it does on native PostgreSQL. Native mode (--native) provisions
the five login roles on the disposable server named by IMPACT_FIXTURE_DSN, migrates as
impact_migrator, loads the fixture as the superuser, and starts the API on the app, identity and
platform logins only: the API process never receives the fixture, migration, worker or
administrator connection, the login passwords, or any libpq PG* variable. The worker login's
connection reaches only the test process (IMPACT_LOGIN_DSN_WORKER), which starts its own worker
subprocesses (qualification/test_native_worker.py). Dev mode also starts one worker process
(python -m impact_api.worker, synthetic mail sink under .local/dev) unless --no-worker is given; it
receives only .local/dev/worker.json, never the API configuration. After the native suite the
runner stops the API and starts a fresh process against the same database between the two phases
of qualification/test_native_restart.py (--skip-restart-check), runs scripts/restore_drill.py on
the database the suite just used (--skip-restore-drill) and scripts/native_upgrade_check.py on a
fresh one (--skip-upgrade-check); all three merge into docs/evidence/native-qualification.json.

With --idp keycloak (test mode, on PGlite or --native, and the idp-browser mode) the runner starts the pinned Keycloak of
scripts/idp.py on an OS-chosen loopback port after the migrations, bootstraps the API for that live
provider (dev_auth off, discovery endpoints, required ACR) with the fixture identities re-pointed
to the realm's issuer, and stops Keycloak on exit. The test mode then runs
qualification/test_live_idp.py (or --pytest-path) and writes docs/evidence/idp-tests.xml
(idp-native-tests.xml with --native) and merges its run into docs/evidence/idp-qualification.json
under runs.pglite or runs.native; it never touches application-tests.xml. With --native the API
runs on the provisioned login roles under IMPACT_REQUIRE_UNPRIVILEGED_DB exactly as in the native
suite, the fixture identities are re-pointed through the superuser fixture connection, and the
restart check, restore drill and upgrade check are not run (they belong to the full native run).
"""

import argparse
import json
import os
import secrets
import signal
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ElementTree
from datetime import datetime, timezone
from pathlib import Path

import httpx
import jwt
import psycopg
from psycopg.conninfo import conninfo_to_dict
from bootstrap import bootstrap
from fixture_support import FIXTURE_EXPIRES_AT, fixture_days_remaining
from provision_logins import LOGINS, login_dsn, passwords_from_env, provision
import migrate
import idp as identity_provider

ROOT = Path(__file__).resolve().parents[1]
# The documented development port; the test and browser runners let the operating system choose.
PGLITE_DEFAULT_PORT = "55432"
# The suites create fixture-relative authority (recovery contacts, initial access, renewals) that
# expires up to 60 days from now and must stay inside the fixture's delegation ceilings, so the
# runner refuses to start once the fixture's own expiry is closer than this.
FIXTURE_PREFLIGHT_DAYS = 90
# Never handed to the API process: fixture, migration and administrator connections and passwords.
PRIVILEGED_ENV = {"IMPACT_FIXTURE_DSN", "IMPACT_MIGRATION_DSN", "IMPACT_ADMIN_DSN"}
BROWSER_MODES = {
    "browser": "check.mjs",
    "admin-browser": "admin-check.mjs",
    "measurement-browser": "measurement-check.mjs",
    "planning-browser": "planning-check.mjs",
    "dashboard-browser": "dashboard-check.mjs",
    "forms-browser": "forms-check.mjs",
    "reporting-browser": "reporting-check.mjs",
    "workspace-browser": "workspace-check.mjs",
    "tenant-browser": "tenant-check.mjs",
    "bootstrap-browser": "bootstrap-check.mjs",
    "recovery-browser": "recovery-check.mjs",
    "renewal-browser": "renewal-check.mjs",
    "idp-browser": "idp-check.mjs",
}
# Browser modes that sign in through the live provider rather than the development login.
IDP_ONLY_MODES = {"idp-browser"}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def pglite_dsn(port):
    """The unauthenticated loopback connection to the development database on the reported port."""
    return "postgresql://postgres:development@127.0.0.1:" + str(port) + "/impact_dev?sslmode=disable"


def database_status(log):
    """The JSON status line tools/dev-db/server.mjs prints once it listens (or fails), parsed
    line by line: a substring such as "ready" inside Node's "address already in use" text is
    never a match."""
    for line in log.read_text().splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            status = json.loads(line)
        except ValueError:
            continue
        if isinstance(status, dict) and status.get("status") in {"ready", "failed"}:
            return status
    return None


def start_database(local, env, mode):
    """Start the PGlite server on IMPACT_DEV_DB_PORT (the documented 55432 in dev mode, a port
    chosen by the operating system elsewhere) and return (process, port) once it listens."""
    port = env.get("IMPACT_DEV_DB_PORT") or (PGLITE_DEFAULT_PORT if mode == "dev" else "0")
    if not port.isdigit() or int(port) > 65535:
        raise RuntimeError("IMPACT_DEV_DB_PORT must be a port number, or 0 for one chosen by the system")
    log = local / "database.log"
    db = subprocess.Popen(
        ["node", "tools/dev-db/server.mjs"],
        cwd=ROOT,
        env={**env, "IMPACT_DEV_DB_PORT": port},
        stdout=open(log, "w"),
        stderr=subprocess.STDOUT,
    )
    for _ in range(240):
        status = database_status(log)
        if status and status["status"] == "ready" and isinstance(status.get("port"), int):
            return db, status["port"]
        if status or db.poll() is not None:
            break
        time.sleep(0.25)
    if db.poll() is None:
        db.terminate()
    db.wait()
    raise RuntimeError(
        (
            "Development database failed: " + str(status.get("error", status))
            if status
            else "Development database failed"
            if db.returncode
            else "Database startup timeout"
        )
        + "; see "
        + str(log)
    )


def preflight_fixture():
    stamped = json.loads((ROOT / "specification/fixtures/api-fixture.json").read_text()).get(
        "fixture_expires_at"
    )
    if not stamped:
        raise SystemExit(
            "api-fixture.json carries no fixture_expires_at stamp; regenerate the fixture with "
            + "scripts/redate_fixture.py rather than editing it, so that the stamp and "
            + "scripts/fixture_support.py agree."
        )
    if stamped != FIXTURE_EXPIRES_AT:
        raise SystemExit(
            "api-fixture.json says the fixture expires at "
            + stamped
            + " but scripts/fixture_support.py says "
            + FIXTURE_EXPIRES_AT
            + "; regenerate the fixture with scripts/redate_fixture.py rather than editing one of them."
        )
    days = fixture_days_remaining()
    if days < FIXTURE_PREFLIGHT_DAYS:
        raise SystemExit(
            "The synthetic fixture expires at "
            + FIXTURE_EXPIRES_AT
            + " ("
            + str(int(days))
            + " days away), inside the "
            + str(FIXTURE_PREFLIGHT_DAYS)
            + "-day margin: the suites nominate contacts, initial access and renewals that expire "
            + "up to 60 days from now, which the fixture's delegation ceilings must still cover. "
            + "Regenerate it with scripts/redate_fixture.py --expires <instant> and rerun the full "
            + "suites before continuing."
        )


def start_api(local, api_env, base):
    """Start uvicorn on the API environment and wait for readiness; returns (process, seconds)."""
    api_log = open(local / "api.log", "a")
    started = time.monotonic()
    api = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "impact_api.main:create_app",
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            str(os.environ.get("IMPACT_PORT", "8000")),
            "--no-access-log",
        ],
        cwd=ROOT,
        env=api_env,
        stdout=api_log,
        stderr=subprocess.STDOUT,
    )
    with httpx.Client(trust_env=False) as client:
        for _ in range(120):
            if api.poll() is not None:
                raise RuntimeError("API failed; see " + str(local / "api.log"))
            try:
                if client.get(base + "/health/ready", timeout=2).status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(0.25)
        else:
            api.kill()
            api.wait()
            raise RuntimeError("API startup timeout; see " + str(local / "api.log"))
    return api, round(time.monotonic() - started, 2)


def worker_environment(local, api_env):
    """The worker receives its own configuration file and nothing of the API's: no API
    configuration file, connection string, login DSN or libpq variable."""
    env = {
        k: v
        for k, v in api_env.items()
        if not k.startswith("IMPACT_") or k in {"IMPACT_ENVIRONMENT", "IMPACT_PORT"}
    }
    env.update(IMPACT_WORKER_CONFIG_FILE=str(local / "worker.json"), PYTHONPATH=str(ROOT / "apps/api"))
    return env


def start_worker(local, api_env):
    """One outbox worker process for the development stack; its log is .local/dev/worker.log."""
    return subprocess.Popen(
        [sys.executable, "-m", "impact_api.worker", "--worker-id", "dev-worker"],
        cwd=ROOT,
        env=worker_environment(local, api_env),
        stdout=open(local / "worker.log", "a"),
        stderr=subprocess.STDOUT,
    )


def stop_api(local, api):
    """Clean shutdown (SIGTERM, then SIGKILL after 10 s). Uvicorn re-raises the captured signal
    once its lifespan shutdown has completed, so the exit code is -15; the log line it writes
    last is the evidence that the shutdown ran. Returns (exit code, clean, seconds)."""
    started = time.monotonic()
    if api.poll() is None:
        api.terminate()
        try:
            api.wait(timeout=10)
        except subprocess.TimeoutExpired:
            api.kill()
            api.wait()
    clean = "Finished server process [" + str(api.pid) + "]" in (local / "api.log").read_text()
    return api.returncode, clean, round(time.monotonic() - started, 2)


def restart_phase(local, env, api, phase):
    """One phase of qualification/test_native_restart.py against the running API process."""
    junit = local / ("restart-phase-" + str(phase) + ".xml")
    started = time.monotonic()
    code = subprocess.call(
        [
            sys.executable,
            "-m",
            "pytest",
            "qualification/test_native_restart.py::test_phase_" + str(phase),
            "--junitxml=" + str(junit),
        ],
        cwd=ROOT,
        env={**env, "IMPACT_RESTART_PHASE": str(phase), "IMPACT_API_PID": str(api.pid)},
    )
    return {
        "api_pid": api.pid,
        "exit_code": code,
        "duration_seconds": round(time.monotonic() - started, 1),
        "junit": str(junit.relative_to(ROOT)),
        **junit_summary(junit),
    }


def restart_check(local, env, api_env, base, api):
    """Writes through the running API, a clean stop, a fresh process on the same database and
    configuration, then the assertions of phase 2. Returns (evidence, replacement process)."""
    result = {"phase_1": restart_phase(local, env, api, 1)}
    exit_code, clean, stop_seconds = stop_api(local, api)
    result["first_api"] = {
        "pid": api.pid,
        "exit_code": exit_code,
        "clean_shutdown": clean,
        "stop_seconds": stop_seconds,
    }
    replacement, ready_seconds = start_api(local, api_env, base)
    result["second_api"] = {"pid": replacement.pid, "ready_seconds": ready_seconds}
    result["phase_2"] = restart_phase(local, env, replacement, 2)
    state = local / "restart-state.json"
    result["state_file"] = str(state.relative_to(ROOT)) if state.exists() else None
    result["outcome"] = (
        "PASS"
        if all(
            result[phase]["exit_code"] == 0 and result[phase]["tests"] == 1 and not result[phase]["skipped"]
            for phase in ["phase_1", "phase_2"]
        )
        and clean
        and api.pid != replacement.pid
        else "FAIL"
    )
    return result, replacement


def junit_summary(path):
    root = ElementTree.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    return {
        "tests": sum(int(s.get("tests", 0)) for s in suites),
        "failures": sum(int(s.get("failures", 0)) for s in suites),
        "errors": sum(int(s.get("errors", 0)) for s in suites),
        "skipped": sum(int(s.get("skipped", 0)) for s in suites),
        "reported_seconds": round(sum(float(s.get("time", 0)) for s in suites), 3),
    }


def junit_cases(path):
    """Each test case of a JUnit file as {name, outcome, seconds}."""
    cases = []
    for case in ElementTree.parse(path).getroot().iter("testcase"):
        outcome = "passed"
        for tag in ["failure", "error", "skipped"]:
            if case.find(tag) is not None:
                outcome = {"failure": "failed", "error": "error", "skipped": "skipped"}[tag]
        cases.append({"name": case.get("name"), "outcome": outcome, "seconds": float(case.get("time", 0))})
    return cases


def write_idp_evidence(evidence, idp, targets, junit, code, seconds, native):
    """docs/evidence/idp-qualification.json: provider version and realm, then one entry per
    database under "runs" ("pglite" or "native", merged with an existing report so both runs of
    a gate are kept) with checks and timings; "database" names the latest run. It names no
    credential, secret or token; the issuer port is the one the operating system chose."""
    database = "native" if native else "pglite"
    report = ROOT / "docs/evidence/idp-qualification.json"
    try:
        existing = json.loads(report.read_text())
    except (OSError, ValueError):
        existing = {}
    run = {
        "database": database,
        **{
            k: evidence[k]
            for k in [
                "started_at",
                "api_ready_seconds",
                "engine",
                "server_version",
                "api_requires_unprivileged_db",
            ]
            if k in evidence
        },
        "finished_at": now(),
        "keycloak_ready_seconds": idp["ready_seconds"],
        "keycloak_imported_seconds": idp["imported_seconds"],
        "tests": {
            "junit": str(junit.relative_to(ROOT)),
            "targets": targets,
            "exit_code": code,
            "duration_seconds": round(seconds, 1),
            **junit_summary(junit),
        },
        "checks": junit_cases(junit),
    }
    result = {
        "identity_provider": {
            "product": "Keycloak",
            "version": idp["keycloak_version"],
            "distribution_sha256": idp["keycloak_sha256"],
            "realm": idp["realm"],
            "realm_source": "tools/idp/qualification-realm.json (derived from "
            + "specification/environment/keycloak-dev-realm.json)",
            "foreign_realm": idp["foreign_realm"],
            "client_id": idp["client_id"],
            "audience": idp["audience"],
            "required_acr": idp["required_acr"],
            "provider_database": "dev-mem (in-memory H2)",
        },
        "database": database,
        "runs": {**existing.get("runs", {}), database: run},
    }
    report.write_text(json.dumps(result, indent=2, default=str) + "\n")
    print("Identity-provider evidence: " + str(report.relative_to(ROOT)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["dev", "check", "test", *BROWSER_MODES])
    parser.add_argument(
        "--native", action="store_true", help="Use a separately provisioned disposable PostgreSQL database"
    )
    parser.add_argument(
        "--ephemeral", action="store_true", help="Use disposable memory storage for local development"
    )
    parser.add_argument(
        "--pytest-path",
        action="append",
        help="Run only this pytest file or node in test mode; repeat for multiple targets",
    )
    parser.add_argument(
        "--skip-upgrade-check",
        action="store_true",
        help="Native test mode: do not run scripts/native_upgrade_check.py after the suite",
    )
    parser.add_argument(
        "--skip-restart-check",
        action="store_true",
        help="Native test mode: do not restart the API between the two phases of test_native_restart.py",
    )
    parser.add_argument(
        "--skip-restore-drill",
        action="store_true",
        help="Native test mode: do not run scripts/restore_drill.py on the suite database afterwards",
    )
    parser.add_argument(
        "--no-worker", action="store_true", help="Dev mode: do not start the outbox worker process"
    )
    parser.add_argument(
        "--idp",
        choices=["keycloak"],
        help="Test or idp-browser mode: qualify against a live Keycloak instead of the development login",
    )
    args = parser.parse_args()
    if args.idp and (args.mode not in {"test", *IDP_ONLY_MODES} or (args.native and args.mode != "test")):
        parser.error("--idp keycloak is available in test mode (PGlite or --native) and idp-browser mode")
    if args.mode in IDP_ONLY_MODES and not args.idp:
        parser.error(args.mode + " needs --idp keycloak")
    preflight_fixture()
    local = ROOT / ".local" / ("dev" if args.mode == "dev" else "test-" + str(uuid.uuid4())[:8])
    local.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(
        IMPACT_ALLOW_FIXTURE_LOAD="1",
        IMPACT_ENVIRONMENT="development" if args.mode == "dev" else "test",
        IMPACT_DEV_DATA=str(local / "database"),
        IMPACT_DEV_EPHEMERAL="0" if args.mode == "dev" and not args.ephemeral else "1",
        PYTHONPATH=str(ROOT / "apps/api"),
        NO_PROXY="127.0.0.1,localhost",
        no_proxy="127.0.0.1,localhost",
    )
    services = []
    evidence = {"started_at": now()}
    keycloak = None

    def stop(*_):
        for p in reversed(services):
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    p.kill()
                    p.wait()

    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    try:
        idp_details = None
        db = None
        if args.native:
            if args.mode == "dev" or not env.get("IMPACT_FIXTURE_DSN"):
                raise RuntimeError("Native qualification requires a disposable test database DSN")
            fixture_dsn = env["IMPACT_FIXTURE_DSN"]
            admin_dsn = env.get("IMPACT_ADMIN_DSN") or fixture_dsn
            try:
                passwords = passwords_from_env(env)
            except RuntimeError:
                passwords = {login: secrets.token_urlsafe(24) for login in LOGINS}
            for login, (_, suffix) in LOGINS.items():
                env["IMPACT_LOGIN_PASSWORD_" + suffix] = passwords[login]
            topology = provision(admin_dsn, passwords, conninfo_to_dict(fixture_dsn).get("dbname"))
            dsns = {login: login_dsn(fixture_dsn, login, passwords[login]) for login in LOGINS}
            env.update(
                IMPACT_NATIVE_TEST="1",
                IMPACT_REQUIRE_UNPRIVILEGED_DB="1",
                IMPACT_ADMIN_DSN=admin_dsn,
                IMPACT_MIGRATION_DSN=dsns["impact_migrator"],
                IMPACT_APP_DSN=dsns["impact_app_login"],
                IMPACT_IDENTITY_DSN=dsns["impact_identity_login"],
                IMPACT_PLATFORM_DSN=dsns["impact_platform_login"],
                IMPACT_LOGIN_DSN_APP=dsns["impact_app_login"],
                IMPACT_LOGIN_DSN_IDENTITY=dsns["impact_identity_login"],
                IMPACT_LOGIN_DSN_PLATFORM=dsns["impact_platform_login"],
                IMPACT_LOGIN_DSN_MIGRATOR=dsns["impact_migrator"],
                IMPACT_LOGIN_DSN_WORKER=dsns["impact_worker_login"],
            )
            os.environ["IMPACT_ALLOW_FIXTURE_LOAD"] = "1"
            migration = migrate.run(env["IMPACT_MIGRATION_DSN"], fixture_dsn, fixture=True)
            with psycopg.connect(fixture_dsn, prepare_threshold=None) as c:
                server_version = c.execute("SELECT version()").fetchone()[0]
            evidence.update(
                engine="PostgreSQL",
                server_version=server_version,
                database=topology["database"],
                login_topology=topology,
                migration=migration,
                api_requires_unprivileged_db=True,
            )
        else:
            db, port = start_database(local, env, args.mode)
            services.append(db)
            # Every connection string, including the API's, derives from the port the server
            # reported: scripts/bootstrap.py reads IMPACT_FIXTURE_DSN and writes it into config.json.
            dsn = pglite_dsn(port)
            env.update(IMPACT_FIXTURE_DSN=dsn, IMPACT_MIGRATION_DSN=dsn)
            os.environ["IMPACT_ALLOW_FIXTURE_LOAD"] = "1"
            migrate.run(dsn, dsn, fixture=args.mode != "dev", fixture_if_empty=args.mode == "dev")
        if args.idp:
            keycloak, idp_details = identity_provider.start(
                local, "http://127.0.0.1:" + str(os.environ.get("IMPACT_PORT", "8000"))
            )
            env.update(IMPACT_IDP="keycloak", IMPACT_IDP_FILE=str(local / "idp.json"))
        os.environ.update({k: v for k, v in env.items() if k.startswith("IMPACT_")})
        config = bootstrap(local, idp_details)
        env["IMPACT_CONFIG_FILE"] = str(local / "config.json")
        # The API reads its three connection strings from config.json; it inherits neither the
        # privileged connections nor any libpq variable (PGPASSWORD, PGPASSFILE, PGSERVICE,
        # PGHOST, ...) that could add a credential or redirect a connection.
        api_env = {
            k: v
            for k, v in env.items()
            if k not in PRIVILEGED_ENV and not k.startswith("IMPACT_LOGIN_") and not k.startswith("PG")
        }
        base = config["public_origin"]
        (local / "api.log").write_text("")
        api, evidence["api_ready_seconds"] = start_api(local, api_env, base)
        services.append(api)
        # Suite-start tokens remain for the reference-v1 suite and the browser tooling; the
        # qualification suite mints its own per-actor tokens (qualification/conftest.py).
        fixture = json.loads((ROOT / "specification/fixtures/api-fixture.json").read_text())
        for actor in fixture["actors"].values() if not args.idp else []:
            env[actor["token_env"]] = jwt.encode(
                {
                    "iss": config["issuer"],
                    "sub": actor["identity_id"],
                    "aud": config["audience"],
                    "azp": config["client_id"],
                    "iat": int(time.time()),
                    "exp": int(time.time()) + 3600,
                    "auth_time": int(time.time()),
                },
                (local / "private.pem").read_bytes(),
                algorithm="RS256",
            )
        env.update(
            IMPACT_BASE_URL=base,
            IMPACT_FIXTURE_FILE=str(ROOT / "specification/fixtures/api-fixture.json"),
            IMPACT_ALLOW_MUTATIONS="1",
            IMPACT_TEST_LOCAL=str(local),
        )
        if args.native and not args.idp:
            with httpx.Client(trust_env=False) as client:
                manifest = client.get(
                    base + "/v1/runtime-manifest",
                    headers={"Authorization": "Bearer " + env[fixture["actors"]["author"]["token_env"]]},
                ).json()
            evidence["runtime_manifest"] = {
                k: manifest.get(k) for k in ["build_id", "schema_version", "api_version", "environment"]
            }
        print("Ready at " + base, flush=True)
        if args.mode == "dev":
            if not args.no_worker:
                services.append(start_worker(local, api_env))
            while api.poll() is None and db.poll() is None:
                time.sleep(1)
            raise RuntimeError("Development service stopped")
        if args.mode == "check":
            with httpx.Client(trust_env=False) as client:
                response = client.get(
                    base + "/v1/tenants/" + fixture["tenant_a"] + "/programmes",
                    headers={"Authorization": "Bearer " + env[fixture["actors"]["author"]["token_env"]]},
                )
                print("Programme API:", response.status_code, "items:", len(response.json().get("items", [])))
                if response.status_code != 200:
                    print(response.text)
                    return 1
            return 0
        if args.mode in BROWSER_MODES:
            return subprocess.call(["node", "tools/browser/" + BROWSER_MODES[args.mode]], cwd=ROOT, env=env)
        targets = args.pytest_path or (
            ["qualification/test_live_idp.py"]
            if args.idp
            else [
                "qualification",
                "specification/reference-v1/tests/test_smoke.py",
                "specification/reference-v1/tests/test_integration.py",
            ]
        )
        junit = (
            ROOT
            / "docs/evidence"
            / (
                ("idp-native-tests.xml" if args.native else "idp-tests.xml")
                if args.idp
                else "native-application-tests.xml"
                if args.native
                else "application-tests.xml"
            )
        )
        started = time.monotonic()
        code = subprocess.call(
            [sys.executable, "-m", "pytest", *targets, "-k", "not IT_018", "--junitxml=" + str(junit)],
            cwd=ROOT,
            env=env,
        )
        if args.idp:
            write_idp_evidence(
                evidence, idp_details, targets, junit, code, time.monotonic() - started, args.native
            )
            return code
        if not args.native:
            return code
        evidence["tests"] = {
            "junit": "docs/evidence/native-application-tests.xml",
            "targets": targets,
            "exit_code": code,
            "duration_seconds": round(time.monotonic() - started, 1),
            **junit_summary(junit),
        }
        winners = local / "renewal-race-winners.json"
        if winners.exists():
            # Observed order of each renewal-versus-revocation race (test_native_concurrency.py).
            evidence["tests"]["renewal_race_winners"] = json.loads(winners.read_text())
        if not args.skip_restart_check:
            evidence["restart_check"], api = restart_check(local, env, api_env, base, api)
            services.append(api)
            code = code or (0 if evidence["restart_check"]["outcome"] == "PASS" else 1)
        stop()
        evidence["finished_at"] = now()
        report = ROOT / "docs/evidence/native-qualification.json"
        report.write_text(json.dumps(evidence, indent=2, default=str) + "\n")
        if not args.skip_restore_drill:
            # The drill dumps the database the suite just used, restores it beside it and merges
            # its result into the report; the API is already stopped.
            drill = subprocess.call(
                [sys.executable, "scripts/restore_drill.py", "--report", str(report)], cwd=ROOT, env=env
            )
            code = code or drill
        if not args.skip_upgrade_check:
            # The upgrade check runs on its own fresh database and merges its result into the report.
            upgrade = subprocess.call(
                [sys.executable, "scripts/native_upgrade_check.py", "--report", str(report)],
                cwd=ROOT,
                env=env,
            )
            code = code or upgrade
        print("Native evidence: " + str(report))
        return code
    finally:
        stop()
        if keycloak is not None:
            identity_provider.stop(keycloak)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
