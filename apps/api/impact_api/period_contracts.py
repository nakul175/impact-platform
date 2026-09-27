"""Contracts for independently reviewed period closure and restatement."""

from copy import deepcopy
import json

from .measurement_contracts import DATE, UUID, closed, text_field

READS = {"period-closes": "PeriodClose", "restatement-requests": "RestatementRequest"}


def nullable_uuid():
    return {"type": ["string", "null"], "format": "uuid"}


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    prefix = "/v1/tenants/{tenant_id}/"
    schemas["SnapshotData"]["properties"]["programme_id"] = UUID
    blocker = closed(
        {"code": text_field(64), "message": text_field(2000), "object_id": nullable_uuid()},
        ["code", "message", "object_id"],
    )
    schemas["PeriodCloseEntry"] = closed(
        {
            "indicator_id": UUID,
            "indicator_revision": UUID,
            "definition_revision": UUID,
            "plan_id": UUID,
            "plan_revision": UUID,
            "result_id": nullable_uuid(),
            "result_revision": nullable_uuid(),
            "source_revisions": {"type": "array", "maxItems": 10000, "items": UUID},
            "source_digest": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
            "coverage": {"$ref": "#/components/schemas/Coverage"},
            "blockers": {"type": "array", "maxItems": 100, "items": blocker},
        },
        [
            "indicator_id",
            "indicator_revision",
            "definition_revision",
            "plan_id",
            "plan_revision",
            "result_id",
            "result_revision",
            "source_revisions",
            "source_digest",
            "coverage",
            "blockers",
        ],
    )
    schemas["PeriodCloseData"] = closed(
        {
            "period_id": UUID,
            "programme_id": UUID,
            "period_revision": UUID,
            "programme_period_state": {"enum": ["Open", "RestatementOpen"]},
            "reason": text_field(2000),
            "previewed_at": DATE,
            "fingerprint": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
            "previous_snapshot_id": nullable_uuid(),
            "entries": {
                "type": "array",
                "maxItems": 500,
                "items": {"$ref": "#/components/schemas/PeriodCloseEntry"},
            },
            "blockers": {"type": "array", "maxItems": 500, "items": blocker},
        },
        [
            "period_id",
            "programme_id",
            "period_revision",
            "programme_period_state",
            "reason",
            "previewed_at",
            "fingerprint",
            "previous_snapshot_id",
            "entries",
            "blockers",
        ],
    )
    schemas["RestatementRequestData"] = closed(
        {
            "period_id": UUID,
            "programme_id": UUID,
            "period_revision": UUID,
            "snapshot_id": UUID,
            "snapshot_revision": UUID,
            "reason": text_field(2000),
            "source_ids": {
                "type": "array",
                "minItems": 1,
                "maxItems": 100,
                "uniqueItems": True,
                "items": UUID,
            },
            "expires_at": DATE,
        },
        [
            "period_id",
            "programme_id",
            "period_revision",
            "snapshot_id",
            "snapshot_revision",
            "reason",
            "source_ids",
            "expires_at",
        ],
    )
    for kind in READS.values():
        for suffix in ["", "List"]:
            schemas[kind + suffix] = json.loads(
                json.dumps(schemas["Programme" + suffix]).replace("Programme", kind)
            )
    for route, kind in READS.items():
        for item in [False, True]:
            suffix = "/{object_id}" if item else ""
            template = paths[prefix + "programmes" + suffix]
            path = prefix + route + suffix
            entry = json.loads(json.dumps(template["get"]).replace("Programme", kind))
            op = ("get_" if item else "list_") + route.replace("-", "_")
            entry.update(
                operationId=op,
                summary=op.replace("_", " "),
                **{"x-capability": route + ".read", "x-contract-version": "1.6.0"},
            )
            paths[path] = {"parameters": deepcopy(template["parameters"]), "get": entry}
            policy["operations"].append(
                {
                    "operation_id": op,
                    "method": "GET",
                    "path": path,
                    "capability": route + ".read",
                    "role_templates": ["AUTHOR", "REVIEWER", "MEL_ADMIN", "PROGRAMME_MANAGER"],
                    "purpose_required": False,
                    "fresh_assurance_seconds": None,
                    "audit": False,
                }
            )

    def replace_action(action, schema, props, required, capability, roles):
        name = "PeriodGovernance" + action.title()
        schemas[name + "Data"] = closed(props, required)
        schemas[name] = closed(
            {
                "operation_id": UUID,
                "expected_revision": UUID,
                "data": {"$ref": "#/components/schemas/" + name + "Data"},
            },
            ["operation_id", "expected_revision", "data"],
        )
        path = prefix + "periods/{object_id}/actions/" + action
        entry = paths[path]["post"]
        entry["requestBody"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/" + name
        }
        entry["responses"]["200"] = entry["responses"].pop("202")
        entry["responses"]["200"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/Receipt"
        }
        entry.update(**{"x-capability": capability, "x-contract-version": "1.6.0"})
        op = "action_periods_" + action
        policy["operations"] = [p for p in policy["operations"] if p["operation_id"] != op]
        policy["operations"].append(
            {
                "operation_id": op,
                "method": "POST",
                "path": path,
                "capability": capability,
                "role_templates": roles,
                "purpose_required": False,
                "fresh_assurance_seconds": 300,
                "audit": True,
            }
        )

    replace_action(
        "close",
        "PeriodGovernanceClose",
        {"workflow_version": UUID, "programme_id": UUID, "reason": text_field(2000)},
        ["workflow_version", "programme_id", "reason"],
        "period.close",
        ["MEL_ADMIN", "PROGRAMME_MANAGER"],
    )
    replace_action(
        "restate",
        "PeriodGovernanceRestate",
        {
            "workflow_version": UUID,
            "programme_id": UUID,
            "reason": text_field(2000),
            "source_ids": {
                "type": "array",
                "minItems": 1,
                "maxItems": 100,
                "uniqueItems": True,
                "items": UUID,
            },
            "expires_at": DATE,
        },
        ["workflow_version", "programme_id", "reason", "source_ids", "expires_at"],
        "period.restate",
        ["MEL_ADMIN", "PROGRAMME_MANAGER"],
    )
    candidate = schemas["ReviewCandidate"]["properties"]
    for kind in READS.values():
        candidate["kind"]["enum"].append(kind)
        candidate["record"]["oneOf"].append({"$ref": "#/components/schemas/" + kind})
    candidate["current_target"]["oneOf"].append({"$ref": "#/components/schemas/Period"})
    spec["info"]["version"] = policy["version"] = "1.6.0"
