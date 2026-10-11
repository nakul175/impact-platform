"""Connection selection and exact attribute preservation; no database/runtime proof."""

import os

from psycopg.conninfo import conninfo_to_dict, make_conninfo
import pytest

from clone_connections import CloneConnectionError, ROLES, clone_login_dsn


@pytest.fixture(autouse=True)
def isolated_configuration(monkeypatch):
    for key in list(os.environ):
        if key.startswith(("IMPACT_LOGIN_DSN_", "IMPACT_DIRECT_LOGIN_DSN_")) or key in {
            "IMPACT_DB_POOLER",
            "IMPACT_FIXTURE_DSN",
            "IMPACT_MIGRATION_DSN",
        }:
            monkeypatch.delenv(key)


def restricted(role, **overrides):
    return make_conninfo(
        **{
            "user": "impact_" + role.lower() + "_login",
            "password": "synthetic spaces ' quote \\ slash",
            "host": "127.0.0.1",
            "port": "55433",
            "dbname": "impact_test_source",
            "sslmode": "verify-full",
            "sslrootcert": "/synthetic/ca with spaces.pem",
            "connect_timeout": "8",
            "application_name": "synthetic clone qualification",
            **overrides,
        }
    )


@pytest.mark.parametrize("role", sorted(ROLES))
def test_nonpooler_legacy_connection_changes_only_database(monkeypatch, role):
    original = restricted(role)
    monkeypatch.setenv("IMPACT_LOGIN_DSN_" + role, original)
    assert conninfo_to_dict(clone_login_dsn(role, "impact_test_copy")) == {
        **conninfo_to_dict(original),
        "dbname": "impact_test_copy",
    }
    assert os.environ["IMPACT_LOGIN_DSN_" + role] == original


@pytest.mark.parametrize("role", sorted(ROLES))
def test_pooler_uses_explicit_direct_role_without_mutating_runtime(monkeypatch, role):
    runtime = restricted(role, port="6432", sslmode="disable")
    direct = restricted(role)
    monkeypatch.setenv("IMPACT_DB_POOLER", "pgbouncer")
    monkeypatch.setenv("IMPACT_LOGIN_DSN_" + role, runtime)
    monkeypatch.setenv("IMPACT_DIRECT_LOGIN_DSN_" + role, direct)
    before = dict(os.environ)
    assert conninfo_to_dict(clone_login_dsn(role, "impact_test_restored")) == {
        **conninfo_to_dict(direct),
        "dbname": "impact_test_restored",
    }
    assert dict(os.environ) == before


@pytest.mark.parametrize("pooler", ["pgbouncer", ""])
def test_pooler_missing_direct_connection_refuses_privileged_or_pooled_fallback(monkeypatch, pooler):
    monkeypatch.setenv("IMPACT_DB_POOLER", pooler)
    for key in [
        "IMPACT_LOGIN_DSN_APP",
        "IMPACT_LOGIN_DSN_MIGRATOR",
        "IMPACT_MIGRATION_DSN",
        "IMPACT_FIXTURE_DSN",
    ]:
        monkeypatch.setenv(key, "postgresql://synthetic:private-value@localhost/source")
    with pytest.raises(CloneConnectionError) as error:
        clone_login_dsn("APP", "copy")
    assert str(error.value) == "Restricted clone connection configuration missing"
    assert "private-value" not in str(error.value)


def test_nonpooler_direct_preferred_and_privileged_only_configuration_refused(monkeypatch):
    monkeypatch.setenv("IMPACT_DIRECT_LOGIN_DSN_APP", restricted("APP"))
    monkeypatch.setenv("IMPACT_LOGIN_DSN_APP", restricted("APP", port="6432"))
    assert conninfo_to_dict(clone_login_dsn("APP", "copy"))["port"] == "55433"
    monkeypatch.delenv("IMPACT_DIRECT_LOGIN_DSN_APP")
    monkeypatch.delenv("IMPACT_LOGIN_DSN_APP")
    monkeypatch.setenv("IMPACT_FIXTURE_DSN", restricted("APP", user="postgres"))
    monkeypatch.setenv("IMPACT_MIGRATION_DSN", restricted("APP", user="impact_migrator"))
    with pytest.raises(CloneConnectionError, match="configuration missing"):
        clone_login_dsn("APP", "copy")


@pytest.mark.parametrize("role", ["MIGRATOR", "FIXTURE", "OWNER", "postgres", "app", None, []])
def test_privileged_unknown_or_invalid_role_refused(role):
    with pytest.raises(CloneConnectionError, match="Restricted clone role required"):
        clone_login_dsn(role, "copy")


@pytest.mark.parametrize("target", [None, "", "  ", []])
def test_invalid_database_selector_refused(target):
    with pytest.raises(CloneConnectionError, match="Clone database selector required"):
        clone_login_dsn("APP", target)


def test_invalid_connection_parser_error_redacted(monkeypatch):
    monkeypatch.setenv("IMPACT_LOGIN_DSN_APP", "private-password-value not valid connection text")
    with pytest.raises(CloneConnectionError) as error:
        clone_login_dsn("APP", "copy")
    assert str(error.value) == "Restricted clone connection configuration invalid"
    assert "private-password-value" not in str(error.value)
    assert error.value.__cause__ is None and error.value.__suppress_context__
