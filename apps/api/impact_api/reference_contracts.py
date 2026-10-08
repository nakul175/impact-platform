"""Closed tenant-administration commands for a tenant's reference data (v0.26a, gap A1).

A tenant onboarded through the control plane starts without a reporting calendar, periods, a
review (workflow) template, a report template or a geography, and nothing else creates them. These
commands follow the tenant-administration pattern (administration_contracts.augment): capability
`reference-data.manage`, a TENANT-scope purpose-less grant, authentication within 300 seconds, a
stated reason, an audit event, an outbox event and an operation receipt in one transaction.

`reference-defaults` applies one documented, deterministic standard set (DEFAULTS below) through the
same governed path; it is refused once applied. The control plane never writes these records: its
role stays inside the object-type lists of migrations 0013/0014 (CLAUDE.md rule 20).
"""

UUID = {"type": "string", "format": "uuid"}
REASON = {"type": "string", "minLength": 1, "maxLength": 2000}
TITLE = {"type": "string", "minLength": 1, "maxLength": 120, "pattern": "\\S"}
CODE = {"type": "string", "minLength": 1, "maxLength": 32, "pattern": "^[A-Za-z0-9][A-Za-z0-9._-]*$"}
FREQUENCIES = ["MONTHLY", "QUARTERLY", "ANNUAL"]
SECTION = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "section_code": {"type": "string", "minLength": 1, "maxLength": 64, "pattern": "^[a-z0-9_]+$"},
        "heading": {"type": "string", "minLength": 1, "maxLength": 200},
        "required": {"type": "boolean"},
        "narrative_limit": {"type": "integer", "minimum": 100, "maximum": 20000},
    },
    "required": ["section_code", "heading", "required", "narrative_limit"],
}
CAPABILITY = "reference-data.manage"
COMMANDS = {
    ("reporting-calendars", None): (
        "create_reporting_calendar",
        CAPABILITY,
        "CreateReportingCalendar",
        False,
        {
            "title": TITLE,
            "frequency": {"enum": FREQUENCIES},
            "zone": {"type": "string", "minLength": 1, "maxLength": 80},
            "first_year": {"type": "integer", "minimum": 2000, "maximum": 2100},
            "years": {"type": "integer", "minimum": 1, "maximum": 5},
            "reason": REASON,
        },
    ),
    ("reporting-calendars", "extend"): (
        "extend_reporting_calendar",
        CAPABILITY,
        "ExtendReportingCalendar",
        True,
        {"years": {"type": "integer", "minimum": 1, "maximum": 5}, "reason": REASON},
    ),
    ("workflow-templates", None): (
        "create_workflow_template",
        CAPABILITY,
        "CreateWorkflowTemplate",
        False,
        {"title": TITLE, "reason": REASON},
    ),
    ("report-templates", None): (
        "create_report_template",
        CAPABILITY,
        "CreateReportTemplate",
        False,
        {
            "title": TITLE,
            "language": {"type": "string", "pattern": "^[a-z]{2,3}(-[A-Z]{2})?$"},
            "sections": {"type": "array", "items": SECTION, "minItems": 1, "maxItems": 20},
            "reason": REASON,
        },
    ),
    ("geographies", None): (
        "create_geography",
        CAPABILITY,
        "CreateGeography",
        False,
        {"title": TITLE, "code": CODE, "reason": REASON},
    ),
    ("reference-defaults", None): (
        "apply_reference_defaults",
        CAPABILITY,
        "ApplyReferenceDefaults",
        False,
        {"reason": REASON},
    ),
}

# The standard set (documented in docs/RELEASE-0.26a.md and DEPLOYMENT-GUIDE.md §4). The calendar is
# quarterly in the tenant's reporting zone and covers the current and the next calendar year of that
# zone at the moment it is applied; everything else is fixed.
DEFAULTS = {
    "calendar": {"title": "Standard quarterly calendar", "frequency": "QUARTERLY", "years": 2},
    "workflow_template": {"title": "Standard independent review"},
    "report_template": {
        "title": "Standard results report",
        "language": "en",
        "sections": [
            {"section_code": "summary", "heading": "Summary", "required": True, "narrative_limit": 4000},
            {"section_code": "results", "heading": "Results", "required": True, "narrative_limit": 8000},
            {
                "section_code": "caveats",
                "heading": "Data quality and caveats",
                "required": False,
                "narrative_limit": 4000,
            },
        ],
    },
    "geography": {"title": "Organisation-wide", "code": "ORG"},
}
