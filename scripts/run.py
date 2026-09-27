"""Single process tree keeps local services reachable in sandboxed workspaces."""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path

import httpx
import jwt
from bootstrap import bootstrap

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        choices=[
            "dev",
            "check",
            "test",
            "browser",
            "admin-browser",
            "measurement-browser",
            "reporting-browser",
            "workspace-browser",
            "tenant-browser",
            "bootstrap-browser",
            "recovery-browser",
        ],
    )
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
    args = parser.parse_args()
    local = ROOT / ".local" / ("dev" if args.mode == "dev" else "test-" + str(uuid.uuid4())[:8])
    local.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(
        IMPACT_DEV_BOOTSTRAP="1",
        IMPACT_ALLOW_FIXTURE_LOAD="1",
        IMPACT_ENVIRONMENT="development" if args.mode == "dev" else "test",
        IMPACT_DEV_DATA=str(local / "database"),
        IMPACT_DEV_EPHEMERAL="0" if args.mode == "dev" and not args.ephemeral else "1",
        PYTHONPATH=str(ROOT / "apps/api"),
        NO_PROXY="127.0.0.1,localhost",
        no_proxy="127.0.0.1,localhost",
    )
    services = []

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
            env["IMPACT_NATIVE_TEST"] = "1"
            subprocess.run([sys.executable, "scripts/migrate.py", "--fixture"], env=env, cwd=ROOT, check=True)
        else:
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
        os.environ.update({k: v for k, v in env.items() if k.startswith("IMPACT_")})
        config = bootstrap(local)
        env["IMPACT_CONFIG_FILE"] = str(local / "config.json")
        api_log = open(local / "api.log", "w")
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
            env=env,
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
        if args.mode == "browser":
            return subprocess.call(["node", "tools/browser/check.mjs"], cwd=ROOT, env=env)
        if args.mode == "admin-browser":
            return subprocess.call(["node", "tools/browser/admin-check.mjs"], cwd=ROOT, env=env)
        if args.mode == "measurement-browser":
            return subprocess.call(["node", "tools/browser/measurement-check.mjs"], cwd=ROOT, env=env)
        if args.mode == "reporting-browser":
            return subprocess.call(["node", "tools/browser/reporting-check.mjs"], cwd=ROOT, env=env)
        if args.mode == "workspace-browser":
            return subprocess.call(["node", "tools/browser/workspace-check.mjs"], cwd=ROOT, env=env)
        if args.mode == "tenant-browser":
            return subprocess.call(["node", "tools/browser/tenant-check.mjs"], cwd=ROOT, env=env)
        if args.mode == "bootstrap-browser":
            return subprocess.call(["node", "tools/browser/bootstrap-check.mjs"], cwd=ROOT, env=env)
        if args.mode == "recovery-browser":
            return subprocess.call(["node", "tools/browser/recovery-check.mjs"], cwd=ROOT, env=env)
        targets = args.pytest_path or [
            "qualification",
            "specification/reference-v1/tests/test_smoke.py",
            "specification/reference-v1/tests/test_integration.py",
        ]
        return subprocess.call(
            [
                sys.executable,
                "-m",
                "pytest",
                *targets,
                "-k",
                "not IT_018",
                "--junitxml=" + str(ROOT / "docs/evidence/application-tests.xml"),
            ],
            cwd=ROOT,
            env=env,
        )
    finally:
        stop()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
