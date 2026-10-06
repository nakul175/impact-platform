"""Atomically update exactly one owned tracker file using a structured JSON patch."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from tracker import (
    DATA,
    MAX_BYTES,
    ROOT,
    SPRINT_FIELDS,
    STREAM_FIELDS,
    identifier,
    parse_json,
    read_json,
    utc_now,
    validate_sprint,
    validate_stream,
)


def atomic_json(path: Path, value: object) -> None:
    encoded = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if len(encoded) > MAX_BYTES:
        raise ValueError("Result exceeds the source-file byte limit")
    descriptor, temporary = tempfile.mkstemp(prefix=".tracker-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def apply_patch(
    data: Path,
    patch: object,
    stream_id: str | None = None,
    expected_updated: str | None = None,
    root: Path | None = ROOT,
) -> dict:
    if not isinstance(patch, dict):
        raise ValueError("Patch must be a JSON object")
    sprint = validate_sprint(read_json(data / "sprint.json"))
    if stream_id is None:
        path = data / "sprint.json"
        before = sprint
        writable = SPRINT_FIELDS - {"schema_version", "updated_at"}
    else:
        identifier(stream_id)
        if stream_id not in sprint["stream_ids"]:
            raise ValueError("Stream must first be registered by the integrator")
        path = data / "streams" / f"{stream_id}.json"
        before = validate_stream(read_json(path), stream_id)
        writable = STREAM_FIELDS - {"id", "updated_at", "history"}
    if set(patch) - writable:
        raise ValueError("Patch includes a server-owned or unsupported field")
    if expected_updated is not None and before["updated_at"] != expected_updated:
        raise ValueError("Source changed; re-read before updating")
    after = dict(before, **patch, updated_at=utc_now())
    if stream_id is None:
        validate_sprint(after)
    else:
        changed = any(after[key] != before[key] for key in writable)
        if changed:
            entry = {
                "at": after["updated_at"],
                "status": after["status"],
                "summary": after["summary"],
                "eta": after["eta"],
            }
            after["history"] = (before["history"] + [entry])[-100:]
        validate_stream(after, stream_id, root)
    atomic_json(path, after)
    return after


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--stream")
    destination.add_argument("--sprint", action="store_true")
    parser.add_argument("--file", required=True, help="JSON patch file; '-' reads stdin")
    parser.add_argument("--expect-updated-at", help="Optional optimistic concurrency check")
    args = parser.parse_args()
    try:
        if args.file == "-":
            raw = sys.stdin.buffer.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError("Patch is too large")
            patch = parse_json(raw)
        else:
            patch = read_json(Path(args.file))
        result = apply_patch(DATA, patch, args.stream, args.expect_updated_at)
    except (OSError, ValueError, TypeError, RecursionError):
        parser.exit(
            1,
            "Tracker update refused: invalid patch, stale source, missing evidence or unavailable source file.\n",
        )
    print(
        json.dumps(
            {"id": result.get("id", "sprint"), "updated_at": result["updated_at"], "status": result["status"]}
        )
    )


if __name__ == "__main__":
    main()
