"""Closed operator view of the operations summary (platform API 1.6.0); counts only, no tenant data."""

from .tenant_contracts import obj, text

COUNT = {"type": "integer", "minimum": 0}
SECONDS = {"type": "number", "minimum": 0}
NULL_SECONDS = {"anyOf": [SECONDS, {"type": "null"}]}
DATE = {"type": "string", "format": "date-time"}
CLASSES = obj({"2xx": COUNT, "3xx": COUNT, "4xx": COUNT, "5xx": COUNT})
FAMILIES = ("tenant", "platform", "auth", "health", "client")
REQUESTS = obj(
    {
        "started_at": DATE,
        "uptime_seconds": COUNT,
        "total": COUNT,
        "by_family": obj({name: CLASSES for name in FAMILIES}),
        "latency_seconds": obj(
            {
                "buckets": {
                    "type": "array",
                    "maxItems": 16,
                    "items": obj({"le": {"anyOf": [SECONDS, {"type": "null"}]}, "count": COUNT}),
                },
                "sum": SECONDS,
            }
        ),
    }
)
METRICS = obj(
    {
        "build": text(32),
        "schema_version": COUNT,
        "schema_expected": COUNT,
        "generated_at": DATE,
        "workers": obj(
            {
                "total": COUNT,
                "running": COUNT,
                "running_fresh": COUNT,
                "stale": COUNT,
                "stale_after_seconds": COUNT,
                "newest_beat_age_seconds": NULL_SECONDS,
                "dead_total": COUNT,
                "failures_total": COUNT,
            }
        ),
        "deliveries": obj({"dead": COUNT, "held": COUNT, "capped": {"type": "boolean"}, "unsent": COUNT}),
        "jobs": obj({"unfinished": COUNT}),
        "tenants": obj(
            {
                "counted": COUNT,
                "not_counted": COUNT,
                "by_lifecycle": {"type": "object", "maxProperties": 7, "additionalProperties": COUNT},
            }
        ),
        "storage": {
            "anyOf": [
                obj({"free_mb": COUNT, "total_mb": COUNT, "free_percent": NULL_SECONDS}),
                {"type": "null"},
            ]
        },
        "requests": REQUESTS,
        # The server's last operations check as deploy/ops-check.sh wrote it (backup, restore drill,
        # disk, alerts); its shape belongs to the deployment package, not to this contract.
        "operations": {"anyOf": [{"type": "object"}, {"type": "null"}]},
    }
)


def add_paths(paths, operation):
    paths["/v1/platform/metrics"] = {"get": operation("platform_metrics", response_schema=METRICS)}
