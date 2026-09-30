"""Regenerate the synthetic fixture's expiry ahead of its current expiry instant.

The fixture is versioned data, never extended silently: this script rewrites every occurrence of
the current expiry instant (FIXTURE_EXPIRES_AT) in specification/fixtures/seed.sql, both inside
immutable revision payloads and in the projection columns, recomputes each changed revision's
payload_sha256 with the canonicalisation the runtime uses (impact_api.store.hash_data), rewrites
records.json, moves the constant in scripts/fixture_support.py that the bootstrap scripts read, and
stamps api-fixture.json with fixture_version and fixture_expires_at. Before touching anything it
recomputes every existing payload hash in seed.sql and stops unless all of them match.

    scripts/redate_fixture.py --expires 2027-09-01T00:00:00Z [--membership-expires <instant>]

--membership-expires moves the one external membership expiry (the `member_partner` record of
records.json, whose current value is read from there rather than assumed), which is the same
kind of time bomb; it defaults to the new authority expiry. When neither instant would change,
the script verifies the hashes, reports that there is nothing to change and writes nothing.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/api"))
sys.path.insert(0, str(ROOT / "scripts"))
from impact_api.store import hash_data  # noqa: E402

FIXTURES = ROOT / "specification/fixtures"
SUPPORT = ROOT / "scripts/fixture_support.py"
CONSTANT = re.compile(r'^FIXTURE_EXPIRES_AT = "(?P<instant>[^"]+)"$', re.M)
REVISION = re.compile(
    r"^(?P<head>INSERT INTO impact\.object_revision\([^)]*\) VALUES\(.*?)'(?P<payload>\{.*\})'(?P<cast>::jsonb)?,decode\('(?P<sha>[0-9a-f]{64})','hex'\)(?P<tail>.*)$",
    re.M,
)
INSTANT = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
MEMBERSHIP_RECORD = "member_partner"


def instant(value):
    if not INSTANT.fullmatch(value):
        raise SystemExit("Instants must look like 2027-09-01T00:00:00Z: " + value)
    datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return value


def parse_payload(text):
    return json.loads(text.replace("''", "'"))


def verify_hashes(seed):
    """Every revision row's payload_sha256 equals the canonical hash of its payload."""
    rows = list(REVISION.finditer(seed))
    mismatches = [
        m.group("sha") for m in rows if hash_data(parse_payload(m.group("payload"))).hex() != m.group("sha")
    ]
    return len(rows), mismatches


def write_like(path, text):
    """Keep the file's trailing-newline convention so the diff shows only the moved values."""
    original = path.read_text()
    path.write_text(text if original.endswith("\n") else text.rstrip("\n"))


def current_expiry():
    """The constant as written in scripts/fixture_support.py, read from the source text rather
    than imported: a stale bytecode cache must never decide what the fixture currently says."""
    match = CONSTANT.search(SUPPORT.read_text())
    if not match:
        raise SystemExit("fixture_support.py does not carry the FIXTURE_EXPIRES_AT constant")
    return instant(match.group("instant"))


def membership_expiry(records):
    """The external membership record and its current expiry, read from records.json."""
    record = next((r for r in records if r["key"] == MEMBERSHIP_RECORD), None)
    if not record or not record["data"].get("expires_at"):
        raise SystemExit("records.json carries no " + MEMBERSHIP_RECORD + " record with an expires_at")
    return record["object_id"], record["data"]["expires_at"]


def redate_seed(seed, mapping, membership_object, membership_mapping):
    """Rewrite seed.sql line by line: the external membership's own rows (its revision and its
    projection carry the object id) take the membership mapping, every other line the authority
    mapping, so the two instants move independently even when they currently coincide."""
    changed = []

    def rewrite(match, line_mapping):
        payload = match.group("payload")
        for old, new in line_mapping.items():
            payload = payload.replace(old, new)
        if payload == match.group("payload"):
            return match.group(0)
        changed.append(match.group("sha"))
        sha = hash_data(parse_payload(payload)).hex()
        return (
            match.group("head")
            + "'"
            + payload
            + "'"
            + (match.group("cast") or "")
            + ",decode('"
            + sha
            + "','hex')"
            + match.group("tail")
        )

    column_changes = 0
    lines = []
    for line in seed.split("\n"):
        line_mapping = membership_mapping if membership_object in line else mapping
        line = REVISION.sub(lambda match: rewrite(match, line_mapping), line)
        for old, new in line_mapping.items():
            line, n = re.subn("'" + re.escape(old) + "'", "'" + new + "'", line)
            column_changes += n
        lines.append(line)
    return "\n".join(lines), len(changed), column_changes


def redate_json(value, mapping):
    if isinstance(value, dict):
        return {k: redate_json(v, mapping) for k, v in value.items()}
    if isinstance(value, list):
        return [redate_json(v, mapping) for v in value]
    return mapping.get(value, value) if isinstance(value, str) else value


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--expires", required=True, help="New expiry instant for every fixture authority")
    parser.add_argument("--membership-expires", help="New expiry for the external fixture membership")
    parser.add_argument("--version", help="fixture_version stamp; defaults to today's UTC date")
    args = parser.parse_args()
    current = current_expiry()
    new = instant(args.expires)
    membership_new = instant(args.membership_expires or new)
    if new < current:
        raise SystemExit("The new expiry must not be earlier than the current one, " + current)
    seed_path = FIXTURES / "seed.sql"
    seed = seed_path.read_text()
    records_path = FIXTURES / "records.json"
    records = json.loads(records_path.read_text())
    membership_object, membership_current = membership_expiry(records)
    if membership_current not in seed:
        raise SystemExit(
            "records.json says the external membership expires at "
            + membership_current
            + " but seed.sql carries no such instant"
        )
    mapping = {current: new} if new != current else {}
    membership_mapping = {membership_current: membership_new} if membership_new != membership_current else {}
    rows, mismatches = verify_hashes(seed)
    if not rows or mismatches:
        raise SystemExit(
            "Refusing to redate: "
            + str(len(mismatches))
            + " of "
            + str(rows)
            + " revision hashes do not match the canonical payload hash"
        )
    print("Verified " + str(rows) + "/" + str(rows) + " revision payload hashes in seed.sql")
    if not mapping and not membership_mapping:
        print(
            "Nothing to change: the fixture authority already expires at "
            + current
            + " and the external membership at "
            + membership_current
        )
        return 0
    print(
        "External membership expiry "
        + membership_current
        + (" -> " + membership_new if membership_mapping else " unchanged")
    )
    seed, payload_rows, column_changes = redate_seed(seed, mapping, membership_object, membership_mapping)
    for old in mapping:
        if old in seed:
            raise SystemExit("An occurrence of " + old + " survived in seed.sql")
    rows_after, mismatches_after = verify_hashes(seed)
    if rows_after != rows or mismatches_after:
        raise SystemExit("Rewritten seed.sql failed hash verification")
    seed_path.write_text(seed)
    print(
        "seed.sql: "
        + str(payload_rows)
        + " revision rows re-hashed, "
        + str(column_changes)
        + " column values moved"
    )
    redated = [
        redate_json(record, membership_mapping if record["key"] == MEMBERSHIP_RECORD else mapping)
        for record in records
    ]
    changed = sum(1 for before, after in zip(records, redated) if before != after)
    write_like(records_path, json.dumps(redated, indent=2) + "\n")
    print("records.json: " + str(changed) + " records moved")
    text = SUPPORT.read_text()
    line = 'FIXTURE_EXPIRES_AT = "' + current + '"'
    if text.count(line) != 1:
        raise SystemExit("fixture_support.py does not carry the expected constant")
    SUPPORT.write_text(text.replace(line, 'FIXTURE_EXPIRES_AT = "' + new + '"'))
    # The rewritten line has the same length, so a cached module compiled within the same
    # second would still validate for the scripts that import it; drop the cache rather than
    # trust the mtime check.
    for cached in (ROOT / "scripts/__pycache__").glob("fixture_support.*.pyc"):
        cached.unlink()
    print("fixture_support.py: FIXTURE_EXPIRES_AT " + current + " -> " + new)
    api_path = FIXTURES / "api-fixture.json"
    api = json.loads(api_path.read_text())
    version = args.version or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # The stamp follows fixture_id on a first stamping and keeps its place afterwards; an
    # existing stamp is replaced, never copied back over the new one.
    stamped = {}
    for key, value in api.items():
        if key in {"fixture_version", "fixture_expires_at"}:
            continue
        stamped[key] = value
        if key == "fixture_id":
            stamped["fixture_version"], stamped["fixture_expires_at"] = version, new
    if stamped.get("fixture_expires_at") != new:
        raise SystemExit("api-fixture.json carries no fixture_id to stamp after")
    write_like(api_path, json.dumps(stamped, indent=2) + "\n")
    print("api-fixture.json: fixture_version " + version + ", fixture_expires_at " + new)
    return 0


if __name__ == "__main__":
    sys.exit(main())
