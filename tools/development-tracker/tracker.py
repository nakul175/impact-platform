"""Read-only, loopback-only development tracker. No product data or credentials."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "docs" / "development-tracker"
STATIC = Path(__file__).resolve().parent
MAX_BYTES = 1_048_576
STATES = {"QUEUED", "INSPECTING", "BUILDING", "REVIEWING", "TESTING", "BLOCKED", "COMPLETE"}
CONFIDENCE = {"UNESTIMATED", "LOW", "MEDIUM", "HIGH"}
STREAM_FIELDS = {
    "id",
    "title",
    "domain",
    "owner",
    "status",
    "summary",
    "next_step",
    "eta",
    "delivered",
    "evidence",
    "blockers",
    "updated_at",
    "history",
}
SPRINT_FIELDS = {
    "schema_version",
    "title",
    "branch",
    "started_at",
    "deadline",
    "updated_at",
    "status",
    "active_agent_limit",
    "stream_ids",
    "rollup",
    "limits",
}
ID = re.compile(r"[a-z][a-z0-9-]{0,63}\Z")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def instant(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("An instant must be an ISO UTC string")
    if not value.endswith("Z"):
        raise ValueError("An instant must end in Z")
    parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    return parsed


def plain(value: object, maximum: int = 2000) -> None:
    if (
        not isinstance(value, str)
        or len(value) > maximum
        or any(ord(c) < 32 and c not in "\n\t" for c in value)
    ):
        raise ValueError("Expected bounded plain text")


def identifier(value: object) -> str:
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise ValueError("Invalid stream identifier")
    return value


def closed(value: object, fields: set[str]) -> dict:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError("Missing or unsupported fields")
    return value


def validate_evidence(item: object, root: Path | None = None) -> None:
    row = closed(item, {"title", "path", "result", "scope", "recorded_at"})
    for field in ("title", "result", "scope"):
        plain(row[field], 1000)
    instant(row["recorded_at"])
    path = row["path"]
    if not isinstance(path, str) or len(path) > 250:
        raise ValueError("Invalid evidence path")
    parts = Path(path).parts
    if not parts or parts[0] not in {"docs", "qualification", "tools", "apps", "packages", "infrastructure"}:
        raise ValueError("Evidence must name a repository source or recorded result")
    if Path(path).is_absolute() or any(
        p in {".", "..", ".local", "secrets.env"} or p.startswith(".") for p in parts
    ):
        raise ValueError("Unsafe evidence path")
    if root is not None:
        candidate = root / path
        if not candidate.is_file() or not candidate.resolve().is_relative_to(root.resolve()):
            raise ValueError("Evidence must already exist inside the repository")


def validate_stream(value: object, expected_id: str | None = None, root: Path | None = None) -> dict:
    row = closed(value, STREAM_FIELDS)
    identifier(row["id"])
    if expected_id is not None and row["id"] != expected_id:
        raise ValueError("Stream identifier does not match its file")
    for field in ("title", "domain", "owner", "summary", "next_step"):
        plain(row[field])
    if row["status"] not in STATES:
        raise ValueError("Unsupported workstream status")
    instant(row["updated_at"])
    eta = closed(row["eta"], {"earliest", "latest", "confidence", "basis"})
    plain(eta["basis"])
    if eta["confidence"] not in CONFIDENCE:
        raise ValueError("Unsupported confidence")
    if eta["confidence"] == "UNESTIMATED":
        if eta["earliest"] is not None or eta["latest"] is not None:
            raise ValueError("Unestimated work cannot have a fabricated deadline")
    else:
        if instant(eta["earliest"]) > instant(eta["latest"]):
            raise ValueError("ETA range is reversed")
    for field in ("delivered", "blockers"):
        if not isinstance(row[field], list) or len(row[field]) > 50:
            raise ValueError("List is too long")
        for text in row[field]:
            plain(text)
    if not isinstance(row["evidence"], list) or len(row["evidence"]) > 50:
        raise ValueError("Too many evidence records")
    for item in row["evidence"]:
        validate_evidence(item, root)
    if row["status"] == "COMPLETE" and (not row["delivered"] or not row["evidence"]):
        raise ValueError("A complete slice requires named deliverables and evidence")
    if not isinstance(row["history"], list) or len(row["history"]) > 100:
        raise ValueError("History must be bounded")
    for item in row["history"]:
        entry = closed(item, {"at", "status", "summary", "eta"})
        instant(entry["at"])
        if entry["status"] not in STATES:
            raise ValueError("Invalid historical state")
        plain(entry["summary"])
        previous = dict(row, eta=entry["eta"], history=[])
        validate_stream(previous, expected_id, root=None)
    return row


def validate_sprint(value: object) -> dict:
    row = closed(value, SPRINT_FIELDS)
    if row["schema_version"] != 1:
        raise ValueError("Unsupported tracker schema")
    for field in ("title", "branch"):
        plain(row[field])
    for field in ("started_at", "deadline", "updated_at"):
        instant(row[field])
    if instant(row["started_at"]) >= instant(row["deadline"]):
        raise ValueError("Sprint window is reversed")
    if row["status"] not in {"ACTIVE", "COMPLETED", "PAUSED", "WINDOW_ENDED"}:
        raise ValueError("Unsupported sprint status")
    if type(row["active_agent_limit"]) is not int or not 1 <= row["active_agent_limit"] <= 100:
        raise ValueError("Invalid concurrency limit")
    if not isinstance(row["stream_ids"], list) or len(row["stream_ids"]) > 100:
        raise ValueError("Invalid stream inventory")
    ids = [identifier(item) for item in row["stream_ids"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate stream identifier")
    rollup = closed(
        row["rollup"],
        {
            "summary",
            "planned_increments",
            "integrated_increments",
            "verified_increments",
            "active_agents",
            "next_checkpoint",
        },
    )
    plain(rollup["summary"])
    for field in ("planned_increments", "integrated_increments", "verified_increments", "active_agents"):
        if type(rollup[field]) is not int or rollup[field] < 0:
            raise ValueError("Invalid bounded count")
    if not rollup["verified_increments"] <= rollup["integrated_increments"] <= rollup["planned_increments"]:
        raise ValueError("Verified <= integrated <= planned is required")
    if rollup["active_agents"] > row["active_agent_limit"]:
        raise ValueError("Active agents exceed the actual concurrency limit")
    if rollup["next_checkpoint"] is not None:
        instant(rollup["next_checkpoint"])
    if not isinstance(row["limits"], list) or len(row["limits"]) > 30:
        raise ValueError("Invalid limits")
    for item in row["limits"]:
        plain(item)
    return row


def parse_json(raw: bytes) -> object:
    if len(raw) > MAX_BYTES:
        raise ValueError("Source grew beyond the bound")

    def unique_pairs(pairs: list[tuple]) -> dict:
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("Duplicate JSON key")
            value[key] = item
        return value

    return json.loads(
        raw,
        object_pairs_hook=unique_pairs,
        parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Non-finite JSON")),
    )


def read_json(path: Path) -> object:
    if path.is_symlink() or path.stat().st_size > MAX_BYTES:
        raise ValueError("Source is not a bounded regular JSON file")
    return parse_json(path.read_bytes())


def snapshot(data: Path = DATA) -> dict:
    sprint = validate_sprint(read_json(data / "sprint.json"))
    streams, errors = [], []
    for stream_id in sprint["stream_ids"]:
        try:
            streams.append(validate_stream(read_json(data / "streams" / f"{stream_id}.json"), stream_id))
        except (OSError, ValueError, TypeError, RecursionError):
            errors.append(
                {
                    "stream_id": stream_id,
                    "message": "This stream file is missing or invalid; its progress is not available.",
                }
            )
    backlog = read_json(data / "backlog.json")
    if not isinstance(backlog, dict):
        raise ValueError("Backlog must be an object")
    return {
        "served_at": utc_now(),
        "sprint": sprint,
        "streams": streams,
        "errors": errors,
        "backlog": backlog,
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        hosts = self.headers.get_all("Host", [])
        port = self.server.server_address[1]
        if len(hosts) != 1 or hosts[0].lower() not in {
            f"127.0.0.1:{port}",
            f"localhost:{port}",
        }:
            self.respond(421, b"Unrecognised local host", "text/plain; charset=utf-8")
            return
        route = urlsplit(self.path).path
        if route == "/api/status":
            try:
                payload = json.dumps(snapshot(), ensure_ascii=False).encode("utf-8")
            except (OSError, ValueError, TypeError, RecursionError):
                self.respond(
                    503,
                    b'{"error":"Tracker source is unavailable or invalid. Last known information may be stale."}',
                    "application/json; charset=utf-8",
                )
                return
            self.respond(200, payload, "application/json; charset=utf-8")
            return
        files = {
            "/": ("index.html", "text/html"),
            "/index.html": ("index.html", "text/html"),
            "/app.js": ("app.js", "text/javascript"),
            "/styles.css": ("styles.css", "text/css"),
        }
        if route not in files:
            self.respond(404, b"Not found", "text/plain; charset=utf-8")
            return
        name, mime = files[route]
        self.respond(200, (STATIC / name).read_bytes(), f"{mime}; charset=utf-8")

    def respond(self, status: int, payload: bytes, mime: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'",
        )
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: object) -> None:
        # No request URLs, query parameters or raw source contents in logs.
        return


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8170)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("Use an unprivileged port between 1024 and 65535")
    snapshot()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Live development tracker: http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
