"""Closed commands for the next tenant-administration increment."""

UUID = {"type": "string", "format": "uuid"}
DATE = {"type": "string", "format": "date-time"}
TEXT = {"type": "string", "minLength": 1, "maxLength": 120}
REASON = {"type": "string", "minLength": 1, "maxLength": 2000}
IDS = {"type": "array", "items": UUID, "uniqueItems": True, "maxItems": 100}
CAPS = {
    "type": "array",
    "items": {"type": "string", "maxLength": 64},
    "uniqueItems": True,
    "minItems": 1,
    "maxItems": 100,
}
PARENT = {"type": ["string", "null"], "format": "uuid"}
BINDING = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "role_template_id": UUID,
        "scope_ids": {**IDS, "minItems": 1, "maxItems": 10},
        "expires_at": DATE,
    },
    "required": ["role_template_id", "scope_ids", "expires_at"],
}
ROLE = {"name": TEXT, "capabilities": CAPS, "reason": REASON}
READS = {
    "access-groups": ("AccessGroup", "groups.read"),
    "group-change-requests": ("GroupChange", "groups.read"),
    "organisation-units": ("UnitDirectory", "organisation-units.read"),
    "renewal-requests": ("MembershipRenewal", "memberships.read"),
    "ownership-transfers": ("OwnershipTransfer", "memberships.read"),
}
KINDS = {
    "access-groups": "AccessGroup",
    "group-change-requests": "GroupChangeRequest",
    "organisation-units": "OrganisationUnit",
    "renewal-requests": "MembershipRenewal",
    "ownership-transfers": "CustodyTransfer",
}
COMMANDS = {
    ("role-templates", None): ("create_role_template", "roles.manage", "CreateRoleTemplate", False, ROLE),
    ("role-templates", "revise"): ("revise_role_template", "roles.manage", "ReviseRoleTemplate", True, ROLE),
    ("role-templates", "retire"): (
        "retire_role_template",
        "roles.manage",
        "RetireRoleTemplate",
        True,
        {"reason": REASON},
    ),
    ("access-groups", None): (
        "create_access_group",
        "groups.manage",
        "CreateAccessGroup",
        False,
        {"name": TEXT, "reason": REASON},
    ),
    ("access-groups", "remove-member"): (
        "remove_group_member",
        "groups.manage",
        "RemoveGroupMember",
        True,
        {"membership_id": UUID, "reason": REASON},
    ),
    ("access-groups", "retire"): (
        "retire_access_group",
        "groups.manage",
        "RetireAccessGroup",
        True,
        {"reason": REASON},
    ),
    ("group-change-requests", None): (
        "request_group_change",
        "groups.request",
        "RequestGroupChange",
        False,
        {
            "group_id": UUID,
            "expected_group_revision": UUID,
            "membership_ids": IDS,
            "bindings": {"type": "array", "items": BINDING, "maxItems": 10},
            "reason": REASON,
        },
    ),
    ("organisation-units", None): (
        "create_organisation_unit",
        "organisation-units.manage",
        "CreateOrganisationUnit",
        False,
        {
            "code": {"type": "string", "pattern": "^[A-Z][A-Z0-9_-]{0,63}$"},
            "name": TEXT,
            "parent_id": PARENT,
            "reason": REASON,
        },
    ),
    ("organisation-units", "reparent"): (
        "reparent_organisation_unit",
        "organisation-units.manage",
        "ReparentOrganisationUnit",
        True,
        {"parent_id": PARENT, "reason": REASON},
    ),
    ("organisation-units", "rename"): (
        "rename_organisation_unit",
        "organisation-units.manage",
        "RenameOrganisationUnit",
        True,
        {"name": TEXT, "reason": REASON},
    ),
    ("renewal-requests", None): (
        "request_membership_renewal",
        "membership.renew.request",
        "RequestMembershipRenewal",
        False,
        {"membership_id": UUID, "expected_membership_revision": UUID, "expires_at": DATE, "reason": REASON},
    ),
    ("ownership-transfers", None): (
        "nominate_owner",
        "ownership.transfer",
        "NominateOwner",
        False,
        {"membership_id": UUID, "expected_membership_revision": UUID, "reason": REASON},
    ),
    ("ownership-transfers", "accept"): (
        "accept_ownership",
        "ownership.transfer",
        "AcceptOwnership",
        True,
        {"reason": REASON},
    ),
    ("ownership-transfers", "cancel"): (
        "cancel_ownership",
        "ownership.transfer",
        "CancelOwnership",
        True,
        {"reason": REASON},
    ),
}
for route, prefix, cap in [
    ("group-change-requests", "GroupChange", "groups.approve"),
    ("renewal-requests", "MembershipRenewal", "membership.renew.approve"),
]:
    for action in ["approve", "reject"]:
        COMMANDS[(route, action)] = (
            action + "_" + route.replace("-", "_"),
            cap,
            action.title() + prefix,
            True,
            {"reason": REASON},
        )


def shapes(common):
    decision = {"requested_by": UUID, "reason": REASON}
    result = {
        "AccessGroup": {
            **common,
            "name": TEXT,
            "membership_ids": IDS,
            "bindings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        **BINDING["properties"],
                        "role_revision": UUID,
                        "role_name": TEXT,
                        "capabilities": CAPS,
                    },
                    "required": [*BINDING["required"], "role_revision", "role_name", "capabilities"],
                },
                "maxItems": 10,
            },
        },
        "GroupChange": {
            **common,
            **decision,
            "group_id": UUID,
            "membership_ids": IDS,
            "role_names": {"type": "array", "items": TEXT, "maxItems": 10},
        },
        "UnitDirectory": {
            **common,
            "code": {"type": "string", "maxLength": 64},
            "name": {"type": "string", "maxLength": 200},
            "parent_id": PARENT,
        },
        "MembershipRenewal": {**common, **decision, "membership_id": UUID, "expires_at": DATE},
        "OwnershipTransfer": {
            **common,
            **decision,
            "membership_id": UUID,
            "owner_membership_id": UUID,
            "expires_at": DATE,
        },
    }
    result["GroupChange"]["bindings"] = result["AccessGroup"]["bindings"]
    return result
