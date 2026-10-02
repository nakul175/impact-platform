"""Static guards for transaction-pooling compatibility (QA 2026-10 non-functional). A PgBouncer in
transaction mode hands a client a different server connection for every transaction, so anything
the runtime keeps on the session breaks there: server-side prepared statements (psycopg prepares
after `prepare_threshold` executions), session-level SET, session advisory locks and LISTEN. The
live qualification runs behind a real pooler (`scripts/run.py test --native --pooler pgbouncer`,
`qualification/test_native_nonfunctional.py`); these checks keep the properties it relies on from
regressing in every suite, without a database."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = sorted((ROOT / "apps/api/impact_api").glob("*.py"))
CONNECT = re.compile(r"psycopg\.connect\((?P<call>.*?)\)\s*(?:as|\n|$)", re.S)


def runtime_sources():
    return {path.name: path.read_text() for path in RUNTIME}


def test_every_runtime_connection_disables_server_side_prepared_statements():
    """Every psycopg.connect(...) in the API and worker passes prepare_threshold=None: under
    transaction pooling a statement prepared on one server connection does not exist on the next."""
    seen = 0
    for name, source in runtime_sources().items():
        for match in re.finditer(r"psycopg\.connect\(", source):
            seen += 1
            depth, index = 0, match.end() - 1
            while True:  # the matching parenthesis of this call
                char = source[index]
                depth += char == "("
                depth -= char == ")"
                index += 1
                if depth == 0:
                    break
            call = source[match.start() : index]
            assert "prepare_threshold=None" in call, (name, call)
    assert seen >= 3, "store.py (two) and worker.py connect with psycopg"


def test_runtime_sql_keeps_no_session_state():
    """No session-level SET (only SET LOCAL and transaction-local set_config), no session advisory
    lock (only pg_advisory_xact_lock) and no LISTEN/NOTIFY in the runtime's SQL."""
    for name, source in runtime_sources().items():
        for line_number, line in enumerate(source.splitlines(), 1):
            sql = line.strip()
            if not (sql.startswith(('"', "'", "c.execute", "connection.execute")) or "execute(" in sql):
                continue
            # A session SET is a statement that starts with SET (never SET LOCAL); an UPDATE's SET
            # clause is not one.
            assert not re.search(r"""(^|["'(])\s*SET\s+(?!LOCAL\b)[A-Za-z_.]+\s*(=|TO\b)""", sql), (
                name,
                line_number,
                line,
            )
            assert not re.search(r"set_config\([^)]*,\s*false\)", sql), (name, line_number, line)
            assert "pg_advisory_lock(" not in sql and "pg_try_advisory_lock(" not in sql, (name, line_number)
            assert not re.search(r"\b(LISTEN|NOTIFY|UNLISTEN)\b", sql), (name, line_number, line)
