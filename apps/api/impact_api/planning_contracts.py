"""Results framework and planning contracts (v0.18): the design contract's framework and target
routes, tightened to what this build implements, plus two read models."""

from copy import deepcopy

from .measurement_contracts import closed, text_field

UUID = {"type": "string", "format": "uuid"}
DATE = {"type": "string", "format": "date-time"}
DECIMAL = r"^-?(0|[1-9][0-9]{0,25})(\.[0-9]{1,12})?$"
NULLABLE_DECIMAL = {"type": ["string", "null"], "pattern": DECIMAL}
NODE_TYPES = ["IMPACT", "OUTCOME", "OUTPUT", "ACTIVITY"]
EXCEPTABLE_RULES = ["UNMEASURED_RESULT", "ORPHAN_NODE", "ORPHAN_INDICATOR"]
VALUE_STATES = ["PRESENT", "MISSING", "NOT_COLLECTED", "NOT_APPLICABLE", "INVALID", "UNDEFINED"]
SPECIAL_READS = {
    "frameworks/{object_id}/completeness": (
        "framework_completeness",
        "frameworks.read",
        "FrameworkCompleteness",
    ),
    "programmes/{object_id}/targets-vs-actuals": (
        "programme_targets_vs_actuals",
        "targets.read",
        "TargetsVersusActuals",
    ),
}
VERSION = "1.11.0"


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    prefix = "/v1/tenants/{tenant_id}/"

    # A framework node: stable identity, intended result level, owner and indicator placement.
    # Theory-of-change relationships (FR-PLN-002, P1) and assumption nodes (FR-PLN-007) are not
    # implemented, so the design's relationship array is accepted only empty.
    schemas["FrameworkNode"] = closed(
        {
            "node_id": UUID,
            "node_type": {"enum": NODE_TYPES},
            "title": text_field(200),
            "definition": text_field(2000),
            "parent_node_id": {"type": ["string", "null"], "format": "uuid"},
            "owner_id": {"type": ["string", "null"], "format": "uuid"},
            "indicator_ids": {"type": "array", "items": UUID, "maxItems": 50, "uniqueItems": True},
        },
        ["node_id", "node_type", "title", "definition"],
    )
    exception = closed(
        {
            "object_id": UUID,
            "rule": {"enum": EXCEPTABLE_RULES},
            "reason": text_field(2000),
            "review_date": {"type": "string", "format": "date"},
        },
        ["object_id", "rule", "reason", "review_date"],
    )
    framework = {
        "programme_id": UUID,
        "version_label": text_field(64),
        "nodes": {"type": "array", "items": {"$ref": "#/components/schemas/FrameworkNode"}, "maxItems": 500},
        "relationships": {"type": "array", "maxItems": 0},
        "effective_from": DATE,
        "supersedes_revision": UUID,
        "exceptions": {"type": "array", "items": exception, "maxItems": 500},
    }
    schemas["FrameworkData"] = closed(deepcopy(framework))
    schemas["FrameworkDraftData"] = closed(deepcopy(framework))

    # Targets, baselines and milestones for one indicator instance in one programme period. The
    # definition revision is pinned by submission (never accepted from a draft command); a blank
    # target keeps its value state and no value, never zero.
    target = {
        "indicator_id": UUID,
        "period_id": UUID,
        "target_kind": {"enum": ["VALUE", "RANGE", "MILESTONE"]},
        "value_state": {"enum": VALUE_STATES},
        "value": NULLABLE_DECIMAL,
        "low": NULLABLE_DECIMAL,
        "high": NULLABLE_DECIMAL,
        "direction": {"enum": ["HIGHER", "LOWER", "RANGE", "MILESTONE"]},
        "target_basis": {"enum": ["ORIGINAL", "REVISED", "BASELINE"]},
        "milestone_label": {"type": ["string", "null"], "minLength": 1, "maxLength": 200, "pattern": r"\S"},
        "due_at": {"type": ["string", "null"], "format": "date-time"},
        "supersedes_revision": {"type": ["string", "null"], "format": "uuid"},
        "reason": {"type": ["string", "null"], "maxLength": 2000},
    }
    blank = {
        "if": {"properties": {"value_state": {"const": "PRESENT"}}, "required": ["value_state"]},
        "then": {},
        "else": {
            "properties": {"value": {"type": "null"}, "low": {"type": "null"}, "high": {"type": "null"}}
        },
    }
    schemas["TargetDraftData"] = {**closed(deepcopy(target)), "allOf": [deepcopy(blank)]}
    schemas["TargetData"] = {
        **closed({**deepcopy(target), "indicator_version": UUID}),
        "allOf": [deepcopy(blank)],
    }
    for kind in ["Framework", "Target"]:
        # The design patch schema references the draft schema; keep its shallow-merge semantics.
        schemas[kind + "Patch"]["properties"]["data"] = {
            "allOf": [{"$ref": "#/components/schemas/" + kind + "DraftData"}],
            "minProperties": 1,
        }

    for route in ["frameworks", "targets"]:
        for suffix, methods in [("", ["get", "post"]), ("/{object_id}", ["get", "patch"])]:
            for method in methods:
                paths[prefix + route + suffix][method]["x-contract-version"] = VERSION
        paths[prefix + route + "/{object_id}/actions/submit"]["post"]["x-contract-version"] = VERSION

    issue = closed(
        {
            "severity": {"enum": ["ERROR", "WARNING"]},
            "rule": text_field(64),
            "object_id": UUID,
            "message": text_field(2000),
            "resolver_id": {"type": ["string", "null"], "format": "uuid"},
            "exceptable": {"type": "boolean"},
            "excepted": {"type": "boolean"},
            "exception": {"oneOf": [{"type": "null"}, exception]},
        },
        ["severity", "rule", "object_id", "message", "resolver_id", "exceptable", "excepted"],
    )
    schemas["FrameworkCompleteness"] = closed(
        {
            "framework_id": UUID,
            "revision_id": UUID,
            "ready": {"type": "boolean"},
            "issues": {"type": "array", "maxItems": 2000, "items": issue},
            "comparison": {
                "oneOf": [
                    {"type": "null"},
                    closed(
                        {
                            "base_revision": UUID,
                            "base_version": {"type": "integer", "minimum": 1},
                            "added": {"type": "array", "items": UUID},
                            "removed": {"type": "array", "items": UUID},
                            "changed": {"type": "array", "items": UUID},
                            "affected_indicator_ids": {"type": "array", "items": UUID},
                        },
                        [
                            "base_revision",
                            "base_version",
                            "added",
                            "removed",
                            "changed",
                            "affected_indicator_ids",
                        ],
                    ),
                ]
            },
        },
        ["framework_id", "revision_id", "ready", "issues", "comparison"],
    )
    target_view = closed(
        {
            "target_id": UUID,
            "revision_id": UUID,
            "target_kind": text_field(64),
            "target_basis": text_field(64),
            "direction": text_field(64),
            "value_state": {"enum": VALUE_STATES},
            "value": NULLABLE_DECIMAL,
            "low": NULLABLE_DECIMAL,
            "high": NULLABLE_DECIMAL,
            "milestone_label": {"type": ["string", "null"]},
            "due_at": {"type": ["string", "null"]},
            "binding_version": {"type": "integer", "minimum": 1},
        },
        ["target_id", "revision_id", "target_kind", "target_basis", "direction", "value_state"],
    )
    row = closed(
        {
            "indicator_id": UUID,
            "indicator_label": text_field(2000),
            "unit": {"type": ["string", "null"]},
            "display_decimals": {"type": "integer", "minimum": 0, "maximum": 6},
            "period_id": UUID,
            "period_code": {"type": ["string", "null"]},
            "period_state": {"enum": ["Open", "Locked", "RestatementOpen"]},
            "framework_revision": {"type": ["string", "null"], "format": "uuid"},
            "node_ids": {"type": "array", "items": UUID},
            "baseline": {"oneOf": [{"type": "null"}, target_view]},
            "target": {"oneOf": [{"type": "null"}, target_view]},
            "milestones": {"type": "array", "items": target_view},
            "actual": closed(
                {
                    "mode": {"enum": ["OFFICIAL", "PROVISIONAL", "NONE"]},
                    "source": {"enum": ["PROGRAMME_SNAPSHOT", "UNBOUND_SNAPSHOT", "CALCULATION", "NONE"]},
                    "value_state": {"enum": VALUE_STATES},
                    "value": NULLABLE_DECIMAL,
                    "displayed_value": {"type": ["string", "null"]},
                    "result_id": {"type": ["string", "null"], "format": "uuid"},
                    "result_revision": {"type": ["string", "null"], "format": "uuid"},
                    "snapshot_id": {"type": ["string", "null"], "format": "uuid"},
                    "stale": {"type": "boolean"},
                },
                ["mode", "source", "value_state", "value", "displayed_value", "stale"],
            ),
            "progress": closed(
                {
                    "status": text_field(64),
                    "attainment_percent": {"type": ["string", "null"]},
                    "deviation": NULLABLE_DECIMAL,
                    "displayed_deviation": {"type": ["string", "null"]},
                    "change_from_baseline": NULLABLE_DECIMAL,
                    "change_from_baseline_percent": {"type": ["string", "null"]},
                    "reason_code": {"type": ["string", "null"]},
                },
                ["status", "attainment_percent", "deviation", "reason_code"],
            ),
        },
        [
            "indicator_id",
            "period_id",
            "period_state",
            "node_ids",
            "baseline",
            "target",
            "milestones",
            "actual",
            "progress",
        ],
    )
    schemas["TargetsVersusActuals"] = closed(
        {
            "programme_id": UUID,
            "framework": {
                "oneOf": [
                    {"type": "null"},
                    closed(
                        {
                            "framework_id": UUID,
                            "revision_id": UUID,
                            "baseline_version": {"type": "integer", "minimum": 1},
                            "effective_from": {"type": "string"},
                            "version_label": {"type": "string"},
                            "nodes": {
                                "type": "array",
                                "items": {"$ref": "#/components/schemas/FrameworkNode"},
                            },
                        },
                        ["framework_id", "revision_id", "baseline_version", "effective_from", "nodes"],
                    ),
                ]
            },
            "rows": {"type": "array", "maxItems": 500, "items": row},
        },
        ["programme_id", "framework", "rows"],
    )

    for route, (op, cap, schema) in SPECIAL_READS.items():
        base = "frameworks" if route.startswith("frameworks") else "programmes"
        template = deepcopy(paths[prefix + base + "/{object_id}"])
        entry = template["get"]
        entry.pop("parameters", None)
        entry["responses"]["200"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/" + schema
        }
        entry.update(
            operationId=op,
            summary=op.replace("_", " "),
            **{"x-capability": cap, "x-contract-version": VERSION},
        )
        paths[prefix + route] = {"parameters": template["parameters"], "get": entry}
        policy["operations"] = [p for p in policy["operations"] if p["operation_id"] != op]
        policy["operations"].append(
            {
                "operation_id": op,
                "method": "GET",
                "path": prefix + route,
                "capability": cap,
                "role_templates": ["MEL_ADMIN", "PROGRAMME_MANAGER", "AUTHOR", "REVIEWER", "ANALYST"],
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": False,
            }
        )

    candidate = schemas["ReviewCandidate"]["properties"]
    for kind in ["Framework", "Target"]:
        if kind not in candidate["kind"]["enum"]:
            candidate["kind"]["enum"].append(kind)
            candidate["record"]["oneOf"].append({"$ref": "#/components/schemas/" + kind})
    # The approved record a Framework or Target draft supersedes, shown beside the candidate.
    candidate["superseded"] = {
        "oneOf": [{"$ref": "#/components/schemas/Framework"}, {"$ref": "#/components/schemas/Target"}]
    }
    candidate["completeness"] = {"$ref": "#/components/schemas/FrameworkCompleteness"}
    spec["info"]["version"] = policy["version"] = VERSION
