"""Additive, closed contracts for access administration, not arbitrary object writes."""

from copy import deepcopy
from .workspace_contracts import (
    READS as WORKSPACE_READS,
    COMMANDS as WORKSPACE_COMMANDS,
    shapes as workspace_shapes,
)

UUID = {"type": "string", "format": "uuid"}
DATE = {"type": "string", "format": "date-time"}
REASON = {"type": "string", "minLength": 1, "maxLength": 2000}
SCOPES = {"type": "array", "items": UUID, "minItems": 1, "maxItems": 20, "uniqueItems": True}
ADMIN_READS = {
    "membership-directory": ("MemberDirectory", "memberships.read"),
    "member-invitations": ("MemberInvitation", "member-invitations.read"),
    "role-templates": ("RoleTemplate", "role-templates.read"),
    "access-scopes": ("AccessScope", "access-scopes.read"),
    "access-requests": ("AccessRequest", "access-requests.read"),
}
COMMANDS = {
    ("member-invitations", None): (
        "invite_member",
        "member.invite",
        "InviteMember",
        False,
        {
            "email": {"type": "string", "format": "email", "maxLength": 254},
            "role_template_id": UUID,
            "scope_ids": SCOPES,
            "expires_at": DATE,
            "membership_expires_at": DATE,
            "external": {"const": True},
            "reason": REASON,
        },
    ),
    ("member-invitations", "resend"): (
        "resend_invitation",
        "member.invite",
        "ResendInvitation",
        True,
        {"reason": REASON},
    ),
    ("member-invitations", "revoke"): (
        "revoke_invitation",
        "member.invite",
        "RevokeInvitation",
        True,
        {"reason": REASON},
    ),
    ("invitation-acceptances", None): (
        "accept_invitation",
        "invitation.accept",
        "AcceptInvitation",
        False,
        {"invitation_token": {"type": "string", "minLength": 40, "maxLength": 512}},
    ),
    ("memberships", "suspend"): (
        "action_memberships_suspend",
        "membership.suspend",
        "SuspendMember",
        True,
        {"reason": REASON},
    ),
    ("memberships", "reactivate"): (
        "reactivate_membership",
        "membership.reactivate",
        "ReactivateMember",
        True,
        {"reason": REASON},
    ),
    ("memberships", "revoke"): (
        "action_memberships_revoke",
        "membership.revoke",
        "RevokeMember",
        True,
        {"reason": REASON},
    ),
    ("grants", "revoke"): ("action_grants_revoke", "grant.revoke", "RevokeGrant", True, {"reason": REASON}),
    ("access-scopes", None): (
        "create_access_scope",
        "access-scopes.create",
        "CreateAccessScope",
        False,
        {
            "title": {"type": "string", "minLength": 1, "maxLength": 120},
            "object_ids": {
                "type": "array",
                "items": UUID,
                "minItems": 1,
                "maxItems": 100,
                "uniqueItems": True,
            },
            "reason": REASON,
        },
    ),
    ("access-requests", None): (
        "request_access_change",
        "grant.request",
        "RequestAccessChange",
        False,
        {
            "membership_id": UUID,
            "expected_membership_revision": UUID,
            "role_template_id": UUID,
            "scope_ids": SCOPES,
            "expires_at": DATE,
            "reason": REASON,
        },
    ),
    ("access-requests", "approve"): (
        "approve_access_change",
        "grant.approve",
        "ApproveAccessChange",
        True,
        {"reason": REASON},
    ),
    ("access-requests", "reject"): (
        "reject_access_change",
        "grant.approve",
        "RejectAccessChange",
        True,
        {"reason": REASON},
    ),
}


ADMIN_READS.update(WORKSPACE_READS)
COMMANDS.update(WORKSPACE_COMMANDS)


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    schemas["AdministrationReceipt"] = deepcopy(schemas["Receipt"])
    schemas["AdministrationReceipt"]["properties"].update(
        invitation_generation=UUID, invitation_url={"type": "string", "format": "uri", "maxLength": 2000}
    )
    rows = {p["operation_id"]: p for p in policy["operations"]}
    for (route, action), (op, cap, name, expected, fields) in COMMANDS.items():
        schemas[name + "Data"] = {
            "type": "object",
            "additionalProperties": False,
            "properties": fields,
            "required": list(fields),
        }
        props = {"operation_id": UUID, "data": {"$ref": "#/components/schemas/" + name + "Data"}}
        if expected:
            props["expected_revision"] = UUID
        schemas[name] = {
            "type": "object",
            "additionalProperties": False,
            "properties": props,
            "required": list(props),
        }
        suffix = "/{object_id}/actions/" + action if action else ""
        path = "/v1/tenants/{tenant_id}/" + route + suffix
        original = spec["paths"]["/v1/tenants/{tenant_id}/programmes" + ("/{object_id}" if expected else "")]
        entry = deepcopy(original["patch" if expected else "post"])
        entry.update(operationId=op, summary=name, **{"x-capability": cap})
        entry["requestBody"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/" + name
        }
        entry["responses"] = {
            **entry["responses"],
            "200": deepcopy(entry["responses"].get("200", entry["responses"].get("201"))),
        }
        entry["responses"].pop("201", None)
        entry["responses"]["200"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/AdministrationReceipt"
        }
        spec["paths"].setdefault(path, {"parameters": deepcopy(original.get("parameters", []))})["post"] = (
            entry
        )
        rows[op] = {
            "operation_id": op,
            "method": "POST",
            "path": path,
            "capability": cap,
            "role_templates": ["EXTERNAL"] if op == "accept_invitation" else ["OWNER", "TENANT_ADMIN"],
            "fresh_assurance_seconds": None if op == "accept_invitation" else 300,
            "purpose_required": False,
            "audit": True,
        }
    # Administration list payloads are intentionally distinct from domain object payloads.
    for route, (name, cap) in ADMIN_READS.items():
        path = "/v1/tenants/{tenant_id}/" + route
        op = "list_" + route.replace("-", "_")
        entry = deepcopy(spec["paths"]["/v1/tenants/{tenant_id}/programmes"]["get"])
        entry.update(operationId=op, summary="List " + name, **{"x-capability": cap})
        entry["responses"]["200"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/" + name + "List"
        }
        spec["paths"].setdefault(
            path,
            {
                "parameters": deepcopy(
                    spec["paths"]["/v1/tenants/{tenant_id}/programmes"].get("parameters", [])
                )
            },
        )["get"] = entry
        rows[op] = {
            "operation_id": op,
            "method": "GET",
            "path": path,
            "capability": cap,
            "role_templates": ["OWNER", "TENANT_ADMIN"],
            "fresh_assurance_seconds": None,
            "purpose_required": False,
            "audit": False,
        }
    text = {"type": "string", "maxLength": 254}
    maybe_text = {"type": ["string", "null"], "maxLength": 254}
    common = {"object_id": UUID, "revision_id": UUID, "state": text}
    shapes = {
        "MemberDirectory": {
            **common,
            "principal_id": UUID,
            "identity_id": UUID,
            "display_name": text,
            "email_mask": maybe_text,
            "external": {"type": "boolean"},
            "expires_at": {"type": ["string", "null"], "format": "date-time"},
            "owner": {"type": "boolean"},
            "roles": {"type": "array", "items": text, "maxItems": 100},
            "grants": {
                "type": "array",
                "maxItems": 500,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "object_id": UUID,
                        "revision_id": UUID,
                        "capability": text,
                        "scope_id": UUID,
                        "expires_at": {"type": ["string", "null"], "format": "date-time"},
                    },
                    "required": ["object_id", "revision_id", "capability", "scope_id", "expires_at"],
                },
            },
        },
        "MemberInvitation": {
            **common,
            "email_mask": text,
            "role_name": text,
            "scope_ids": SCOPES,
            "expires_at": DATE,
            "membership_expires_at": DATE,
            "inviter_id": UUID,
        },
        "RoleTemplate": {
            **common,
            "name": text,
            "capabilities": {"type": "array", "items": text, "maxItems": 200},
            "administrative": {"type": "boolean"},
        },
        "AccessScope": {
            "object_id": UUID,
            "title": text,
            "scope_type": text,
            "object_ids": {"type": "array", "items": UUID, "maxItems": 10000},
        },
        "AccessRequest": {
            **common,
            "membership_id": UUID,
            "requested_by": UUID,
            "role_name": text,
            "scope_ids": SCOPES,
            "expires_at": DATE,
            "reason": REASON,
        },
    }
    shapes.update(workspace_shapes(common))
    for name, props in shapes.items():
        schemas[name + "Item"] = {
            "type": "object",
            "additionalProperties": False,
            "properties": props,
            "required": list(props),
        }
        schemas[name + "List"] = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "items": {
                    "type": "array",
                    "maxItems": 100,
                    "items": {"$ref": "#/components/schemas/" + name + "Item"},
                },
                "next_cursor": {"type": ["string", "null"]},
                "scope_label": text,
            },
            "required": ["items", "next_cursor", "scope_label"],
        }
    policy["operations"] = list(rows.values())
    policy["version"] = "1.3.0"
    spec["info"]["version"] = "1.3.0"
