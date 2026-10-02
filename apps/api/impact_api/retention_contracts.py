"""Security and privacy contracts (v0.27): denial auditing read, tenant retention policies with
independent approval, and the retention-hold API.

- GET /access-denials (`list_access_denials`, `access-denials.read`, OWNER and TENANT_ADMIN): the
  tenant's collapsed access-denial rows, newest first.
- retention-policies (design routes kept and tightened; RetentionPolicy registry kind): list, get,
  create and patch a Draft (`retention-policies.read/.draft.create/.draft.edit`; OWNER, TENANT_ADMIN,
  PRIVACY) and the one transition `actions/approve` (`retention-policy.approve`; TENANT_ADMIN,
  PRIVACY; 300 s; independent natural person) that appends the insert-only binding the sweep reads.
- retention-holds: list (`retention-holds.read`), place (`retention.hold`, 300 s) and release
  (`retention.release`, 300 s, independent of the placer). A hold is not a registry object: the
  receipt's object_id is the hold id and its revision_id the held object's revision at the time.

Every route is served explicitly by main.py (before the generic handlers)."""

from copy import deepcopy

from .measurement_contracts import closed, text_field
from .retention import POLICY_BOUNDS, SCHEDULE

UUID = {"type": "string", "format": "uuid"}
DATE = {"type": "string", "format": "date-time"}
PREFIX = "/v1/tenants/{tenant_id}/"
POLICY_ROUTE = "retention-policies"
HOLD_ROUTE = "retention-holds"
DENIAL_ROUTE = "access-denials"
POLICY_ROLES = ["OWNER", "TENANT_ADMIN", "PRIVACY"]
APPROVER_ROLES = ["TENANT_ADMIN", "PRIVACY"]
HOLD_ROLES = ["PRIVACY", "TENANT_ADMIN"]
DENIAL_ROLES = ["OWNER", "TENANT_ADMIN"]
ACTIONS = sorted({c["action"] for c in SCHEDULE})
IMPLEMENTED = [
    ("get", DENIAL_ROUTE),
    ("get", POLICY_ROUTE),
    ("post", POLICY_ROUTE),
    ("get", POLICY_ROUTE + "/{object_id}"),
    ("patch", POLICY_ROUTE + "/{object_id}"),
    ("post", POLICY_ROUTE + "/{object_id}/actions/approve"),
    ("get", HOLD_ROUTE),
    ("post", HOLD_ROUTE),
    ("post", HOLD_ROUTE + "/{object_id}/actions/release"),
]
VERSION = "1.17.0"


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    base = PREFIX + POLICY_ROUTE
    item = base + "/{object_id}"
    tenant_parameters = deepcopy(paths[base]["parameters"])
    item_parameters = deepcopy(paths[item]["parameters"])

    # ---- retention policies: tightened data schemas -------------------------------------------
    draft = {
        "data_class": {"enum": sorted(POLICY_BOUNDS)},
        "duration_days": {"type": "integer", "minimum": 0, "maximum": 3650},
        "expiry_action": {"enum": ACTIONS},
        "trigger": text_field(64),
        "purpose": text_field(64),
        "reason": text_field(2000),
        "supersedes_revision": UUID,
    }
    server = {
        "approved_by": UUID,
        "approved_at": DATE,
        "approved_revision": UUID,
    }
    # The stored payload stays open to the tenant-level closure policy the control plane writes at
    # owner acceptance (data class TENANT_DATA, action REVIEW; tenant_lifecycle.py); only proposals
    # through the API (Create/Patch below) are confined to the policy-able classes and sweep actions.
    stored = {
        **deepcopy(draft),
        "data_class": text_field(64),
        "expiry_action": {"enum": sorted(set(ACTIONS) | {"RESTRICT", "REVIEW"})},
    }
    schemas["RetentionPolicyDraftData"] = closed(deepcopy(stored))
    schemas["RetentionPolicyData"] = closed(
        {**deepcopy(stored), **{k: {**v, "readOnly": True} for k, v in server.items()}}
    )
    schemas["RetentionPolicyCreate"] = closed(
        {
            "operation_id": UUID,
            "data": closed(deepcopy(draft), ["data_class", "duration_days", "expiry_action", "reason"]),
        },
        ["operation_id", "data"],
    )
    schemas["RetentionPolicyPatch"] = closed(
        {
            "operation_id": UUID,
            "expected_revision": UUID,
            "data": {**closed(deepcopy(draft)), "minProperties": 1},
        },
        ["operation_id", "expected_revision", "data"],
    )
    schemas["ActionRetentionPoliciesApproveData"] = closed({"reason": text_field(2000)}, ["reason"])
    schemas["ActionRetentionPoliciesApprove"] = closed(
        {
            "operation_id": UUID,
            "expected_revision": UUID,
            "data": {"$ref": "#/components/schemas/ActionRetentionPoliciesApproveData"},
        },
        ["operation_id", "expected_revision", "data"],
    )
    paths[base]["post"]["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/RetentionPolicyCreate"
    }
    paths[item]["patch"]["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/RetentionPolicyPatch"
    }
    approve = deepcopy(paths[base]["post"])
    approve.update(
        operationId="action_retention_policies_approve",
        summary="approve retention policy",
        description="Independent approval of a proposed retention policy: a natural person other than every "
        "author of the draft, within 300 seconds of authentication. Writes the Approved revision and appends "
        "the binding the retention sweep applies for that data class from its next run.",
        **{"x-capability": "retention-policy.approve", "x-audit-required": True},
    )
    approve["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/ActionRetentionPoliciesApprove"
    }
    paths[item + "/actions/approve"] = {"parameters": deepcopy(item_parameters), "post": approve}

    # ---- retention holds ------------------------------------------------------------------------
    schemas["RetentionHoldCreateData"] = closed(
        {
            "object_id": UUID,
            "authority_reference": text_field(200),
            "reason": text_field(2000),
            "review_at": DATE,
        },
        ["object_id", "authority_reference", "reason", "review_at"],
    )
    schemas["RetentionHoldCreate"] = closed(
        {"operation_id": UUID, "data": {"$ref": "#/components/schemas/RetentionHoldCreateData"}},
        ["operation_id", "data"],
    )
    schemas["ActionRetentionHoldsReleaseData"] = closed({"reason": text_field(2000)}, ["reason"])
    schemas["ActionRetentionHoldsRelease"] = closed(
        {"operation_id": UUID, "data": {"$ref": "#/components/schemas/ActionRetentionHoldsReleaseData"}},
        ["operation_id", "data"],
    )
    schemas["RetentionHold"] = closed(
        {
            "hold_id": UUID,
            "object_id": UUID,
            "object_type": {"type": "string", "maxLength": 64},
            "authority_reference": {"type": "string"},
            "reason": {"type": ["string", "null"]},
            "review_at": DATE,
            "placed_by": {"type": ["string", "null"], "format": "uuid"},
            "placed_at": {"type": ["string", "null"], "format": "date-time"},
            "released_at": {"type": ["string", "null"], "format": "date-time"},
            "released_by": {"type": ["string", "null"], "format": "uuid"},
            "release_reason": {"type": ["string", "null"]},
        },
        [
            "hold_id",
            "object_id",
            "object_type",
            "authority_reference",
            "reason",
            "review_at",
            "placed_by",
            "placed_at",
            "released_at",
            "released_by",
            "release_reason",
        ],
    )
    schemas["RetentionHoldList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 200,
                "items": {"$ref": "#/components/schemas/RetentionHold"},
            },
            "next_cursor": {"type": "null"},
            "scope_label": {"type": "string"},
        },
        ["items", "next_cursor", "scope_label"],
    )
    # A hold command's receipt names the held object and carries the hold id beside it.
    schemas["Receipt"]["properties"]["hold_id"] = UUID
    hold_base = PREFIX + HOLD_ROUTE
    hold_list = deepcopy(paths[base]["get"])
    hold_list.update(
        operationId="list_retention_holds",
        summary="list retention holds",
        description="The tenant's retention holds, active first: object, authority reference, reason, review "
        "date, who placed and who released each.",
        **{"x-capability": "retention-holds.read"},
    )
    hold_list["parameters"] = []
    hold_list["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/RetentionHoldList"
    }
    hold_place = deepcopy(paths[base]["post"])
    hold_place.update(
        operationId="create_retention_holds",
        summary="place retention hold",
        description="Place a retention hold on one object of this tenant the caller can read (authority "
        "reference, reason, future review date). Effective at once: the erasure plan reports the object as "
        "HELD and the revision-removal guard refuses it. Requires authentication within 300 seconds.",
        **{"x-capability": "retention.hold", "x-audit-required": True},
    )
    hold_place["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/RetentionHoldCreate"
    }
    paths[hold_base] = {"parameters": deepcopy(tenant_parameters), "get": hold_list, "post": hold_place}
    hold_release = deepcopy(hold_place)
    hold_release.update(
        operationId="action_retention_holds_release",
        summary="release retention hold",
        description="Release a hold: a natural person other than the one who placed it, with a reason, within "
        "300 seconds of authentication. A released hold is final.",
        **{"x-capability": "retention.release", "x-audit-required": True},
    )
    hold_release["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/ActionRetentionHoldsRelease"
    }
    paths[hold_base + "/{object_id}/actions/release"] = {
        "parameters": deepcopy(item_parameters),
        "post": hold_release,
    }

    # ---- access denials -------------------------------------------------------------------------
    schemas["AccessDenial"] = closed(
        {
            "denial_id": UUID,
            "principal_id": UUID,
            "operation_id": {"type": "string", "maxLength": 128},
            "capability": {"type": "string", "maxLength": 128},
            "route": {"type": "string", "maxLength": 256},
            "status": {"enum": [403, 404]},
            "code": {"type": "string", "maxLength": 64},
            "reason_code": {"type": "string", "maxLength": 64},
            "object_id": {"type": ["string", "null"], "format": "uuid"},
            "window_start": DATE,
            "first_at": DATE,
            "last_at": DATE,
            "first_correlation_id": UUID,
            "last_correlation_id": UUID,
            "occurrences": {"type": "integer", "minimum": 1},
        },
        [
            "denial_id",
            "principal_id",
            "operation_id",
            "capability",
            "route",
            "status",
            "code",
            "reason_code",
            "object_id",
            "window_start",
            "first_at",
            "last_at",
            "first_correlation_id",
            "last_correlation_id",
            "occurrences",
        ],
    )
    schemas["AccessDenialList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 200,
                "items": {"$ref": "#/components/schemas/AccessDenial"},
            },
            "next_cursor": {"type": "null"},
            "scope_label": {"type": "string"},
        },
        ["items", "next_cursor", "scope_label"],
    )
    denials = deepcopy(paths[base]["get"])
    denials.update(
        operationId="list_access_denials",
        summary="list access denials",
        description="Refused authorisations of this tenant's members (denial auditing, v0.27): principal, "
        "operation, capability, route, status, reason and correlation ids, collapsed per principal, operation "
        "and reason inside a 300-second window with an occurrence counter; newest first, at most 200.",
        **{"x-capability": "access-denials.read"},
    )
    denials["parameters"] = [
        {
            "name": "limit",
            "in": "query",
            "required": False,
            "schema": {"type": "integer", "minimum": 1, "maximum": 200},
        },
        {"name": "since", "in": "query", "required": False, "schema": DATE},
    ]
    denials["responses"]["200"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/AccessDenialList"
    }
    paths[PREFIX + DENIAL_ROUTE] = {"parameters": deepcopy(tenant_parameters), "get": denials}

    # ---- policy rows ----------------------------------------------------------------------------
    rows = {
        "list_retention_policies": ("GET", base, "retention-policies.read", POLICY_ROLES, None, False, False),
        "get_retention_policies": ("GET", item, "retention-policies.read", POLICY_ROLES, None, False, False),
        "create_retention_policies": (
            "POST",
            base,
            "retention-policies.draft.create",
            POLICY_ROLES,
            None,
            False,
            True,
        ),
        "patch_retention_policies": (
            "PATCH",
            item,
            "retention-policies.draft.edit",
            POLICY_ROLES,
            None,
            False,
            True,
        ),
        "action_retention_policies_approve": (
            "POST",
            item + "/actions/approve",
            "retention-policy.approve",
            APPROVER_ROLES,
            300,
            True,
            True,
        ),
        "list_retention_holds": ("GET", hold_base, "retention-holds.read", HOLD_ROLES, None, False, False),
        "create_retention_holds": ("POST", hold_base, "retention.hold", HOLD_ROLES, 300, False, True),
        "action_retention_holds_release": (
            "POST",
            hold_base + "/{object_id}/actions/release",
            "retention.release",
            HOLD_ROLES,
            300,
            True,
            True,
        ),
        "list_access_denials": (
            "GET",
            PREFIX + DENIAL_ROUTE,
            "access-denials.read",
            DENIAL_ROLES,
            None,
            False,
            False,
        ),
    }
    guards = {
        "create_retention_policies": "Draft only; data class within the policy-able set, duration inside the "
        "class bounds (the 365-day audit floor among them), action fixed per class.",
        "action_retention_policies_approve": "Independent natural person (never an author of the draft); "
        "Draft → Approved; one insert-only binding row per approval; the sweep applies the latest binding.",
        "create_retention_holds": "The object must be readable by the caller; review date in the future; "
        "effective immediately.",
        "action_retention_holds_release": "Never the natural person who placed the hold; a released hold is final.",
        "list_access_denials": "Identifiers, codes and correlation ids only; never a payload or secret.",
    }
    policy["operations"] = [p for p in policy["operations"] if p["operation_id"] not in rows]
    for op, (method, path, cap, roles, fresh, independence, audited) in rows.items():
        policy["operations"].append(
            {
                "operation_id": op,
                "method": method,
                "path": path,
                "capability": cap,
                "role_templates": roles,
                "scope": "tenant; explicit TENANT-scope grant required",
                "fresh_assurance_seconds": fresh,
                "independence_required": independence,
                "purpose_required": False,
                "field_filter_required": False,
                "state_guard": guards.get(op, "Authorise current tenant and capability."),
                "audit": audited,
            }
        )
    for method, route in IMPLEMENTED:
        paths[PREFIX + route][method]["x-contract-version"] = VERSION
