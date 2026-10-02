"""The single version source: VERSION.json at the repository root plus the migration count.

Build, domain API, platform API and documentation edition are read from VERSION.json. The schema
version is never a literal: it is the number of migration files, which scripts/migrate.py applies
in order and checksum-ledgers (LATEST there uses the same rule), so adding a migration needs no
version edit. qualification/test_version_unit.py keeps the migration numbering contiguous (so the
count equals the highest applied version) and apps/web/package.json equal to the build.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MIGRATIONS = ROOT / "infrastructure/migrations"
_SOURCE = json.loads((ROOT / "VERSION.json").read_text())

BUILD = _SOURCE["build"]
DOMAIN_API = _SOURCE["domain_api"]
PLATFORM_API = _SOURCE["platform_api"]
DOCUMENTATION_EDITION = _SOURCE["documentation_edition"]


def schema_version(directory=MIGRATIONS):
    """Expected schema version: the number of migration files (0001_… to NNNN_…)."""
    return len(list(Path(directory).glob("*.sql")))


SCHEMA = schema_version()
