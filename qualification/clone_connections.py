"""Restricted restored-copy connections; never route copied databases through a pooler."""

import os

from psycopg.conninfo import make_conninfo

ROLES = frozenset({"APP", "IDENTITY", "PLATFORM", "WORKER", "EXECUTOR"})


class CloneConnectionError(ValueError):
    """Safe configuration refusal without connection details."""


def clone_login_dsn(role, target):
    """Preserve an explicit restricted connection, replacing only its database selector.

    Pooler runtime connections name only their configured source database. Clone
    qualification must use the separately retained direct restricted connection.
    Neither administrator nor migration connections are a permitted fallback.
    """
    if not isinstance(role, str) or role not in ROLES:
        raise CloneConnectionError("Restricted clone role required")
    if not isinstance(target, str) or not target.strip():
        raise CloneConnectionError("Clone database selector required")
    direct = os.environ.get("IMPACT_DIRECT_LOGIN_DSN_" + role)
    if "IMPACT_DB_POOLER" in os.environ:
        source = direct
    else:
        source = direct or os.environ.get("IMPACT_LOGIN_DSN_" + role)
    if not source or not source.strip():
        raise CloneConnectionError("Restricted clone connection configuration missing")
    try:
        return make_conninfo(source, dbname=target)
    except Exception:
        # Parsing errors can include passwords or other original DSN text.
        raise CloneConnectionError("Restricted clone connection configuration invalid") from None
