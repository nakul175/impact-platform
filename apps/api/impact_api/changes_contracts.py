"""Contracts for independently reviewed amendments to approved measurement data."""

from copy import deepcopy
import json
from .measurement_contracts import closed, text_field, UUID


def augment(spec, policy):
    schemas, paths = spec["components"]["schemas"], spec["paths"]
    prefix = "/v1/tenants/{tenant_id}/"
    observation = schemas["ObservationDraftData"]["properties"]
    variants = []
    for kind, fields in [
        (
            "Observation",
            {
                k: deepcopy(observation[k])
                for k in ["value_state", "value", "numerator", "denominator", "source_version"]
            },
        ),
        (
            "CollectionPlan",
            {k: deepcopy(schemas["CollectionPlanData"]["properties"][k]) for k in ["title", "obligations"]},
        ),
        ("IndicatorInstance", {"collector_id": UUID, "reviewer_id": UUID}),
    ]:
        proposed = closed(fields)
        proposed["minProperties"] = 1
        variants.append(
            closed(
                {
                    "target_kind": {"const": kind},
                    "target_id": UUID,
                    "target_revision": UUID,
                    "reason": text_field(2000),
                    "proposed_data": proposed,
                },
                ["target_kind", "target_id", "target_revision", "reason", "proposed_data"],
            )
        )
    schemas["MeasurementChangeData"] = {"oneOf": variants}
    schemas["MeasurementChangeDraftData"] = deepcopy(schemas["MeasurementChangeData"])
    for suffix in ["", "List", "Create", "Patch"]:
        schemas["MeasurementChange" + suffix] = json.loads(
            json.dumps(schemas["Programme" + suffix]).replace("Programme", "MeasurementChange")
        )
    for suffix, methods in [
        ("", ["get", "post"]),
        ("/{object_id}", ["get", "patch"]),
        ("/{object_id}/actions/submit", ["post"]),
    ]:
        template_route = "collection-plans" if "actions" in suffix else "programmes"
        template = paths[prefix + template_route + suffix]
        path = prefix + "measurement-changes" + suffix
        paths[path] = {"parameters": deepcopy(template["parameters"])}
        for method in methods:
            entry = json.loads(json.dumps(template[method]).replace("Programme", "MeasurementChange"))
            verb = (
                "submit"
                if "actions" in suffix
                else ("get" if suffix else "list")
                if method == "get"
                else ("patch" if suffix else "create")
            )
            op = "action_measurement_changes_submit" if verb == "submit" else verb + "_measurement_changes"
            cap = (
                "measurement-changes."
                + {
                    "list": "read",
                    "get": "read",
                    "patch": "draft.edit",
                    "create": "draft.create",
                    "submit": "submit",
                }[verb]
            )
            entry.update(operationId=op, summary=op.replace("_", " "), **{"x-capability": cap})
            paths[path][method] = entry
            policy["operations"].append(
                {
                    "operation_id": op,
                    "method": method.upper(),
                    "path": path,
                    "capability": cap,
                    "role_templates": ["AUTHOR", "REVIEWER", "MEL_ADMIN", "PROGRAMME_MANAGER"]
                    if method == "get"
                    else ["AUTHOR", "MEL_ADMIN", "PROGRAMME_MANAGER"],
                    "purpose_required": False,
                    "fresh_assurance_seconds": None,
                    "audit": method != "get",
                }
            )
    candidate = schemas["ReviewCandidate"]["properties"]
    candidate["kind"]["enum"].append("MeasurementChange")
    candidate["record"]["oneOf"].append({"$ref": "#/components/schemas/MeasurementChange"})
    candidate["current_target"] = {
        "oneOf": [
            {"$ref": "#/components/schemas/" + kind}
            for kind in ["Observation", "CollectionPlan", "IndicatorInstance"]
        ]
    }
    spec["info"]["version"] = policy["version"] = "1.5.0"
