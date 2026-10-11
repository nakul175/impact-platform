"""Read-only pre-migration check; never terminates sessions or changes accounts.

Stopping the Compose writers is necessary but does not exclude another operator/client.
Refuse any other application-database client or prepared transaction. The operator must
keep external writers disconnected throughout the maintenance window.
"""

import json
import os
import sys

import psycopg


class QuiescenceError(RuntimeError):
    pass


def check(admin_dsn):
    if not admin_dsn:
        raise QuiescenceError("Missing administrator connection configuration")
    with psycopg.connect(admin_dsn, connect_timeout=10, prepare_threshold=None) as connection:
        with connection.transaction():
            connection.execute("SET TRANSACTION READ ONLY")
            if not connection.execute("SELECT current_setting('is_superuser') = 'on'").fetchone()[0]:
                raise QuiescenceError("Complete session visibility requires the existing administrator")
            sessions = connection.execute(
                "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database() "
                "AND pid <> pg_backend_pid() AND backend_type = 'client backend'"
            ).fetchone()[0]
            prepared = connection.execute(
                "SELECT count(*) FROM pg_prepared_xacts WHERE database = current_database()"
            ).fetchone()[0]
            exists = connection.execute("SELECT to_regclass('impact.schema_migration')").fetchone()[0]
            schema = (
                connection.execute(
                    "SELECT coalesce(max(version), 0) FROM impact.schema_migration"
                ).fetchone()[0]
                if exists
                else 0
            )
            if sessions or prepared:
                raise QuiescenceError(
                    f"Migration refused: {sessions} other client sessions, {prepared} prepared transactions"
                )
            return {"other_client_sessions": 0, "prepared_transactions": 0, "schema_before": schema}


def main():
    try:
        result = check(os.environ.get("IMPACT_ADMIN_DSN"))
    except QuiescenceError as error:
        print(str(error), file=sys.stderr)
        return 1
    except Exception:
        # Driver/connection errors may contain connection details: fail closed without printing them.
        print("Writer quiescence probe failed; migration remains blocked", file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
