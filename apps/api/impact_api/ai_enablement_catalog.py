"""Versioned editorial examples and transparent rules; no provider calls or official results."""

from copy import deepcopy
import re

SCHEMA_VERSION = "1.0"
CONTENT_VERSION = "nonprofit-2026-10-05.1"
SECTORS = {"GENERAL", "EDUCATION", "HEALTH", "LIVELIHOODS", "ENVIRONMENT"}
PROFILE_FIELDS = {"sector", "team_size", "goal", "data_readiness", "ai_experience", "sensitive_data"}


def _use_case(id, title, sectors, description, data, sensitivity, keywords, checks):
    return {
        "id": id,
        "title": title,
        "sectors": sectors,
        "description": description,
        "kind": "NON_AI" if id == "data_foundation" else "AI_ASSISTED",
        "data_requirement": data,
        "sensitivity": sensitivity,
        "goal_keywords": keywords,
        "prerequisites": ["Name a responsible owner and reviewer", "Define a small test and stop rule"],
        "acceptance_checks": checks,
        "human_approval_needs": ["Responsible staff approve every externally used output"],
        "content_status": "EDITORIAL_EXAMPLE",
    }


_USE_CASES = [
    _use_case(
        "data_foundation",
        "Organise a shared programme data register",
        ["GENERAL"],
        "Agree definitions, record ownership and a repeatable quality review before automation.",
        "NONE",
        "LOW",
        ["data", "quality", "record", "collection"],
        ["Check missing values and duplicate records", "Reconcile samples with approved sources"],
    ),
    _use_case(
        "communications",
        "Draft communications from approved public material",
        ["GENERAL"],
        "Create draft newsletters and donor updates without uploading beneficiary information.",
        "NONE",
        "LOW",
        ["communication", "newsletter", "donor", "fundraising", "grant"],
        ["Verify every claim and citation", "Obtain consent for stories and images"],
    ),
    _use_case(
        "knowledge_search",
        "Search an approved internal knowledge collection",
        ["GENERAL"],
        "Pilot source-linked answers over a deliberately selected document collection.",
        "BASIC",
        "MEDIUM",
        ["knowledge", "search", "policy", "document"],
        ["Answers link to supporting passages", "Test refusal for missing evidence and restricted documents"],
    ),
    _use_case(
        "learning_material",
        "Draft accessible learning material",
        ["EDUCATION"],
        "Help educators draft activities and plain-language explanations from approved curriculum.",
        "BASIC",
        "MEDIUM",
        ["education", "learning", "training", "curriculum"],
        [
            "Educators verify accuracy and age appropriateness",
            "Test accessibility and language with intended users",
        ],
    ),
    _use_case(
        "health_communications",
        "Draft public health information for expert review",
        ["HEALTH"],
        "Draft explanations from organisation-approved sources; exclude clinical diagnosis and triage.",
        "BASIC",
        "HIGH",
        ["health", "awareness", "information"],
        [
            "Qualified reviewer approves every health claim",
            "No patient data, diagnosis or treatment decisions",
        ],
    ),
    _use_case(
        "livelihood_resources",
        "Draft livelihood training resources",
        ["LIVELIHOODS"],
        "Help trainers organise existing vocational resources into draft activities.",
        "BASIC",
        "MEDIUM",
        ["livelihood", "skill", "employment", "training"],
        ["Trainers verify local relevance", "No automated eligibility or job allocation"],
    ),
    _use_case(
        "environment_briefs",
        "Draft environmental project evidence briefs",
        ["ENVIRONMENT"],
        "Summarise approved documents into source-linked draft project briefs.",
        "BASIC",
        "MEDIUM",
        ["environment", "climate", "conservation", "brief"],
        [
            "Verify source context and uncertainty",
            "Exclude sensitive location data unless explicitly approved",
        ],
    ),
    _use_case(
        "mel_narratives",
        "Draft narratives around approved impact results",
        ["GENERAL"],
        "Explain already approved results while preserving their source, period and limitations.",
        "STRUCTURED",
        "MEDIUM",
        ["impact", "report", "monitoring", "evaluation", "result"],
        [
            "Numbers match approved deterministic results",
            "No AI-generated official arithmetic or causal claims",
        ],
    ),
]

_LEARNING_PATHS = [
    {
        "id": "foundations",
        "title": "AI foundations for nonprofit teams",
        "steps": [
            "Practise with synthetic or approved public examples",
            "Check factual claims and sources",
            "Learn when to use a checklist or spreadsheet instead",
            "Document allowed and prohibited data",
        ],
    },
    {
        "id": "pilot_design",
        "title": "Design and evaluate a bounded pilot",
        "steps": [
            "Pick one problem and accountable owner",
            "Measure the current process first",
            "Create representative test cases and refusal cases",
            "Agree human review and a stop rule",
        ],
    },
    {
        "id": "procurement",
        "title": "Compare and procure responsibly",
        "steps": [
            "Write requirements and acceptance tests",
            "Request comparable written offers",
            "Review recurring and exit costs",
            "Review data terms and support responsibilities",
        ],
    },
]

_CRITERIA = [
    (
        "fitness",
        "Fit and evidence",
        ["Can the provider demonstrate our acceptance tests?", "What fails and how is it detected?"],
    ),
    (
        "data",
        "Data handling",
        [
            "What data leaves our environment?",
            "Who can access it, train on it or retain it?",
            "How are deletion and export verified?",
        ],
    ),
    (
        "cost",
        "Total cost",
        [
            "What are setup, usage, review, support and exit costs?",
            "What spending controls and alerts are available?",
        ],
    ),
    (
        "inclusion",
        "Accessibility and language",
        [
            "Can intended users operate it in their languages?",
            "Does it work with our accessibility and connectivity needs?",
        ],
    ),
    (
        "delivery",
        "Delivery and support",
        ["Who owns integration and incidents?", "Which milestones require our acceptance before payment?"],
    ),
    (
        "exit",
        "Ownership and exit",
        [
            "Can we export data and configuration in usable formats?",
            "What happens if the service or provider closes?",
        ],
    ),
    (
        "governance",
        "Accountability",
        [
            "Who approves outputs and consequential decisions?",
            "How are conflicts of interest and provider claims reviewed?",
        ],
    ),
]


def catalog():
    """Return an isolated copy; callers cannot mutate later assessments."""
    return {
        "schema_version": SCHEMA_VERSION,
        "content_version": CONTENT_VERSION,
        "provenance": {
            "status": "EDITORIAL_ASSUMPTIONS",
            "validated_demand": False,
            "source_concept": "describe-diagnose-procure-deploy-run",
            "note": "Nonprofit examples need practitioner review; no factory study data or estimates reused.",
        },
        "journey": [
            {"id": id, "title": title, "purpose": purpose, "human_owner": owner}
            for id, title, purpose, owner in [
                ("describe", "Describe", "State the problem and constraints", "Programme lead"),
                (
                    "diagnose",
                    "Assess",
                    "Review opportunities and capacity gaps",
                    "Programme lead and data owner",
                ),
                (
                    "procure",
                    "Compare and procure",
                    "Compare written offers against acceptance tests",
                    "Procurement lead",
                ),
                ("deploy", "Pilot and deploy", "Accept milestones against agreed tests", "Delivery owner"),
                ("run", "Operate and learn", "Monitor failures, costs and outcomes", "Service owner"),
            ]
        ],
        "use_cases": deepcopy(_USE_CASES),
        "learning_paths": deepcopy(_LEARNING_PATHS),
        "procurement_criteria": [
            {"id": id, "title": title, "questions": list(questions)} for id, title, questions in _CRITERIA
        ],
        "marketplace_status": {
            "status": "NOT_CONNECTED",
            "vendors": [],
            "explanation": "No verified provider listings, live quotes, purchasing or endorsements are available.",
        },
    }


def validate_profile(profile):
    if not isinstance(profile, dict) or set(profile) != PROFILE_FIELDS:
        raise ValueError("Supply exactly the six assessment profile fields.")
    for field, options in [
        ("sector", SECTORS),
        ("data_readiness", {"NONE", "BASIC", "STRUCTURED"}),
        ("ai_experience", {"NONE", "EXPERIMENTING", "REGULAR"}),
    ]:
        if not isinstance(profile[field], str) or profile[field] not in options:
            raise ValueError(f"Invalid {field}.")
    if type(profile["team_size"]) is not int or not 1 <= profile["team_size"] <= 100000:
        raise ValueError("team_size must be an integer from 1 to 100000.")
    if (
        not isinstance(profile["goal"], str)
        or not 1 <= len(profile["goal"].strip()) <= 1000
        or len(profile["goal"]) > 1000
    ):
        raise ValueError("goal must contain 1 to 1000 characters.")
    if type(profile["sensitive_data"]) is not bool:
        raise ValueError("sensitive_data must be a boolean.")


def assess(profile):
    """Rank editorial examples without external calls, promises or data persistence.

    Sort by keyword relevance, then unmet prerequisites, then stable ID. Sector-only
    examples are included with an explicit applicability reason. Goal text is never
    interpreted as instructions or returned in generated content.
    """
    validate_profile(profile)
    gaps, approvals, reasons = (
        [],
        ["Organisation owner approves pilot scope, budget and responsible reviewer"],
        [],
    )
    if profile["data_readiness"] == "NONE":
        gaps.append("Agree data definitions, ownership and a basic quality routine")
        reasons.append("No organised data foundation was reported.")
    if profile["ai_experience"] == "NONE":
        gaps.append("Practise verification and safe prompting before live use")
        reasons.append("No prior AI use was reported.")
    if profile["team_size"] < 5:
        gaps.append("Reserve staff time and name a backup reviewer for a small team")
    if profile["sensitive_data"]:
        gaps.append("Complete a data-handling review before any real data enters an AI service")
        approvals.append("Data owner approves permitted data, access, retention and provider terms")
        reasons.append("Sensitive data was reported; a synthetic-data pilot needs review before live use.")
    stage = (
        "FOUNDATION"
        if profile["data_readiness"] == "NONE" or profile["ai_experience"] == "NONE"
        else "REVIEW_REQUIRED"
        if profile["sensitive_data"]
        else "PILOT_CANDIDATE"
    )
    if not reasons:
        reasons.append(
            "Reported experience and data organisation support considering a bounded pilot; capability is not verified."
        )
    words = set(re.findall(r"[a-z]+", profile["goal"].lower()))
    ranked = []
    levels = {"NONE": 0, "BASIC": 1, "STRUCTURED": 2}
    for case in _USE_CASES:
        if "GENERAL" not in case["sectors"] and profile["sector"] not in case["sectors"]:
            continue
        matched = sorted(words.intersection(case["goal_keywords"]))
        case_gaps = []
        if case["kind"] == "AI_ASSISTED" and profile["ai_experience"] == "NONE":
            case_gaps.append("Practise safe prompting and verification before this pilot.")
        if levels[profile["data_readiness"]] < levels[case["data_requirement"]]:
            case_gaps.append(f"This example needs {case['data_requirement'].lower()} data organisation.")
        case_approvals = list(case["human_approval_needs"])
        if profile["sensitive_data"] and case["kind"] == "AI_ASSISTED":
            case_approvals.append(
                "Data owner approves any real-data use; start with synthetic or approved public data"
            )
        if case["sensitivity"] == "HIGH":
            case_approvals.append("Qualified domain expert approves scope and every public output")
        why = (
            [f"Goal keywords matched: {', '.join(matched)}."]
            if matched
            else ["General nonprofit example; confirm relevance with the programme lead."]
        )
        if case["sectors"] != ["GENERAL"]:
            why.append(f"Matches the reported {profile['sector'].lower()} sector.")
        status = (
            "FOUNDATION_STEP"
            if case["kind"] == "NON_AI"
            else "PREREQUISITES_REQUIRED"
            if case_gaps
            else "REVIEW_REQUIRED"
            if profile["sensitive_data"] or case["sensitivity"] == "HIGH"
            else "PILOT_CANDIDATE"
        )
        ranked.append(
            (
                (-len(matched), len(case_gaps), case["id"]),
                {
                    "use_case_id": case["id"],
                    "priority": 0,
                    "status": status,
                    "reasons": why,
                    "capacity_gaps": case_gaps,
                    "human_approval_needs": case_approvals,
                },
            )
        )
    ranked.sort(key=lambda pair: pair[0])
    recommendations = [item for _, item in ranked]
    for priority, item in enumerate(recommendations, 1):
        item["priority"] = priority
    return {
        "schema_version": SCHEMA_VERSION,
        "content_version": CONTENT_VERSION,
        "method": "DETERMINISTIC_RULES",
        "readiness": {"stage": stage, "reasons": reasons},
        "recommendations": recommendations,
        "capacity_gaps": gaps,
        "learning_path_ids": (["foundations"] if profile["ai_experience"] == "NONE" else [])
        + ["pilot_design", "procurement"],
        "next_steps": [
            "Review these editorial examples with staff and intended users",
            "Choose one bounded problem and define acceptance tests",
            "Measure current time, quality and cost before a synthetic-data pilot",
            "Compare written offers only after agreeing requirements",
        ],
        "human_approval_needs": approvals,
        "limitations": [
            "Self-reported readiness is not verified capability or certification",
            "Goal matching uses English keywords only and can miss context",
            "No ROI, savings, vendor quality or price is estimated",
            "This plan does not authorise spending, deployment or sensitive-data disclosure",
            "No automatic beneficiary eligibility, clinical decisions or official impact arithmetic",
        ],
    }
