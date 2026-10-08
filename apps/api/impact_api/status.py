"""User-visible degradation status (VF-AVL-002, the "users shall see the affected function" half).

`GET /v1/status` answers every signed-in identity (bearer or cookie; anonymous callers 401) with a
closed catalogue of plain-language notices derived from what the API can observe itself and from the
server's last operations check:

- the schema ledger versus the build (readiness), on the application connection;
- worker freshness from `worker_heartbeat` (platform connection; the same 120 s window as the alert);
- the evidence object store's directory and free space;
- the closed alert codes `deploy/ops-check.sh` wrote to `ops_status_file` (backup, drill, disk,
  containers), mapped to the functions users would notice.

Members receive `state` (OK | DEGRADED), the notices and a poll interval, nothing else. Platform
operators additionally receive `detail`: the figures behind the notices, the server's alert list,
and the published on-call rota (`on_call_file`, by default `on-call.json` beside the ops status
file). No reason code that could name a login, a tenant, an address or a secret is ever copied into
a notice: notices are catalogue text only; the detail carries closed codes and counts.

The database and the identity provider are required dependencies: when they fail this route fails
too (503 with `reason_code` DATABASE_UNAVAILABLE / IDENTITY_PROVIDER_UNAVAILABLE), and the client
shows the matching catalogue text for that reason code itself.
"""

import json
import os
from datetime import datetime, timezone

from .clock import now
from .ops_metrics import operations, storage
from .version import SCHEMA

POLL_SECONDS = 60
STALE_AFTER_SECONDS = 120
OPERATIONS_CHECK_STALE_SECONDS = 1800
# Uploads carry at most 25,000,000 bytes and are written through a temporary file: below the first
# figure the next upload is likely to fail, below the second large ones may.
STORAGE_UNAVAILABLE_MB = 64
STORAGE_LOW_MB = 512
MAX_ON_CALL_TEXT = 200

# The closed catalogue. Keys are the only codes a client ever renders; the client holds the same
# table for the two codes that reach it as a 503 reason rather than in a 200 body.
CATALOGUE = {
    "DATABASE_UNAVAILABLE": (
        "critical",
        "The database is unavailable. Nothing can be read or saved until it is back; "
        "work already saved is safe.",
    ),
    "IDENTITY_PROVIDER_UNAVAILABLE": (
        "critical",
        "Sign-in is unavailable while the identity provider is unreachable. "
        "Sessions that are already open continue.",
    ),
    "UPGRADE_IN_PROGRESS": (
        "critical",
        "The system is being updated. Please wait a few minutes before saving work.",
    ),
    "DELIVERY_DELAYED": (
        "warning",
        "Email and in-app notices are delayed. Nothing is lost; they are sent when background "
        "processing resumes.",
    ),
    "EXPORTS_DELAYED": (
        "warning",
        "Report files (PDF, XLSX and DOCX) are not being produced at the moment. Requests stay "
        "queued and complete when background processing resumes.",
    ),
    "EMAIL_UNAVAILABLE": (
        "warning",
        "Email delivery is paused. In-app notices continue.",
    ),
    "EVIDENCE_UPLOADS_UNAVAILABLE": (
        "warning",
        "Evidence uploads are unavailable because file storage is full or unreachable. "
        "Existing evidence can still be downloaded.",
    ),
    "EVIDENCE_STORAGE_LOW": (
        "warning",
        "File storage is nearly full; large evidence uploads may fail.",
    ),
}
ORDER = list(CATALOGUE)
# Server alert codes (deploy/ops_alerts.py) and the user-facing functions they affect; anything not
# listed here is operator detail only.
ALERT_NOTICES = {
    ("WORKER_STALE", None): ("DELIVERY_DELAYED", "EXPORTS_DELAYED"),
    ("CONTAINER_UNHEALTHY", "worker"): ("DELIVERY_DELAYED", "EXPORTS_DELAYED"),
    ("CONTAINER_UNHEALTHY", "mailsink"): ("EMAIL_UNAVAILABLE",),
    ("CONTAINER_UNHEALTHY", "keycloak"): ("IDENTITY_PROVIDER_UNAVAILABLE",),
    ("DISK_LOW", None): ("EVIDENCE_STORAGE_LOW",),
    ("SCHEMA_MISMATCH", None): ("UPGRADE_IN_PROGRESS",),
}


def parse_time(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


TARGET_FIRST_CODES = {"CONTAINER_UNHEALTHY", "DISK_LOW"}


def alert_target(alert):
    """The alert's target: the explicit field (release 0.27 files), or, for a file written before
    targets existed, the first word of a message that begins with the service or file system."""
    target = alert.get("target")
    if isinstance(target, str):
        return target
    message = alert.get("message")
    if alert.get("code") in TARGET_FIRST_CODES and isinstance(message, str) and message:
        return message.split(" ", 1)[0].rstrip(":")
    return ""


def notices_from_alerts(alerts):
    """Catalogue codes for the server's alert list; (code, target) then (code, None); DISK_LOW only
    when critical (a warning leaves room for the uploads in flight)."""
    codes = []
    for alert in alerts if isinstance(alerts, list) else []:
        if not isinstance(alert, dict):
            continue
        code, target = alert.get("code"), alert_target(alert)
        if code == "DISK_LOW" and alert.get("severity") != "critical":
            continue
        for key in [(code, target), (code, None)]:
            if key in ALERT_NOTICES:
                codes.extend(ALERT_NOTICES[key])
                break
    return codes


def store_space(directory):
    """Free space where the object store writes: the directory, or (the store creates its tree on
    first use) its nearest existing ancestor; None when that path is not a directory at all."""
    if not directory:
        return None
    path = os.path.abspath(directory)
    while not os.path.exists(path):
        parent = os.path.dirname(path)
        if parent == path:
            return None
        path = parent
    return storage(path) if os.path.isdir(path) else None


def storage_notices(view, configured):
    if not configured:
        return []
    if view is None:
        return ["EVIDENCE_UPLOADS_UNAVAILABLE"]
    free = view.get("free_mb")
    if free is None:
        return []
    if free < STORAGE_UNAVAILABLE_MB:
        return ["EVIDENCE_UPLOADS_UNAVAILABLE"]
    if free < STORAGE_LOW_MB:
        return ["EVIDENCE_STORAGE_LOW"]
    return []


def worker_view(beats, environment):
    """Fresh/stale from heartbeat rows (state, age in seconds). A deployment that has never run a
    worker counts as stale only where a worker is required (staging and production); development
    and test runs without a worker are not degraded."""
    running = [b for b in beats if b["state"] == "RUNNING"]
    fresh = [b for b in running if b["age"] is not None and b["age"] <= STALE_AFTER_SECONDS]
    ages = [b["age"] for b in running if b["age"] is not None]
    required = bool(beats) or environment in {"staging", "production"}
    return {
        "total": len(beats),
        "running": len(running),
        "running_fresh": len(fresh),
        "stale_after_seconds": STALE_AFTER_SECONDS,
        "newest_beat_age_seconds": round(min(ages), 1) if ages else None,
        "stale": required and not fresh,
    }


def catalogue(codes):
    ordered = [code for code in ORDER if code in set(codes)]
    return [{"code": code, "severity": CATALOGUE[code][0], "message": CATALOGUE[code][1]} for code in ordered]


def compose(schema_version, workers, storage_view, storage_configured, ops, environment, at):
    """(notices, operations view) from the observations; pure, for the unit tests."""
    codes, sources = [], []
    if schema_version != SCHEMA:
        codes.append("UPGRADE_IN_PROGRESS")
        sources.append("SCHEMA_MISMATCH")
    if workers and workers["stale"]:
        codes.extend(["DELIVERY_DELAYED", "EXPORTS_DELAYED"])
        sources.append("WORKER_STALE")
    for code in storage_notices(storage_view, storage_configured):
        codes.append(code)
        sources.append("OBJECT_STORE_" + ("UNAVAILABLE" if code.endswith("UNAVAILABLE") else "LOW"))
    alerts = ops.get("alerts") if isinstance(ops, dict) else None
    checked = parse_time((ops.get("operations") or {}).get("checked_at")) if isinstance(ops, dict) else None
    stale_check = checked is None or (at - checked).total_seconds() > OPERATIONS_CHECK_STALE_SECONDS
    if isinstance(alerts, list) and not stale_check:
        mapped = notices_from_alerts(alerts)
        codes.extend(mapped)
        if mapped:
            sources.append("OPERATIONS_CHECK")
    view = {
        "checked_at": checked.isoformat(timespec="seconds") if checked else None,
        "stale": stale_check,
        "alerts": [
            {
                "code": str(a.get("code"))[:64],
                "severity": str(a.get("severity"))[:16],
                "target": alert_target(a)[:64],
                "message": str(a.get("message"))[:300],
            }
            for a in (alerts if isinstance(alerts, list) else [])
            if isinstance(a, dict)
        ][:50],
    }
    return catalogue(codes), sorted(set(sources)), view


def person(value):
    if not isinstance(value, dict):
        return None
    view = {
        key: str(value[key])[:MAX_ON_CALL_TEXT]
        for key in ("name", "role", "contact", "hours")
        if isinstance(value.get(key), (str, int))
    }
    return view if view.get("name") else None


def on_call(path):
    """The published rota (deploy/on-call.example.json): bounded strings of the known keys only, or
    a closed problem code. The file is operator-facing: it names people and how to reach them."""
    if not path:
        return {"status": "NOT_CONFIGURED"}
    try:
        with open(path, encoding="utf-8") as handle:
            document = json.load(handle)
    except OSError:
        return {"status": "MISSING"}
    except ValueError:
        return {"status": "INVALID"}
    if not isinstance(document, dict) or document.get("schema") != "impact-on-call-v1":
        return {"status": "INVALID"}
    primary = person(document.get("primary"))
    if not primary:
        return {"status": "INVALID"}
    escalation = [p for p in map(person, document.get("escalation") or []) if p][:5]
    rota = {
        "status": "OK",
        "primary": primary,
        "secondary": person(document.get("secondary")),
        "escalation": escalation,
        "timezone": str(document.get("timezone") or "UTC")[:64],
        "updated_at": str(document.get("updated_at") or "")[:40] or None,
        "notes": str(document.get("notes") or "")[: MAX_ON_CALL_TEXT * 2] or None,
    }
    valid_until = parse_time(document.get("valid_until"))
    rota["expired"] = bool(valid_until and valid_until < now())
    return rota


def on_call_path(settings):
    if settings.on_call_file:
        return settings.on_call_file
    if settings.ops_status_file:
        return os.path.join(os.path.dirname(settings.ops_status_file), "on-call.json")
    return ""


class Status:
    def __init__(self, lifecycle):
        self.lifecycle, self.db, self.s = lifecycle, lifecycle.db, lifecycle.s

    def read(self, identity):
        at = now()
        with self.db.transaction() as c:
            schema = c.execute("SELECT max(version) AS version FROM impact.schema_migration").fetchone()[
                "version"
            ]
        workers, dead, held, operator = None, None, None, False
        if self.s.platform_dsn:
            with self.db.transaction(platform=True) as c:
                operator = self.lifecycle.operator(c, identity)
                beats = c.execute(
                    "SELECT state,EXTRACT(EPOCH FROM statement_timestamp()-beat_at)::float8 AS age "
                    "FROM impact.worker_heartbeat"
                ).fetchall()
                workers = worker_view(beats, self.s.environment)
                if operator:
                    attention = c.execute(
                        "SELECT state,held FROM impact.operator_delivery_attention(NULL,%s)", (50,)
                    ).fetchall()
                    dead = sum(1 for row in attention if row["state"] == "DEAD")
                    held = sum(1 for row in attention if row["held"] and row["state"] != "DEAD")
        storage_view = store_space(self.s.object_store_dir)
        ops = operations(self.s.ops_status_file)
        notices, sources, operations_view = compose(
            schema, workers, storage_view, bool(self.s.object_store_dir), ops, self.s.environment, at
        )
        body = {
            "generated_at": at.isoformat(timespec="seconds"),
            "state": "DEGRADED" if notices else "OK",
            "poll_seconds": POLL_SECONDS,
            "notices": notices,
        }
        if operator:
            body["detail"] = {
                "sources": sources,
                "workers": workers,
                "deliveries": {"dead": dead, "held": held},
                "storage": storage_view,
                "operations": operations_view if self.s.ops_status_file else None,
                "on_call": on_call(on_call_path(self.s)),
            }
        return body
