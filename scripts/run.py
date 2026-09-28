"""Single process tree keeps local services reachable in sandboxed workspaces.

PGlite modes (dev, test, browser checks) start tools/dev-db/server.mjs, which only serves the
database; scripts/migrate.py then applies the migrations and the fixture over the wire exactly as
it does on native PostgreSQL. Native mode (--native) provisions the four login roles on the
disposable server named by IMPACT_FIXTURE_DSN, migrates as impact_migrator, loads the fixture as
the superuser, and starts the API on the app, identity and platform logins only: the API process
never receives the fixture, migration or administrator connection.
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

ROOT = Path(__file__).resolve().parents[1]
PGLITE_DSN = "postgresql://postgres:development@127.0.0.1:55432/impact_dev?sslmode=disable"
# Never handed to the API process: fixture, migration and administrator connections and passwords.
PRIVILEGED_ENV = {"IMPACT_FIXTURE_DSN", "IMPACT_MIGRATION_DSN", "IMPACT_ADMIN_DSN"}
BROWSER_MODES = {
    "browser": "check.mjs",
    "admin-browser": "admin-check.mjs",
    "measurement-browser": "measurement-check.mjs",
    "reporting-browser": "reporting-check.mjs",
    "workspace-browser": "workspace-check.mjs",
    "tenant-browser": "tenant-check.mjs",
    "bootstrap-browser": "bootstrap-check.mjs",
    "recovery-browser": "recovery-check.mjs",
    "renewal-browser": "renewal-check.mjs",
}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def preflight_fixture():
    stamped = json.loads((ROOT / "specification/fixtures/api-fixture.json").read_text()).get(
        "fixture_expires_at"
    )
    if stamped and stamped != FIXTURE_EXPIRES_AT:
        raise SystemExit(
            "api-fixture.json says the fixture expires at "
            + stamped
            + " but scripts/fixture_support.py says "
            + FIXTURE_EXPIRES_AT
            + "; regenerate the fixture with scripts/redate_fixture.py rather than editing one of them."
        )
    days = fixture_days_remaining()
    if days < 30:
        raise SystemExit(
            "The synthetic fixture expires at "
            + FIXTURE_EXPIRES_AT
            + " ("
            + str(int(days))
            + " days away). Regenerate it with scripts/redate_fixture.py --expires <instant> "
            + "and rerun the full suites before continuing."
        )


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
    args = parser.parse_args()
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
            env.update(IMPACT_FIXTURE_DSN=PGLITE_DSN, IMPACT_MIGRATION_DSN=PGLITE_DSN)
            db_log = open(local / "database.log", "w")
            db = subprocess.Popen(
                ["node", "tools/dev-db/server.mjs"],
                cwd=ROOT,
                env=env,
                stdout=db_log,
                stderr=subprocess.STDOUT,
            )
            services.append(db)
            for _ in range(240):
                if db.poll() is not None:
                    raise RuntimeError("Development database failed; see " + str(local / "database.log"))
                if "ready" in (local / "database.log").read_text():
                    break
                time.sleep(0.25)
            else:
                raise RuntimeError("Database startup timeout")
            os.environ["IMPACT_ALLOW_FIXTURE_LOAD"] = "1"
            migrate.run(
                PGLITE_DSN,
                PGLITE_DSN,
                fixture=args.mode != "dev",
                fixture_if_empty=args.mode == "dev",
            )
        os.environ.update({k: v for k, v in env.items() if k.startswith("IMPACT_")})
        config = bootstrap(local)
        env["IMPACT_CONFIG_FILE"] = str(local / "config.json")
        api_env = {
            k: v for k, v in env.items() if k not in PRIVILEGED_ENV and not k.startswith("IMPACT_LOGIN_")
        }
        api_log = open(local / "api.log", "w")
        api_started = time.monotonic()
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
        services.append(api)
        base = config["public_origin"]
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
                raise RuntimeError("API startup timeout; see " + str(local / "api.log"))
        evidence["api_ready_seconds"] = round(time.monotonic() - api_started, 2)
        # Suite-start tokens remain for the reference-v1 suite and the browser tooling; the
        # qualification suite mints its own per-actor tokens (qualification/conftest.py).
        fixture = json.loads((ROOT / "specification/fixtures/api-fixture.json").read_text())
        for actor in fixture["actors"].values():
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
        if args.native:
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
        targets = args.pytest_path or [
            "qualification",
            "specification/reference-v1/tests/test_smoke.py",
            "specification/reference-v1/tests/test_integration.py",
        ]
        junit = (
            ROOT
            / "docs/evidence"
            / ("native-application-tests.xml" if args.native else "application-tests.xml")
        )
        started = time.monotonic()
        code = subprocess.call(
            [sys.executable, "-m", "pytest", *targets, "-k", "not IT_018", "--junitxml=" + str(junit)],
            cwd=ROOT,
            env=env,
        )
        if not args.native:
            return code
        evidence["tests"] = {
            "junit": "docs/evidence/native-application-tests.xml",
            "targets": targets,
            "exit_code": code,
            "duration_seconds": round(time.monotonic() - started, 1),
            **junit_summary(junit),
        }
        stop()
        evidence["finished_at"] = now()
        report = ROOT / "docs/evidence/native-qualification.json"
        report.write_text(json.dumps(evidence, indent=2, default=str) + "\n")
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


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
