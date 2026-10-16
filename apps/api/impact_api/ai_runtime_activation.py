"""Server-owned local activation; tenant approval and safety checks remain mandatory."""

REVIEWABLE_USE_CASES = (
    "INDICATOR_DESIGN",
    "IMPORT_CLEANING",
    "EVIDENCE_QUESTION",
    "NUMERIC_ANALYSIS",
    "QUALITATIVE_ASSISTANCE",
    "PROACTIVE_FINDINGS",
    "ACTION_PROPOSAL",
)


def reviewed_use_cases(value, environment):
    if not isinstance(value, str):
        raise ValueError("ai_reviewed_use_cases must be a comma-separated string")
    if not value:
        return ()
    cases = tuple(item.strip() for item in value.split(","))
    if environment not in {"development", "test"}:
        raise ValueError("Reviewed local AI activation is forbidden outside development/test")
    if len(set(cases)) != len(cases) or any(case not in REVIEWABLE_USE_CASES for case in cases):
        raise ValueError("Reviewed AI activation must name distinct implemented use cases")
    return tuple(case for case in REVIEWABLE_USE_CASES if case in cases)


def activated(service):
    settings = getattr(service, "s", None)
    return getattr(settings, "reviewed_ai_use_cases", ())
