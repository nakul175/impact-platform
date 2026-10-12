"""Deterministic, source-backed opportunity mappings for completed diagnosis revisions."""

from copy import deepcopy
import re

from .domain import DomainError

PATTERN_EDITION = "imprana-patterns-2026-10-12.1"
MAPPING_RULE_VERSION = "keyword-intersection-v1"

# Each example is reported by the named organisation at its pinned public URL. Examples provide
# context only; they do not predict results for another organisation.
_PATTERNS = (
    {
        "pattern_id": "public-information-assistant",
        "kind": "AI_ASSISTED",
        "title": "Answer recurring public-information questions",
        "description": "Use reviewed source material to help people find consistent public information.",
        "match_terms": ("communication", "information", "question", "support", "health", "awareness"),
        "real_world_examples": (
            {
                "example_id": "unicef-ureport-covid19",
                "organisation": "UNICEF",
                "title": "U-Report COVID-19 information chatbot",
                "source_url": "https://www.unicef.org/innovation/ureportCOVID19",
                "checked_on": "2026-10-12",
                "summary": "UNICEF reports using a localized information chatbot for risk communication and community engagement.",
            },
        ),
    },
    {
        "pattern_id": "learning-support",
        "kind": "AI_ASSISTED",
        "title": "Support learning with bounded, reviewed assistance",
        "description": "Pair an AI learning aid with educators, defined content and evaluation.",
        "match_terms": ("education", "learning", "student", "teacher", "training", "curriculum", "skill"),
        "real_world_examples": (
            {
                "example_id": "world-bank-nigeria-learning-pilot",
                "organisation": "World Bank",
                "title": "Generative AI after-school learning pilot in Edo, Nigeria",
                "source_url": "https://blogs.worldbank.org/en/education/From-chalkboards-to-chatbots-Transforming-learning-in-Nigeria",
                "checked_on": "2026-10-12",
                "summary": "The World Bank describes a supervised after-school programme using generative AI to support learning.",
            },
        ),
    },
    {
        "pattern_id": "record-quality-review",
        "kind": "AI_ASSISTED",
        "title": "Review records for likely duplicates or anomalies",
        "description": "Flag records for trained staff to review while retaining privacy controls and human decisions.",
        "match_terms": ("data", "record", "duplicate", "quality", "registration", "beneficiary", "database"),
        "real_world_examples": (
            {
                "example_id": "wfp-enterprise-deduplication",
                "organisation": "World Food Programme",
                "title": "Enterprise Deduplication Solution",
                "source_url": "https://www.wfp.org/stories/every-meal-counts-how-wfp-using-ai-reach-more-people-faster",
                "checked_on": "2026-10-12",
                "summary": "WFP reports using its Enterprise Deduplication Solution to help staff identify duplicate assistance records.",
            },
        ),
    },
    {
        "pattern_id": "rapid-image-assessment",
        "kind": "AI_ASSISTED",
        "title": "Accelerate review of imagery for emergency assessment",
        "description": "Use machine-assisted image review to prioritize expert assessment after an emergency.",
        "match_terms": ("image", "damage", "disaster", "emergency", "climate", "environment", "assessment"),
        "real_world_examples": (
            {
                "example_id": "wfp-deep-emergency-imagery",
                "organisation": "World Food Programme",
                "title": "Digital Engine for Emergency Photo-analysis",
                "source_url": "https://www.wfp.org/stories/does-artificial-intelligence-hold-key-ending-hunger",
                "checked_on": "2026-10-12",
                "summary": "WFP describes machine-assisted analysis of drone imagery used during humanitarian emergencies.",
            },
        ),
    },
    {
        "pattern_id": "review-and-localize-information",
        "kind": "PROCESS_FIX",
        "title": "Create a reviewed, localized information routine",
        "description": "Assign content owners, localize approved answers and schedule review without requiring a new technology purchase.",
        "match_terms": ("communication", "information", "question", "support", "health", "awareness"),
        "real_world_examples": (
            {
                "example_id": "unicef-ureport-content-localization",
                "organisation": "UNICEF",
                "title": "U-Report COVID-19 content localization",
                "source_url": "https://www.unicef.org/innovation/ureportCOVID19",
                "checked_on": "2026-10-12",
                "summary": "UNICEF describes content and navigation review plus localization for specific contexts and groups; the reusable process is independent of buying a new tool.",
            },
        ),
    },
    {
        "pattern_id": "staff-practice-and-review",
        "kind": "PROCESS_FIX",
        "title": "Build staff practice and human review into the workflow",
        "description": "Use short practice, explicit review responsibilities and feedback before considering additional technology.",
        "match_terms": ("education", "learning", "student", "teacher", "training", "curriculum", "skill"),
        "real_world_examples": (
            {
                "example_id": "world-bank-peru-practice-support",
                "organisation": "World Bank",
                "title": "Practice-oriented teacher and principal support in Peru",
                "source_url": "https://www.worldbank.org/en/results/2026/07/02/artificial-intelligence-in-action-in-latin-america-s-schools-evidence-from-peru",
                "checked_on": "2026-10-12",
                "summary": "The World Bank reports that practical training and ongoing human support accompanied adoption, and warns that technology alone rarely changes outcomes.",
            },
        ),
    },
)


def pattern_library():
    return {"edition": PATTERN_EDITION, "patterns": deepcopy(list(_PATTERNS))}


def _validate_library():
    seen = set()
    for pattern in _PATTERNS:
        if pattern["pattern_id"] in seen or pattern["kind"] not in {
            "AI_ASSISTED",
            "TECHNOLOGY",
            "PROCESS_FIX",
        }:
            raise DomainError("SERVICE_UNAVAILABLE", 503, reason="PATTERN_LIBRARY_INVALID")
        seen.add(pattern["pattern_id"])
        examples = pattern.get("real_world_examples")
        if not examples or any(
            set(example) != {"example_id", "organisation", "title", "source_url", "checked_on", "summary"}
            or not example["source_url"].startswith("https://")
            or not all(isinstance(value, str) and value.strip() for value in example.values())
            for example in examples
        ):
            raise DomainError("SERVICE_UNAVAILABLE", 503, reason="PATTERN_LIBRARY_INVALID")


def _rationale(problem, pattern, basis):
    description = problem["description"].strip()
    area = problem["affected_area"].strip()
    if not description or not area or not basis:
        raise DomainError("SERVICE_UNAVAILABLE", 503, reason="OPPORTUNITY_RATIONALE_INVALID")
    return {
        "plain_language": (
            f"This pattern is suggested because the priority problem in {area} uses "
            f"the matching terms {', '.join(basis)}. Review the linked problem inputs and "
            "source example before deciding whether it fits."
        ),
        "diagnosis_input_links": [
            {"problem_id": problem["problem_id"], "field": "description"},
            {"problem_id": problem["problem_id"], "field": "affected_area"},
        ],
    }


def map_diagnosis(diagnosis):
    """Return an edition-pinned map; never invent a generic match to force completion."""
    _validate_library()
    if diagnosis["business_state"] != "Completed":
        raise DomainError("STATE_TRANSITION_DENIED", 409, reason="DIAGNOSIS_NOT_COMPLETE")
    data = diagnosis["data"]
    by_id = {problem["problem_id"]: problem for problem in data["problems"]}
    results, unmapped = [], []
    for problem_id in data["priority_order"]:
        problem = by_id.get(problem_id)
        if not problem:
            raise DomainError("SERVICE_UNAVAILABLE", 503, reason="DIAGNOSIS_PRIORITY_INVALID")
        tokens = set(re.findall(r"[a-z]+", (problem["description"] + " " + problem["affected_area"]).lower()))
        matches = []
        for pattern in _PATTERNS:
            basis = sorted(tokens.intersection(pattern["match_terms"]))
            if basis:
                item = deepcopy(pattern)
                item.pop("match_terms")
                item["real_world_examples"] = list(item["real_world_examples"])
                item["match_basis"] = basis
                item["rationale"] = _rationale(problem, pattern, basis)
                matches.append(item)
        matches.sort(key=lambda item: (-len(item["match_basis"]), item["pattern_id"]))
        if not matches:
            unmapped.append(problem_id)
        results.append({"problem_id": problem_id, "opportunities": matches})
    return {
        "diagnosis_id": diagnosis["object_id"],
        "diagnosis_revision": diagnosis["revision_id"],
        "pattern_edition": PATTERN_EDITION,
        "mapping_rule_version": MAPPING_RULE_VERSION,
        "mapping_state": "COMPLETE" if not unmapped and results else "INCOMPLETE",
        "problems": results,
        "unmapped_problem_ids": unmapped,
        "disclaimer": "Examples are source-linked context, not endorsement, predicted results, procurement approval or deployment authority.",
    }


class AIOpportunityMapping:
    def __init__(self, diagnoses):
        self.diagnoses = diagnoses

    def get(self, identity, tenant, diagnosis_id, revision_id=None):
        return map_diagnosis(self.diagnoses.get(identity, tenant, diagnosis_id, revision_id))
