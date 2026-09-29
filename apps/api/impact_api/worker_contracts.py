"""Closed operator view of the worker heartbeats (v0.16); no tenant data."""

from .tenant_contracts import obj, text

DATE = {"type": "string", "format": "date-time"}
COUNT = {"type": "integer", "minimum": 0}
WORKER = obj(
    {
        "worker_id": text(128),
        "build": text(32),
        "state": {"enum": ["RUNNING", "STOPPING", "STOPPED"]},
        "started_at": DATE,
        "beat_at": DATE,
        "stopped_at": {"anyOf": [DATE, {"type": "null"}]},
        "stale": {"type": "boolean"},
        "iterations": COUNT,
        "sent": COUNT,
        "retried": COUNT,
        "dead": COUNT,
    }
)
WORKERS = obj(
    {
        "stale_after_seconds": {"type": "integer", "minimum": 1},
        "items": {"type": "array", "maxItems": 50, "items": WORKER},
    }
)


def add_paths(paths, operation):
    paths["/v1/platform/workers"] = {"get": operation("list_workers", response_schema=WORKERS)}
