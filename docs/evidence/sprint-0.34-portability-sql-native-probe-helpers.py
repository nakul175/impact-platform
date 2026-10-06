"""Prepared native probes only; not executed or registered as qualification.

Use actual runtime logins supplied by the coordinated native runner. Trusted
fixture-superuser storage seeding is a distinct, labelled step outside these
probes. Never print DSNs, environment values or connection exception messages.
"""

from contextlib import contextmanager
import os

import psycopg
from psycopg import sql
from psycopg.errors import InsufficientPrivilege

LOGINS = {
    'APP': ('impact_app_login', 'impact_app'),
    'EXECUTOR': ('impact_executor_login', 'impact_app'),
    'WORKER': ('impact_worker_login', 'impact_worker'),
    'IDENTITY': ('impact_identity_login', 'impact_identity'),
    'PLATFORM': ('impact_platform_login', 'impact_platform'),
}

POINTER_QUERIES = {
    'issuance': 'SELECT count(*) FROM impact.ai_plan_export_issuance WHERE tenant_id=%s AND issuance_id=%s',
    'bytes': 'SELECT count(*) FROM impact.ai_plan_export_bytes WHERE tenant_id=%s AND issuance_id=%s',
    'registry': 'SELECT count(*) FROM impact.object_registry WHERE tenant_id=%s AND object_id=%s',
    'revision': 'SELECT count(*) FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s',
    'audit': 'SELECT count(*) FROM impact.audit_event_current WHERE tenant_id=%s AND object_id=%s',
    'author': 'SELECT count(*) FROM impact.object_natural_author WHERE tenant_id=%s AND object_id=%s',
    'receipt': "SELECT count(*) FROM impact.operation_receipt WHERE tenant_id=%s AND command_type='issue_ai_plan_export' AND outcome->>'object_id'=%s",
    'event': 'SELECT count(*) FROM impact.outbox_event WHERE tenant_id=%s AND event_id=%s',
    'delivery': 'SELECT count(*) FROM impact.outbox_delivery WHERE tenant_id=%s AND event_id=%s',
    'consumer': 'SELECT count(*) FROM impact.consumer_receipt WHERE tenant_id=%s AND event_id=%s',
}


@contextmanager
def native_connection(login_name):
    if os.environ.get('IMPACT_NATIVE_TEST') != '1':
        raise RuntimeError('Actual native qualification context required')
    expected_login, _ = LOGINS[login_name]
    dsn = os.environ.get('IMPACT_LOGIN_DSN_' + login_name)
    if not dsn:
        raise RuntimeError('Required native login DSN unavailable')
    # No fallback to the fixture superuser and no password generation or rotation.
    with psycopg.connect(dsn, autocommit=True, prepare_threshold=None) as connection:
        if connection.execute('SELECT session_user').fetchone()[0] != expected_login:
            raise RuntimeError('Native login selector mismatch')
        yield connection


@contextmanager
def runtime_context(connection, login_name, tenant, principal=None):
    _, runtime_role = LOGINS[login_name]
    with connection.transaction():
        connection.execute(sql.SQL('SET LOCAL ROLE {}').format(sql.Identifier(runtime_role)))
        connection.execute("SET LOCAL statement_timeout='8s'")
        connection.execute("SELECT set_config('impact.tenant_id',%s,true)", (str(tenant),))
        if principal is not None:
            connection.execute("SELECT set_config('impact.ai_plan_export_principal',%s,true)", (str(principal),))
        yield connection


def pointer_observations(connection, tenant, issuance_id, event_id):
    observations = {}
    for label, query in POINTER_QUERIES.items():
        target = event_id if label in {'event', 'delivery', 'consumer'} else issuance_id
        try:
            with connection.transaction():
                count = connection.execute(query, (str(tenant), str(target))).fetchone()[0]
        except InsufficientPrivilege:
            observations[label] = {'access': 'TABLE_PRIVILEGE_DENIED'}
        else:
            observations[label] = {'access': 'ROWS', 'count': count}
    return observations


def assert_pointers_hidden(observations):
    assert all(value == {'access': 'TABLE_PRIVILEGE_DENIED'} or value == {'access': 'ROWS', 'count': 0}
               for value in observations.values()), observations


def assert_context_cleared(connection):
    settings = connection.execute("SELECT current_setting('impact.ai_plan_export_principal',true),current_setting('role',true)").fetchone()
    assert settings[0] in (None, '')
    assert settings[1] in (None, '', 'none')
