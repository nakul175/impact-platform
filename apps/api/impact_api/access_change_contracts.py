"""FR-ACC-011 bounded online-presentation revalidation contracts."""

VERSION = "1.79.0"
IMPLEMENTED = [
    ("post", "derivatives/{derivative_id}/revisions/{revision_id}/presentation-leases"),
    ("get", "presentation-leases/{lease_id}"),
]


def augment(spec, policy):
    tenant = {
        "name": "tenant_id",
        "in": "path",
        "required": True,
        "schema": {"type": "string", "format": "uuid"},
    }
    derivative = {
        "name": "derivative_id",
        "in": "path",
        "required": True,
        "schema": {"type": "string", "format": "uuid"},
    }
    revision = {
        "name": "revision_id",
        "in": "path",
        "required": True,
        "schema": {"type": "string", "format": "uuid"},
    }
    base = "/v1/tenants/{tenant_id}/derivatives/{derivative_id}/revisions/{revision_id}/presentation-leases"
    spec["paths"][base] = {
        "post": {
            "operationId": "issue_presentation_lease",
            "summary": "Issue a current-policy online presentation lease for at most sixty seconds",
            "x-capability": "reports.read",
            "x-contract-version": VERSION,
            "parameters": [tenant, derivative, revision],
            "responses": {"200": {"description": "Policy-epoch-bound lease"}},
        }
    }
    check = "/v1/tenants/{tenant_id}/presentation-leases/{lease_id}"
    spec["paths"][check] = {
        "get": {
            "operationId": "validate_presentation_lease",
            "summary": "Revalidate a presentation lease against current authority",
            "x-capability": "reports.read",
            "x-contract-version": VERSION,
            "parameters": [
                tenant,
                {
                    "name": "lease_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "format": "uuid"},
                },
            ],
            "responses": {
                "200": {"description": "Lease remains current"},
                "404": {"description": "Expired, policy-stale or inaccessible without content preview"},
            },
        }
    }
    for op, method, path, guard in [
        (
            "issue_presentation_lease",
            "POST",
            base,
            "All derivative sources are checked and the current policy epoch is pinned for no more than sixty seconds.",
        ),
        (
            "validate_presentation_lease",
            "GET",
            check,
            "Principal, expiry, tenant policy epoch and every source are rechecked; stale presentations fail closed.",
        ),
    ]:
        policy["operations"].append(
            {
                "operation_id": op,
                "method": method,
                "path": path,
                "capability": "reports.read",
                "role_templates": ["TENANT_MEMBER"],
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": False,
                "state_guard": guard,
            }
        )
