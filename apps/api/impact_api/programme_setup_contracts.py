"""Explicit, reviewable defaults for template-based programme setup."""

from copy import deepcopy
from .measurement_contracts import closed

VERSION = "1.58.0"


def augment(spec, policy):
    del policy
    schemas = spec["components"]["schemas"]
    setup = closed(
        {
            "unit": {"enum": ["COUNT", "DECIMAL", "PERCENTAGE"]},
            "period_basis": {"const": "REPORTING_CALENDAR"},
            "aggregation_method": {"const": "SUM"},
            "consent": {"const": "EXPLICIT"},
            "audience": {"enum": ["INTERNAL", "NAMED_RECIPIENTS"]},
            "unique_reach": {"const": False},
            "sharing": {"const": "NONE"},
        },
        ["unit", "period_basis", "aggregation_method", "consent", "audience", "unique_reach", "sharing"],
    )
    for name in ("ProgrammeData", "ProgrammeDraftData"):
        schema = schemas[name]
        schema["properties"].update(
            template_code={"enum": ["SIMPLE"]},
            setup_defaults=deepcopy(setup),
        )
        schema.setdefault("allOf", []).append(
            {
                "if": {"required": ["template_code"]},
                "then": {"required": ["reporting_calendar_id", "setup_defaults"]},
            }
        )
    for name in ("ProgrammeCreate", "ProgrammePatch", "Programme"):
        # Mark the evolved representation without replacing the existing operation surface.
        schemas[name]["description"] = (
            (schemas[name].get("description", "") + " ").strip()
            + "SIMPLE template records carry every calculation, consent and audience default explicitly; no unique-reach or sharing default is inferred."
        ).strip()
