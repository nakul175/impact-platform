"""Draft closed contracts for internal peer advice; no disclosure or provider authority."""

from copy import deepcopy

from jsonschema import Draft202012Validator, FormatChecker

from .ai_adoption_contracts import MANAGERS
from .ai_enablement_contracts import ROLES
from .domain import DomainError
from .measurement_contracts import UUID, closed

VERSION = "1.24.0"
ROUTE = "ai-enablement/human-advice"
STATES = ["Open", "Assigned", "AwaitingInput", "AdviceDraft", "Closed", "Cancelled"]
MATERIAL_POLICY = "SYNTHETIC_OR_PUBLIC_TEXT"
PRIVATE_PROOF_FIELDS = {
    "requester_natural_id",
    "adviser_natural_id",
    "requester_auth_time",
    "case_schema_version",
    "problem_sha256",
}
PUBLIC_FIELDS = (
    "title",
    "context_plan_id",
    "context_plan_revision",
    "adviser_membership_id",
    "scope",
    "data_boundary",
    "desired_outcome",
    "material_policy",
    "invitation_consent",
    "requester_principal_id",
    "requester_membership_id",
    "adviser_principal_id",
    "state",
    "declaration",
    "assignment",
    "notes",
    "advice",
    "closure",
    "cancellation",
)
PUBLIC_DECISION_FIELDS = {
    "declaration": ("conflict", "details", "scope_accepted", "declared_by", "declared_at"),
    "assignment": ("declaration_revision_id", "sharing_confirmed", "assigned_by", "assigned_at"),
}


def text(maximum):
    return {"type": "string", "minLength": 1, "maxLength": maximum, "pattern": r"\S"}


def shape(fields):
    return closed(fields, list(fields))


CREATE_DATA = shape(
    {
        "title": text(150),
        "context_plan_id": deepcopy(UUID),
        "context_plan_revision": deepcopy(UUID),
        "adviser_membership_id": deepcopy(UUID),
        "problem": text(4000),
        "scope": text(2000),
        "data_boundary": text(2000),
        "desired_outcome": text(2000),
        "material_policy": {"const": MATERIAL_POLICY},
        "invitation_consent": {"const": True},
    }
)
ACTION_DATA = {
    "declare-scope": shape(
        {
            "conflict": {"enum": ["NONE", "DECLARED"]},
            "details": text(1000),
            "scope_accepted": {"type": "boolean"},
        }
    ),
    "assign": shape({"declaration_revision_id": deepcopy(UUID), "sharing_confirmed": {"const": True}}),
    "request-input": shape({"question": text(2000)}),
    "respond": shape({"response": text(4000)}),
    "advise": shape(
        {
            "advice": text(6000),
            "actions": {
                "type": "array",
                "maxItems": 20,
                "items": shape(
                    {"description": text(1000), "responsibility": {"enum": ["REQUESTER", "ADVISER"]}}
                ),
            },
        }
    ),
    "close": shape(
        {
            "advice_revision_id": deepcopy(UUID),
            "acknowledged_action_ids": {
                "type": "array",
                "maxItems": 20,
                "uniqueItems": True,
                "items": deepcopy(UUID),
            },
            "closure_reason": text(1000),
        }
    ),
    "cancel": shape({"reason": text(1000)}),
}


def request_schema(action=None):
    fields = {
        "operation_id": deepcopy(UUID),
        "data": deepcopy(CREATE_DATA if action is None else ACTION_DATA[action]),
    }
    if action is not None:
        fields["expected_revision"] = deepcopy(UUID)
    return shape(fields)


def validate_body(body, action=None):
    if action is not None and action not in ACTION_DATA:
        raise DomainError("RESOURCE_UNAVAILABLE", 404)
    if not Draft202012Validator(request_schema(action), format_checker=FormatChecker()).is_valid(body):
        raise DomainError("VALIDATION_FAILED", reason="HUMAN_ADVICE_INVALID")
    if (
        action == "declare-scope"
        and body["data"]["conflict"] == "DECLARED"
        and body["data"]["scope_accepted"]
    ):
        raise DomainError("VALIDATION_FAILED", reason="CONFLICT_CANNOT_ACCEPT_SCOPE")


def operation(action=None):
    return "create_human_advice_case" if action is None else "human_advice_" + action.replace("-", "_")


IMPLEMENTED = [
    ("get", ROUTE),
    ("post", ROUTE),
    ("get", ROUTE + "/eligible-peers"),
    ("get", ROUTE + "/{object_id}"),
    ("get", ROUTE + "/{object_id}/revisions"),
    ("get", ROUTE + "/{object_id}/revisions/{revision_id}"),
    *[("post", ROUTE + "/{object_id}/actions/" + action) for action in ACTION_DATA],
]


def stored_schema():
    uuid = deepcopy(UUID)
    stamp = {"type": "string", "format": "date-time"}
    declaration = shape(
        {
            **deepcopy(ACTION_DATA["declare-scope"]["properties"]),
            "declared_by": uuid,
            "declared_at": stamp,
            "authenticated_at": stamp,
        }
    )
    assignment = shape(
        {
            **deepcopy(ACTION_DATA["assign"]["properties"]),
            "assigned_by": uuid,
            "assigned_at": stamp,
            "authenticated_at": stamp,
        }
    )
    action = deepcopy(ACTION_DATA["advise"]["properties"]["actions"]["items"])
    action["properties"]["action_id"] = deepcopy(UUID)
    action["required"].append("action_id")
    advice = shape(
        {
            "text": text(6000),
            "actions": {"type": "array", "maxItems": 20, "items": action},
            "advised_by": uuid,
            "advised_at": stamp,
        }
    )
    note = shape(
        {
            "note_id": uuid,
            "kind": {"enum": ["QUESTION", "RESPONSE"]},
            "text": text(4000),
            "author_id": uuid,
            "recorded_at": stamp,
        }
    )

    def nullable(schema):
        return {"oneOf": [schema, {"type": "null"}]}

    fields = {
        key: deepcopy(value)
        for key, value in CREATE_DATA["properties"].items()
        if key not in {"problem", "adviser_membership_id"}
    }
    fields.update(
        {
            key: deepcopy(UUID)
            for key in (
                "requester_principal_id",
                "requester_membership_id",
                "requester_natural_id",
                "adviser_principal_id",
                "adviser_membership_id",
                "adviser_natural_id",
            )
        }
    )
    fields.update(
        {
            "state": {"enum": STATES},
            "case_schema_version": {"const": "internal-peer-advice-v1"},
            "requester_auth_time": stamp,
            "problem_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
            "declaration": nullable(declaration),
            "assignment": nullable(assignment),
            "notes": {"type": "array", "maxItems": 50, "items": note},
            "advice": nullable(advice),
            "closure": nullable(
                shape({**deepcopy(ACTION_DATA["close"]["properties"]), "closed_by": uuid, "closed_at": stamp})
            ),
            "cancellation": nullable(
                shape({"reason": text(1000), "cancelled_by": uuid, "cancelled_at": stamp})
            ),
        }
    )
    return shape(fields)


def public_schema():
    stored = stored_schema()
    result = shape({key: deepcopy(stored["properties"][key]) for key in PUBLIC_FIELDS})
    for key, fields in PUBLIC_DECISION_FIELDS.items():
        decision = result["properties"][key]["oneOf"][0]
        result["properties"][key]["oneOf"][0] = shape(
            {field: decision["properties"][field] for field in fields}
        )
    return result


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    schemas["HumanAdviceCreate"] = request_schema()
    schemas["HumanAdviceStoredData"] = stored_schema()
    schemas["HumanAdvicePublicData"] = public_schema()
    result = shape(
        {
            "object_id": deepcopy(UUID),
            "revision_id": deepcopy(UUID),
            "business_state": {"enum": STATES},
            "context_current": {"type": "boolean"},
            "problem": {"type": ["string", "null"], "maxLength": 4000},
            "data": {"$ref": "#/components/schemas/HumanAdvicePublicData"},
        }
    )
    schemas["HumanAdviceCase"] = result
    cursor = {"type": ["string", "null"], "maxLength": 4096}
    schemas["HumanAdviceList"] = shape(
        {
            "items": {
                "type": "array",
                "maxItems": 50,
                "items": {"$ref": "#/components/schemas/HumanAdviceCase"},
            },
            "next_cursor": cursor,
        }
    )
    schemas["HumanAdviceEligiblePeers"] = shape(
        {
            "items": {
                "type": "array",
                "maxItems": 50,
                "items": shape({"membership_id": deepcopy(UUID), "display_name": text(120)}),
            },
            "next_cursor": deepcopy(cursor),
        }
    )
    history_item = shape(
        {
            "revision_id": deepcopy(UUID),
            "revision_number": {"type": "integer", "minimum": 1},
            "saved_at": {"type": "string", "format": "date-time"},
        }
    )
    schemas["HumanAdviceHistory"] = shape(
        {
            "object_id": deepcopy(UUID),
            "items": {"type": "array", "maxItems": 50, "items": history_item},
            "next_cursor": cursor,
        }
    )
    schemas["HumanAdviceReceipt"] = shape(
        {
            "object_id": deepcopy(UUID),
            "revision_id": deepcopy(UUID),
            "business_state": {"enum": STATES},
            "operation_id": deepcopy(UUID),
            "correlation_id": deepcopy(UUID),
            "saved_at": {"type": "string", "format": "date-time"},
        }
    )
    operations = [
        ("get", "", "list_human_advice_cases", None, "HumanAdviceList"),
        ("post", "", operation(), "HumanAdviceCreate", "HumanAdviceReceipt"),
        ("get", "/eligible-peers", "list_human_advice_eligible_peers", None, "HumanAdviceEligiblePeers"),
        ("get", "/{object_id}", "get_human_advice_case", None, "HumanAdviceCase"),
        ("get", "/{object_id}/revisions", "list_human_advice_revisions", None, "HumanAdviceHistory"),
        ("get", "/{object_id}/revisions/{revision_id}", "get_human_advice_revision", None, "HumanAdviceCase"),
    ]
    for action in ACTION_DATA:
        name = "HumanAdvice" + "".join(piece.title() for piece in action.split("-"))
        schemas[name] = request_schema(action)
        operations.append(
            ("post", "/{object_id}/actions/" + action, operation(action), name, "HumanAdviceReceipt")
        )
    for method, suffix, name, request, response in operations:
        path = "/v1/tenants/{tenant_id}/" + ROUTE + suffix
        write_access = method == "post"
        parameters = [
            {"name": key, "in": "path", "required": True, "schema": deepcopy(UUID)}
            for key in ("tenant_id", "object_id", "revision_id")
            if "{" + key + "}" in path
        ]
        peer_lookup = name == "list_human_advice_eligible_peers"
        if name in {"list_human_advice_cases", "list_human_advice_revisions"} or peer_lookup:
            parameters.extend(
                [
                    {
                        "name": "limit",
                        "in": "query",
                        "schema": {"type": "integer", "minimum": 1, "maximum": 50},
                    },
                    {"name": "cursor", "in": "query", "schema": {"type": "string", "maxLength": 4096}},
                ]
            )
        if peer_lookup:
            parameters.append(
                {"name": "context_plan_id", "in": "query", "required": True, "schema": deepcopy(UUID)}
            )
        capability = "ai.enablement.manage" if write_access or peer_lookup else "ai.enablement.read"
        entry = {
            "operationId": name,
            "summary": name.replace("_", " "),
            "x-capability": capability,
            "x-contract-version": VERSION,
            "parameters": parameters,
            "responses": {
                "201" if name == operation() else "200": {
                    "description": "Restricted internal peer advice; never an official approval",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
                }
            },
        }
        if request:
            entry["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
            }
        for status in ("400", "401", "403", "404", "409", "422", "429", "503"):
            entry["responses"][status] = {
                "description": "Request refused; hidden and missing cases are indistinguishable",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
            }
        spec["paths"].setdefault(path, {})[method] = entry
        policy["operations"].append(
            {
                "operation_id": name,
                "method": method.upper(),
                "path": path,
                "capability": capability,
                "role_templates": ["OWNER", "TENANT_ADMIN"]
                if peer_lookup
                else deepcopy(MANAGERS if write_access else ROLES),
                "purpose_required": False,
                "fresh_assurance_seconds": 300 if write_access else None,
                "audit": write_access,
            }
        )
