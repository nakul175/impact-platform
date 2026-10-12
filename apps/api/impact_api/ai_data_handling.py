"""Server-owned data-handling plan applied before advisory content leaves the platform."""

import re

from .domain import DomainError

PURPOSE = "AI_ADOPTION_ADVISORY"
PROFILE_VERSION = "advisory-minimisation-2026-10-13.1"
DESTINATIONS = {
    "openai-us": {
        "version": "openai-us-responses-no-store-2026-10-13.1",
        "region": "United States",
        "provider_retention": "NO_STORE",
        "training_reuse_opt_in": False,
        "fallback_destination": None,
    }
}

_EMAIL = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
_PHONE = re.compile(r"(?<!\w)(?:\+?\d[\d ()-]{7,}\d)(?!\w)")
_SECRET = re.compile(
    r"(?i)\b(?:api[_ -]?key|access[_ -]?token|password|secret)\s*[:=]\s*\S+"
)


def _goal(value):
    categories = []
    for category, pattern in (("EMAIL", _EMAIL), ("PHONE", _PHONE), ("CREDENTIAL", _SECRET)):
        value, count = pattern.subn("[REDACTED]", value)
        if count:
            categories.append(category)
    return value, categories


def prepare(profile, destination, purpose):
    """Return minimized provider data plus non-content handling metadata."""
    details = DESTINATIONS.get(destination)
    if details is None or purpose != PURPOSE:
        raise DomainError("VALIDATION_FAILED", 422, reason="AI_DATA_HANDLING_BLOCKED")
    goal, redactions = _goal(profile["goal"])
    size = profile["team_size"]
    representative_size = 2 if size < 5 else 10 if size < 15 else 15
    minimized = {
        "sector": profile["sector"],
        "team_size": representative_size,
        "goal": goal,
        "data_readiness": profile["data_readiness"],
        "ai_experience": profile["ai_experience"],
        "sensitive_data": profile["sensitive_data"],
    }
    handling = {
        "purpose": PURPOSE,
        "destination": destination,
        "destination_version": details["version"],
        "region": details["region"],
        "provider_retention": details["provider_retention"],
        "training_reuse_opt_in": False,
        "fallback_destination": None,
        "minimisation_profile_version": PROFILE_VERSION,
        "transmitted_fields": sorted(minimized),
        "excluded_fields": ["exact_team_size"],
        "redaction_categories": redactions,
        "evaluation_dataset_eligible": False,
    }
    return minimized, handling
