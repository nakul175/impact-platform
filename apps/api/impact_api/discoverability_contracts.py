"""Personal, permission-rechecked saved views with exact definition bindings."""

from copy import deepcopy
from .measurement_contracts import closed, text_field

VERSION = "1.59.0"
ROOT = "saved-views"
IMPLEMENTED = [
    ("get", ROOT),
    ("post", ROOT),
    ("get", ROOT + "/{object_id}"),
    ("patch", ROOT + "/{object_id}"),
]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    uid = {"type": "string", "format": "uuid"}
    data = closed(
        {
            "title": text_field(),
            "search_text": {"type": "string", "maxLength": 200},
            "definition_id": deepcopy(uid),
            "definition_revision": deepcopy(uid),
        },
        ["title", "search_text", "definition_id", "definition_revision"],
    )
    schemas["SavedViewDraftData"] = deepcopy(data)
    data["properties"].update(
        binding_state={"enum": ["CURRENT", "PINNED_REVISION"]},
        definition_revision_in_use=deepcopy(uid),
    )
    schemas["SavedViewData"] = data
    for suffix in ("", "List", "Create", "Patch"):
        schemas["SavedView" + suffix] = __import__("json").loads(
            __import__("json").dumps(schemas["Programme" + suffix]).replace("Programme", "SavedView")
        )
    prefix = "/v1/tenants/{tenant_id}/"
    for item in (False, True):
        suffix = "/{object_id}" if item else ""
        path = prefix + ROOT + suffix
        template = spec["paths"][prefix + "programmes" + suffix]
        spec["paths"][path] = {"parameters": deepcopy(template.get("parameters", []))}
        methods = ("get", "patch") if item else ("get", "post")
        for method in methods:
            entry = __import__("json").loads(
                __import__("json").dumps(template[method]).replace("Programme", "SavedView")
            )
            verb = (
                "get"
                if item and method == "get"
                else "list"
                if method == "get"
                else "patch"
                if item
                else "create"
            )
            operation = verb + "_saved_views"
            entry.update(
                operationId=operation,
                summary=operation.replace("_", " "),
                **{"x-capability": "work-items.read", "x-contract-version": VERSION},
            )
            spec["paths"][path][method] = entry
            policy["operations"].append(
                {
                    "operation_id": operation,
                    "method": method.upper(),
                    "path": path,
                    "capability": "work-items.read",
                    "role_templates": ["AUTHOR", "REVIEWER", "MEL_ADMIN", "PROGRAMME_MANAGER", "ANALYST"],
                    "purpose_required": False,
                    "fresh_assurance_seconds": None,
                    "audit": method != "get",
                }
            )
