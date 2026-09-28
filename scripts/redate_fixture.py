"""Regenerate the synthetic fixture's expiry ahead of its current expiry instant.

The fixture is versioned data, never extended silently: this script rewrites every occurrence of
the current expiry instant (FIXTURE_EXPIRES_AT) in specification/fixtures/seed.sql, both inside
immutable revision payloads and in the projection columns, recomputes each changed revision's
payload_sha256 with the canonicalisation the runtime uses (impact_api.store.hash_data), rewrites
records.json, moves the constant in scripts/fixture_support.py that the bootstrap scripts read, and
stamps api-fixture.json with fixture_version and fixture_expires_at. Before touching anything it
recomputes every existing payload hash in seed.sql and stops unless all of them match.

    scripts/redate_fixture.py --expires 2027-09-01T00:00:00Z [--membership-expires <instant>]

--membership-expires moves the one external membership expiry (2026-12-23 in the 2026-09-25
fixture), which is the same kind of time bomb; it defaults to the new authority expiry.
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
import fixture_support  # noqa: E402

FIXTURES = ROOT / "specification/fixtures"
REVISION = re.compile(
    r"^(?P<head>INSERT INTO impact\.object_revision\([^)]*\) VALUES\(.*?)'(?P<payload>\{.*\})'(?P<cast>::jsonb)?,decode\('(?P<sha>[0-9a-f]{64})','hex'\)(?P<tail>.*)$",
    re.M,
)
INSTANT = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
MEMBERSHIP_EXPIRES_AT = "2026-12-23T00:00:00Z"


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


def redate_seed(seed, mapping):
    changed = []

    def rewrite(match):
        payload = match.group("payload")
        for old, new in mapping.items():
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

    seed = REVISION.sub(rewrite, seed)
    column_changes = 0
    for old, new in mapping.items():
        seed, n = re.subn("'" + re.escape(old) + "'", "'" + new + "'", seed)
        column_changes += n
    return seed, len(changed), column_changes


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
    current = fixture_support.FIXTURE_EXPIRES_AT
    new = instant(args.expires)
    membership_new = instant(args.membership_expires or new)
    if new <= current:
        raise SystemExit("The new expiry must be later than the current one, " + current)
    mapping = {current: new}
    seed_path = FIXTURES / "seed.sql"
    seed = seed_path.read_text()
    if MEMBERSHIP_EXPIRES_AT in seed and membership_new != MEMBERSHIP_EXPIRES_AT:
        mapping[MEMBERSHIP_EXPIRES_AT] = membership_new
    else:
        print("No external membership expiry " + MEMBERSHIP_EXPIRES_AT + " to move")
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
    seed, payload_rows, column_changes = redate_seed(seed, mapping)
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
    records_path = FIXTURES / "records.json"
    records = json.loads(records_path.read_text())
    before = json.dumps(records)
    records = redate_json(records, mapping)
    changed = sum(before.count(old) for old in mapping)
    write_like(records_path, json.dumps(records, indent=2) + "\n")
    print("records.json: " + str(changed) + " values moved")
    support = ROOT / "scripts/fixture_support.py"
    text = support.read_text()
    line = 'FIXTURE_EXPIRES_AT = "' + current + '"'
    if text.count(line) != 1:
        raise SystemExit("fixture_support.py does not carry the expected constant")
    support.write_text(text.replace(line, 'FIXTURE_EXPIRES_AT = "' + new + '"'))
    # The rewritten line has the same length, so a cached module compiled within the same
    # second would still validate; drop the cache rather than trust the mtime check.
    for cached in (ROOT / "scripts/__pycache__").glob("fixture_support.*.pyc"):
        cached.unlink()
    print("fixture_support.py: FIXTURE_EXPIRES_AT " + current + " -> " + new)
    api_path = FIXTURES / "api-fixture.json"
    api = json.loads(api_path.read_text())
    stamped = {}
    for key, value in api.items():
        stamped[key] = value
        if key == "fixture_id":
            stamped["fixture_version"] = args.version or datetime.now(timezone.utc).strftime("%Y-%m-%d")
            stamped["fixture_expires_at"] = new
    write_like(api_path, json.dumps(stamped, indent=2) + "\n")
    print("api-fixture.json: fixture_version " + stamped["fixture_version"] + ", fixture_expires_at " + new)
    return 0


if __name__ == "__main__":
    sys.exit(main())
