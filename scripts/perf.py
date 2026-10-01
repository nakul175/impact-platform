#!/usr/bin/env python3
"""Reproducible performance measurement (QA 2026-10): `make perf`.

Needs IMPACT_FIXTURE_DSN (superuser) to a disposable database named impact_test or impact_test_<x>,
exactly as `scripts/run.py test --native`; `--recreate` drops and creates that database first. The
run provisions the login roles, migrates, starts the API on the provisioned logins with
IMPACT_REQUIRE_UNPRIVILEGED_DB=1 and runs qualification/perf_harness.py, which seeds the synthetic
workload through the API and measures it. Raw numbers go to docs/evidence/performance-<date>.json
and a summary table to the same name with .md. Nothing is optimised or asserted against targets:
the verdicts are computed and written, never enforced."""

import argparse
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import psycopg
from psycopg.conninfo import conninfo_to_dict, make_conninfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "qualification"))
from perf_support import SCALES, markdown, workload  # noqa: E402


def recreate(dsn):
    name = conninfo_to_dict(dsn).get("dbname") or ""
    if not (name == "impact_test" or name.startswith("impact_test_")):
        raise SystemExit("Refusing to recreate a database not named impact_test or impact_test_<x>: " + name)
    with psycopg.connect(make_conninfo(dsn, dbname="postgres"), autocommit=True) as c:
        c.execute(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')
        c.execute(f"CREATE DATABASE \"{name}\" ENCODING 'UTF8' TEMPLATE template0")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", choices=sorted(SCALES), default="sandbox")
    parser.add_argument("--seed", type=int, default=20261001)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--recreate", action="store_true", help="Drop and create the fixture database first")
    parser.add_argument("--output", help="JSON path (default docs/evidence/performance-<date>.json)")
    args = parser.parse_args()
    workload(args.scale, args.seed, args.concurrency)  # validates the arguments
    dsn = os.environ.get("IMPACT_FIXTURE_DSN")
    if not dsn:
        raise SystemExit("Set IMPACT_FIXTURE_DSN to an empty disposable impact_test_<x> database (superuser)")
    if args.recreate:
        recreate(dsn)
    output = Path(
        args.output or ROOT / "docs/evidence" / ("performance-" + date.today().isoformat() + ".json")
    )
    output = output.resolve()
    env = os.environ.copy()
    env.update(
        IMPACT_PERF="1",
        IMPACT_PERF_SCALE=args.scale,
        IMPACT_PERF_SEED=str(args.seed),
        IMPACT_PERF_CONCURRENCY=str(args.concurrency),
        IMPACT_PERF_OUTPUT=str(output),
    )
    code = subprocess.call(
        [
            sys.executable,
            "scripts/run.py",
            "test",
            "--native",
            "--perf",
            "--pytest-path",
            "qualification/perf_harness.py",
            "--skip-restart-check",
            "--skip-restore-drill",
            "--skip-upgrade-check",
        ],
        cwd=ROOT,
        env=env,
    )
    if output.exists():
        report = json.loads(output.read_text())
        summary = output.with_suffix(".md")
        summary.write_text(markdown(report))
        print(summary.read_text())
    else:
        print("No report written", file=sys.stderr)
        code = code or 1
    return code


if __name__ == "__main__":
    sys.exit(main())
