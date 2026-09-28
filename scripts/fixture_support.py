"""Shared constants for the synthetic acceptance fixture. Not a runtime module.

Every fixture grant, delegation ceiling, role assignment, platform operator and deployment
qualification expires at FIXTURE_EXPIRES_AT. `scripts/redate_fixture.py` moves that instant and
rewrites `specification/fixtures/` together with this constant; nothing extends it silently.
"""

import re
from datetime import datetime, timezone

FIXTURE_EXPIRES_AT = "2027-09-01T00:00:00Z"
FIXTURE_STARTS_AT = "2026-01-01T00:00:00Z"

# Disposable fixture targets: the two fixed development/test names plus parallel test databases.
FIXTURE_DATABASES = {"impact_dev", "impact_test"}
FIXTURE_DATABASE_PATTERN = re.compile(r"^impact_test_[a-z0-9_]+$")


def fixture_database_allowed(name):
    return name in FIXTURE_DATABASES or bool(FIXTURE_DATABASE_PATTERN.fullmatch(name or ""))


def fixture_expires_at():
    return datetime.strptime(FIXTURE_EXPIRES_AT, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def fixture_days_remaining(now=None):
    now = now or datetime.now(timezone.utc)
    return (fixture_expires_at() - now).total_seconds() / 86400
