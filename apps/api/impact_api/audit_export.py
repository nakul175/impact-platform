"""Audit export (v0.25 part A, VF-AUD-001): a bounded, verifiable page of the tenant's audit events.

The tenant's audit events are AuditEvent registry objects whose revisions are insert-only
(object_revision with payload_sha256). An export reads one page of them for a closed time window
[window_start, window_end), ordered by (occurred_at, event id), and returns:

- content: JSON Lines, one canonical JSON object per event with identifiers, codes, the revision
  digest and a running hash chain (no payload text, secret, sealed value or address exists in these
  columns, and nothing else is read); since v0.27 the collapsed access denials of the window are
  lines of the same stream (outcome DENIED, occurrences = the collapsed count, no revision) and
  every page is registered durably in impact.audit_export_register;
- manifest: tenant, window, purpose, page, counts, the SHA-256 of the content, the chain start and
  end, the fields, and an HMAC-SHA256 seal over the manifest under a key derived from the current
  cookie secret (named by its kid; verifiable by the platform during the key's grace window);
- next_cursor: a signed, 15-minute cursor bound to tenant, principal, grants, window and purpose,
  carrying the sequence and chain position so the next page continues the chain.

Chain: chain_0 = SHA-256("impact-audit-export-v1:<tenant>:<window_start>:<window_end>") (hex);
chain_i = SHA-256(bytes(chain_{i-1}) || SHA-256(canonical line_i without "chain")) (hex). Anyone
holding the pages can recompute every digest and the chain; the seal additionally binds a manifest
to this platform.

Each export (each page) is a command: audit.export at TENANT scope for the stated purpose, fresh
authentication (300 s), an operation receipt (an exact retry returns the same page) and an audit
event (action create_audit_export, specification_ref VF-AUD-001/<purpose>) in the same transaction.
"""

import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from .clock import now
from .audit_export_contracts import DEFAULT_LIMIT, FORMAT, MAX_WINDOW_DAYS, OPERATION, ROUTE
from .contracts import validate
from .domain import DomainError
from .keyring import ring
from .store import authorize, canonical, context, hash_data, write

FIELDS = [
    "sequence",
    "event_id",
    "revision_id",
    "revision_sha256",
    "occurred_at",
    "action_type",
    "outcome",
    "real_actor_id",
    "effective_actor_id",
    "object_reference",
    "correlation_id",
    "specification_ref",
    "occurrences",
    "chain",
]
CHAIN_ALGORITHM = "chain_i = SHA-256(chain_{i-1} bytes || SHA-256(canonical JSON line without chain)); hex"
SEAL_PURPOSE = b"impact-audit-export-seal-v1"
# v0.27: audit events and collapsed access denials (security events) in one ordered stream. A
# denial line has outcome DENIED, action_type = the refused operation, the principal as actor, the
# selector as object_reference, the first correlation id, specification_ref FR-SEC-007/<reason>
# and occurrences = the collapsed count; it has no revision (null revision fields).
QUERY = (
    "SELECT * FROM ("
    "SELECT a.object_id AS event_id,a.revision_id,v.payload_sha256,a.occurred_at,a.action_type,a.outcome,"
    "a.real_actor_id,a.effective_actor_id,a.object_reference,a.correlation_id,a.specification_ref,"
    "NULL::integer AS occurrences "
    "FROM impact.audit_event_current a JOIN impact.object_revision v "
    "ON v.tenant_id=a.tenant_id AND v.object_id=a.object_id AND v.revision_id=a.revision_id "
    "WHERE a.tenant_id=%s AND a.occurred_at>=%s AND a.occurred_at<%s "
    "UNION ALL "
    "SELECT d.denial_id,NULL::uuid,NULL::bytea,d.first_at,d.operation_id,'DENIED',d.principal_id,d.principal_id,"
    "d.object_id,d.first_correlation_id,'FR-SEC-007/'||d.reason_code,d.occurrences "
    "FROM impact.access_denial d WHERE d.tenant_id=%s AND d.first_at>=%s AND d.first_at<%s"
    ") a WHERE TRUE"
)


def instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def stamp(value):
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def text(value):
    return None if value is None else str(value)


def genesis(tenant, start, end):
    return hashlib.sha256(
        ("impact-audit-export-v1:" + str(tenant) + ":" + start + ":" + end).encode()
    ).hexdigest()


def link(previous, body):
    return hashlib.sha256(bytes.fromhex(previous) + hashlib.sha256(canonical(body)).digest()).hexdigest()


def seal_key(secret):
    return hmac.new(secret.encode(), SEAL_PURPOSE, hashlib.sha256).digest()


def seal(settings, manifest):
    keys = ring(settings, "cookie")
    value = hmac.new(seal_key(keys.current), canonical(manifest), hashlib.sha256).hexdigest()
    return {"algorithm": "HMAC-SHA256", "key_id": keys.current_id, "value": value}


def verify_seal(settings, manifest):
    """True when the manifest's seal was made by this platform under a non-retired cookie secret."""
    body = {k: v for k, v in manifest.items() if k != "seal"}
    stated = manifest.get("seal") or {}
    secret = ring(settings, "cookie").get(stated.get("key_id"))
    if not secret or not isinstance(stated.get("value"), str):
        return False
    expected = hmac.new(seal_key(secret), canonical(body), hashlib.sha256).hexdigest()
    return hmac.compare_digest(stated["value"], expected)


def verify_content(manifest, content, chain_start=None):
    """Recompute the content digest and the chain of one page; returns the problems found."""
    problems = []
    raw = content.encode()
    if hashlib.sha256(raw).hexdigest() != manifest["content_sha256"] or len(raw) != manifest["content_bytes"]:
        problems.append("CONTENT_DIGEST")
    chain = chain_start or manifest["chain_start"]
    lines = [line for line in content.split("\n") if line]
    if len(lines) != manifest["event_count"]:
        problems.append("EVENT_COUNT")
    for line in lines:
        record = json.loads(line)
        chain = link(chain, {k: v for k, v in record.items() if k != "chain"})
        if record.get("chain") != chain:
            problems.append("CHAIN")
            break
    if chain != manifest["chain_end"]:
        problems.append("CHAIN_END")
    return problems


class AuditExports:
    def __init__(self, service):
        self.service, self.s, self.db = service, service.s, service.db

    def create(self, identity, tenant, body, correlation):
        validate("AuditExportRequest", body)
        data = body["data"]
        start, end, at = instant(data["window_start"]), instant(data["window_end"]), now()
        if not start < end:
            raise DomainError("VALIDATION_FAILED", reason="WINDOW_INVALID")
        if end > at:
            raise DomainError("VALIDATION_FAILED", reason="WINDOW_IN_FUTURE")
        if end - start > timedelta(days=MAX_WINDOW_DAYS):
            raise DomainError("VALIDATION_FAILED", reason="WINDOW_TOO_LONG")
        fingerprint = hash_data([OPERATION, None, body])
        with self.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (str(tenant),))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, OPERATION, purpose=data["purpose"])
            outcome, _ = self.service.evidence.receipted(
                c, ctx, OPERATION, body, fingerprint, lambda: self.page(c, ctx, data, start, end, correlation)
            )
            return outcome

    def page(self, c, ctx, data, start, end, correlation):
        window = (stamp(start), stamp(end))
        binding = hash_data(
            [self.service.cursor_binding(ctx, ROUTE), window[0], window[1], data["purpose"]]
        ).hex()
        position = self.service.cursor_key(binding, data.get("cursor"))
        query, args = QUERY, [ctx.tenant_id, start, end, ctx.tenant_id, start, end]
        if position:
            after, after_id, sequence, chain, page = position
            query += " AND (a.occurred_at,a.event_id)>(%s::timestamptz,%s::uuid)"
            args += [after, after_id]
            page += 1
        else:
            sequence, chain, page = 0, genesis(ctx.tenant_id, *window), 1
        limit = data.get("limit", DEFAULT_LIMIT)
        rows = c.execute(query + " ORDER BY a.occurred_at,a.event_id LIMIT %s", args + [limit + 1]).fetchall()
        more, rows = len(rows) > limit, rows[:limit]
        chain_start, first, lines, denials = chain, sequence + 1 if rows else None, [], 0
        for row in rows:
            sequence += 1
            denials += row["occurrences"] is not None
            record = {
                "sequence": sequence,
                "event_id": str(row["event_id"]),
                "revision_id": text(row["revision_id"]),
                "revision_sha256": bytes(row["payload_sha256"]).hex() if row["payload_sha256"] else None,
                "occurred_at": stamp(row["occurred_at"]),
                "action_type": row["action_type"],
                "outcome": row["outcome"],
                "real_actor_id": text(row["real_actor_id"]),
                "effective_actor_id": text(row["effective_actor_id"]),
                "object_reference": text(row["object_reference"]),
                "correlation_id": text(row["correlation_id"]),
                "specification_ref": row["specification_ref"],
                "occurrences": row["occurrences"],
            }
            chain = link(chain, record)
            lines.append(canonical({**record, "chain": chain}).decode())
        content = "".join(line + "\n" for line in lines)
        export_id, generated = str(uuid4()), now()
        # The export itself is an audit event in this transaction (outside the window it reads).
        write(
            c,
            ctx,
            "AuditEvent",
            {
                "real_actor_id": ctx.principal_id,
                "effective_actor_id": ctx.principal_id,
                "action_type": OPERATION,
                "outcome": "SUCCEEDED",
                "occurred_at": generated.isoformat(),
                "correlation_id": correlation,
                "specification_ref": "VF-AUD-001/" + data["purpose"],
            },
            "Recorded",
            object_id=export_id,
            track_author=False,
        )
        manifest = {
            "format": FORMAT,
            "export_id": export_id,
            "tenant_id": ctx.tenant_id,
            "window_start": window[0],
            "window_end": window[1],
            "purpose": data["purpose"],
            "generated_at": stamp(generated),
            "generated_by": ctx.principal_id,
            "correlation_id": correlation,
            "page": page,
            "first_sequence": first,
            "event_count": len(lines),
            "denial_count": denials,
            "complete": not more,
            "media_type": "application/x-ndjson",
            "content_sha256": hashlib.sha256(content.encode()).hexdigest(),
            "content_bytes": len(content.encode()),
            "chain_algorithm": CHAIN_ALGORITHM,
            "chain_start": chain_start,
            "chain_end": chain,
            "fields": FIELDS,
        }
        manifest["seal"] = seal(self.s, manifest)
        # v0.27: the durable register row (insert-only) keyed by the export's own audit event, so the
        # window, purpose, digest, chain and seal key outlive the 7-day operation receipt.
        c.execute(
            "INSERT INTO impact.audit_export_register(tenant_id,export_id,principal_id,purpose,reason,window_start,"
            "window_end,page,first_sequence,event_count,denial_count,content_sha256,chain_start,chain_end,"
            "seal_key_id,correlation_id,created_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                ctx.tenant_id,
                export_id,
                ctx.principal_id,
                data["purpose"],
                data["reason"],
                start,
                end,
                page,
                first,
                len(lines),
                denials,
                bytes.fromhex(manifest["content_sha256"]),
                bytes.fromhex(chain_start),
                bytes.fromhex(chain),
                manifest["seal"]["key_id"],
                correlation,
                generated,
            ),
        )
        next_cursor = None
        if more:
            last = rows[-1]
            next_cursor = self.service.next_cursor(
                binding, [last["occurred_at"].isoformat(), str(last["event_id"]), sequence, chain, page]
            )
        return {"manifest": manifest, "content": content, "next_cursor": next_cursor}
