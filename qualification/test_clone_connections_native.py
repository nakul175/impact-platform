"""Actual process isolation and runtime topology for clone-only restricted connections."""

import os

from psycopg.conninfo import conninfo_to_dict
import pytest

from test_native_restart import assert_api_process_holds_no_privileged_connection

pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1", reason="Actual native API process required"
)


def test_clone_direct_credentials_stay_out_of_actual_api_and_runtime_remains_pooled(live):
    assert_api_process_holds_no_privileged_connection(live, int(os.environ["IMPACT_API_PID"]))
    for role in ["APP", "IDENTITY", "PLATFORM", "WORKER", "EXECUTOR"]:
        direct = conninfo_to_dict(os.environ["IMPACT_DIRECT_LOGIN_DSN_" + role])
        runtime = conninfo_to_dict(os.environ["IMPACT_LOGIN_DSN_" + role])
        assert direct["user"] == runtime["user"] == "impact_" + role.lower() + "_login"
        assert direct["dbname"] == runtime["dbname"]
        assert direct["password"] == runtime["password"]
        if os.environ.get("IMPACT_DB_POOLER") and role != "EXECUTOR":
            assert runtime["host"] == "127.0.0.1" and direct["port"] != runtime["port"]
        else:
            assert direct == runtime
