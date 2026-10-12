"""Closed contracts for self-reported, immutable problem baselines."""

from copy import deepcopy

from .measurement_contracts import closed

VERSION = "1.32.0"
ROOT = "ai-enablement/problem-baselines"
ROUTES = [
    ("get", "", "list_ai_problem_baselines", None, "AIProblemBaselineList"),
    ("post", "", "create_ai_problem_baseline", "AIProblemBaselineCreate", "AIProblemBaselineReceipt"),
    ("get", "/{object_id}", "get_ai_problem_baseline", None, "AIProblemBaseline"),
    (
        "put",
        "/{object_id}",
        "update_ai_problem_baseline",
        "AIProblemBaselineUpdate",
        "AIProblemBaselineReceipt",
    ),
    (
        "post",
        "/{object_id}/actions/lock",
        "lock_ai_problem_baseline",
        "AIProblemBaselineLock",
        "AIProblemBaselineReceipt",
    ),
    ("get", "/{object_id}/revisions", "list_ai_problem_baseline_revisions", None, "AIProblemBaselineHistory"),
    (
        "get",
        "/{object_id}/revisions/{revision_id}",
        "get_ai_problem_baseline_revision",
        None,
        "AIProblemBaseline",
    ),
]
IMPLEMENTED = [(method, ROOT + suffix) for method, suffix, *_ in ROUTES]


def augment(spec, policy):
    schemas = spec["components"]["schemas"]
    uid = {"type": "string", "format": "uuid"}
    decimal = {"type": "string", "pattern": r"^-?(?:0|[1-9][0-9]{0,25})(?:\.[0-9]{1,12})?$"}
    measure = {
        "value": decimal,
        "unit": {"type": "string", "minLength": 1, "maxLength": 80},
        "basis": {"type": "string", "minLength": 1, "maxLength": 500},
        "observed_from": {"type": "string", "format": "date"},
        "observed_to": {"type": "string", "format": "date"},
    }
    schemas["AIProblemBaselineMeasure"] = closed(measure, list(measure))
    metrics = {
        key: {"$ref": "#/components/schemas/AIProblemBaselineMeasure"}
        for key in ("time", "cost", "quality", "reach")
    }
    schemas["AIProblemBaselineMetrics"] = closed(metrics, [])
    ref = {"object_id": deepcopy(uid), "revision_id": deepcopy(uid)}
    schemas["AIProblemBaselineEvidenceReference"] = closed(ref, list(ref))
    data = {
        "diagnosis_id": deepcopy(uid),
        "diagnosis_revision": deepcopy(uid),
        "problem_id": deepcopy(uid),
        "title": {"type": "string", "minLength": 1, "maxLength": 150},
        "metrics": {"$ref": "#/components/schemas/AIProblemBaselineMetrics"},
        "supporting_evidence": {"type": "string", "maxLength": 4000},
        "evidence_references": {
            "type": "array",
            "maxItems": 5,
            "uniqueItems": True,
            "items": {"$ref": "#/components/schemas/AIProblemBaselineEvidenceReference"},
        },
    }
    schemas["AIProblemBaselineData"] = closed(data, list(data))
    create = {"operation_id": deepcopy(uid), "data": {"$ref": "#/components/schemas/AIProblemBaselineData"}}
    schemas["AIProblemBaselineCreate"] = closed(create, list(create))
    update = {**create, "expected_revision": deepcopy(uid)}
    schemas["AIProblemBaselineUpdate"] = closed(update, list(update))
    lock = {"operation_id": deepcopy(uid), "expected_revision": deepcopy(uid)}
    schemas["AIProblemBaselineLock"] = closed(lock, list(lock))
    stored = {
        **deepcopy(data),
        "locked_at": {"type": "string", "format": "date-time"},
        "locked_by": deepcopy(uid),
    }
    schemas["AIProblemBaselineStoredData"] = closed(stored, list(data))
    state = {"enum": ["Draft", "Locked"]}
    result = {
        "object_id": deepcopy(uid),
        "revision_id": deepcopy(uid),
        "business_state": deepcopy(state),
        "data": {"$ref": "#/components/schemas/AIProblemBaselineStoredData"},
    }
    schemas["AIProblemBaseline"] = closed(result, list(result))
    receipt = {key: deepcopy(value) for key, value in result.items() if key != "data"}
    receipt.update(
        operation_id=deepcopy(uid),
        correlation_id=deepcopy(uid),
        saved_at={"type": "string", "format": "date-time"},
    )
    schemas["AIProblemBaselineReceipt"] = closed(receipt, list(receipt))
    schemas["AIProblemBaselineList"] = closed(
        {
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/AIProblemBaseline"},
            },
            "next_cursor": {"type": ["string", "null"]},
        },
        ["items", "next_cursor"],
    )
    schemas["AIProblemBaselineHistoryItem"] = closed(
        {
            "revision_id": deepcopy(uid),
            "revision_number": {"type": "integer", "minimum": 1},
            "saved_at": {"type": "string", "format": "date-time"},
            "business_state": deepcopy(state),
            "title": {"type": "string", "maxLength": 150},
        },
        ["revision_id", "revision_number", "saved_at", "business_state", "title"],
    )
    schemas["AIProblemBaselineHistory"] = closed(
        {
            "object_id": deepcopy(uid),
            "items": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/AIProblemBaselineHistoryItem"},
            },
            "next_cursor": {"type": ["string", "null"]},
        },
        ["object_id", "items", "next_cursor"],
    )
    for method, suffix, operation, request, response in ROUTES:
        path = "/v1/tenants/{tenant_id}/" + ROOT + suffix
        parameters = [{"name": "tenant_id", "in": "path", "required": True, "schema": deepcopy(uid)}]
        for name in ("object_id", "revision_id"):
            if "{" + name + "}" in suffix:
                parameters.append({"name": name, "in": "path", "required": True, "schema": deepcopy(uid)})
        if operation in ("list_ai_problem_baselines", "list_ai_problem_baseline_revisions"):
            parameters += [
                {"name": "limit", "in": "query", "schema": {"type": "integer", "minimum": 1, "maximum": 100}},
                {"name": "cursor", "in": "query", "schema": {"type": "string", "maxLength": 4096}},
            ]
        capability = "ai.problem-baseline.manage" if request else "ai.problem-baseline.read"
        entry = {
            "operationId": operation,
            "summary": operation.replace("_", " "),
            "x-capability": capability,
            "x-contract-version": VERSION,
            "parameters": parameters,
            "responses": {},
        }
        entry["responses"]["201" if operation == "create_ai_problem_baseline" else "200"] = {
            "description": "Self-reported problem baseline; Locked is immutable but is not independent approval",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + response}}},
        }
        for refusal in ("400", "401", "403", "404", "409", "422", "429", "503"):
            entry["responses"][refusal] = {
                "description": "Request refused",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
            }
        if request:
            entry["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + request}}},
            }
        spec["paths"].setdefault(path, {})[method] = entry
        policy["operations"].append(
            {
                "operation_id": operation,
                "method": method.upper(),
                "path": path,
                "capability": capability,
                "role_templates": ["TENANT_ADMIN"],
                "purpose_required": False,
                "fresh_assurance_seconds": 300 if operation == "lock_ai_problem_baseline" else None,
                "audit": request is not None,
            }
        )
