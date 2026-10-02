"""Results framework and planning contracts (v0.18): the design contract's framework and target
routes, tightened to what this build implements, plus two read models. v0.27 adds theory-of-change
relationships, assumption records, status thresholds, the amendment fields of targets versus actuals
and the review candidate's amendment comparison (no new route or capability)."""

from copy import deepcopy

from .measurement_contracts import closed, text_field

UUID = {"type": "string", "format": "uuid"}
DATE = {"type": "string", "format": "date-time"}
DECIMAL = r"^-?(0|[1-9][0-9]{0,25})(\.[0-9]{1,12})?$"
NULLABLE_DECIMAL = {"type": ["string", "null"], "pattern": DECIMAL}
NODE_TYPES = ["IMPACT", "OUTCOME", "OUTPUT", "ACTIVITY"]
EXCEPTABLE_RULES = [
    "UNMEASURED_RESULT",
    "ORPHAN_NODE",
    "ORPHAN_INDICATOR",
    "UNTESTED_RELATIONSHIP",
    "UNLINKED_ASSUMPTION",
    "ASSUMPTION_INVALID",
    "ASSUMPTION_REVIEW_DUE",
]
# Theory-of-change links are directed contributions between two nodes of one framework (FR-PLN-002);
# DEPENDS_ON states the same contribution from the dependent side. Neither creates a numeric rule.
RELATIONSHIP_TYPES = ["CONTRIBUTES_TO", "DEPENDS_ON"]
EVIDENCE_STRENGTHS = ["STRONG", "MODERATE", "WEAK", "UNTESTED"]
ASSUMPTION_KINDS = ["ASSUMPTION", "RISK", "CONTEXT"]
ASSUMPTION_STATUSES = ["UNTESTED", "HOLDS", "AT_RISK", "INVALID"]
# ATTAINMENT_PERCENT bands a higher-is-better value target by attainment; DEVIATION bands any value
# or range target by the adverse distance from the target in the indicator's unit.
THRESHOLD_SCHEMES = ["ATTAINMENT_PERCENT", "DEVIATION"]
BANDS = ["ON_TRACK", "AT_RISK", "OFF_TRACK"]
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
    # A theory-of-change relationship (FR-PLN-002): a directed contribution between two nodes with
    # its rationale, evidence strength, the assumptions it rests on and optional external context.
    schemas["FrameworkRelationship"] = closed(
        {
            "relationship_id": UUID,
            "from_node_id": UUID,
            "to_node_id": UUID,
            "relationship_type": {"enum": RELATIONSHIP_TYPES},
            "rationale": text_field(2000),
            "evidence_strength": {"enum": EVIDENCE_STRENGTHS},
            "assumption_ids": {"type": "array", "items": UUID, "maxItems": 20, "uniqueItems": True},
            "external_context": {"type": ["string", "null"], "maxLength": 2000},
        },
        [
            "relationship_id",
            "from_node_id",
            "to_node_id",
            "relationship_type",
            "rationale",
            "evidence_strength",
        ],
    )
    # An assumption, risk or context record (FR-PLN-007) linked to nodes, with the expected condition,
    # evidence, owner, review date and status. Its status changes interpretation, never an actual.
    assumption = closed(
        {
            "assumption_id": UUID,
            "kind": {"enum": ASSUMPTION_KINDS},
            "node_ids": {"type": "array", "items": UUID, "maxItems": 50, "uniqueItems": True},
            "statement": text_field(2000),
            "expected_condition": {"type": ["string", "null"], "maxLength": 2000},
            "evidence": {"type": ["string", "null"], "maxLength": 2000},
            "owner_id": {"type": ["string", "null"], "format": "uuid"},
            "review_date": {"type": "string", "format": "date"},
            "status": {"enum": ASSUMPTION_STATUSES},
        },
        ["assumption_id", "kind", "node_ids", "statement", "review_date", "status"],
    )
    # Who last assessed an assumption's status, and when, is server-owned: stored revisions only.
    assessed = deepcopy(assumption)
    assessed["properties"].update(assessed_by=UUID, assessed_at=DATE)
    schemas["FrameworkAssumption"] = assessed
    exception = closed(
        {
            "object_id": UUID,
            "rule": {"enum": EXCEPTABLE_RULES},
            "reason": text_field(2000),
            "review_date": {"type": "string", "format": "date"},
        },
        ["object_id", "rule", "reason", "review_date"],
    )
    # Who recorded an exception, and when, is server-owned: present only in stored revisions.
    recorded = deepcopy(exception)
    recorded["properties"].update(recorded_by=UUID, recorded_at=DATE)
    framework = {
        "programme_id": UUID,
        "version_label": text_field(64),
        "nodes": {"type": "array", "items": {"$ref": "#/components/schemas/FrameworkNode"}, "maxItems": 500},
        "relationships": {
            "type": "array",
            "items": {"$ref": "#/components/schemas/FrameworkRelationship"},
            "maxItems": 1000,
        },
        "assumptions": {"type": "array", "items": assumption, "maxItems": 500},
        "effective_from": DATE,
        "supersedes_revision": UUID,
        "exceptions": {"type": "array", "items": exception, "maxItems": 500},
    }
    schemas["FrameworkDraftData"] = closed(deepcopy(framework))
    framework["exceptions"] = {"type": "array", "items": recorded, "maxItems": 500}
    framework["assumptions"] = {
        "type": "array",
        "items": {"$ref": "#/components/schemas/FrameworkAssumption"},
        "maxItems": 500,
    }
    schemas["FrameworkData"] = closed(deepcopy(framework))

    # Targets, baselines and milestones for one indicator instance in one programme period. The
    # definition revision is pinned by submission (never accepted from a draft command); a blank
    # target keeps its value state and no value, never zero.
    # Status thresholds travel with the target version they qualify (FSD 32.2: thresholds are
    # visible and reviewed; they never conceal a missing, undefined, stale or unapproved state).
    thresholds = closed(
        {
            "scheme": {"enum": THRESHOLD_SCHEMES},
            "on_track": {"type": "string", "pattern": DECIMAL},
            "at_risk": {"type": "string", "pattern": DECIMAL},
        },
        ["scheme", "on_track", "at_risk"],
    )
    schemas["StatusThresholds"] = thresholds
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
        "status_thresholds": {"oneOf": [{"type": "null"}, thresholds]},
    }
    # A stated non-PRESENT value state carries no value or bounds; a patch that changes only the
    # value is merged first and the merged record is checked by the service (and the database).
    blank = {
        "if": {"properties": {"value_state": {"not": {"const": "PRESENT"}}}, "required": ["value_state"]},
        "then": {
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
            "exception": {"oneOf": [{"type": "null"}, recorded]},
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
            "status_thresholds": {"oneOf": [{"type": "null"}, thresholds]},
        },
        ["target_id", "revision_id", "target_kind", "target_basis", "direction", "value_state"],
    )
    progress = closed(
        {
            "status": text_field(64),
            "attainment_percent": {"type": ["string", "null"]},
            "deviation": NULLABLE_DECIMAL,
            "displayed_deviation": {"type": ["string", "null"]},
            "change_from_baseline": NULLABLE_DECIMAL,
            "change_from_baseline_percent": {"type": ["string", "null"]},
            "change_from_baseline_reason": {"type": ["string", "null"]},
            "reason_code": {"type": ["string", "null"]},
            # The performance band from the target's thresholds; null, with a reason, whenever a
            # separately visible state (no actual, no target, undefined, stale, milestone) comes first.
            "band": {"oneOf": [{"type": "null"}, {"enum": BANDS}]},
            "band_reason": {"type": ["string", "null"]},
        },
        ["status", "attainment_percent", "deviation", "reason_code"],
    )
    flag = closed(
        {
            "assumption_id": UUID,
            "kind": {"enum": ASSUMPTION_KINDS},
            "status": {"enum": ASSUMPTION_STATUSES},
            "statement": text_field(2000),
        },
        ["assumption_id", "kind", "status", "statement"],
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
                    "source": {"enum": ["PROGRAMME_SNAPSHOT", "CALCULATION", "NONE"]},
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
            "progress": progress,
            # FR-IND-004: a target approved after the period closed is shown beside the comparison
            # the close pinned, distinctly labelled; it never replaces the official comparison.
            "amended_target": {"oneOf": [{"type": "null"}, target_view]},
            "amended_progress": {"oneOf": [{"type": "null"}, progress]},
            "amended_after_close": {"type": "boolean"},
            # FR-PLN-007: assumptions linked to the nodes placing this indicator that are at risk or
            # invalid, so the affected planning view is highlighted.
            "assumption_flags": {"type": "array", "items": flag, "maxItems": 500},
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
            "amended_target",
            "amended_progress",
            "amended_after_close",
            "assumption_flags",
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
                            "relationships": {
                                "type": "array",
                                "items": {"$ref": "#/components/schemas/FrameworkRelationship"},
                            },
                            "assumptions": {
                                "type": "array",
                                "items": {"$ref": "#/components/schemas/FrameworkAssumption"},
                            },
                        },
                        ["framework_id", "revision_id", "baseline_version", "effective_from", "nodes"],
                    ),
                ]
            },
            # One page of at most 100 indicators with at most 100 periods each.
            "rows": {"type": "array", "maxItems": 10000, "items": row},
            "next_cursor": {"type": ["string", "null"], "maxLength": 4096},
        },
        ["programme_id", "framework", "rows", "next_cursor"],
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
        if base == "programmes":
            entry["parameters"] = [
                {
                    "name": "limit",
                    "in": "query",
                    "schema": {"type": "integer", "minimum": 1, "maximum": 100, "default": 50},
                },
                {"name": "cursor", "in": "query", "schema": {"type": "string", "maxLength": 4096}},
                {"name": "period_id", "in": "query", "schema": UUID},
            ]
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

    # The framework baseline governing a closed period, pinned at close when one exists.
    schemas["PolicyContext"]["properties"]["framework_revision"] = UUID
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
    # FR-IND-004: a target amendment's review compares the original, the currently effective
    # (`superseded`) and the proposed values, and says whether the period is already closed.
    candidate["original"] = {"$ref": "#/components/schemas/Target"}
    candidate["amendment"] = closed(
        {
            "period_state": {"enum": ["Open", "Locked", "RestatementOpen"]},
            "prospective_only": {"type": "boolean"},
        },
        ["period_state", "prospective_only"],
    )
    spec["info"]["version"] = policy["version"] = VERSION
