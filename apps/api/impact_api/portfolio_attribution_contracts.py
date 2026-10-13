"""FR-CAL-014 portfolio membership and approved allocation-view contracts."""

from copy import deepcopy
from .measurement_contracts import closed, text_field

VERSION = "1.64.0"
UUID = {"type": "string", "format": "uuid"}
SHARE = {"type": "string", "pattern": r"^(0|1|0\.[0-9]{1,12}|1\.0{1,12}|[1-9][0-9]*(\.[0-9]{1,12})?)$"}
ROOT = "portfolio-allocation-views"
PREVIEW = ROOT + "/{object_id}/preview"
IMPLEMENTED = [
    ("get", ROOT),
    ("post", ROOT),
    ("get", ROOT + "/{object_id}"),
    ("patch", ROOT + "/{object_id}"),
    ("post", ROOT + "/{object_id}/actions/submit"),
    ("post", PREVIEW),
]


def _replace(value, old, new):
    if isinstance(value, dict):
        return {k: _replace(v, old, new) for k, v in value.items()}
    if isinstance(value, list):
        return [_replace(v, old, new) for v in value]
    return value.replace(old, new) if isinstance(value, str) else value


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    portfolio = closed(
        {
            "portfolio_id": deepcopy(UUID),
            "title": text_field(200),
            "project_ids": {
                "type": "array",
                "minItems": 1,
                "maxItems": 1000,
                "uniqueItems": True,
                "items": deepcopy(UUID),
            },
        },
        ["portfolio_id", "title", "project_ids"],
    )
    allocation = closed(
        {
            "portfolio_id": deepcopy(UUID),
            "project_id": deepcopy(UUID),
            "result_revision": deepcopy(UUID),
            "share": SHARE,
            "basis": text_field(1000),
        },
        ["portfolio_id", "project_id", "result_revision", "share", "basis"],
    )
    data = closed(
        {
            "title": text_field(200),
            "portfolios": {"type": "array", "minItems": 1, "maxItems": 100, "items": portfolio},
            "allocations": {"type": "array", "maxItems": 5000, "items": allocation},
            "remainder_policy": {
                "enum": [
                    "UNALLOCATED_REMAINDER",
                    "RETURN_TO_SOURCE",
                    "NOT_APPLICABLE_NONADDITIVE",
                ]
            },
            "nonadditive": {"type": "boolean"},
            "nonadditive_label": {"type": ["string", "null"], "maxLength": 500},
        },
        ["title", "portfolios", "allocations", "remainder_policy", "nonadditive", "nonadditive_label"],
    )
    schemas["PortfolioAllocationViewData"] = data
    schemas["PortfolioAllocationViewDraftData"] = deepcopy(data)
    for suffix in ("", "List", "Create", "Patch"):
        schemas["PortfolioAllocationView" + suffix] = _replace(
            deepcopy(schemas["IndicatorDefinition" + suffix]),
            "IndicatorDefinition",
            "PortfolioAllocationView",
        )
    schemas["PortfolioAttributionPreviewRequest"] = closed(
        {"view_revision": deepcopy(UUID)}, ["view_revision"]
    )
    schemas["PortfolioMembershipSummary"] = closed(
        {
            "portfolio_id": deepcopy(UUID),
            "title": text_field(200),
            "project_ids": {"type": "array", "maxItems": 1000, "uniqueItems": True, "items": deepcopy(UUID)},
            "project_count": {"type": "integer", "minimum": 0},
        },
        ["portfolio_id", "title", "project_ids", "project_count"],
    )
    schemas["PortfolioAllocationAmount"] = closed(
        {
            "portfolio_id": deepcopy(UUID),
            "project_id": deepcopy(UUID),
            "result_revision": deepcopy(UUID),
            "share": SHARE,
            "allocated_value": {"type": "string"},
            "basis": text_field(1000),
        },
        ["portfolio_id", "project_id", "result_revision", "share", "allocated_value", "basis"],
    )
    schemas["PortfolioAttributionPreview"] = closed(
        {
            "view_revision": deepcopy(UUID),
            "portfolios": {
                "type": "array",
                "maxItems": 100,
                "items": {"$ref": "#/components/schemas/PortfolioMembershipSummary"},
            },
            "organisation_unique_project_count": {"type": "integer", "minimum": 0},
            "allocations": {
                "type": "array",
                "maxItems": 5000,
                "items": {"$ref": "#/components/schemas/PortfolioAllocationAmount"},
            },
            "remainders": {
                "type": "object",
                "maxProperties": 5000,
                "propertyNames": deepcopy(UUID),
                "additionalProperties": {"type": "string"},
            },
            "nonadditive": {"type": "boolean"},
            "label": text_field(500),
            "causal_ownership": {"const": False},
        },
        [
            "view_revision",
            "portfolios",
            "organisation_unique_project_count",
            "allocations",
            "remainders",
            "nonadditive",
            "label",
            "causal_ownership",
        ],
    )
    prefix = "/v1/tenants/{tenant_id}/"
    for item in (False, True):
        suffix = "/{object_id}" if item else ""
        template = _replace(
            deepcopy(paths[prefix + "indicator-definitions" + suffix]),
            "IndicatorDefinition",
            "PortfolioAllocationView",
        )
        for method in ("get", "patch") if item else ("get", "post"):
            verb = (
                "get"
                if item and method == "get"
                else "list"
                if method == "get"
                else "patch"
                if item
                else "create"
            )
            template[method].update(
                operationId=verb + "_portfolio_allocation_views",
                **{"x-capability": "calculated-results.read", "x-contract-version": VERSION},
            )
        paths[prefix + ROOT + suffix] = template
    submit = _replace(
        deepcopy(paths[prefix + "indicator-definitions/{object_id}/actions/submit"]),
        "IndicatorDefinition",
        "PortfolioAllocationView",
    )
    submit["post"].update(
        operationId="submit_portfolio_allocation_view",
        **{"x-capability": "calculated-results.read", "x-contract-version": VERSION},
    )
    paths[prefix + ROOT + "/{object_id}/actions/submit"] = submit
    preview = deepcopy(paths[prefix + "recalculations"])
    preview["parameters"] = deepcopy(paths[prefix + "indicator-definitions/{object_id}"]["parameters"])
    op = preview["post"]
    op.update(
        operationId="preview_portfolio_attribution",
        summary="Preview visible portfolio membership and approved allocation",
        **{"x-capability": "calculated-results.read", "x-contract-version": VERSION},
    )
    op["requestBody"]["content"]["application/json"]["schema"] = {
        "$ref": "#/components/schemas/PortfolioAttributionPreviewRequest"
    }
    op["responses"].pop("202", None)
    op["responses"]["200"] = {
        "description": "Permission-filtered unique project and allocation view",
        "content": {
            "application/json": {"schema": {"$ref": "#/components/schemas/PortfolioAttributionPreview"}}
        },
    }
    paths[prefix + PREVIEW] = preview
    ids = (
        {paths[prefix + ROOT][m]["operationId"] for m in ("get", "post")}
        | {paths[prefix + ROOT + "/{object_id}"][m]["operationId"] for m in ("get", "patch")}
        | {"submit_portfolio_allocation_view", "preview_portfolio_attribution"}
    )
    policy["operations"] = [r for r in policy["operations"] if r["operation_id"] not in ids]
    for method, path in IMPLEMENTED:
        full = prefix + path
        policy["operations"].append(
            {
                "operation_id": paths[full][method]["operationId"],
                "method": method.upper(),
                "path": full,
                "capability": "calculated-results.read",
                "role_templates": ["MEL_ADMIN", "PROGRAMME_MANAGER", "ANALYST"],
                "purpose_required": False,
                "fresh_assurance_seconds": None,
                "audit": method != "get",
                "state_guard": "Current visible projects only; organisation count deduplicates project identity; approved shares disclose basis/remainder and never causal ownership.",
            }
        )
