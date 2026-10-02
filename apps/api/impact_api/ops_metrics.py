"""Operations summary for platform operators and for the server's alert check (no tenant data).

`GET /v1/platform/metrics` (platform API 1.6.0, operators only; anyone else 404) answers with:

- `requests`: this API process's request counts by route family and status class and a latency
  histogram (cumulative buckets in seconds), since `started_at`. Counters live in memory and start
  again at zero when the process restarts; no path, tenant, identity or query is recorded.
- `workers`: heartbeat rows (count, running, stale, newest beat age by the database clock, the
  workers' own dead and failure totals).
- `deliveries`: dispatchable outbox rows that are DEAD or held (through the control plane's
  attention function, capped at 50 rows, `capped` then true) and the number still unsent (PENDING or
  LEASED) summed over the tenants counted.
- `jobs`: unfinished jobs (not Succeeded, SucceededWithIssues, Failed or Cancelled) over the same
  tenants. Tenants are those under control-plane custody (`tenant_onboarding`), at most 200
  (`tenants.not_counted` says how many more exist).
- `storage`: free space of the file system holding the evidence object store.
- `operations`: the server's last operations check (backup age, restore drill, disk, alerts) as
  deploy/ops-check.sh wrote it to IMPACT_OPS_STATUS_FILE, or null when there is none.

Only counts, ages, states and closed codes leave this module: never a tenant identifier, name,
address, reference or secret.

`python -m impact_api.ops_metrics` prints `collect()` (workers, deliveries, jobs, storage) as one
JSON line for deploy/ops-check.sh, which runs it inside the API container (`docker compose exec`,
root on the server only); it uses the API's own platform connection.
"""

import json
import os
import shutil
import sys
from datetime import datetime, timezone
from threading import Lock
from time import monotonic

from .domain import unavailable
from .version import BUILD, SCHEMA

# Upper bounds (seconds) of the latency histogram; the last bucket is everything slower.
BUCKETS = (0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
FAMILIES = ("tenant", "platform", "auth", "health", "client")
STALE_AFTER_SECONDS = 120
MAX_TENANTS = 200
ATTENTION_CAP = 50


def family(path):
    """The route family of a request path: a fixed vocabulary, never the path itself."""
    if path.startswith("/v1/platform"):
        return "platform"
    if path.startswith("/v1/"):
        return "tenant"
    if path.startswith("/auth/"):
        return "auth"
    if path.startswith("/health/"):
        return "health"
    return "client"


class RequestMetrics:
    """In-process request counters, safe to update from the event loop and worker threads."""

    def __init__(self, clock=monotonic):
        self.clock = clock
        self.lock = Lock()
        self.started = clock()
        self.started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.total = 0
        self.by_family = {name: {"2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0} for name in FAMILIES}
        self.buckets = [0] * (len(BUCKETS) + 1)
        self.seconds_total = 0.0

    def observe(self, path, status, seconds):
        status_class = str(min(max(int(status) // 100, 2), 5)) + "xx"
        index = next((i for i, bound in enumerate(BUCKETS) if seconds <= bound), len(BUCKETS))
        with self.lock:
            self.total += 1
            self.by_family[family(path)][status_class] += 1
            self.buckets[index] += 1
            self.seconds_total += seconds

    def snapshot(self):
        with self.lock:
            cumulative, running = [], 0
            for bound, count in zip([*BUCKETS, None], self.buckets):
                running += count
                cumulative.append({"le": bound, "count": running})
            return {
                "started_at": self.started_at,
                "uptime_seconds": int(self.clock() - self.started),
                "total": self.total,
                "by_family": {name: dict(counts) for name, counts in self.by_family.items()},
                "latency_seconds": {
                    "buckets": cumulative,
                    "sum": round(self.seconds_total, 3),
                },
            }


def storage(directory):
    if not directory or not os.path.isdir(directory):
        return None
    usage = shutil.disk_usage(directory)
    return {
        "free_mb": usage.free // (1024 * 1024),
        "total_mb": usage.total // (1024 * 1024),
        "free_percent": round(100 * usage.free / usage.total, 1) if usage.total else None,
    }


def operations(path):
    """The server's last operations check, or None (absent, unreadable or not JSON)."""
    if not path:
        return None
    try:
        with open(path, encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, ValueError):
        return None
    return document if isinstance(document, dict) else None


def collect(db, settings):
    """Workers, deliveries, jobs and storage, read on the platform connection."""
    # The migration ledger is readable by the application role (as for readiness), not the platform's.
    with db.transaction() as c:
        schema = c.execute("SELECT max(version) AS version FROM impact.schema_migration").fetchone()[
            "version"
        ]
    with db.transaction(platform=True) as c:
        beats = c.execute(
            "SELECT state,EXTRACT(EPOCH FROM statement_timestamp()-beat_at)::float8 AS age,dead,failures "
            "FROM impact.worker_heartbeat"
        ).fetchall()
        attention = c.execute(
            "SELECT state,held FROM impact.operator_delivery_attention(NULL,%s)", (ATTENTION_CAP,)
        ).fetchall()
        tenants = [
            str(row["tenant_id"])
            for row in c.execute(
                "SELECT tenant_id FROM impact.tenant_onboarding ORDER BY tenant_id LIMIT %s",
                (MAX_TENANTS + 1,),
            ).fetchall()
        ]
        lifecycle, unsent, unfinished = {}, 0, 0
        for tenant in tenants[:MAX_TENANTS]:
            c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
            state = c.execute(
                "SELECT lifecycle_state FROM impact.tenant_root WHERE tenant_id=%s", (tenant,)
            ).fetchone()
            if state:
                lifecycle[state["lifecycle_state"]] = lifecycle.get(state["lifecycle_state"], 0) + 1
            impact = c.execute("SELECT impact.tenant_work_impact(%s) AS impact", (tenant,)).fetchone()[
                "impact"
            ]
            unsent += int(impact.get("unsent_events") or 0)
            unfinished += int(impact.get("unfinished_jobs") or 0)
    running = [b for b in beats if b["state"] == "RUNNING"]
    fresh = [b for b in running if b["age"] is not None and b["age"] <= STALE_AFTER_SECONDS]
    ages = [b["age"] for b in running if b["age"] is not None]
    return {
        "build": BUILD,
        "schema_version": schema,
        "schema_expected": SCHEMA,
        "workers": {
            "total": len(beats),
            "running": len(running),
            "running_fresh": len(fresh),
            "stale": len(running) - len(fresh),
            "stale_after_seconds": STALE_AFTER_SECONDS,
            "newest_beat_age_seconds": round(min(ages), 1) if ages else None,
            "dead_total": sum(int(b["dead"]) for b in beats),
            "failures_total": sum(int(b["failures"]) for b in beats),
        },
        "deliveries": {
            "dead": sum(1 for row in attention if row["state"] == "DEAD"),
            "held": sum(1 for row in attention if row["held"] and row["state"] != "DEAD"),
            "capped": len(attention) >= ATTENTION_CAP,
            "unsent": unsent,
        },
        "jobs": {"unfinished": unfinished},
        "tenants": {
            "counted": min(len(tenants), MAX_TENANTS),
            "not_counted": max(len(tenants) - MAX_TENANTS, 0),
            "by_lifecycle": lifecycle,
        },
        "storage": storage(settings.object_store_dir),
    }


class OpsMetrics:
    def __init__(self, lifecycle, requests):
        self.lifecycle, self.db, self.s, self.requests = lifecycle, lifecycle.db, lifecycle.s, requests

    def summary(self, identity):
        if not self.s.platform_dsn:
            unavailable()
        with self.db.transaction(platform=True) as c:
            if not self.lifecycle.operator(c, identity):
                unavailable()
        return {
            **collect(self.db, self.s),
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "requests": self.requests.snapshot(),
            "operations": operations(self.s.ops_status_file),
        }


def main():
    from .config import Settings
    from .store import Database

    settings = Settings.load()
    try:
        result = collect(Database(settings), settings)
        result["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    except Exception as exc:  # reported as a class only: the check records it as an alert
        print(json.dumps({"error": type(exc).__name__}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
