"""Nonprofit AI enablement: editorial assessment and separately permitted advisory drafts."""

from copy import deepcopy

from .measurement_contracts import closed

VERSION = "1.20.0"
# FR-AI-001 (build 0.37.0): the tenant AI policy routes and the advisory request's policy pin.
POLICY_VERSION = "1.26.0"
IMPLEMENTED = [
    ("get", "ai-enablement/catalog"),
    ("post", "ai-enablement/assessment"),
    ("post", "ai-enablement/advisory"),
    ("get", "ai-enablement/solutions"),
    ("get", "ai-enablement/policy"),
    ("put", "ai-enablement/policy"),
    ("get", "ai-enablement/policy/revisions"),
]
ROLES = ["TENANT_ADMIN", "MEL_ADMIN", "PROGRAMME_MANAGER", "AUTHOR", "REVIEWER", "ANALYST", "DATA_STEWARD"]
# Changing the policy is an administrative, sensitive action: TENANT_ADMIN only, with authentication
# within the previous 300 seconds plus the configured assurance (store.authorize), always audited.
POLICY_MANAGERS = ["TENANT_ADMIN"]
POLICY_CAPABILITY = "ai.policy.manage"
USE_CASES = ["ADVISORY_DRAFT", "EXTRACTION", "REPORT_DRAFT", "CHAT"]
DATA_CLASSES = ["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"]
# The closed provider-and-region list. Adding a destination is a reviewed change to this list and to
# the CHECK constraint of migration 0041; a tenant policy starts with no destination selected.
DESTINATIONS = ["openai-us"]
REVIEW_MODES = ["HUMAN_REVIEW"]
LANGUAGE_PATTERN = "^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8}){0,3}$"
TOOL_PATTERN = "^[a-z][a-z0-9_.-]{0,63}$"
MAX_BUDGET_UNITS = 1000000
MAX_POLICY_VERSION = 2147483647


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    schemas["AIEnablementProfile"] = closed(
        {
            "sector": {"enum": ["GENERAL", "EDUCATION", "HEALTH", "LIVELIHOODS", "ENVIRONMENT"]},
            "team_size": {"type": "integer", "minimum": 1, "maximum": 100000},
            "goal": {"type": "string", "minLength": 1, "maxLength": 1000},
            "data_readiness": {"enum": ["NONE", "BASIC", "STRUCTURED"]},
            "ai_experience": {"enum": ["NONE", "EXPERIMENTING", "REGULAR"]},
            "sensitive_data": {"type": "boolean"},
        },
        ["sector", "team_size", "goal", "data_readiness", "ai_experience", "sensitive_data"],
    )
    schemas["AIAssessmentRequest"] = closed(
        {"profile": {"$ref": "#/components/schemas/AIEnablementProfile"}}, ["profile"]
    )
    schemas["AIAdvisoryRequest"] = closed(
        {
            "operation_id": {"type": "string", "format": "uuid"},
            "profile": {"$ref": "#/components/schemas/AIEnablementProfile"},
            "consent": {"const": True},
            # The policy version shown to the requester ("Policy in force"); a request made against
            # any other version is refused with 409 AI_POLICY_CHANGED before any reservation.
            "policy_version": {"type": "integer", "minimum": 0, "maximum": MAX_POLICY_VERSION},
            # Tools are never implicit: a tool the use case's policy does not list is refused with
            # 422 AI_POLICY_BLOCKED. No policy can list a tool in this build.
            "tools": {
                "type": "array",
                "maxItems": 10,
                "uniqueItems": True,
                "items": {"type": "string", "pattern": TOOL_PATTERN},
            },
        },
        ["operation_id", "profile", "consent", "policy_version"],
    )
    policy_schemas(schemas)
    # This increment publishes versioned editorial content, not an authored domain object.
    schemas["AIEnablementCatalog"] = {
        "type": "object",
        "required": [
            "schema_version",
            "content_version",
            "provenance",
            "journey",
            "use_cases",
            "learning_paths",
            "procurement_criteria",
            "marketplace_status",
            "advisory_available",
        ],
    }
    schemas["AIEnablementAssessment"] = closed({"assessment": {"type": "object"}}, ["assessment"])
    schemas["AISolutionsCatalog"] = {
        "type": "object",
        "required": ["content_version", "checked_on", "explanation", "solutions", "comparison_criteria"],
    }
    schemas["AIAdvisoryDraft"] = closed(
        {
            "status": {"const": "DRAFT"},
            "text": {"type": "string", "maxLength": 12000},
            "assessment": {"type": "object"},
            "model": {"type": "string"},
            "disclaimer": {"type": "string"},
        },
        ["status", "text", "assessment", "model", "disclaimer"],
    )
    for method, route, op, cap, request, response, roles in [
        (
            "get",
            "ai-enablement/catalog",
            "get_ai_enablement_catalog",
            "ai.enablement.read",
            None,
            "AIEnablementCatalog",
            ROLES,
        ),
        (
            "post",
            "ai-enablement/assessment",
            "assess_ai_enablement",
            "ai.enablement.read",
            "AIAssessmentRequest",
            "AIEnablementAssessment",
            ROLES,
        ),
        (
            "get",
            "ai-enablement/solutions",
            "get_ai_solutions",
            "ai.enablement.read",
            None,
            "AISolutionsCatalog",
            ROLES,
        ),
        (
            "post",
            "ai-enablement/advisory",
            "create_ai_advisory",
            "ai.advisory.request",
            "AIAdvisoryRequest",
            "AIAdvisoryDraft",
            ["TENANT_ADMIN", "MEL_ADMIN", "PROGRAMME_MANAGER"],
        ),
    ]:
        path = "/v1/tenants/{tenant_id}/" + route
        node = {
            "parameters": [
                {
                    "name": "tenant_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "format": "uuid"},
                }
            ]
        }
        entry = {
            "operationId": op,
            "summary": op.replace("_", " "),
            "x-capability": cap,
            "x-contract-version": VERSION,
            "responses": {
                "200": {
                    "description": "Editorial content or unapproved draft",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
                }
            },
        }
        if request:
            entry["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
            }
        for status in ["400", "401", "403", "404", "409", "429", "503"]:
            entry["responses"][status] = {
                "description": "Request refused",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
            }
        node[method] = entry
        spec["paths"][path] = node
        policy["operations"].append(
            {
                "operation_id": op,
                "method": method.upper(),
                "path": path,
                "capability": cap,
                "role_templates": deepcopy(roles),
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": op == "create_ai_advisory",
            }
        )
    policy_paths(spec, policy)


def _strings(enum=None, pattern=None, maximum=10, length=None):
    items = {"type": "string"}
    if enum is not None:
        items = {"enum": list(enum)}
    if pattern:
        items["pattern"] = pattern
    if length:
        items.update(minLength=1, maxLength=length)
    return {"type": "array", "maxItems": maximum, "uniqueItems": True, "items": items}


def policy_schemas(schemas):
    """Closed schemas of the versioned tenant AI policy (FR-AI-001, migration 0041)."""
    rule = {
        "use_case": {"enum": list(USE_CASES)},
        "enabled": {"type": "boolean"},
        "data_classes": _strings(DATA_CLASSES, maximum=len(DATA_CLASSES)),
        "destinations": _strings(DESTINATIONS, maximum=10),
        "purposes": _strings(maximum=10, length=200),
        "languages": _strings(pattern=LANGUAGE_PATTERN, maximum=20),
        "review_mode": {"enum": list(REVIEW_MODES)},
        "budget_units": {"type": "integer", "minimum": 0, "maximum": MAX_BUDGET_UNITS},
        # Empty by default and, in this build, always: no tool catalogue exists yet.
        "tools": {"type": "array", "maxItems": 0, "items": {"type": "string", "pattern": TOOL_PATTERN}},
    }
    schemas["AIUseCasePolicy"] = closed(rule, list(rule))
    schemas["AIPolicyData"] = closed(
        {
            "use_cases": {
                "type": "array",
                "maxItems": len(USE_CASES),
                "items": {"$ref": "#/components/schemas/AIUseCasePolicy"},
            }
        },
        ["use_cases"],
    )
    command = {
        "operation_id": {"type": "string", "format": "uuid"},
        # 0 when the tenant has no policy yet; otherwise the version the editor was opened on.
        "expected_version": {"type": "integer", "minimum": 0, "maximum": MAX_POLICY_VERSION},
        "data": {"$ref": "#/components/schemas/AIPolicyData"},
    }
    schemas["AIPolicyCommand"] = closed(command, list(command))
    destination = {
        "id": {"enum": list(DESTINATIONS)},
        "provider": {"type": "string"},
        "region": {"type": "string"},
    }
    schemas["AIPolicyDestination"] = closed(destination, list(destination))
    nullable_uuid = {"type": ["string", "null"], "format": "uuid"}
    version = {
        "policy_version": {"type": "integer", "minimum": 0, "maximum": MAX_POLICY_VERSION},
        "policy_version_id": deepcopy(nullable_uuid),
        "created_at": {"type": ["string", "null"], "format": "date-time"},
        "created_by": deepcopy(nullable_uuid),
        "use_cases": {
            "type": "array",
            "maxItems": len(USE_CASES),
            "items": {"$ref": "#/components/schemas/AIUseCasePolicy"},
        },
    }
    schemas["AIPolicyRevision"] = closed(version, list(version))
    view = {
        **deepcopy(version),
        "server_enabled": {"type": "boolean"},
        "advisory_available": {"type": "boolean"},
        "destinations": {
            "type": "array",
            "items": {"$ref": "#/components/schemas/AIPolicyDestination"},
        },
        "reserved_use_cases": {"type": "array", "items": {"enum": list(USE_CASES)}},
    }
    schemas["AIPolicy"] = closed(view, list(view))
    schemas["AIPolicyRevisionList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/AIPolicyRevision"},
            },
            "next_cursor": {"type": ["string", "null"]},
        },
        ["items", "next_cursor"],
    )
    receipt = {
        "object_id": {"type": "string", "format": "uuid"},
        "revision_id": {"type": "string", "format": "uuid"},
        "policy_version": {"type": "integer", "minimum": 1, "maximum": MAX_POLICY_VERSION},
        "policy_version_id": {"type": "string", "format": "uuid"},
        "business_state": {"const": "Active"},
        "saved_at": {"type": "string", "format": "date-time"},
        "operation_id": {"type": "string", "format": "uuid"},
        "correlation_id": {"type": "string", "format": "uuid"},
    }
    schemas["AIPolicyReceipt"] = closed(receipt, list(receipt))


def policy_paths(spec, policy):
    """GET and PUT .../ai-enablement/policy and GET .../policy/revisions."""
    for method, suffix, op, cap, request, response, roles, fresh in [
        ("get", "", "get_ai_policy", "ai.enablement.read", None, "AIPolicy", ROLES, None),
        (
            "put",
            "",
            "update_ai_policy",
            POLICY_CAPABILITY,
            "AIPolicyCommand",
            "AIPolicyReceipt",
            POLICY_MANAGERS,
            300,
        ),
        (
            "get",
            "/revisions",
            "list_ai_policy_revisions",
            "ai.enablement.read",
            None,
            "AIPolicyRevisionList",
            ROLES,
            None,
        ),
    ]:
        path = "/v1/tenants/{tenant_id}/ai-enablement/policy" + suffix
        parameters = [
            {
                "name": "tenant_id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            }
        ]
        if op == "list_ai_policy_revisions":
            parameters += [
                {"name": "limit", "in": "query", "schema": {"type": "integer", "minimum": 1, "maximum": 100}},
                {"name": "cursor", "in": "query", "schema": {"type": "string", "maxLength": 4096}},
            ]
        entry = {
            "operationId": op,
            "summary": op.replace("_", " "),
            "x-capability": cap,
            "x-contract-version": POLICY_VERSION,
            "parameters": parameters,
            "responses": {
                "200": {
                    "description": "The policy in force, its history or the new version's receipt",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
                }
            },
        }
        if request:
            entry["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
            }
        for status in ["400", "401", "403", "404", "409", "422", "503"]:
            entry["responses"][status] = {
                "description": "Request refused",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
            }
        spec["paths"].setdefault(path, {})[method] = entry
        policy["operations"].append(
            {
                "operation_id": op,
                "method": method.upper(),
                "path": path,
                "capability": cap,
                "role_templates": deepcopy(roles),
                "purpose_required": False,
                "fresh_assurance_seconds": fresh,
                "audit": op == "update_ai_policy",
            }
        )
