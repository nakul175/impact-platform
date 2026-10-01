"""The single version source (VERSION.json + migration count) and everything that must agree with it."""

import json
import re
from pathlib import Path

from impact_api import version

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def test_version_source_is_complete_and_well_formed():
    source = json.loads((ROOT / "VERSION.json").read_text())
    assert {"build", "domain_api", "platform_api", "documentation_edition"} <= set(source)
    for key in ["build", "domain_api", "platform_api"]:
        assert SEMVER.match(source[key]), key
    assert (version.BUILD, version.DOMAIN_API, version.PLATFORM_API) == (
        source["build"],
        source["domain_api"],
        source["platform_api"],
    )


def test_migrations_are_numbered_contiguously_so_their_count_is_the_schema_version():
    names = sorted(p.name for p in (ROOT / "infrastructure/migrations").glob("*.sql"))
    numbers = [int(name.split("_", 1)[0]) for name in names]
    assert numbers == list(range(1, len(names) + 1)), names
    assert all(re.match(r"^\d{4}_[a-z0-9_]+\.sql$", name) for name in names), names
    assert version.SCHEMA == len(names) == numbers[-1]


def test_web_client_package_matches_the_build():
    package = json.loads((ROOT / "apps/web/package.json").read_text())
    lock = json.loads((ROOT / "apps/web/package-lock.json").read_text())
    assert package["version"] == version.BUILD
    assert lock["version"] == lock["packages"][""]["version"] == version.BUILD


def test_generated_contracts_carry_the_source_versions():
    """Fails when VERSION.json moved but `scripts/build_contracts.py` was not re-run."""
    contracts = ROOT / "packages/contracts"
    for name in ["openapi.json", "openapi-implemented.json"]:
        assert json.loads((contracts / name).read_text())["info"]["version"] == version.DOMAIN_API, name
    assert json.loads((contracts / "access-policy.json").read_text())["version"] == version.DOMAIN_API
    platform = json.loads((contracts / "openapi-platform.json").read_text())
    assert platform["info"]["version"] == version.PLATFORM_API


def test_runtime_code_carries_no_version_literal():
    """Build, published API and schema versions come from impact_api.version, never literals.

    The per-feature *_contracts.py modules keep the API version that introduced each route
    (x-contract-version, VERSION); scripts/build_contracts.py overwrites the published version.
    """
    offenders = [
        path.name
        for path in sorted((ROOT / "apps/api/impact_api").glob("*.py"))
        if '"' + version.BUILD + '"' in path.read_text()
    ]
    assert not offenders, offenders
    platform = (ROOT / "apps/api/impact_api/tenant_contracts.py").read_text()
    assert '"version": PLATFORM_API' in platform and '"' + version.PLATFORM_API + '"' not in platform
    main = (ROOT / "apps/api/impact_api/main.py").read_text()
    assert "version != SCHEMA" in main and not re.search(r"version != \d+", main)
    for script in [
        "scripts/build_contracts.py",
        "scripts/build_completion_ledger.py",
        "scripts/package_source.py",
    ]:
        text = (ROOT / script).read_text()
        assert '"' + version.BUILD + '"' not in text and "-v" + version.BUILD not in text, script
