"""A PgBouncer in TRANSACTION pooling mode in front of a native qualification database
(QA 2026-10 non-functional: `scripts/run.py test --native --pooler pgbouncer`).

The runner provisions the login roles and migrates directly, then starts one `pgbouncer` process
on an OS-chosen loopback port with the four runtime logins (app, identity, platform, worker) in its
authentication file — never the migrator or the superuser fixture connection — and points the API's
three connection strings and the worker's at it. `pool_mode = transaction` with a deliberately
small `default_pool_size` forces many client connections through few server connections, so every
transaction of the suite is served by whichever server connection is free: anything that relied on
session state (session-level SET, session advisory locks, server-side prepared statements, LISTEN)
would break here and does not elsewhere. The admin console is reachable for the tests as
IMPACT_POOLER_ADMIN_DSN (SHOW POOLS / SHOW STATS prove the multiplexing).

Nothing here is used by the application: production topology is an owner decision (no pooler
exists on the staging droplet)."""

import os
import shutil
import socket
import subprocess
import time

import psycopg
from psycopg.conninfo import conninfo_to_dict, make_conninfo

POOL_SIZE = 3  # server connections per (database, user): small on purpose
ADMIN_USER = "pooler_admin"
POOLED_LOGINS = ["impact_app_login", "impact_identity_login", "impact_platform_login", "impact_worker_login"]


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def binary():
    path = shutil.which("pgbouncer") or next(
        (p for p in ["/usr/sbin/pgbouncer", "/usr/local/bin/pgbouncer"] if os.path.exists(p)), None
    )
    if not path:
        raise RuntimeError(
            "pgbouncer is not installed (apt-get install pgbouncer, or build 1.22+ from source)"
        )
    return path


def through(dsn, port):
    params = conninfo_to_dict(dsn)
    params.update(host="127.0.0.1", port=str(port))
    return make_conninfo(**params)


def start(local, fixture_dsn, passwords, admin_password):
    """Write the configuration under `local`, start pgbouncer, wait until it accepts connections and
    return (process, port, admin_dsn)."""
    params = conninfo_to_dict(fixture_dsn)
    host = params.get("host") or "127.0.0.1"
    upstream_port = int(params.get("port") or 5432)
    database = params["dbname"]
    port = free_port()
    directory = (local / "pgbouncer").resolve()
    directory.mkdir(parents=True, exist_ok=True)
    userlist = directory / "userlist.txt"
    lines = [f'"{login}" "{passwords[login]}"' for login in POOLED_LOGINS]
    lines.append(f'"{ADMIN_USER}" "{admin_password}"')
    userlist.write_text("\n".join(lines) + "\n")
    userlist.chmod(0o600)
    ini = directory / "pgbouncer.ini"
    ini.write_text(
        f"""[databases]
{database} = host={host} port={upstream_port} dbname={database}

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = {port}
unix_socket_dir = {directory}
auth_type = scram-sha-256
auth_file = {userlist}
admin_users = {ADMIN_USER}
pool_mode = transaction
default_pool_size = {POOL_SIZE}
min_pool_size = 0
reserve_pool_size = 0
max_client_conn = 400
max_db_connections = {POOL_SIZE * len(POOLED_LOGINS)}
server_idle_timeout = 60
server_connect_timeout = 5
server_login_retry = 1
query_wait_timeout = 5
ignore_startup_parameters = extra_float_digits
logfile = {directory / "pgbouncer.log"}
pidfile = {directory / "pgbouncer.pid"}
log_connections = 0
log_disconnections = 0
"""
    )
    command = [binary(), str(ini)]
    if os.geteuid() == 0:
        # PgBouncer refuses to run as root. Under a root runner (the development sandbox) it runs
        # as IMPACT_POOLER_USER (default postgres), which must be able to read its configuration
        # and write its log, socket and pid file: the directory and its files change hands.
        user = os.environ.get("IMPACT_POOLER_USER", "postgres")
        shutil.chown(directory, user, None)
        for path in [userlist, ini]:
            shutil.chown(path, user, None)
        (directory / "pgbouncer.out").touch()
        shutil.chown(directory / "pgbouncer.out", user, None)
        command = ["setpriv", "--reuid=" + user, "--regid=" + user, "--init-groups", *command]
    process = subprocess.Popen(
        command,
        cwd=directory,
        stdout=open(directory / "pgbouncer.out", "w"),
        stderr=subprocess.STDOUT,
    )
    admin_dsn = f"postgresql://{ADMIN_USER}:{admin_password}@127.0.0.1:{port}/pgbouncer"
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("pgbouncer exited: " + (directory / "pgbouncer.out").read_text()[-2000:])
        try:
            with psycopg.connect(admin_dsn, autocommit=True, prepare_threshold=None, connect_timeout=2) as c:
                rows = c.execute("SHOW CONFIG").fetchall()
                mode = next(r[1] for r in rows if r[0] == "pool_mode")
                if mode != "transaction":
                    raise RuntimeError("pgbouncer is not in transaction mode: " + mode)
            return process, port, admin_dsn
        except psycopg.OperationalError:
            time.sleep(0.2)
    process.terminate()
    raise RuntimeError("pgbouncer did not accept connections within 15 s")


def version():
    """The first line of `pgbouncer --version` (the build details follow it)."""
    try:
        output = subprocess.run([binary(), "--version"], capture_output=True, text=True, timeout=10).stdout
        return output.strip().splitlines()[0] if output.strip() else None
    except (RuntimeError, OSError, subprocess.TimeoutExpired):
        return None
