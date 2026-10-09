"""Source-backed discovery content, with editorial use-case mappings and no vendor calls.

Every listing carries a commercial disclosure (US-DC-04): whether Imprana has a known commercial
relationship with the listing's provider. A listing without a valid disclosure fails closed: the
catalogue is not served (`solutions_catalog` raises) and no saved plan can archive it.
"""

from copy import deepcopy
from datetime import date

from jsonschema import Draft202012Validator, FormatChecker

# Edition .2 adds the commercial disclosures; the source facts were last checked on CHECKED_ON.
CONTENT_VERSION = "nonprofit-solutions-2026-10-05.2"
CHECKED_ON = "2026-10-05"
# The date Imprana editorial declared the disclosures of this edition (Sprint 1 default decision:
# disclosures are Imprana editorial content, reviewed by an advisor; no advisor has reviewed them yet).
DISCLOSURES_DECLARED_ON = "2026-10-09"
DISCLOSURE_STATUSES = ("NONE_KNOWN", "DISCLOSED")
# The closed set of relationship types a DISCLOSED listing names (at least one).
RELATIONSHIP_TYPES = ("referral_fee", "revenue_share", "reseller", "sponsorship", "ownership")
STATEMENT_MAX = 1000
CATEGORIES = frozenset(
    {
        "GENERAL_ASSISTANT",
        "WORKSPACE_ASSISTANT",
        "KNOWLEDGE_ASSISTANT",
        "TRANSLATION",
        "DESIGN",
        "DEVELOPER_PLATFORM",
    }
)

_DATA_QUESTIONS = [
    "Which exact plan and contract govern our uploads, prompts and generated content?",
    "How are training use, retention, deletion, subprocessors and processing regions handled?",
    "Who can access connected documents, and how are existing permissions enforced?",
    "Can we test with public or synthetic material before any approved sensitive-data pilot?",
]


class SolutionsCatalogInvalid(ValueError):
    """The published catalogue does not satisfy its contract; it must not be served or archived."""


def _none_known(provider):
    """Imprana editorial declaration that no commercial relationship with the provider is known.

    Never a claim that none exists: it records what Imprana editorial knows on the declaration date.
    """
    return {
        "status": "NONE_KNOWN",
        "relationship_types": [],
        "statement": (
            "Imprana editorial declaration, pending advisor review: no referral fee, revenue share, "
            "reseller, sponsorship or ownership relationship between Imprana and "
            + provider
            + " is known. The platform has no registered marketplace vendors."
        ),
        "declared_on": DISCLOSURES_DECLARED_ON,
    }


def _solution(
    id,
    name,
    provider,
    category,
    cases,
    description,
    deployment,
    commercial_model,
    nonprofit_offer,
    api_available,
    sources,
    notes,
    questions=(),
    disclosure=None,
):
    item = {
        "id": id,
        "name": name,
        "provider": provider,
        "category": category,
        "use_case_ids": list(cases),
        "description": description,
        "deployment": deployment,
        "commercial_model": commercial_model,
        "nonprofit_offer": nonprofit_offer,
        "api_available": api_available,
        "source_urls": [{"label": label, "url": url} for label, url in sources],
        "verification_notes": list(notes),
        "data_review_questions": [*_DATA_QUESTIONS, *questions],
    }
    # A listing given no disclosure stays without one, so validation refuses the whole catalogue.
    if disclosure is not None:
        item["commercial_disclosure"] = disclosure
    return item


_SOLUTIONS = [
    _solution(
        "chatgpt_business",
        "ChatGPT Business",
        "OpenAI",
        "GENERAL_ASSISTANT",
        ["communications", "knowledge_search", "learning_material", "mel_narratives"],
        "A shared team workspace for ChatGPT with member administration and organisational tools.",
        "Provider-hosted team workspace; review enabled apps and connectors separately.",
        "Paid workspace seats; API usage is billed separately. Your final price is not verified.",
        "OpenAI advertises up to 75% off Business or Enterprise for nonprofits. Your eligibility is not verified.",
        "Separate OpenAI API exists; a ChatGPT Business subscription does not include API usage.",
        [
            ("Business overview", "https://help.openai.com/en/articles/8792828-chatgpt-business-overview"),
            ("Nonprofit programme", "https://openai.com/index/introducing-openai-for-nonprofits/"),
        ],
        [
            "Use-case mappings are editorial pilot ideas, not measured fit or performance claims.",
            "The nonprofit article's February 2026 update supersedes its older discount figures.",
            "Confirm seat type, limits, local taxes and nonprofit approval before estimating cost.",
        ],
        disclosure=_none_known("OpenAI"),
    ),
    _solution(
        "claude_team",
        "Claude Team",
        "Anthropic",
        "GENERAL_ASSISTANT",
        ["communications", "knowledge_search", "learning_material", "environment_briefs", "mel_narratives"],
        "A team assistant with shared projects and organisational knowledge; connectors can link other services.",
        "Provider-hosted team service; each connector needs its own permissions and data review.",
        "Paid Team or Enterprise plans. Your final seat price and limits are not verified.",
        "Anthropic advertises up to 75% off Team and Enterprise for nonprofits. Your eligibility is not verified.",
        "API entitlement and price for this Team offer are not verified; confirm separately.",
        [
            ("Nonprofit announcement", "https://www.anthropic.com/news/claude-for-nonprofits"),
            ("Nonprofit programme", "https://claude.com/solutions/nonprofits"),
        ],
        [
            "The published nonprofit offer requires application and eligibility checks.",
            "A connector's presence does not establish authorisation to share donor or beneficiary data.",
            "Use-case mappings are editorial pilot ideas, not an endorsement or benchmark.",
        ],
        disclosure=_none_known("Anthropic"),
    ),
    _solution(
        "microsoft_365_copilot",
        "Microsoft 365 Copilot",
        "Microsoft",
        "WORKSPACE_ASSISTANT",
        ["communications", "knowledge_search", "learning_material", "mel_narratives"],
        "An assistant for work in Microsoft 365, including drafting and summaries of emails and meetings.",
        "Microsoft-hosted service within an organisation's Microsoft 365 environment.",
        "Requires a Microsoft 365 licence and a Copilot offer. Your combined licence price is not verified.",
        "Microsoft advertises a nonprofit Copilot discount. Your eligibility and regional offer are not verified.",
        "API access to these end-user features is not verified; evaluate integrations separately.",
        [
            (
                "Nonprofit offerings and licence prerequisite",
                "https://learn.microsoft.com/en-us/industry/nonprofit/microsoft-for-nonprofits/nonprofit-offerings-products",
            ),
            ("Nonprofit programme", "https://www.microsoft.com/en-us/nonprofits"),
        ],
        [
            "Copilot and Copilot Chat have different entitlements; confirm the exact product in a quote.",
            "Check existing document sharing before enabling knowledge access.",
            "Use-case mappings are editorial; spreadsheet assistance does not replace official calculations.",
        ],
        disclosure=_none_known("Microsoft"),
    ),
    _solution(
        "google_workspace_gemini",
        "Gemini for Google Workspace",
        "Google",
        "WORKSPACE_ASSISTANT",
        ["communications", "knowledge_search", "learning_material", "mel_narratives"],
        "Google's Gemini app and plan-dependent assistance in Workspace tools such as Gmail and Docs.",
        "Google-hosted services tied to a Workspace account and administrator settings.",
        "No-cost nonprofit and discounted paid Workspace offers differ. Your final price is not verified.",
        "Google includes selected AI features in Workspace for Nonprofits. Your eligibility is not verified.",
        "Separate Gemini API exists; entitlement under a Workspace nonprofit plan is not verified.",
        [
            (
                "AI features by nonprofit plan",
                "https://support.google.com/nonprofits/answer/16345471?hl=en",
            ),
            ("Gemini developer API", "https://ai.google.dev/gemini-api/docs"),
        ],
        [
            "The no-cost plan includes Gemini app access; the published table excludes Gemini in Workspace.",
            "Gmail/Docs side panels and meeting-note features are listed under paid Business Standard.",
            "Review the exact edition and account type; personal-account terms may differ.",
        ],
        disclosure=_none_known("Google"),
    ),
    _solution(
        "notebooklm",
        "Gemini Notebook (NotebookLM)",
        "Google",
        "KNOWLEDGE_ASSISTANT",
        ["knowledge_search", "learning_material", "environment_briefs", "mel_narratives"],
        "A notebook assistant for questions and summaries over selected sources, with citations for review.",
        "Google-hosted notebook service; Workspace and Cloud Enterprise editions have different controls.",
        "Features and limits depend on account and edition. Your final price is not verified.",
        "Selected notebook features are included in Workspace for Nonprofits. Your eligibility is not verified.",
        "Cloud Enterprise notebook-management APIs exist; nonprofit Workspace API entitlement is not verified.",
        [
            (
                "Source citations and chat",
                "https://support.google.com/gemininotebook/answer/16179559?hl=en",
            ),
            (
                "Features by nonprofit plan",
                "https://support.google.com/nonprofits/answer/16345471?hl=en",
            ),
            (
                "Enterprise notebook API",
                "https://docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks",
            ),
        ],
        [
            "Official NotebookLM help now redirects to Gemini Notebook; the stable catalogue ID remains notebooklm.",
            "Citations support review; they do not establish that an answer is correct or complete.",
            "Advanced limits and Enterprise APIs are not assumed to be included in the no-cost nonprofit offer.",
        ],
        ["Who can view or share each notebook and the source copies uploaded to it?"],
        disclosure=_none_known("Google"),
    ),
    _solution(
        "deepl",
        "DeepL Translator and API",
        "DeepL",
        "TRANSLATION",
        ["communications", "learning_material", "livelihood_resources"],
        "Translation tools for text and documents, with a separate API for application integration.",
        "Provider-hosted translation service; API integration requires a developer-managed application.",
        "Translator and API offers have different plans and limits. Your final price is not verified.",
        "A nonprofit-specific offer and your eligibility are not verified from the reviewed sources.",
        "Yes; the DeepL API supports text and document translation through an HTTP interface.",
        [
            ("Translator product", "https://www.deepl.com/en/products/translator"),
            (
                "API overview",
                "https://support.deepl.com/hc/en-us/articles/9773914250012-About-DeepL-API",
            ),
            ("Plan comparison", "https://www.deepl.com/en/pro"),
        ],
        [
            "Confirm support for the exact language pair, terminology and file formats in a pilot.",
            "A fluent translation can still change meaning; use a competent language reviewer.",
            "Do not assume free Translator and paid/API services have identical data terms.",
        ],
        ["Who verifies translated instructions and terminology with the intended community?"],
        disclosure=_none_known("DeepL"),
    ),
    _solution(
        "canva_magic_studio",
        "Canva Magic Studio",
        "Canva",
        "DESIGN",
        ["communications", "learning_material", "livelihood_resources"],
        "AI-assisted writing and visual design tools within Canva for draft communication materials.",
        "Canva-hosted design workspace; check sharing and external app access before uploading material.",
        "AI features and usage limits depend on the plan. Your final price is not verified.",
        "Canva offers free Pro features and collaboration for approved nonprofits. Your eligibility is not verified.",
        "API access to Magic Studio features is not verified; confirm separately before integration.",
        [
            ("AI feature announcement", "https://www.canva.com/newsroom/news/magic-studio/"),
            ("Nonprofit programme", "https://www.canva.com/nonprofits/"),
        ],
        [
            "Nonprofit approval does not establish unlimited AI use or third-party app entitlement.",
            "Check image consent, accessibility, copyright and factual accuracy before publication.",
            "Use-case mappings are editorial design pilots, not evidence of programme outcomes.",
        ],
        ["Can uploaded photos and generated imagery be used under our consent and asset-licensing rules?"],
        disclosure=_none_known("Canva"),
    ),
    _solution(
        "microsoft_foundry",
        "Microsoft Foundry (Azure AI Foundry)",
        "Microsoft",
        "DEVELOPER_PLATFORM",
        ["knowledge_search", "learning_material", "environment_briefs", "mel_narratives"],
        "An Azure platform for building applications and agents using models, tools and evaluations.",
        "Azure resources and model endpoints; regions, networking and deployment types depend on the chosen service.",
        "Cloud and model usage create service-dependent costs. Your total implementation price is not verified.",
        "An Azure nonprofit credit grant is advertised; your eligibility and covered Foundry services are not verified.",
        "Yes; the platform supports developer SDKs and model/agent endpoints.",
        [
            ("Platform overview", "https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry"),
            (
                "Azure nonprofit grant",
                "https://learn.microsoft.com/en-us/industry/nonprofit/microsoft-for-nonprofits/nonprofit-offerings-products",
            ),
        ],
        [
            "Official documentation now uses Microsoft Foundry as the product name.",
            "A developer platform needs application engineering and operational ownership beyond model access.",
            "Grant availability does not establish that every model, region or marketplace charge is covered.",
        ],
        ["Who owns application permissions, monitoring, usage limits and incident response?"],
        disclosure=_none_known("Microsoft"),
    ),
]

SOLUTION_IDS = frozenset(item["id"] for item in _SOLUTIONS)

_COMPARISON_CRITERIA = [
    {
        "id": "fit",
        "label": "Fit for our task",
        "prompt": "Test the same public or synthetic example against your acceptance checks and record failures.",
    },
    {
        "id": "existing_stack",
        "label": "Existing tools and setup",
        "prompt": "Which subscriptions, accounts, connectors and staff skills are prerequisites?",
    },
    {
        "id": "data_terms",
        "label": "Data handling",
        "prompt": "Review the exact plan's permissions, training terms, retention, deletion and processing regions.",
    },
    {
        "id": "total_cost",
        "label": "Total cost",
        "prompt": "Request a dated quote covering seats, usage, setup, training, support, taxes and exit costs.",
    },
    {
        "id": "nonprofit_eligibility",
        "label": "Nonprofit eligibility",
        "prompt": "Verify legal status, country rules, staff eligibility and renewal requirements with the provider.",
    },
    {
        "id": "human_review",
        "label": "Review and evidence",
        "prompt": "Name reviewers; test factual accuracy, citations, accessibility and language with intended users.",
    },
    {
        "id": "integration_exit",
        "label": "Integration and exit",
        "prompt": "Confirm APIs, export formats, account removal, data deletion and who maintains the integration.",
    },
]


def _closed(properties):
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": list(properties),
    }


def _text():
    return {"type": "string", "maxLength": 12000}


def _texts():
    return {"type": "array", "maxItems": 100, "items": _text()}


def disclosure_schema():
    """NONE_KNOWN names no relationship type; DISCLOSED names at least one; both carry a statement."""
    statement = {"type": "string", "minLength": 1, "maxLength": STATEMENT_MAX, "pattern": "\\S"}
    declared_on = {"type": "string", "format": "date", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"}
    return {
        "oneOf": [
            _closed(
                {
                    "status": {"const": "NONE_KNOWN"},
                    "relationship_types": {"type": "array", "maxItems": 0},
                    "statement": deepcopy(statement),
                    "declared_on": deepcopy(declared_on),
                }
            ),
            _closed(
                {
                    "status": {"const": "DISCLOSED"},
                    "relationship_types": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": len(RELATIONSHIP_TYPES),
                        "uniqueItems": True,
                        "items": {"enum": list(RELATIONSHIP_TYPES)},
                    },
                    "statement": deepcopy(statement),
                    "declared_on": deepcopy(declared_on),
                }
            ),
        ]
    }


def catalog_schema():
    """The closed published catalogue (the AISolutionsCatalog contract).

    It is the solutions component of the current archive edition (nonprofit-ai-guidance-v2, frozen in
    ai_content_schema_v2.json): the edition-1 listing shape plus a required commercial_disclosure. A
    change here needs a new archive edition with a retained reader (test_ai_content_archives.py).
    """
    listing = _closed(
        {
            "id": _text(),
            "name": _text(),
            "provider": _text(),
            "category": _text(),
            "use_case_ids": _texts(),
            "description": _text(),
            "deployment": _text(),
            "commercial_model": _text(),
            "nonprofit_offer": _text(),
            "api_available": _text(),
            "source_urls": {
                "type": "array",
                "maxItems": 100,
                "items": _closed({"label": _text(), "url": _text()}),
            },
            "verification_notes": _texts(),
            "data_review_questions": _texts(),
            "commercial_disclosure": disclosure_schema(),
        }
    )
    return _closed(
        {
            "content_version": _text(),
            "checked_on": _text(),
            "explanation": _text(),
            "solutions": {"type": "array", "maxItems": 100, "items": listing},
            "comparison_criteria": {
                "type": "array",
                "maxItems": 100,
                "items": _closed({"id": _text(), "label": _text(), "prompt": _text()}),
            },
        }
    )


_VALIDATOR = Draft202012Validator(catalog_schema(), format_checker=FormatChecker())


def validate_disclosure(value):
    """The disclosure rules in plain terms; raises SolutionsCatalogInvalid naming the first breach."""
    if not isinstance(value, dict):
        raise SolutionsCatalogInvalid("commercial_disclosure is missing")
    if set(value) != {"status", "relationship_types", "statement", "declared_on"}:
        raise SolutionsCatalogInvalid("commercial_disclosure must have exactly its four fields")
    status, types, statement = value["status"], value["relationship_types"], value["statement"]
    if status not in DISCLOSURE_STATUSES:
        raise SolutionsCatalogInvalid("commercial_disclosure status must be NONE_KNOWN or DISCLOSED")
    if type(types) is not list or any(item not in RELATIONSHIP_TYPES for item in types):
        raise SolutionsCatalogInvalid("relationship_types must come from the closed list")
    if len(set(types)) != len(types):
        raise SolutionsCatalogInvalid("relationship_types must not repeat a type")
    if status == "NONE_KNOWN" and types:
        raise SolutionsCatalogInvalid("NONE_KNOWN must not name a relationship type")
    if status == "DISCLOSED" and not types:
        raise SolutionsCatalogInvalid("DISCLOSED must name at least one relationship type")
    if type(statement) is not str or not statement.strip() or len(statement) > STATEMENT_MAX:
        raise SolutionsCatalogInvalid("commercial_disclosure needs a statement of 1 to 1000 characters")
    declared_on = value["declared_on"]
    try:
        if type(declared_on) is not str or date.fromisoformat(declared_on).isoformat() != declared_on:
            raise ValueError
    except ValueError:
        raise SolutionsCatalogInvalid("declared_on must be a calendar date (YYYY-MM-DD)") from None


def validate_catalog(value):
    """Every listing must be well formed and carry a valid commercial disclosure, or nothing is served."""
    if not isinstance(value, dict) or not isinstance(value.get("solutions"), list):
        raise SolutionsCatalogInvalid("the catalogue has no list of solutions")
    for item in value["solutions"]:
        label = item.get("id") if isinstance(item, dict) else None
        try:
            validate_disclosure(item.get("commercial_disclosure") if isinstance(item, dict) else None)
        except SolutionsCatalogInvalid as error:
            raise SolutionsCatalogInvalid(f"listing {label!r}: {error}") from None
    error = next(iter(sorted(_VALIDATOR.iter_errors(value), key=lambda e: list(map(str, e.path)))), None)
    if error is not None:
        where = "/".join(map(str, error.absolute_path)) or "catalogue"
        raise SolutionsCatalogInvalid(f"{where} does not satisfy the catalogue contract ({error.validator})")
    ids = [item["id"] for item in value["solutions"]]
    if len(set(ids)) != len(ids):
        raise SolutionsCatalogInvalid("listing IDs must be unique")
    return value


def solutions_catalog():
    """Return an isolated, validated published snapshot; reading it never calls a provider.

    Raises SolutionsCatalogInvalid when any listing lacks a valid commercial disclosure (fail closed).
    """
    return validate_catalog(
        {
            "content_version": CONTENT_VERSION,
            "checked_on": CHECKED_ON,
            "explanation": (
                "A source-backed starting list checked on the stated date, not an endorsement, live price "
                "feed or guarantee of eligibility. Use-case mappings are editorial pilot ideas. "
                "Each listing states any commercial relationship between Imprana and its provider that "
                "Imprana editorial knows of. "
                "Compare evidence and obtain a current quote before choosing a solution."
            ),
            "solutions": deepcopy(_SOLUTIONS),
            "comparison_criteria": deepcopy(_COMPARISON_CRITERIA),
        }
    )


def validate_solution_ids(value):
    """Accept only a bounded, unique shortlist from this published catalogue."""
    if type(value) is not list or not 1 <= len(value) <= 4:
        raise ValueError("Select between one and four solutions.")
    if any(type(item) is not str or item not in SOLUTION_IDS for item in value):
        raise ValueError("Select known solution IDs from the catalogue.")
    if len(set(value)) != len(value):
        raise ValueError("Select each solution only once.")
    return list(value)
