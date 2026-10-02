"""Operations status and alerts for the staging server (host side; standard library only).

Used by deploy/ops-check.sh (every 5 minutes, systemd timer impact-ops-check.timer) and by
deploy/restore-drill.sh. Nothing here contacts anything: the shell scripts collect the inputs, this
module evaluates them and writes files.

    ops_alerts.py evaluate --ops-dir D --containers F --app F --disk F [--status-file F ...]
        Reads the backup status the backup container wrote (D/backup-status.json), the last restore
        drill (D/restore-drill.json), the containers (`docker compose ps --format json`), the API's
        operations summary (`python -m impact_api.ops_metrics` inside the API container) and the
        disk figures; writes D/ops-status.json and merges `operations` and `alerts` into each status
        file (deploy-status.json, public and private copies). Values found in --secrets-file are
        never written (a defensive scrub; none of the inputs should carry one).
    ops_alerts.py drill-result F
        Writes a restore drill's result from the environment restore-drill.sh sets (OUTCOME,
        STARTED, FINISHED, RESTORE, CHECK, ERROR).
    ops_alerts.py notify --ops-dir D [--renotify-seconds N] [--deployment NAME] [--status-url U]
        Delivers alert transitions (release 0.27, VF-OBS-001): compares D/ops-status.json with
        D/alert-state.json, deduplicated by alert code and target, and sends NEW alerts, CLEARED
        alerts and, for alerts still active after N seconds (default 21600), one REMINDER through
        the channels configured in the environment: a generic webhook (ALERT_WEBHOOK_URL; JSON POST
        with a Slack-compatible `text`, signed with HMAC-SHA256 when ALERT_WEBHOOK_SECRET is set:
        header X-Impact-Signature "t=<unix>,v1=<hex of HMAC(secret, t + "." + body)>") and e-mail
        through the worker's SMTP (SMTP_HOST/SMTP_PORT/SMTP_USERNAME/SMTP_PASSWORD/SMTP_FROM, the
        same variables compose.yaml hands the worker, to ALERT_EMAIL_TO; a loopback host is the
        staging capture and is skipped). A transition is recorded as notified only once at least
        one configured channel accepted it; otherwise the next check retries. Messages carry the
        closed codes and their messages only: no secret, address, tenant or login ever enters an
        alert, and secrets are read from the environment, never from arguments.

Every alert is {"code", "severity" (critical|warning), "message", "target"} with a closed code;
`target` names the thing the alert is about (a service, a file system, or "" for the whole server)
so that two alerts with one code are told apart:

    BACKUP_MISSING            no verified backup set yet
    BACKUP_STALE              the newest verified set is older than BACKUP_STALE_HOURS (26)
    BACKUP_FAILED             the last attempt failed (its step is in the message)
    BACKUP_REFUSED_DISK_LOW   the last attempt was refused for lack of free space
    DISK_LOW                  a watched file system is below DISK_WARN_PERCENT (10 %) or
                              DISK_WARN_MB (2048) free; critical below 5 % or 1024 MB
    CONTAINER_UNHEALTHY       an expected service is absent, not running, or reports unhealthy
    WORKER_STALE              no running worker has beaten within its staleness window
    DELIVERIES_DEAD           dispatchable deliveries are DEAD (an operator may re-queue them)
    QUEUE_BACKLOG             unsent deliveries or unfinished jobs exceed QUEUE_WARN (200)
    SCHEMA_MISMATCH           the database schema differs from the one this build expects
    OPS_SUMMARY_UNAVAILABLE   the API's operations summary could not be read
    RESTORE_DRILL_FAILED      the last restore drill failed
    RESTORE_DRILL_STALE       no restore drill, or the last one is older than DRILL_STALE_DAYS (8)
"""

import argparse
import hashlib
import hmac
import json
import os
import smtplib
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from email.message import EmailMessage

EXPECTED_SERVICES = ("postgres", "keycloak", "api", "worker", "mailsink", "caddy", "backup")
BACKUP_STALE_HOURS = 26
DISK_WARN_PERCENT, DISK_CRITICAL_PERCENT = 10, 5
DISK_WARN_MB, DISK_CRITICAL_MB = 2048, 1024
QUEUE_WARN = 200
DRILL_STALE_DAYS = 8
RENOTIFY_SECONDS = 6 * 3600
WEBHOOK_TIMEOUT = 10
SMTP_TIMEOUT = 20
STATE_FILE = "alert-state.json"
MAX_DELIVERY_RECORDS = 100
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1", "mailsink"}


def parse_time(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def stamp(moment):
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def hours_between(earlier, later):
    return round((later - earlier).total_seconds() / 3600, 1)


def alert(code, severity, message, target=""):
    return {"code": code, "severity": severity, "message": message, "target": target}


def read_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read().strip()
    except OSError:
        return default
    if not text:
        return default
    try:
        return json.loads(text)
    except ValueError:
        # `docker compose ps --format json` prints one object per line on some versions.
        try:
            return [json.loads(line) for line in text.splitlines() if line.strip()]
        except ValueError:
            return default


def services_from(rows):
    services = {}
    for row in rows if isinstance(rows, list) else []:
        name = row.get("Service") or row.get("Name")
        if name:
            services[name] = {"state": row.get("State"), "health": row.get("Health") or None}
    return services


def backup_view(status, now):
    if not isinstance(status, dict):
        return {"result": None, "last_set": None, "age_hours": None}
    last = status.get("last_success") if isinstance(status.get("last_success"), dict) else None
    finished = parse_time(last.get("finished_at")) if last else None
    return {
        "result": status.get("result"),
        "reason": status.get("reason") or None,
        "attempted_at": status.get("attempted_at"),
        "last_set": last.get("set") if last else None,
        "last_success_at": last.get("finished_at") if last else None,
        "age_hours": hours_between(finished, now) if finished else None,
        "bytes": last.get("bytes") if last else None,
        "schema_version": last.get("schema_version") if last else None,
        "objects": last.get("objects") if last else None,
        "free_mb": status.get("free_mb"),
        "required_mb": status.get("required_mb"),
        "daily_sets": len(status.get("daily_sets") or []),
        "weekly_sets": len(status.get("weekly_sets") or []),
    }


def drill_view(drill, now):
    if not isinstance(drill, dict):
        return {"outcome": None}
    finished = parse_time(drill.get("finished_at"))
    return {
        "outcome": drill.get("outcome"),
        "finished_at": drill.get("finished_at"),
        "age_days": round((now - finished).total_seconds() / 86400, 1) if finished else None,
        "set": drill.get("set"),
        "duration_seconds": drill.get("duration_seconds"),
        "backup_age_hours": drill.get("backup_age_hours"),
        "error": drill.get("error"),
    }


def evaluate(backup_status, drill, containers, app, disks, now):
    """(operations view, alerts) from the collected inputs; pure, for the unit tests."""
    alerts = []
    backup = backup_view(backup_status, now)
    if backup["last_set"] is None:
        alerts.append(alert("BACKUP_MISSING", "critical", "No verified backup set exists yet."))
    elif backup["age_hours"] is not None and backup["age_hours"] > BACKUP_STALE_HOURS:
        alerts.append(
            alert(
                "BACKUP_STALE",
                "critical",
                "The newest verified backup set is " + str(backup["age_hours"]) + " hours old.",
            )
        )
    if backup["result"] == "failed":
        alerts.append(
            alert(
                "BACKUP_FAILED", "critical", "The last backup attempt failed (" + str(backup["reason"]) + ")."
            )
        )
    elif backup["result"] == "refused":
        alerts.append(
            alert(
                "BACKUP_REFUSED_DISK_LOW",
                "critical",
                "The last backup was refused: "
                + str(backup["free_mb"])
                + " MB free, "
                + str(backup["required_mb"])
                + " MB required.",
            )
        )
    disk_view = {}
    for name, figures in (disks or {}).items():
        if not isinstance(figures, dict) or not figures.get("total_mb"):
            continue
        free, total = int(figures.get("free_mb") or 0), int(figures["total_mb"])
        percent = round(100 * free / total, 1)
        disk_view[name] = {"free_mb": free, "total_mb": total, "free_percent": percent}
        if percent < DISK_CRITICAL_PERCENT or free < DISK_CRITICAL_MB:
            severity = "critical"
        elif percent < DISK_WARN_PERCENT or free < DISK_WARN_MB:
            severity = "warning"
        else:
            continue
        alerts.append(
            alert("DISK_LOW", severity, name + ": " + str(free) + " MB free (" + str(percent) + " %).", name)
        )
    services = services_from(containers)
    for name in EXPECTED_SERVICES:
        row = services.get(name)
        if not row:
            alerts.append(alert("CONTAINER_UNHEALTHY", "critical", name + " is not present.", name))
        elif row["state"] != "running" or row["health"] not in (None, "healthy"):
            alerts.append(
                alert(
                    "CONTAINER_UNHEALTHY",
                    "critical",
                    name
                    + " is "
                    + str(row["state"])
                    + (" (" + str(row["health"]) + ")" if row["health"] else "")
                    + ".",
                    name,
                )
            )
    if not isinstance(app, dict) or app.get("error") or "workers" not in app:
        alerts.append(
            alert(
                "OPS_SUMMARY_UNAVAILABLE",
                "warning",
                "The API's operations summary could not be read"
                + (" (" + str(app.get("error")) + ")" if isinstance(app, dict) and app.get("error") else "")
                + ".",
            )
        )
        app = {}
    else:
        workers, deliveries, jobs = app["workers"], app.get("deliveries", {}), app.get("jobs", {})
        if not workers.get("running_fresh"):
            alerts.append(
                alert(
                    "WORKER_STALE",
                    "critical",
                    "No running worker has reported within "
                    + str(workers.get("stale_after_seconds"))
                    + " seconds (newest beat "
                    + str(workers.get("newest_beat_age_seconds"))
                    + " s ago).",
                )
            )
        if deliveries.get("dead"):
            alerts.append(
                alert(
                    "DELIVERIES_DEAD",
                    "warning",
                    str(deliveries["dead"])
                    + ("+" if deliveries.get("capped") else "")
                    + " deliveries are DEAD; see Tenant lifecycle > Workers to re-queue them.",
                )
            )
        backlog = max(int(deliveries.get("unsent") or 0), int(jobs.get("unfinished") or 0))
        if backlog > QUEUE_WARN:
            alerts.append(
                alert(
                    "QUEUE_BACKLOG",
                    "warning",
                    str(deliveries.get("unsent"))
                    + " unsent deliveries, "
                    + str(jobs.get("unfinished"))
                    + " unfinished jobs.",
                )
            )
        if app.get("schema_version") != app.get("schema_expected"):
            alerts.append(
                alert(
                    "SCHEMA_MISMATCH",
                    "critical",
                    "Database schema "
                    + str(app.get("schema_version"))
                    + ", build expects "
                    + str(app.get("schema_expected"))
                    + ".",
                )
            )
    restore = drill_view(drill, now)
    if restore["outcome"] == "FAIL":
        alerts.append(
            alert(
                "RESTORE_DRILL_FAILED",
                "critical",
                "The last restore drill failed (" + str(restore["error"]) + ").",
            )
        )
    elif restore["outcome"] is None or restore["age_days"] is None or restore["age_days"] > DRILL_STALE_DAYS:
        alerts.append(
            alert(
                "RESTORE_DRILL_STALE",
                "warning",
                "No restore drill in the last " + str(DRILL_STALE_DAYS) + " days.",
            )
        )
    view = {
        "checked_at": stamp(now),
        "backup": backup,
        "restore_drill": restore,
        "disk": disk_view,
        "services": services,
        "workers": app.get("workers"),
        "deliveries": app.get("deliveries"),
        "jobs": app.get("jobs"),
    }
    return view, alerts


def secret_values(path):
    values = []
    try:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                if "=" in line:
                    value = line.split("=", 1)[1].strip()
                    # Grace secrets after a rotation (deploy/rotate-secrets.sh) are one value per
                    # family, comma- or space-separated: scrub each part as well as the whole.
                    for part in [value, *value.replace(",", " ").split()]:
                        if len(part) >= 8 and part not in values:
                            values.append(part)
    except OSError:
        pass
    return values


def scrub(document, values):
    text = json.dumps(document)
    for value in values:
        text = text.replace(json.dumps(value)[1:-1], "[redacted]")
    return json.loads(text)


def write_json(path, document, mode=0o644):
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".ops-")
    with os.fdopen(fd, "w") as handle:
        json.dump(document, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.chmod(tmp, mode)
    os.replace(tmp, path)


def merge_into_status(path, view, alerts):
    """Put `operations` and `alerts` into an existing deploy-status file; other fields untouched."""
    document = read_json(path)
    if not isinstance(document, dict):
        return False
    document["operations"] = view
    document["alerts"] = alerts
    write_json(path, document)
    return True


# ---- alert delivery (release 0.27) --------------------------------------------------------------


def alert_key(entry):
    return str(entry.get("code")) + "|" + str(entry.get("target") or "")


def transitions(alerts, state, now, renotify_seconds=RENOTIFY_SECONDS):
    """(new state, events) for the current alert list against the recorded state. Pure.

    `state["active"]` maps key -> {code, severity, message, target, first_seen, last_notified}.
    An alert whose key is unknown (or whose severity rose) is NEW; a recorded alert no longer
    present is CLEARED; a recorded alert still present is a REMINDER once `renotify_seconds` have
    passed since it was last notified. Each event carries the alerts it is about."""
    previous = (
        state.get("active") if isinstance(state, dict) and isinstance(state.get("active"), dict) else {}
    )
    current, new, reminders = {}, [], []
    rank = {"warning": 1, "critical": 2}
    for entry in alerts if isinstance(alerts, list) else []:
        if not isinstance(entry, dict) or not entry.get("code"):
            continue
        key = alert_key(entry)
        record = {
            "code": str(entry["code"]),
            "severity": str(entry.get("severity") or "warning"),
            "message": str(entry.get("message") or ""),
            "target": str(entry.get("target") or ""),
        }
        before = previous.get(key) if isinstance(previous.get(key), dict) else None
        notified = parse_time(before.get("last_notified")) if before else None
        if before and notified and rank.get(record["severity"], 0) <= rank.get(before.get("severity"), 0):
            record["first_seen"] = before.get("first_seen") or stamp(now)
            record["last_notified"] = before["last_notified"]
            if (now - notified).total_seconds() >= renotify_seconds:
                reminders.append(record)
        else:
            # Unknown, never successfully notified (a failed delivery is retried as NEW), or worse
            # than before.
            record["first_seen"] = (before or {}).get("first_seen") or stamp(now)
            record["last_notified"] = None
            new.append(record)
        current[key] = record
    cleared = [
        {**previous[key], "cleared_at": stamp(now)}
        for key in previous
        if key not in current and isinstance(previous[key], dict)
    ]
    events = []
    if new:
        events.append({"event": "NEW", "alerts": new})
    if cleared:
        events.append({"event": "CLEARED", "alerts": cleared})
    if reminders:
        events.append({"event": "REMINDER", "alerts": reminders})
    return {"active": current, "deliveries": list((state or {}).get("deliveries") or [])}, events


def describe(event, deployment):
    """One line per event for a chat channel or a subject line; codes and their messages only."""
    heads = {"NEW": "new alert", "CLEARED": "cleared", "REMINDER": "still active"}
    count = len(event["alerts"])
    head = heads[event["event"]] + ("s" if count != 1 and event["event"] == "NEW" else "")
    codes = ", ".join(
        sorted({a["code"] + (" (" + a["target"] + ")" if a.get("target") else "") for a in event["alerts"]})
    )
    return "[impact " + deployment + "] " + str(count) + " " + head + ": " + codes


def render_text(events, deployment, status_url):
    lines = []
    for event in events:
        lines.append(describe(event, deployment))
        for a in event["alerts"]:
            lines.append("  - " + a["severity"] + " " + a["code"] + ": " + a["message"])
    if status_url:
        lines.append("Status: " + status_url)
    return "\n".join(lines)


def webhook_request(url, secret, body, now):
    """The signed request: Slack-compatible JSON (`text`) plus the structured events."""
    raw = json.dumps(body, sort_keys=True).encode("utf-8")
    headers = {"Content-Type": "application/json", "User-Agent": "impact-ops-check"}
    if secret:
        unix = str(int(now.timestamp()))
        digest = hmac.new(
            secret.encode("utf-8"), (unix + ".").encode("utf-8") + raw, hashlib.sha256
        ).hexdigest()
        headers["X-Impact-Signature"] = "t=" + unix + ",v1=" + digest
    return urllib.request.Request(url, data=raw, headers=headers, method="POST")


def verify_signature(secret, header, raw, now, tolerance=300):
    """For receivers (and the tests): True when `header` signs `raw` with `secret` within tolerance."""
    try:
        parts = dict(part.split("=", 1) for part in header.split(","))
        unix = int(parts["t"])
    except (AttributeError, KeyError, ValueError):
        return False
    if abs(now.timestamp() - unix) > tolerance:
        return False
    expected = hmac.new(
        secret.encode("utf-8"), (str(unix) + ".").encode("utf-8") + raw, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, parts.get("v1", ""))


def send_webhook(url, secret, events, deployment, status_url, now, opener=urllib.request.urlopen):
    body = {
        "schema": "impact-alert-v1",
        "deployment": deployment,
        "sent_at": stamp(now),
        "status_url": status_url or None,
        "events": events,
        "text": render_text(events, deployment, status_url),
    }
    try:
        with opener(webhook_request(url, secret, body, now), timeout=WEBHOOK_TIMEOUT) as response:
            code = getattr(response, "status", 200)
    except urllib.error.HTTPError as exc:
        return {"outcome": "failed", "error": "HTTP_" + str(exc.code)}
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return {"outcome": "failed", "error": type(exc).__name__}
    if 200 <= int(code) < 300:
        return {"outcome": "ok", "http_status": int(code)}
    return {"outcome": "failed", "error": "HTTP_" + str(code)}


def send_email(smtp, events, deployment, status_url, now, smtp_factory=smtplib.SMTP):
    """One message per check through the worker's SMTP settings; STARTTLS for any host that is not
    loopback (the staging capture); AUTH when a username is set. Errors are returned as classes."""
    recipients = [r.strip() for r in str(smtp.get("to") or "").split(",") if r.strip()]
    if not recipients or not smtp.get("host"):
        return {"outcome": "not_configured"}
    if smtp["host"] in LOOPBACK_HOSTS:
        return {"outcome": "skipped", "error": "LOOPBACK_SMTP"}
    message = EmailMessage()
    message["Subject"] = describe(events[0], deployment) + (
        " (+" + str(len(events) - 1) + " more)" if len(events) > 1 else ""
    )
    message["From"] = smtp.get("sender") or "impact@" + deployment
    message["To"] = ", ".join(recipients)
    message["Date"] = now.strftime("%a, %d %b %Y %H:%M:%S +0000")
    message.set_content(render_text(events, deployment, status_url) + "\n")
    try:
        with smtp_factory(smtp["host"], int(smtp.get("port") or 25), timeout=SMTP_TIMEOUT) as client:
            client.ehlo()
            if client.has_extn("starttls"):
                client.starttls()
                client.ehlo()
            if smtp.get("username"):
                client.login(smtp["username"], smtp.get("password") or "")
            client.send_message(message)
    except smtplib.SMTPResponseException as exc:
        return {"outcome": "failed", "error": "SMTP_" + str(exc.smtp_code)}
    except (smtplib.SMTPException, OSError) as exc:
        return {"outcome": "failed", "error": type(exc).__name__}
    return {"outcome": "ok", "recipients": len(recipients)}


def notify(
    ops_dir,
    env,
    now,
    renotify_seconds=RENOTIFY_SECONDS,
    deployment="",
    status_url="",
    opener=None,
    smtp_factory=None,
):
    """Read the alerts and the state, deliver the transitions, record the outcome; returns the
    summary that is printed. Secrets come from `env` only (ALERT_WEBHOOK_SECRET, SMTP_PASSWORD)."""
    status = read_json(os.path.join(ops_dir, "ops-status.json"), {}) or {}
    state_path = os.path.join(ops_dir, STATE_FILE)
    state, events = transitions(status.get("alerts"), read_json(state_path, {}) or {}, now, renotify_seconds)
    channels = {}
    if events:
        if env.get("ALERT_WEBHOOK_URL"):
            channels["webhook"] = send_webhook(
                env["ALERT_WEBHOOK_URL"],
                env.get("ALERT_WEBHOOK_SECRET") or "",
                events,
                deployment or "server",
                status_url,
                now,
                **({"opener": opener} if opener else {}),
            )
        if env.get("ALERT_EMAIL_TO"):
            channels["email"] = send_email(
                {
                    "to": env.get("ALERT_EMAIL_TO"),
                    "host": env.get("SMTP_HOST") or "",
                    "port": env.get("SMTP_PORT") or 25,
                    "username": env.get("SMTP_USERNAME") or "",
                    "password": env.get("SMTP_PASSWORD") or "",
                    "sender": env.get("SMTP_FROM") or "",
                },
                events,
                deployment or "server",
                status_url,
                now,
                **({"smtp_factory": smtp_factory} if smtp_factory else {}),
            )
    configured = [name for name in channels]
    accepted = any(result.get("outcome") == "ok" for result in channels.values())
    if events and (accepted or not configured):
        # Delivered through at least one channel, or nothing is configured (the status page is the
        # only signal, as before): the transitions are consumed. Otherwise they are retried next check.
        for event in events:
            if event["event"] in {"NEW", "REMINDER"}:
                for entry in event["alerts"]:
                    key = alert_key(entry)
                    if key in state["active"]:
                        state["active"][key]["last_notified"] = stamp(now)
    elif events:
        # Not delivered: NEW alerts stay recorded with last_notified null (NEW again next check),
        # reminders keep their old last_notified, and a CLEARED alert stays in the state so its
        # clearance is reported by the next successful delivery.
        for event in events:
            if event["event"] == "CLEARED":
                for entry in event["alerts"]:
                    state["active"][alert_key(entry)] = {k: v for k, v in entry.items() if k != "cleared_at"}
    record = {
        "at": stamp(now),
        "events": [{"event": e["event"], "codes": sorted(a["code"] for a in e["alerts"])} for e in events],
        "channels": channels,
        "consumed": bool(events and (accepted or not configured)),
    }
    if events:
        state["deliveries"] = ([*state.get("deliveries", []), record])[-MAX_DELIVERY_RECORDS:]
    state["checked_at"] = stamp(now)
    write_json(state_path, state, mode=0o600)
    return record


def drill_record(env, now):
    started = datetime.fromtimestamp(int(env["STARTED"]), timezone.utc)
    finished = datetime.fromtimestamp(int(env.get("FINISHED") or now.timestamp()), timezone.utc)

    def parsed(name):
        try:
            value = json.loads(env.get(name) or "null")
        except ValueError:
            return None
        return value if isinstance(value, dict) else None

    restore, check = parsed("RESTORE"), parsed("CHECK")
    manifest = (restore or {}).get("manifest") or {}
    created = parse_time(manifest.get("finished_at"))
    return {
        "outcome": env["OUTCOME"],
        "error": env.get("ERROR") or None,
        "started_at": stamp(started),
        "finished_at": stamp(finished),
        # End to end: throwaway database start, checksum verification, roles, both restores, every
        # check and the migrator pass. The measured recovery time of the databases at this size.
        "duration_seconds": int((finished - started).total_seconds()),
        "set": (restore or {}).get("set") or None,
        "set_created_at": manifest.get("finished_at"),
        "backup_age_hours": hours_between(created, started) if created else None,
        "set_bytes": sum(int(f.get("bytes") or 0) for f in manifest.get("files") or []),
        "set_schema_version": manifest.get("schema_version"),
        "restore_seconds": (restore or {}).get("seconds"),
        "restore_failed_step": (restore or {}).get("failed_step") or None,
        "checks": (check or {}).get("checks"),
        "check_seconds": (check or {}).get("seconds"),
        "restored": (check or {}).get("restored"),
        "objects": (check or {}).get("objects"),
        "blobs": (check or {}).get("blobs"),
        "migration": (check or {}).get("migration"),
        "check_error": (check or {}).get("error"),
    }


def main(argv=None, env=os.environ, now=None):
    now = now or datetime.now(timezone.utc)
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    ev = sub.add_parser("evaluate")
    ev.add_argument("--ops-dir", required=True)
    ev.add_argument("--containers", required=True)
    ev.add_argument("--app", required=True)
    ev.add_argument("--disk", required=True)
    ev.add_argument("--status-file", action="append", default=[])
    ev.add_argument("--secrets-file", default="")
    dr = sub.add_parser("drill-result")
    dr.add_argument("path")
    nt = sub.add_parser("notify")
    nt.add_argument("--ops-dir", required=True)
    nt.add_argument("--renotify-seconds", type=int, default=RENOTIFY_SECONDS)
    nt.add_argument("--deployment", default="")
    nt.add_argument("--status-url", default="")
    args = parser.parse_args(argv)
    if args.command == "drill-result":
        write_json(args.path, drill_record(env, now))
        return 0
    if args.command == "notify":
        record = notify(
            args.ops_dir,
            env,
            now,
            renotify_seconds=max(60, args.renotify_seconds),
            deployment=args.deployment,
            status_url=args.status_url,
        )
        print(json.dumps(record, sort_keys=True))
        return 0
    view, alerts = evaluate(
        read_json(os.path.join(args.ops_dir, "backup-status.json")),
        read_json(os.path.join(args.ops_dir, "restore-drill.json")),
        read_json(args.containers, []),
        read_json(args.app),
        read_json(args.disk, {}),
        now,
    )
    values = secret_values(args.secrets_file) if args.secrets_file else []
    view, alerts = scrub(view, values), scrub(alerts, values)
    write_json(os.path.join(args.ops_dir, "ops-status.json"), {"operations": view, "alerts": alerts})
    for path in args.status_file:
        merge_into_status(path, view, alerts)
    print(json.dumps({"alerts": [a["code"] for a in alerts], "checked_at": view["checked_at"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
