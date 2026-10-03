"""Denial auditing (v0.27, FR-SEC-007 / FSD §35 denied operations).

A refused authorisation (store.authorize: POLICY_DENIED, a hidden RESOURCE_UNAVAILABLE,
PURPOSE_REQUIRED, ASSURANCE_REQUIRED) is a security event. The refused transaction rolls back, so
the event is recorded afterwards by the request layer (main.py's DomainError handler) in a
transaction of its own, through the SECURITY DEFINER impact.record_access_denial: the application
holds only SELECT on impact.access_denial. What is recorded: tenant, principal, operation,
capability, route template, the client-supplied selector (an identifier, never proof of anything),
HTTP status, error code, reason code and correlation ids; never a payload, token, secret or address.

Flood control (per tenant and principal, on the database clock): repeats of the same operation and
reason inside one WINDOW_SECONDS window collapse into one row whose counter advances; once a
principal holds CAP_PER_WINDOW distinct rows in a window, every further distinct denial counts in
one overflow row (operation '*', reason DENIAL_LIMIT). A scan of n operations therefore costs at
most CAP_PER_WINDOW + 1 rows per window, whatever n is. Recording never changes the response: a
failure to record is logged with the correlation id and swallowed.

Denials before authorisation (unknown tenant, no membership, an invalid token) are not security
events of a tenant and are not recorded; neither are 404s that hide an object the policy lets the
caller see nothing of outside authorize (store.load with a capability).
"""

import logging
from datetime import datetime, timezone

from .domain import DomainError
from .store import authorize, context

LOG = logging.getLogger("impact")
WINDOW_SECONDS = 300
CAP_PER_WINDOW = 50
LIST_LIMIT = 200
OPERATION = "list_access_denials"


def iso(value):
    return value.astimezone(timezone.utc).isoformat() if isinstance(value, datetime) else value


def route_of(path, tenant):
    """The route template of a request path (tenant and object identifiers replaced), bounded."""
    parts = []
    for part in path.split("/"):
        if part == str(tenant):
            parts.append("{tenant_id}")
        elif len(part) == 36 and part.count("-") == 4:
            parts.append("{id}")
        else:
            parts.append(part)
    return "/".join(parts)[:256]


def record(db, denial, correlation, path):
    """Record one denial in its own transaction (never inside the refused one). Best effort."""
    try:
        with db.transaction(denial["tenant_id"]) as c:
            c.execute(
                "SELECT impact.record_access_denial(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) AS denial_id",
                (
                    denial["principal_id"],
                    denial["operation_id"],
                    denial["capability"],
                    route_of(path, denial["tenant_id"]),
                    denial["status"],
                    denial["code"],
                    denial["reason_code"],
                    denial.get("object_id"),
                    correlation,
                    WINDOW_SECONDS,
                    CAP_PER_WINDOW,
                ),
            )
    except Exception as exc:  # noqa: BLE001 - recording a denial never alters the response
        LOG.warning("access denial not recorded correlation=%s class=%s", correlation, type(exc).__name__)


def listing(db, identity, tenant, limit=50, since=None):
    """The tenant's collapsed denials, newest first (access-denials.read)."""
    if not 1 <= limit <= LIST_LIMIT:
        raise DomainError("VALIDATION_FAILED")
    with db.transaction(tenant) as c:
        ctx = context(c, identity, tenant)
        authorize(c, ctx, OPERATION)
        query = "SELECT * FROM impact.access_denial WHERE tenant_id=%s"
        params = [tenant]
        if since:
            query += " AND last_at>=%s"
            params.append(since)
        rows = c.execute(
            query + " ORDER BY last_at DESC,denial_id DESC LIMIT %s", params + [limit]
        ).fetchall()
        return {
            "items": [
                {
                    "denial_id": str(r["denial_id"]),
                    "principal_id": str(r["principal_id"]),
                    "operation_id": r["operation_id"],
                    "capability": r["capability"],
                    "route": r["route"],
                    "status": r["status"],
                    "code": r["code"],
                    "reason_code": r["reason_code"],
                    "object_id": str(r["object_id"]) if r["object_id"] else None,
                    "window_start": iso(r["window_start"]),
                    "first_at": iso(r["first_at"]),
                    "last_at": iso(r["last_at"]),
                    "first_correlation_id": str(r["first_correlation_id"]),
                    "last_correlation_id": str(r["last_correlation_id"]),
                    "occurrences": r["occurrences"],
                }
                for r in rows
            ],
            "next_cursor": None,
            "scope_label": "Access denied to members of this workspace (collapsed per "
            + str(WINDOW_SECONDS)
            + " s window)",
        }
