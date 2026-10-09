"""Immutable server-owned editorial guidance, bound to an exact saved plan revision."""

from copy import deepcopy
import hmac
import json
import logging
from pathlib import Path
from uuid import uuid4

from jsonschema import Draft202012Validator, FormatChecker
from psycopg.types.json import Jsonb

from .ai_enablement_catalog import catalog
from .ai_solutions_catalog import SolutionsCatalogInvalid, solutions_catalog
from .ai_task_practice import task_templates
from .domain import DomainError
from .store import canonical, hash_data

SCHEMA_V1 = "nonprofit-ai-guidance-v1"
# US-DC-04 (build 0.39.0): every tool listing carries its commercial disclosure.
SCHEMA_V2 = "nonprofit-ai-guidance-v2"
# New revisions are captured in the current edition; every earlier edition keeps its reader, so a
# revision saved under v1 stays readable exactly as captured (migration 0043 admits both labels).
SCHEMA_VERSION = SCHEMA_V2
MAX_SNAPSHOT_BYTES = 262144
COMPONENTS = ("catalog", "solutions", "practice")
LOG = logging.getLogger("impact")
DISCLAIMER = (
    "Editorial guidance captured for this saved revision, including self-checks and manual practice. "
    "It is not a supplier quote, competency certification, procurement approval or official impact result. "
    "Unavailable historical wording is not reconstructed from current content."
)
# Each file is a frozen archive format. A structural editorial change needs a new schema edition
# with a retained reader, never a regeneration of an existing file. v2 differs from v1 only by the
# required commercial_disclosure of each solutions listing (catalog and practice are identical).
SCHEMA_FILES = {SCHEMA_V1: "ai_content_schema_v1.json", SCHEMA_V2: "ai_content_schema_v2.json"}
EDITIONS = {
    version: json.loads(Path(__file__).with_name(name).read_text()) for version, name in SCHEMA_FILES.items()
}
READERS = {
    version: {
        name: Draft202012Validator(schema, format_checker=FormatChecker())
        for name, schema in components.items()
    }
    for version, components in EDITIONS.items()
}


def _unreadable():
    raise DomainError("SERVICE_UNAVAILABLE", 503, reason="AI_GUIDANCE_UNREADABLE")


def _validate_bundle(payload):
    """A bundle is readable only under the reader of the edition it names."""
    if not isinstance(payload, dict) or set(payload) != {"schema_version", *COMPONENTS}:
        _unreadable()
    version = payload["schema_version"]
    if not isinstance(version, str) or version not in READERS:
        _unreadable()
    for name in COMPONENTS:
        value = payload[name]
        if value is None:
            if name != "practice":
                _unreadable()
            continue
        if not READERS[version][name].is_valid(value):
            _unreadable()
        if not isinstance(value.get("content_version"), str) or not 1 <= len(value["content_version"]) <= 100:
            _unreadable()
    if len(canonical(payload)) > MAX_SNAPSHOT_BYTES:
        _unreadable()


def _bound(c, tenant, object_id, revision_id):
    return c.execute(
        "SELECT s.* FROM impact.ai_plan_content_binding b "
        "JOIN impact.ai_content_snapshot s ON s.tenant_id=b.tenant_id AND s.snapshot_id=b.snapshot_id "
        "WHERE b.tenant_id=%s AND b.object_id=%s AND b.revision_id=%s",
        (tenant, object_id, revision_id),
    ).fetchone()


def _verified(row):
    if not row or row["schema_version"] not in EDITIONS:
        _unreadable()
    payload = row["payload"]
    _validate_bundle(payload)
    # The row's edition label and the hashed payload's own label must agree.
    if payload["schema_version"] != row["schema_version"]:
        _unreadable()
    if not hmac.compare_digest(bytes(row["payload_sha256"]), hash_data(payload)):
        _unreadable()
    return deepcopy(payload)


def capture(c, ctx, receipt, saved_data, previous=None, retained_planning=False):
    """Called after the governed revision write, inside that same locked transaction."""
    try:
        solutions = solutions_catalog()
    except SolutionsCatalogInvalid as error:
        # A listing without a valid commercial disclosure is never archived: the save rolls back.
        LOG.error("AI solutions catalogue refused at archive capture: %s", error)
        raise DomainError("SERVICE_UNAVAILABLE", 503, reason="AI_SOLUTIONS_CATALOG_INVALID") from None
    payload = {
        "schema_version": SCHEMA_VERSION,
        "catalog": catalog(),
        "solutions": solutions,
        "practice": task_templates(),
    }
    # The catalogue already includes the exact learning paths and their self-checks.
    versions = saved_data["content_versions"]
    if any(payload[name]["content_version"] != versions[name] for name in ("catalog", "solutions")):
        _unreadable()
    worksheet = saved_data.get("planning", {}).get("task_practice")
    if retained_planning and worksheet is not None:
        retained_version = versions.get("practice")
        if payload["practice"]["content_version"] != retained_version:
            payload["practice"] = None
            old = _bound(c, ctx.tenant_id, previous["object_id"], previous["head_revision"])
            if old:
                archived = _verified(old)["practice"]
                if archived and archived["content_version"] == retained_version:
                    payload["practice"] = archived
    elif worksheet is not None and payload["practice"]["content_version"] != versions.get("practice"):
        _unreadable()
    _validate_bundle(payload)
    digest = hash_data(payload)
    for name in COMPONENTS:
        component = payload[name]
        if component is None:
            continue
        # name is one of the fixed server component identifiers, never client input.
        published = c.execute(
            "SELECT * FROM impact.ai_content_snapshot WHERE tenant_id=%s AND payload->'"
            + name
            + "'->>'content_version'=%s ORDER BY captured_at,snapshot_id LIMIT 1",
            (ctx.tenant_id, component["content_version"]),
        ).fetchone()
        if published and not hmac.compare_digest(hash_data(_verified(published)[name]), hash_data(component)):
            raise DomainError("SERVICE_UNAVAILABLE", 503, reason="AI_GUIDANCE_VERSION_CHANGED")
    existing = c.execute(
        "SELECT * FROM impact.ai_content_snapshot WHERE tenant_id=%s AND payload_sha256=%s",
        (ctx.tenant_id, digest),
    ).fetchone()
    if existing:
        if _verified(existing) != payload:
            _unreadable()
        snapshot_id = existing["snapshot_id"]
    else:
        snapshot_id = str(uuid4())
        c.execute(
            "INSERT INTO impact.ai_content_snapshot "
            "(tenant_id,snapshot_id,schema_version,payload,payload_sha256,captured_at) "
            "VALUES(%s,%s,%s,%s,%s,statement_timestamp())",
            (ctx.tenant_id, snapshot_id, payload["schema_version"], Jsonb(payload), digest),
        )
    c.execute(
        "INSERT INTO impact.ai_plan_content_binding(tenant_id,object_id,revision_id,snapshot_id) "
        "VALUES(%s,%s,%s,%s)",
        (ctx.tenant_id, receipt["object_id"], receipt["revision_id"], snapshot_id),
    )


def availability(c, tenant, object_id, revision_id):
    """A complete claim requires a real verified binding, never version metadata alone."""
    row = _bound(c, tenant, object_id, revision_id)
    return bool(row and _verified(row)["practice"] is not None)


def joined_availability(row):
    """Verify a bounded listing's joined archive without one query per revision."""
    if row.get("archive_id") is None:
        return False
    archived = {
        "schema_version": row["archive_schema_version"],
        "payload": row["archived_guidance"],
        "payload_sha256": row["archive_sha256"],
    }
    return _verified(archived)["practice"] is not None


def result(c, tenant, object_id, revision_id, saved_data):
    row = _bound(c, tenant, object_id, revision_id)
    payload = _verified(row) if row else None
    versions = saved_data.get("content_versions", {})
    if not isinstance(versions, dict):
        versions = {}
    entries = {}
    for name in COMPONENTS:
        content = payload[name] if payload else None
        stored_version = versions.get(name)
        entries[name] = {
            "status": "AVAILABLE" if content else "UNAVAILABLE",
            "content_version": content["content_version"]
            if content
            else stored_version
            if isinstance(stored_version, str) and stored_version
            else None,
            "payload": content,
        }
    return {
        "object_id": str(object_id),
        "revision_id": str(revision_id),
        "status": "COMPLETE" if payload and payload["practice"] else "PARTIAL" if payload else "UNAVAILABLE",
        "snapshot_schema_version": row["schema_version"] if row else None,
        "captured_at": row["captured_at"].isoformat() if row else None,
        "snapshot_sha256": bytes(row["payload_sha256"]).hex() if row else None,
        **entries,
        "disclaimer": DISCLAIMER,
    }
